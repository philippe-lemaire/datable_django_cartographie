import requests
import pandas as pd
import geopandas as gpd
import folium
import os
import shutil
import h3pandas

DATA_FOLDER = "data/"
EXPORT_PATH = "maps/templates/maps/"
MAP_PATH = EXPORT_PATH + "full_map.html"


def gen_maps(
    velov_used=False,
    trains_used=False,
    cars_used=False,
    rhone_buses_used=False,
    subway_used=False,
    stop_points_used=False,
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

    m = folium.Map(location=lyon, zoom_start=11, tiles=tiles[4])



    # kwargs for gpd.explore()
    kwargs = {
        "m": m,
        "marker_kwds": {"radius": 3},
    }

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


    # get the communes shapes and resample them as hexagons
    communes_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=adr_voie_lieu.adrcomgl&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
    communes_filename = "communes.geojson"
    communes = get_data(communes_url, communes_filename)
    # reduce the columns
    communes_columns = ['nom', 'insee', 'geometry']
    communes = communes[communes_columns]

    # choice of resolution. The bigger the int, the smaller the hexagons 9 seems to
    # be a happy medium
    resolution = 9

    # Resample to H3 cells
    communes = communes.h3.polyfill_resample(resolution)
    communes.explore(color="#CCC",tooltip=None, **kwargs)

    # Velov part
    if velov_used:
        url_velov = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=jcd_jcdecaux.jcdvelov&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        velov_filename = "velov.geojson"

        velov = get_data(url_velov, velov_filename)

        velov_columns = [
            "number",
            "name",
            "address",
            "address2",
            "commune",
            "bike_stands",
            "available_bike_stands",
            "available_bikes",
            "lat",
            "lng",
            "geometry",
        ]

        velov[velov_columns].explore(color="red", **kwargs)

        # aménagements cyclables
        ac_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvoamenagementcyclable&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        ac_filename = "amenagements_cyclables.geojson"
        ac = get_data(ac_url, ac_filename)
        ac.explore(color="purple", **kwargs)

    # Position Gares
    if trains_used:
        gares_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=adr_voie_lieu.adrgarefer&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        gares_filename = "gares.geojson"

        gares = get_data(gares_url, gares_filename)
        gares_columns = ["nom", "theme", "soustheme", "geometry"]

        gares[gares_columns].explore(color="gray", **kwargs)

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
            "geometry",
        ]

        parkings[parkings_columns].explore(color="blue", **kwargs)

        # infos autopartage
        autopartage_url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvostationautopartage&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        autopartage_filename = "autopartage.geojson"
        autopartage = get_data(autopartage_url, autopartage_filename)

        autopartage.explore(color="light blue", **kwargs)

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
            "geometry",
        ]

        pr[pr_columns].explore(color="yellow", **kwargs)

    # infos transports en commun
    if rhone_buses_used:
        cars_url = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=cdr_cardurhone.cdrarret&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        cars_filename = "cars.geojson"

        cars = get_data(cars_url, cars_filename)

        cars.explore(color="lime", **kwargs)

    if subway_used:
        ## metro
        metro_url = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=tcl_sytral.tclstation&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        metro_filename = "metro_entrees_sorties.geojson"

        metro = get_data(metro_url, metro_filename)
        metro_columns = ["nom", "desserte", "geometry"]
        metro[metro_columns].explore(**kwargs)

    if stop_points_used:
        ## Points d'arrêt

        points_arret_url = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=tcl_sytral.tclarret&outputFormat=application/json; subtype=geojson&SRSNAME=EPSG:4171"
        points_arret_filename = "points_arret.geojson"
        pa = get_data(points_arret_url, points_arret_filename)
        pa_columns = ["nom", "desserte", "pmr", "ascenseur", "escalator", "geometry"]

        pa[pa_columns].explore(color="orange", **kwargs)

    # create the export path
    os.makedirs(EXPORT_PATH, exist_ok=True)
    # save the map
    m.save(MAP_PATH)
    print(f"Map created at {EXPORT_PATH}")
    return m
