NLL_STA_FMT = ('GTSRCE {station:7} LATLON {latitude:8} {longitude:8} '
               '{depth:5} {elevation:9}')
NLL_EQSTA_FMT = ('EQSTA {station:7} {phase:5} {errorType:9} {error:5} '
                 '{errorReportType:15} {errorReport:11} {probActive:10}')


def sta2NLLoc(df, f):
    f.write('# ')

    f.write(
        NLL_STA_FMT.format(
            station   = 'station',
            latitude  = 'latitude',
            longitude = 'longitude',
            depth     = 'depth',
            elevation = 'elevation')
    )
    f.write('\n')

    for i, row in df.iterrows():
        f.write(
            NLL_STA_FMT.format(
                station   =  '  ' +row.code,
                latitude  = row.latitude,
                longitude = row.longitude,
                depth     = 0.0,
                elevation = row.elevation/1000
            )
        )
        f.write('\n')
    return


def sta2NLLocEQ(df, f):
    f.write('# ')

    f.write(
        NLL_EQSTA_FMT.format(
            station         = 'station',
            phase           = 'phase',
            errorType       = 'errorType',
            error           = 'error',
            errorReportType = 'errorReportType',
            errorReport     = 'errorReport',
            probActive      = 'probActive'
        )
    )

    f.write('\n')

    for i, row in df.iterrows():
        f.write(
            NLL_EQSTA_FMT.format(
                station         =  row.code,
                phase           = 'P',
                errorType       = 'GAU',
                error           = '0.1',
                errorReportType = 'GAU',
                errorReport     = '0.1',
                probActive      = ''
            )
        )

        f.write('\n')
    return


