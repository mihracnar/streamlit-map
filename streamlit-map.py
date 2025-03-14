import streamlit as st
from streamlit_option_menu import option_menu
import leafmap.leafmap as leafmap

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
    
    /* Leafmap yüksekliği */
    iframe {
        height: 96vh !important;
        width: 100% !important;
    }
    
    .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    /* Kontrol paneli */
    .control-panel {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        max-width: 300px;
    }
</style>
""", unsafe_allow_html=True)

# Basemap seçenekleri
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
    basemap = st.selectbox("Harita Türü:", basemap_options, index=0)
    
    # Zoom seviyesi
    zoom = st.slider("Zoom Seviyesi:", 1, 20, 6)
    
    # Ek Katmanlar
    st.subheader("Katmanlar")
    show_dem = st.checkbox("Yükseklik Modeli", False)
    show_buildings = st.checkbox("Binalar", False)
    show_labels = st.checkbox("Yer Adları", True)
    
    # Ölçüm araçları
    st.subheader("Araçlar")
    measurement = st.checkbox("Ölçüm Araçları", True)
    drawing = st.checkbox("Çizim Araçları", True)
    fullscreen = st.checkbox("Tam Ekran Kontrolü", True)
    layercontrol = st.checkbox("Katman Kontrolü", True)
    
    # Veri ekleme
    st.subheader("Veri")
    data_option = st.radio(
        "Veri Kaynağı:",
        ["Yok", "Depremler", "Ülke Sınırları", "3D Terrain"]
    )
    
    if data_option == "Depremler":
        days = st.slider("Son kaç gün:", 1, 30, 7)
        magnitude = st.slider("Min büyüklük:", 2.5, 8.0, 4.5, 0.5)
    
    elif data_option == "Ülke Sınırları":
        country = st.selectbox(
            "Ülke:",
            ["Turkey", "United States", "Germany", "France", "Italy", "Spain", "Japan", "China"]
        )
    
    elif data_option == "3D Terrain":
        exaggeration = st.slider("Yükseltme faktörü:", 1, 10, 3)
    
    # Haritayı sıfırla
    if st.button("🔄 Haritayı Sıfırla", use_container_width=True):
        st.experimental_rerun()

# Harita container - Tam ekran için
map_container = st.container()

with map_container:
    # Leafmap haritası
    m = leafmap.Map(
        center=[39.925533, 32.866287],  # Ankara
        zoom=zoom,
        draw_control=drawing,
        measure_control=measurement,
        fullscreen_control=fullscreen,
        search_control=False,
        scale=True,
        attribution_control=True
    )
    
    # Basemap'i ayarla
    if basemap in ["SATELLITE", "ROADMAP", "TERRAIN", "HYBRID"]:
        m.add_basemap(f"Google {basemap}")
    else:
        m.add_basemap(basemap)
    
    # Ek katmanlar
    if show_dem:
        m.add_basemap("OpenTopoMap")
    
    if show_labels and not "Google" in basemap and not "Stamen" in basemap:
        m.add_basemap("CartoDB.PositronOnlyLabels")
    
    if show_buildings:
        m.add_cog_layer(
            "https://ecmwf-ara-processing.s3.amazonaws.com/ecmwf_processed/c3s/building-heights/global/2018/global_building_heights.tif", 
            name="Global Building Heights"
        )
    
    # Verileri Ekle
    if data_option == "Depremler":
        m.add_earthquake(magnitude, days, name=f"M{magnitude}+ Son {days} Gün Depremler")
    
    elif data_option == "Ülke Sınırları":
        m.add_geojson(
            f"https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson",
            layer_name="Ülke Sınırları",
            style={
                "color": "blue",
                "weight": 2,
                "fillOpacity": 0.1
            },
            hover_style={
                "fillOpacity": 0.7,
                "fillColor": "yellow"
            }
        )
    
    elif data_option == "3D Terrain":
        m.add_3d_terrain(exaggeration=exaggeration)
    
    # Katman kontrolü
    if layercontrol:
        m.add_layer_control()
    
    # Tam ekran harita
    m.to_streamlit(height=800)

# Mini panel üstte sağda (opsiyonel)
st.markdown(
    f"""
    <div class="control-panel">
        <h4>Harita Durumu:</h4>
        <p>Konum: Ankara, Türkiye</p>
        <p>Zoom: {zoom}</p>
        <p>Harita: {basemap}</p>
    </div>
    """,
    unsafe_allow_html=True
)