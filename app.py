import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Kasamla Portföy", page_icon="💰", layout="centered")

# Karanlık Tema
st.markdown("""
    <style>
    .main { background-color: #111625; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #ff5252 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Kasamla / Harcama Portföyü")

# Veritabanı
if "harcamalar" not in st.session_state:
    st.session_state.harcamalar = pd.DataFrame(columns=["Tarih", "Harcama Adı", "Miktar (€)"])

AYLIK_BUTCE = 500.0

# Harcama Ekleme
st.subheader("➕ Hızlı Harcama Ekle")
with st.form("harcama_formu", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        harcama_adi = st.text_input("Harcama Adı", placeholder="Örn: Monster").strip().capitalize()
    with col2:
        miktar = st.number_input("Miktar (€)", min_value=0.0, step=0.50, format="%.2f")
    
    ekle_btn = st.form_submit_button("Portföye Ekle")
    
    if ekle_btn and harcama_adi and miktar > 0:
        yeni_veri = pd.DataFrame([{"Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Harcama Adı": harcama_adi, "Miktar (€)": miktar}])
        st.session_state.harcamalar = pd.concat([st.session_state.harcamalar, yeni_veri], ignore_index=True)
        st.success(f"✅ {harcama_adi} eklendi!")

# Dashboard Özeti
df = st.session_state.harcamalar
st.write("---")
st.subheader("📊 Bu Ayki Nakit Akışı")

toplam_gider = df["Miktar (€)"].sum() if not df.empty else 0.0
kalan_butce = AYLIK_BUTCE - toplam_gider

c1, c2 = st.columns(2)
c1.metric(label="Toplam Harcanan", value=f"-€{toplam_gider:.2f}")
c2.metric(label="Kalan Bütçe", value=f"€{kalan_butce:.2f}", delta_color="normal")

# Kendi İçindeki Çubuk Grafiği (Sorunsuz Çalışır)
if not df.empty:
    st.write("---")
    st.subheader("🎯 Harcama Dağılımı")
    
    grup_df = df.groupby("Harcama Adı")["Miktar (€)"].sum()
    st.bar_chart(grup_df)
    
    st.subheader("📋 Harcama Geçmişi")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
