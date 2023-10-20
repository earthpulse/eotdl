'''
Geometry utils
'''

from pandas import isna


def convert_df_geom_to_shape(row):
    """
    Convert the geometry of a dataframe row to a shapely shape

    :param row: row of a dataframe
    """
    from shapely.geometry import shape

    if not isna(row["geometry"]):
        geo = shape(row["geometry"])
        wkt = geo.wkt
    else:
        wkt = "POLYGON EMPTY"

    return wkt