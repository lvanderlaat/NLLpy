# Python Standard Library
import argparse
from glob import glob
from multiprocessing import Pool, cpu_count
from os import path, makedirs, chdir, listdir, remove
from pathlib import Path
from shutil import copy, rmtree, copytree
from subprocess import call
import sys

# Other dependencies
import pandas as pd

# Local files
from catalog import hypodd_pha_to_nlloc
from config import *
from stations import sta2NLLoc, sta2NLLocEQ


def parse_args():
    description = (
        '\tParallel wrapper for NonLinLoc\n'
        '\tThe catalog is subdivided to a number of processes\n'
    )

    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=FormatterClass)

    ###########################################################################
    #                             Required 
    ###########################################################################

    required = parser.add_argument_group('Required arguments')

    required.add_argument('--base_dir', required=True,
                          help='Path to folder of your NonLinLoc project')

    required.add_argument('--stations_csv', required=True,
                          help='Path to csv file with stations info')

    ############################################################################
    #                                 Run 
    ############################################################################

    run = parser.add_argument_group('Run arguments')

    run.add_argument('--run', action = 'store_true',
                     help='Whether to run NLLoc for the catalog')

    run.add_argument('--n_procs', default=cpu_count(), type=int,
                     help='Number of parallel processes')

    run.add_argument('--obs_file', help='Phases file',
                     required='--run' in sys.argv)

    run.add_argument('--obs_type',
                     help='Phase file type: NLLOC_OBS, SEISAN, HYPODD',
                     required='--run' in sys.argv)

    run.add_argument('--root_name',
                     help='Root name of project',
                     default='nll')

    args = parser.parse_args()
    return args


def init_IO(base_dir):

    for fname in listdir(DATA_PATH):
        if fname != '.DS_Store':
            outpath = path.join(base_dir, fname)
            if not path.exists(outpath):
                copytree(path.join(DATA_PATH, fname), path.join(base_dir, fname))
    return


def clean(base_dir, ranks_path):
    for folder in [MODEL_FOLDER, TIME_FOLDER, SYNTH_FOLDER, LOC_FOLDER]:
        files = glob(path.join(base_dir, folder, '*'))
        for f in files:
            remove(f)

    if path.exists(ranks_path): rmtree(ranks_path)

    return


def distribute(length, size):
    count, res =  divmod(length, size)
    counts     =  [count+1 if rank<res else count for rank in range(size)]
    displs     =  [sum(counts[:rank]) for rank in range(size)]
    return counts, displs


def subdivide_catalog(obs_file, obs_type, base_dir, root_name, n_procs, ranks_path):
    if not path.exists(ranks_path):
        makedirs(ranks_path)

    with open(obs_file) as f:
        n_events = 0
        for line in f:
            if not line.strip() or len(line.split()) == 0:
                n_events += 1

    print(f'\nTotal number of events: {n_events}')

    counts, displs = distribute(n_events, n_procs)

    with open(obs_file) as f_in:
        rank = 0
        n_events = 0
        f_out = open(
            path.join(ranks_path, RANK_OBS_FILE.format(rank=rank)), 'w'
        )

        for line in f_in:
            if not line.strip() or len(line.split()) == 0:
                n_events += 1

            if n_events <= counts[rank]:
                f_out.write(line)

            elif rank + 1 < n_procs:
                f_out.close()

                rank += 1
                n_events = 0
                f_out = open(
                    path.join(ranks_path, RANK_OBS_FILE.format(rank=rank)), 'w'
                )

        f_out.close()

    for rank in range(n_procs):
        in_filepath = path.join(ranks_path, RANK_IN_FILE.format(rank=rank))
        copy(path.join(base_dir, IN_FILE), in_filepath)


        obs_filepath = path.join(ranks_path, RANK_OBS_FILE.format(rank=rank))

        with open(in_filepath, 'a') as f:
            f.write('\n')
            f.write(
                LOCFILES_STATEMENT.format(
                    obs_filepath      = obs_filepath,
                    obs_type          = obs_type,
                    time_folder_path  = path.join(base_dir, TIME_FOLDER),
                    loc_folder_path   = path.join(base_dir, LOC_FOLDER),
                    root_name         = root_name,
                )
            )
            f.write('_{rank:03d}'.format(rank=rank))
    return


def join_summary(base_dir, root_name, n_procs):
    file_sum_hypoell = path.join(base_dir, LOC_FOLDER, root_name+'.sum.hypo_ell')
    with open(file_sum_hypoell, 'w') as f_out:

        for rank in range(n_procs):
            filename = FILE_RANK_HYPOELL.format(root_name=root_name, rank=rank)
            filepath = path.join(base_dir, LOC_FOLDER, filename)
            with open(filepath) as f_in:
                if rank != 0: next(f_in); next(f_in)

                for line in f_in:
                    if line.strip(): f_out.write(line)
    return


def locate(in_file):
    call(NLLOC_CMD + ' ' + in_file, shell=True)


def run(obs_file, obs_type, base_dir, root_name, n_procs):
    chdir(path.join(base_dir))

    ranks_path = path.join(base_dir, IN_FOLDER, IN_RANKS_FOLDER)

    clean(base_dir, ranks_path)

    call(VEL2GRID_CMD + ' ' + IN_FILE, shell=True)
    call(GRID2TIME_CMD + ' ' + IN_FILE, shell=True)

    subdivide_catalog(obs_file, obs_type, base_dir, root_name,
                      n_procs, ranks_path)

    in_files = [
        path.join(ranks_path, RANK_IN_FILE.format(rank=rank))
        for rank in range(n_procs)
    ]

    with Pool(n_procs) as pool:
        pool.starmap(locate, zip(in_files, ))

    join_summary(base_dir, root_name, n_procs)

    return


if __name__ == '__main__':
    args = parse_args()

    init_IO(args.base_dir)

    df = pd.read_csv(args.stations_csv)

    with open(path.join(args.base_dir, IN_FOLDER, STA_FILENAME), 'w') as f:
        sta2NLLoc(df, f)
    with open(path.join(args.base_dir, IN_FOLDER, EQSTA_FILENAME), 'w') as f:
        sta2NLLocEQ(df, f)

    if args.run:
        if args.obs_type == 'HYPODD':
            nlloc_filepath = path.join(args.base_dir, IN_FOLDER, 'obs.txt')

            hypodd_pha_to_nlloc(args.obs_file, nlloc_filepath)

            args.obs_file = nlloc_filepath
            args.obs_type = 'NLLOC_OBS'

        run(args.obs_file, args.obs_type, args.base_dir, args.root_name,
            args.n_procs)
