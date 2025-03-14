import streamlit as st
import leafmap.leafmap as leafmap
import pandas as pd
import os
import requests
import json
import random

# Sayfa konfigürasyonu - Tam Ekran için
st.set_page_config(
    page_title="Tam Ekran Leafmap",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Yan paneli otomatik kapalı başlat
)

# CSS ile tam ekran efekti
st.markdown("""
<style>
    .main > div {
        padding-top: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Leafmap yüksekliği - iframe için */
    iframe {
        height: 95vh !important;
        width: 100% !important;
    }
    
    /* Buton stilleri */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Oturum durumu (ayarları saklamak için)
if 'basemap' not in st.session_state:
    st.session_state.basemap = "OpenStreetMap"
if 'zoom' not in st.session_state:
    st.session_state.zoom = 6
if 'center_lat' not in st.session_state:
    st.session_state.center_lat = 39.925533  # Ankara
if 'center_lon' not in st.session_state:
    st.session_state.center_lon = 32.866287  # Ankara
if 'data_option' not in st.session_state:
    st.session_state.data_option = "Şehirler"

# Leafmap için kullanılabilir harita altlıkları
basemap_options = [
    "OpenStreetMap",
    "SATELLITE",
    "ROADMAP",
    "TERRAIN",
    "HYBRID",
    "CartoDB.Positron",
    "CartoDB.DarkMatter",
    "Stamen.Terrain",
    "Stamen.Toner",
    "Esri.WorldImagery"
]

# Yan panel (gizlenebilir)
with st.sidebar:
    st.title("🗺️ Harita Ayarları")
    
    # Basemap seçimi
    basemap = st.selectbox(
        "Harita Türü:", 
        basemap_options,
        index=basemap_options.index(st.session_state.basemap)
    )
    st.session_state.basemap = basemap
    
    # Konum ayarları
    st.subheader("Konum")
    
    location_option = st.radio(
        "Konum:",
        ["Ankara (Varsayılan)", "Kendi konumum"]
    )
    
    if location_option == "Kendi konumum":
        col1, col2 = st.columns(2)
        with col1:
            center_lat = st.number_input("Enlem", value=st.session_state.center_lat, format="%.6f")
        with col2:
            center_lon = st.number_input("Boylam", value=st.session_state.center_lon, format="%.6f")
        
        st.session_state.center_lat = center_lat
        st.session_state.center_lon = center_lon
    else:
        st.session_state.center_lat = 39.925533  # Ankara
        st.session_state.center_lon = 32.866287  # Ankara
    
    # Zoom seviyesi
    zoom = st.slider("Zoom seviyesi:", 1, 18, st.session_state.zoom)
    st.session_state.zoom = zoom
    
    # Harita özellikleri
    st.subheader("Harita Özellikleri")
    
    show_minimap = st.checkbox("Mini harita", True)
    show_draw = st.checkbox("Çizim araçları", True)
    show_fullscreen = st.checkbox("Tam ekran kontrolü", True)
    show_search = st.checkbox("Arama", False)
    
    # Veri ekleme seçenekleri
    st.subheader("Veri Seçenekleri")
    
    data_option = st.radio(
        "Veri Türü:",
        ["Şehirler", "Depremler", "İlgi Noktaları", "3D Arazi", "Temiz Harita"],
        index=["Şehirler", "Depremler", "İlgi Noktaları", "3D Arazi", "Temiz Harita"].index(st.session_state.data_option)
    )
    st.session_state.data_option = data_option
    
    if data_option == "Depremler":
        if 'eq_days' not in st.session_state:
            st.session_state.eq_days = 7
        if 'eq_magnitude' not in st.session_state:
            st.session_state.eq_magnitude = 4.5
            
        days = st.slider("Son kaç gün:", 1, 30, st.session_state.eq_days)
        magnitude = st.slider("Min. büyüklük:", 2.5, 8.0, st.session_state.eq_magnitude, 0.5)
        
        st.session_state.eq_days = days
        st.session_state.eq_magnitude = magnitude
    
    elif data_option == "İlgi Noktaları":
        if 'poi_type' not in st.session_state:
            st.session_state.poi_type = "Şehirler"
        
        poi_type = st.selectbox(
            "POI tipi:",
            ["Şehirler", "Havalimanları", "Limanlar", "Dağlar", "Barajlar"],
            index=["Şehirler", "Havalimanları", "Limanlar", "Dağlar", "Barajlar"].index(st.session_state.poi_type)
        )
        st.session_state.poi_type = poi_type
    
    elif data_option == "3D Arazi":
        if 'exaggeration' not in st.session_state:
            st.session_state.exaggeration = 3
        
        exaggeration = st.slider("Yükseklik çarpanı:", 1, 10, st.session_state.exaggeration)
        st.session_state.exaggeration = exaggeration
    
    # Haritayı sıfırla
    if st.button("🔄 Haritayı Sıfırla", use_container_width=True):
        st.session_state.basemap = "OpenStreetMap"
        st.session_state.zoom = 6
        st.session_state.center_lat = 39.925533
        st.session_state.center_lon = 32.866287
        st.session_state.data_option = "Şehirler"
        st.rerun()  # Modern Streamlit API
    
    # Bilgi
    st.markdown("---")
    st.markdown("### Tam Ekran İpuçları")
    st.info("Yan menüyü gizlemek için ekranın sol üst köşesindeki '>' butonuna tıklayabilirsiniz.")

# Ana container - harita için
map_container = st.container()

with map_container:
    try:
        # Leafmap haritası oluştur
        m = leafmap.Map(
            center=[st.session_state.center_lat, st.session_state.center_lon],
            zoom=st.session_state.zoom,
            draw_control=show_draw,
            measure_control=True,
            fullscreen_control=show_fullscreen,
            search_control=show_search,
            attribution_control=True
        )
        
        # Mini harita
        if show_minimap:
            m.add_minimap()
        
        # Basemap'i ayarla
        if basemap in ["SATELLITE", "ROADMAP", "TERRAIN", "HYBRID"]:
            m.add_basemap(f"Google {basemap}")
        else:
            m.add_basemap(basemap)
        
        # Veri Ekle
        if data_option == "Şehirler":
            # Türkiye'nin büyük şehirleri
            cities = {
                "İstanbul": [41.0082, 28.9784, 16000000],
                "Ankara": [39.9334, 32.8597, 5700000],
                "İzmir": [38.4192, 27.1287, 4400000],
                "Antalya": [36.8969, 30.7133, 2500000],
                "Bursa": [40.1885, 29.0610, 3100000],
                "Adana": [37.0000, 35.3213, 2200000],
                "Konya": [37.8746, 32.4932, 2300000],
                "Trabzon": [41.0027, 39.7168, 800000],
                "Gaziantep": [37.0662, 37.3833, 2100000],
                "Diyarbakır": [37.9144, 40.2306, 1800000]
            }
            
            # Veri çerçevesi oluştur
            city_data = []
            for city, info in cities.items():
                city_data.append({
                    "City": city,
                    "Latitude": info[0],
                    "Longitude": info[1],
                    "Population": info[2]
                })
            
            df = pd.DataFrame(city_data)
            
            # Şehir bilgilerini gösterme
            info_col1, info_col2 = st.columns([1, 3])
            with info_col1:
                st.markdown("### 🏙️ Türkiye Şehirleri")
            with info_col2:
                st.success(f"Toplam {len(cities)} büyük şehir gösteriliyor")
            
            # Şehirleri haritaya ekle
            m.add_points_from_xy(
                df,
                x="Longitude",
                y="Latitude",
                color_column="Population",
                add_legend=True,
                legend_title="Nüfus",
                layer_name="Türkiye Şehirleri",
                popup=["City", "Population"],
                icon_names=['city'] * len(df)
            )
        
        elif data_option == "Depremler":
            try:
                # USGS API'sinden deprem verilerini çek
                period_dict = {1: "day", 7: "week", 30: "month"}
                selected_period = period_dict[st.session_state.eq_days]
                
                url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{st.session_state.eq_magnitude}_{selected_period}.geojson"
                response = requests.get(url)
                
                if response.status_code == 200:
                    earthquake_data = response.json()
                    
                    # Deprem bilgilerini gösterme
                    info_col1, info_col2 = st.columns([1, 3])
                    with info_col1:
                        st.markdown("### 🌍 Depremler")
                    with info_col2:
                        st.success(f"Son {st.session_state.eq_days} gün içindeki M{st.session_state.eq_magnitude}+ depremler gösteriliyor")
                    
                    # GeoJSON'u haritaya ekle
                    m.add_geojson(
                        earthquake_data,
                        layer_name=f"Son {st.session_state.eq_days} gün M{st.session_state.eq_magnitude}+ Depremler",
                        info_mode="on_click",
                        style={
                            "color": "red",
                            "fillOpacity": 0.7,
                            "weight": 1
                        }
                    )
                else:
                    st.error(f"Deprem verileri alınamadı: Hata kodu {response.status_code}")
            except Exception as e:
                st.error(f"Deprem verileri alınırken hata: {e}")
        
        elif data_option == "İlgi Noktaları":
            # POI türüne göre sembolik gösterim (leafmap özelliği)
            if st.session_state.poi_type == "Şehirler":
                m.add_osm_from_geocode(
                    "Ankara, Turkey",
                    layer_name="Ankara",
                    buffer_dist=30000,
                    tags={"place": "city"}
                )
                
            elif st.session_state.poi_type == "Havalimanları":
                try:
                    # Türkiye'deki havalimanları için temsili noktalar
                    airports = [
                        {"name": "İstanbul Havalimanı", "lat": 41.2753, "lon": 28.7519},
                        {"name": "Sabiha Gökçen Havalimanı", "lat": 40.8985, "lon": 29.3092},
                        {"name": "Ankara Esenboğa Havalimanı", "lat": 40.1283, "lon": 32.9956},
                        {"name": "İzmir Adnan Menderes Havalimanı", "lat": 38.2924, "lon": 27.1562},
                        {"name": "Antalya Havalimanı", "lat": 36.9039, "lon": 30.7917},
                        {"name": "Dalaman Havalimanı", "lat": 36.7134, "lon": 28.7930},
                        {"name": "Milas-Bodrum Havalimanı", "lat": 37.2505, "lon": 27.6643}
                    ]
                    
                    airport_df = pd.DataFrame(airports)
                    m.add_points_from_xy(
                        airport_df,
                        x="lon",
                        y="lat",
                        layer_name="Havalimanları",
                        popup=["name"],
                        icon_names=['plane'] * len(airport_df)
                    )
                except Exception as e:
                    st.error(f"Havalimanları eklenirken hata: {e}")
            
            elif st.session_state.poi_type == "Limanlar":
                try:
                    # Türkiye'deki limanlar için temsili noktalar
                    ports = [
                        {"name": "İstanbul Limanı", "lat": 41.0050, "lon": 28.9783},
                        {"name": "İzmir Limanı", "lat": 38.4422, "lon": 27.1428},
                        {"name": "Mersin Limanı", "lat": 36.8103, "lon": 34.6361},
                        {"name": "Samsun Limanı", "lat": 41.2867, "lon": 36.3367},
                        {"name": "Trabzon Limanı", "lat": 41.0027, "lon": 39.7333}
                    ]
                    
                    port_df = pd.DataFrame(ports)
                    m.add_points_from_xy(
                        port_df,
                        x="lon",
                        y="lat",
                        layer_name="Limanlar",
                        popup=["name"],
                        icon_names=['anchor'] * len(port_df)
                    )
                except Exception as e:
                    st.error(f"Limanlar eklenirken hata: {e}")
            
            elif st.session_state.poi_type == "Dağlar":
                try:
                    # Türkiye'deki dağlar için temsili noktalar
                    mountains = [
                        {"name": "Ağrı Dağı", "lat": 39.7020, "lon": 44.2988, "height": 5137},
                        {"name": "Kaçkar Dağı", "lat": 40.8350, "lon": 41.1600, "height": 3937},
                        {"name": "Erciyes Dağı", "lat": 38.5308, "lon": 35.4477, "height": 3916},
                        {"name": "Uludağ", "lat": 40.0959, "lon": 29.2239, "height": 2543},
                        {"name": "Suphan Dağı", "lat": 38.9158, "lon": 42.8336, "height": 4058}
                    ]
                    
                    mountain_df = pd.DataFrame(mountains)
                    m.add_points_from_xy(
                        mountain_df,
                        x="lon",
                        y="lat",
                        color_column="height",
                        layer_name="Dağlar",
                        add_legend=True,
                        legend_title="Yükseklik (m)",
                        popup=["name", "height"],
                        icon_names=['mountain'] * len(mountain_df)
                    )
                except Exception as e:
                    st.error(f"Dağlar eklenirken hata: {e}")
            
            elif st.session_state.poi_type == "Barajlar":
                try:
                    # Türkiye'deki barajlar için temsili noktalar
                    dams = [
                        {"name": "Atatürk Barajı", "lat": 37.4933, "lon": 38.3303, "capacity": 48.7},
                        {"name": "Keban Barajı", "lat": 38.8123, "lon": 38.7551, "capacity": 31.0},
                        {"name": "Karakaya Barajı", "lat": 38.2422, "lon": 39.2842, "capacity": 9.58},
                        {"name": "Ilısu Barajı", "lat": 37.5428, "lon": 41.2123, "capacity": 10.9},
                        {"name": "Hirfanlı Barajı", "lat": 39.1672, "lon": 33.4913, "capacity": 7.6}
                    ]
                    
                    dam_df = pd.DataFrame(dams)
                    m.add_points_from_xy(
                        dam_df,
                        x="lon",
                        y="lat",
                        color_column="capacity",
                        layer_name="Barajlar",
                        add_legend=True,
                        legend_title="Kapasite (km³)",
                        popup=["name", "capacity"],
                        icon_names=['water'] * len(dam_df)
                    )
                except Exception as e:
                    st.error(f"Barajlar eklenirken hata: {e}")
        
        elif data_option == "3D Arazi":
            try:
                # 3D Arazi ekle
                m.add_3d_terrain(
                    exaggeration=st.session_state.exaggeration,
                    texture="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                )
                info_col1, info_col2 = st.columns([1, 3])
                with info_col1:
                    st.markdown("### 🏔️ 3D Arazi")
                with info_col2:
                    st.success(f"3D Arazi görüntüsü yükseklik çarpanı: {st.session_state.exaggeration}x")
            except Exception as e:
                st.error(f"3D Arazi eklenirken hata: {e}")
        
        # Katman kontrolü ekle
        m.add_layer_control()
        
        # Haritayı göster
        m.to_streamlit(height=800)
        
    except Exception as e:
        st.error(f"Leafmap hatası: {e}")
        st.info("""
        Leafmap yüklenirken bir sorun oluştu. Bu sorun genellikle Streamlit Cloud'da görülür.
        Bu kütüphanenin düzgün çalışması için şunları deneyebilirsiniz:
        
        1. requirements.txt dosyanızı şu şekilde güncelleyin:
        ```
        streamlit>=1.22.0
        leafmap
        geocoder
        ipywidgets
        ```
        
        2. Uygulamanızı yerel olarak çalıştırın:
        ```
        pip install leafmap
        streamlit run streamlit-map.py
        ```
        """)