filepath_out = 'velmod_lesage.in'
VELMOD_FMT = 'LAYER {depth} {Vp_top} 0.00 {Vs_top} 0.00 2.7 0.00'

max_depth = 4000
delta     = 100
max_altitude = 3.4

def vp(depth):
    v0   = 540 # m/s
    alfa = 0.315
    a    = 10
    return v0*((depth+a)**alfa - a**alfa + 1)

def vs(depth):
    v0   = 320 # m/s
    alfa = 0.3
    a    = 15
    return v0*((depth+a)**alfa - a**alfa + 1)


with open(filepath_out, 'w') as f:
    for depth in range(0, max_depth, delta):
        Vp_top = vp(depth)
        Vs_top = vs(depth)
        f.write(VELMOD_FMT.format(
            depth  = round(depth/1000 - max_altitude, 1),
            Vp_top = round(Vp_top/1000, 2),
            Vs_top = round(Vs_top/1000, 2)
        ))
        f.write('\n')
