import streamlit as st
import leafmap.leafmap as leafmap
import pandas as pd
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
        options=[
            "ROADMAP", "SATELLITE", "TERRAIN", "HYBRID", 
            "OpenStreetMap", "CartoDB.Positron", "CartoDB.DarkMatter",
            "Stamen.Terrain", "Stamen.Toner", "Stamen.Watercolor",
            "ESRI.WorldTopoMap", "ESRI.WorldImagery"
        ],
        index=4  # OpenStreetMap varsayılan
    )
    
    # Zoom seviyesi
    zoom_level = st.slider("Zoom seviyesi:", 1, 18, 6)
    
    # Harita yüksekliği
    height = st.slider("Harita yüksekliği (piksel):", 300, 1000, 650)
    
    # Harita özellikleri
    st.markdown("## Harita Özellikleri")
    
    add_google_map = st.checkbox("Google Maps ekle", False)
    add_minimap = st.checkbox("Mini harita ekle", True)
    draw_export = st.checkbox("Çizim araçları", True)
    scale_bar = st.checkbox("Ölçek çubuğu", True)
    
    # Veri ekleme seçenekleri
    st.markdown("## Veri Seçenekleri")
    
    data_option = st.radio(
        "Veri kaynağı:",
        ["Önceden tanımlı veriler", "CSV yükle", "Çevrimiçi veriler", "Hiçbiri"]
    )
    
    if data_option == "Önceden tanımlı veriler":
        data_layer = st.selectbox(
            "Veri katmanı:",
            ["Ülke sınırları", "Eyalet sınırları", "Nüfus yoğunluğu", "Depremler"]
        )
        
        if data_layer == "Ülke sınırları":
            selected_region = st.multiselect(
                "Ülkeler:",
                ["Turkey", "United States", "Germany", "France", "Italy", "Spain", "China", "Japan"]
            )
    
    elif data_option == "CSV yükle":
        file_format = st.radio("Dosya formatı:", ["CSV", "GeoJSON", "Shapefile"], horizontal=True)
        uploaded_file = st.file_uploader(f"{file_format} dosyası yükleyin", type=["csv", "geojson", "shp"] if file_format == "Shapefile" else [file_format.lower()])
        if uploaded_file is not None:
            st.success(f"{file_format} dosyası yüklendi!")
    
    elif data_option == "Çevrimiçi veriler":
        online_source = st.selectbox(
            "Veri kaynağı:",
            ["USGS Depremler", "NASA GIBS", "NOAA Hava Durumu", "OpenStreetMap"]
        )
        
        if online_source == "USGS Depremler":
            eq_days = st.radio("Zaman aralığı:", ["1 gün", "7 gün", "30 gün"], horizontal=True)
            eq_mag = st.slider("Min. büyüklük:", 2.5, 8.0, 4.5, 0.5)
    
    # Harita aktif durumu için bir hızlı erişim linki
    st.markdown("## Harita İşlemleri")
    
    if st.button("🔄 Haritayı Sıfırla", use_container_width=True):
        st.experimental_rerun()
    
    if st.button("💾 Haritayı Kaydet", use_container_width=True):
        st.session_state.save_map = True

