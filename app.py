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


# ==========================================
# GEMEINSAME UI- & OPTIMIERUNGSHILFEN
# ==========================================
def beste_option_ermitteln(optionen, bewertungs_fn):
    bester_wert = None
    beste_opt = None
    for opt in optionen:
        wert = bewertungs_fn(opt)
        if bester_wert is None or wert > bester_wert:
            bester_wert = wert
            beste_opt = opt
    return beste_opt, bester_wert


def format_radio_option(opt, beste_opt, aktiv):
    if aktiv and opt == beste_opt:
        return f":green[{opt}]"
    return opt


def render_kleinen_gruenen_hinweis(beste_opt, aktiv):
    if aktiv and beste_opt is not None:
        st.markdown(
            f"<div style='color:#15803d; font-size:0.78rem; line-height:1.1; margin-top:-0.65rem; margin-bottom:0.55rem;'>{beste_opt}</div>",
            unsafe_allow_html=True
        )


def opt_selectbox(label, options, key, aktiv, beste_opt=None, index=None, format_func=None, beste_label=None):
    default_idx = 0
    if index is not None:
        default_idx = index
    elif aktiv and beste_opt in options:
        default_idx = options.index(beste_opt)

    kwargs = {"index": default_idx, "key": key}
    if format_func is not None:
        kwargs["format_func"] = format_func

    val = st.selectbox(label, options, **kwargs)
    anzeige = beste_label if beste_label is not None else beste_opt
    render_kleinen_gruenen_hinweis(anzeige, aktiv)
    return val


# ==========================================
# BERECHNUNGSLOGIK ROHRGLANZGRAS
# ==========================================
def rohrglanzgras_szenario_daten(etablierungs_art, mahd_zeitpunkt):
    ist_ansaat = (etablierungs_art == "Erstetablierung")
    ist_sommer = (mahd_zeitpunkt == "Sommermahd")
    if ist_sommer and ist_ansaat:
        return {
            "key": "sommer_ansaat",
            "ertrag_tm": 10.0,
            "fm_haeck_ballen": 12.50,
            "fm_pellets": 11.11,
            "etablierung": 35.0,
            "laufend": 60.0,
            "ernte_haeck": 310.0,
            "ernte_ballen": 350.0,
            "ernte_langgut": 250.0,
            "pressen": 400.00,
            "stationaer_pellet": 581.60,
            "brikettierung": 600.00,
            "mobil_pellet": 1795.00,
            "transport_haeck": {2.5: 91.0, 5.0: 109.0, 10.0: 146.0, 20.0: 219.0, 30.0: 293.0, 50.0: 440.0},
            "transport_ballen": {2.5: 57.0, 5.0: 65.0, 10.0: 79.0, 20.0: 108.0, 30.0: 137.0, 50.0: 196.0},
            "transport_pellets": {2.5: 23.0, 5.0: 27.0, 10.0: 34.0, 20.0: 48.0, 30.0: 61.0, 50.0: 89.0},
            "lager_haeck_halle": 187.50,
            "lager_haeck_frei": 71.25,
            "lager_ballen_halle": 318.75,
            "lager_ballen_alt": 137.50,
            "lager_ballen_frei": 66.25,
            "lager_pellets_halle": 130.56
        }
    elif ist_sommer and not ist_ansaat:
        return {
            "key": "sommer_sukzession",
            "ertrag_tm": 7.5,
            "fm_haeck_ballen": 9.38,
            "fm_pellets": 8.33,
            "etablierung": 0.0,
            "laufend": 60.0,
            "ernte_haeck": 310.0,
            "ernte_ballen": 350.0,
            "ernte_langgut": 250.0,
            "pressen": 300.00,
            "stationaer_pellet": 436.20,
            "brikettierung": 450.00,
            "mobil_pellet": 1346.25,
            "transport_haeck": {2.5: 68.3, 5.0: 81.8, 10.0: 109.5, 20.0: 164.3, 30.0: 219.8, 50.0: 330.0},
            "transport_ballen": {2.5: 42.8, 5.0: 48.8, 10.0: 59.3, 20.0: 81.0, 30.0: 102.8, 50.0: 147.0},
            "transport_pellets": {2.5: 17.3, 5.0: 20.3, 10.0: 25.5, 20.0: 36.0, 30.0: 45.8, 50.0: 66.8},
            "lager_haeck_halle": 140.63,
            "lager_haeck_frei": 53.44,
            "lager_ballen_halle": 239.07,
            "lager_ballen_alt": 103.13,
            "lager_ballen_frei": 49.69,
            "lager_pellets_halle": 97.92
        }
    elif not ist_sommer and ist_ansaat:
        return {
            "key": "winter_ansaat",
            "ertrag_tm": 4.0,
            "fm_haeck_ballen": 5.00,
            "fm_pellets": 4.44,
            "etablierung": 35.0,
            "laufend": 60.0,
            "ernte_haeck": 300.0,
            "ernte_ballen": 320.0,
            "ernte_langgut": 250.0,
            "pressen": 160.00,
            "stationaer_pellet": 232.64,
            "brikettierung": 240.00,
            "mobil_pellet": 718.00,
            "transport_haeck": {2.5: 36.4, 5.0: 43.6, 10.0: 58.4, 20.0: 87.6, 30.0: 117.2, 50.0: 176.0},
            "transport_ballen": {2.5: 22.8, 5.0: 26.0, 10.0: 31.6, 20.0: 43.2, 30.0: 54.8, 50.0: 78.4},
            "transport_pellets": {2.5: 9.2, 5.0: 10.8, 10.0: 13.6, 20.0: 19.2, 30.0: 24.4, 50.0: 35.6},
            "lager_haeck_halle": 75.00,
            "lager_haeck_frei": 28.50,
            "lager_ballen_halle": 127.50,
            "lager_ballen_alt": 55.00,
            "lager_ballen_frei": 26.50,
            "lager_pellets_halle": 52.22
        }
    else:
        return {
            "key": "winter_sukzession",
            "ertrag_tm": 3.0,
            "fm_haeck_ballen": 3.75,
            "fm_pellets": 3.33,
            "etablierung": 0.0,
            "laufend": 60.0,
            "ernte_haeck": 300.0,
            "ernte_ballen": 320.0,
            "ernte_langgut": 250.0,
            "pressen": 120.00,
            "stationaer_pellet": 174.48,
            "brikettierung": 180.00,
            "mobil_pellet": 538.50,
            "transport_haeck": {2.5: 27.3, 5.0: 32.7, 10.0: 43.8, 20.0: 65.7, 30.0: 87.9, 50.0: 132.0},
            "transport_ballen": {2.5: 17.1, 5.0: 19.5, 10.0: 23.7, 20.0: 32.4, 30.0: 41.1, 50.0: 58.8},
            "transport_pellets": {2.5: 6.9, 5.0: 8.1, 10.0: 10.2, 20.0: 14.4, 30.0: 18.3, 50.0: 26.7},
            "lager_haeck_halle": 56.25,
            "lager_haeck_frei": 21.38,
            "lager_ballen_halle": 95.63,
            "lager_ballen_alt": 41.25,
            "lager_ballen_frei": 19.88,
            "lager_pellets_halle": 39.17
        }


def rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_zeitpunkt, ernteform, verwertung, folge, ballen_winter):
    sz = rohrglanzgras_szenario_daten(etablierungs_art, mahd_zeitpunkt)
    k = sz["key"]
    ist_sommer = (mahd_zeitpunkt == "Sommermahd")
    ist_pellet_form = ernteform in [
        "Pelletierte Form (mobile Pelletierungsmaschine)",
        "Brikettierte Form (mobile Brikettierungsmaschine)"
    ] or folge in ["Pellets", "Briketts", "Pellets und Briketts", "Stationäre Pelletieranlage", "Brennstoff-Pellets / Briketts"] or ballen_winter in ["Pellets", "Briketts"]

    if ist_pellet_form:
        ziel = folge or verwertung or ballen_winter
        if ziel in ["Verbrennen", "Brennstoff-Pellets / Briketts", "Briketts", "Pellets"]:
            return 0.0 if ist_sommer else (880.0 if k == "winter_ansaat" else 660.0)
        if ziel in ["Tiereinstreu", "Einstreu"]:
            return {"sommer_ansaat": 2800.0, "sommer_sukzession": 2100.0, "winter_ansaat": 1120.0, "winter_sukzession": 840.0}[k]
        if ziel in ["Raufutterersatz", "Raufutter"]:
            return {"sommer_ansaat": 3100.0, "sommer_sukzession": 2325.0, "winter_ansaat": 0.0, "winter_sukzession": 0.0}[k]
        if ziel in ["Organischer Dünger", "Dünger"]:
            return {"sommer_ansaat": 2400.0, "sommer_sukzession": 1800.0, "winter_ansaat": 0.0, "winter_sukzession": 0.0}[k]
        if ziel in ["Torfersatz in Kultursubstraten", "Torf- und Kompostersatz", "Kultursubstrate"]:
            return {"sommer_ansaat": 2100.0, "sommer_sukzession": 1575.0, "winter_ansaat": 840.0, "winter_sukzession": 630.0}[k]
        if ziel in ["Mulch-Pellets", "Mulchmaterial"]:
            return {"sommer_ansaat": 2300.0, "sommer_sukzession": 1725.0, "winter_ansaat": 920.0, "winter_sukzession": 690.0}[k]
        if ziel in ["Biokunststoffe & Spritzguss", "Biokunststoffe"]:
            return {"sommer_ansaat": 2700.0, "sommer_sukzession": 2025.0, "winter_ansaat": 1080.0, "winter_sukzession": 810.0}[k]
        if ziel in ["Faserplatten & Dämmstoffe", "Faserplatten und Biokunststoffe", "Plattenwerkstoffe"]:
            return {"sommer_ansaat": 2100.0, "sommer_sukzession": 1575.0, "winter_ansaat": 840.0, "winter_sukzession": 630.0}[k]
        if ziel in ["Biogas-Substrat", "Biogasproduktion", "Biogassubstrat"]:
            return {"sommer_ansaat": 1100.0, "sommer_sukzession": 825.0, "winter_ansaat": 0.0, "winter_sukzession": 0.0}[k]
        if ziel in ["Papier herstellen", "Papier- und Kartonherstellung"]:
            return {"sommer_ansaat": 1800.0, "sommer_sukzession": 1350.0, "winter_ansaat": 720.0, "winter_sukzession": 540.0}[k]

    ziel = folge or verwertung
    if ziel in ["Pferdeheu", "Heu"]:
        return {"sommer_ansaat": 1765.0, "sommer_sukzession": 1325.0, "winter_ansaat": 0.0, "winter_sukzession": 0.0}[k]
    if ziel == "Raufutter":
        return {"sommer_ansaat": 1100.0, "sommer_sukzession": 825.0, "winter_ansaat": 0.0, "winter_sukzession": 0.0}[k]
    if ziel in ["Silage", "Biogasproduktion", "Biogassubstrat"]:
        return {"sommer_ansaat": 600.0, "sommer_sukzession": 450.0, "winter_ansaat": 0.0, "winter_sukzession": 0.0}[k]
    if ziel == "Proteinkonzentrat":
        return {"sommer_ansaat": 1400.0, "sommer_sukzession": 1050.0, "winter_ansaat": 0.0, "winter_sukzession": 0.0}[k]
    if ziel in ["Einstreu", "Tiereinstreu"]:
        return {"sommer_ansaat": 0.0, "sommer_sukzession": 0.0, "winter_ansaat": 400.0, "winter_sukzession": 300.0}[k]
    if ziel in ["Mulchmaterial", "Mulch"]:
        return {"sommer_ansaat": 450.0, "sommer_sukzession": 337.5, "winter_ansaat": 340.0, "winter_sukzession": 255.0}[k]
    if ziel in ["Dünger", "Organischer Dünger"]:
        return {"sommer_ansaat": 550.0, "sommer_sukzession": 412.5, "winter_ansaat": 80.0, "winter_sukzession": 60.0}[k]
    if ziel == "Einblasdämmung":
        return 0.0
    if ziel in ["Dämmmatten", "Dämmplatten"]:
        return {"sommer_ansaat": 0.0, "sommer_sukzession": 0.0, "winter_ansaat": 640.0, "winter_sukzession": 480.0}[k]
    if ziel in ["Plattenwerkstoffe", "Faserplatten und Biokunststoffe", "Bau- & Dämmstoffe", "Dämmen und Bauen"]:
        return {"sommer_ansaat": 900.0, "sommer_sukzession": 675.0, "winter_ansaat": 740.0, "winter_sukzession": 555.0}[k]
    if ziel in ["Thermische Verwertung", "Direkte Verbrennung", "Verbrennung"]:
        return 0.0 if ist_sommer else (673.0 if k == "winter_ansaat" else 504.75)
    if ziel in ["Torf- und Kompostersatz", "Kultursubstrate"]:
        return {"sommer_ansaat": 455.0, "sommer_sukzession": 341.25, "winter_ansaat": 1552.5, "winter_sukzession": 1164.38}[k]
    if ziel in ["Pflanzenkohle & Aktivkohle", "Pflanzenkohle"]:
        return 0.0 if ist_sommer else (1190.5 if k == "winter_ansaat" else 892.88)
    if ziel in ["Papier- und Kartonherstellung", "Papier herstellen"]:
        return 0.0 if ist_sommer else (1190.5 if k == "winter_ansaat" else 892.88)
    if ziel == "Biokunststoffe":
        return 0.0 if ist_sommer else (2329.0 if k == "winter_ansaat" else 1746.75)

    return {"sommer_ansaat": 950.0, "sommer_sukzession": 712.5, "winter_ansaat": 380.0, "winter_sukzession": 285.0}[k]


