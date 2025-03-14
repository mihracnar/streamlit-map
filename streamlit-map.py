import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import geopandas as gpd
import os

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Leafmap Harita Uygulaması",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Başlık
st.title("🗺️ Leafmap Harita Uygulaması")

# İki panel oluştur
col1, col2 = st.columns([1, 2])

# Parametre ve ayarlar için sol panel
with col1:
    st.markdown("## Harita Ayarları")
    
    # Harita tipi seçimi
    basemap = st.selectbox(
        "Harita türü seçin:",
        leafmap.basemaps.keys(),
        index=list(leafmap.basemaps.keys()).index("OpenStreetMap")
    )
    
    # Zoom seviyesi
    zoom_level = st.slider("Zoom seviyesi:", 1, 18, 6)
    
    # Harita yüksekliği
    height = st.slider("Harita yüksekliği (piksel):", 300, 1000, 650)
    
    # Harita özellikleri
    st.markdown("## Harita Özellikleri")
    
    show_measurement = st.checkbox("Ölçüm araçlarını göster", True)
    show_draw = st.checkbox("Çizim araçlarını göster", True)
    show_scale = st.checkbox("Ölçek çubuğunu göster", True)
    show_latlon = st.checkbox("Koordinatları göster", True)
    
    # Veri ekleme seçenekleri
    st.markdown("## Veri Seçenekleri")
    
    data_option = st.radio(
        "Veri kaynağı:",
        ["Ülke sınırları", "Deprem verileri", "CSV yükle", "GeoJSON yükle"]
    )
    
    if data_option == "Ülke sınırları":
        country = st.selectbox(
            "Ülke seçin:",
            ["Türkiye", "ABD", "Almanya", "Fransa", "İtalya", "İspanya", "Japonya"]
        )
    
    elif data_option == "Deprem verileri":
        days = st.radio("Son kaç gün:", ["1", "7", "30"], horizontal=True)
        min_magnitude = st.slider("Minimum büyüklük:", 2.5, 8.0, 4.5, 0.5)
    
    elif data_option == "CSV yükle" or data_option == "GeoJSON yükle":
        file_format = "csv" if data_option == "CSV yükle" else "geojson"
        uploaded_file = st.file_uploader(f"{file_format.upper()} dosyası yükleyin", type=[file_format])
        if uploaded_file is not None:
            st.success(f"{file_format.upper()} dosyası yüklendi!")
    
    # Harita ekstra özellikleri
    st.markdown("## Ekstra Özellkler")
    
    add_labels = st.checkbox("Yer adları ekle")
    
    # Harita aktif durumu için bir hızlı erişim linki
    st.markdown("## Harita İşlemleri")
    
    if st.button("🔄 Haritayı Sıfırla", use_container_width=True):
        st.experimental_rerun()
    
    if st.button("💾 Haritayı Kaydet", use_container_width=True):
        st.session_state.save_map = True

# Harita için sağ panel
with col2:
    # Leafmap haritası oluştur
    m = leafmap.Map(
        center=[39.925533, 32.866287],  # Ankara
        zoom=zoom_level,
        basemap=basemap,
        height=height,
        width=800
    )
    
    # Harita özelliklerini ekle
    if show_measurement:
        m.add_measurement()
    
    if show_draw:
        m.add_draw_control()
    
    if show_scale:
        m.add_scale_bar()
    
    if show_latlon:
        m.add_mouse_position()
    
    # Kontrol katmanı ekle
    m.add_layer_control()
    
    # Seçilen veri kaynağına göre haritayı doldur
    if data_option == "Ülke sınırları":
        country_dict = {
            "Türkiye": "Turkey", 
            "ABD": "United States of America", 
            "Almanya": "Germany", 
            "Fransa": "France", 
            "İtalya": "Italy", 
            "İspanya": "Spain", 
            "Japonya": "Japan"
        }
        
        if country in country_dict:
            # Leafmap'in ülke sınırları fonksiyonunu kullan
            m.add_country_boundary(country_dict[country], layer_name=f"{country} Sınırları")
            
            # Türkiye için ek olarak iller ekle
            if country == "Türkiye":
                # Not: Gerçek uygulamada Türkiye il sınırlarını GeoJSON olarak ekleyebilirsiniz
                st.info("Türkiye il sınırları için GeoJSON ekleyebilirsiniz.")
    
    elif data_option == "Deprem verileri":
        days_dict = {"1": "day", "7": "week", "30": "month"}
        selected_period = days_dict[days]
        
        # USGS deprem verilerini ekle
        m.add_earthquake(
            period=selected_period, 
            min_magnitude=min_magnitude,
            layer_name=f"Son {days} gün, M{min_magnitude}+ Depremler"
        )
    
    elif data_option == "CSV yükle" and uploaded_file is not None:
        # CSV dosyasını oku
        try:
            df = pd.read_csv(uploaded_file)
            
            # Koordinat sütunlarını tanımla - farklı sütun isimleri için kontrol et
            lat_col = next((col for col in df.columns if col.lower() in ['lat', 'latitude', 'enlem']), None)
            lon_col = next((col for col in df.columns if col.lower() in ['lon', 'longitude', 'boylam']), None)
            
            if lat_col and lon_col:
                # CSV noktalarını haritaya ekle
                m.add_points_from_xy(
                    df,
                    x=lon_col,
                    y=lat_col,
                    layer_name="CSV Verileri"
                )
            else:
                st.error("CSV dosyasında enlem ve boylam sütunları bulunamadı.")
        except Exception as e:
            st.error(f"CSV okunamadı: {e}")
    
    elif data_option == "GeoJSON yükle" and uploaded_file is not None:
        # GeoJSON dosyasını oku
        try:
            # Dosyayı geçici olarak kaydet
            with open("temp.geojson", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # GeoJSON'u haritaya ekle
            m.add_geojson("temp.geojson", layer_name="GeoJSON Verileri")
            
            # Geçici dosyayı temizle
            if os.path.exists("temp.geojson"):
                os.remove("temp.geojson")
                
        except Exception as e:
            st.error(f"GeoJSON okunamadı: {e}")
    
    # Ekstra özellikler
    if add_labels:
        m.add_labels()
    
    # Haritayı göster
    m.to_streamlit()
    
    # İsteğe bağlı harita kaydetme
    if 'save_map' in st.session_state and st.session_state.save_map:
        m.to_html("harita.html")
        st.success("Harita 'harita.html' olarak kaydedildi!")
        st.session_state.save_map = False

# Sayfa altı bilgileri
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>Bu uygulama <a href="https://github.com/giswqs/leafmap" target="_blank">leafmap</a> ve 
    <a href="https://streamlit.io/" target="_blank">Streamlit</a> kullanılarak geliştirilmiştir.</p>
</div>
""", unsafe_allow_html=True)