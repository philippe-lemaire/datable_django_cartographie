import requests
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import os
import h3pandas
import warnings

warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

DATA_FOLDER = "data/"
EXPORT_PATH = "maps/templates/maps/"
MAP_PATH = EXPORT_PATH + "full_map.html"
COLORS = {
    "train_stations": "#9A9A9A",
    "buses": "#73C6C1",
    "public_transports": "#EB5099",
    "taxis": "#FFC403",
    "river_boats": "#8A77BA",
}

MARKER_COLORS = [
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "darkred",
    "lightred",
    "beige",
    "darkblue",
    "darkgreen",
    "cadetblue",
    "darkpurple",
    "white",
    "pink",
    "lightblue",
    "lightgreen",
    "gray",
    "black",
    "lightgray",
]

RESOLUTION = 9


def download_file(url, filename):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if filename in os.listdir(DATA_FOLDER):
        print(f"Fichier {filename} déjà téléchargé")
        return True
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"{DATA_FOLDER}{filename}", "wb") as file:
            file.write(response.content)
        print(f"Fichier {filename} enregistré")
        return True
    else:
        print(f"La requête n’a pas abouti : status {response.status_code}.")
        return False


def get_data(url, filename):
    if download_file(url, filename):
        if filename.endswith("csv"):
            return pd.read_csv(f"{DATA_FOLDER}{filename}", sep=";")
        elif filename.endswith("geojson"):
            return gpd.read_file(f"{DATA_FOLDER}{filename}")
    else:
        print("Rien à ouvrir")
        return None


def compute_heat_from_points(hex_map, df, colname="some_name", coeff=1):
    """Computes heat based on points being contained on hexagons on the hex maps"""
    # on itere sur chaque ligne de la dataframe df, et donc sur chaque point positionné
    for index, (gid, point) in df[["gid", "geometry"]].iterrows():
        # on stocke le résultat du test "l'hexagone contient ce point" dans une colonne de la table hex_map créée à ce effet
        hex_map[f"{colname}_{gid}"] = hex_map.geometry.contains(point)

    # On constitue la liste des colonnes ainsi créées
    column_names = [name for name in hex_map.columns if name.startswith(f"{colname}_")]

    # On incrémente une colonne 'heat' dans hex_map avec la somme des lignes : un dénombrement des points présents dans le hex
    hex_map["heat"] += hex_map[column_names].sum(axis=1) * coeff
    hex_map = hex_map[["nom", "geometry", "heat"]]
    print(f"hex_map mise à jour avec les {index} points de la dataframe")
    return hex_map


def compute_heat_from_lines(hex_map, df, colname="some_name", coeff=1):
    """Computes heat based on lines crossing hexagons on the hex map"""
    # on itere sur chaque ligne de la dataframe df, et donc sur chaque point positionné
    for index, (gid, line) in df[["gid", "geometry"]].iterrows():
        # on stocke le résultat du test "l'hexagone contient ce point" dans une colonne de la table hex_map créée à ce effet
        hex_map[f"{colname}_{gid}"] = hex_map.geometry.crosses(line)

    # On constitue la liste des colonnes ainsi créée
    column_names = [name for name in hex_map.columns if name.startswith(f"{colname}_")]

    # On incrémente la colonne 'heat' dans hex_map avec la somme des lignes : un dénombrement des points présents dans le hex multiplié par le coeff
    hex_map["heat"] += hex_map[column_names].sum(axis=1) * coeff
    hex_map = hex_map[["nom", "geometry", "heat"]]
    print(f"hex_map mise à jour avec les {index} points de la dataframe")
    return hex_map


