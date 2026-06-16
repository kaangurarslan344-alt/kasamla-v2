import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

# 1. Sayfa Ayarları ve Birebir Görsel Teması (Dark Mode)
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

# 2. Veritabanı Altyapısı (Tüm Hazır Veriler Temizlendi - Sıfır Liste)
if "islemler" not in st.session_state:
    st.session_state.islemler = pd.DataFrame(columns=["Tarih", "Tür", "Kategori", "Miktar"])

df = st.session_state.islemler

# --- ÜST BAŞLIK VE TARİH ALANI ---
st.markdown('<div class="kasamla-header">Kasamla</div>', unsafe_allow_html=True)
st.markdown('<div class="date-range">‹ &nbsp; Bu Ay &nbsp; ›</div>', unsafe_allow_html=True)

# Hesaplamalar
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum() if not df.empty else 0.0
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum() if not df.empty else 0.0
nakit_akisi = toplam_gelir - toplam_gider
toplam_varlik = nakit_akisi 

# --- 1. ANA KART: NAKİT AKIŞI ---
akis_class = "nakit-akis-value" if nakit_akisi <= 0 else "nakit-akis-value-pos"
akis_sign = "" if nakit_akisi > 0 else "-"
st.markdown(f"""
    <div class="main-card">
        <div class="sub-text" style="color: #ffb142;">Toplam Varlık: ₺ {toplam_varlik:.0f}</div>
        <div class="sub-text">Bu Ayki Nakit Akışı</div>
        <div class="{akis_class}">{akis_sign}₺ {abs(nakit_akisi):.0f}</div>
        <table style="width:100%; margin-top:15px; border-top: 1px solid #232a45; padding-top:10px;">
            <tr>
                <td style="width:50%; text-align:center;">
                    <div class="sub-text">⬇️ Bu Ay Gelir</div>
                    <div style="color: #2ecc71; font-weight:bold; font-size:18px;">₺ {toplam_gelir:.0f}</div>
                </td>
                <td style="width:50%; text-align:center; border-left: 1px solid #232a45;">
                    <div class="sub-text">⬆️ Bu Ay Gider</div>
                    <div style="color: #ff5252; font-weight:bold; font-size:18px;">₺ {toplam_gider:.0f}</div>
                </td>
            </tr>
        </table>
    </div>
""", unsafe_allow_html=True)

# --- 2. KART: HARCAMA DAĞILIMI (DONUT CHART) ---
st.markdown('<div class="row-box">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Harcama Dağılımı</div>', unsafe_allow_html=True)

if not df.empty and toplam_gider > 0:
    gider_df = df[df["Tür"] == "Gider"]
    grup_df = gider_df.groupby("Kategori")["Miktar"].sum().reset_index()
    grup_df["Yüzde"] = (grup_df["Miktar"] / toplam_gider * 100).round(0).astype(str) + "%"
    
    # Renkler artık sabit değil, girdiğin kategoriye göre otomatik atanacak
    donut = alt.Chart(grup_df).mark_arc(innerRadius=65, outerRadius=95).encode(
        theta=alt.Theta(field="Miktar", type="quantitative"),
        color=alt.Color(field="Kategori", type="nominal", scale=alt.Scale(scheme='category20'), legend=alt.Legend(title="Gider Dağılımı", orient="right")),
        tooltip=['Kategori', 'Miktar']
    ).properties(height=240).configure_view(strokeWidth=0)
    
    st.altair_chart(donut, use_container_width=True)
    
    st.markdown(f"<div style='text-align:center; color:#8a99ad; font-size:14px; margin-top:-30px;'>Halkadaki Toplam Gider: <b style='color:#ff5252;'>₺ {toplam_gider:.0f}</b></div>", unsafe_allow_html=True)
else:
    st.info("Portföyün şu an tertemiz! Aşağıdan ilk gelir veya giderini ekleyebilirsin.")
st.markdown('</div>', unsafe_allow_html=True)

# --- 3. DİNAMİK İŞLEM EKLEME ALANI ---
st.markdown('<div class="row-box">', unsafe_allow_html=True)
st.markdown('<div class="card-title">➕ Yeni Gelir / Gider Ekle</div>', unsafe_allow_html=True)

islem_turu = st.radio("Tür Seçin:", ["🔴 Gider (-)", "🟢 Gelir (+)"], horizontal=True)

with st.form("yeni_islem_formu", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        kat_input = st.text_input("Açıklama / Kategori", placeholder="Örn: Katılım Fonu, Altın, Monster...").strip().capitalize()
    with c2:
        mik_input = st.number_input("Miktar (₺)", min_value=0.0, step=10.0, format="%.2f")
    
    submit = st.form_submit_button("Hesaba İşle")
    
    if submit and kat_input and mik_input > 0:
        tur_net = "Gelir" if "Gelir" in islem_turu else "Gider"
        yeni_satir = pd.DataFrame([{"Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Tür": tur_net, "Kategori": kat_input, "Miktar": mik_input}])
        st.session_state.islemler = pd.concat([st.session_state.islemler, yeni_satir], ignore_index=True)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- 4. TÜM İŞLEMLER LİSTESİ ---
st.markdown('<div class="row-box">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📋 İşlem Geçmişi</div>', unsafe_allow_html=True)
if not df.empty:
    st.dataframe(df.sort_index(ascending=False), use_container_width=True, hide_index=True)
else:
    st.write("Henüz bir işlem yapılmadı.")
st.markdown('</div>', unsafe_allow_html=True)
