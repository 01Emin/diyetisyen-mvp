import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SAYFA AYARLARI (Geniş Ekran ve Sekme Başlığı)
st.set_page_config(page_title="Dijital Diyetisyen", page_icon="🍏", layout="wide")

# 2. GİZLİ ŞİFREYİ ALMA VE MODELİ BAŞLATMA
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. ŞIK ÜST BANNER TASARIMI (CSS ile)
st.markdown("""
    <div style='background-color:#2c3e50;padding:20px;border-radius:10px;margin-bottom:25px;'>
        <h1 style='color:white;margin:0;'>🍏 Dijital Diyetisyen Asistanı</h1>
        <p style='color:#cbd5e0;margin:5px 0 0 0;'>Yapay Zeka Destekli Klinik Beslenme Analizi</p>
    </div>
""", unsafe_allow_html=True)

# 4. SEKMELİ YAPI (TABS)
with tab2:
st.subheader("Uzman Diyetisyeninizle Görüşün")

# --- BİRİNCİ SEKME: FOTOĞRAF ANALİZİ ---
with tab1:
    # Ekranı yan yana iki eşit kolona bölüyoruz
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Öğün Fotoğrafı Yükle")
        uploaded_file = st.file_uploader("Yemeğinizin fotoğrafını sürükleyin veya seçin", type=["jpg", "png", "jpeg"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Yüklenen Öğün", use_container_width=True)

    with col2:
        st.subheader("2. Analiz ve Rapor")
        if uploaded_file is not None:
            if st.button("🔍 Besin Değerlerini Analiz Et", use_container_width=True):
                with st.spinner("Yapay zeka öğününüzü inceliyor..."):
                    # Yapay zekaya giden özel komut
                    prompt = "Bir diyetisyen gibi davran. Bu fotoğraftaki yemeği detaylı analiz et. Tahmini kalori, protein, karbonhidrat ve yağ oranlarını ver. Sonuna beni motive edecek kısa bir tavsiye ekle."
                    response = model.generate_content([prompt, image])
                    
                    # Sonucu yeşil bir onay kutusuyla göster
                    st.success("Analiz Tamamlandı!")
                    st.markdown(response.text)
                    
                    # Görsel Şov: Temsili Metrik Kartları
                    st.divider()
                    st.markdown("### 📊 Hızlı Özet")
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="Tahmini Porsiyon", value="1 Tabak", delta="Standart")
                    m2.metric(label="Sağlık Skoru", value="A Sınıfı", delta="Çok İyi")
                    m3.metric(label="Doyuruculuk", value="Yüksek", delta="+ Lif")
        else:
            st.info("👈 Analize başlamak için lütfen sol taraftan bir yemek fotoğrafı yükleyin.")

# --- İKİNCİ SEKME: CHATBOT (Gelecek Aşama) ---
with tab2:
    st.subheader("Diyetisyen Chatbot")
    with tab2:
    st.subheader("Uzman Diyetisyeninizle Görüşün")
    st.markdown("Beslenme, diyet listeleri veya kalori hesabı hakkında her şeyi sorabilirsiniz.")
    
    # Sohbet hafızasını (session_state) başlatma
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Gemini'nin chat oturumunu başlatıyoruz ki önceki mesajları hatırlasın
        st.session_state.chat_session = model.start_chat(history=[])

    # Geçmiş mesajları ekranda gösterme döngüsü
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kullanıcıdan yeni mesaj alma
    if user_prompt := st.chat_input("Sorunuzu buraya yazın (Örn: Aralıklı oruç nedir?)..."):
        
        # Kullanıcı mesajını ekrana ve hafızaya ekle
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Yapay zekanın cevabını al ve ekrana yazdır
        with st.chat_message("assistant"):
            with st.spinner("Diyetisyeniniz yazıyor..."):
                # Diyetisyen rolüne girmesi için gizli bir talimat ekliyoruz
                bot_instruction = f"Sen tecrübeli ve motive edici bir klinik diyetisyensin. Sadece beslenme, diyet ve sağlık konularında cevap ver. Kullanıcının sorusu: {user_prompt}"
                response = st.session_state.chat_session.send_message(bot_instruction)
                st.markdown(response.text)
                
        # Yapay zekanın cevabını hafızaya ekle
        st.session_state.messages.append({"role": "assistant", "content": response.text})
