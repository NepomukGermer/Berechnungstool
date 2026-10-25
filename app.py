import streamlit as st
import pandas as pd

st.title("🌱 Klima- & Berechnungs-Hub")

# Oben zwei Reiter (Fenster) erstellen
tab1, tab2 = st.tabs(["🌱 Moor-Berechnungs-Tool", "⚡ BECCS-Berechnungs-Tool"])

with tab1:
    st.header("Moor-Berechnung")
    
    moor_typ = st.selectbox("Moor-Typ:", ["Hochmoor", "Niedermoor"], key="moor_typ")
    bundesland = st.selectbox("Bundesland:", ["Niedersachsen", "Bayern", "Brandenburg", "Schleswig-Holstein"], key="bundesland")

    # Flächengröße in Zehntelschritten (0.1)
    flaechen_groesse = st.number_input("Flächengröße (ha):", value=10.0, step=0.1, key="moor_flaeche")
    torf_maechtigkeit = st.number_input("Torfmächtigkeit (m):", value=2.0, step=0.1, key="moor_torf")

    # Einnahmen in €/ha, ohne Nachkommastellen (Ganzzahlen)
    aktuelle_einnahmen_pro_ha = st.number_input("Aktuelle Einnahmen (€/ha):", value=5000, step=1, format="%d", key="moor_einnahmen")

    # Berechnungs-Logik Moor
    faktor_moor = 1.5 if moor_typ == "Hochmoor" else 1.2
    gesamt_einnahmen = aktuelle_einnahmen_pro_ha * flaechen_groesse
    ergebnis_wert = (flaechen_groesse * torf_maechtigkeit * faktor_moor * 1000) + gesamt_einnahmen

    st.metric(label="Berechneter Zielwert (Moor)", value=f"{ergebnis_wert:,.2f} €")

    st.subheader("Verlaufskurve (Prognose Moor)")
    jahre = list(range(1, 11))
    verlauf = [ergebnis_wert * (1 + i * 0.05) for i in range(10)]
    df_moor = pd.DataFrame({"Jahr": jahre, "Wert": verlauf})
    st.line_chart(df_moor.set_index("Jahr"))

with tab2:
    st.header("BECCS-Berechnung (Carbon Capture & Storage)")
    
    # 1. Technologie zur CO2-Abscheidung
    beccs_technologie = st.selectbox(
        "Technologie zur CO₂-Abscheidung:", 
        ["Aminwäsche (Post-Combustion)", "Oxyfuel-Verfahren", "Druckwechseladsorption (PSA)"]
    )
    
    # 2. Baufläche der BECCS-Anlage
    bauflaeche = st.number_input("Baufläche der BECCS-Anlage (m²):", value=2500.0, step=100.0, key="beccs_flaeche")
    
    # 3. Herkunft der Biomasse
    biomasse_herkunft = st.selectbox(
        "Herkunft der Biomasse:", 
        ["Regional (< 50 km)", "National (50 - 200 km)", "International (> 200 km)"]
    )
    
    # 4. Zusammensetzung / Art der Biomasse
    biomasse_art = st.selectbox(
        "Woraus besteht die Biomasse (Zusammensetzung):", 
        ["Forstrestholz / Altholz", "Landwirtschaftliche Reststoffe (Stroh)", "Spezielle Energiepflanzen (Miscanthus)"]
    )

    biomasse_menge = st.number_input("Biomasse-Einsatz (t/Jahr):", value=5000.0, step=100.0, key="beccs_biomasse")
    abscheide_grad = st.slider("CO₂-Abscheidegrad (%):", min_value=50, max_value=100, value=90, key="beccs_grad")
    co2_preis = st.number_input("Aktueller CO₂-Zertifikatspreis (€/t CO₂):", value=120.0, step=5.0, key="beccs_preis")

    # Berechnungs-Logik für Kosten pro Tonne CO₂
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

    # Fixkosten über die Baufläche (z.B. 15 € pro m² und Jahr für Instandhaltung/Abschreibung)
    flaechen_kosten_jahr = bauflaeche * 15.0 

    # CO2-Menge berechnen
    co2_abgeschieden = biomasse_menge * 1.2 * (abscheide_grad / 100)
    
    if co2_abgeschieden > 0:
        gesamtkosten_jahr = (tech_kosten_faktor + herkunft_faktor + biomasse_faktor) * co2_abgeschieden + flaechen_kosten_jahr
        kosten_pro_tonne = gesamtkosten_jahr / co2_abgeschieden
    else:
        kosten_pro_tonne = 0.0
        gesamtkosten_jahr = 0.0

    co2_erloes = co2_abgeschieden * co2_preis
    gewinn_verlust = co2_erloes - gesamtkosten_jahr

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Abgeschiedenes CO₂", value=f"{co2_abgeschieden:,.1f} t/Jahr")
        st.metric(label="Gesamtkosten / Jahr", value=f"{gesamtkosten_jahr:,.2f} €")
    with col2:
        st.metric(label="Kosten pro Tonne CO₂", value=f"{kosten_pro_tonne:,.2f} € / t CO₂")
        st.metric(label="Netto-Ertrag (Erlös - Kosten)", value=f"{gewinn_verlust:,.2f} €/Jahr")

    st.subheader("Kumulierter Netto-Ertrag über 10 Jahre")
    jahre_beccs = list(range(1, 11))
    kumuliert_gewinn = [gewinn_verlust * i for i in range(1, 11)]
    df_beccs = pd.DataFrame({"Jahr": jahre_beccs, "Kumulierter Netto-Ertrag (€)": kumuliert_gewinn})
    st.line_chart(df_beccs.set_index("Jahr"))
