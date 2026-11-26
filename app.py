import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Klima- & Berechnungs-Hub", layout="wide")
st.title("🌱 Klima- & Berechnungs-Hub")

if "moor_step" not in st.session_state:
    st.session_state.moor_step = 0


def go_to_start():
    st.session_state.moor_step = 0


def go_back():
    st.session_state.moor_step = max(0, st.session_state.moor_step - 1)


def go_next():
    st.session_state.moor_step = min(2, st.session_state.moor_step + 1)


tab1, tab2, tab3 = st.tabs([
    "🌱 Moor-Berechnung",
    "⚡ BECCS-Berechnung",
    "📊 Vergleich & Volkswirtschaft"
])

# ==========================================
# TAB 1: MOOR-WIEDERVERNÄSSUNG (SCHRITTE)
# ==========================================
with tab1:
    st.header("Moor-Wiedervernässung & Paludikultur")

    flaechen_groesse = st.session_state.get("moor_flaeche_val", 10.0)
    bundesland = st.session_state.get("moor_bundesland_val", "Schleswig-Holstein")
    moor_typ = st.session_state.get("moor_typ_val", "Hochmoor")
    besitz_status = st.session_state.get("moor_besitz_val", "Bereits im Besitz")
    vorher_nutzung = st.session_state.get("moor_vorher_val", "Grünland")
    bisherige_ertraege_pro_ha = st.session_state.get("moor_ertrag_val", 800.0)
    kaufkosten_gesamt = st.session_state.get("moor_kaufkosten_val", 0.0)

    bewirtschaftung = st.session_state.get("moor_bewirtschaftung_val", "Rohrglanzgras")
    etablierungs_art = st.session_state.get("moor_etablierung_val", "Natürliche Sukzession")
    etablierungs_detail = st.session_state.get("moor_etablierung_detail_val", None)

    mahd_zeitpunkt = st.session_state.get("moor_mahd_zeitpunkt_val", "Sommermahd")
    ernteform_biomasse = st.session_state.get("moor_ernteform_val", "Häckselgut")
    schwarzerle_ernte = st.session_state.get("moor_schwarzerle_ernte_val", "Stammholz")
    verwertung = st.session_state.get("moor_verwertung_val", None)
    folge_auswahl = st.session_state.get("moor_folge_val", None)
    unter_folge_auswahl = st.session_state.get("moor_unter_folge_val", None)
    ballen_winter_option = st.session_state.get("moor_ballen_winter_val", None)
    tier_art = st.session_state.get("moor_tier_art_val", None)
    tier_haltungssystem = st.session_state.get("moor_tier_haltung_val", None)
    tier_vermarktung = st.session_state.get("moor_tier_vermarktung_val", None)
    erntetechnik = st.session_state.get("moor_erntetechnik_val", None)

    transport_bekannt = st.session_state.get("moor_transport_bekannt_val", "Nein")
    transport_km = st.session_state.get("moor_transport_km_val", 10.0)
    lagerung_geplant = st.session_state.get("moor_lagerung_geplant_val", "Nein")
    lagerung_art = st.session_state.get("moor_lagerung_art_val", None)

    if st.session_state.moor_step >= 1:
        info_teile = [
            f"**Bundesland:** {bundesland}",
            f"**Fläche:** {flaechen_groesse:.1f} ha",
            f"**Moortyp:** {moor_typ}",
            f"**Status:** {besitz_status}",
            f"**Vorher:** {vorher_nutzung}"
        ]
        if st.session_state.moor_step == 2:
            info_teile.append(f"**Bewirtschaftung:** {bewirtschaftung}")
            if etablierungs_art:
                etab_text = etablierungs_art
                if etablierungs_art == "Erstetablierung" and etablierungs_detail:
                    etab_text += f" ({etablierungs_detail})"
                info_teile.append(f"**Etablierung:** {etab_text}")

        st.info("📌 **Aktuelle Auswahl:** " + "  |  ".join(info_teile))

    # --- SCHRITT 0: STARTMASKE ---
    if st.session_state.moor_step == 0:
        st.subheader("Schritt 1 von 3: Startmaske – Fläche & Ausgangslage")

        bundesland_optionen = [
            "Schleswig-Holstein",
            "Bayern",
            "Niedersachsen",
            "Mecklenburg-Vorpommern"
        ]
        bundesland_input = st.selectbox(
            "In welchem Bundesland liegt das Moor?",
            bundesland_optionen,
            index=bundesland_optionen.index(bundesland) if bundesland in bundesland_optionen else 0,
            key="input_bundesland"
        )

        flaeche_input = st.number_input(
            "Wie viel Hektar (ha) möchten Sie wiedervernässen?",
            min_value=0.1,
            value=float(flaechen_groesse),
            step=0.1,
            key="input_flaeche"
        )

        moor_typ_input = st.selectbox(
            "Um welchen Moortyp handelt es sich?",
            ["Hochmoor", "Niedermoor", "Weiß ich nicht"],
            index=["Hochmoor", "Niedermoor", "Weiß ich nicht"].index(moor_typ),
            key="input_moortyp"
        )

        besitz_input = st.radio(
            "Besitzen Sie die Fläche bereits oder müssen Sie sie kaufen?",
            ["Bereits im Besitz", "Muss gekauft werden"],
            index=["Bereits im Besitz", "Muss gekauft werden"].index(besitz_status),
            key="input_besitz"
        )

        kaufkosten_tmp = 0.0
        vorbesitzer_ertrag_bekannt = False
        ertrag_step1_tmp = float(bisherige_ertraege_pro_ha)

        kaufpreis_bundesland_map = {
            "Schleswig-Holstein": 26875.0,
            "Bayern": 60864.0,
            "Niedersachsen": 33497.
