import streamlit as st
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
        height: 95vh !important;
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

# Oturum durumu (ayarları saklamak için)
if 'basemap' not in st.session_state:
    st.session_state.basemap = "OpenStreetMap"
if 'zoom' not in st.session_state:
    st.session_state.zoom = 6
if 'data_option' not in st.session_state:
    st.session_state.data_option = "Yok"

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
    basemap = st.selectbox("Harita Türü:", basemap_options, index=basemap_options.index(st.session_state.basemap))
    st.session_state.basemap = basemap
    
    # Zoom seviyesi
    zoom = st.slider("Zoom Seviyesi:", 1, 20, st.session_state.zoom)
    st.session_state.zoom = zoom
    
    # Ek Katmanlar
    st.subheader("Katmanlar")
    show_dem = st.checkbox("Yükseklik Modeli", False)
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
        ["Yok", "Depremler", "Ülke Sınırları"],
        index=["Yok", "Depremler", "Ülke Sınırları"].index(st.session_state.data_option)
    )
    st.session_state.data_option = data_option
    
    if data_option == "Depremler":
        if 'eq_days' not in st.session_state:
            st.session_state.eq_days = 7
        if 'eq_magnitude' not in st.session_state:
            st.session_state.eq_magnitude = 4.5
            
        days = st.slider("Son kaç gün:", 1, 30, st.session_state.eq_days)
        magnitude = st.slider("Min büyüklük:", 2.5, 8.0, st.session_state.eq_magnitude, 0.5)
        
        st.session_state.eq_days = days
        st.session_state.eq_magnitude = magnitude
    
    elif data_option == "Ülke Sınırları":
        if 'country' not in st.session_state:
            st.session_state.country = "Turkey"
            
        country = st.selectbox(
            "Ülke:",
            ["Turkey", "United States", "Germany", "France", "Italy", "Spain", "Japan", "China"],
            index=["Turkey", "United States", "Germany", "France", "Italy", "Spain", "Japan", "China"].index(st.session_state.country)
        )
        st.session_state.country = country
    
    # Haritayı sıfırla (modern Streamlit API kullanıyor)
    if st.button("🔄 Haritayı Sıfırla", use_container_width=True):
        # Modern Streamlit için rerun
        st.session_state.basemap = "OpenStreetMap"
        st.session_state.zoom = 6
        st.session_state.data_option = "Yok"
        st.rerun()  # experimental_rerun yerine modern API

# Ana container - harita için
map_container = st.container()

with map_container:
    try:
        # Leafmap haritası oluştur
        m = leafmap.Map(
            center=[39.925533, 32.866287],  # Ankara
            zoom=zoom,
            draw_control=drawing,
            measure_control=measurement,
            fullscreen_control=fullscreen,
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
        
        # Verileri Ekle
        if data_option == "Depremler":
            try:
                m.add_earthquake(st.session_state.eq_magnitude, st.session_state.eq_days, 
                                name=f"M{st.session_state.eq_magnitude}+ Son {st.session_state.eq_days} Gün Depremler")
            except Exception as e:
                st.warning(f"Deprem verileri eklenirken bir sorun oluştu. Hata: {e}")
        
        elif data_option == "Ülke Sınırları":
            try:
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
            except Exception as e:
                st.warning(f"Ülke sınırları eklenirken bir sorun oluştu. Hata: {e}")
        
        # Katman kontrolü
        if layercontrol:
            m.add_layer_control()
        
        # Haritayı gösterme denemeleri - farklı alternatifler sunuyor
        try:
            # İlk deneme - to_streamlit metodu
            m.to_streamlit(height=800)
        except Exception as e1:
            st.warning(f"Birincil harita gösterimi başarısız oldu. Alternatif yöntem deneniyor. Hata: {e1}")
            try:
                # İkinci deneme - daha eski API
                import folium
                from streamlit_folium import folium_static
                folium_map = m.to_folium()
                folium_static(folium_map, width=1400, height=800)
            except Exception as e2:
                st.error(f"Harita gösterimi başarısız. Hata: {e2}")
        
    except Exception as e:
        st.error(f"Leafmap hatası: {e}")
        st.info("Lütfen leafmap paketinin yüklü olduğundan emin olun: pip install leafmap")
        
        # Yedek çözüm olarak mesaj göster
        st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: #f8f9fa; border-radius: 10px;">
            <h2>Leafmap yüklenemedi</h2>
            <p>Leafmap kütüphanesinin kurulumu için terminal veya komut satırına şunu yazın:</p>
            <code>pip install leafmap</code>
            <p>veya requirements.txt dosyanıza "leafmap" ekleyin.</p>
        </div>
        """, unsafe_allow_html=True)