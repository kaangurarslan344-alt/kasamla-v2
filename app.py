import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Kasamla Portföy", page_icon="💰", layout="centered")

# Karanlık Tema ve Renk Ayarları
st.markdown("""
    <style>
    .main { background-color: #111625; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #ff5252 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Kasamla / Harcama Portföyü")

# Veritabanı (Session State)
if "harcamalar" not in st.session_state:
    st.session_state.harcamalar = pd.DataFrame(columns=["Tarih", "Harcama Adı", "Miktar (€)"])

AYLIK_BUTCE = 500.0

# Harcama Ekleme Formu
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

# Dashboard
df = st.session_state.harcamalar
st.write("---")
st.subheader("📊 Bu Ayki Nakit Akışı")

toplam_gider = df["Miktar (€)"].sum() if not df.empty else 0.0
kalan_butce = AYLIK_BUTCE - toplam_gider

c1, c2 = st.columns(2)
c1.metric(label="Toplam Harcanan", value=f"-€{toplam_gider:.2f}")
c2.metric(label="Kalan Bütçe", value=f"€{kalan_butce:.2f}", delta_color="normal")

# Grafik ve Geçmiş
if not df.empty:
    st.write("---")
    st.subheader("🎯 Harcama Dağılımı")
    
    grup_df = df.groupby("Harcama Adı")["Miktar (€)"].sum().reset_index()
    fig = px.pie(grup_df, values='Miktar (€)', names='Harcama Adı', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Harcama Geçmişi")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
