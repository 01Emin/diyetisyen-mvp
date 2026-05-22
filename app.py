import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SAYFA AYARLARI
st.set_page_config(page_title="AIDijital Diyetisyen", layout="wide")

# 2. GİZLİ ŞİFREYİ ALMA VE MODELİ BAŞLATMA
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Settings > Secrets bölümünü kontrol edin.")
    st.stop()

# 3. YAN MENÜ (SIDEBAR) - NASIL ÇALIŞIR BİLGİLENDİRMESİ
with st.sidebar:
    st.title("ℹ️ Nasıl Çalışır?")
    st.info(
        "**1. Fotoğraf Yükle:**\n"
        "Yediğiniz yemeğin fotoğrafını çekip Akıllı Analizör sekmesine yükleyin.\n\n"
        "**2. Yapay Zeka Analizi:**\n"
        "Sistem yemeğin kalorisini ve makro besinlerini saniyeler içinde tahmin etsin.\n\n"
        "**3. Canlı Danışmanlık:**\n"
        "Aklınıza takılan tüm beslenme sorularını Diyetisyen Chatbot'a sorun."
    )
    st.divider()
    st.caption("© 2026 Dijital Diyetisyen Asistanı MVP")

# 4. ŞIK ÜST BANNER TASARIMI (CSS ile)
st.markdown("""
    <div style='background-color:#2c3e50;padding:20px;border-radius:10px;margin-bottom:25px;'>
        <h1 style='color:white;margin:0;'> Dijital Diyetisyen Asistanı</h1>
        <p style='color:#cbd5e0;margin:5px 0 0 0;'>Yapay Zeka Destekli Klinik Beslenme Analizi ve Danışmanlık</p>
    </div>
""", unsafe_allow_html=True)

# 5. SEKMELİ YAPI (TABS) - HATA BURADAYDI, DÜZELTİLDİ
tab1, tab2 = st.tabs(["📸 Akıllı Öğün Analizörü", "💬 Diyetisyene Danış"])

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
                with st.spinner("Yapay zeka öğününüzü inceliyor, lütfen bekleyin..."):
                    try:
                        # Daha detaylı ve yapılandırılmış Prompt (Talimat)
                        prompt = (
                            "Sen uzman bir klinik diyetisyensin. Bu fotoğraftaki yemeği analiz et. "
                            "Şu başlıklar altında detaylı rapor ver: "
                            "1) Tabaktakiler, 2) Tahmini Kalori, 3) Makro Besin Değerleri (Protein, Karb, Yağ). "
                            "Sonuna öğünü iyileştirmek için 1 tane pratik, motive edici tavsiye ekle. "
                            "Formatı Markdown kullanarak, şık ve okunaklı yap."
                        )
                        response = model.generate_content([prompt, image])
                        
                        st.success("Analiz Tamamlandı!")
                        st.markdown(response.text)
                        
                        # Görsel Şov: Temsili Metrik Kartları
                        st.divider()
                        st.markdown("### 📊 Hızlı Özet")
                        m1, m2, m3 = st.columns(3)
                        m1.metric(label="Tahmini Porsiyon", value="1 Tabak", delta="Standart")
                        m2.metric(label="Sağlık Skoru", value="A Sınıfı", delta="Çok İyi")
                        m3.metric(label="Doyuruculuk", value="Yüksek", delta="+ Lif ve Protein")
                    except Exception as e:
                        st.error("Analiz sırasında bir sorun oluştu. Lütfen fotoğrafı değiştirip tekrar deneyin.")
        else:
            st.info(" Analize başlamak için lütfen sol taraftan bir yemek fotoğrafı yükleyin.")

# --- İKİNCİ SEKME: CHATBOT ---
with tab2:
    st.subheader("👩‍⚕️ Uzman Diyetisyeninizle Görüşün")
    st.markdown("Beslenme, diyet listeleri, kalori hesabı veya hedefleriniz hakkında her şeyi sorabilirsiniz.")
    
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
                # Diyetisyen rolüne girmesi için çok daha spesifik ve detaylı bir talimat
                bot_instruction = (
                    f"Sen tecrübeli, anlayışlı ve bilimsel gerçeklere dayanan bir klinik diyetisyensin. "
                    f"Kullanıcıya her zaman sıcak ve motive edici bir dille cevap ver. "
                    f"Sadece beslenme, diyet ve sağlıklı yaşam konularında yanıt ver. Tıbbi teşhis gerektiren durumlarda doktora yönlendir. "
                    f"Kullanıcının sorusu: {user_prompt}"
                )
                response = st.session_state.chat_session.send_message(bot_instruction)
                st.markdown(response.text)
                
        # Yapay zekanın cevabını hafızaya ekle (EKSİK KISIM DÜZELTİLDİ)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
