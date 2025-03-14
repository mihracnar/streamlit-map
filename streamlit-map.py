import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import json
import random
from folium.plugins import Draw, Fullscreen, MeasureControl, MousePosition

# Sayfa konfigürasyonu - Tam Ekran için
st.set_page_config(
    page_title="Tam Ekran Harita",
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
    
    /* Folium harita yüksekliği */
    .stFolium {
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

# Harita tiplerini ve attribution değerlerini tanımla
MAP_TYPES = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": "© OpenStreetMap contributors"
    },
    "Kartografen": {
        "tiles": "CartoDB positron",
        "attr": "© OpenStreetMap contributors, © CARTO"
    },
    "Koyu Tema": {
        "tiles": "CartoDB dark_matter",
        "attr": "© OpenStreetMap contributors, © CARTO"
    },
    "Arazi Haritası": {
        "tiles": "Stamen Terrain",
        "attr": "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
    },
    "Siyah Beyaz": {
        "tiles": "Stamen Toner",
        "attr": "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
    },
    "Uydu Görüntüsü": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri, Maxar, Earthstar Geographics, and the GIS User Community"
    }
}

# Oturum durumu (ayarları saklamak için)
if 'map_type' not in st.session_state:
    st.session_state.map_type = "OpenStreetMap"
if 'zoom' not in st.session_state:
    st.session_state.zoom = 6
if 'center_lat' not in st.session_state:
    st.session_state.center_lat = 39.925533  # Ankara
if 'center_lon' not in st.session_state:
    st.session_state.center_lon = 32.866287  # Ankara
if 'data_option' not in st.session_state:
    st.session_state.data_option = "Şehir Noktaları"

# Yan panel (gizlenebilir)
with st.sidebar:
    st.title("🗺️ Harita Ayarları")
    
    # Harita tipi seçimi
    map_type = st.selectbox(
        "Harita türü:", 
        list(MAP_TYPES.keys()),
        index=list(MAP_TYPES.keys()).index(st.session_state.map_type)
    )
    st.session_state.map_type = map_type
    
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
    
    show_measurement = st.checkbox("Ölçüm aracı", True)
    show_draw = st.checkbox("Çizim aracı", True)
    show_fullscreen = st.checkbox("Tam ekran kontrolü", True)
    show_scale = st.checkbox("Ölçek çubuğu", True)
    show_location = st.checkbox("Koordinat gösterici", True)
    
    # Veri ekleme seçenekleri
    st.subheader("Veri Seçenekleri")
    
    data_option = st.radio(
        "Veri Türü:",
        ["Şehir Noktaları", "Deprem Verileri", "İlgi Noktaları", "Harita Temiz"],
        index=["Şehir Noktaları", "Deprem Verileri", "İlgi Noktaları", "Harita Temiz"].index(st.session_state.data_option)
    )
    st.session_state.data_option = data_option
    
    if data_option == "Deprem Verileri":
        if 'eq_days' not in st.session_state:
            st.session_state.eq_days = 7
        if 'eq_magnitude' not in st.session_state:
            st.session_state.eq_magnitude = 4.5
            
        days = st.radio("Son kaç gün:", ["1", "7", "30"], index=["1", "7", "30"].index(str(st.session_state.eq_days)))
        magnitude = st.slider("Min. büyüklük:", 2.5, 8.0, st.session_state.eq_magnitude, 0.5)
        
        st.session_state.eq_days = int(days)
        st.session_state.eq_magnitude = magnitude
    
    elif data_option == "İlgi Noktaları":
        if 'poi_type' not in st.session_state:
            st.session_state.poi_type = "Restoranlar"
        
        poi_type = st.selectbox(
            "POI tipi:",
            ["Restoranlar", "Oteller", "Müzeler", "Parklar", "Alışveriş"],
            index=["Restoranlar", "Oteller", "Müzeler", "Parklar", "Alışveriş"].index(st.session_state.poi_type)
        )
        st.session_state.poi_type = poi_type
    
    # Haritayı sıfırla
    if st.button("🔄 Haritayı Sıfırla", use_container_width=True):
        st.session_state.map_type = "OpenStreetMap"
        st.session_state.zoom = 6
        st.session_state.center_lat = 39.925533
        st.session_state.center_lon = 32.866287
        st.session_state.data_option = "Şehir Noktaları"
        st.rerun()  # Modern Streamlit API
    
    # Bilgi
    st.markdown("---")
    st.markdown("### Tam Ekran İpuçları")
    st.info("Yan menüyü gizlemek için ekranın sol üst köşesindeki '>' butonuna tıklayabilirsiniz.")

# Ana container - harita için
map_container = st.container()

