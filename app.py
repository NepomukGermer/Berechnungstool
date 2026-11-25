import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Klima- & Berechnungs-Hub", layout="wide")
st.title("🌱 Klima- & Berechnungs-Hub")

tab1, tab2, tab3 = st.tabs([
    "🌱 Moor-Berechnung",
    "⚡ BECCS-Berechnung",
    "📊 Vergleich & Volkswirtschaft"
])

# ==========================================
# TAB 1: MOOR-WIEDERVERNÄSSUNG (DETAILLIERT)
# ==========================================
with tab1:
    st.header("Moor-Wiedervernässung & Paludikultur")

    # 1. Fläche in Hektar
    flaechen_groesse = st.number_input(
        "Wie viel Hektar (ha) möchten Sie wiedervernässen?",
        min_value=0.1,
        value=10.0,
        step=0.1,
        key="moor_flaeche"
    )

    # 2. Eigentum oder Kauf
    besitz_status = st.radio(
        "Besitzen Sie die Fläche bereits oder müssen Sie sie kaufen?",
        ["Bereits im Besitz", "Muss gekauft werden"],
        key="moor_besitz"
    )

    kaufkosten_gesamt = 0.0
    vorbesitzer_ertrag_bekannt = False

    if besitz_status == "Muss gekauft werden":
        preis_bekannt = st.radio(
            "Kennen Sie den Kaufpreis für das Grundstück?",
            ["Ja", "Nein"],
            key="moor_preis_bekannt"
        )
        if preis_bekannt == "Ja":
            kaufpreis_pro_ha = st.number_input(
                "Kaufpreis (€/ha):",
                min_value=0.0,
                value=15000.0,
                step=500.0,
                key="moor_kaufpreis_ha"
            )
            kaufkosten_gesamt = kaufpreis_pro_ha * flaechen_groesse
        else:
            # Schätzwert, falls Preis unbekannt
            kaufkosten_gesamt = 14000.0 * flaechen_groesse
            st.info("Kein Kaufpreis bekannt – es wird mit einem Richtwert von 14.000 €/ha gerechnet.")

        vorbesitzer_ertrag_bekannt = st.checkbox(
            "Kennen Sie die bisherigen Erträge pro ha und Jahr vom Vorbesitzer?",
            value=False,
            key="moor_vorbesitzer_ertrag"
        )

    # 3. Vorherige Nutzung & Moortyp (in beiden Fällen abfragbar)
    col_a, col_b = st.columns(2)
    with col_a:
        vorher_nutzung = st.selectbox(
            "Was war die Fläche vorher?",
            ["Ackerland", "Grünland"],
            key="moor_vorher_nutzung"
        )
    with col_b:
        moor_typ = st.selectbox(
            "Um welchen Moortyp handelt es sich?",
            ["Hochmoor", "Niedermoor", "Weiß ich nicht"],
            key="moor_typ"
        )

    # 4. Bisherige Erträge (€/ha/Jahr) bei Besitz oder bekanntem Vorbesitzer-Ertrag
    bisherige_ertraege_pro_ha = 0.0
    if besitz_status == "Bereits im Besitz" or vorbesitzer_ertrag_bekannt:
        bisherige_ertraege_pro_ha = st.number_input(
            "Wie hoch waren die bisherigen Erträge auf der Fläche (€/ha und Jahr)?",
            min_value=0.0,
            value=800.0,
            step=50.0,
            key="moor_bisher_ertrag"
        )

    st.markdown("---")
    st.subheader("Nutzung & Bewirtschaftung nach Wiedervernässung")

    # 5. Bewirtschaftungsart
    bewirtschaftung = st.selectbox(
        "Wie möchten Sie wirtschaften?",
        [
            "Rohrglanzgras",
            "Schwarzerle",
            "Nasswiese",
            "Schilf",
            "Rohrkolben",
            "Torfmoos",
            "Wasserbüffel",
            "Photo-Voltaik",
            "Seggen"
        ],
        key="moor_bewirtschaftung"
    )

    # 6. Natürliche Sukzession vs. Erstetablierung (außer Wasserbüffel und PV)
    etablierungs_art = None
    etablierungs_detail = None
    if bewirtschaftung not in ["Wasserbüffel", "Photo-Voltaik"]:
        etablierungs_art = st.radio(
            "Möchten Sie natürliche Sukzession oder eine Erstetablierung durchführen?",
            ["Natürliche Sukzession", "Erstetablierung"],
            key="moor_etablierung"
        )
        if etablierungs_art == "Erstetablierung":
            etablierungs_detail = st.radio(
                "Wie erfolgt die Erstetablierung?",
                ["Aussaat", "Anpflanzung mit Jungpflanzen"],
                key="moor_etablierung_detail"
            )

    # 7. Verwertungsoptionen je nach Bewirtschaftung
    verwertung = None
    folge_auswahl = None
    tier_art = None
    tier_vermarktung = None
    erntetechnik = None
    erntezeitpunkt = None

    if bewirtschaftung == "Rohrkolben":
        verwertung = st.selectbox(
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
            key="verwertung_rohrkolben"
        )

    elif bewirtschaftung == "Schilf":
        verwertung = st.selectbox(
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
            key="verwertung_schilf"
        )

    elif bewirtschaftung == "Torfmoos":
        verwertung = st.selectbox(
            "Was möchten Sie mit Torfmoos tun?",
            [
                "Kultursubstrate herstellen",
                "Saatgut ernten",
                "Verbands- & Hygieneartikel",
                "Dämm- & Verpackungsmaterial",
                "Absorptionsmittel & Wasserfilter"
            ],
            key="verwertung_torfmoos"
        )

    elif bewirtschaftung == "Schwarzerle":
        verwertung = st.selectbox(
            "Welche Verwertung streben Sie bei Schwarzerle an?",
            ["Wertholz", "Plattenwerkstoffe", "Heizen"],
            key="verwertung_schwarzerle"
        )

    elif bewirtschaftung == "Nasswiese":
        verwertung = st.selectbox(
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
            key="verwertung_nasswiese"
        )

    elif bewirtschaftung == "Seggen":
        verwertung = st.selectbox(
            "Welche Verwertung streben Sie bei Seggen an?",
            [
                "Verbrennung",
                "Pferdeheu",
                "Einstreu",
                "Bau- & Dämmstoffe",
                "Gartenbausubstrate",
                "Kohle"
            ],
            key="verwertung_seggen"
        )

    elif bewirtschaftung == "Rohrglanzgras":
        verwertung = st.selectbox(
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
            key="verwertung_rohrglanzgras"
        )

    # 8. Anschlussfragen je nach gewählter Verwertung
    if verwertung in ["Dämmen und Bauen", "Bau- & Dämmstoffe"]:
        folge_auswahl = st.selectbox(
            "Welche Dämm- bzw. Bauprodukte möchten Sie herstellen?",
            ["Einblasdämmung", "Dämmmatten", "Dämmplatten", "Plattenwerkstoffe"],
            key="folge_daemmung"
        )

    if bewirtschaftung == "Schilf" and verwertung == "Dämmen":
        folge_auswahl = st.selectbox(
            "Was möchten Sie aus Schilf zum Dämmen herstellen?",
            ["Dämmplatten", "Putzträger"],
            key="folge_schilf_daemmen"
        )

    if verwertung in ["Werkstoffe & Papier", "Zellulose & Papier", "Papier"]:
        folge_auswahl = st.selectbox(
            "Welche Werkstoff- bzw. Papiervariante möchten Sie herstellen?",
            ["Plattenwerkstoffe", "Zellulosefasern für Papier", "Formteile"],
            key="folge_werkstoffe_papier"
        )

    if verwertung in ["Heizen", "Verbrennung"]:
        folge_auswahl = st.selectbox(
            "Wie möchten Sie heizen bzw. die Biomasse thermisch nutzen?",
            ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung", "Heu", "Biogas"],
            key="folge_heizen"
        )

    if verwertung in ["Samen", "Saatgut ernten", "Fasern"]:
        folge_auswahl = st.selectbox(
            "Wie möchten Sie Samen bzw. Fasern nutzen?",
            [
                "Samen zur Weitervermehrung nutzen",
                "Fasern als Füllfaser verwenden",
                "Fasern als Dämmfaser verwenden"
            ],
            key="folge_samen_fasern"
        )

    if bewirtschaftung == "Torfmoos" and verwertung == "Kultursubstrate herstellen":
        folge_auswahl = st.selectbox(
            "Welches Substrat-Ziel verfolgen Sie bei Torfmoos?",
            [
                "Fossiler Weißtorf (Vergleich / Ersatz)",
                "Spezialsubstrate für die Orchideenzucht"
            ],
            key="folge_torfmoos_substrat"
        )

    if verwertung == "Tiere halten":
        folge_auswahl = st.selectbox(
            "Wie möchten Sie die Tiere halten?",
            ["Ganzjährig", "Extensiv", "Vollweidesystem", "Teilweidesystem"],
            key="folge_tierhaltung_system"
        )
        tier_art = st.radio(
            "Welche Tierart möchten Sie halten?",
            ["Wasserbüffel", "Robustrinder"],
            key="folge_tierart"
        )
        tier_vermarktung = st.radio(
            "Was ist Ihr Schwerpunkt bei der Tierhaltung?",
            ["Fleisch verkaufen", "Züchten und Tiere verkaufen"],
            key="folge_tier_vermarktung"
        )

    if verwertung == "Raufutter gewinnen":
        folge_auswahl = st.selectbox(
            "Welche Raufutter-Form möchten Sie gewinnen?",
            ["Heu", "Silage", "Einstreu"],
            key="folge_raufutter"
        )

    # 9. Erntemaschinen (alle Pflanzenarten außer PV, Wasserbüffel und Schwarzerle)
    if bewirtschaftung not in ["Photo-Voltaik", "Wasserbüffel", "Schwarzerle"]:
        erntetechnik = st.selectbox(
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

    # 10. Häckselgut -> Sommer- oder Winterernte
    if verwertung == "Häckselgut":
        erntezeitpunkt = st.radio(
            "Wann erfolgt die Ernte für Häckselgut?",
            ["Sommerernte", "Winterernte"],
            key="moor_erntezeitpunkt_haeckselfutter"
        )

    # ==========================================
    # BERECHNUNGSLOGIK MOOR
    # ==========================================
    moor_basis_co2 = {
        "Hochmoor": 28.0,
        "Niedermoor": 24.0,
        "Weiß ich nicht": 22.0
    }[moor_typ]
    vorher_aufschlag = 1.15 if vorher_nutzung == "Ackerland" else 1.0
    co2_minderung_moor = flaechen_groesse * moor_basis_co2 * vorher_aufschlag

    # Jährliche Bewirtschaftungs- & Etablierungskosten (auf 10 Jahre umgelegt)
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

    # Kosten für den Bauern pro Jahr
    kosten_bauer_jahr = (
        flaechen_groesse * (etablierung_kosten_pro_ha_jahr + technik_kosten_pro_ha_jahr)
        + kauf_annuitaet_jahr
    )

    # Volkswirtschaftliche Kosten pro Jahr (inkl. Fördermittel / Wiedervernässungsmaßnahmen)
    kosten_volk_jahr = (
        flaechen_groesse * 850.0
        + flaechen_groesse * etablierung_kosten_pro_ha_jahr
        + kauf_annuitaet_jahr
    )

    # Erlöse pro Jahr (bisherige Erträge + geschätzter Paludikultur-/Nutzungserlös)
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

    # Grüne gestrichelte Linie: Moor – Erträge der Bauern über 10 Jahre
    fig.add_trace(go.Scatter(
        x=jahre,
        y=moor_bauer_ertraege_10j,
        mode="lines",
        name="Moor: Erträge Bauern",
        line=dict(color="green", dash="dash")
    ))

    # Grüne durchgezogene Linie: Moor – Kosten für die Volkswirtschaft über 10 Jahre
    fig.add_trace(go.Scatter(
        x=jahre,
        y=moor_volk_kosten_10j,
        mode="lines",
        name="Moor: Kosten Volkswirtschaft",
        line=dict(color="green", dash="solid")
    ))

    # Blaue gestrichelte Linie: BECCS – Kosten für die Betreiberfirma über 10 Jahre
    fig.add_trace(go.Scatter(
        x=jahre,
        y=beccs_firma_kosten_10j,
        mode="lines",
        name="BECCS: Kosten Firma",
        line=dict(color="blue", dash="dash")
    ))

    # Blaue durchgezogene Linie: BECCS – Kosten für die Volkswirtschaft über 10 Jahre
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
