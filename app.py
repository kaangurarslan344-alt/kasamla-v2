import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kasamla", page_icon="📊", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #ffffff; }
    .kasamla-header { text-align: center; color: #ff9f43; font-size: 28px; font-weight: bold; margin-bottom: 2px; }
    .date-range { text-align: center; color: #8a99ad; font-size: 16px; margin-bottom: 20px; }
    .main-card { background-color: #161b2b; border-radius: 16px; padding: 20px; margin-bottom: 20px; text-align: center; border: 1px solid #232a45; }
    .sub-text { color: #8a99ad; font-size: 14px; margin-bottom: 5px; }
    .nakit-akis-value { font-size: 36px; font-weight: bold; color: #ff5252; margin: 10px 0; }
    .nakit-akis-value-pos { font-size: 36px; font-weight: bold; color: #2ecc71; margin: 10px 0; }
    .row-box { background-color: #161b2b; border-radius: 16px; padding: 20px; margin-bottom: 20px; border: 1px solid #232a45; }
    .card-title { font-size: 18px; font-weight: bold; color: #ffffff; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

if "islemler" not in st.session_state:
    st.session_state.islemler = pd.DataFrame(columns=["Tarih", "Tür", "Kategori", "Miktar"])

df = st.session_state.islemler

# Üst Başlık
st.markdown('<div class="kasamla-header">Kasamla</div>', unsafe_allow_html=True)
st.markdown('<div class="date-range">‹ &nbsp; Bu Ay &nbsp; ›</div>', unsafe_allow_html=True)

toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum() if not df.empty else 0.0
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum() if not df.empty else 0.0
nakit_akisi = toplam_gelir - toplam_gider

# Ana Kart
akis_class = "nakit-akis-value" if nakit_akisi <= 0 else "nakit-akis-value-pos"
st.markdown(f"""
    <div class="main-card">
        <div class="sub-text">Bu Ayki Nakit Akışı</div>
        <div class="{akis_class}">₺ {nakit_akisi:.0f}</div>
        <table style="width:100%; border-top: 1px solid #232a45; padding-top:10px;">
            <tr>
                <td style="text-align:center;">Gelir: <b style="color:#2ecc71;">₺ {toplam_gelir:.0f}</b></td>
                <td style="text-align:center;">Gider: <b style="color:#ff5252;">₺ {toplam_gider:.0f}</b></td>
            </tr>
        </table>
    </div>
""", unsafe_allow_html=True)

# Harcama Dağılımı ve Liste
st.markdown('<div class="row-box">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Harcama Dağılımı</div>', unsafe_allow_html=True)

if not df.empty and toplam_gider > 0:
    gider_df = df[df["Tür"] == "Gider"].groupby("Kategori")["Miktar"].sum().reset_index()
    gider_df["Yüzde"] = (gider_df["Miktar"] / toplam_gider * 100).round(1)
    
    # Donut Grafik
    donut = alt.Chart(gider_df).mark_arc(innerRadius=65, outerRadius=95).encode(
        theta=alt.Theta("Miktar", type="quantitative"),
        color=alt.Color("Kategori", type="nominal", scale=alt.Scale(scheme='category20')),
        tooltip=['Kategori', 'Miktar', 'Yüzde']
    ).properties(height=240)
    st.altair_chart(donut, use_container_width=True)
    
    # YENİ EKLENEN LİSTE: Kategori | Miktar | %
    st.markdown("---")
    for _, row in gider_df.iterrows():
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span>{row['Kategori']}</span>
                <span><b>₺{row['Miktar']:.0f}</b> (<span style="color:#ff9f43;">%{row['Yüzde']}</span>)</span>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Henüz harcama yok.")
st.markdown('</div>', unsafe_allow_html=True)

# İşlem Ekle
with st.markdown('<div class="row-box">', unsafe_allow_html=True):
    st.markdown('<div class="card-title">➕ Yeni İşlem</div>', unsafe_allow_html=True)
    islem_turu = st.radio("Tür:", ["🔴 Gider (-)", "🟢 Gelir (+)"], horizontal=True)
    with st.form("ekle", clear_on_submit=True):
        c1, c2 = st.columns(2)
        kat = c1.text_input("Kategori")
        mik = c2.number_input("Miktar", min_value=0.0)
        if st.form_submit_button("Ekle"):
            yeni = pd.DataFrame([{"Tarih": datetime.now().strftime("%Y-%m-%d"), "Tür": "Gelir" if "Gelir" in islem_turu else "Gider", "Kategori": kat, "Miktar": mik}])
            st.session_state.islemler = pd.concat([st.session_state.islemler, yeni], ignore_index=True)
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