def berechne_rohrglanzgras_kosten_und_erloes(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    etablierungs_art,
    mahd_zeitpunkt,
    ernteform_biomasse,
    verwertung,
    folge_auswahl,
    ballen_winter_option,
    transport_bekannt,
    transport_km,
    lagerung_geplant,
    lagerung_art,
    kaufkosten_gesamt
):
    sz = rohrglanzgras_szenario_daten(etablierungs_art, mahd_zeitpunkt)
    etab_ha = sz["etablierung"]
    laufend_ha = sz["laufend"]

    ist_mobil_pellet = ernteform_biomasse == "Pelletierte Form (mobile Pelletierungsmaschine)"
    ist_mobil_brikett = ernteform_biomasse == "Brikettierte Form (mobile Brikettierungsmaschine)"
    ist_pellet_oder_brikett = (
        ist_mobil_pellet
        or ist_mobil_brikett
        or folge_auswahl in ["Pellets", "Briketts", "Pellets und Briketts", "Stationäre Pelletieranlage", "Brennstoff-Pellets / Briketts"]
        or ballen_winter_option in ["Pellets", "Briketts"]
    )

    if ernteform_biomasse == "Häckselgut":
        ernte_ha = sz["ernte_haeck"]
    elif ernteform_biomasse in ["Rundballen", "Quaderballen"]:
        ernte_ha = sz["ernte_ballen"]
    elif ernteform_biomasse == "Loses Langgut":
        ernte_ha = sz["ernte_langgut"]
    elif ist_mobil_pellet:
        ernte_ha = sz["mobil_pellet"]
    elif ist_mobil_brikett:
        ernte_ha = sz["brikettierung"]
    else:
        ernte_ha = sz["ernte_ballen"]

    endprodukt_ha = 0.0
    if ernteform_biomasse in ["Rundballen", "Quaderballen"] and mahd_zeitpunkt == "Wintermahd":
        if ballen_winter_option == "Pellets":
            endprodukt_ha += sz["stationaer_pellet"]
        elif ballen_winter_option == "Briketts":
            endprodukt_ha += sz["brikettierung"]
        elif ballen_winter_option == "Pressen":
            endprodukt_ha += sz["pressen"]

    if not ist_mobil_pellet and not ist_mobil_brikett:
        if folge_auswahl in ["Pellets", "Pellets und Briketts", "Stationäre Pelletieranlage", "Brennstoff-Pellets / Briketts"]:
            endprodukt_ha += sz["stationaer_pellet"]
        elif folge_auswahl == "Briketts":
            endprodukt_ha += sz["brikettierung"]
        elif folge_auswahl in ["Plattenwerkstoffe", "Faserplatten und Biokunststoffe"] or verwertung in ["Bau- & Dämmstoffe", "Dämmen und Bauen"]:
            endprodukt_ha += 920.0
        elif folge_auswahl == "Biokunststoffe":
            endprodukt_ha += 1280.0

    if ist_pellet_oder_brikett:
        t_map = sz["transport_pellets"]
    elif ernteform_biomasse == "Häckselgut":
        t_map = sz["transport_haeck"]
    else:
        t_map = sz["transport_ballen"]

    if transport_bekannt == "Ja":
        transport_ha = t_map.get(transport_km, t_map[10.0])
    else:
        transport_ha = t_map[10.0]

    lager_ha = 0.0
    if lagerung_geplant == "Ja":
        if ist_pellet_oder_brikett:
            if lagerung_art == "In einer Halle":
                lager_ha = sz["lager_pellets_halle"]
        elif ernteform_biomasse == "Häckselgut":
            lager_ha = {
                "In einer Halle": sz["lager_haeck_halle"],
                "Auf einer freien Fläche mit Abdeckung": sz["lager_haeck_frei"]
            }.get(lagerung_art, 0.0)
        else:
            lager_ha = {
                "In einer Halle": sz["lager_ballen_halle"],
                "In einem Altgebäude": sz["lager_ballen_alt"],
                "Auf einer freien Fläche mit Abdeckung": sz["lager_ballen_frei"]
            }.get(lagerung_art, 0.0)

    erloes_ha = rohrglanzgras_erloes_pro_ha(
        etablierungs_art, mahd_zeitpunkt, ernteform_biomasse, verwertung, folge_auswahl, ballen_winter_option
    )

    kauf_annuitaet_pro_ha = (kaufkosten_gesamt / 10.0) / flaechen_groesse if flaechen_groesse > 0 else 0.0
    kosten_pro_ha = etab_ha + laufend_ha + ernte_ha + endprodukt_ha + transport_ha + lager_ha + kauf_annuitaet_pro_ha
    netto_gesamt = ((bisherige_ertraege_pro_ha + erloes_ha) - kosten_pro_ha) * flaechen_groesse

    return {
        "etablierung": etab_ha,
        "laufend": laufend_ha,
        "ernte": ernte_ha,
        "endprodukt": endprodukt_ha,
        "transport": transport_ha,
        "lager": lager_ha,
        "erloes_ha": erloes_ha,
        "netto_gesamt": netto_gesamt
    }


def berechne_rohrglanzgras_netto_pro_ha(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    etablierungs_art,
    mahd_zeitpunkt,
    ernteform_biomasse,
    verwertung,
    folge_auswahl,
    ballen_winter_option,
    transport_bekannt,
    transport_km,
    lagerung_geplant,
    lagerung_art,
    kaufkosten_gesamt
):
    return berechne_rohrglanzgras_kosten_und_erloes(
        flaechen_groesse,
        bisherige_ertraege_pro_ha,
        etablierungs_art,
        mahd_zeitpunkt,
        ernteform_biomasse,
        verwertung,
        folge_auswahl,
        ballen_winter_option,
        transport_bekannt,
        transport_km,
        lagerung_geplant,
        lagerung_art,
        kaufkosten_gesamt
    )["netto_gesamt"]


def rohrglanzgras_ernteformen_fuer_mahd(mahd):
    opts = ["Häckselgut", "Rundballen", "Quaderballen", "Bunde", "Loses Langgut"]
    if mahd != "Sommermahd":
        opts.extend([
            "Pelletierte Form (mobile Pelletierungsmaschine)",
            "Brikettierte Form (mobile Brikettierungsmaschine)"
        ])
    return opts