def compute_heat_train_station(hex_map, df, colname="gare", coeff=3):
    """#compute_heat_train_station : avoir un moyen que les gares rayonnent leur chaleur sur les hexagones qui les contiennent et les adjacents"""

    if "voyageurs" in df.columns:
        for index, (gid, trafic, polygon) in df[
            ["gid", "voyageurs", "geometry"]
        ].iterrows():
            # on stocke le résultat du test "l'hexagone contient cette gare" ou bien la gare et l'hexagone overlappent dans une colonne de la table hex_map créée à ce effet
            hex_map[f"{colname}_contains_{gid}"] = (
                hex_map.geometry.contains(polygon) * trafic
            )
            hex_map[f"{colname}_overlaps_{gid}"] = (
                hex_map.geometry.overlaps(polygon) * trafic
            )
    else:
        for index, (gid, polygon) in df[["gid", "geometry"]].iterrows():
            # on stocke le résultat du test "l'hexagone contient cette gare" ou bien la gare et l'hexagone overlappent dans une colonne de la table hex_map créée à ce effet
            hex_map[f"{colname}_contains_{gid}"] = hex_map.geometry.contains(polygon)
            hex_map[f"{colname}_overlaps_{gid}"] = hex_map.geometry.overlaps(polygon)

    # On constitue la liste des colonnes ainsi créées
    column_names = [name for name in hex_map.columns if name.startswith(f"{colname}_")]

    # On crée une colonne "has_trainstation" dans hex_map
    hex_map["has_train_station"] = hex_map[column_names].sum(axis=1)

    # on ajoute une colonne : 'close_to_train_station'
    hex_map["close_to_train_station"] = False

    # d'abord on calcule la liste des hex adjacents à chaque hex
    hex_map = hex_map.h3.hex_ring()

    # on itère sur chaque ligne, et sur chaque hex indiqué dans la colonne h3_hex_ring
    for i, row in hex_map.iterrows():
        if row.has_train_station:  # si on a une gare sur l'hexagone
            for (
                hex_code
            ) in row.h3_hex_ring:  # on prend la liste des hexagones adjacents
                try:
                    if not hex_map.loc[
                        hex_code, "has_train_station"
                    ]:  # s'il n"y a pas déjà une gare dessus
                        hex_map.loc[
                            hex_code, "close_to_train_station"
                        ] = (
                            row.has_train_station
                        )  # on le flagge comme voisin d'une gare
                except (
                    KeyError
                ):  # exception pour les hex_code non existants (liés à la bordure de notre hex map)
                    pass

    # on retire les lignes avec des nans ajoutés
    hex_map = hex_map.dropna(axis=0)
    # on calcule la heat : +coeff si has_train_station, +coeff/2 si close_to_train_station
    hex_map["heat"] += (
        hex_map["has_train_station"] * coeff
        + hex_map["close_to_train_station"] * coeff / 2
    )

    # on limite hex_map aux colonnes qui nous intéressent
    hex_map_columns = [
        "nom",
        "geometry",
        "heat",
    ]
    hex_map = hex_map[hex_map_columns]
    return hex_map


