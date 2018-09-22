import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

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


def write_poll_data_to_csv():
    if not os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
    for xls_file in XLS_FILES:
        pd.read_excel(os.path.join(POLL_DATA_FOLDER, xls_file)) \
            .to_csv(os.path.join(DATA_FOLDER, "%s.csv" % os.path.splitext(xls_file)[0]), encoding="utf-8", index=False)


if __name__ == "__main__":
    # write_poll_data_to_csv()

    osaalueet = gpd.read_file(MAP_DATA, driver="GPKG", layer="osa_alue_2016")
    print osaalueet.shape
    osaalueet.plot()
    plt.show()
