from argparse import ArgumentDefaultsHelpFormatter, RawTextHelpFormatter
from os import path
from pathlib import Path


class FormatterClass(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    pass

DATA_PATH = path.join(Path(path.realpath(__file__)).parent, 'data')

IN_FOLDER           = '0_IN'
MODEL_FOLDER        = '1_MODEL'
TIME_FOLDER         = '2_TIME'
SYNTH_FOLDER        = '3_SYNTH'
LOC_FOLDER          = '4_LOC'

IN_FILE_NAME        = 'nlloc.in'
IN_FILE             = path.join(IN_FOLDER, IN_FILE_NAME)

IN_RANKS_FOLDER     = 'RANKS'
RANK_OBS_FILE       = '{rank:03d}_obs.txt'
RANK_IN_FILE        = '{rank:03d}.in'
FILE_RANK_HYPOELL   = ('{root_name}_{rank:03d}.sum.grid0.loc.hypo_ell')

LOCFILES_STATEMENT  = ('LOCFILES {obs_filepath} {obs_type} '
                           '{time_folder_path}/layer '
                           '{loc_folder_path}/{root_name}')

VEL2GRID_CMD        = 'Vel2Grid'
GRID2TIME_CMD       = 'Grid2Time'
NLLOC_CMD           = 'NLLoc'

PHA_FMT = (
    '{station:6} {network:4} {component:4} {P_phase_onset:1} {phase:6} '
    '{first_motion:1} {year:04d}{month:02d}{day:02d} {hour:02d}{minute:02d} '
    '{second:7.4f} {err:3} {pick_error:9.2e} {err_mag:9.2e} {coda_dur:9.2e} '
    '{amplitude:9.2e}'
)

STA_FILENAME        = 'stations.in'
STA_FMT             = (
    'GTSRCE {station:7} LATLON {latitude:8} {longitude:8} '
    '{depth:5} {elevation:9}'
)

EQSTA_FILENAME      = 'eqsta.in'
EQSTA_FMT           = (
    'EQSTA {station:7} {phase:5} {errorType:9} {error:5} '
    '{errorReportType:15} {errorReport:11} {probActive:10}'
)
