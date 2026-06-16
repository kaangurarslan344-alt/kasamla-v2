import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Kasamla Premium", page_icon="💸", layout="centered")

# Karanlık Mod (Dark Mode) Zorlaması ve Arayüz Ayarları
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

st.title("💸 Kasamla Portföy")

# Veritabanı oluştur
if "islemler" not in st.session_state:
    st.session_state.islemler = pd.DataFrame(columns=["Tarih", "Tür", "Kategori", "Miktar (€)"])

# 📱 UYGULAMA SEKMELERİ (Tasarımı Şıklaştıran Kısım)
tab_ana, tab_ekle, tab_gecmis = st.tabs(["📊 Ana Panel", "➕ İşlem Ekle", "📋 Tüm Geçmiş"])

df = st.session_state.islemler

# --- SEKME 2: GELİR VE GİDER EKLEME EKRANI ---
with tab_ekle:
    st.subheader("Gelir veya Gider Ekle")
    
    # + Gelir ve - Gider Seçeneği (Uygulama Hissiyatı)
    islem_turu = st.radio("İşlem Türünü Seçin:", ["🔴 Gider (-)", "🟢 Gelir (+)"], horizontal=True)
    
    with st.form("islem_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            kategori = st.text_input("Nereye / Nereden?", placeholder="Örn: Monster, Maaş, Kira").strip().capitalize()
        with col2:
            # Euro bazlı giriş
            miktar = st.number_input("Miktar (€)", min_value=0.0, step=1.0, format="%.2f")
        
        kaydet = st.form_submit_button("Portföye İşle")
        
        if kaydet and kategori and miktar > 0:
            tur = "Gelir" if "Gelir" in islem_turu else "Gider"
            yeni_islem = pd.DataFrame([{"Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Tür": tur, "Kategori": kategori, "Miktar (€)": miktar}])
            st.session_state.islemler = pd.concat([st.session_state.islemler, yeni_islem], ignore_index=True)
            st.success(f"✅ {kategori} ({tur}) başarıyla eklendi!")

# --- SEKME 1: ANA DASHBOARD (Özet ve Grafikler) ---
with tab_ana:
    # Arka planda net bakiye hesaplamaları
    toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar (€)"].sum() if not df.empty else 0.0
    toplam_gider = df[df["Tür"] == "Gider"]["Miktar (€)"].sum() if not df.empty else 0.0
    net_bakiye = toplam_gelir - toplam_gider

    # Şık Metrik Kartları
    st.write("### 💳 Cüzdan Özeti")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Bakiye (Net)", f"€{net_bakiye:.2f}")
    c2.metric("Toplam Gelir (+)", f"€{toplam_gelir:.2f}")
    c3.metric("Toplam Gider (-)", f"€{toplam_gider:.2f}")

    st.write("---")
    st.subheader("🎯 Gider Dağılımı (Portföy)")
    
    if not df.empty and toplam_gider > 0:
        # Sadece harcamaları grafikleştirir (Maaşı portföy dağılımına katmaz)
        gider_df = df[df["Tür"] == "Gider"]
        grup_df = gider_df.groupby("Kategori")["Miktar (€)"].sum().reset_index()
        
        # Harcamaları şık bir kırmızı bar grafiğiyle göster
        st.bar_chart(grup_df.set_index("Kategori"), color="#ff5252")
    else:
        st.info("Henüz bir harcama (gider) verisi yok. İşlem Ekle kısm