with map_container:
    # Harita merkezi
    center_location = [st.session_state.center_lat, st.session_state.center_lon]
    
    # Harita oluştur
    m = folium.Map(
        location=center_location,
        zoom_start=st.session_state.zoom,
        tiles=MAP_TYPES[map_type]["tiles"],
        attr=MAP_TYPES[map_type]["attr"],
        control_scale=show_scale
    )
    
    # Harita eklentileri
    if show_measurement:
        MeasureControl(
            position="bottomright",
            primary_length_unit="kilometers",
            secondary_length_unit="miles",
            primary_area_unit="sqmeters",
            secondary_area_unit="acres"
        ).add_to(m)
    
    if show_draw:
        Draw(
            position="topleft",
            draw_options={
                'polyline': True,
                'polygon': True,
                'rectangle': True,
                'circle': True,
                'marker': True,
                'circlemarker': False
            },
            edit_options={
                'poly': {'allowIntersection': False}
            }
        ).add_to(m)
    
    if show_fullscreen:
        Fullscreen(
            position="topright",
            title="Tam ekrana geç",
            title_cancel="Tam ekrandan çık",
            force_separate_button=True
        ).add_to(m)
    
    if show_location:
        MousePosition(
            position="bottomleft",
            separator=" | ",
            prefix="Koordinatlar:",
            num_digits=6
        ).add_to(m)
    
    # Veri ekleme
    if data_option == "Şehir Noktaları":
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
        
        # Kümeleyici ekle
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster(name="Şehir Kümeleri").add_to(m)
        
        # Şehirler için marker ekle
        for city, data in cities.items():
            # Nüfus verilerini kullan
            radius = (data[2] / 16000000) * 25 + 5
            
            # Popup içeriği
            popup_text = f"""
            <div style="font-family: Arial, sans-serif; font-size: 12px; width: 200px;">
                <h4 style="margin: 5px 0; color: #0078D7;">{city}</h4>
                <hr style="margin: 5px 0;">
                <p><b>Nüfus:</b> {data[2]:,}</p>
                <p><b>Konum:</b> {data[0]:.4f}, {data[1]:.4f}</p>
            </div>
            """
            
            # Marker ekle
            folium.CircleMarker(
                location=data[:2],
                radius=radius,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=city,
                fill=True,
                fill_color="blue",
                color="darkblue",
                fill_opacity=0.6,
                weight=2
            ).add_to(marker_cluster)
    
    elif data_option == "Deprem Verileri":
        try:
            # USGS API'sinden deprem verilerini çek
            period_dict = {"1": "day", "7": "week", "30": "month"}
            selected_period = period_dict[str(st.session_state.eq_days)]
            
            url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{st.session_state.eq_magnitude}_{selected_period}.geojson"
            response = requests.get(url)
            
            if response.status_code == 200:
                earthquake_data = response.json()
                
                # Deprem sayısı
                eq_count = len(earthquake_data["features"])
                info_col1, info_col2 = st.columns([1, 3])
                with info_col1:
                    st.markdown("### 🌍 Depremler")
                with info_col2:
                    st.success(f"Son {st.session_state.eq_days} gün içindeki M{st.session_state.eq_magnitude}+ toplam {eq_count} deprem gösteriliyor")
                
                # Her deprem için marker ekle
                for eq in earthquake_data["features"]:
                    props = eq["properties"]
                    geometry = eq["geometry"]["coordinates"]
                    
                    mag = props["mag"]
                    place = props["place"]
                    time = pd.to_datetime(props["time"], unit="ms")
                    depth = geometry[2]
                    
                    # Büyüklüğe göre renk ve boyut
                    if mag >= 5.0:
                        color = "red"
                        radius = mag * 3
                    elif mag >= 4.0:
                        color = "orange"
                        radius = mag * 2.5
                    else:
                        color = "green"
                        radius = mag * 2
                    
                    # Popup içeriği
                    popup_text = f"""
                    <div style="font-family: Arial, sans-serif; font-size: 12px; width: 200px;">
                        <h4 style="margin: 5px 0; color: #D32F2F;">{place}</h4>
                        <hr style="margin: 5px 0;">
                        <p><b>Büyüklük:</b> {mag}</p>
                        <p><b>Derinlik:</b> {depth:.1f} km</p>
                        <p><b>Zaman:</b> {time}</p>
                        <p><b>Konum:</b> {geometry[1]:.4f}, {geometry[0]:.4f}</p>
                    </div>
                    """
                    
                    # Deprem marker'ı
                    folium.CircleMarker(
                        location=[geometry[1], geometry[0]],
                        radius=radius,
                        popup=folium.Popup(popup_text, max_width=300),
                        tooltip=f"M{mag} - {place}",
                        fill=True,
                        fill_color=color,
                        color="black",
                        fill_opacity=0.7,
                        weight=1
                    ).add_to(m)
            else:
                st.error(f"Deprem verileri alınamadı: Hata kodu {response.status_code}")
        except Exception as e:
            st.error(f"Deprem verileri alınırken hata: {e}")
    
    elif data_option == "İlgi Noktaları":
        # POI simüle edilmiş verileri
        import random
        
        # POI'ler için simge belirle
        poi_icons = {
            "Restoranlar": "cutlery",
            "Oteller": "home",
            "Müzeler": "university",
            "Parklar": "tree",
            "Alışveriş": "shopping-cart"
        }
        
        # POI'ler için renk belirle
        poi_colors = {
            "Restoranlar": "red",
            "Oteller": "blue",
            "Müzeler": "green",
            "Parklar": "green",
            "Alışveriş": "orange"
        }
        
        # POI sayısı
        poi_count = 15
        
        # Kümeleyici ekle
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster(name=st.session_state.poi_type).add_to(m)
        
        # Veri oluştur
        poi_data = []
        for i in range(poi_count):
            # Merkez etrafında rastgele noktalar
            lat_offset = random.uniform(-0.1, 0.1)
            lon_offset = random.uniform(-0.1, 0.1)
            
            lat = center_location[0] + lat_offset
            lon = center_location[1] + lon_offset
            
            if st.session_state.poi_type == "Restoranlar":
                name = f"{random.choice(['Lezzet', 'Anadolu', 'İstanbul', 'Mavi', 'Yeşil'])} Restoran {i+1}"
                rating = round(random.uniform(3.0, 5.0), 1)
                details = f"Mutfak: {random.choice(['Türk', 'İtalyan', 'Çin', 'Meksika'])}"
            elif st.session_state.poi_type == "Oteller":
                name = f"{random.choice(['Grand', 'Royal', 'Palace', 'City'])} Hotel {i+1}"
                rating = round(random.uniform(3.0, 5.0), 1)
                details = f"Yıldız: {random.randint(3, 5)}"
            elif st.session_state.poi_type == "Müzeler":
                name = f"{random.choice(['Tarih', 'Sanat', 'Arkeoloji', 'Modern'])} Müzesi {i+1}"
                rating = round(random.uniform(3.5, 5.0), 1)
                details = f"Tür: {random.choice(['Tarih', 'Sanat', 'Arkeoloji', 'Bilim'])}"
            elif st.session_state.poi_type == "Parklar":
                name = f"{random.choice(['Millet', 'Gençlik', 'Atatürk', 'Kültür'])} Parkı {i+1}"
                rating = round(random.uniform(3.8, 5.0), 1)
                details = f"Alan: {random.randint(5, 100)} dönüm"
            else:
                name = f"{random.choice(['Mega', 'Star', 'City', 'Plaza'])} AVM {i+1}"
                rating = round(random.uniform(3.5, 5.0), 1)
                details = f"Mağaza sayısı: {random.randint(20, 150)}"
            
            poi_data.append({
                "name": name,
                "lat": lat,
                "lon": lon,
                "rating": rating,
                "details": details
            })
        
        # İlgi noktaları için mini bilgi paneli
        info_col1, info_col2 = st.columns([1, 3])
        with info_col1:
            st.markdown(f"### 📍 {st.session_state.poi_type}")
        with info_col2:
            st.info(f"Toplam {poi_count} adet {st.session_state.poi_type.lower()} gösteriliyor")
        
        # Veri ön izleme
        with st.expander(f"{st.session_state.poi_type} Listesi", expanded=False):
            st.dataframe(pd.DataFrame(poi_data))
        
        # Her POI için marker ekle
        for poi in poi_data:
            # Popup içeriği
            popup_text = f"""
            <div style="font-family: Arial, sans-serif; font-size: 12px; width: 200px;">
                <h4 style="margin: 5px 0; color: #0078D7;">{poi['name']}</h4>
                <hr style="margin: 5px 0;">
                <p><b>Puan:</b> {poi['rating']}/5.0 ⭐</p>
                <p><b>{poi['details']}</b></p>
                <p><b>Konum:</b> {poi['lat']:.4f}, {poi['lon']:.4f}</p>
            </div>
            """
            
            # Marker ekle
            folium.Marker(
                location=[poi['lat'], poi['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=poi['name'],
                icon=folium.Icon(color=poi_colors[st.session_state.poi_type], icon=poi_icons[st.session_state.poi_type], prefix="fa")
            ).add_to(marker_cluster)
    
    # Katman kontrolü ekle
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Haritayı göster - st_folium ile modern method
    st_folium(m, width=1500, height=800, returned_objects=[])