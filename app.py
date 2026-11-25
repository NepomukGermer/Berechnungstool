import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Klima- & Berechnungs-Hub", layout="wide")
st.title("🌱 Klima- & Berechnungs-Hub")

# Schritt-Steuerung für das Moor-Tool initialisieren
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

    # Standardwerte, damit Tab 3 immer auf gültige Zahlen zugreifen kann
    flaechen_groesse = st.session_state.get("moor_flaeche_val", 10.0)
    moor_typ = st.session_state.get("moor_typ_val", "Hochmoor")
    besitz_status = st.session_state.get("moor_besitz_val", "Bereits im Besitz")
    vorher_nutzung = st.session_state.get("moor_vorher_val", "Grünland")
    bisherige_ertraege_pro_ha = st.session_state.get("moor_ertrag_val", 800.0)
    kaufkosten_gesamt = st.session_state.get("moor_kaufkosten_val", 0.0)
    bewirtschaftung = st.session_state.get("moor_bewirtschaftung_val", "Rohrglanzgras")
    etablierungs_art = st.session_state.get("moor_etablierung_val", "Natürliche Sukzession")
    etablierungs_detail = st.session_state.get("moor_etablierung_detail_val", None)
    verwertung = st.session_state.get("moor_verwertung_val", None)
    folge_auswahl = st.session_state.get("moor_folge_val", None)
    tier_art = st.session_state.get("moor_tier_art_val", None)
    tier_vermarktung = st.session_state.get("moor_tier_vermarktung_val", None)
    erntetechnik = st.session_state.get("moor_erntetechnik_val", None)
    erntezeitpunkt = st.session_state.get("moor_erntezeitpunkt_val", None)

    # --- SCHRITT 0: STARTMASKE ---
    if st.session_state.moor_step == 0:
        st.subheader("Schritt 1 von 3: Startmaske – Fläche & Ausgangslage")

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

        if besitz_input == "Muss gekauft werden":
            preis_bekannt = st.radio(
                "Kennen Sie den Kaufpreis für das Grundstück?",
                ["Ja", "Nein"],
                key="input_preis_bekannt"
            )
            if preis_bekannt == "Ja":
                kaufpreis_pro_ha = st.number_input(
                    "Kaufpreis (€/ha):",
                    min_value=0.0,
                    value=15000.0,
                    step=500.0,
                    key="input_kaufpreis_ha"
                )
                kaufkosten_tmp = kaufpreis_pro_ha * flaeche_input
            else:
                kaufkosten_tmp = 14000.0 * flaeche_input
                st.info("Kein Kaufpreis bekannt – es wird mit einem Richtwert von 14.000 €/ha gerechnet.")

            vorbesitzer_ertrag_bekannt = st.checkbox(
                "Kennen Sie die bisherigen Erträge pro ha und Jahr vom Vorbesitzer?",
                value=st.session_state.get("moor_vorbesitzer_bekannt_val", False),
                key="input_vorbesitzer_bekannt"
            )

        vorher_input = st.selectbox(
            "Was war die Fläche vorher?",
            ["Ackerland", "Grünland"],
            index=["Ackerland", "Grünland"].index(vorher_nutzung),
            key="input_vorher"
        )

        st.markdown("---")
        if st.button("Weiter →", type="primary", key="btn_weiter_0"):
            st.session_state.moor_flaeche_val = flaeche_input
            st.session_state.moor_typ_val = moor_typ_input
            st.session_state.moor_besitz_val = besitz_input
            st.session_state.moor_kaufkosten_val = kaufkosten_tmp
            st.session_state.moor_vorbesitzer_bekannt_val = vorbesitzer_ertrag_bekannt
            st.session_state.moor_vorher_val = vorher_input
            go_next()
            st.rerun()

    # --- SCHRITT 1: ERTRÄGE & BEWIRTSCHAFTUNG ---
    elif st.session_state.moor_step == 1:
        nav_col1, nav_col2, _ = st.columns([1, 1, 4])
        with nav_col1:
            st.button("← Schritt zurück", on_click=go_back, key="btn_zurueck_1")
        with nav_col2:
            st.button("🏠 Zur Startseite", on_click=go_to_start, key="btn_start_1")

        st.subheader("Schritt 2 von 3: Bisherige Erträge & Bewirtschaftung")

        vorbesitzer_bekannt = st.session_state.get("moor_vorbesitzer_bekannt_val", False)
        ertrag_tmp = bisherige_ertraege_pro_ha
        if besitz_status == "Bereits im Besitz" or vorbesitzer_bekannt:
            ertrag_tmp = st.number_input(
                "Wie hoch waren die bisherigen Erträge auf der Fläche (€/ha und Jahr)?",
                min_value=0.0,
                value=float(bisherige_ertraege_pro_ha),
                step=50.0,
                key="input_bisher_ertrag"
            )

        bew_optionen = [
            "Rohrglanzgras",
            "Schwarzerle",
            "Nasswiese",
            "Schilf",
            "Rohrkolben",
            "Torfmoos",
            "Wasserbüffel",
            "Photo-Voltaik",
            "Seggen"
        ]
        bew_tmp = st.selectbox(
            "Wie möchten Sie wirtschaften?",
            bew_optionen,
            index=bew_optionen.index(bewirtschaftung),
            key="input_bewirtschaftung"
        )

        etab_tmp = None
        etab_detail_tmp = None
        if bew_tmp not in ["Wasserbüffel", "Photo-Voltaik"]:
            etab_tmp = st.radio(
                "Möchten Sie natürliche Sukzession oder eine Erstetablierung durchführen?",
                ["Natürliche Sukzession", "Erstetablierung"],
                index=0 if etablierungs_art != "Erstetablierung" else 1,
                key="input_etablierung"
            )
            if etab_tmp == "Erstetablierung":
                etab_detail_tmp = st.radio(
                    "Wie erfolgt die Erstetablierung?",
                    ["Aussaat", "Anpflanzung mit Jungpflanzen"],
                    index=0 if etablierungs_detail != "Anpflanzung mit Jungpflanzen" else 1,
                    key="input_etablierung_detail"
                )

        st.markdown("---")
        if st.button("Weiter →", type="primary", key="btn_weiter_1"):
            st.session_state.moor_ertrag_val = ertrag_tmp
            st.session_state.moor_bewirtschaftung_val = bew_tmp
            st.session_state.moor_etablierung_val = etab_tmp
            st.session_state.moor_etablierung_detail_val = etab_detail_tmp
            go_next()
            st.rerun()

    # --- SCHRITT 2: VERWERTUNG, TECHNIK & AUSWERTUNG ---
    elif st.session_state.moor_step == 2:
        nav_col1, nav_col2, _ = st.columns([1, 1, 4])
        with nav_col1:
            st.button("← Schritt zurück", on_click=go_back, key="btn_zurueck_2")
        with nav_col2:
            st.button("🏠 Zur Startseite", on_click=go_to_start, key="btn_start_2")

        st.subheader("Schritt 3 von 3: Verwertung, Erntetechnik & Auswertung")

        verwertung_tmp = None
        folge_tmp = None
        tier_art_tmp = None
        tier_vermarktung_tmp = None
        erntetechnik_tmp = None
        erntezeitpunkt_tmp = None

        if bewirtschaftung == "Rohrkolben":
            verwertung_tmp = st.selectbox(
                "Welche Verwertungsmöglichkeit für Rohrkolben streben Sie an?",
                [
                    "Dämmen und Bauen",
                    "Werkstoffe & Papier",
                    "Heizen",
                    "Samen",
                    "Fasern",
                    "Gartenbausubstrate",
                    "Einstreu",
                    "Plattformchemikalien",
                    "Häckselgut",
                    "Ballen",
                    "Bunde"
                ],
                key="sel_verwertung_rohrkolben"
            )
        elif bewirtschaftung == "Schilf":
            verwertung_tmp = st.selectbox(
                "Welche Verwertungsmöglichkeit für Schilf streben Sie an?",
                [
                    "Häckselgut",
                    "Ballen",
                    "Bunde",
                    "Dämmen",
                    "Werkstoffe & Papier",
                    "Heizen",
                    "Kultursubstrate",
                    "Einstreu",
                    "Bio-Aktivkohle",
                    "Plattformchemikalien"
                ],
                key="sel_verwertung_schilf"
            )
        elif bewirtschaftung == "Torfmoos":
            verwertung_tmp = st.selectbox(
                "Was möchten Sie mit Torfmoos tun?",
                [
                    "Kultursubstrate herstellen",
                    "Saatgut ernten",
                    "Verbands- & Hygieneartikel",
                    "Dämm- & Verpackungsmaterial",
                    "Absorptionsmittel & Wasserfilter"
                ],
                key="sel_verwertung_torfmoos"
            )
        elif bewirtschaftung == "Schwarzerle":
            verwertung_tmp = st.selectbox(
                "Welche Verwertung streben Sie bei Schwarzerle an?",
                ["Wertholz", "Plattenwerkstoffe", "Heizen"],
                key="sel_verwertung_schwarzerle"
            )
        elif bewirtschaftung == "Nasswiese":
            verwertung_tmp = st.selectbox(
                "Welche Nutzung auf Nasswiesen / Nassweiden streben Sie an?",
                [
                    "Tiere halten",
                    "Raufutter gewinnen",
                    "Heizen",
                    "Bau- & Dämmstoffe",
                    "Bio-Aktivkohle",
                    "Substrate",
                    "Zellulose & Papier",
                    "Sonnentau"
                ],
                key="sel_verwertung_nasswiese"
            )
        elif bewirtschaftung == "Seggen":
            verwertung_tmp = st.selectbox(
                "Welche Verwertung streben Sie bei Seggen an?",
                [
                    "Verbrennung",
                    "Pferdeheu",
                    "Einstreu",
                    "Bau- & Dämmstoffe",
                    "Gartenbausubstrate",
                    "Kohle"
                ],
                key="sel_verwertung_seggen"
            )
        elif bewirtschaftung == "Rohrglanzgras":
            verwertung_tmp = st.selectbox(
                "Welche Verwertung streben Sie bei Rohrglanzgras an?",
                [
                    "Pferdeheu",
                    "Raufutter",
                    "Proteinkonzentrat",
                    "Einstreu",
                    "Verbrennung",
                    "Faserguss",
                    "Papier",
                    "Bau- & Dämmstoffe",
                    "Häckselgut",
                    "Ballen",
                    "Bunde"
                ],
                key="sel_verwertung_rohrglanzgras"
            )

        # Anschlussfragen nach Verwertung
        if verwertung_tmp in ["Dämmen und Bauen", "Bau- & Dämmstoffe"]:
            folge_tmp = st.selectbox(
                "Welche Dämm- bzw. Bauprodukte möchten Sie herstellen?",
                ["Einblasdämmung", "Dämmmatten", "Dämmplatten", "Plattenwerkstoffe"],
                key="folge_daemmung"
            )

        if bewirtschaftung == "Schilf" and verwertung_tmp == "Dämmen":
            folge_tmp = st.selectbox(
                "Was möchten Sie aus Schilf zum Dämmen herstellen?",
                ["Dämmplatten", "Putzträger"],
                key="folge_schilf_daemmen"
            )

        if verwertung_tmp in ["Werkstoffe & Papier", "Zellulose & Papier", "Papier"]:
            folge_tmp = st.selectbox(
                "Welche Werkstoff- bzw. Papiervariante möchten Sie herstellen?",
                ["Plattenwerkstoffe", "Zellulosefasern für Papier", "Formteile"],
                key="folge_werkstoffe_papier"
            )

        if verwertung_tmp in ["Heizen", "Verbrennung"]:
            folge_tmp = st.selectbox(
                "Wie möchten Sie heizen bzw. die Biomasse thermisch nutzen?",
                ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung", "Heu", "Biogas"],
                key="folge_heizen"
            )

        if verwertung_tmp in ["Samen", "Saatgut ernten", "Fasern"]:
            folge_tmp = st.selectbox(
                "Wie möchten Sie Samen bzw. Fasern nutzen?",
                [
                    "Samen zur Weitervermehrung nutzen",
                    "Fasern als Füllfaser verwenden",
                    "Fasern als Dämmfaser verwenden"
                ],
                key="folge_samen_fasern"
            )

        if bewirtschaftung == "Torfmoos" and verwertung_tmp == "Kultursubstrate herstellen":
            folge_tmp = st.selectbox(
                "Welches Substrat-Ziel verfolgen Sie bei Torfmoos?",
                [
                    "Fossiler Weißtorf (Vergleich / Ersatz)",
                    "Spezialsubstrate für die Orchideenzucht"
                ],
                key="folge_torfmoos_substrat"
            )

        if verwertung_tmp == "Tiere halten":
            folge_tmp = st.selectbox(
                "Wie möchten Sie die Tiere halten?",
                ["Ganzjährig", "Extensiv", "Vollweidesystem", "Teilweidesystem"],
                key="folge_tierhaltung_system"
            )
            tier_art_tmp = st.radio(
                "Welche Tierart möchten Sie halten?",
                ["Wasserbüffel", "Robustrinder"],
                key="folge_tierart"
            )
            tier_vermarktung_tmp = st.radio(
                "Was ist Ihr Schwerpunkt bei der Tierhaltung?",
                ["Fleisch verkaufen", "Züchten und Tiere verkaufen"],
                key="folge_tier_vermarktung"
            )

        if verwertung_tmp == "Raufutter gewinnen":
            folge_tmp = st.selectbox(
                "Welche Raufutter-Form möchten Sie gewinnen?",
                ["Heu", "Silage", "Einstreu"],
                key="folge_raufutter"
            )

        if bewirtschaftung not in ["Photo-Voltaik", "Wasserbüffel", "Schwarzerle"]:
            erntetechnik_tmp = st.selectbox(
                "Wie sieht es mit Erntemaschinen aus?",
                [
                    "Eigene Maschinen vorhanden, die auf der Fläche fahren können",
                    "Zugang zu einem Maschinenring",
                    "Vorhandene Maschinen können angepasst werden",
                    "Spezialtechnik kaufen",
                    "Spezialfirmen beauftragen"
                ],
                key="moor_erntetechnik"
            )

        if verwertung_tmp == "Häckselgut":
            erntezeitpunkt_tmp = st.radio(
                "Wann erfolgt die Ernte für Häckselgut?",
                ["Sommerernte", "Winterernte"],
                key="moor_erntezeitpunkt_haeckselfutter"
            )

        st.session_state.moor_verwertung_val = verwertung_tmp
        st.session_state.moor_folge_val = folge_tmp
        st.session_state.moor_tier_art_val = tier_art_tmp
        st.session_state.moor_tier_vermarktung_val = tier_vermarktung_tmp
        st.session_state.moor_erntetechnik_val = erntetechnik_tmp
        st.session_state.moor_erntezeitpunkt_val = erntezeitpunkt_tmp

        verwertung = verwertung_tmp
        folge_auswahl = folge_tmp
        tier_art = tier_art_tmp
        tier_vermarktung = tier_vermarktung_tmp
        erntetechnik = erntetechnik_tmp
        erntezeitpunkt = erntezeitpunkt_tmp

    # ==========================================
    # BERECHNUNGSLOGIK MOOR (IMMER AKTUELL)
    # ==========================================
    moor_basis_co2 = {
        "Hochmoor": 28.0,
        "Niedermoor": 24.0,
        "Weiß ich nicht": 22.0
    }[moor_typ]
    vorher_aufschlag = 1.15 if vorher_nutzung == "Ackerland" else 1.0
    co2_minderung_moor = flaechen_groesse * moor_basis_co2 * vorher_aufschlag

    etablierung_kosten_pro_ha_jahr = 0.0
    if etablierungs_art == "Erstetablierung":
        etablierung_kosten_pro_ha_jahr = 450.0 if etablierungs_detail == "Anpflanzung mit Jungpflanzen" else 250.0
    elif etablierungs_art == "Natürliche Sukzession":
        etablierung_kosten_pro_ha_jahr = 80.0

    technik_kosten_pro_ha_jahr = {
        None: 120.0,
        "Eigene Maschinen vorhanden, die auf der Fläche fahren können": 150.0,
        "Zugang zu einem Maschinenring": 220.0,
        "Vorhandene Maschinen können angepasst werden": 260.0,
        "Spezialtechnik kaufen": 420.0,
        "Spezialfirmen beauftragen": 480.0
    }[erntetechnik]

    kauf_annuitaet_jahr = kaufkosten_gesamt / 10.0

    kosten_bauer_jahr = (
        flaechen_groesse * (etablierung_kosten_pro_ha_jahr + technik_kosten_pro_ha_jahr)
        + kauf_annuitaet_jahr
    )

    kosten_volk_jahr = (
        flaechen_groesse * 850.0
        + flaechen_groesse * etablierung_kosten_pro_ha_jahr
        + kauf_annuitaet_jahr
    )

    nutzung_erloes_pro_ha_jahr = {
        "Rohrglanzgras": 950.0,
        "Schwarzerle": 1100.0,
        "Nasswiese": 750.0,
        "Schilf": 1050.0,
        "Rohrkolben": 1150.0,
        "Torfmoos": 1400.0,
        "Wasserbüffel": 900.0,
        "Photo-Voltaik": 2200.0,
        "Seggen": 700.0
    }[bewirtschaftung]

    erloes_moor = flaechen_groesse * (bisherige_ertraege_pro_ha + nutzung_erloes_pro_ha_jahr)
    netto_ertrag_moor = erloes_moor - kosten_bauer_jahr

    kosten_pro_t_bauer = (kosten_bauer_jahr / co2_minderung_moor) if co2_minderung_moor > 0 else 0.0
    kosten_pro_t_volk = (kosten_volk_jahr / co2_minderung_moor) if co2_minderung_moor > 0 else 0.0

    if st.session_state.moor_step == 2:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Abgeschiedenes / Eingespartes CO₂", value=f"{co2_minderung_moor:,.1f} t/Jahr")
            st.metric(label="Gesamtkosten / Jahr (Bauer)", value=f"{kosten_bauer_jahr:,.2f} €")
            st.metric(label="Gesamtkosten / Jahr (Volkswirtschaft)", value=f"{kosten_volk_jahr:,.2f} €")
        with col2:
            st.metric(label="Kosten pro Tonne CO₂ (Bauer)", value=f"{kosten_pro_t_bauer:,.2f} € / t CO₂")
            st.metric(label="Kosten pro Tonne CO₂ (Volkswirtschaft)", value=f"{kosten_pro_t_volk:,.2f} € / t CO₂")
            st.metric(label="Netto-Ertrag (Erlös - Kosten Bauer)", value=f"{netto_ertrag_moor:,.2f} €/Jahr")


