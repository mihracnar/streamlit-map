import streamlit as st
import folium
from streamlit_folium import st_folium

# Sayfa konfigürasyonu - Tam Ekran için
st.set_page_config(
    page_title="Basit Tam Ekran Harita",
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
    [data-testid="stFormSubmitButton"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Yan panel (gizlenebilir)
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
    
    show_markers = st.checkbox("Şehir noktalarını göster", True)
    
    # Yenileme butonu
    if st.button("🔄 Haritayı Yenile", use_container_width=True):
        st.rerun()

# Ana container - harita için
st.markdown("## Tam Ekran Harita")

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

# Şehir markerları ekle
if show_markers:
    # Türkiye'nin büyük şehirleri
    cities = {
        "Ankara": [39.925533, 32.866287],
        "İstanbul": [41.0082, 28.9784],
        "İzmir": [38.4192, 27.1287],
        "Antalya": [36.8969, 30.7133],
        "Bursa": [40.1885, 29.0610]
    }
    
    # Her şehir için marker ekle
    for city, coords in cities.items():
        folium.Marker(
            location=coords,
            popup=city,
            tooltip=city
        ).add_to(m)

# Tam ekran kontrolü ekle
folium.plugins.Fullscreen(
    position="topright",
    title="Tam ekrana geç",
    title_cancel="Tam ekrandan çık",
    force_separate_button=True
).add_to(m)

# Haritayı Streamlit'e göster
map_data = st_folium(m, width=1400, height=700)

# Harita etkileşimi bilgisi
if map_data["last_clicked"]:
    st.success(f"Son tıklanan konum: {map_data['last_clicked']['lat']:.4f}, {map_data['last_clicked']['lng']:.4f}")