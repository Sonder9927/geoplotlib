import pygmt


def hull_clip_grd(grd, hull, region, spacing=0.01):
    data = pygmt.grd2xyz(grd)
    clip_data = pygmt.select(data, polygon=hull)
    grid = pygmt.xyz2grd(data=clip_data, region=region, spacing=spacing)
    return grid
