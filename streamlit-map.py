import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests
import json
import random

# Sayfa konfigürasyonu - Tam ekran için
st.set_page_config(
    page_title="İnteraktif Harita Uygulaması",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS ile tam ekran harita
st.markdown("""
<style>
    .main > div {
        padding-top: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .main .block-container {
        max-width: 100%;
        width: 100%;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Harita container stilini düzenle */
    .folium-map {
        width: 100%;
        height: 90vh;
        z-index: 0;
    }
</style>
""", unsafe_allow_html=True)

# Uygulamanın başlığı - Daha kısa ve minimal tutuyoruz
st.title('İnteraktif Web Harita Uygulaması')

# Yan menü
with st.sidebar:
    st.header('Harita Ayarları')

    # Harita tipi seçeneği
    map_type = st.selectbox(
        'Harita tipi:',
        ('OpenStreetMap', 'Stamen Terrain', 'Stamen Toner', 'CartoDB positron')
    )

    # Varsayılan konum (Türkiye için)
    default_location = [39.925533, 32.866287]  # Ankara

    # Başlangıç zoom seviyesi
    zoom_level = st.slider('Zoom seviyesi', 1, 18, 6)

    # Kullanıcıdan konum seçimi
    location_option = st.radio(
        'Konum:',
        ('Ankara (Varsayılan)', 'Kendi konumum')
    )

    if location_option == 'Kendi konumum':
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input('Enlem', value=default_location[0], format="%.6f")
        with col2:
            lon = st.number_input('Boylam', value=default_location[1], format="%.6f")
        
        center_location = [lat, lon]
    else:
        center_location = default_location

    # Veri ekleme seçeneği
    data_option = st.radio(
        'Veri:',
        ('Şehir Noktaları', 'Kendi Verilerim', 'API Verileri', 'Sadece Harita')
    )

    # Görünürlük ayarı
    show_controls = st.checkbox('Harita kontrolleri', value=True)
    
    # Tam ekran butonu
    if st.button('🔍 Gerçek Tam Ekran'):
        st.markdown("""
        <script>
            var elem = document.documentElement;
            function openFullscreen() {
                if (elem.requestFullscreen) {
                    elem.requestFullscreen();
                } else if (elem.webkitRequestFullscreen) { /* Safari */
                    elem.webkitRequestFullscreen();
                } else if (elem.msRequestFullscreen) { /* IE11 */
                    elem.msRequestFullscreen();
                }
            }
            openFullscreen();
        </script>
        """, unsafe_allow_html=True)

# Harita oluşturma fonksiyonu
def create_map(center, zoom, tiles):
    m = folium.Map(
        location=center, 
        zoom_start=zoom, 
        tiles=tiles,
        control_scale=True,
        attributionControl=False if not show_controls else True,
        zoomControl=show_controls
    )
    return m

# Haritayı oluştur
m = create_map(center_location, zoom_level, map_type)

# Örnek veri oluştur
if data_option == 'Şehir Noktaları':
    # Türkiye'nin büyük şehirleri
    cities = {
        'İstanbul': [41.0082, 28.9784],
        'Ankara': [39.9334, 32.8597],
        'İzmir': [38.4192, 27.1287],
        'Antalya': [36.8969, 30.7133],
        'Bursa': [40.1885, 29.0610],
        'Adana': [37.0000, 35.3213],
        'Konya': [37.8746, 32.4932],
        'Trabzon': [41.0027, 39.7168],
        'Gaziantep': [37.0662, 37.3833],
        'Diyarbakır': [37.9144, 40.2306]
    }
    
    # Rastgele değerler oluştur (örneğin nüfus verisi)
    data = []
    for city, coords in cities.items():
        population = random.randint(500000, 15000000)
        data.append({
            'Şehir': city,
            'Enlem': coords[0],
            'Boylam': coords[1],
            'Nüfus': population
        })
    
    # DataFrame oluştur
    df = pd.DataFrame(data)
    
    # Mini veri paneli - daha kompakt ve soldaki haritaya bindirme
    with st.expander("📊 Veri Tablosu", expanded=False):
        st.dataframe(df, height=250)
    
    # Her şehir için marker ekle
    for _, row in df.iterrows():
        # Marker boyutunu nüfusa göre ayarla
        radius = (row['Nüfus'] / 15000000) * 25 + 5
        
        # Popup içeriği
        popup_text = f"""
        <b>{row['Şehir']}</b><br>
        Nüfus: {row['Nüfus']:,}
        """
        
        # Marker ekle
        folium.CircleMarker(
            location=[row['Enlem'], row['Boylam']],
            radius=radius,
            popup=popup_text,
            tooltip=row['Şehir'],
            fill=True,
            fill_color='red',
            color='red',
            fill_opacity=0.6
        ).add_to(m)

elif data_option == 'Kendi Verilerim':
    with st.sidebar:
        st.info('CSV dosyanızda "Şehir", "Enlem", "Boylam" sütunları olmalıdır.')
        
        uploaded_file = st.file_uploader("CSV dosyanızı yükleyin", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Gerekli sütunları kontrol et
                required_columns = ['Şehir', 'Enlem', 'Boylam']
                if all(col in df.columns for col in required_columns):
                    # Veri ön izleme
                    with st.expander("📊 Veri Tablosu", expanded=False):
                        st.dataframe(df, height=250)
                    
                    # Her nokta için marker ekle
                    for _, row in df.iterrows():
                        popup_text = f"<b>{row['Şehir']}</b>"
                        
                        # Eğer ek sütunlar varsa, popup'a ekle
                        for col in df.columns:
                            if col not in required_columns:
                                popup_text += f"<br>{col}: {row[col]}"
                        
                        # Marker ekle
                        folium.Marker(
                            location=[row['Enlem'], row['Boylam']],
                            popup=popup_text,
                            tooltip=row['Şehir']
                        ).add_to(m)
                else:
                    st.error('CSV dosyanızda gerekli sütunlar eksik. "Şehir", "Enlem" ve "Boylam" sütunları olmalıdır.')
            except Exception as e:
                st.error(f'Dosya yüklenirken bir hata oluştu: {e}')

elif data_option == 'API Verileri':
    # Online veri kaynağı seçimi
    with st.sidebar:
        api_option = st.selectbox(
            'Veri kaynağı:',
            ('Deprem Verileri', 'Hava Durumu', 'İlgi Noktaları')
        )
    
    if api_option == 'Deprem Verileri':
        # Bir küçük bilgi kutusu ile deprem verilerini gösterebiliriz
        info_col1, info_col2 = st.columns([1, 3])
        with info_col1:
            st.markdown("### 🌍 Depremler")
        with info_col2:
            st.markdown("Son 24 saat içindeki M2.5+ depremler")
        
        # API'den veri çekme işlemi
        try:
            with st.spinner('Deprem verileri yükleniyor...'):
                # Gerçek projede doğru API kullanılmalıdır
                url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
                response = requests.get(url)
                
                if response.status_code == 200:
                    earthquake_data = response.json()
                    
                    # Verileri DataFrame'e dönüştürme
                    earthquakes = []
                    for feature in earthquake_data['features']:
                        prop = feature['properties']
                        geo = feature['geometry']['coordinates']
                        earthquakes.append({
                            'Yer': prop.get('place', 'Bilinmiyor'),
                            'Enlem': geo[1],
                            'Boylam': geo[0],
                            'Derinlik': geo[2],
                            'Büyüklük': prop.get('mag', 0),
                            'Zaman': pd.to_datetime(prop.get('time', 0), unit='ms')
                        })
                    
                    df = pd.DataFrame(earthquakes)
                    
                    # Veri ön izleme - mini ve açılır panel ile
                    with st.expander("📊 Deprem Listesi", expanded=False):
                        st.dataframe(df.sort_values(by='Büyüklük', ascending=False), height=300)
                    
                    # Depremleri haritada gösterme
                    for _, quake in df.iterrows():
                        # Büyüklüğe göre renk belirleme
                        if quake['Büyüklük'] >= 5.0:
                            color = 'red'
                        elif quake['Büyüklük'] >= 4.0:
                            color = 'orange'
                        else:
                            color = 'green'
                        
                        # Popup içeriği
                        popup_text = f"""
                        <b>{quake['Yer']}</b><br>
                        Büyüklük: {quake['Büyüklük']}<br>
                        Derinlik: {quake['Derinlik']} km<br>
                        Zaman: {quake['Zaman']}
                        """
                        
                        # Deprem marker'ı ekleme
                        folium.CircleMarker(
                            location=[quake['Enlem'], quake['Boylam']],
                            radius=quake['Büyüklük'] * 2,  # Büyüklük ile orantılı
                            popup=popup_text,
                            tooltip=f"M{quake['Büyüklük']} - {quake['Yer']}",
                            fill=True,
                            fill_color=color,
                            color=color,
                            fill_opacity=0.7
                        ).add_to(m)
                    
                    # Mini bilgi kutusu - sağ üst köşede
                    stat_box = folium.Element('''
                    <div style="
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        z-index: 999;
                        background-color: white;
                        padding: 10px;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.3);
                        font-family: Arial, sans-serif;
                    ">
                        <strong>Deprem İstatistikleri:</strong><br>
                        Toplam: {} deprem<br>
                        En büyük: M{:.1f}<br>
                        M5.0+: {} deprem<br>
                        M4.0+: {} deprem
                    </div>
                    '''.format(
                        len(df),
                        df['Büyüklük'].max(),
                        len(df[df['Büyüklük'] >= 5.0]),
                        len(df[df['Büyüklük'] >= 4.0])
                    ))
                    m.get_root().html.add_child(stat_box)
                else:
                    st.error(f"API'den veri alınamadı. Durum kodu: {response.status_code}")
        except Exception as e:
            st.error(f"Veri çekerken bir hata oluştu: {e}")
    
    elif api_option == 'Hava Durumu':
        info_col1, info_col2 = st.columns([1, 3])
        with info_col1:
            st.markdown("### ☁️ Hava Durumu")
        with info_col2:
            st.markdown("Türkiye'deki büyük şehirlerin güncel hava durumu")
            
        # Örnek şehirler
        cities = {
            'İstanbul': [41.0082, 28.9784],
            'Ankara': [39.9334, 32.8597],
            'İzmir': [38.4192, 27.1287],
            'Antalya': [36.8969, 30.7133],
            'Bursa': [40.1885, 29.0610]
        }
        
        # Örnek hava durumu verileri
        weather_data = []
        for city, coords in cities.items():
            # Gerçek bir projede API'den gelen veriler kullanılır
            temp = random.randint(10, 35)
            conditions = random.choice(['Güneşli', 'Bulutlu', 'Yağmurlu', 'Karlı'])
            
            weather_data.append({
                'Şehir': city,
                'Enlem': coords[0],
                'Boylam': coords[1],
                'Sıcaklık': temp,
                'Durum': conditions
            })
        
        weather_df = pd.DataFrame(weather_data)
        with st.expander("📊 Hava Durumu Verileri", expanded=False):
            st.dataframe(weather_df)
        
        # Hava durumu verilerini haritada gösterme
        for _, weather in weather_df.iterrows():
            # Sıcaklığa göre renk belirleme
            if weather['Sıcaklık'] >= 25:
                color = 'red'
            elif weather['Sıcaklık'] >= 15:
                color = 'orange'
            else:
                color = 'blue'
            
            # Hava durumu simgesi
            icon = 'cloud' if weather['Durum'] == 'Bulutlu' else 'info-sign'
            
            # Popup içeriği
            popup_text = f"""
            <b>{weather['Şehir']}</b><br>
            Sıcaklık: {weather['Sıcaklık']}°C<br>
            Durum: {weather['Durum']}
            """
            
            # Marker ekleme
            folium.Marker(
                location=[weather['Enlem'], weather['Boylam']],
                popup=popup_text,
                tooltip=f"{weather['Şehir']}: {weather['Sıcaklık']}°C",
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
    
    elif api_option == 'İlgi Noktaları':
        info_col1, info_col2 = st.columns([1, 3])
        with info_col1:
            st.markdown("### 🏙️ İlgi Noktaları")
        with info_col2:
            st.markdown("Seçilen konumun çevresindeki önemli noktalar")
            
        # İlgi noktası tipi seçimi
        with st.sidebar:
            poi_type = st.selectbox(
                'İlgi noktası tipi:',
                ('Restoranlar', 'Oteller', 'Müzeler', 'Parklar')
            )
        
        # Örnek ilgi noktaları
        try:
            # Örnek veri
            pois = []
            poi_count = random.randint(5, 15)
            
            for i in range(poi_count):
                lat_offset = random.uniform(-0.05, 0.05)
                lng_offset = random.uniform(-0.05, 0.05)
                
                poi_name = f"{poi_type[:-1]} {i+1}"
                if poi_type == 'Restoranlar':
                    poi_name = f"Restoran {i+1}"
                    rating = round(random.uniform(3.0, 5.0), 1)
                    additional_info = f"Mutfak: {random.choice(['Türk', 'İtalyan', 'Çin', 'Meksika'])}"
                elif poi_type == 'Oteller':
                    poi_name = f"{random.choice(['Grand', 'Royal', 'Palace', 'City'])} Hotel"
                    rating = round(random.uniform(3.0, 5.0), 1)
                    additional_info = f"Yıldız: {random.randint(3, 5)}"
                elif poi_type == 'Müzeler':
                    poi_name = f"{random.choice(['Tarih', 'Sanat', 'Arkeoloji', 'Modern'])} Müzesi"
                    rating = round(random.uniform(3.5, 5.0), 1)
                    additional_info = f"Tür: {random.choice(['Tarih', 'Sanat', 'Arkeoloji', 'Bilim'])}"
                else:  # Parklar
                    poi_name = f"{random.choice(['Millet', 'Gençlik', 'Atatürk', 'Kültür'])} Parkı"
                    rating = round(random.uniform(3.8, 5.0), 1)
                    additional_info = f"Alan: {random.randint(5, 100)} dönüm"
                
                pois.append({
                    'İsim': poi_name,
                    'Enlem': center_location[0] + lat_offset,
                    'Boylam': center_location[1] + lng_offset,
                    'Puan': rating,
                    'Bilgi': additional_info
                })
            
            poi_df = pd.DataFrame(pois)
            with st.expander(f"📊 {poi_type} Listesi", expanded=False):
                st.dataframe(poi_df)
            
            # İlgi noktaları kümesi oluştur
            marker_cluster = folium.plugins.MarkerCluster(name=poi_type).add_to(m)
            
            # İlgi noktalarını haritada gösterme
            for _, poi in poi_df.iterrows():
                # İlgi noktası tipine göre simge belirleme
                if poi_type == 'Restoranlar':
                    icon = folium.Icon(color='red', icon='cutlery', prefix='fa')
                elif poi_type == 'Oteller':
                    icon = folium.Icon(color='blue', icon='hotel', prefix='fa')
                elif poi_type == 'Müzeler':
                    icon = folium.Icon(color='green', icon='institution', prefix='fa')
                else:  # Parklar
                    icon = folium.Icon(color='green', icon='tree', prefix='fa')
                
                # Popup içeriği
                popup_text = f"""
                <b>{poi['İsim']}</b><br>
                Puan: {poi['Puan']}/5.0<br>
                {poi['Bilgi']}
                """
                
                # Marker ekleme
                folium.Marker(
                    location=[poi['Enlem'], poi['Boylam']],
                    popup=popup_text,
                    tooltip=poi['İsim'],
                    icon=icon
                ).add_to(marker_cluster)
            
        except Exception as e:
            st.error(f"Veri gösterilirken bir hata oluştu: {e}")

# Ekstra harita eklentileri
folium.plugins.Fullscreen(
    position="topright",
    title="Tam Ekran",
    title_cancel="Çık",
    force_separate_button=True
).add_to(m)

folium.plugins.LocateControl(
    position="topright",
    strings={"title": "Konumumu bul"},
    icon="fa fa-map-marker"
).add_to(m)

# Harita ölçeği
folium.plugins.MeasureControl(
    position="bottomleft",
    primary_length_unit="meters",
    secondary_length_unit="kilometers",
    primary_area_unit="sqmeters",
    secondary_area_unit="hectares"
).add_to(m)

# Harita katmanları ekle
folium.LayerControl(collapsed=True).add_to(m)

# Haritayı göster (tam ekran)
folium_static(m, width=1500, height=750)

# Uygulamayla ilgili bilgiler
with st.sidebar:
    st.markdown('---')
    st.info('Bu harita uygulaması, Streamlit ve Folium kullanılarak geliştirilmiştir.')
    
    # Kaynak kod bağlantısı
    st.markdown("[Kaynak Kodu Görüntüle](https://github.com/)")
    
    # Telif hakkı
    st.markdown("© 2025 Web Map Project")