# Harita için sağ panel
with col2:
    # Harita oluştur
    m = leafmap.Map(
        center=[39.925533, 32.866287],  # Ankara
        zoom=zoom_level,
        height=height
    )
    
    # Harita özellikleri
    try:
        # Basemap değiştir
        if basemap in ["ROADMAP", "SATELLITE", "TERRAIN", "HYBRID"]:
            m.add_basemap("Google " + basemap)
        else:
            m.add_basemap(basemap)
            
        # Ek özellikler
        if add_google_map:
            m.add_basemap("Google ROADMAP")
            
        if add_minimap:
            m.add_minimap()
            
        if draw_export:
            m.add_draw_control()
            
        if scale_bar:
            m.scale_bar = True
            
        # Veri işlemleri
        if data_option == "Önceden tanımlı veriler":
            if data_layer == "Ülke sınırları" and selected_region:
                for region in selected_region:
                    m.add_geojson(f"https://raw.githubusercontent.com/johan/world.geo.json/master/countries/{region.lower()}.geo.json", layer_name=region)
                    
            elif data_layer == "Nüfus yoğunluğu":
                m.add_heatmap(
                    "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.geojson",
                    "pop_max",
                    layer_name="Nüfus Yoğunluğu"
                )
                
            elif data_layer == "Depremler":
                m.add_earthquake(5, 365, layer_name="Son 1 yıl M5.0+ Depremler")
                
        elif data_option == "CSV yükle" and uploaded_file is not None:
            # Geçici dosya oluştur
            file_path = f"temp.{file_format.lower()}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Dosya formatına göre işlem
            if file_format == "CSV":
                df = pd.read_csv(file_path)
                # Koordinat sütunlarını kontrol et
                lat_col = next((col for col in df.columns if col.lower() in ['lat', 'latitude', 'enlem']), None)
                lon_col = next((col for col in df.columns if col.lower() in ['lon', 'long', 'longitude', 'boylam']), None)
                
                if lat_col and lon_col:
                    m.add_points_from_xy(df, lon_col, lat_col, layer_name="CSV Veri Noktaları")
                else:
                    st.error("CSV'de enlem/boylam sütunları bulunamadı")
                    
            elif file_format == "GeoJSON":
                m.add_geojson(file_path, layer_name="GeoJSON Verisi")
                
            elif file_format == "Shapefile":
                m.add_shp(file_path, layer_name="Shapefile Verisi")
                
            # Geçici dosyayı temizle
            if os.path.exists(file_path):
                os.remove(file_path)
                
        elif data_option == "Çevrimiçi veriler":
            if online_source == "USGS Depremler":
                # Days
                if eq_days == "1 gün":
                    period = 1
                elif eq_days == "7 gün":
                    period = 7
                else:
                    period = 30
                
                m.add_earthquake(eq_mag, period, layer_name=f"Son {eq_days} M{eq_mag}+ Depremler")
                
            elif online_source == "NASA GIBS":
                m.add_tile_layer(
                    url="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2020-04-01/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
                    name="NASA GIBS",
                    attribution="NASA GIBS"
                )
                
            elif online_source == "OpenStreetMap":
                st.info("Bu işlev, OpenStreetMap API'sine istek gönderilmesini gerektirir ve genellikle sınırlı API anahtarları gerektirir.")
        
        # Haritayı göster
        m.to_streamlit(height=height)
        
        # İsteğe bağlı harita kaydetme
        if 'save_map' in st.session_state and st.session_state.save_map:
            m.to_html("harita.html")
            st.success("Harita 'harita.html' olarak kaydedildi!")
            st.session_state.save_map = False
            
    except Exception as e:
        st.error(f"Harita oluşturulurken bir hata oluştu: {e}")
        st.info("Leafmap'in son sürümüyle uyumluluk sorunları olabilir. Bazı özellikler devre dışı bırakılacak.")
        
        # Yedek basit harita - hata durumunda
        import folium
        from streamlit_folium import folium_static
        
        f_map = folium.Map(
            location=[39.925533, 32.866287],
            zoom_start=zoom_level,
            tiles=basemap.replace(".", " ") if "." in basemap else basemap
        )
        
        folium.LayerControl().add_to(f_map)
        folium_static(f_map, height=height)

# Sayfa altı bilgileri
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>Bu uygulama <a href="https://github.com/giswqs/leafmap" target="_blank">leafmap</a> ve 
    <a href="https://streamlit.io/" target="_blank">Streamlit</a> kullanılarak geliştirilmiştir.</p>
</div>
""", unsafe_allow_html=True)

# Bağımlılık bilgileri
with st.expander("Uygulama Hakkında Bilgiler"):
    st.code("""
    # Bu uygulamanın bağımlılıkları:
    streamlit>=1.11.0
    leafmap>=0.10.0
    pandas
    
    # requirements.txt dosyanızda bu paketlerin belirtildiğinden emin olun
    """)