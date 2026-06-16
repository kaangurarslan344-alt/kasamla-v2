import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

st.set_page_config(page_title="Kasamla Premium", page_icon="📊", layout="centered")

# Tasarım CSS (Koyu Tema)
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #ffffff; }
    .row-box { background-color: #161b2b; border-radius: 16px; padding: 20px; margin-bottom: 20px; border: 1px solid #232a45; }
    .card-title { font-size: 18px; font-weight: bold; color: #ffffff; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# Veritabanı (Sessiyonda tutulur)
if "islemler" not in st.session_state:
    st.session_state.islemler = pd.DataFrame(columns=["Tarih", "Tür", "Kategori", "Miktar"])

# --- AY/YIL SEÇİCİ ---
st.markdown('<div style="text-align:center; font-size:24px; font-weight:bold; color:#ff9f43;">Kasamla</div>', unsafe_allow_html=True)

# Mevcut ay ve geçmiş 12 ayı seçenek olarak sun
aylar = [datetime(2026, i, 1).strftime("%Y-%m") for i in range(1, 13)]
secili_ay = st.selectbox("Dönem Seçin (Ay/Yıl):", aylar, index=datetime.now().month-1)

df = st.session_state.islemler
# Seçili aya göre filtrele
df_ay = df[df['Tarih'] == secili_ay] if not df.empty else df

# Hesaplamalar
gelir = df_ay[df_ay["Tür"] == "Gelir"]["Miktar"].sum()
gider = df_ay[df_ay["Tür"] == "Gider"]["Miktar"].sum()

# --- ÖZET KARTLARI ---
c1, c2, c3 = st.columns(3)
c1.metric("Gelir", f"₺{gelir:.0f}")
c2.metric("Gider", f"₺{gider:.0f}")
c3.metric("Net", f"₺{gelir-gider:.0f}")

# --- HARCAMA DAĞILIMI ---
st.markdown('<div class="row-box">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Harcama Dağılımı</div>', unsafe_allow_html=True)

if gider > 0:
    gider_df = df_ay[df_ay["Tür"] == "Gider"].groupby("Kategori")["Miktar"].sum().reset_index()
    gider_df["Yüzde"] = (gider_df["Miktar"] / gider * 100).round(1).astype(str) + "%"
    
    # Donut Grafik
    donut = alt.Chart(gider_df).mark_arc(innerRadius=60).encode(
        theta=alt.Theta("Miktar", type="quantitative"),
        color=alt.Color("Kategori", type="nominal"),
        tooltip=['Kategori', 'Miktar', 'Yüzde']
    ).properties(height=200)
    st.altair_chart(donut, use_container_width=True)
    
    st.table(gider_df[["Kategori", "Miktar", "Yüzde"]].sort_values(by="Miktar", ascending=False))
else:
    st.info("Bu dönemde henüz harcama yok.")
st.markdown('</div>', unsafe_allow_html=True)

# --- İŞLEM EKLEME ---
with st.expander("➕ Yeni İşlem Ekle"):
    with st.form("ekle", clear_on_submit=True):
        tur = st.radio("Tür:", ["Gider", "Gelir"], horizontal=True)
        kat = st.text_input("Kategori")
        mik = st.number_input("Miktar", min_value=0.0)
        if st.form_submit_button("Kaydet"):
            yeni = pd.DataFrame([{"Tarih": secili_ay, "Tür": tur, "Kategori": kat, "Miktar": mik}])
            st.session_state.islemler = pd.concat([st.session_state.islemler, yeni], ignore_index=True)
            st.rerun()

# --- İŞLEM GEÇMİŞİ ---
st.markdown('<div class="row-box">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📋 İşlem Geçmişi</div>', unsafe_allow_html=True)
st.dataframe(df_ay, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