# ==========================================
# TAB 2: BECCS-BERECHNUNG
# ==========================================
with tab2:
    st.header("BECCS-Berechnung (Carbon Capture & Storage)")

    beccs_technologie = st.selectbox(
        "Technologie zur CO₂-Abscheidung:",
        ["Aminwäsche (Post-Combustion)", "Oxyfuel-Verfahren", "Druckwechseladsorption (PSA)"],
        key="beccs_tech"
    )
    bauflaeche = st.number_input(
        "Baufläche der BECCS-Anlage (m²):",
        min_value=0.0,
        value=2500.0,
        step=100.0,
        key="beccs_flaeche"
    )
    biomasse_herkunft = st.selectbox(
        "Herkunft der Biomasse:",
        ["Regional (< 50 km)", "National (50 - 200 km)", "International (> 200 km)"],
        key="beccs_herkunft"
    )
    biomasse_art = st.selectbox(
        "Woraus besteht die Biomasse (Zusammensetzung):",
        ["Forstrestholz / Altholz", "Landwirtschaftliche Reststoffe (Stroh)", "Spezielle Energiepflanzen (Miscanthus)"],
        key="beccs_art"
    )
    biomasse_menge = st.number_input(
        "Biomasse-Einsatz (t/Jahr):",
        min_value=0.0,
        value=5000.0,
        step=100.0,
        key="beccs_biomasse"
    )
    abscheide_grad = st.slider(
        "CO₂-Abscheidegrad (%):",
        min_value=50,
        max_value=100,
        value=90,
        key="beccs_grad"
    )
    co2_preis = st.number_input(
        "Aktueller CO₂-Zertifikatspreis (€/t CO₂):",
        min_value=0.0,
        value=120.0,
        step=5.0,
        key="beccs_preis"
    )

    tech_kosten_faktor = {
        "Aminwäsche (Post-Combustion)": 90.0,
        "Oxyfuel-Verfahren": 110.0,
        "Druckwechseladsorption (PSA)": 80.0
    }[beccs_technologie]

    herkunft_faktor = {
        "Regional (< 50 km)": 10.0,
        "National (50 - 200 km)": 25.0,
        "International (> 200 km)": 50.0
    }[biomasse_herkunft]

    biomasse_faktor = {
        "Forstrestholz / Altholz": 15.0,
        "Landwirtschaftliche Reststoffe (Stroh)": 20.0,
        "Spezielle Energiepflanzen (Miscanthus)": 40.0
    }[biomasse_art]

    flaechen_kosten_jahr = bauflaeche * 15.0
    co2_abgeschieden = biomasse_menge * 1.2 * (abscheide_grad / 100)

    if co2_abgeschieden > 0:
        gesamtkosten_jahr_beccs = (tech_kosten_faktor + herkunft_faktor + biomasse_faktor) * co2_abgeschieden + flaechen_kosten_jahr
        kosten_pro_tonne_beccs = gesamtkosten_jahr_beccs / co2_abgeschieden
    else:
        gesamtkosten_jahr_beccs = 0.0
        kosten_pro_tonne_beccs = 0.0

    co2_erloes_beccs = co2_abgeschieden * co2_preis
    gewinn_verlust_beccs = co2_erloes_beccs - gesamtkosten_jahr_beccs
    beccs_volk_kosten_jahr = gesamtkosten_jahr_beccs * 0.4

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Abgeschiedenes CO₂", value=f"{co2_abgeschieden:,.1f} t/Jahr")
        st.metric(label="Gesamtkosten / Jahr (Firma)", value=f"{gesamtkosten_jahr_beccs:,.2f} €")
    with col2:
        st.metric(label="Kosten pro Tonne CO₂", value=f"{kosten_pro_tonne_beccs:,.2f} € / t CO₂")
        st.metric(label="Netto-Ertrag (Erlös - Kosten)", value=f"{gewinn_verlust_beccs:,.2f} €/Jahr")


