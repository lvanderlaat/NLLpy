from obspy import UTCDateTime


from config import PHA_FMT


def hypodd_pha_to_nlloc(filepath_in, filepath_out, max_depth=30):
    with open(filepath_in) as f:
        blocks = f.read().split('#')[1:]

    f = open(filepath_out, 'w')

    for block in blocks:
        lines = block.strip().splitlines()
        yr, mo, dy, hr, mn, sc, la, lo, dp, mg, eh, ez, rms, id_ = lines[0].split()
        time = UTCDateTime(int(yr), int(mo), int(dy), int(hr), int(mn), float(sc))

        if float(dp) <= max_depth:
            for line in lines[1:]:
                station, reltime, weight, phase = line.split()
                pick_time = time + float(reltime)

                f.write(PHA_FMT.format(
                    station       = station,
                    network       = '?',
                    component     = '?',
                    P_phase_onset = '?',
                    phase         = phase,
                    first_motion  = '?',
                    year          = pick_time.year,
                    month         = pick_time.month,
                    day           = pick_time.day,
                    hour          = pick_time.hour,
                    minute        = pick_time.minute,
                    second        = pick_time.second + pick_time.microsecond/1e6,
                    err           = 'GAU',
                    pick_error    = 0.1,
                    err_mag       = -1,
                    coda_dur      = -1,
                    amplitude     = -1
                ))
                f.write('\n')
            f.write('\n')
    return

