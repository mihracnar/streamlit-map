import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen, MeasureControl, MousePosition, Draw

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="İnteraktif Harita",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Yan paneli otomatik kapalı başlat
)

# CSS ile dengeli bir yerleşim için düzenleme
st.markdown("""
<style>
    /* Tüm sayfayı düzenle */
    .stApp {
        margin: 0;
        padding: 0;
    }
    
    /* Konteyner düzenlemesi */
    .block-container {
        padding-top: 2rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Streamlit arayüzünü koru */
    #MainMenu {visibility: visible;}
    footer {visibility: visible;}
    header {visibility: visible;}
    
    /* Harita iframe'in yerleşimini düzenle */
    iframe {
        height: 80vh !important;
        width: 100% !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Diğer elementleri düzenle */
    h3 {
        margin-top: 0;
        margin-bottom: 1rem;
    }
    
    /* Alt bilgiyi düzenle */
    footer {
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Yan panel oluştur
with st.sidebar:
    st.title("🗺️ Harita Ayarları")
    
    # Harita tipi seçimi
    map_type = st.selectbox(
        "Harita Türü:", 
        ["OpenStreetMap", "CartoDB Dark", "CartoDB Positron", "Stamen Terrain", "Stamen Toner"]
    )
    
    # Konum ayarları
    st.subheader("Konum")
    location_option = st.radio(
        "Konum:",
        ["Ankara (Varsayılan)", "İstanbul", "İzmir", "Kendi konumum"]
    )
    
    if location_option == "Ankara (Varsayılan)":
        center_location = [39.925533, 32.866287]
    elif location_option == "İstanbul":
        center_location = [41.0082, 28.9784]
    elif location_option == "İzmir":
        center_location = [38.4192, 27.1287]
    else:  # Kendi konumum
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Enlem", value=39.925533, format="%.6f")
        with col2:
            lon = st.number_input("Boylam", value=32.866287, format="%.6f")
        center_location = [lat, lon]
    
    # Zoom seviyesi
    zoom_level = st.slider("Zoom seviyesi:", 1, 18, 6)
    
    # Harita özellikleri
    st.subheader("Harita Özellikleri")
    
    show_markers = st.checkbox("Şehir noktaları", True)
    show_measure = st.checkbox("Ölçüm araçları", True)
    show_locate = st.checkbox("Konum bulma", True)
    show_draw = st.checkbox("Çizim araçları", True)
    
    # Yenileme butonu
    if st.button("🔄 Haritayı Yenile", use_container_width=True):
        st.rerun()

# Ana içerik
st.title("İnteraktif Türkiye Haritası")

# Harita altlığı ve attribution
tiles_dict = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": "© OpenStreetMap contributors"
    },
    "CartoDB Dark": {
        "tiles": "CartoDB dark_matter",
        "attr": "© OpenStreetMap contributors, © CARTO"
    },
    "CartoDB Positron": {
        "tiles": "CartoDB positron",
        "attr": "© OpenStreetMap contributors, © CARTO"
    },
    "Stamen Terrain": {
        "tiles": "Stamen Terrain",
        "attr": "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
    },
    "Stamen Toner": {
        "tiles": "Stamen Toner",
        "attr": "Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
    }
}

# Harita oluştur
m = folium.Map(
    location=center_location,
    zoom_start=zoom_level,
    tiles=tiles_dict[map_type]["tiles"],
    attr=tiles_dict[map_type]["attr"],
    control_scale=True
)

# Türkiye'nin büyük şehirleri
cities = {
    "Ankara": [39.925533, 32.866287],
    "İstanbul": [41.0082, 28.9784],
    "İzmir": [38.4192, 27.1287],
    "Antalya": [36.8969, 30.7133],
    "Bursa": [40.1885, 29.0610],
    "Adana": [37.0000, 35.3213],
    "Konya": [37.8746, 32.4932],
    "Trabzon": [41.0027, 39.7168],
    "Gaziantep": [37.0662, 37.3833],
    "Diyarbakır": [37.9144, 40.2306]
}

# Her şehir için marker ekle
if show_markers:
    # Kümeleyici ekle
    from folium.plugins import MarkerCluster
    marker_cluster = MarkerCluster(name="Şehirler").add_to(m)
    
    for city, coords in cities.items():
        # Popup içeriği
        popup_text = f"""
        <div style="font-family: Arial, sans-serif; width: 150px; text-align: center">
            <h4 style="margin-bottom: 5px">{city}</h4>
            <p style="margin-top: 0">{coords[0]:.4f}, {coords[1]:.4f}</p>
        </div>
        """
        
        # Marker ekle
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_text, max_width=200),
            tooltip=city,
            icon=folium.Icon(icon="home", prefix="fa")
        ).add_to(marker_cluster)

# Harita eklentileri
if show_measure:
    MeasureControl(
        position="bottomright",
        primary_length_unit="kilometers",
        secondary_length_unit="miles",
        primary_area_unit="sqmeters",
        secondary_area_unit="acres"
    ).add_to(m)

if show_locate:
    from folium.plugins import LocateControl
    LocateControl(
        position="topright",
        strings={"title": "Konumumu bul"},
        icon="fa fa-map-marker"
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

# Tam ekran kontrolü ekle
Fullscreen(
    position="topright",
    title="Tam ekrana geç",
    title_cancel="Tam ekrandan çık",
    force_separate_button=True
).add_to(m)

# Fare koordinatları
MousePosition(
    position="bottomleft",
    separator=" | ",
    prefix="Koordinatlar:",
    num_digits=6
).add_to(m)

# Katman kontrolü
folium.LayerControl(collapsed=False).add_to(m)

# Haritayı Streamlit'e göster
map_data = st_folium(
    m, 
    width=None,  # Genişliği otomatik olarak ayarla
    height=600,   # Dengeli bir yükseklik
    returned_objects=["last_clicked"]
)

# Harita etkileşimi bilgisi
if map_data["last_clicked"]:
    st.info(f"Son tıklanan konum: {map_data['last_clicked']['lat']:.6f}, {map_data['last_clicked']['lng']:.6f}")

# Alt bilgi
st.markdown("---")
st.markdown("Bu harita uygulaması Streamlit ve Folium kütüphaneleri kullanılarak geliştirilmiştir. © 2025")