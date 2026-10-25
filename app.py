import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("🌱 Klima- & Berechnungs-Hub")

# Drei Reiter (Fenster) erstellen
tab1, tab2, tab3 = st.tabs(["🌱 Moor-Berechnung", "⚡ BECCS-Berechnung", "📊 Vergleich & Volkswirtschaft"])

with tab1:
    st.header("Moor-Wiedervernässung & CO₂-Minderung")
    
    moor_typ = st.selectbox("Moor-Typ:", ["Hochmoor", "Niedermoor"], key="moor_typ")
    bundesland = st.selectbox("Bundesland:", ["Niedersachsen", "Bayern", "Brandenburg", "Schleswig-Holstein"], key="bundesland")

    # Flächengröße in Zehntelschritten (0.1)
    flaechen_groesse = st.number_input("Flächengröße (ha):", value=10.0, step=0.1, key="moor_flaeche")
    torf_maechtigkeit = st.number_input("Torfmächtigkeit (m):", value=2.0, step=0.1, key="moor_torf")

    # Einnahmen in €/ha, ohne Nachkommastellen (Ganzzahlen)
    aktuelle_einnahmen_pro_ha = st.number_input("Aktuelle Einnahmen (€/ha):", value=5000, step=1, format="%d", key="moor_einnahmen")

    # Berechnungs-Logik Moor
    co2_minderung_moor = flaechen_groesse * 25.0  # Annahme: 25 t CO2-Minderung pro ha und Jahr
    kosten_bauer_jahr = flaechen_groesse * 300.0    # Jährliche Kosten/Ertragsausfall für den Bauern
    kosten_volk_jahr = flaechen_groesse * 800.0     # Jährliche volkswirtschaftliche Kosten (Förderung etc.)
    
    erloes_moor = flaechen_groesse * aktuelle_einnahmen_pro_ha
    netto_ertrag_moor = erloes_moor - kosten_bauer_jahr

    kosten_pro_t_bauer = kosten_bauer_jahr / co2_minderung_moor if co2_minderung_moor > 0 else 0
    kosten_pro_t_volk = kosten_volk_jahr / co2_minderung_moor if co2_minderung_moor > 0 else 0

    st.markdown("---")
    
    # Metriken wie im BECCS-Bereich angeordnet
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Eingespartes CO₂", value=f"{co2_minderung_moor:,.1f} t/Jahr")
        st.metric(label="Gesamtkosten / Jahr (Bauer)", value=f"{kosten_bauer_jahr:,.2f} €")
        st.metric(label="Gesamtkosten / Jahr (Volkswirtschaft)", value=f"{kosten_volk_jahr:,.2f} €")
    with col2:
        st.metric(label="Kosten pro Tonne CO₂ (Bauer)", value=f"{kosten_pro_t_bauer:,.2f} € / t CO₂")
        st.metric(label="Kosten pro Tonne CO₂ (Volkswirtschaft)", value=f"{kosten_pro_t_volk:,.2f} € / t CO₂")
        st.metric(label="Netto-Ertrag (Erlös - Kosten Bauer)", value=f"{netto_ertrag_moor:,.2f} €/Jahr")

