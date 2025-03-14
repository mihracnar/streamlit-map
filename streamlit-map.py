import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests
import json
import random

# Uygulama başlığı
st.title('İnteraktif Harita Uygulaması')
st.write('Bu uygulama ile coğrafi verileri görselleştirebilirsiniz.')

# Yan menü oluşturma
st.sidebar.header('Ayarlar')

# Harita tipi seçeneği
map_type = st.sidebar.selectbox(
    'Harita tipi seçin:',
    ('OpenStreetMap', 'Stamen Terrain', 'Stamen Toner', 'CartoDB positron')
)

# Varsayılan konum (Türkiye için)
default_location = [39.925533, 32.866287]  # Ankara

# Başlangıç zoom seviyesi
zoom_level = st.sidebar.slider('Zoom seviyesi', 1, 18, 6)

# Kullanıcıdan konum seçimi
location_option = st.sidebar.radio(
    'Konum seçimi:',
    ('Varsayılan konum (Ankara)', 'Kendi konumunuzu girin')
)

if location_option == 'Kendi konumunuzu girin':
    col1, col2 = st.sidebar.columns(2)
    with col1:
        lat = st.number_input('Enlem', value=default_location[0], format="%.6f")
    with col2:
        lon = st.number_input('Boylam', value=default_location[1], format="%.6f")
    
    center_location = [lat, lon]
else:
    center_location = default_location

# Veri ekleme seçeneği
data_option = st.sidebar.radio(
    'Veri seçimi:',
    ('Örnek noktalar', 'Kendi verilerinizi yükleyin', 'Online veri kaynağı', 'Hiç veri yok')
)

# Harita oluşturma fonksiyonu
def create_map(center, zoom, tiles):
    m = folium.Map(location=center, zoom_start=zoom, tiles=tiles)
    return m

# Haritayı başlat
m = create_map(center_location, zoom_level, map_type)

# Örnek veri oluştur
if data_option == 'Örnek noktalar':
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
    
    # Veri ön izleme
    st.subheader('Veri Önizleme')
    st.dataframe(df)
    
    # Her şehir için marker ekle
    for _, row in df.iterrows():
        # Marker boyutunu nüfusa göre ayarla (bir örnek olarak)
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
            fill=True,
            fill_color='red',
            color='red',
            fill_opacity=0.6
        ).add_to(m)

elif data_option == 'Kendi verilerinizi yükleyin':
    st.sidebar.info('CSV dosyanızda "Şehir", "Enlem", "Boylam" sütunları olmalıdır.')
    
    uploaded_file = st.sidebar.file_uploader("CSV dosyanızı yükleyin", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Gerekli sütunları kontrol et
            required_columns = ['Şehir', 'Enlem', 'Boylam']
            if all(col in df.columns for col in required_columns):
                # Veri ön izleme
                st.subheader('Veri Önizleme')
                st.dataframe(df)
                
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
                        popup=popup_text
                    ).add_to(m)
            else:
                st.error('CSV dosyanızda gerekli sütunlar eksik. "Şehir", "Enlem" ve "Boylam" sütunları olmalıdır.')
        except Exception as e:
            st.error(f'Dosya yüklenirken bir hata oluştu: {e}')

elif data_option == 'Online veri kaynağı':
    # Online veri kaynağı seçimi
    api_option = st.sidebar.selectbox(
        'Veri kaynağı seçin:',
        ('Deprem Verileri (Kandilli API)', 'Hava Durumu Verileri', 'OpenStreetMap POI Verileri')
    )
    
    if api_option == 'Deprem Verileri (Kandilli API)':
        st.subheader('Son Depremler (Kandilli Rasathanesi)')
        
        # API'den veri çekme işlemi
        try:
            # Kandilli Rasathanesi'nin resmi API'si olmadığı için açık bir veri kaynağı kullanıyorum
            # Bu örnek sadece gösterim amaçlıdır
            with st.spinner('Deprem verileri yükleniyor...'):
                # Bu URL değişebilir veya kullanılamaz olabilir - gerçek projede doğru API kullanılmalıdır
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
                    
                    # Veri ön izleme
                    st.dataframe(df)
                    
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
                            fill=True,
                            fill_color=color,
                            color=color,
                            fill_opacity=0.7
                        ).add_to(m)
                    
                    st.success(f"Toplam {len(df)} deprem görüntüleniyor")
                else:
                    st.error(f"API'den veri alınamadı. Durum kodu: {response.status_code}")
        except Exception as e:
            st.error(f"Veri çekerken bir hata oluştu: {e}")
    
    elif api_option == 'Hava Durumu Verileri':
        st.subheader('Türkiye Şehirleri Hava Durumu')
        st.info("Bu bölüm gerçek bir API entegrasyonu için hazırlanmıştır. Gerçek bir projede OpenWeatherMap, Visual Crossing veya diğer hava durumu API'leri kullanılabilir.")
        
        # Örnek şehirler
        cities = {
            'İstanbul': [41.0082, 28.9784],
            'Ankara': [39.9334, 32.8597],
            'İzmir': [38.4192, 27.1287],
            'Antalya': [36.8969, 30.7133],
            'Bursa': [40.1885, 29.0610]
        }
        
        # Örnek hava durumu verileri (gerçek bir API'den alınacak veriler)
        weather_data = []
        for city, coords in cities.items():
            # Burada gerçek bir API çağrısı yapılabilir
            # Örnek: response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={coords[0]}&lon={coords[1]}&appid={API_KEY}")
            
            # Örnek veri (gerçek projede API'den gelen veri kullanılır)
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
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
    
    elif api_option == 'OpenStreetMap POI Verileri':
        st.subheader('İlgi Noktaları (POI)')
        
        # İlgi noktası tipi seçimi
        poi_type = st.sidebar.selectbox(
            'İlgi noktası tipi:',
            ('Restoranlar', 'Oteller', 'Müzeler', 'Parklar')
        )
        
        st.info(f'Bu bölüm {poi_type} için Overpass API veya Nominatim API entegrasyonuyla kullanılabilir.')
        
        # Örnek olarak, seçilen merkez çevresinde ilgi noktaları gösterelim
        try:
            # Gerçek bir projede: 
            # url = f"https://nominatim.openstreetmap.org/search.php?q={poi_type}+near+{center_location[0]},{center_location[1]}&format=jsonv2"
            
            # Örnek veri
            pois = []
            poi_count = random.randint(5, 15)
            
            for i in range(poi_count):
                # Merkez etrafında rastgele noktalar (gerçek projede API'den gelen veriler)
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
            st.dataframe(poi_df)
            
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
                    icon=icon
                ).add_to(m)
            
            st.success(f"Toplam {len(poi_df)} adet {poi_type.lower()} görüntüleniyor")
        except Exception as e:
            st.error(f"Veri gösterilirken bir hata oluştu: {e}")

# Harita katmanları ekle
folium.LayerControl().add_to(m)

# Haritayı göster
st.subheader('İnteraktif Harita')
folium_static(m)

# Ek özellikler
st.subheader('Ek Bilgiler')
st.write("""
Bu uygulamayı geliştirmek için yapabilecekleriniz:
- Haritaya çizgi ve poligon ekleyebilirsiniz
- Farklı veri kaynakları kullanabilirsiniz
- Isı haritası (heatmap) ekleyebilirsiniz
- Gerçek zamanlı veri görselleştirebilirsiniz
- Coğrafi analizler yapabilirsiniz
""")

# Uygulama hakkında bilgi
st.sidebar.markdown('---')
st.sidebar.info('Bu uygulama Streamlit, Folium ve Pandas kullanılarak geliştirilmiştir.')