def rohrglanzgras_pfade_fuer(etab_art, mahd, ernteform):
    pfade = []
    if ernteform == "Häckselgut":
        bereiche = ["Energetische Verwertung", "Bau- und Werkstoffe", "Gartenbau und Landwirtschaft"]
        if mahd != "Sommermahd":
            bereiche.append("Thermische Verwertung")
        for b in bereiche:
            if b == "Thermische Verwertung":
                folgen = ["Verbrennung", "Pellets", "Briketts"]
            elif b == "Energetische Verwertung":
                if mahd == "Sommermahd":
                    folgen = ["Biogasproduktion"]
                else:
                    folgen = ["Direkte Verbrennung", "Pellets und Briketts"]
            elif b == "Bau- und Werkstoffe":
                folgen = ["Faserplatten und Biokunststoffe"] if mahd == "Sommermahd" else ["Faserplatten und Biokunststoffe", "Papier- und Kartonherstellung"]
            else:
                folgen = ["Torf- und Kompostersatz", "Mulchmaterial"] if mahd == "Sommermahd" else ["Torf- und Kompostersatz", "Mulchmaterial", "Tiereinstreu", "Pflanzenkohle & Aktivkohle"]
            for f in folgen:
                if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, b, f, None) > 0:
                    pfade.append((b, f, None))

    elif ernteform in ["Rundballen", "Quaderballen"]:
        ballen_opts = ["Keine zusätzliche Verarbeitung", "Pellets", "Briketts", "Pressen"] if mahd == "Wintermahd" else ["Keine zusätzliche Verarbeitung"]
        for bw in ballen_opts:
            if bw != "Keine zusätzliche Verarbeitung":
                if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, bw, bw, bw) > 0:
                    pfade.append((bw, bw, bw))
            else:
                verw_list = ["Pferdeheu", "Raufutter", "Proteinkonzentrat", "Bau- & Dämmstoffe"] if mahd == "Sommermahd" else ["Einstreu", "Thermische Verwertung", "Bau- & Dämmstoffe"]
                for v in verw_list:
                    if v == "Bau- & Dämmstoffe":
                        folgen = ["Plattenwerkstoffe"] if mahd == "Sommermahd" else ["Dämmmatten", "Dämmplatten", "Plattenwerkstoffe"]
                        for f in folgen:
                            if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, v, f, bw) > 0:
                                pfade.append((v, f, bw))
                    elif v == "Thermische Verwertung":
                        for f in ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung"]:
                            if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, v, f, bw) > 0:
                                pfade.append((v, f, bw))
                    else:
                        if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, v, None, bw) > 0:
                            pfade.append((v, None, bw))

    elif ernteform == "Bunde":
        verw_list = ["Pferdeheu", "Raufutter", "Proteinkonzentrat", "Bau- & Dämmstoffe"] if mahd == "Sommermahd" else ["Einstreu", "Thermische Verwertung", "Bau- & Dämmstoffe"]
        for v in verw_list:
            if v == "Bau- & Dämmstoffe":
                folgen = ["Plattenwerkstoffe"] if mahd == "Sommermahd" else ["Dämmmatten", "Dämmplatten", "Plattenwerkstoffe"]
                for f in folgen:
                    if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, v, f, None) > 0:
                        pfade.append((v, f, None))
            elif v == "Thermische Verwertung":
                for f in ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung"]:
                    if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, v, f, None) > 0:
                        pfade.append((v, f, None))
            else:
                if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, v, None, None) > 0:
                    pfade.append((v, None, None))

    elif ernteform == "Loses Langgut":
        direkt = ["Raufutter", "Heu", "Silage", "Dünger", "Mulchmaterial"] if mahd == "Sommermahd" else ["Einstreu", "Dünger", "Mulchmaterial"]
        weiter = ["Biogassubstrat"] if mahd == "Sommermahd" else ["Stationäre Pelletieranlage", "Briketts", "Pflanzenkohle"]
        for f in direkt:
            if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, "Direkte Nutzung", f, None) > 0:
                pfade.append(("Direkte Nutzung", f, None))
        for f in weiter:
            if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, "Weiterverarbeitung", f, None) > 0:
                pfade.append(("Weiterverarbeitung", f, None))

    else:
        pellet_opts = [
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
        for v in pellet_opts:
            if rohrglanzgras_erloes_pro_ha(etab_art, mahd, ernteform, v, v, None) > 0:
                pfade.append((v, v, None))

    return pfade


def max_netto_fuer_rohrglanzgras_teilbaum(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    kaufkosten_gesamt,
    etab_art=None,
    mahd=None,
    ernteform=None,
    verwertung=None,
    folge=None,
    ballen_winter=None,
    transport_bekannt=None,
    transport_km=None,
    lagerung_geplant=None,
    lagerung_art=None
):
    etab_liste = [etab_art] if etab_art is not None else ["Natürliche Sukzession", "Erstetablierung"]
    mahd_liste = [mahd] if mahd is not None else ["Sommermahd", "Wintermahd"]
    bester_netto = None

    for ea in etab_liste:
        for m in mahd_liste:
            ef_liste = [ernteform] if ernteform is not None else rohrglanzgras_ernteformen_fuer_mahd(m)
            for ef in ef_liste:
                alle_pfade = rohrglanzgras_pfade_fuer(ea, m, ef)
                for v, f, bw in alle_pfade:
                    if verwertung is not None and v != verwertung:
                        continue
                    if folge is not None and f != folge:
                        continue
                    if ballen_winter is not None and bw != ballen_winter:
                        continue

                    tb = transport_bekannt if transport_bekannt is not None else "Ja"
                    tk = transport_km if transport_km is not None else 10.0
                    lg = lagerung_geplant if lagerung_geplant is not None else "Nein"
                    la = lagerung_art if lagerung_art is not None else None

                    netto = berechne_rohrglanzgras_netto_pro_ha(
                        flaechen_groesse=flaechen_groesse,
                        bisherige_ertraege_pro_ha=bisherige_ertraege_pro_ha,
                        etablierungs_art=ea,
                        mahd_zeitpunkt=m,
                        ernteform_biomasse=ef,
                        verwertung=v,
                        folge_auswahl=f,
                        ballen_winter_option=bw,
                        transport_bekannt=tb,
                        transport_km=tk,
                        lagerung_geplant=lg,
                        lagerung_art=la,
                        kaufkosten_gesamt=kaufkosten_gesamt
                    )
                    if bester_netto is None or netto > bester_netto:
                        bester_netto = netto
    return bester_netto if bester_netto is not None else 0.0


# ==========================================
# BERECHNUNGSLOGIK SCHILF
# ==========================================
def berechne_schilf_netto_pro_ha(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    etablierungs_art,
    etablierungs_detail,
    mahd_zeitpunkt,
    ernteform_biomasse,
    verwertung,
    folge_auswahl,
    ballen_winter_option,
    erntetechnik,
    transport_bekannt,
    transport_km,
    lagerung_geplant,
    lagerung_art,
    kaufkosten_gesamt
):
    if ernteform_biomasse == "Loses Langgut":
        if etablierungs_art == "Erstetablierung":
            etablierung_kosten_pro_ha_jahr = (
                680.00 if etablierungs_detail == "Anpflanzung mit Jungpflanzen" else 410.00
            )
        else:
            etablierung_kosten_pro_ha_jahr = 380.00
        laufende_kosten_pro_ha_jahr = 0.0
    else:
        if etablierungs_art == "Erstetablierung":
            etablierung_kosten_pro_ha_jahr = (
                378.50 if etablierungs_detail == "Anpflanzung mit Jungpflanzen" else 247.22
            )
        else:
            etablierung_kosten_pro_ha_jahr = 224.00
        laufende_kosten_pro_ha_jahr = 693.75

    sonderkosten_schilf_pro_ha_jahr = 0.0
    entfaellt_ernte_und_transport = False
    if verwertung == "Thermische Verwertung" and folge_auswahl == "Ethanol":
        sonderkosten_schilf_pro_ha_jahr = 2387.00
        entfaellt_ernte_und_transport = True
    elif verwertung == "Energetische Verwertung" and folge_auswahl == "Biogasanlage":
        sonderkosten_schilf_pro_ha_jahr = 1900.00
        entfaellt_ernte_und_transport = True

    if entfaellt_ernte_und_transport or ernteform_biomasse == "Loses Langgut":
        erntekosten_pro_ha_jahr = 0.0
    elif ernteform_biomasse in ["Rundballen", "Quaderballen", "Häckselgut"]:
        erntekosten_pro_ha_jahr = 410.00
    elif ernteform_biomasse == "Bunde":
        erntekosten_pro_ha_jahr = 640.00
    elif ernteform_biomasse == "Pelletierte Form (mobile Pelletierungsmaschine)":
        erntekosten_pro_ha_jahr = 2719.43 if mahd_zeitpunkt == "Sommermahd" else 1759.10
    else:
        erntekosten_pro_ha_jahr = 350.00

    if ernteform_biomasse in ["Rundballen", "Quaderballen"] and mahd_zeitpunkt == "Wintermahd":
        erntekosten_pro_ha_jahr += {
            "Pellets": 569.97,
            "Briketts": 588.00,
            "Pressen": 392.00
        }.get(ballen_winter_option, 0.0)

    ist_mobile_pellet_oder_brikett = ernteform_biomasse in [
        "Pelletierte Form (mobile Pelletierungsmaschine)",
        "Brikettierte Form (mobile Brikettierungsmaschine)"
    ]
    endprodukt_kosten_pro_ha_jahr = 0.0
    if not ist_mobile_pellet_oder_brikett:
        if (
            folge_auswahl in ["Pellets", "Pellets und Briketts", "Stationäre Pelletieranlage", "Brennstoff-Pellets / Briketts"]
            or ballen_winter_option == "Pellets"
        ):
            endprodukt_kosten_pro_ha_jahr = 1000.00
        elif folge_auswahl in ["Briketts"] or ballen_winter_option == "Briketts":
            endprodukt_kosten_pro_ha_jahr = 800.00
        elif (
            folge_auswahl in ["Formteile", "Plattenwerkstoffe", "Faserplatten und Biokunststoffe"]
            or verwertung in ["Werkstoffe", "Faserplatten & Dämmstoffe"]
        ):
            endprodukt_kosten_pro_ha_jahr = 920.00
        elif folge_auswahl == "Biokunststoffe" or verwertung == "Biokunststoffe":
            endprodukt_kosten_pro_ha_jahr = 1280.00
        elif (
            folge_auswahl in ["Einblasdämmung", "Dämmmatten", "Dämmstoffe (Einblasdämmung / Dämmmatten)"]
            or verwertung == "Dämm- und Baustoffe"
        ):
            endprodukt_kosten_pro_ha_jahr = 11200.00

    transport_kosten_pro_ha_jahr = 0.0
    if not entfaellt_ernte_und_transport:
        ist_pellet_brikett_produkt = (
            ist_mobile_pellet_oder_brikett
            or folge_auswahl in [
                "Pellets",
                "Briketts",
                "Pellets und Briketts",
                "Stationäre Pelletieranlage",
                "Brennstoff-Pellets / Briketts"
            ]
            or ballen_winter_option in ["Pellets", "Briketts"]
        )
        ist_dachschilf_bunde_langgut = (
            verwertung == "Dachreed"
            or folge_auswahl == "Sortierung zu Dachreetbunden"
            or ernteform_biomasse in ["Bunde", "Loses Langgut"]
        )

        if ernteform_biomasse == "Häckselgut":
            if mahd_zeitpunkt == "Sommermahd":
                transport_kosten_pro_ha_jahr = (
                    {2.5: 137.87, 5.0: 165.14, 10.0: 221.19, 20.0: 331.79, 30.0: 443.90, 50.0: 666.60}.get(transport_km, 387.85)
                    if transport_bekannt == "Ja" else 387.85
                )
            else:
                transport_kosten_pro_ha_jahr = (
                    {2.5: 89.18, 5.0: 106.82, 10.0: 143.08, 20.0: 214.62, 30.0: 287.14, 50.0: 431.20}.get(transport_km, 250.88)
                    if transport_bekannt == "Ja" else 250.88
                )
        elif ist_dachschilf_bunde_langgut:
            if mahd_zeitpunkt == "Sommermahd":
                if flaechen_groesse >= 2.5:
                    transport_kosten_pro_ha_jahr = (
                        {2.5: 89.39, 5.0: 99.99, 10.0: 122.72, 20.0: 166.65, 30.0: 212.10, 50.0: 299.997}.get(transport_km, 189.76)
                        if transport_bekannt == "Ja" else 189.76
                    )
                else:
                    transport_kosten_pro_ha_jahr = (
                        {2.5: 212.10, 5.0: 236.34, 10.0: 284.82, 20.0: 383.30, 30.0: 480.26, 50.0: 677.21}.get(transport_km, 431.78)
                        if transport_bekannt == "Ja" else 431.78
                    )
            else:
                if flaechen_groesse >= 2.5:
                    transport_kosten_pro_ha_jahr = (
                        {2.5: 57.82, 5.0: 64.68, 10.0: 79.38, 20.0: 107.80, 30.0: 137.20, 50.0: 194.04}.get(transport_km, 122.50)
                        if transport_bekannt == "Ja" else 122.50
                    )
                else:
                    transport_kosten_pro_ha_jahr = (
                        {2.5: 137.20, 5.0: 152.88, 10.0: 184.24, 20.0: 247.94, 30.0: 310.66, 50.0: 438.06}.get(transport_km, 279.30)
                        if transport_bekannt == "Ja" else 279.30
                    )
        elif ist_pellet_brikett_produkt and mahd_zeitpunkt == "Wintermahd":
            transport_kosten_pro_ha_jahr = (
                {2.5: 22.54, 5.0: 26.46, 10.0: 33.32, 20.0: 47.04, 30.0: 59.78, 50.0: 87.22}.get(transport_km, 53.41)
                if transport_bekannt == "Ja" else 53.41
            )
        elif ernteform_biomasse in ["Rundballen", "Quaderballen"]:
            if mahd_zeitpunkt == "Sommermahd":
                transport_kosten_pro_ha_jahr = (
                    {2.5: 86.36, 5.0: 98.48, 10.0: 119.69, 20.0: 163.62, 30.0: 207.56, 50.0: 296.94}.get(transport_km, 185.59)
                    if transport_bekannt == "Ja" else 185.59
                )
            else:
                transport_kosten_pro_ha_jahr = (
                    {2.5: 55.86, 5.0: 63.70, 10.0: 77.42, 20.0: 105.84, 30.0: 134.26, 50.0: 192.08}.get(transport_km, 120.05)
                    if transport_bekannt == "Ja" else 120.05
                )
        elif transport_bekannt == "Ja":
            transport_kosten_pro_ha_jahr = transport_km * 3.5

    lager_kosten_pro_ha_jahr = 0.0
    if lagerung_geplant == "Ja" and ernteform_biomasse not in ["Bunde", "Loses Langgut"]:
        ist_pellet_brikett_lager = (
            ist_mobile_pellet_oder_brikett
            or folge_auswahl in [
                "Pellets",
                "Briketts",
                "Pellets und Briketts",
                "Stationäre Pelletieranlage",
                "Brennstoff-Pellets / Briketts"
            ]
            or ballen_winter_option in ["Pellets", "Briketts"]
        )
        if ist_pellet_brikett_lager:
            if lagerung_art == "In einer Halle":
                lager_kosten_pro_ha_jahr = 178.01 if mahd_zeitpunkt == "Sommermahd" else 115.15
        elif ernteform_biomasse == "Häckselgut":
            if mahd_zeitpunkt == "Sommermahd":
                lager_kosten_pro_ha_jahr = {"In einer Halle": 227.25, "Auf einer freien Fläche mit Abdeckung": 86.36}.get(lagerung_art, 0.0)
            else:
                lager_kosten_pro_ha_jahr = {"In einer Halle": 147.00, "Auf einer freien Fläche mit Abdeckung": 55.86}.get(lagerung_art, 0.0)
        elif ernteform_biomasse in ["Rundballen", "Quaderballen"]:
            if mahd_zeitpunkt == "Sommermahd":
                lager_kosten_pro_ha_jahr = {"In einer Halle": 386.33, "In einem Altgebäude": 166.65, "Auf einer freien Fläche mit Abdeckung": 80.30}.get(lagerung_art, 0.0)
            else:
                lager_kosten_pro_ha_jahr = {"In einer Halle": 249.90, "In einem Altgebäude": 107.80, "Auf einer freien Fläche mit Abdeckung": 51.94}.get(lagerung_art, 0.0)
        else:
            lager_kosten_pro_ha_jahr = {"In einer Halle": 120.0, "In einem Altgebäude": 65.0, "Auf einer freien Fläche mit Abdeckung": 35.0}.get(lagerung_art, 0.0)

    ist_sommer = (mahd_zeitpunkt == "Sommermahd")
    nutzung_erloes_pro_ha_jahr = 1050.0

    if verwertung == "Dachreed" or folge_auswahl == "Sortierung zu Dachreetbunden":
        nutzung_erloes_pro_ha_jahr = 4704.00
    elif verwertung == "Dämmplatten" or folge_auswahl in ["Dämmplatten", "Dämmplatten & Leichtbaumatten"]:
        nutzung_erloes_pro_ha_jahr = 4410.00
    elif folge_auswahl in ["Einblasdämmung", "Dämmmatten"]:
        nutzung_erloes_pro_ha_jahr = 13600.00
    elif folge_auswahl == "Putzträger":
        nutzung_erloes_pro_ha_jahr = 1750.00
    elif folge_auswahl == "Zuschlagstoff für Lehm- und Kalkputze":
        nutzung_erloes_pro_ha_jahr = 1400.00
    elif folge_auswahl == "Papier- und Kartonherstellung" or verwertung == "Papier herstellen":
        nutzung_erloes_pro_ha_jahr = 1127.00
    elif folge_auswahl in ["Plattenwerkstoffe", "Faserplatten und Biokunststoffe"] or verwertung == "Faserplatten & Dämmstoffe":
        nutzung_erloes_pro_ha_jahr = 632.50 if ist_sommer else 2400.00
    elif folge_auswahl == "Formteile":
        nutzung_erloes_pro_ha_jahr = 715.00 if ist_sommer else 1440.00
    elif (
        ist_mobile_pellet_oder_brikett
        or folge_auswahl in [
            "Pellets",
            "Briketts",
            "Pellets und Briketts",
            "Stationäre Pelletieranlage",
            "Brennstoff-Pellets / Briketts"
        ]
        or ballen_winter_option in ["Pellets", "Briketts"]
    ):
        nutzung_erloes_pro_ha_jahr = 2100.00
    elif verwertung == "Thermische Verwertung" and folge_auswahl == "Verbrennung":
        if ernteform_biomasse == "Häckselgut":
            nutzung_erloes_pro_ha_jahr = 1430.80
        elif ernteform_biomasse in ["Rundballen", "Quaderballen"]:
            nutzung_erloes_pro_ha_jahr = 950.60 if etablierungs_art == "Erstetablierung" else 676.20
    elif folge_auswahl == "Heu":
        nutzung_erloes_pro_ha_jahr = 211.50 if ist_sommer else 395.25
    elif folge_auswahl in ["Biogasproduktion", "Biogassubstrat", "Biogasanlage", "Biogas"]:
        nutzung_erloes_pro_ha_jahr = 100.00
    elif verwertung in ["Kultursubstrate", "Torfersatz in Kultursubstraten"]:
        nutzung_erloes_pro_ha_jahr = 375.00 if ist_sommer else 1200.00
    elif folge_auswahl == "Torf- und Kompostersatz":
        nutzung_erloes_pro_ha_jahr = 275.00 if ist_sommer else 480.00
    elif folge_auswahl == "Mulchmaterial" or verwertung == "Mulch-Pellets":
        nutzung_erloes_pro_ha_jahr = 225.00 if ist_sommer else 720.00
    elif verwertung in ["Einstreu", "Tiereinstreu"] or folge_auswahl in ["Einstreu", "Tiereinstreu"]:
        nutzung_erloes_pro_ha_jahr = 720.00
    elif folge_auswahl in ["Raufutter", "Silage"] or verwertung == "Raufutterersatz":
        nutzung_erloes_pro_ha_jahr = 500.00
    elif folge_auswahl == "Dünger" or verwertung == "Organischer Dünger":
        nutzung_erloes_pro_ha_jahr = 300.00 if ist_sommer else 160.00

    kauf_annuitaet_pro_ha = (kaufkosten_gesamt / 10.0) / flaechen_groesse if flaechen_groesse > 0 else 0.0
    kosten_pro_ha = (
        etablierung_kosten_pro_ha_jahr
        + laufende_kosten_pro_ha_jahr
        + sonderkosten_schilf_pro_ha_jahr
        + erntekosten_pro_ha_jahr
        + endprodukt_kosten_pro_ha_jahr
        + transport_kosten_pro_ha_jahr
        + lager_kosten_pro_ha_jahr
        + kauf_annuitaet_pro_ha
    )
    erloes_pro_ha = bisherige_ertraege_pro_ha + nutzung_erloes_pro_ha_jahr
    return (erloes_pro_ha - kosten_pro_ha) * flaechen_groesse


def schilf_ernteformen_fuer_mahd(mahd):
    opts = ["Häckselgut", "Rundballen", "Quaderballen", "Bunde", "Loses Langgut"]
    if mahd != "Sommermahd":
        opts.extend([
            "Pelletierte Form (mobile Pelletierungsmaschine)",
            "Brikettierte Form (mobile Brikettierungsmaschine)"
        ])
    return opts


def schilf_pfade_fuer(mahd, ernteform):
    pfade = []
    if ernteform == "Häckselgut":
        bereiche = ["Energetische Verwertung", "Bau- und Werkstoffe", "Gartenbau und Landwirtschaft"]
        if mahd != "Sommermahd":
            bereiche.append("Thermische Verwertung")
        for b in bereiche:
            if b == "Thermische Verwertung":
                folgen = ["Verbrennung"] + (["Pellets", "Briketts"] if mahd != "Sommermahd" else [])
            elif b == "Energetische Verwertung":
                folgen = []
                if mahd == "Sommermahd":
                    folgen.append("Biogasproduktion")
                if mahd == "Wintermahd":
                    folgen.append("Direkte Verbrennung")
                if mahd != "Sommermahd":
                    folgen.append("Pellets und Briketts")
                folgen.append("Zellulose-Ethanol")
                if mahd == "Sommermahd":
                    folgen.append("Biogasanlage")
            elif b == "Bau- und Werkstoffe":
                if mahd == "Sommermahd":
                    folgen = ["Dämmplatten", "Faserplatten und Biokunststoffe", "Papier- und Kartonherstellung"]
                else:
                    folgen = [
                        "Einblasdämmung",
                        "Dämmplatten & Leichtbaumatten",
                        "Zuschlagstoff für Lehm- und Kalkputze",
                        "Faserplatten und Biokunststoffe",
                        "Papier- und Kartonherstellung"
                    ]
            else:
                folgen = ["Torf- und Kompostersatz", "Mulchmaterial", "Pflanzenkohle & Aktivkohle"]
                if mahd == "Wintermahd":
                    folgen.insert(2, "Tiereinstreu")
            for f in folgen:
                pfade.append((b, f, None))

    elif ernteform in ["Rundballen", "Quaderballen"]:
        ballen_opts = ["Keine zusätzliche Verarbeitung", "Pellets", "Briketts", "Pressen"] if mahd == "Wintermahd" else ["Keine zusätzliche Verarbeitung"]
        for bw in ballen_opts:
            if bw != "Keine zusätzliche Verarbeitung":
                pfade.append((bw, bw, bw))
            else:
                verw_list = (
                    ["Dämmplatten", "Kultursubstrate", "Plattformchemikalien"]
                    if mahd == "Sommermahd"
                    else ["Dämmen", "Werkstoffe", "Thermische Verwertung", "Kultursubstrate", "Einstreu", "Bio-Aktivkohle", "Plattformchemikalien"]
                )
                for v in verw_list:
                    if v == "Dämmen":
                        for f in ["Dämmplatten", "Putzträger"]:
                            pfade.append((v, f, bw))
                    elif v == "Werkstoffe":
                        for f in ["Plattenwerkstoffe", "Formteile"]:
                            pfade.append((v, f, bw))
                    elif v == "Thermische Verwertung":
                        t_opts = ["Verbrennung", "Ethanol"] + (["Briketts", "Pellets"] if mahd != "Sommermahd" else [])
                        for f in t_opts:
                            pfade.append((v, f, bw))
                    else:
                        pfade.append((v, None, bw))

    elif ernteform == "Bunde":
        verw_list = (
            ["Dämmplatten", "Kultursubstrate", "Plattformchemikalien"]
            if mahd == "Sommermahd"
            else ["Dachreed", "Dämmen", "Werkstoffe", "Thermische Verwertung", "Kultursubstrate", "Einstreu", "Bio-Aktivkohle", "Plattformchemikalien"]
        )
        for v in verw_list:
            if v == "Dämmen":
                for f in ["Dämmplatten", "Putzträger"]:
                    pfade.append((v, f, None))
            elif v == "Werkstoffe":
                for f in ["Plattenwerkstoffe", "Formteile"]:
                    pfade.append((v, f, None))
            elif v == "Thermische Verwertung":
                t_opts = ["Verbrennung", "Ethanol"] + (["Briketts", "Pellets"] if mahd != "Sommermahd" else [])
                for f in t_opts:
                    pfade.append((v, f, None))
            else:
                pfade.append((v, None, None))

    elif ernteform == "Loses Langgut":
        direkt = (
            ["Raufutter", "Heu", "Silage", "Dünger", "Mulchmaterial"]
            if mahd == "Sommermahd"
            else ["Heu", "Einstreu", "Dünger", "Mulchmaterial"]
        )
        for f in direkt:
            pfade.append(("Direkte Nutzung", f, None))
        weiter = (
            ["Biogassubstrat"]
            if mahd == "Sommermahd"
            else ["Stationäre Pelletieranlage", "Briketts", "Einblasdämmung", "Biogassubstrat", "Pflanzenkohle", "Sortierung zu Dachreetbunden"]
        )
        for f in weiter:
            pfade.append(("Weiterverarbeitung", f, None))

    else:
        pellet_opts = [
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
        for v in pellet_opts:
            pfade.append((v, v, None))

    return pfade


def max_netto_fuer_schilf_teilbaum(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    kaufkosten_gesamt,
    etab_art=None,
    etab_detail=None,
    mahd=None,
    ernteform=None,
    verwertung=None,
    folge=None,
    ballen_winter=None,
    transport_bekannt=None,
    transport_km=None,
    lagerung_geplant=None,
    lagerung_art=None
):
    etab_kombis = (
        [(etab_art, etab_detail)]
        if etab_art is not None
        else [
            ("Natürliche Sukzession", None),
            ("Erstetablierung", "Aussaat"),
            ("Erstetablierung", "Anpflanzung mit Jungpflanzen")
        ]
    )
    mahd_liste = [mahd] if mahd is not None else ["Sommermahd", "Wintermahd"]

    bester_netto = None
    for ea, ed in etab_kombis:
        for m in mahd_liste:
            ef_liste = [ernteform] if ernteform is not None else schilf_ernteformen_fuer_mahd(m)
            for ef in ef_liste:
                alle_pfade = schilf_pfade_fuer(m, ef)
                for v, f, bw in alle_pfade:
                    if verwertung is not None and v != verwertung:
                        continue
                    if folge is not None and f != folge:
                        continue
                    if ballen_winter is not None and bw != ballen_winter:
                        continue

                    tb = transport_bekannt if transport_bekannt is not None else "Ja"
                    tk = transport_km if transport_km is not None else 2.5
                    lg = lagerung_geplant if lagerung_geplant is not None else "Nein"
                    la = lagerung_art if lagerung_art is not None else None

                    netto = berechne_schilf_netto_pro_ha(
                        flaechen_groesse=flaechen_groesse,
                        bisherige_ertraege_pro_ha=bisherige_ertraege_pro_ha,
                        etablierungs_art=ea,
                        etablierungs_detail=ed,
                        mahd_zeitpunkt=m,
                        ernteform_biomasse=ef,
                        verwertung=v,
                        folge_auswahl=f,
                        ballen_winter_option=bw,
                        erntetechnik=None,
                        transport_bekannt=tb,
                        transport_km=tk,
                        lagerung_geplant=lg,
                        lagerung_art=la,
                        kaufkosten_gesamt=kaufkosten_gesamt
                    )
                    if bester_netto is None or netto > bester_netto:
                        bester_netto = netto
    return bester_netto if bester_netto is not None else 0.0


# ==========================================
# BERECHNUNGSLOGIK ROHRKOLBEN
# ==========================================
def berechne_rohrkolben_kosten_und_erloes(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    mahd_zeitpunkt,
    ernteform_biomasse,
    verwertung,
    folge_auswahl,
    ballen_winter_option,
    transport_bekannt,
    transport_km,
    lagerung_geplant,
    lagerung_art,
    kaufkosten_gesamt
):
    etablierung_kosten_pro_ha_jahr = 1124.67
    laufende_kosten_pro_ha_jahr = 925.00

    ist_mobile_pellet = (ernteform_biomasse == "Pelletierte Form (mobile Pelletierungsmaschine)")
    ist_mobile_brikett = (ernteform_biomasse == "Brikettierte Form (mobile Brikettierungsmaschine)")
    ist_mobile_pellet_oder_brikett = ist_mobile_pellet or ist_mobile_brikett

    if ernteform_biomasse == "Häckselgut":
        erntekosten_pro_ha_jahr = 620.00
    elif ernteform_biomasse == "Bunde":
        erntekosten_pro_ha_jahr = 1600.00
    elif ernteform_biomasse in ["Rundballen", "Quaderballen", "Loses Langgut"]:
        erntekosten_pro_ha_jahr = 420.00
    elif ist_mobile_pellet:
        erntekosten_pro_ha_jahr = 1857.83
    elif ist_mobile_brikett:
        erntekosten_pro_ha_jahr = 414.00
    else:
        erntekosten_pro_ha_jahr = 420.00

    if ernteform_biomasse in ["Rundballen", "Quaderballen"] and mahd_zeitpunkt == "Wintermahd":
        erntekosten_pro_ha_jahr += {
            "Pellets": 601.96,
            "Briketts": 414.00,
            "Pressen": 621.00
        }.get(ballen_winter_option, 0.0)

    endprodukt_kosten_pro_ha_jahr = 0.0
    if not ist_mobile_pellet_oder_brikett:
        if folge_auswahl in ["Pellets", "Pellets und Briketts", "Stationäre Pelletieranlage"]:
            endprodukt_kosten_pro_ha_jahr = 601.96
        elif folge_auswahl == "Briketts":
            endprodukt_kosten_pro_ha_jahr = 414.00
        elif (
            folge_auswahl in ["Formteile", "Plattenwerkstoffe", "Faserplatten und Biokunststoffe"]
            or verwertung == "Werkstoffe"
        ):
            endprodukt_kosten_pro_ha_jahr = 920.00
        elif folge_auswahl == "Biokunststoffe":
            endprodukt_kosten_pro_ha_jahr = 1280.00
        elif (
            folge_auswahl in ["Einblasdämmung", "Dämmmatten", "Dämmstoffe (Einblasdämmung / Dämmmatten)"]
            or verwertung in ["Dämmen und Bauen", "Bau- & Dämmstoffe"]
        ):
            endprodukt_kosten_pro_ha_jahr = 11200.00

    ist_pellet_oder_brikett_produkt = (
        ist_mobile_pellet_oder_brikett
        or folge_auswahl in ["Pellets", "Briketts", "Pellets und Briketts", "Stationäre Pelletieranlage"]
        or ballen_winter_option in ["Pellets", "Briketts"]
    )
    ist_ballen_oder_langgut = ernteform_biomasse in ["Rundballen", "Quaderballen", "Loses Langgut", "Bunde"]

    if ist_pellet_oder_brikett_produkt:
        if transport_bekannt == "Ja":
            transport_kosten_pro_ha_jahr = {
                2.5: 23.80,
                5.0: 27.90,
                10.0: 35.20,
                20.0: 49.70,
                30.0: 63.10,
                50.0: 92.10
            }.get(transport_km, 56.40)
        else:
            transport_kosten_pro_ha_jahr = 56.40
    elif ernteform_biomasse == "Häckselgut":
        if transport_bekannt == "Ja":
            transport_kosten_pro_ha_jahr = {
                2.5: 121.10,
                5.0: 145.10,
                10.0: 194.30,
                20.0: 291.40,
                30.0: 389.90,
                50.0: 585.50
            }.get(transport_km, 340.65)
        else:
            transport_kosten_pro_ha_jahr = 340.65
    elif ist_ballen_oder_langgut:
        if transport_bekannt == "Ja":
            transport_kosten_pro_ha_jahr = {
                2.5: 72.10,
                5.0: 82.20,
                10.0: 100.00,
                20.0: 136.60,
                30.0: 173.30,
                50.0: 248.00
            }.get(transport_km, 154.95)
        else:
            transport_kosten_pro_ha_jahr = 154.95
    else:
        transport_kosten_pro_ha_jahr = 154.95

    lager_kosten_pro_ha_jahr = 0.0
    if lagerung_geplant == "Ja":
        if ist_pellet_oder_brikett_produkt:
            if lagerung_art == "In einer Halle":
                lager_kosten_pro_ha_jahr = 135.13
        elif ernteform_biomasse == "Häckselgut":
            lager_kosten_pro_ha_jahr = {
                "In einer Halle": 194.10,
                "Auf einer freien Fläche mit Abdeckung": 73.76
            }.get(lagerung_art, 0.0)
        else:
            lager_kosten_pro_ha_jahr = {
                "In einer Halle": 329.97,
                "In einem Altgebäude": 142.34,
                "Auf einer freien Fläche mit Abdeckung": 68.58
            }.get(lagerung_art, 0.0)

    ist_sommer = (mahd_zeitpunkt == "Sommermahd")
    nutzung_erloes_pro_ha_jahr = 1150.0

    if verwertung == "Samen" or folge_auswahl in [
        "Samen zur Weitervermehrung nutzen",
        "Fasern als Füllfaser verwenden",
        "Fasern als Dämmfaser verwenden"
    ]:
        nutzung_erloes_pro_ha_jahr = 1750.00
    elif verwertung == "Dämmplatten" or folge_auswahl in ["Dämmplatten", "Dämmplatten & Leichtbaumatten"]:
        nutzung_erloes_pro_ha_jahr = 3000.00
    elif folge_auswahl in ["Einblasdämmung", "Dämmmatten"] or verwertung in ["Dämmen und Bauen", "Bau- & Dämmstoffe"]:
        nutzung_erloes_pro_ha_jahr = 17595.00
    elif folge_auswahl == "Zuschlagstoff für Lehm- und Kalkputze":
        nutzung_erloes_pro_ha_jahr = 1811.50
    elif folge_auswahl in ["Plattenwerkstoffe", "Faserplatten und Biokunststoffe"] or verwertung == "Faserplatten & Dämmstoffe":
        nutzung_erloes_pro_ha_jahr = 747.50 if ist_sommer else 2846.50
    elif folge_auswahl == "Formteile" or verwertung == "Werkstoffe":
        nutzung_erloes_pro_ha_jahr = 747.50 if ist_sommer else 1863.00
    elif folge_auswahl == "Biokunststoffe":
        nutzung_erloes_pro_ha_jahr = 2329.00
    elif folge_auswahl == "Papier- und Kartonherstellung" or verwertung == "Papier herstellen":
        nutzung_erloes_pro_ha_jahr = 1190.50
    elif verwertung in ["Plattformchemikalien", "Biokunststoffe & Spritzguss"]:
        nutzung_erloes_pro_ha_jahr = 585.00 if ist_sommer else 1242.00
    elif verwertung in ["Bio-Aktivkohle"] or folge_auswahl in ["Pflanzenkohle & Aktivkohle", "Pflanzenkohle"]:
        nutzung_erloes_pro_ha_jahr = 1190.50
    elif (
        ist_mobile_pellet_oder_brikett
        or folge_auswahl in ["Pellets", "Briketts", "Pellets und Briketts", "Stationäre Pelletieranlage", "Direkte Verbrennung", "Verbrennung"]
        or ballen_winter_option in ["Pellets", "Briketts"]
        or verwertung in ["Thermische Verwertung", "Verbrennen"]
    ):
        nutzung_erloes_pro_ha_jahr = 673.00
    elif folge_auswahl in ["Biogasproduktion", "Biogassubstrat", "Biogas-Substrat"]:
        nutzung_erloes_pro_ha_jahr = 220.00
    elif verwertung in ["Gartenbausubstrate", "Torfersatz in Kultursubstraten"] or folge_auswahl == "Torf- und Kompostersatz":
        nutzung_erloes_pro_ha_jahr = 455.00 if ist_sommer else 1552.50
    elif folge_auswahl == "Mulchmaterial" or verwertung == "Mulch-Pellets":
        nutzung_erloes_pro_ha_jahr = 292.50 if ist_sommer else 931.50
    elif verwertung in ["Einstreu", "Tiereinstreu"] or folge_auswahl in ["Einstreu", "Tiereinstreu"]:
        nutzung_erloes_pro_ha_jahr = 931.50
    elif folge_auswahl in ["Raufutter", "Heu"] or verwertung == "Raufutterersatz":
        nutzung_erloes_pro_ha_jahr = 617.50
    elif folge_auswahl == "Silage":
        nutzung_erloes_pro_ha_jahr = 660.00
    elif folge_auswahl == "Dünger" or verwertung == "Organischer Dünger":
        nutzung_erloes_pro_ha_jahr = 357.50 if ist_sommer else 207.50
    elif ernteform_biomasse == "Häckselgut":
        nutzung_erloes_pro_ha_jahr = 1728.45

    kauf_annuitaet_pro_ha = (kaufkosten_gesamt / 10.0) / flaechen_groesse if flaechen_groesse > 0 else 0.0
    kosten_pro_ha = (
        etablierung_kosten_pro_ha_jahr
        + laufende_kosten_pro_ha_jahr
        + erntekosten_pro_ha_jahr
        + endprodukt_kosten_pro_ha_jahr
        + transport_kosten_pro_ha_jahr
        + lager_kosten_pro_ha_jahr
        + kauf_annuitaet_pro_ha
    )
    erloes_pro_ha = bisherige_ertraege_pro_ha + nutzung_erloes_pro_ha_jahr
    netto_gesamt = (erloes_pro_ha - kosten_pro_ha) * flaechen_groesse

    return {
        "etablierung": etablierung_kosten_pro_ha_jahr,
        "laufend": laufende_kosten_pro_ha_jahr,
        "ernte": erntekosten_pro_ha_jahr,
        "endprodukt": endprodukt_kosten_pro_ha_jahr,
        "transport": transport_kosten_pro_ha_jahr,
        "lager": lager_kosten_pro_ha_jahr,
        "erloes_ha": nutzung_erloes_pro_ha_jahr,
        "netto_gesamt": netto_gesamt
    }


def berechne_rohrkolben_netto_pro_ha(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    mahd_zeitpunkt,
    ernteform_biomasse,
    verwertung,
    folge_auswahl,
    ballen_winter_option,
    transport_bekannt,
    transport_km,
    lagerung_geplant,
    lagerung_art,
    kaufkosten_gesamt
):
    return berechne_rohrkolben_kosten_und_erloes(
        flaechen_groesse,
        bisherige_ertraege_pro_ha,
        mahd_zeitpunkt,
        ernteform_biomasse,
        verwertung,
        folge_auswahl,
        ballen_winter_option,
        transport_bekannt,
        transport_km,
        lagerung_geplant,
        lagerung_art,
        kaufkosten_gesamt
    )["netto_gesamt"]


def rohrkolben_ernteformen_fuer_mahd(mahd):
    opts = ["Häckselgut", "Rundballen", "Quaderballen", "Loses Langgut"]
    if mahd != "Sommermahd":
        opts.extend([
            "Pelletierte Form (mobile Pelletierungsmaschine)",
            "Brikettierte Form (mobile Brikettierungsmaschine)"
        ])
    return opts


def rohrkolben_pfade_fuer(mahd, ernteform):
    pfade = []
    if ernteform == "Häckselgut":
        if mahd == "Sommermahd":
            bereiche = ["Energetische Verwertung", "Bau- und Werkstoffe", "Gartenbau und Landwirtschaft"]
        else:
            bereiche = ["Thermische Verwertung", "Energetische Verwertung", "Bau- und Werkstoffe", "Gartenbau und Landwirtschaft"]

        for b in bereiche:
            if b == "Thermische Verwertung":
                folgen = ["Verbrennung", "Pellets", "Briketts"]
            elif b == "Energetische Verwertung":
                if mahd == "Sommermahd":
                    folgen = ["Biogasproduktion"]
                else:
                    folgen = ["Direkte Verbrennung", "Pellets und Briketts"]
            elif b == "Bau- und Werkstoffe":
                if mahd == "Sommermahd":
                    folgen = ["Faserplatten und Biokunststoffe"]
                else:
                    folgen = [
                        "Einblasdämmung",
                        "Dämmplatten & Leichtbaumatten",
                        "Zuschlagstoff für Lehm- und Kalkputze",
                        "Faserplatten und Biokunststoffe",
                        "Papier- und Kartonherstellung"
                    ]
            else:
                if mahd == "Sommermahd":
                    folgen = ["Torf- und Kompostersatz", "Mulchmaterial"]
                else:
                    folgen = ["Torf- und Kompostersatz", "Mulchmaterial", "Tiereinstreu", "Pflanzenkohle & Aktivkohle"]
            for f in folgen:
                pfade.append((b, f, None))

    elif ernteform in ["Rundballen", "Quaderballen"]:
        ballen_opts = ["Keine zusätzliche Verarbeitung", "Pellets", "Briketts", "Pressen"] if mahd == "Wintermahd" else ["Keine zusätzliche Verarbeitung"]
        for bw in ballen_opts:
            if bw != "Keine zusätzliche Verarbeitung":
                pfade.append((bw, bw, bw))
            else:
                if mahd == "Sommermahd":
                    verw_list = ["Werkstoffe", "Gartenbausubstrate", "Plattformchemikalien"]
                else:
                    verw_list = [
                        "Dämmen und Bauen",
                        "Werkstoffe",
                        "Thermische Verwertung",
                        "Samen",
                        "Fasern",
                        "Gartenbausubstrate",
                        "Einstreu",
                        "Plattformchemikalien"
                    ]
                for v in verw_list:
                    if v == "Dämmen und Bauen":
                        for f in ["Einblasdämmung", "Dämmmatten", "Dämmplatten", "Plattenwerkstoffe"]:
                            pfade.append((v, f, bw))
                    elif v == "Werkstoffe":
                        f_opts = ["Formteile"] if mahd == "Sommermahd" else ["Plattenwerkstoffe", "Formteile"]
                        for f in f_opts:
                            pfade.append((v, f, bw))
                    elif v == "Thermische Verwertung":
                        for f in ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung"]:
                            pfade.append((v, f, bw))
                    elif v in ["Samen", "Fasern"]:
                        for f in ["Samen zur Weitervermehrung nutzen", "Fasern als Füllfaser verwenden", "Fasern als Dämmfaser verwenden"]:
                            pfade.append((v, f, bw))
                    else:
                        pfade.append((v, None, bw))

    elif ernteform == "Loses Langgut":
        if mahd == "Sommermahd":
            direkt = ["Raufutter", "Heu", "Silage", "Dünger", "Mulchmaterial"]
            weiter = ["Biogassubstrat"]
        else:
            direkt = ["Einstreu", "Dünger", "Mulchmaterial"]
            weiter = ["Stationäre Pelletieranlage", "Briketts", "Einblasdämmung", "Pflanzenkohle"]
        for f in direkt:
            pfade.append(("Direkte Nutzung", f, None))
        for f in weiter:
            pfade.append(("Weiterverarbeitung", f, None))

    else:
        pellet_opts = [
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
        for v in pellet_opts:
            pfade.append((v, v, None))

    return pfade


def max_netto_fuer_rohrkolben_teilbaum(
    flaechen_groesse,
    bisherige_ertraege_pro_ha,
    kaufkosten_gesamt,
    mahd=None,
    ernteform=None,
    verwertung=None,
    folge=None,
    ballen_winter=None,
    transport_bekannt=None,
    transport_km=None,
    lagerung_geplant=None,
    lagerung_art=None
):
    mahd_liste = [mahd] if mahd is not None else ["Sommermahd", "Wintermahd"]
    bester_netto = None
    for m in mahd_liste:
        ef_liste = [ernteform] if ernteform is not None else rohrkolben_ernteformen_fuer_mahd(m)
        for ef in ef_liste:
            alle_pfade = rohrkolben_pfade_fuer(m, ef)
            for v, f, bw in alle_pfade:
                if verwertung is not None and v != verwertung:
                    continue
                if folge is not None and f != folge:
                    continue
                if ballen_winter is not None and bw != ballen_winter:
                    continue

                tb = transport_bekannt if transport_bekannt is not None else "Ja"
                tk = transport_km if transport_km is not None else 2.5
                lg = lagerung_geplant if lagerung_geplant is not None else "Nein"
                la = lagerung_art if lagerung_art is not None else None

                netto = berechne_rohrkolben_netto_pro_ha(
                    flaechen_groesse=flaechen_groesse,
                    bisherige_ertraege_pro_ha=bisherige_ertraege_pro_ha,
                    mahd_zeitpunkt=m,
                    ernteform_biomasse=ef,
                    verwertung=v,
                    folge_auswahl=f,
                    ballen_winter_option=bw,
                    transport_bekannt=tb,
                    transport_km=tk,
                    lagerung_geplant=lg,
                    lagerung_art=la,
                    kaufkosten_gesamt=kaufkosten_gesamt
                )
                if bester_netto is None or netto > bester_netto:
                    bester_netto = netto
    return bester_netto if bester_netto is not None else 0.0


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
        st.success("💡 **Hinweis:** Optionen in :green[**grüner Schrift**] kennzeichnen jeweils die Option mit dem höchsten wirtschaftlichen Erlös.")

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

        ist_schilf_step1 = (bew_tmp == "Schilf")
        ist_rgg_step1 = (bew_tmp == "Rohrglanzgras")
        aktiv_step1 = ist_schilf_step1 or ist_rgg_step1

        etab_tmp = None
        etab_detail_tmp = None
        if bew_tmp not in ["Tierhaltung", "Photo-Voltaik"]:
            etab_optionen = ["Natürliche Sukzession", "Erstetablierung"]
            beste_etab, _ = (None, None)
            if ist_schilf_step1:
                beste_etab, _ = beste_option_ermitteln(
                    etab_optionen,
                    lambda opt: max_netto_fuer_schilf_teilbaum(
                        flaechen_groesse, ertrag_tmp, kaufkosten_gesamt, etab_art=opt
                    )
                )
            elif ist_rgg_step1:
                beste_etab, _ = beste_option_ermitteln(
                    etab_optionen,
                    lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                        flaechen_groesse, ertrag_tmp, kaufkosten_gesamt, etab_art=opt
                    )
                )

            etab_tmp = st.radio(
                "Möchten Sie natürliche Sukzession oder eine Erstetablierung durchführen?",
                etab_optionen,
                index=0 if etablierungs_art != "Erstetablierung" else 1,
                format_func=lambda opt: format_radio_option(opt, beste_etab, aktiv_step1),
                key="input_etablierung"
            )

            if etab_tmp == "Erstetablierung" and not ist_rgg_step1:
                detail_optionen = ["Aussaat", "Anpflanzung mit Jungpflanzen"]
                beste_detail, _ = (None, None)
                if ist_schilf_step1:
                    beste_detail, _ = beste_option_ermitteln(
                        detail_optionen,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, ertrag_tmp, kaufkosten_gesamt,
                            etab_art="Erstetablierung", etab_detail=opt
                        )
                    )

                etab_detail_tmp = st.radio(
                    "Wie erfolgt die Erstetablierung?",
                    detail_optionen,
                    index=0 if etablierungs_detail != "Anpflanzung mit Jungpflanzen" else 1,
                    format_func=lambda opt: format_radio_option(opt, beste_detail, ist_schilf_step1),
                    key="input_etablierung_detail"
                )
            elif etab_tmp == "Erstetablierung" and ist_rgg_step1:
                etab_detail_tmp = "Aussaat"

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

        ist_schilf = (bewirtschaftung == "Schilf")
        ist_rohrkolben = (bewirtschaftung == "Rohrkolben")
        ist_rgg = (bewirtschaftung == "Rohrglanzgras")
        hat_opt_highlight = ist_schilf or ist_rohrkolben or ist_rgg

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
        ballen_endprodukt_gewuenscht = False

        # A) Rohrglanzgras, Schilf, Rohrkolben, Seggen
        if bewirtschaftung in ["Rohrglanzgras", "Schilf", "Rohrkolben", "Seggen"]:
            mahd_optionen = ["Sommermahd", "Wintermahd"]
            beste_mahd, _ = (None, None)
            if ist_schilf:
                beste_mahd, _ = beste_option_ermitteln(
                    mahd_optionen,
                    lambda opt: max_netto_fuer_schilf_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, etab_detail=etablierungs_detail, mahd=opt
                    )
                )
            elif ist_rohrkolben:
                beste_mahd, _ = beste_option_ermitteln(
                    mahd_optionen,
                    lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt, mahd=opt
                    )
                )
            elif ist_rgg:
                beste_mahd, _ = beste_option_ermitteln(
                    mahd_optionen,
                    lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, mahd=opt
                    )
                )

            mahd_tmp = st.radio(
                f"Wann erfolgt die Mahd bei {bewirtschaftung}?",
                mahd_optionen,
                format_func=lambda opt: format_radio_option(opt, beste_mahd, hat_opt_highlight),
                key=f"mahd_{bewirtschaftung}"
            )

            if ist_rohrkolben:
                ernteform_optionen = rohrkolben_ernteformen_fuer_mahd(mahd_tmp)
            elif ist_rgg:
                ernteform_optionen = rohrglanzgras_ernteformen_fuer_mahd(mahd_tmp)
            else:
                ernteform_optionen = schilf_ernteformen_fuer_mahd(mahd_tmp)

            beste_ernteform, _ = (None, None)
            if ist_schilf:
                beste_ernteform, _ = beste_option_ermitteln(
                    ernteform_optionen,
                    lambda opt: max_netto_fuer_schilf_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                        mahd=mahd_tmp, ernteform=opt
                    )
                )
            elif ist_rohrkolben:
                beste_ernteform, _ = beste_option_ermitteln(
                    ernteform_optionen,
                    lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        mahd=mahd_tmp, ernteform=opt
                    )
                )
            elif ist_rgg:
                beste_ernteform, _ = beste_option_ermitteln(
                    ernteform_optionen,
                    lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=opt
                    )
                )

            ernteform_tmp = opt_selectbox(
                "In welcher Form möchten Sie die Biomasse ernten?",
                ernteform_optionen,
                key=f"ernteform_{bewirtschaftung}_{mahd_tmp}",
                aktiv=hat_opt_highlight,
                beste_opt=beste_ernteform
            )

            # 1) Häckselgut
            if ernteform_tmp == "Häckselgut":
                bereich_optionen = [
                    "Energetische Verwertung",
                    "Bau- und Werkstoffe",
                    "Gartenbau und Landwirtschaft"
                ]
                if not (bewirtschaftung in ["Schilf", "Rohrkolben"] and mahd_tmp == "Sommermahd"):
                    bereich_optionen.append("Thermische Verwertung")

                if ist_rgg:
                    bereich_optionen = [
                        b for b in bereich_optionen
                        if any(
                            rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, b, f, None) > 0
                            for _, f, _ in rohrglanzgras_pfade_fuer(etablierungs_art, mahd_tmp, ernteform_tmp)
                            if _ == b
                        )
                    ]

                beste_verw, _ = (None, None)
                if ist_schilf:
                    beste_verw, _ = beste_option_ermitteln(
                        bereich_optionen,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )
                elif ist_rohrkolben:
                    beste_verw, _ = beste_option_ermitteln(
                        bereich_optionen,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )
                elif ist_rgg:
                    beste_verw, _ = beste_option_ermitteln(
                        bereich_optionen,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )

                verwertung_tmp = opt_selectbox(
                    "Wofür soll das Häckselgut genutzt werden?",
                    bereich_optionen,
                    key=f"haeckselfeld_bereich_{bewirtschaftung}_{mahd_tmp}",
                    aktiv=hat_opt_highlight,
                    beste_opt=beste_verw
                )

                if verwertung_tmp == "Thermische Verwertung":
                    thermisch_haeckselfeld_optionen = ["Verbrennung"]
                    if mahd_tmp != "Sommermahd":
                        thermisch_haeckselfeld_optionen.extend(["Pellets", "Briketts"])
                    if ist_rgg:
                        thermisch_haeckselfeld_optionen = [
                            f for f in thermisch_haeckselfeld_optionen
                            if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, None) > 0
                        ]

                    beste_folge, _ = (None, None)
                    if ist_schilf:
                        beste_folge, _ = beste_option_ermitteln(
                            thermisch_haeckselfeld_optionen,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rohrkolben:
                        beste_folge, _ = beste_option_ermitteln(
                            thermisch_haeckselfeld_optionen,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rgg:
                        beste_folge, _ = beste_option_ermitteln(
                            thermisch_haeckselfeld_optionen,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )

                    folge_tmp = opt_selectbox(
                        "Welche thermische Verwertung soll erfolgen?",
                        thermisch_haeckselfeld_optionen,
                        key=f"haeckselfeld_thermisch_{bewirtschaftung}_{mahd_tmp}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_folge
                    )

                elif verwertung_tmp == "Energetische Verwertung":
                    energie_optionen = []
                    if mahd_tmp == "Sommermahd":
                        energie_optionen.append("Biogasproduktion")
                    if mahd_tmp == "Wintermahd":
                        energie_optionen.append("Direkte Verbrennung")
                    if mahd_tmp != "Sommermahd":
                        energie_optionen.append("Pellets und Briketts")
                    if bewirtschaftung != "Rohrkolben":
                        energie_optionen.append("Zellulose-Ethanol")
                    if bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd":
                        energie_optionen.append("Biogasanlage")
                    if ist_rgg:
                        energie_optionen = [
                            f for f in energie_optionen
                            if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, None) > 0
                        ]

                    beste_folge, _ = (None, None)
                    if ist_schilf:
                        beste_folge, _ = beste_option_ermitteln(
                            energie_optionen,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rohrkolben:
                        beste_folge, _ = beste_option_ermitteln(
                            energie_optionen,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rgg:
                        beste_folge, _ = beste_option_ermitteln(
                            energie_optionen,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )

                    folge_tmp = opt_selectbox(
                        "Welche energetische Verwertung soll erfolgen?",
                        energie_optionen,
                        key=f"haeckselfeld_energie_{bewirtschaftung}_{mahd_tmp}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_folge
                    )

                elif verwertung_tmp == "Bau- und Werkstoffe":
                    if bewirtschaftung == "Schilf" and mahd_tmp == "Sommermahd":
                        stoff_optionen = [
                            "Dämmplatten",
                            "Faserplatten und Biokunststoffe",
                            "Papier- und Kartonherstellung"
                        ]
                    elif bewirtschaftung == "Rohrkolben" and mahd_tmp == "Sommermahd":
                        stoff_optionen = ["Faserplatten und Biokunststoffe"]
                    elif ist_rgg and mahd_tmp == "Sommermahd":
                        stoff_optionen = ["Faserplatten und Biokunststoffe"]
                    else:
                        stoff_optionen = [
                            "Einblasdämmung",
                            "Dämmplatten & Leichtbaumatten",
                            "Zuschlagstoff für Lehm- und Kalkputze",
                            "Faserplatten und Biokunststoffe",
                            "Papier- und Kartonherstellung"
                        ]
                    if ist_rgg:
                        stoff_optionen = [
                            f for f in stoff_optionen
                            if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, None) > 0
                        ]

                    beste_folge, _ = (None, None)
                    if ist_schilf:
                        beste_folge, _ = beste_option_ermitteln(
                            stoff_optionen,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rohrkolben:
                        beste_folge, _ = beste_option_ermitteln(
                            stoff_optionen,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rgg:
                        beste_folge, _ = beste_option_ermitteln(
                            stoff_optionen,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )

                    folge_tmp = opt_selectbox(
                        "Welche Verwertung im Bereich Bau- und Werkstoffe soll erfolgen?",
                        stoff_optionen,
                        key=f"haeckselfeld_stoff_{bewirtschaftung}_{mahd_tmp}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_folge
                    )

                elif verwertung_tmp == "Gartenbau und Landwirtschaft":
                    if bewirtschaftung in ["Rohrkolben", "Rohrglanzgras"] and mahd_tmp == "Sommermahd":
                        garten_optionen = [
                            "Torf- und Kompostersatz",
                            "Mulchmaterial"
                        ]
                    else:
                        garten_optionen = [
                            "Torf- und Kompostersatz",
                            "Mulchmaterial",
                            "Pflanzenkohle & Aktivkohle"
                        ]
                        if mahd_tmp == "Wintermahd":
                            garten_optionen.insert(2, "Tiereinstreu")
                    if ist_rgg:
                        garten_optionen = [
                            f for f in garten_optionen
                            if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, None) > 0
                        ]

                    beste_folge, _ = (None, None)
                    if ist_schilf:
                        beste_folge, _ = beste_option_ermitteln(
                            garten_optionen,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rohrkolben:
                        beste_folge, _ = beste_option_ermitteln(
                            garten_optionen,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rgg:
                        beste_folge, _ = beste_option_ermitteln(
                            garten_optionen,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )

                    folge_tmp = opt_selectbox(
                        "Welche Nutzung im Bereich Gartenbau und Landwirtschaft soll erfolgen?",
                        garten_optionen,
                        key=f"haeckselfeld_garten_{bewirtschaftung}_{mahd_tmp}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_folge
                    )

            # 2) Rundballen / Quaderballen
            elif ernteform_tmp in ["Rundballen", "Quaderballen"]:
                if mahd_tmp == "Wintermahd":
                    ballen_opt_list = ["Keine zusätzliche Verarbeitung", "Pellets", "Briketts", "Pressen"]
                    beste_bw, _ = (None, None)
                    if ist_schilf:
                        beste_bw, _ = beste_option_ermitteln(
                            ballen_opt_list,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp, ballen_winter=opt
                            )
                        )
                    elif ist_rohrkolben:
                        beste_bw, _ = beste_option_ermitteln(
                            ballen_opt_list,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp, ballen_winter=opt
                            )
                        )
                    elif ist_rgg:
                        beste_bw, _ = beste_option_ermitteln(
                            ballen_opt_list,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp, ballen_winter=opt
                            )
                        )

                    ballen_winter_tmp = opt_selectbox(
                        "Welche Weiterverarbeitung / Pressung für die Ballen (Wintermahd) ist geplant?",
                        ballen_opt_list,
                        key=f"ballen_winter_opt_{bewirtschaftung}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_bw
                    )

                    if ballen_winter_tmp != "Keine zusätzliche Verarbeitung":
                        ballen_endprodukt_gewuenscht = True
                        verwertung_tmp = ballen_winter_tmp
                        folge_tmp = ballen_winter_tmp

                if not ballen_endprodukt_gewuenscht:
                    if bewirtschaftung == "Rohrkolben":
                        if mahd_tmp == "Sommermahd":
                            basis_verwertung = [
                                "Werkstoffe",
                                "Gartenbausubstrate",
                                "Plattformchemikalien"
                            ]
                        else:
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
                    else:
                        if mahd_tmp == "Sommermahd":
                            basis_verwertung = [
                                "Pferdeheu",
                                "Raufutter",
                                "Proteinkonzentrat",
                                "Bau- & Dämmstoffe"
                            ]
                        else:
                            basis_verwertung = [
                                "Einstreu",
                                "Thermische Verwertung",
                                "Bau- & Dämmstoffe"
                            ]
                        if ist_rgg:
                            basis_verwertung = [
                                v for v in basis_verwertung
                                if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, v, None, ballen_winter_tmp) > 0
                                or v in ["Bau- & Dämmstoffe", "Thermische Verwertung"]
                            ]

                    beste_verw, _ = (None, None)
                    if ist_schilf:
                        beste_verw, _ = beste_option_ermitteln(
                            basis_verwertung,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=opt, ballen_winter=ballen_winter_tmp
                            )
                        )
                    elif ist_rohrkolben:
                        beste_verw, _ = beste_option_ermitteln(
                            basis_verwertung,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=opt, ballen_winter=ballen_winter_tmp
                            )
                        )
                    elif ist_rgg:
                        beste_verw, _ = beste_option_ermitteln(
                            basis_verwertung,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=opt, ballen_winter=ballen_winter_tmp
                            )
                        )

                    verwertung_tmp = opt_selectbox(
                        f"Welche Verwertung für {ernteform_tmp} streben Sie an?",
                        basis_verwertung,
                        key=f"ballen_verwertung_{bewirtschaftung}_{mahd_tmp}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_verw
                    )

            # 3) Bunde
            elif ernteform_tmp == "Bunde":
                if bewirtschaftung == "Schilf":
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
                else:
                    basis_verwertung = (
                        ["Pferdeheu", "Raufutter", "Proteinkonzentrat", "Bau- & Dämmstoffe"]
                        if mahd_tmp == "Sommermahd"
                        else ["Einstreu", "Thermische Verwertung", "Bau- & Dämmstoffe"]
                    )

                beste_verw, _ = (None, None)
                if ist_schilf:
                    beste_verw, _ = beste_option_ermitteln(
                        basis_verwertung,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )
                elif ist_rgg:
                    beste_verw, _ = beste_option_ermitteln(
                        basis_verwertung,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )

                verwertung_tmp = opt_selectbox(
                    "Welche Verwertung für Bunde streben Sie an?",
                    basis_verwertung,
                    key=f"bunde_verwertung_{bewirtschaftung}_{mahd_tmp}",
                    aktiv=(ist_schilf or ist_rgg),
                    beste_opt=beste_verw
                )

            # 4) Loses Langgut
            elif ernteform_tmp == "Loses Langgut":
                langgut_bereiche = ["Direkte Nutzung", "Weiterverarbeitung"]
                beste_verw, _ = (None, None)
                if ist_schilf:
                    beste_verw, _ = beste_option_ermitteln(
                        langgut_bereiche,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )
                elif ist_rohrkolben:
                    beste_verw, _ = beste_option_ermitteln(
                        langgut_bereiche,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )
                elif ist_rgg:
                    beste_verw, _ = beste_option_ermitteln(
                        langgut_bereiche,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt
                        )
                    )

                verwertung_tmp = opt_selectbox(
                    "Wie soll das lose Langgut genutzt werden?",
                    langgut_bereiche,
                    key=f"langgut_bereich_{bewirtschaftung}_{mahd_tmp}",
                    aktiv=hat_opt_highlight,
                    beste_opt=beste_verw
                )

                if verwertung_tmp == "Direkte Nutzung":
                    if bewirtschaftung in ["Schilf", "Rohrkolben", "Rohrglanzgras"] and mahd_tmp == "Sommermahd":
                        direkt_optionen = [
                            "Raufutter",
                            "Heu",
                            "Silage",
                            "Dünger",
                            "Mulchmaterial"
                        ]
                    elif bewirtschaftung in ["Schilf", "Rohrkolben", "Rohrglanzgras"] and mahd_tmp == "Wintermahd":
                        direkt_optionen = (
                            ["Heu", "Einstreu", "Dünger", "Mulchmaterial"]
                            if bewirtschaftung == "Schilf"
                            else ["Einstreu", "Dünger", "Mulchmaterial"]
                        )
                    else:
                        direkt_optionen = [
                            "Raufutter",
                            "Heu",
                            "Silage",
                            "Einstreu",
                            "Dünger",
                            "Mulchmaterial"
                        ]
                    if ist_rgg:
                        direkt_optionen = [
                            f for f in direkt_optionen
                            if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, None) > 0
                        ]

                    beste_folge, _ = (None, None)
                    if ist_schilf:
                        beste_folge, _ = beste_option_ermitteln(
                            direkt_optionen,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rohrkolben:
                        beste_folge, _ = beste_option_ermitteln(
                            direkt_optionen,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rgg:
                        beste_folge, _ = beste_option_ermitteln(
                            direkt_optionen,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )

                    folge_tmp = opt_selectbox(
                        "Welche direkte Nutzung soll erfolgen?",
                        direkt_optionen,
                        key=f"langgut_direkt_{bewirtschaftung}_{mahd_tmp}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_folge
                    )
                else:
                    if mahd_tmp == "Sommermahd":
                        if bewirtschaftung in ["Schilf", "Rohrkolben", "Rohrglanzgras"]:
                            weiter_optionen = ["Biogassubstrat"]
                        else:
                            weiter_optionen = [
                                "Einblasdämmung",
                                "Biogassubstrat",
                                "Pflanzenkohle"
                            ]
                    else:
                        if bewirtschaftung == "Rohrkolben":
                            weiter_optionen = [
                                "Stationäre Pelletieranlage",
                                "Briketts",
                                "Einblasdämmung",
                                "Pflanzenkohle"
                            ]
                        elif bewirtschaftung == "Rohrglanzgras":
                            weiter_optionen = [
                                "Stationäre Pelletieranlage",
                                "Briketts",
                                "Pflanzenkohle"
                            ]
                        else:
                            weiter_optionen = [
                                "Stationäre Pelletieranlage",
                                "Briketts",
                                "Einblasdämmung",
                                "Biogassubstrat",
                                "Pflanzenkohle"
                            ]
                            if bewirtschaftung == "Schilf":
                                weiter_optionen.append("Sortierung zu Dachreetbunden")
                    if ist_rgg:
                        weiter_optionen = [
                            f for f in weiter_optionen
                            if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, None) > 0
                        ]

                    beste_folge, _ = (None, None)
                    if ist_schilf:
                        beste_folge, _ = beste_option_ermitteln(
                            weiter_optionen,
                            lambda opt: max_netto_fuer_schilf_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rohrkolben:
                        beste_folge, _ = beste_option_ermitteln(
                            weiter_optionen,
                            lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )
                    elif ist_rgg:
                        beste_folge, _ = beste_option_ermitteln(
                            weiter_optionen,
                            lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                                flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                                etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                                verwertung=verwertung_tmp, folge=opt
                            )
                        )

                    folge_tmp = opt_selectbox(
                        "Welche Weiterverarbeitung soll erfolgen?",
                        weiter_optionen,
                        key=f"langgut_weiter_{bewirtschaftung}_{mahd_tmp}",
                        aktiv=hat_opt_highlight,
                        beste_opt=beste_folge
                    )

            # 5) Pelletierte oder Brikettierte Form (mobile Maschine, nur bei Wintermahd)
            else:
                if bewirtschaftung in ["Schilf", "Rohrkolben"] and mahd_tmp == "Wintermahd":
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
                if ist_rgg:
                    pellet_optionen = [
                        f for f in pellet_optionen
                        if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, f, f, None) > 0
                    ]

                beste_verw, _ = (None, None)
                if ist_schilf:
                    beste_verw, _ = beste_option_ermitteln(
                        pellet_optionen,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt, folge=opt
                        )
                    )
                elif ist_rohrkolben:
                    beste_verw, _ = beste_option_ermitteln(
                        pellet_optionen,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt, folge=opt
                        )
                    )
                elif ist_rgg:
                    beste_verw, _ = beste_option_ermitteln(
                        pellet_optionen,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp, verwertung=opt, folge=opt
                        )
                    )

                verwertung_tmp = opt_selectbox(
                    f"Welche Verwertung für '{ernteform_tmp}' streben Sie an?",
                    pellet_optionen,
                    key=f"pellet_brikett_verwertung_{bewirtschaftung}_{mahd_tmp}",
                    aktiv=hat_opt_highlight,
                    beste_opt=beste_verw
                )
                folge_tmp = verwertung_tmp

        # B) Schwarzerle
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

        # Allgemeine Folgeabfragen (nur wenn bei Ballen nicht schon eine Weiterverarbeitung gewählt wurde)
        if not ballen_endprodukt_gewuenscht:
            if verwertung_tmp in ["Dämmen und Bauen", "Bau- & Dämmstoffe"]:
                if ist_rgg:
                    daemm_opts = ["Plattenwerkstoffe"] if mahd_tmp == "Sommermahd" else ["Dämmmatten", "Dämmplatten", "Plattenwerkstoffe"]
                    daemm_opts = [
                        f for f in daemm_opts
                        if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, ballen_winter_tmp) > 0
                    ]
                else:
                    daemm_opts = ["Einblasdämmung", "Dämmmatten", "Dämmplatten", "Plattenwerkstoffe"]

                beste_folge, _ = (None, None)
                if ist_rohrkolben:
                    beste_folge, _ = beste_option_ermitteln(
                        daemm_opts,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                elif ist_rgg:
                    beste_folge, _ = beste_option_ermitteln(
                        daemm_opts,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                folge_tmp = opt_selectbox(
                    "Welche Dämm- bzw. Bauprodukte möchten Sie herstellen?",
                    daemm_opts,
                    key="folge_daemmung",
                    aktiv=(ist_rohrkolben or ist_rgg),
                    beste_opt=beste_folge
                )

            if bewirtschaftung == "Schilf" and verwertung_tmp == "Dämmen":
                schilf_daemm_opts = ["Dämmplatten", "Putzträger"]
                beste_folge, _ = beste_option_ermitteln(
                    schilf_daemm_opts,
                    lambda opt: max_netto_fuer_schilf_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                        mahd=mahd_tmp, ernteform=ernteform_tmp,
                        verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                    )
                )
                folge_tmp = opt_selectbox(
                    "Was möchten Sie aus Schilf zum Dämmen herstellen?",
                    schilf_daemm_opts,
                    key="folge_schilf_daemmen",
                    aktiv=ist_schilf,
                    beste_opt=beste_folge
                )

            if verwertung_tmp == "Werkstoffe":
                if bewirtschaftung == "Rohrkolben" and mahd_tmp == "Sommermahd":
                    werkstoff_opts = ["Formteile"]
                else:
                    werkstoff_opts = ["Plattenwerkstoffe", "Formteile"]

                beste_folge, _ = (None, None)
                if ist_schilf:
                    beste_folge, _ = beste_option_ermitteln(
                        werkstoff_opts,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                elif ist_rohrkolben:
                    beste_folge, _ = beste_option_ermitteln(
                        werkstoff_opts,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                folge_tmp = opt_selectbox(
                    "Welche Werkstoffvariante möchten Sie herstellen?",
                    werkstoff_opts,
                    key="folge_werkstoffe",
                    aktiv=(ist_schilf or ist_rohrkolben),
                    beste_opt=beste_folge
                )

            if verwertung_tmp == "Thermische Verwertung" and ernteform_tmp != "Häckselgut":
                if bewirtschaftung == "Schwarzerle":
                    folge_tmp = st.selectbox(
                        "Wie möchten Sie die Schwarzerle thermisch nutzen?",
                        ["Direkte Verbrennung"],
                        key="folge_thermisch_schwarzerle"
                    )
                elif bewirtschaftung == "Schilf":
                    thermisch_schilf_optionen = ["Verbrennung", "Ethanol"]
                    if mahd_tmp != "Sommermahd":
                        thermisch_schilf_optionen.extend(["Briketts", "Pellets"])

                    beste_folge, _ = beste_option_ermitteln(
                        thermisch_schilf_optionen,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                    folge_tmp = opt_selectbox(
                        "Wie möchten Sie das Schilf thermisch nutzen?",
                        thermisch_schilf_optionen,
                        key=f"folge_thermisch_schilf_{mahd_tmp}",
                        aktiv=ist_schilf,
                        beste_opt=beste_folge
                    )
                elif bewirtschaftung == "Rohrkolben":
                    thermisch_rk_optionen = ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung"]
                    beste_folge, _ = beste_option_ermitteln(
                        thermisch_rk_optionen,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                    folge_tmp = opt_selectbox(
                        "Wie möchten Sie den Rohrkolben thermisch nutzen?",
                        thermisch_rk_optionen,
                        key=f"folge_thermisch_rk_{mahd_tmp}",
                        aktiv=ist_rohrkolben,
                        beste_opt=beste_folge
                    )
                elif ist_rgg:
                    thermisch_rgg_optionen = ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung"]
                    thermisch_rgg_optionen = [
                        f for f in thermisch_rgg_optionen
                        if rohrglanzgras_erloes_pro_ha(etablierungs_art, mahd_tmp, ernteform_tmp, verwertung_tmp, f, ballen_winter_tmp) > 0
                    ]
                    beste_folge, _ = beste_option_ermitteln(
                        thermisch_rgg_optionen,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                    folge_tmp = opt_selectbox(
                        "Wie möchten Sie das Rohrglanzgras thermisch nutzen?",
                        thermisch_rgg_optionen,
                        key=f"folge_thermisch_rgg_{mahd_tmp}",
                        aktiv=ist_rgg,
                        beste_opt=beste_folge
                    )
                else:
                    folge_tmp = st.selectbox(
                        "Wie möchten Sie die Biomasse thermisch nutzen?",
                        ["Briketts", "Pellets", "Trockenmasse / Direktverbrennung", "Biogas"],
                        key="folge_thermisch"
                    )

            if verwertung_tmp in ["Samen", "Saatgut ernten", "Fasern"]:
                samen_opts = [
                    "Samen zur Weitervermehrung nutzen",
                    "Fasern als Füllfaser verwenden",
                    "Fasern als Dämmfaser verwenden"
                ]
                beste_folge, _ = (None, None)
                if ist_rohrkolben:
                    beste_folge, _ = beste_option_ermitteln(
                        samen_opts,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=opt, ballen_winter=ballen_winter_tmp
                        )
                    )
                folge_tmp = opt_selectbox(
                    "Wie möchten Sie Samen bzw. Fasern nutzen?",
                    samen_opts,
                    key="folge_samen_fasern",
                    aktiv=ist_rohrkolben,
                    beste_opt=beste_folge
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

        ohne_maschinenfrage = (
            (bewirtschaftung == "Schilf" and ernteform_tmp in ["Häckselgut", "Rundballen", "Quaderballen", "Loses Langgut"])
            or bewirtschaftung in ["Rohrkolben", "Rohrglanzgras"]
        )

        ist_tierhaltung = (
            bewirtschaftung == "Tierhaltung"
            or (bewirtschaftung == "Nasswiese" and verwertung_tmp == "Tierhaltung")
        )
        if (
            bewirtschaftung not in ["Photo-Voltaik", "Tierhaltung", "Schwarzerle"]
            and not ist_tierhaltung
            and not keine_ernte_und_kein_transport
            and not ohne_maschinenfrage
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

        hat_transport_gut = (
            not keine_ernte_und_kein_transport
            and (
                ist_rohrkolben
                or ist_rgg
                or ernteform_tmp in [
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

        hat_lager_option = (
            bewirtschaftung not in ["Photo-Voltaik", "Tierhaltung"]
            and not ist_tierhaltung
            and (ist_rohrkolben or ist_rgg or ernteform_tmp not in ["Bunde", "Loses Langgut"])
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
            tb_optionen = ["Ja", "Nein"]
            beste_tb, _ = (None, None)
            if ist_schilf:
                beste_tb, _ = beste_option_ermitteln(
                    tb_optionen,
                    lambda opt: max_netto_fuer_schilf_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                        mahd=mahd_tmp, ernteform=ernteform_tmp,
                        verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                        transport_bekannt=opt, transport_km=2.5,
                        lagerung_geplant=lagerung_geplant, lagerung_art=lagerung_art
                    )
                )
            elif ist_rohrkolben:
                beste_tb, _ = beste_option_ermitteln(
                    tb_optionen,
                    lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        mahd=mahd_tmp, ernteform=ernteform_tmp,
                        verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                        transport_bekannt=opt, transport_km=2.5,
                        lagerung_geplant=lagerung_geplant, lagerung_art=lagerung_art
                    )
                )
            elif ist_rgg:
                beste_tb, _ = beste_option_ermitteln(
                    tb_optionen,
                    lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                        verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                        transport_bekannt=opt, transport_km=2.5,
                        lagerung_geplant=lagerung_geplant, lagerung_art=lagerung_art
                    )
                )

            transport_bekannt_tmp = st.radio(
                "Wissen Sie, wie weit das Gut vom Hof zur Verwertungsstelle transportiert werden soll?",
                tb_optionen,
                index=0 if transport_bekannt == "Ja" else 1,
                format_func=lambda opt: format_radio_option(opt, beste_tb, hat_opt_highlight),
                key="moor_transport_bekannt"
            )

            if transport_bekannt_tmp == "Ja":
                distanz_optionen = [2.5, 5.0, 10.0, 20.0, 30.0, 50.0]
                beste_km, _ = (None, None)
                if ist_schilf:
                    beste_km, _ = beste_option_ermitteln(
                        distanz_optionen,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                            transport_bekannt="Ja", transport_km=opt,
                            lagerung_geplant=lagerung_geplant, lagerung_art=lagerung_art
                        )
                    )
                elif ist_rohrkolben:
                    beste_km, _ = beste_option_ermitteln(
                        distanz_optionen,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                            transport_bekannt="Ja", transport_km=opt,
                            lagerung_geplant=lagerung_geplant, lagerung_art=lagerung_art
                        )
                    )
                elif ist_rgg:
                    beste_km, _ = beste_option_ermitteln(
                        distanz_optionen,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                            transport_bekannt="Ja", transport_km=opt,
                            lagerung_geplant=lagerung_geplant, lagerung_art=lagerung_art
                        )
                    )

                km_idx = (
                    distanz_optionen.index(beste_km)
                    if (hat_opt_highlight and beste_km in distanz_optionen)
                    else (distanz_optionen.index(transport_km) if transport_km in distanz_optionen else 2)
                )
                transport_km_tmp = opt_selectbox(
                    "Transportentfernung vom Hof zur Verwertungsstelle (km):",
                    distanz_optionen,
                    key="moor_transport_km",
                    aktiv=hat_opt_highlight,
                    beste_opt=beste_km,
                    index=km_idx,
                    format_func=lambda x: f"{x:g} km",
                    beste_label=f"{beste_km:g} km" if beste_km is not None else None
                )

        if hat_lager_option:
            lg_optionen = ["Ja", "Nein"]
            beste_lg, _ = (None, None)
            if ist_schilf:
                beste_lg, _ = beste_option_ermitteln(
                    lg_optionen,
                    lambda opt: max_netto_fuer_schilf_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                        mahd=mahd_tmp, ernteform=ernteform_tmp,
                        verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                        transport_bekannt=transport_bekannt_tmp, transport_km=transport_km_tmp,
                        lagerung_geplant=opt, lagerung_art="Auf einer freien Fläche mit Abdeckung"
                    )
                )
            elif ist_rohrkolben:
                beste_lg, _ = beste_option_ermitteln(
                    lg_optionen,
                    lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        mahd=mahd_tmp, ernteform=ernteform_tmp,
                        verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                        transport_bekannt=transport_bekannt_tmp, transport_km=transport_km_tmp,
                        lagerung_geplant=opt, lagerung_art="Auf einer freien Fläche mit Abdeckung"
                    )
                )
            elif ist_rgg:
                beste_lg, _ = beste_option_ermitteln(
                    lg_optionen,
                    lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                        flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                        etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                        verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                        transport_bekannt=transport_bekannt_tmp, transport_km=transport_km_tmp,
                        lagerung_geplant=opt, lagerung_art="Auf einer freien Fläche mit Abdeckung"
                    )
                )

            lagerung_geplant_tmp = st.radio(
                "Möchten Sie die Produkte lagern?",
                lg_optionen,
                index=0 if lagerung_geplant == "Ja" else 1,
                format_func=lambda opt: format_radio_option(opt, beste_lg, hat_opt_highlight),
                key="moor_lagerung_geplant"
            )

            if lagerung_geplant_tmp == "Ja":
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

                beste_la, _ = (None, None)
                if ist_schilf:
                    beste_la, _ = beste_option_ermitteln(
                        lager_optionen,
                        lambda opt: max_netto_fuer_schilf_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, etab_detail=etablierungs_detail,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                            transport_bekannt=transport_bekannt_tmp, transport_km=transport_km_tmp,
                            lagerung_geplant="Ja", lagerung_art=opt
                        )
                    )
                elif ist_rohrkolben:
                    beste_la, _ = beste_option_ermitteln(
                        lager_optionen,
                        lambda opt: max_netto_fuer_rohrkolben_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                            transport_bekannt=transport_bekannt_tmp, transport_km=transport_km_tmp,
                            lagerung_geplant="Ja", lagerung_art=opt
                        )
                    )
                elif ist_rgg:
                    beste_la, _ = beste_option_ermitteln(
                        lager_optionen,
                        lambda opt: max_netto_fuer_rohrglanzgras_teilbaum(
                            flaechen_groesse, bisherige_ertraege_pro_ha, kaufkosten_gesamt,
                            etab_art=etablierungs_art, mahd=mahd_tmp, ernteform=ernteform_tmp,
                            verwertung=verwertung_tmp, folge=folge_tmp, ballen_winter=ballen_winter_tmp,
                            transport_bekannt=transport_bekannt_tmp, transport_km=transport_km_tmp,
                            lagerung_geplant="Ja", lagerung_art=opt
                        )
                    )

                la_idx = (
                    lager_optionen.index(beste_la)
                    if (hat_opt_highlight and beste_la in lager_optionen)
                    else (lager_optionen.index(lagerung_art) if lagerung_art in lager_optionen else 0)
                )
                lagerung_art_tmp = opt_selectbox(
                    "Wie sollen die Produkte gelagert werden?",
                    lager_optionen,
                    key="moor_lagerung_art",
                    aktiv=hat_opt_highlight,
                    beste_opt=beste_la,
                    index=la_idx
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

    kauf_annuitaet_jahr = kaufkosten_gesamt / 10.0

    if bewirtschaftung == "Rohrglanzgras":
        rgg_daten = berechne_rohrglanzgras_kosten_und_erloes(
            flaechen_groesse=flaechen_groesse,
            bisherige_ertraege_pro_ha=bisherige_ertraege_pro_ha,
            etablierungs_art=etablierungs_art,
            mahd_zeitpunkt=mahd_zeitpunkt,
            ernteform_biomasse=ernteform_biomasse,
            verwertung=verwertung,
            folge_auswahl=folge_auswahl,
            ballen_winter_option=ballen_winter_option,
            transport_bekannt=transport_bekannt,
            transport_km=transport_km,
            lagerung_geplant=lagerung_geplant,
            lagerung_art=lagerung_art,
            kaufkosten_gesamt=kaufkosten_gesamt
        )
        kosten_bauer_jahr = (
            flaechen_groesse * (
                rgg_daten["etablierung"]
                + rgg_daten["laufend"]
                + rgg_daten["ernte"]
                + rgg_daten["endprodukt"]
                + rgg_daten["transport"]
                + rgg_daten["lager"]
            )
            + kauf_annuitaet_jahr
        )
        kosten_volk_jahr = (
            flaechen_groesse * 850.0
            + flaechen_groesse * (
                rgg_daten["etablierung"]
                + rgg_daten["laufend"]
                + rgg_daten["endprodukt"]
            )
            + kauf_annuitaet_jahr
        )
        erloes_moor = flaechen_groesse * (bisherige_ertraege_pro_ha + rgg_daten["erloes_ha"])
        netto_ertrag_moor = erloes_moor - kosten_bauer_jahr

    elif bewirtschaftung == "Rohrkolben":
        rk_daten = berechne_rohrkolben_kosten_und_erloes(
            flaechen_groesse=flaechen_groesse,
            bisherige_ertraege_pro_ha=bisherige_ertraege_pro_ha,
            mahd_zeitpunkt=mahd_zeitpunkt,
            ernteform_biomasse=ernteform_biomasse,
            verwertung=verwertung,
            folge_auswahl=folge_auswahl,
            ballen_winter_option=ballen_winter_option,
            transport_bekannt=transport_bekannt,
            transport_km=transport_km,
            lagerung_geplant=lagerung_geplant,
            lagerung_art=lagerung_art,
            kaufkosten_gesamt=kaufkosten_gesamt
        )
        kosten_bauer_jahr = (
            flaechen_groesse * (
                rk_daten["etablierung"]
                + rk_daten["laufend"]
                + rk_daten["ernte"]
                + rk_daten["endprodukt"]
                + rk_daten["transport"]
                + rk_daten["lager"]
            )
            + kauf_annuitaet_jahr
        )
        kosten_volk_jahr = (
            flaechen_groesse * 850.0
            + flaechen_groesse * (
                rk_daten["etablierung"]
                + rk_daten["laufend"]
                + rk_daten["endprodukt"]
            )
            + kauf_annuitaet_jahr
        )
        erloes_moor = flaechen_groesse * (bisherige_ertraege_pro_ha + rk_daten["erloes_ha"])
        netto_ertrag_moor = erloes_moor - kosten_bauer_jahr

    else:
        if bewirtschaftung == "Schilf" and ernteform_biomasse == "Loses Langgut":
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

        sonderkosten_schilf_pro_ha_jahr = 0.0
        entfaellt_ernte_und_transport = False
        if bewirtschaftung == "Schilf" and verwertung == "Thermische Verwertung" and folge_auswahl == "Ethanol":
            sonderkosten_schilf_pro_ha_jahr = 2387.00
            entfaellt_ernte_und_transport = True
        elif bewirtschaftung == "Schilf" and verwertung == "Energetische Verwertung" and folge_auswahl == "Biogasanlage":
            sonderkosten_schilf_pro_ha_jahr = 1900.00
            entfaellt_ernte_und_transport = True

        if entfaellt_ernte_und_transport or (bewirtschaftung == "Schilf" and ernteform_biomasse == "Loses Langgut"):
            erntekosten_pro_ha_jahr = 0.0
        elif bewirtschaftung == "Schilf":
            if ernteform_biomasse in ["Rundballen", "Quaderballen", "Häckselgut"]:
                erntekosten_pro_ha_jahr = 410.00
            elif ernteform_biomasse == "Bunde":
                erntekosten_pro_ha_jahr = 640.00
            elif ernteform_biomasse == "Pelletierte Form (mobile Pelletierungsmaschine)":
                erntekosten_pro_ha_jahr = 2719.43 if mahd_zeitpunkt == "Sommermahd" else 1759.10
            else:
                erntekosten_pro_ha_jahr = 350.00
        else:
            if ernteform_biomasse == "Pelletierte Form (mobile Pelletierungsmaschine)":
                erntekosten_pro_ha_jahr = 2719.43 if mahd_zeitpunkt == "Sommermahd" else 1759.10
            else:
                erntekosten_pro_ha_jahr = {
                    None: 120.0,
                    "Eigene Maschinen vorhanden, die auf der Fläche fahren können": 150.0,
                    "Zugang zu einem Maschinenring": 220.0,
                    "Vorhandene Maschinen können angepasst werden": 260.0,
                    "Spezialtechnik kaufen": 420.0,
                    "Spezialfirmen beauftragen": 480.0
                }[erntetechnik]

        if ernteform_biomasse in ["Rundballen", "Quaderballen"] and mahd_zeitpunkt == "Wintermahd":
            erntekosten_pro_ha_jahr += {
                "Pellets": 569.97,
                "Briketts": 588.00,
                "Pressen": 392.00
            }.get(ballen_winter_option, 0.0)

        ist_mobile_pellet_oder_brikett = ernteform_biomasse in [
            "Pelletierte Form (mobile Pelletierungsmaschine)",
            "Brikettierte Form (mobile Brikettierungsmaschine)"
        ]
        endprodukt_kosten_pro_ha_jahr = 0.0
        if not ist_mobile_pellet_oder_brikett:
            if (
                folge_auswahl in ["Pellets", "Pellets und Briketts", "Stationäre Pelletieranlage", "Brennstoff-Pellets / Briketts"]
                or ballen_winter_option == "Pellets"
            ):
                endprodukt_kosten_pro_ha_jahr = 1000.00
            elif folge_auswahl in ["Briketts"] or ballen_winter_option == "Briketts":
                endprodukt_kosten_pro_ha_jahr = 800.00
            elif (
                folge_auswahl in ["Formteile", "Plattenwerkstoffe", "Faserplatten und Biokunststoffe"]
                or verwertung in ["Werkstoffe", "Faserplatten & Dämmstoffe"]
            ):
                endprodukt_kosten_pro_ha_jahr = 920.00
            elif folge_auswahl == "Biokunststoffe" or verwertung == "Biokunststoffe":
                endprodukt_kosten_pro_ha_jahr = 1280.00
            elif (
                folge_auswahl in ["Einblasdämmung", "Dämmmatten", "Dämmstoffe (Einblasdämmung / Dämmmatten)"]
                or verwertung == "Dämm- und Baustoffe"
            ):
                endprodukt_kosten_pro_ha_jahr = 11200.00

        transport_kosten_pro_ha_jahr = 0.0
        if not entfaellt_ernte_und_transport:
            ist_pellet_brikett_produkt = (
                ist_mobile_pellet_oder_brikett
                or folge_auswahl in [
                    "Pellets",
                    "Briketts",
                    "Pellets und Briketts",
                    "Stationäre Pelletieranlage",
                    "Brennstoff-Pellets / Briketts"
                ]
                or ballen_winter_option in ["Pellets", "Briketts"]
            )

            ist_dachschilf_bunde_langgut = (
                verwertung == "Dachreed"
                or folge_auswahl == "Sortierung zu Dachreetbunden"
                or ernteform_biomasse in ["Bunde", "Loses Langgut"]
            )

            if ernteform_biomasse == "Häckselgut":
                if mahd_zeitpunkt == "Sommermahd":
                    if transport_bekannt == "Ja":
                        transport_kosten_pro_ha_jahr = {
                            2.5: 137.87,
                            5.0: 165.14,
                            10.0: 221.19,
                            20.0: 331.79,
                            30.0: 443.90,
                            50.0: 666.60
                        }.get(transport_km, 387.85)
                    else:
                        transport_kosten_pro_ha_jahr = 387.85
                else:
                    if transport_bekannt == "Ja":
                        transport_kosten_pro_ha_jahr = {
                            2.5: 89.18,
                            5.0: 106.82,
                            10.0: 143.08,
                            20.0: 214.62,
                            30.0: 287.14,
                            50.0: 431.20
                        }.get(transport_km, 250.88)
                    else:
                        transport_kosten_pro_ha_jahr = 250.88

            elif ist_dachschilf_bunde_langgut:
                if mahd_zeitpunkt == "Sommermahd":
                    if flaechen_groesse >= 2.5:
                        if transport_bekannt == "Ja":
                            transport_kosten_pro_ha_jahr = {
                                2.5: 89.39,
                                5.0: 99.99,
                                10.0: 122.72,
                                20.0: 166.65,
                                30.0: 212.10,
                                50.0: 299.997
                            }.get(transport_km, 189.76)
                        else:
                            transport_kosten_pro_ha_jahr = 189.76
                    else:
                        if transport_bekannt == "Ja":
                            transport_kosten_pro_ha_jahr = {
                                2.5: 212.10,
                                5.0: 236.34,
                                10.0: 284.82,
                                20.0: 383.30,
                                30.0: 480.26,
                                50.0: 677.21
                            }.get(transport_km, 431.78)
                        else:
                            transport_kosten_pro_ha_jahr = 431.78
                else:
                    if flaechen_groesse >= 2.5:
                        if transport_bekannt == "Ja":
                            transport_kosten_pro_ha_jahr = {
                                2.5: 57.82,
                                5.0: 64.68,
                                10.0: 79.38,
                                20.0: 107.80,
                                30.0: 137.20,
                                50.0: 194.04
                            }.get(transport_km, 122.50)
                        else:
                            transport_kosten_pro_ha_jahr = 122.50
                    else:
                        if transport_bekannt == "Ja":
                            transport_kosten_pro_ha_jahr = {
                                2.5: 137.20,
                                5.0: 152.88,
                                10.0: 184.24,
                                20.0: 247.94,
                                30.0: 310.66,
                                50.0: 438.06
                            }.get(transport_km, 279.30)
                        else:
                            transport_kosten_pro_ha_jahr = 279.30

            elif ist_pellet_brikett_produkt and mahd_zeitpunkt == "Wintermahd":
                if transport_bekannt == "Ja":
                    transport_kosten_pro_ha_jahr = {
                        2.5: 22.54,
                        5.0: 26.46,
                        10.0: 33.32,
                        20.0: 47.04,
                        30.0: 59.78,
                        50.0: 87.22
                    }.get(transport_km, 53.41)
                else:
                    transport_kosten_pro_ha_jahr = 53.41

            elif ernteform_biomasse in ["Rundballen", "Quaderballen"]:
                if mahd_zeitpunkt == "Sommermahd":
                    if transport_bekannt == "Ja":
                        transport_kosten_pro_ha_jahr = {
                            2.5: 86.36,
                            5.0: 98.48,
                            10.0: 119.69,
                            20.0: 163.62,
                            30.0: 207.56,
                            50.0: 296.94
                        }.get(transport_km, 185.59)
                    else:
                        transport_kosten_pro_ha_jahr = 185.59
                else:
                    if transport_bekannt == "Ja":
                        transport_kosten_pro_ha_jahr = {
                            2.5: 55.86,
                            5.0: 63.70,
                            10.0: 77.42,
                            20.0: 105.84,
                            30.0: 134.26,
                            50.0: 192.08
                        }.get(transport_km, 120.05)
                    else:
                        transport_kosten_pro_ha_jahr = 120.05

            elif transport_bekannt == "Ja":
                transport_kosten_pro_ha_jahr = transport_km * 3.5

        lager_kosten_pro_ha_jahr = 0.0
        if lagerung_geplant == "Ja" and ernteform_biomasse not in ["Bunde", "Loses Langgut"]:
            ist_pellet_brikett_lager = (
                ist_mobile_pellet_oder_brikett
                or folge_auswahl in [
                    "Pellets",
                    "Briketts",
                    "Pellets und Briketts",
                    "Stationäre Pelletieranlage",
                    "Brennstoff-Pellets / Briketts"
                ]
                or ballen_winter_option in ["Pellets", "Briketts"]
            )

            if ist_pellet_brikett_lager:
                if lagerung_art == "In einer Halle":
                    lager_kosten_pro_ha_jahr = 178.01 if mahd_zeitpunkt == "Sommermahd" else 115.15
            elif ernteform_biomasse == "Häckselgut":
                if mahd_zeitpunkt == "Sommermahd":
                    lager_kosten_pro_ha_jahr = {
                        "In einer Halle": 227.25,
                        "Auf einer freien Fläche mit Abdeckung": 86.36
                    }.get(lagerung_art, 0.0)
                else:
                    lager_kosten_pro_ha_jahr = {
                        "In einer Halle": 147.00,
                        "Auf einer freien Fläche mit Abdeckung": 55.86
                    }.get(lagerung_art, 0.0)
            elif ernteform_biomasse in ["Rundballen", "Quaderballen"]:
                if mahd_zeitpunkt == "Sommermahd":
                    lager_kosten_pro_ha_jahr = {
                        "In einer Halle": 386.33,
                        "In einem Altgebäude": 166.65,
                        "Auf einer freien Fläche mit Abdeckung": 80.30
                    }.get(lagerung_art, 0.0)
                else:
                    lager_kosten_pro_ha_jahr = {
                        "In einer Halle": 249.90,
                        "In einem Altgebäude": 107.80,
                        "Auf einer freien Fläche mit Abdeckung": 51.94
                    }.get(lagerung_art, 0.0)
            else:
                lager_kosten_pro_ha_jahr = {
                    "In einer Halle": 120.0,
                    "In einem Altgebäude": 65.0,
                    "Auf einer freien Fläche mit Abdeckung": 35.0
                }.get(lagerung_art, 0.0)

        kosten_bauer_jahr = (
            flaechen_groesse * (
                etablierung_kosten_pro_ha_jahr
                + laufende_kosten_pro_ha_jahr
                + sonderkosten_schilf_pro_ha_jahr
                + erntekosten_pro_ha_jahr
                + endprodukt_kosten_pro_ha_jahr
                + transport_kosten_pro_ha_jahr
                + lager_kosten_pro_ha_jahr
            )
            + kauf_annuitaet_jahr
        )

        kosten_volk_jahr = (
            flaechen_groesse * 850.0
            + flaechen_groesse * (
                etablierung_kosten_pro_ha_jahr
                + laufende_kosten_pro_ha_jahr
                + sonderkosten_schilf_pro_ha_jahr
                + endprodukt_kosten_pro_ha_jahr
            )
            + kauf_annuitaet_jahr
        )

        nutzung_erloes_pro_ha_jahr = {
            "Rohrglanzgras": 950.0,
            "Schwarzerle": 1100.0,
            "Nasswiese": 750.0,
            "Schilf": 1050.0,
            "Rohrkolben": 1150.0,
            "Torfmoos": 1400.0,
            "Tierhaltung": 900.0,
            "Photo-Voltaik": 2200.0,
            "Seggen": 700.0
        }.get(bewirtschaftung, 850.0)

        if bewirtschaftung == "Schilf":
            ist_sommer = (mahd_zeitpunkt == "Sommermahd")

            if verwertung == "Dachreed" or folge_auswahl == "Sortierung zu Dachreetbunden":
                nutzung_erloes_pro_ha_jahr = 4704.00
            elif verwertung == "Dämmplatten" or folge_auswahl in ["Dämmplatten", "Dämmplatten & Leichtbaumatten"]:
                nutzung_erloes_pro_ha_jahr = 4410.00
            elif folge_auswahl in ["Einblasdämmung", "Dämmmatten"]:
                nutzung_erloes_pro_ha_jahr = 13600.00
            elif folge_auswahl == "Putzträger":
                nutzung_erloes_pro_ha_jahr = 1750.00
            elif folge_auswahl == "Zuschlagstoff für Lehm- und Kalkputze":
                nutzung_erloes_pro_ha_jahr = 1400.00
            elif folge_auswahl == "Papier- und Kartonherstellung" or verwertung == "Papier herstellen":
                nutzung_erloes_pro_ha_jahr = 1127.00
            elif folge_auswahl in ["Plattenwerkstoffe", "Faserplatten und Biokunststoffe"] or verwertung == "Faserplatten & Dämmstoffe":
                nutzung_erloes_pro_ha_jahr = 632.50 if ist_sommer else 2400.00
            elif folge_auswahl == "Formteile":
                nutzung_erloes_pro_ha_jahr = 715.00 if ist_sommer else 1440.00
            elif (
                ist_mobile_pellet_oder_brikett
                or folge_auswahl in [
                    "Pellets",
                    "Briketts",
                    "Pellets und Briketts",
                    "Stationäre Pelletieranlage",
                    "Brennstoff-Pellets / Briketts"
                ]
                or ballen_winter_option in ["Pellets", "Briketts"]
            ):
                nutzung_erloes_pro_ha_jahr = 2100.00
            elif verwertung == "Thermische Verwertung" and folge_auswahl == "Verbrennung":
                if ernteform_biomasse == "Häckselgut":
                    nutzung_erloes_pro_ha_jahr = 1430.80
                elif ernteform_biomasse in ["Rundballen", "Quaderballen"]:
                    nutzung_erloes_pro_ha_jahr = (
                        950.60 if etablierungs_art == "Erstetablierung" else 676.20
                    )
            elif folge_auswahl == "Heu":
                nutzung_erloes_pro_ha_jahr = 211.50 if ist_sommer else 395.25
            elif folge_auswahl in ["Biogasproduktion", "Biogassubstrat", "Biogasanlage", "Biogas"]:
                nutzung_erloes_pro_ha_jahr = 100.00
            elif verwertung in ["Kultursubstrate", "Torfersatz in Kultursubstraten"]:
                nutzung_erloes_pro_ha_jahr = 375.00 if ist_sommer else 1200.00
            elif folge_auswahl == "Torf- und Kompostersatz":
                nutzung_erloes_pro_ha_jahr = 275.00 if ist_sommer else 480.00
            elif folge_auswahl == "Mulchmaterial" or verwertung == "Mulch-Pellets":
                nutzung_erloes_pro_ha_jahr = 225.00 if ist_sommer else 720.00
            elif verwertung in ["Einstreu", "Tiereinstreu"] or folge_auswahl in ["Einstreu", "Tiereinstreu"]:
                nutzung_erloes_pro_ha_jahr = 720.00
            elif folge_auswahl in ["Raufutter", "Silage"] or verwertung == "Raufutterersatz":
                nutzung_erloes_pro_ha_jahr = 500.00
            elif folge_auswahl == "Dünger" or verwertung == "Organischer Dünger":
                nutzung_erloes_pro_ha_jahr = 300.00 if ist_sommer else 160.00

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