# ==========================================
# TAB 3: 10-JAHRES-VERGLEICH
# ==========================================
with tab3:
    st.header("📊 10-Jahres-Vergleich: Moor & BECCS")

    jahre = list(range(1, 11))

    moor_bauer_ertraege_10j = [netto_ertrag_moor * j for j in jahre]
    moor_volk_kosten_10j = [kosten_volk_jahr * j for j in jahre]
    beccs_firma_kosten_10j = [gesamtkosten_jahr_beccs * j for j in jahre]
    beccs_volk_kosten_10j = [beccs_volk_kosten_jahr * j for j in jahre]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=jahre,
        y=moor_bauer_ertraege_10j,
        mode="lines",
        name="Moor: Erträge Bauern",
        line=dict(color="green", dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=jahre,
        y=moor_volk_kosten_10j,
        mode="lines",
        name="Moor: Kosten Volkswirtschaft",
        line=dict(color="green", dash="solid")
    ))

    fig.add_trace(go.Scatter(
        x=jahre,
        y=beccs_firma_kosten_10j,
        mode="lines",
        name="BECCS: Kosten Firma",
        line=dict(color="blue", dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=jahre,
        y=beccs_volk_kosten_10j,
        mode="lines",
        name="BECCS: Kosten Volkswirtschaft",
        line=dict(color="blue", dash="solid")
    ))

    fig.update_layout(
        title="Entwicklung über 10 Jahre (€)",
        xaxis_title="Jahre",
        yaxis_title="Euro (€)",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
