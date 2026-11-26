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

    # Kompakte Status-Leiste oben (sichtbar ab Schritt 2)
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
            "Niedersachsen": 33497.0,
            "Mecklenburg-Vorpommern": 21822.0
        }

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
                    value=float(kaufpreis_bundesland_map[bundesland_input]),
                    step=500.0,
                    key="input_kaufpreis_ha"
                )
                kaufkosten_tmp = kaufpreis_pro_ha * flaeche_input
            else:
                richtwert_ha = kaufpreis_bundesland_map[bundesland_input]
                kaufkosten_tmp = richtwert_ha * flaeche_input
                st.info(
                    f"Kein Kaufpreis bekannt – für **{bundesland_input}** wird mit einem "
                    f"durchschnittlichen Kaufpreis von **{richtwert_ha:,.0f} €/ha** gerechnet."
                )

            vorbesitzer_ertrag_bekannt = st.checkbox(
                "Kennen Sie die bisherigen Erträge pro ha und Jahr vom Vorbesitzer?",
                value=st.session_state.get("moor_vorbesitzer_bekannt_val", False),
                key="input_vorbesitzer_bekannt"
            )

            if vorbesitzer_ertrag_bekannt:
                ertrag_step1_tmp = st.number_input(
                    "Bisherige Erträge vom Vorbesitzer (€/ha):",
                    min_value=0.0,
                    value=float(bisherige_ertraege_pro_ha),
                    step=50.0,
                    key="input_vorbesitzer_ertrag_ha"
                )

        vorher_input = st.selectbox(
            "Was war die Fläche vorher?",
            ["Ackerland", "Grünland"],
            index=["Ackerland", "Grünland"].index(vorher_nutzung),
            key="input_vorher"
        )

        st.markdown("---")
        if st.button("Weiter →", type="primary", key="btn_weiter_0"):
            st.session_state.moor_bundesland_val = bundesland_input
            st.session_state.moor_flaeche_val = flaeche_input
            st.session_state.moor_typ_val = moor_typ_input
            st.session_state.moor_besitz_val = besitz_input
            st.session_state.moor_kaufkosten_val = kaufkosten_tmp
            st.session_state.moor_vorbesitzer_bekannt_val = vorbesitzer_ertrag_bekannt
            if besitz_input == "Muss gekauft werden" and vorbesitzer_ertrag_bekannt:
                st.session_state.moor_ertrag_val = ertrag_step1_tmp
            st.session_state.moor_vorher_val = vorher_input
            go_next()
            st.rerun()

    # --- SCHRITT 1: ERTRÄGE (BEI BESITZ) & BEWIRTSCHAFTUNG ---
    elif st.session_state.moor_step == 1:
        nav_col1, nav_col2, _ = st.columns([1, 1, 4])
        with nav_col1:
            st.button("← Schritt zurück", on_click=go_back, key="btn_zurueck_1")
        with nav_col2:
            st.button("🏠 Zur Startseite", on_click=go_to_start, key="btn_start_1")

        st.subheader("Schritt 2 von 3: Bisherige Erträge & Bewirtschaftung")

        ertrag_tmp = bisherige_ertraege_pro_ha
        if besitz_status == "Bereits im Besitz":
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
            "Tierhaltung",
            "Photo-Voltaik",
            "Seggen"
        ]
        aktuelle_bew = bewirtschaftung if bewirtschaftung in bew_optionen else "Rohrglanzgras"
        bew_tmp = st.selectbox(
            "Wie möchten Sie wirtschaften?",
            bew_optionen,
            index=bew_optionen.index(aktuelle_bew),
            key="input_bewirtschaftung"
        )

        etab_tmp = None
        etab_detail_tmp = None
        if bew_tmp not in ["Tierhaltung", "Photo-Voltaik"]:
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

    # --- SCHRITT 2: ERNTEFORM, VERWERTUNG, TECHNIK, TRANSPORT, LAGERUNG & AUSWERTUNG ---
    elif st.session_state.moor_step == 2:
        nav_col1, nav_col2, _ = st.columns([1, 1, 4])
        with nav_col1:
            st.button("← Schritt zurück", on_click=go_back, key="btn_zurueck_2")
        with nav_col2:
            st.button("🏠 Zur Startseite", on_click=go_to_start, key="btn_start_2")

        st.subheader("Schritt 3 von 3: Ernteform, Verwertung, Logistik & Auswertung")

        mahd_tmp = mahd_zeitpunkt
        ernteform_tmp = None
        schwarzerle_tmp = None
        verwertung_tmp = None
        folge_tmp = None
        unter_folge_tmp = None
        ballen_winter_tmp = None
        tier_art_tmp = None
        tier_haltung_tmp = None
        tier_vermarktung_tmp = None
        erntetechnik_tmp = None
        transport_bekannt_tmp = "Nein"
        transport_km_tmp = 10.0
        lagerung_geplant_tmp = "Nein"
        lagerung_art_tmp = None

        # A) Rohrglanzgras, Schilf, Rohrkolben, Seggen
        if bewirtschaftung in ["Rohrglanzgras", "Schilf", "Rohrkolben", "Seggen"]:
            mahd_tmp = st.radio(
                f"Wann erfolgt die Mahd bei {bewirtschaftung}?",
                ["Sommermahd", "Wintermahd"],
                key=f"mahd_{bewirtschaftung}"
            )
            ernteform_tmp = st.selectbox(
                "In welcher Form möchten Sie die Biomasse ernten?",
                [
                    "Häckselgut",
                    "Rundballen",
                    "Quaderballen",
                    "Bunde",
                    "Loses Langgut",
                    "Pelletierte Form (mobile Pelletierungsmaschine)",
                    "Brikettierte Form (mobile Brikettierungsmaschine)"
                ],
                key=f"ernteform_{bewirtschaftung}"
            )

            # 1) Häckselgut
            if ernteform_tmp == "Häckselgut":
                bereich_optionen = [
                    "Energetische Verwertung",
                    "Bau- und Werkstoffe",
                    "Gartenbau und Landwirtschaft"
                ]
                if not (bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd"):
                    bereich_optionen.append("Thermische Verwertung")

                verwertung_tmp = st.selectbox(
                    "Wofür soll das Häckselgut genutzt werden?",
                    bereich_optionen,
                    key=f"haeckselfeld_bereich_{bewirtschaftung}"
                )

                if verwertung_tmp == "Thermische Verwertung":
                    folge_tmp = st.selectbox(
                        "Welche thermische Verwertung soll erfolgen?",
                        ["Verbrennung"],
                        key=f"haeckselfeld_thermisch_{bewirtschaftung}"
                    )

                elif verwertung_tmp == "Energetische Verwertung":
                    energie_optionen = []
                    if mahd_tmp == "Sommermahd":
                        energie_optionen.append("Biogasproduktion")
                    if mahd_tmp == "Wintermahd":
                        energie_optionen.append("Direkte Verbrennung")
                    energie_optionen.extend([
                        "Pellets und Briketts",
                        "Zellulose-Ethanol"
                    ])
                    if bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd":
                        energie_optionen.append("Biogasanlage")

                    folge_tmp = st.selectbox(
                        "Welche energetische Verwertung soll erfolgen?",
                        energie_optionen,
                        key=f"haeckselfeld_energie_{bewirtschaftung}"
                    )

                elif verwertung_tmp == "Bau- und Werkstoffe":
                    if bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd":
                        stoff_optionen = [
                            "Dämmplatten",
                            "Faserplatten und Biokunststoffe",
                            "Papier- und Kartonherstellung"
                        ]
                    else:
                        stoff_optionen = [
                            "Einblasdämmung",
                            "Dämmplatten & Leichtbaumatten",
                            "Zuschlagstoff für Lehm- und Kalkputze",
                            "Faserplatten und Biokunststoffe",
                            "Papier- und Kartonherstellung"
                        ]
                    folge_tmp = st.selectbox(
                        "Welche Verwertung im Bereich Bau- und Werkstoffe soll erfolgen?",
                        stoff_optionen,
                        key=f"haeckselfeld_stoff_{bewirtschaftung}"
                    )

                elif verwertung_tmp == "Gartenbau und Landwirtschaft":
                    garten_optionen = [
                        "Torf- und Kompostersatz",
                        "Mulchmaterial",
                        "Pflanzenkohle & Aktivkohle"
                    ]
                    if mahd_tmp == "Wintermahd":
                        garten_optionen.insert(2, "Tiereinstreu")

                    folge_tmp = st.selectbox(
                        "Welche Nutzung im Bereich Gartenbau und Landwirtschaft soll erfolgen?",
                        garten_optionen,
                        key=f"haeckselfeld_garten_{bewirtschaftung}"
                    )

            # 2) Rundballen / Quaderballen
            elif ernteform_tmp in ["Rundballen", "Quaderballen"]:
                if mahd_tmp == "Wintermahd":
                    ballen_winter_tmp = st.selectbox(
                        "Welche Weiterverarbeitung / Pressung für die Ballen (Wintermahd) ist geplant?",
                        ["Keine zusätzliche Verarbeitung", "Pellets", "Briketts", "Pressen"],
                        key=f"ballen_winter_opt_{bewirtschaftung}"
                    )

                if bewirtschaftung == "Rohrkolben":
                    basis_verwertung = [
                        "Dämmen und Bauen",
                        "Werkstoffe",
                        "Thermische Verwertung",
                        "Samen",
                        "Fasern",
                        "Gartenbausubstrate",
                        "Einstreu",
                        "Plattformchemikalien"
                    ]
                elif bewirtschaftung == "Schilf":
                    if mahd_tmp == "Sommermahd":
                        basis_verwertung = [
                            "Dämmplatten",
                            "Kultursubstrate",
                            "Plattformchemikalien"
                        ]
                    else:
                        basis_verwertung = [
                            "Dämmen",
                            "Werkstoffe",
                            "Thermische Verwertung",
                            "Kultursubstrate",
                            "Einstreu",
                            "Bio-Aktivkohle",
                            "Plattformchemikalien"
                        ]
                elif bewirtschaftung == "Seggen":
                    basis_verwertung = [
                        "Thermische Verwertung",
                        "Pferdeheu",
                        "Einstreu",
                        "Bau- & Dämmstoffe",
                        "Gartenbausubstrate",
                        "Kohle"
                    ]
                else:  # Rohrglanzgras
                    basis_verwertung = [
                        "Pferdeheu",
                        "Raufutter",
                        "Proteinkonzentrat",
                        "Einstreu",
                        "Thermische Verwertung",
                        "Bau- & Dämmstoffe"
                    ]

                verwertung_tmp = st.selectbox(
                    f"Welche Verwertung für {ernteform_tmp} streben Sie an?",
                    basis_verwertung,
                    key=f"ballen_verwertung_{bewirtschaftung}"
                )

            # 3) Bunde
            elif ernteform_tmp == "Bunde":
                if bewirtschaftung == "Rohrkolben":
                    basis_verwertung = [
                        "Dämmen und Bauen",
                        "Werkstoffe",
                        "Thermische Verwertung",
                        "Samen",
                        "Fasern",
                        "Gartenbausubstrate",
                        "Einstreu",
                        "Plattformchemikalien"
                    ]
                elif bewirtschaftung == "Schilf":
                    if mahd_tmp == "Sommermahd":
                        basis_verwertung = [
                            "Dämmplatten",
                            "Kultursubstrate",
                            "Plattformchemikalien"
                        ]
                    else:
                        basis_verwertung = [
                            "Dachreed",
                            "Dämmen",
                            "Werkstoffe",
                            "Thermische Verwertung",
                            "Kultursubstrate",
                            "Einstreu",
                            "Bio-Aktivkohle",
                            "Plattformchemikalien"
                        ]
                elif bewirtschaftung == "Seggen":
                    basis_verwertung = [
                        "Thermische Verwertung",
                        "Pferdeheu",
                        "Einstreu",
                        "Bau- & Dämmstoffe",
                        "Gartenbausubstrate",
                        "Kohle"
                    ]
                else:  # Rohrglanzgras
                    basis_verwertung = [
                        "Pferdeheu",
                        "Raufutter",
                        "Proteinkonzentrat",
                        "Einstreu",
                        "Thermische Verwertung",
                        "Bau- & Dämmstoffe"
                    ]

                verwertung_tmp = st.selectbox(
                    "Welche Verwertung für Bunde streben Sie an?",
                    basis_verwertung,
                    key=f"bunde_verwertung_{bewirtschaftung}"
                )

            # 4) Loses Langgut
            elif ernteform_tmp == "Loses Langgut":
                verwertung_tmp = st.selectbox(
                    "Wie soll das lose Langgut genutzt werden?",
                    ["Direkte Nutzung", "Weiterverarbeitung"],
                    key=f"langgut_bereich_{bewirtschaftung}"
                )

                if verwertung_tmp == "Direkte Nutzung":
                    if bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd":
                        direkt_optionen = [
                            "Raufutter",
                            "Heu",
                            "Silage",
                            "Dünger",
                            "Mulchmaterial"
                        ]
                    elif bewirtschaftung == "Schilf" and mahd_tmp == "Wintermahd":
                        direkt_optionen = [
                            "Heu",
                            "Einstreu",
                            "Dünger",
                            "Mulchmaterial"
                        ]
                    else:
                        direkt_optionen = [
                            "Raufutter",
                            "Heu",
                            "Silage",
                            "Einstreu",
                            "Dünger",
                            "Mulchmaterial"
                        ]
                    folge_tmp = st.selectbox(
                        "Welche direkte Nutzung soll erfolgen?",
                        direkt_optionen,
                        key=f"langgut_direkt_{bewirtschaftung}"
                    )
                else:  # Weiterverarbeitung
                    if bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd":
                        weiter_optionen = [
                            "Stationäre Pelletieranlage",
                            "Briketts",
                            "Biogassubstrat"
                        ]
                    else:
                        weiter_optionen = [
                            "Stationäre Pelletieranlage",
                            "Briketts",
                            "Einblasdämmung",
                            "Biogassubstrat",
                            "Pflanzenkohle"
                        ]
                        if bewirtschaftung == "Schilf" and mahd_tmp == "Wintermahd":
                            weiter_optionen.append("Sortierung zu Dachreetbunden")

                    folge_tmp = st.selectbox(
                        "Welche Weiterverarbeitung soll erfolgen?",
                        weiter_optionen,
                        key=f"langgut_weiter_{bewirtschaftung}"
                    )

            # 5) Pelletierte oder Brikettierte Form (mobile Maschine)
            else:
                if bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd":
                    pellet_optionen = [
                        "Raufutterersatz",
                        "Organischer Dünger",
                        "Torfersatz in Kultursubstraten",
                        "Mulch-Pellets",
                        "Biokunststoffe & Spritzguss",
                        "Faserplatten & Dämmstoffe",
                        "Biogas-Substrat",
                        "Papier herstellen"
                    ]
                elif bewirtschaftung == "Schilf" and mahd_tmp == "Wintermahd":
                    pellet_optionen = [
                        "Verbrennen",
                        "Tiereinstreu",
                        "Organischer Dünger",
                        "Torfersatz in Kultursubstraten",
                        "Mulch-Pellets",
                        "Biokunststoffe & Spritzguss",
                        "Faserplatten & Dämmstoffe",
                        "Pflanzenkohle & Aktivkohle",
                        "Papier herstellen"
                    ]
                else:
                    pellet_optionen = [
                        "Verbrennen",
                        "Tiereinstreu",
                        "Raufutterersatz",
                        "Organischer Dünger",
                        "Torfersatz in Kultursubstraten",
                        "Mulch-Pellets",
                        "Biokunststoffe & Spritzguss",
                        "Faserplatten & Dämmstoffe",
                        "Pflanzenkohle & Aktivkohle",
                        "Biogas-Substrat",
                        "Papier herstellen"
                    ]
                verwertung_tmp = st.selectbox(
                    f"Welche Verwertung für '{ernteform_tmp}' streben Sie an?",
                    pellet_optionen,
                    key=f"pellet_brikett_verwertung_{bewirtschaftung}"
                )
                folge_tmp = verwertung_tmp

        # B) Schwarzerle: Stammholz vs. Hackschnitzel
        elif bewirtschaftung == "Schwarzerle":
            schwarzerle_tmp = st.radio(
                "Ernten Sie bei der Schwarzerle Stammholz oder Hackschnitzel?",
                ["Stammholz", "Hackschnitzel"],
                key="schwarzerle_ernte_art"
            )
            if schwarzerle_tmp == "Hackschnitzel":
                verwertung_tmp = st.selectbox(
                    "Welche Verwertung für Schwarzerle-Hackschnitzel streben Sie an?",
                    ["Thermische Verwertung", "Mulch", "Pilzzucht", "Biofilter"],
                    key="sel_verwertung_schwarzerle_hackschnitzel"
                )
            else:
                verwertung_tmp = st.selectbox(
                    "Welche Verwertung streben Sie bei Schwarzerle (Stammholz) an?",
                    ["Wertholz", "Plattenwerkstoffe", "Thermische Verwertung"],
                    key="sel_verwertung_schwarzerle_stammholz"
                )

        # C) Torfmoos
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

        # D) Nasswiese
        elif bewirtschaftung == "Nasswiese":
            verwertung_tmp = st.selectbox(
                "Welche Nutzung auf der Nasswiese streben Sie an?",
                [
                    "Tierhaltung",
                    "Landwirtschaftliche Nutzung",
                    "Stoffliche und industrielle Verwertung",
                    "Energetische Verwertung"
                ],
                key="sel_verwertung_nasswiese"
            )

            if verwertung_tmp == "Tierhaltung":
                tier_art_tmp = st.radio(
                    "Welche Tierart möchten Sie halten?",
                    ["Wasserbüffel", "Robustrinder"],
                    key="nasswiese_tierart"
                )
                tier_haltung_tmp = st.selectbox(
                    "Wie wird die Bewirtschaftung durchgeführt?",
                    ["Ganzjährig", "Extensiv", "Vollweidesystem", "Teilweidesystem"],
                    key="nasswiese_tierhaltung_system"
                )
                tier_vermarktung_tmp = st.radio(
                    "Wie soll die Nutzung / Vermarktung erfolgen?",
                    ["Tier selbst verkaufen", "Als Fleischprodukt verkaufen", "Landschaftspflege"],
                    key="nasswiese_tier_vermarktung"
                )
                folge_tmp = f"{tier_art_tmp} – {tier_haltung_tmp} – {tier_vermarktung_tmp}"

            elif verwertung_tmp == "Landwirtschaftliche Nutzung":
                folge_tmp = st.selectbox(
                    "Welche landwirtschaftliche Nutzung soll erfolgen?",
                    ["Raufutter", "Heu", "Silage", "Einstreu", "Dünger"],
                    key="nasswiese_landwirtschaft"
                )

            elif verwertung_tmp == "Stoffliche und industrielle Verwertung":
                folge_tmp = st.selectbox(
                    "Welche stoffliche und industrielle Verwertung soll erfolgen?",
                    [
                        "Papier- und Kartonherstellung",
                        "Faserguss-Produkte",
                        "Dämm- und Baustoffe",
                        "Biokunststoffe",
                        "Torfersatz"
                    ],
                    key="nasswiese_stofflich"
                )

            elif verwertung_tmp == "Energetische Verwertung":
                folge_tmp = st.selectbox(
                    "Welche energetische Verwertung soll erfolgen?",
                    [
                        "Biogasproduktion",
                        "Brennstoff-Pellets / Briketts",
                        "Direkte Verbrennung",
                        "Pflanzenkohle"
                    ],
                    key="nasswiese_energetisch"
                )
                if folge_tmp == "Direkte Verbrennung":
                    unter_folge_tmp = st.radio(
                        "In welcher Form erfolgt die direkte Verbrennung?",
                        ["Häckselgut", "Ballen"],
                        key="nasswiese_direkt_verbrennung_form"
                    )

        # E) Tierhaltung (direkt gewählt)
        elif bewirtschaftung == "Tierhaltung":
            verwertung_tmp = "Tierhaltung"
            tier_art_tmp = st.radio(
                "Welche Tierart möchten Sie halten?",
                ["Wasserbüffel", "Robustrinder"],
                key="tierhaltung_art_direkt"
            )
            tier_haltung_tmp = st.selectbox(
                "Wie wird die Bewirtschaftung durchgeführt?",
                ["Ganzjährig", "Extensiv", "Vollweidesystem", "Teilweidesystem"],
                key="tierhaltung_system_direkt"
            )
            tier_vermarktung_tmp = st.radio(
                "Wie soll die Nutzung / Vermarktung erfolgen?",
                ["Tier selbst verkaufen", "Als Fleischprodukt verkaufen", "Landschaftspflege"],
                key="tierhaltung_vermarktung_direkt"
            )
            folge_tmp = f"{tier_art_tmp} – {tier_haltung_tmp} – {tier_vermarktung_tmp}"

        # Allgemeine Folgeabfragen
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

        if verwertung_tmp == "Werkstoffe":
            folge_tmp = st.selectbox(
                "Welche Werkstoffvariante möchten Sie herstellen?",
                ["Plattenwerkstoffe", "Formteile"],
                key="folge_werkstoffe"
            )

        if verwertung_tmp == "Thermische Verwertung" and ernteform_tmp != "Häckselgut":
            if bewirtschaftung == "Schwarzerle":
                folge_tmp = st.selectbox(
                    "Wie möchten Sie die Schwarzerle thermisch nutzen?",
                    ["Direkte Verbrennung"],
                    key="folge_thermisch_schwarzerle"
                )
            elif bewirtschaftung == "Schilf":
                folge_tmp = st.selectbox(
                    "Wie möchten Sie das Schilf thermisch nutzen?",
                    ["Verbrennung", "Briketts", "Pellets", "Ethanol"],
                    key="folge_thermisch_schilf"
                )
            else:
                folge_tmp = st.selectbox(
                    "Wie möchten Sie die Biomasse thermisch nutzen?",
                    ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung", "Biogas"],
                    key="folge_thermisch"
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

        # Sonderfälle bei Schilf: Ethanol (thermische Verwertung) und Biogasanlage (energetische Verwertung)
        ist_schilf_ethanol = (
            bewirtschaftung == "Schilf"
            and verwertung_tmp == "Thermische Verwertung"
            and folge_tmp == "Ethanol"
        )
        ist_schilf_biogasanlage = (
            bewirtschaftung == "Schilf"
            and verwertung_tmp == "Energetische Verwertung"
            and folge_tmp == "Biogasanlage"
        )
        keine_ernte_und_kein_transport = ist_schilf_ethanol or ist_schilf_biogasanlage

        # Erntemaschinen: entfällt bei PV, Tierhaltung, Schwarzerle sowie Schilf-Ethanol / Schilf-Biogasanlage
        ist_tierhaltung = (
            bewirtschaftung == "Tierhaltung"
            or (bewirtschaftung == "Nasswiese" and verwertung_tmp == "Tierhaltung")
        )
        if (
            bewirtschaftung not in ["Photo-Voltaik", "Tierhaltung", "Schwarzerle"]
            and not ist_tierhaltung
            and not keine_ernte_und_kein_transport
        ):
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

        # Transport-Abfrage bei Häckselgut, Dachschilf/Dachreed, Bunden, losem Langgut, Ballen und Pellets/Briketts
        hat_transport_gut = (
            not keine_ernte_und_kein_transport
            and (
                ernteform_tmp in [
                    "Häckselgut",
                    "Rundballen",
                    "Quaderballen",
                    "Bunde",
                    "Loses Langgut",
                    "Pelletierte Form (mobile Pelletierungsmaschine)",
                    "Brikettierte Form (mobile Brikettierungsmaschine)"
                ]
                or verwertung_tmp == "Dachreed"
                or folge_tmp in [
                    "Sortierung zu Dachreetbunden",
                    "Pellets",
                    "Briketts",
                    "Pellets und Briketts",
                    "Stationäre Pelletieranlage",
                    "Brennstoff-Pellets / Briketts"
                ]
                or unter_folge_tmp in ["Häckselgut", "Ballen"]
            )
        )

        # Lagerung entfällt für Bunde und Loses Langgut
        hat_lager_option = (
            bewirtschaftung not in ["Photo-Voltaik", "Tierhaltung"]
            and not ist_tierhaltung
            and ernteform_tmp not in ["Bunde", "Loses Langgut"]
        )

        if hat_transport_gut or hat_lager_option:
            st.markdown("---")
            if hat_transport_gut and hat_lager_option:
                st.subheader("Transport & Lagerung")
            elif hat_transport_gut:
                st.subheader("Transport")
            else:
                st.subheader("Lagerung")

        if hat_transport_gut:
            transport_bekannt_tmp = st.radio(
                "Wissen Sie, wie weit das Gut vom Hof zur Verwertungsstelle transportiert werden soll?",
                ["Ja", "Nein"],
                index=0 if transport_bekannt == "Ja" else 1,
                key="moor_transport_bekannt"
            )
            if transport_bekannt_tmp == "Ja":
                distanz_optionen = [2.5, 5.0, 10.0, 20.0, 30.0, 50.0]
                transport_km_tmp = st.selectbox(
                    "Transportentfernung vom Hof zur Verwertungsstelle (km):",
                    distanz_optionen,
                    format_func=lambda x: f"{x:g} km",
                    index=distanz_optionen.index(transport_km) if transport_km in distanz_optionen else 2,
                    key="moor_transport_km"
                )

        if hat_lager_option:
            lagerung_geplant_tmp = st.radio(
                "Möchten Sie die Produkte lagern?",
                ["Ja", "Nein"],
                index=0 if lagerung_geplant == "Ja" else 1,
                key="moor_lagerung_geplant"
            )
            if lagerung_geplant_tmp == "Ja":
                # Verfügbare Lageroptionen je nach Ernteform / Produkt
                ist_pellet_oder_brikett = (
                    ernteform_tmp in [
                        "Pelletierte Form (mobile Pelletierungsmaschine)",
                        "Brikettierte Form (mobile Brikettierungsmaschine)"
                    ]
                    or folge_tmp in [
                        "Pellets",
                        "Briketts",
                        "Pellets und Briketts",
                        "Stationäre Pelletieranlage",
                        "Brennstoff-Pellets / Briketts"
                    ]
                    or ballen_winter_tmp in ["Pellets", "Briketts"]
                )

                if ist_pellet_oder_brikett:
                    lager_optionen = ["In einer Halle"]
                elif ernteform_tmp == "Häckselgut":
                    lager_optionen = ["In einer Halle", "Auf einer freien Fläche mit Abdeckung"]
                else:
                    lager_optionen = [
                        "In einer Halle",
                        "In einem Altgebäude",
                        "Auf einer freien Fläche mit Abdeckung"
                    ]

                lagerung_art_tmp = st.selectbox(
                    "Wie sollen die Produkte gelagert werden?",
                    lager_optionen,
                    index=lager_optionen.index(lagerung_art) if lagerung_art in lager_optionen else 0,
                    key="moor_lagerung_art"
                )

        st.session_state.moor_mahd_zeitpunkt_val = mahd_tmp
        st.session_state.moor_ernteform_val = ernteform_tmp
        st.session_state.moor_schwarzerle_ernte_val = schwarzerle_tmp
        st.session_state.moor_verwertung_val = verwertung_tmp
        st.session_state.moor_folge_val = folge_tmp
        st.session_state.moor_unter_folge_val = unter_folge_tmp
        st.session_state.moor_ballen_winter_val = ballen_winter_tmp
        st.session_state.moor_tier_art_val = tier_art_tmp
        st.session_state.moor_tier_haltung_val = tier_haltung_tmp
        st.session_state.moor_tier_vermarktung_val = tier_vermarktung_tmp
        st.session_state.moor_erntetechnik_val = erntetechnik_tmp
        st.session_state.moor_transport_bekannt_val = transport_bekannt_tmp
        st.session_state.moor_transport_km_val = transport_km_tmp
        st.session_state.moor_lagerung_geplant_val = lagerung_geplant_tmp
        st.session_state.moor_lagerung_art_val = lagerung_art_tmp

        mahd_zeitpunkt = mahd_tmp
        ernteform_biomasse = ernteform_tmp
        schwarzerle_ernte = schwarzerle_tmp
        verwertung = verwertung_tmp
        folge_auswahl = folge_tmp
        unter_folge_auswahl = unter_folge_tmp
        ballen_winter_option = ballen_winter_tmp
        tier_art = tier_art_tmp
        tier_haltungssystem = tier_haltung_tmp
        tier_vermarktung = tier_vermarktung_tmp
        erntetechnik = erntetechnik_tmp
        transport_bekannt = transport_bekannt_tmp
        transport_km = transport_km_tmp
        lagerung_geplant = lagerung_geplant_tmp
        lagerung_art = lagerung_art_tmp

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

    # Etablierungskosten & laufende Pflegekosten (€/ha/Jahr)
    if bewirtschaftung == "Schilf" and ernteform_biomasse == "Loses Langgut":
        # Bei losem Langgut gelten die spezifischen Produktionskosten zusätzlich zu den Grundstückskosten
        if etablierungs_art == "Erstetablierung":
            etablierung_kosten_pro_ha_jahr = (
                680.00 if etablierungs_detail == "Anpflanzung mit Jungpflanzen" else 410.00
            )
        else:
            etablierung_kosten_pro_ha_jahr = 380.00
        laufende_kosten_pro_ha_jahr = 0.0
    elif bewirtschaftung == "Schilf":
        if etablierungs_art == "Erstetablierung":
            etablierung_kosten_pro_ha_jahr = (
                378.50 if etablierungs_detail == "Anpflanzung mit Jungpflanzen" else 247.22
            )
        else:
            etablierung_kosten_pro_ha_jahr = 224.00
        laufende_kosten_pro_ha_jahr = 693.75
    else:
        if etablierungs_art == "Erstetablierung":
            etablierung_kosten_pro_ha_jahr = (
                450.0 if etablierungs_detail == "Anpflanzung mit Jungpflanzen" else 250.0
            )
        elif etablierungs_art == "Natürliche Sukzession":
            etablierung_kosten_pro_ha_jahr = 80.0
        else:
            etablierung_kosten_pro_ha_jahr = 0.0
        laufende_kosten_pro_ha_jahr = 0.0

    # Sonderfall-Prüfung für Schilf (Ethanol vs. Biogasanlage)
    sonderkosten_schilf_pro_ha_jahr = 0.0
    entfaellt_ernte_und_transport = False
    if bewirtschaftung == "Schilf" and verwertung == "Thermische Verwertung" and folge_auswahl == "Ethanol":
        sonderkosten_schilf_pro_ha_jahr = 2387.00
        entfaellt_ernte_und_transport = True
    elif bewirtschaftung == "Schilf" and verwertung == "Energetische Verwertung" and folge