def gen_maps(
    own_bike_used=False,
    velov_used=False,
    trains_used=False,
    cars_used=False,
    rhone_buses_used=False,
    public_transports_used=False,
    taxis_used=False,
    river_boat_used=False,
):
    # map preparation

    lyon = (45.75, 4.85)
    tiles = [
        "OpenStreetMap",
        "Stamen Terrain",
        "Stamen Toner",
        "Stamen Watercolor",
        "CartoDB positron",
        "CartoDB dark_matter",
    ]

    m = folium.Map(location=lyon, zoom_start=11, tiles=tiles[4], control_scale=True)

    # kwargs for gpd.explore()
    kwargs = {
        "m": m,
        "marker_kwds": {"radius": 3},
    }

    # own_bike_used part
    if own_bike_used:
        stationnement_velo_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvostationnementvelo&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        stationnement_velo_filename = "stationnement_velo.geojson"
        stationnement_velo = get_data(
            stationnement_velo_url, stationnement_velo_filename
        )
        # on filtre les stationnements seulement en projet
        stationnement_velo = stationnement_velo[
            stationnement_velo.avancement == "Existant"
        ]

    # Velov part
    if velov_used:
        url_velov = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=jcd_jcdecaux.jcdvelov&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        velov_filename = "velov.geojson"

        velov = get_data(url_velov, velov_filename)
        # remove closed stations
        velov = velov[velov.status == "OPEN"]
        velovdf_columns = [
            "name",
            "address",
            "commune",
            "bike_stands",
            "geometry",
            "gid",
        ]

        velov = velov[velovdf_columns]

    if velov_used or own_bike_used:
        # aménagements cyclables
        ac_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvoamenagementcyclable&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        ac_filename = "amenagements_cyclables.geojson"
        ac = get_data(ac_url, ac_filename)

    # Position Gares
    if trains_used:
        gares_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=adr_voie_lieu.adrgarefer&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        gares_filename = "gares.geojson"

        gares = get_data(gares_url, gares_filename)
        gares_columns = ["nom", "geometry", "idexterne", "gid"]

        print(gares.columns)
        gares = gares[gares_columns]

        # turn idexterne to int for future merge with traffic data
        gares.idexterne = pd.to_numeric(gares.idexterne)

        # remove the one line with no idxexterne info
        gares = gares[~gares.idexterne.isna()]

        # collect traffic data to give weight to bigger train stations
        trafic_voyageurs_url = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/frequentation-gares/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
        trafic_voyageurs_filename = "trafic_voyageurs_gares.csv"

        trafic = get_data(trafic_voyageurs_url, trafic_voyageurs_filename)

        gares_trafic = pd.merge(
            left=gares,
            right=trafic,
            left_on="idexterne",
            right_on="Code UIC",
            how="left",
        )
        gares_trafic_columns = [
            "nom",
            "gid",
            "geometry",
            "Total Voyageurs 2021",
        ]

        gares = gares_trafic[gares_trafic_columns].rename(
            columns={"Total Voyageurs 2021": "voyageurs"}
        )
        # normalize the traffic data to get some reasonnable numbers
        gares.voyageurs = 100 * gares.voyageurs / np.linalg.norm(gares.voyageurs)
        # Project to NAD83 projected crs
        gares = gares.to_crs(epsg=2263)

        # Access the centroid attribute of each polygon
        gares["centroid"] = gares.centroid

        # Project to WGS84 geographic crs
        # geometry (active) column
        gares = gares.to_crs(epsg=4326)

        # Centroid column
        gares["centroid"] = gares["centroid"].to_crs(epsg=4326)

        print(gares.columns)

    if cars_used:
        # infos stationnement

        parkings_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvoparking&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        parkings_filename = "parkings.geojson"
        parkings = get_data(parkings_url, parkings_filename)
        parkings_columns = [
            "nom",
            "commune",
            "voieentree",
            "voiesortie",
            # 'avancement',
            # 'annee',
            "typeparking",
            "situation",
            #'parkingtempsreel',
            #  'gabarit',
            "capacite",
            #'capacite2rm',
            "capacitevelo",
            "capaciteautopartage",
            "capacitepmr",
            #'usage',
            #'vocation',
            "reglementation",
            # 'fermeture',
            # 'observation',
            # 'codetype',
            "gid",
            "geometry",
        ]
        parkings = parkings[parkings_columns]

        # infos autopartage
        autopartage_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvostationautopartage&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        autopartage_filename = "autopartage.geojson"
        autopartage = get_data(autopartage_url, autopartage_filename)

        # parcs relais
        parcs_relais_url = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=tcl_sytral.tclparcrelaisst&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        parcs_relais_filename = "parcs_relais.geojson"

        pr = get_data(parcs_relais_url, parcs_relais_filename)
        pr_columns = [
            "nom",
            "capacite",
            "place_handi",
            "horaires",
            "p_surv",
            "gid",
            "geometry",
        ]
        pr = pr[pr_columns]

    # infos transports en commun
    if rhone_buses_used:
        cars_url = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=cdr_cardurhone.cdrarret&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        cars_filename = "cars.geojson"
        cars = get_data(cars_url, cars_filename)

    if public_transports_used:
        ## Points d'arrêt
        points_arret_url = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=tcl_sytral.tclarret&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        points_arret_filename = "points_arret.geojson"
        pa = get_data(points_arret_url, points_arret_filename)
        pa_columns = [
            "nom",
            "desserte",
            "pmr",
            "ascenseur",
            "escalator",
            "gid",
            "geometry",
        ]
        pa = pa[pa_columns]

    if taxis_used:
        ## taxis
        taxis_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvostationtaxi&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        taxis_filename = "stations_taxi.geojson"
        taxis = get_data(taxis_url, taxis_filename)
        taxis_columns = ["nom", "gid", "geometry"]
        taxis = taxis[taxis_columns]

    if river_boat_used:
        # points arrêt navette fluviale
        navette_fluviale_url = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=tca_transports_alternatifs.tcaarretvaporetto&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        navette_fluviale_filename = "navette_fluviale.geojson"
        navette_fluviale = get_data(navette_fluviale_url, navette_fluviale_filename)
        navette_fluviale_columns = ["nom", "gid", "geometry"]
        navette_fluviale = navette_fluviale[navette_fluviale_columns]

    ## HEX GRID Part
    # get the communes shapes and resample them as hexagons
    communes_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=adr_voie_lieu.adrcomgl&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
    communes_filename = "communes.geojson"
    hex_map = get_data(communes_url, communes_filename)

    # reduce the columns
    hex_map_columns = ["nom", "geometry"]
    hex_map = hex_map[hex_map_columns]
    # create the heat column with zero values
    hex_map["heat"] = 0.0

    # choice of resolution. The bigger the int, the smaller the hexagons 9 seems to
    # be a happy medium

    # Resample to H3 cells
    hex_map = hex_map.h3.polyfill_resample(RESOLUTION)

    # compute heat
    if own_bike_used:
        hex_map = compute_heat_from_points(
            hex_map, stationnement_velo, "stationnement_velo", coeff=1
        )

    if velov_used:
        hex_map = compute_heat_from_points(hex_map, velov, "velov", coeff=1)

    if own_bike_used or velov_used:
        hex_map = compute_heat_from_lines(hex_map, ac, "ac", coeff=0.5)

    if trains_used:
        hex_map = compute_heat_train_station(hex_map, gares)

    if public_transports_used:
        hex_map = compute_heat_from_points(hex_map, pa, "points_access", coeff=2)

    if river_boat_used:
        hex_map = compute_heat_train_station(
            hex_map, navette_fluviale, "navette_fluv", coeff=1
        )
    if taxis_used:
        hex_map = compute_heat_from_points(hex_map, taxis, "taxis", coeff=1)

    if rhone_buses_used:
        hex_map = compute_heat_from_points(hex_map, cars, "cars", coeff=1)

    if cars_used:
        hex_map = compute_heat_from_points(hex_map, parkings, "parkings", coeff=1)
        hex_map = compute_heat_from_points(hex_map, autopartage, "autopartage", coeff=1)
        hex_map = compute_heat_from_points(hex_map, pr, "pr", coeff=1)

    ## add the hex_map with heat first, then the points
    hex_map.explore(
        column="heat",
        cmap="plasma",
        style_kwds={"opacity": 0.05},
        legend=None,
        **kwargs,
    )

    ## add the geometries from datasets used after the hexagon tiles
    # It's a bit too taxing to draw markers for each stationnement vélo
    """
    if own_bike_used:
        # own_bike_marker = folium.Marker(icon=folium.Icon(color="darkpurple", icon="lock-keyhole", prefix="fa"), )
        # own_bike_marker = None
        stationnement_velo.explore(color="gray", marker_type=own_bike_marker, **kwargs)
    """
    if velov_used:
        velov_marker = folium.Marker(
            icon=folium.Icon(color="red", icon="bicycle", prefix="fa"),
        )
        velov.explore(
            # color=COLORS.get("bikes"),
            marker_type=velov_marker,
            **kwargs,
        )

    # if own_bike_used or velov_used:
    #   ac.explore(color=COLORS.get("bikes"), **kwargs)

    if cars_used:
        parking_marker = folium.Marker(
            icon=folium.Icon(color="cadetblue", icon="square-parking", prefix="fa"),
        )
        pr_marker = folium.Marker(
            icon=folium.Icon(color="lightred", icon="square-parking", prefix="fa"),
        )
        autopartage_marker = folium.Marker(
            icon=folium.Icon(color="lightblue", icon="square-parking", prefix="fa"),
        )
        parkings.explore(marker_type=parking_marker, **kwargs)
        autopartage.explore(marker_type=autopartage_marker, **kwargs)
        pr.explore(marker_type=pr_marker, **kwargs)

    if trains_used:
        gares.explore(color=COLORS.get("train_stations"), **kwargs)
        # add the train marker to the centroid of each train station
        for _, r in gares.iterrows():
            lat = r["centroid"].y
            lon = r["centroid"].x
            folium.Marker(
                location=[lat, lon],
                popup=r["nom"],
                icon=folium.Icon(color="gray", icon="train", prefix="fa"),
            ).add_to(m)

    if public_transports_used:
        pa.explore(color=COLORS.get("public_transports"), **kwargs)

    if river_boat_used:
        ferry_marker = folium.Marker(
            icon=folium.Icon(color="darkblue", icon="ferry", prefix="fa"),
        )
        navette_fluviale.explore(
            color=COLORS.get("river_boats"), marker_type=ferry_marker, **kwargs
        )

    if taxis_used:
        taxis.explore(color=COLORS.get("taxis"), **kwargs)

    if rhone_buses_used:
        cars.explore(color=COLORS.get("buses"), **kwargs)
    # create the export path
    os.makedirs(EXPORT_PATH, exist_ok=True)
    # save the map
    m.save(MAP_PATH)
    print(f"Map created at {EXPORT_PATH}")
    return m
