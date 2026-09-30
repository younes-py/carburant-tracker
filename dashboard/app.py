import html

import pandas as pd
import pydeck as pdk
import streamlit as st
from db.models import get_connection

st.set_page_config(page_title="Carburant Tracker", page_icon="⛽", layout="wide")

CARBURANTS = {
    "Gazole": "gazole",
    "SP95": "sp95",
    "SP98": "sp98",
    "E10": "e10",
    "E85": "e85",
    "GPL": "gplc",
}

FOND_DE_CARTE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500&family=Chakra+Petch:wght@500;600;700&family=Doto:wght@900&display=swap');
.stApp {background-color: #0A0F1C; background-image: radial-gradient(ellipse 70% 45% at 50% -5%, rgba(34, 211, 238, .16), transparent 70%), linear-gradient(rgba(34, 211, 238, .045) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 211, 238, .045) 1px, transparent 1px); background-size: 100% 100%, 48px 48px, 48px 48px;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stAppDeployButton"], .stDeployButton {display: none;}
.block-container {padding-top: 2.5rem; max-width: 1240px;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #0F1830 0%, #0A0F1C 100%); border-right: 1px solid rgba(34, 211, 238, .18);}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {font-family: 'Chakra Petch', sans-serif !important; font-size: .85rem !important; letter-spacing: .06em; color: #8B97AD !important;}
[data-testid="stSidebar"] [role="radiogroup"] p {font-family: 'Chakra Petch', sans-serif !important; font-size: 1.05rem !important;}
[data-baseweb="select"] > div {background: #111A2E !important; border: 1px solid rgba(34, 211, 238, .25) !important;}
.ct-marque {font-family: 'Chakra Petch', sans-serif; font-weight: 700; font-size: 1.3rem; color: #E6EDF7; margin: .5rem 0 1.5rem;}
.ct-titre {font-family: 'Chakra Petch', sans-serif; font-weight: 700; font-size: 2.8rem; color: #E6EDF7; line-height: 1.05;}
.ct-sous-titre {font-family: 'Barlow', sans-serif; font-size: 1.05rem; color: #8B97AD; margin: .4rem 0 2.2rem;}
.ct-hero {display: grid; grid-template-columns: minmax(280px, 380px) 1fr; gap: 2.5rem; margin-bottom: 3rem;}
.ct-totem {position: relative; overflow: hidden; background: linear-gradient(180deg, rgba(17, 26, 46, .95), rgba(10, 15, 28, .95)); border: 1px solid rgba(34, 211, 238, .25); border-radius: 18px; padding: 1.4rem 1.6rem 1.6rem; box-shadow: 0 24px 60px -24px rgba(34, 211, 238, .45);}
.ct-totem::before {content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #22D3EE, transparent);}
.ct-totem-carburant {font-family: 'Chakra Petch', sans-serif; font-weight: 600; font-size: 1.05rem; letter-spacing: .04em; color: #8B97AD;}
.ct-totem-prix {font-family: 'Doto', monospace; font-weight: 900; font-size: 4.4rem; line-height: 1; color: #4ADE80; text-shadow: 0 0 10px rgba(74, 222, 128, .8), 0 0 32px rgba(74, 222, 128, .45); margin: .6rem 0 .9rem; animation: allumage 1.2s ease-out both;}
.ct-totem-unite {font-family: 'Chakra Petch', sans-serif; font-size: 1.2rem; color: #8B97AD; text-shadow: none; margin-left: .4rem;}
.ct-totem-lieu {font-family: 'Barlow', sans-serif; font-size: .95rem; color: #C8D1E0;}
@keyframes allumage {0% {opacity: 0;} 30% {opacity: 1;} 40% {opacity: .25;} 55% {opacity: 1;} 65% {opacity: .5;} 100% {opacity: 1;}}
@media (prefers-reduced-motion: reduce) {.ct-totem-prix {animation: none;}}
.ct-stats {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.8rem 2rem; align-content: center;}
.ct-stat-valeur {font-family: 'Chakra Petch', sans-serif; font-weight: 600; font-size: 2.3rem; color: #E6EDF7; line-height: 1;}
.ct-stat-valeur.cher {color: #F43F5E;}
.ct-stat-label {font-family: 'Barlow', sans-serif; font-size: .95rem; color: #8B97AD; margin-top: .35rem;}
.ct-section {font-family: 'Chakra Petch', sans-serif; font-weight: 600; font-size: 1.35rem; color: #E6EDF7; margin-bottom: .9rem;}
.ct-legende {font-family: 'Barlow', sans-serif; font-size: .9rem; color: #8B97AD; margin-top: .6rem;}
[data-testid="stDeckGlJsonChart"] {border: 1px solid rgba(34, 211, 238, .2); border-radius: 16px; overflow: hidden;}
.ct-ligne {display: flex; align-items: baseline; gap: .9rem; padding: .7rem 0; border-bottom: 1px solid rgba(139, 151, 173, .15);}
.ct-rang {font-family: 'Chakra Petch', sans-serif; color: #22D3EE; width: 1.6rem; flex-shrink: 0;}
.ct-station {flex: 1; min-width: 0;}
.ct-ville {font-family: 'Barlow', sans-serif; font-weight: 500; color: #E6EDF7;}
.ct-adresse {font-family: 'Barlow', sans-serif; font-size: .85rem; color: #8B97AD;}
.ct-prix {font-family: 'Chakra Petch', sans-serif; font-weight: 600; color: #E6EDF7; white-space: nowrap;}
@media (max-width: 800px) {.ct-hero {grid-template-columns: 1fr;}}
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_departements():
    connection = get_connection()
    df = pd.read_sql(
        "SELECT DISTINCT departement FROM stations WHERE departement IS NOT NULL ORDER BY departement",
        connection,
    )
    connection.close()
    return df["departement"].tolist()


@st.cache_data(ttl=3600)
def get_prix(departement, carburant):
    connection = get_connection()
    df = pd.read_sql(
        """
        SELECT DISTINCT ON (station_id)
            ville, adresse, prix, latitude, longitude
        FROM stations
        WHERE departement = %s AND carburant = %s
        ORDER BY station_id, date_maj DESC
        """,
        connection,
        params=(departement, carburant),
    )
    connection.close()
    return df.sort_values("prix")


def euros(valeur, decimales=3):
    return f"{valeur:.{decimales}f} €".replace(".", ",")


def texte(valeur):
    return "" if pd.isna(valeur) else html.escape(str(valeur))


def couleur(prix, prix_min, prix_max):
    t = 0 if prix_max == prix_min else (prix - prix_min) / (prix_max - prix_min)
    vert, rose = (74, 222, 128), (244, 63, 94)
    return [int(v + t * (r - v)) for v, r in zip(vert, rose)] + [220]


with st.sidebar:
    st.markdown('<div class="ct-marque">Filtres</div>', unsafe_allow_html=True)
    departements = get_departements()
    departement = st.selectbox(
        "Département",
        departements,
        index=departements.index("69") if "69" in departements else 0,
    )
    nom_carburant = st.radio("Carburant", list(CARBURANTS))
    st.caption("Données : data.economie.gouv.fr")

df = get_prix(departement, CARBURANTS[nom_carburant])

st.markdown(
    '<div class="ct-titre">Carburant Tracker</div>'
    f'<div class="ct-sous-titre">Prix du {nom_carburant} dans le département {departement}</div>',
    unsafe_allow_html=True,
)

if df.empty:
    st.info(f"Aucune station ne vend de {nom_carburant} dans ce département. Choisis un autre carburant dans la barre latérale.")
    st.stop()

moins_chere = df.iloc[0]
prix_min, prix_max = df["prix"].min(), df["prix"].max()

stats = [
    (euros(df["prix"].mean()), "Prix moyen", ""),
    (euros(prix_max), "Le plus cher", "cher"),
    (euros((prix_max - prix_min) * 50, 2), "D'écart sur un plein de 50 L", ""),
    (str(len(df)), "Stations", ""),
]
stats_html = "".join(
    f'<div><div class="ct-stat-valeur {classe}">{valeur}</div><div class="ct-stat-label">{label}</div></div>'
    for valeur, label, classe in stats
)
prix_totem = f"{moins_chere['prix']:.3f}".replace(".", ",")

st.markdown(
    '<div class="ct-hero">'
    '<div class="ct-totem">'
    f'<div class="ct-totem-carburant">{nom_carburant}, le moins cher du {departement}</div>'
    f'<div class="ct-totem-prix">{prix_totem}<span class="ct-totem-unite">€/L</span></div>'
    f'<div class="ct-totem-lieu">{texte(moins_chere["ville"])}, {texte(moins_chere["adresse"])}</div>'
    '</div>'
    f'<div class="ct-stats">{stats_html}</div>'
    '</div>',
    unsafe_allow_html=True,
)

gauche, droite = st.columns([3, 2], gap="large")

with gauche:
    st.markdown('<div class="ct-section">Où faire le plein</div>', unsafe_allow_html=True)
    carte = df.dropna(subset=["latitude", "longitude"]).copy()
    carte["couleur"] = carte["prix"].apply(lambda p: couleur(p, prix_min, prix_max))
    carte["prix_affiche"] = carte["prix"].map(euros)
    st.pydeck_chart(pdk.Deck(
        map_style=FOND_DE_CARTE,
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=carte,
            get_position="[longitude, latitude]",
            get_fill_color="couleur",
            get_radius=500,
            radius_min_pixels=4,
            stroked=True,
            get_line_color=[10, 15, 28],
            line_width_min_pixels=1,
            pickable=True,
        )],
        initial_view_state=pdk.ViewState(
            latitude=carte["latitude"].mean(),
            longitude=carte["longitude"].mean(),
            zoom=8.5,
        ),
        tooltip={
            "html": "<b>{ville}</b><br/>{adresse}<br/>{prix_affiche}",
            "style": {"backgroundColor": "#111A2E", "color": "#E6EDF7", "border": "1px solid rgba(34, 211, 238, .4)", "borderRadius": "8px"},
        },
    ))
    st.markdown('<div class="ct-legende">Plus le point est vert, moins la station est chère.</div>', unsafe_allow_html=True)

with droite:
    st.markdown('<div class="ct-section">Les 10 moins chères</div>', unsafe_allow_html=True)
    lignes = "".join(
        '<div class="ct-ligne">'
        f'<span class="ct-rang">{rang}</span>'
        f'<div class="ct-station"><div class="ct-ville">{texte(s.ville)}</div><div class="ct-adresse">{texte(s.adresse)}</div></div>'
        f'<span class="ct-prix">{euros(s.prix)}</span>'
        '</div>'
        for rang, s in enumerate(df.head(10).itertuples(), start=1)
    )
    st.markdown(lignes, unsafe_allow_html=True)