with tab2:
    st.header("BECCS-Berechnung (Carbon Capture & Storage)")
    
    beccs_technologie = st.selectbox(
        "Technologie zur CO₂-Abscheidung:", 
        ["Aminwäsche (Post-Combustion)", "Oxyfuel-Verfahren", "Druckwechseladsorption (PSA)"]
    )
    bauflaeche = st.number_input("Baufläche der BECCS-Anlage (m²):", value=2500.0, step=100.0, key="beccs_flaeche")
    biomasse_herkunft = st.selectbox(
        "Herkunft der Biomasse:", 
        ["Regional (< 50 km)", "National (50 - 200 km)", "International (> 200 km)"]
    )
    biomasse_art = st.selectbox(
        "Woraus besteht die Biomasse (Zusammensetzung):", 
        ["Forstrestholz / Altholz", "Landwirtschaftliche Reststoffe (Stroh)", "Spezielle Energiepflanzen (Miscanthus)"]
    )

    biomasse_menge = st.number_input("Biomasse-Einsatz (t/Jahr):", value=5000.0, step=100.0, key="beccs_biomasse")
    abscheide_grad = st.slider("CO₂-Abscheidegrad (%):", min_value=50, max_value=100, value=90, key="beccs_grad")
    co2_preis = st.number_input("Aktueller CO₂-Zertifikatspreis (€/t CO₂):", value=120.0, step=5.0, key="beccs_preis")

    # Berechnungs-Logik BECCS
    tech_kosten_faktor = {"Aminwäsche (Post-Combustion)": 90.0, "Oxyfuel-Verfahren": 110.0, "Druckwechseladsorption (PSA)": 80.0}[beccs_technologie]
    herkunft_faktor = {"Regional (< 50 km)": 10.0, "National (50 - 200 km)": 25.0, "International (> 200 km)": 50.0}[biomasse_herkunft]
    biomasse_faktor = {"Forstrestholz / Altholz": 15.0, "Landwirtschaftliche Reststoffe (Stroh)": 20.0, "Spezielle Energiepflanzen (Miscanthus)": 40.0}[biomasse_art]

    flaechen_kosten_jahr = bauflaeche * 15.0 
    co2_abgeschieden = biomasse_menge * 1.2 * (abscheide_grad / 100)
    
    if co2_abgeschieden > 0:
        gesamtkosten_jahr_beccs = (tech_kosten_faktor + herkunft_faktor + biomasse_faktor) * co2_abgeschieden + flaechen_kosten_jahr
        kosten_pro_tonne_beccs = gesamtkosten_jahr_beccs / co2_abgeschieden
    else:
        kosten_pro_tonne_beccs = 0.0
        gesamtkosten_jahr_beccs = 0.0

    co2_erloes_beccs = co2_abgeschieden * co2_preis
    gewinn_verlust_beccs = co2_erloes_beccs - gesamtkosten_jahr_beccs

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Abgeschiedenes CO₂", value=f"{co2_abgeschieden:,.1f} t/Jahr")
        st.metric(label="Gesamtkosten / Jahr (Firma)", value=f"{gesamtkosten_jahr_beccs:,.2f} €")
    with col2:
        st.metric(label="Kosten pro Tonne CO₂", value=f"{kosten_pro_tonne_beccs:,.2f} € / t CO₂")
        st.metric(label="Netto-Ertrag (Erlös - Kosten)", value=f"{gewinn_verlust_beccs:,.2f} €/Jahr")

with tab3:
    st.header("📊 10-Jahres-Vergleich: Moor & BECCS")
    
    jahre = list(range(1, 11))
    
    # Kumulierte Werte über 10 Jahre berechnen
    moor_bauer_ertrag = [netto_ertrag_moor * i for i in range(1, 11)]
    moor_volk_kosten = [kosten_volk_jahr * i for i in range(1, 11)]
    beccs_firma_kosten = [gesamtkosten_jahr_beccs * i for i in range(1, 11)]
    beccs_volk_kosten = [gesamtkosten_jahr_beccs * 0.4 * i for i in range(1, 11)] # Annahme BECCS Volkswirtschaftskosten

    fig = go.Figure()
    
    # 1. Moor: Erträge Bauer (gestrichelt, grün)
    fig.add_trace(go.Scatter(
        x=jahre, y=moor_bauer_ertrag, mode='lines', 
        name='Moor: Erträge Bauer',
        line=dict(color='green', dash='dash')
    ))
    
    # 2. Moor: Kosten Volkswirtschaft (durchgezogen, grün)
    fig.add_trace(go.Scatter(
        x=jahre, y=moor_volk_kosten, mode='lines', 
        name='Moor: Kosten Volkswirtschaft',
        line=dict(color='green', dash='solid')
    ))
    
    # 3. BECCS: Kosten Firma (gestrichelt, blau)
    fig.add_trace(go.Scatter(
        x=jahre, y=beccs_firma_kosten, mode='lines', 
        name='BECCS: Kosten Firma',
        line=dict(color='blue', dash='dash')
    ))
    
    # 4. BECCS: Kosten Volkswirtschaft (durchgezogen, blau)
    fig.add_trace(go.Scatter(
        x=jahre, y=beccs_volk_kosten, mode='lines', 
        name='BECCS: Kosten Volkswirtschaft',
        line=dict(color='blue', dash='solid')
    ))

    fig.update_layout(
        title="Kumulierte Entwicklung über 10 Jahre (€)",
        xaxis_title="Jahre",
        yaxis_title="Euro (€)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
