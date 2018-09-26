import itertools
import os

import flask
import geopandas as gpd
import matplotlib.colors as cm
import matplotlib.pyplot as plt
import pandas as pd
import shapely as shp
import shapely.wkt

# app = flask.Flask(__name__)

if __name__ == "__main__":
    peruspiirit = pd.read_csv(os.path.join("data", "peruspiirit_statistics.csv"))
    peruspiirit["geometry"] = peruspiirit["geometry"].apply(shp.wkt.loads)
    peruspiirit = gpd.GeoDataFrame(peruspiirit, geometry="geometry")
    city_map = peruspiirit.plot(color="white", edgecolor="black")

    color_map = cm.ListedColormap(list(itertools.islice(cm.CSS4_COLORS.keys(), len(peruspiirit))), name="Test map")

    addresses = pd.read_csv(os.path.join("data", "postcode_to_peruspiiri.csv"))
    addresses["COORDS"] = addresses["COORDS"].apply(shp.wkt.loads)
    addresses = gpd.GeoDataFrame(addresses, geometry="COORDS")
    # fig = addresses.plot(ax=city_map, column="POSTCODE", markersize=0.1, cmap=color_map)\
    peruspiirit.plot(column="Yli 65-vuotiaat")
    plt.show()
    #
    # agg_zp = addresses.groupby(["PERUS", "POSTCODE"]).count()
    # agg_z = addresses.groupby("POSTCODE").count()
    #
    # app.layout = html.Div(children=[
    #     html.H3("Visualisation"),
    #     html.Table(children=[
    #         html.Tr(children=[
    #             html.Td(html.Img()),
    #             html.Td("Features")
    #         ])
    #     ])
    # ])
    # app.run_server(debug=True)
