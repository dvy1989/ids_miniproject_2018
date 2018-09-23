# coding=utf-8

import os
import re

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import shapely as shp
import shapely.geometry

XLS_FILES = [
    "tuulivoimakysely_avovastaukset.xlsx",
    "tuulivoimakysely_kielletyt_paikat.xlsx",
    "tuulivoimakysely_monivalinnat.xls",
    "tuulivoimakysely_omat_paikat.xlsx",
    "tuulivoimakysely_soveltuvat_paikat.xlsx",
    "PKS_postinumeroalueet_2017_xlsx.xlsx"
]

DATA_FOLDER = "data"
RAW_DATA_FOLDER = os.path.join(DATA_FOLDER, "raw")
POLL_DATA_FOLDER = os.path.join(RAW_DATA_FOLDER, "Helsingin_tuulivoimakysely_2015")
MAP_DATA = os.path.join(RAW_DATA_FOLDER, "HKI-aluejako-1995-2016-gpkg", "GeoPackage", "piirialuejako-1995-2016.gpkg")
PERUSPIIRIT_STATISTICS = os.path.join(RAW_DATA_FOLDER, "Helsinki_alueittain_2016.xlsx")
ADDRESSES_FILE = os.path.join(RAW_DATA_FOLDER, "openaddr-collected-europe", "fi", "uusimaa-fi.csv")


def write_poll_data_to_csv():
    if not os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
    for xls_file in XLS_FILES:
        pd.read_excel(os.path.join(POLL_DATA_FOLDER, xls_file)) \
            .to_csv(os.path.join(DATA_FOLDER, "%s.csv" % os.path.splitext(xls_file)[0]), encoding="utf-8", index=False)


def add_matches_column(row, matches, addresses):
    matches[row["Nimi"]] = addresses["Coordinates"].within(row["geometry"])


if __name__ == "__main__":
    # write_poll_data_to_csv()
    peruspiirit_statistics = pd.read_excel(PERUSPIIRIT_STATISTICS)
    peruspiirit_statistics.to_csv(os.path.join(DATA_FOLDER, "stats.csv"), encoding="utf-8")
    peruspiirit_statistics = peruspiirit_statistics.loc[peruspiirit_statistics["Alue"].notna() & peruspiirit_statistics["Alue"].str.contains("n peruspiiri")]
    print peruspiirit_statistics.shape
    peruspiirit_statistics["PERUS"] = peruspiirit_statistics["Alue"].apply(lambda x: int(re.search("(\d+)?[ ]+", x).group(0)))

    peruspiirit_shapes = gpd.read_file(MAP_DATA, driver="GPKG", layer="perus_2016", encoding="cp1252")
    print peruspiirit_shapes.shape
    peruspiirit_shapes["Nimi"] = peruspiirit_shapes["Nimi"].str.replace(re.compile("[^\w]", flags=re.UNICODE), "")
    peruspiirit_shapes["Nimi"] = peruspiirit_shapes["Nimi"].apply(lambda x: x.decode("cp1252"))
    peruspiirit_shapes = peruspiirit_shapes.sort_values(by=["Nimi"])
    peruspiirit_shapes["PERUS"] = peruspiirit_shapes["PERUS"].apply(lambda x: int(x))

    data_set = peruspiirit_shapes.merge(peruspiirit_statistics, on="PERUS")
    addresses = pd.read_csv(ADDRESSES_FILE)
    addresses["Coordinates"] = list(zip(addresses["LON"] * 10 ** 6 + 519100, addresses["LAT"] * 10 ** 5 + 658000))  # x * 10**7 + 5191000 y * 10**6 + 658000
    addresses["Coordinates"] = addresses["Coordinates"].apply(shp.geometry.Point)
    # peruspiirit_shapes.rename(columns={"geometry": "Area"})
    addresses = gpd.GeoDataFrame(addresses, geometry="Coordinates")
    # print addresses["Coordinates"].head()
    # print data_set["geometry"].head()

    # with open(os.path.join(DATA_FOLDER, "output.json"), "w") as json_file:
    #     json_file.write(dataset.to_json(encoding="cp1252"))
    #
    # matches = pd.DataFrame()
    # dataset.apply(lambda row: add_matches_column(row, matches, addresses), axis=1)
    # mask = (matches == False).all(axis=1)
    # matches = matches[~mask]
    # matches.to_csv(os.path.join(DATA_FOLDER, "matches.csv"), encoding="cp1252")

    suutarila = data_set.loc[data_set["Nimi"] == "Suutarila"]
    peltokylantie = addresses.loc[addresses["STREET"].notna() & addresses["STREET"].str.contains("Peltokyl")]
    print peltokylantie["STREET"].head()

    ax = suutarila.plot(color="white", edgecolor="black")
    peltokylantie.plot(ax=ax, color="red")
    plt.show()
