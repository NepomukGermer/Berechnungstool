import streamlit as st
import pandas as pd

st.title("🌱 Moor-Berechnungs-Tool")

st.sidebar.header("Parameter")
moor_typ = st.sidebar.selectbox("Moor-Typ:", ["Hochmoor", "Niedermoor"])
bundesland = st.sidebar.selectbox("Bundesland:", ["Niedersachsen", "Bayern", "Brandenburg", "Schleswig-Holstein"])

flaechen_groesse = st.sidebar.number_input("Flächengröße (ha):", value=10.0)
torf_maechtigkeit = st.sidebar.number_input("Torfmächtigkeit (m):", value=2.0)
aktuelle_einnahmen = st.sidebar.number_input("Aktuelle Einnahmen (€):", value=5000.0)

# Berechnungs-Logik
faktor_moor = 1.5 if moor_typ == "Hochmoor" else 1.2
ergebnis_wert = (flaechen_groesse * torf_maechtigkeit * faktor_moor * 1000) + aktuelle_einnahmen

st.metric(label="Berechneter Zielwert", value=f"{ergebnis_wert:,.2f} €")

st.subheader("Verlaufskurve (Prognose)")
jahre = list(range(1, 11))
verlauf = [ergebnis_wert * (1 + i * 0.05) for i in range(10)]
df = pd.DataFrame({"Jahr": jahre, "Wert": verlauf})
st.line_chart(df.set_index("Jahr"))