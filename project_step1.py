import os
import re

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely as shp
import shapely.geometry


# Read peruspiirit statistics
def read_peruspiirit_statistics():
    path_to_file = os.path.join("data", "raw", "Helsinki_alueittain_2016.xlsx")
    data = pd.read_excel(path_to_file)
    # As the file contains also information about suurpiiri (big district?) and some other irrelevant row
    # We need to do some cleanup
    # As all peruspiirit name follows the same pattern (name-n peruspiiri), then the cleaning is quite easy
    data = data[data["Alue"].notna() & data["Alue"].str.contains("n peruspiiri")]
    # Extract ID for merge
    data["PERUS"] = data["Alue"].apply(lambda x: int(re.search("(\d+)?[ ]+", x).group(0)))
    # Drop column
    data = data.drop(["Alue"], axis=1)
    return data


# Read peruspiirit areas
def read_peruspiirit_areas():
    path_to_file = os.path.join("data", "raw", "HKI-aluejako-1995-2016-gpkg", "GeoPackage", "piirialuejako-1995-2016.gpkg")
    data = gpd.read_file(path_to_file, driver="GPKG", layer="perus_2016")
    # Well, it uses some exotic encoding
    # Let's make it readable
    data["Nimi"] = data["Nimi"].apply(lambda x: x.decode("cp1252"))
    data["PERUS"] = data["PERUS"].apply(int)
    # Drop other columns as they will not be used
    return data[["PERUS", "Nimi", "geometry"]]


def read_addresses():
    path_to_file = os.path.join("data", "raw", "openaddr-collected-europe", "fi", "uusimaa-fi.csv")
    addresses = pd.read_csv(path_to_file)
    addresses["COORDS"] = list(zip(addresses["LON"], addresses["LAT"]))
    addresses["COORDS"] = addresses["COORDS"].apply(shp.geometry.Point)
    # It is known, that the largest postcode in Helsinki is 00990
    addresses = addresses[(addresses["POSTCODE"] >= 2) & (addresses["POSTCODE"] <= 990)]
    return gpd.GeoDataFrame(addresses[["POSTCODE", "COORDS"]], geometry="COORDS", crs={"init": "epsg:4326"}).to_crs({"init": "epsg:3879"})


def get_peruspiiri(address_coords, areas):
    belongs = areas["geometry"].apply(lambda area: address_coords.within(area))
    if len(areas[belongs]) > 0:
        return areas[belongs]["PERUS"].iloc[0]
    return np.nan


if __name__ == "__main__":
    peruspiirit_statistics = read_peruspiirit_statistics()
    peruspiirit_areas = read_peruspiirit_areas()
    addresses = read_addresses()

    # addresses["PERUS"] = addresses["COORDS"].apply(lambda x: get_peruspiiri(x, peruspiirit_areas))
    # addresses = addresses[addresses["PERUS"].notna()]
    # addresses.to_csv(os.path.join("data", "postcode_to_peruspiiri.csv"), encoding="utf-8")
    peruspiirit_areas.merge(peruspiirit_statistics, on="PERUS").to_csv(os.path.join("data", "peruspiirit_statistics.csv"), encoding="utf-8")
    # addresses.plot(column="PERUS", markersize=0.01)
    plt.show()
