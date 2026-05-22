import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Aı Dijital Diyetisyen Asistanı - Dashboard", layout="wide")

# 2. GİZLİ ŞİFREYİ ALMA VE MODELİ BAŞLATMA
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Settings > Secrets bölümünü kontrol edin.")
    st.stop()

# 3. YAN MENÜ (SIDEBAR) - LOGOUT BUTONU
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if st.session_state.logged_in:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username.capitalize()}")
        st.caption(f"Rol: {st.session_state.role.capitalize()}")
        st.divider()
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.username = None
            st.rerun() # Sayfayı yenileyerek giriş ekranına döndür

# 4. GİRİŞ VE ROL MANTIĞI (LOGIN LOGIC)
if not st.session_state.logged_in:
    # Giriş Ekranı Tasarımı
    st.markdown("""
        <div style='background-color:#2c3e50;padding:20px;border-radius:10px;margin-bottom:25px;'>
            <h1 style='color:white;margin:0;'>🔐 ProNutri AI - Giriş Portalı</h1>
            <p style='color:#cbd5e0;margin:5px 0 0 0;'>Giriş yapmak için lütfen bilgilerinizi girin.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Oturum Aç")
            username_input = st.text_input("Kullanıcı Adı veya E-posta")
            password_input = st.text_input("Şifre", type="password")
            submitted = st.form_submit_submit("Giriş Yap", use_container_width=True)
            
            if submitted:
                # Sabit Şifreli Test Girişleri (Veritabanı Yokken)
                if username_input == "kullanici" and password_input == "user123":
                    st.session_state.logged_in = True
                    st.session_state.role = "kullanici"
                    st.session_state.username = username_input
                    st.success("Kullanıcı girişi başarılı!")
                    st.rerun()
                elif username_input == "diyetisyen" and password_input == "diet123":
                    st.session_state.logged_in = True
                    st.session_state.role = "diyetisyen"
                    st.session_state.username = username_input
                    st.success("Diyetisyen girişi başarılı!")
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop() # Giriş yapana kadar aşağıdaki kodları çalıştırma

# ==============================================================================
# 5. ANA UYGULAMA İÇERİĞİ (Giriş Yapıldıktan Sonra Çalışır)
# ==============================================================================

# 5a. ŞIK ÜST BANNER (Ortak)
st.markdown("""
    <div style='background-color:#2c3e50;padding:20px;border-radius:10px;margin-bottom:25px;'>
        <h1 style='color:white;margin:0;'>  Dijital Diyetisyen Aı  Dashboard</h1>
        <p style='color:#cbd5e0;margin:5px 0 0 0;'>Yapay Zeka Destekli Klinik Beslenme Portalı</p>
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5b. KULLANICI ROLÜ EKRANI
# ------------------------------------------------------------------------------
if st.session_state.role == "kullanici":
    tab1, tab2 = st.tabs(["📸 Akıllı Analizör", "💬 Diyetisyen Chatbot"])

    with tab1:
        st.subheader("📸 Yemeğinizin Fotoğrafını Analiz Edin")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Öğün fotoğrafını yükleyin...", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Yüklenen Öğün", use_container_width=True)

        with col2:
            if uploaded_file is not None:
                if st.button("🔍 Besin Değerlerini Analiz Et", use_container_width=True):
                    with st.spinner("Yapay zeka öğününüzü inceliyor..."):
                        prompt = (
                            "Sen uzman bir klinik diyetisyensin. Bu fotoğraftaki yemeği detaylı analiz et. "
                            "Tahmini kalori, protein, karbonhidrat ve yağ oranlarını madde madde ver. "
                            "Sonuna motive edici kısa bir tavsiye ekle. Markdown kullanarak formatla."
                        )
                        response = model.generate_content([prompt, image])
                        st.success("Analiz Tamamlandı!")
                        st.markdown(response.text)
                        
                        st.divider()
                        st.markdown("### 📊 Hızlı Özet")
                        m1, m2, m3 = st.columns(3)
                        m1.metric(label="Kalori", value="450 kcal", delta="+5%")
                        m2.metric(label="Protein", value="24g", delta="Hedef: 30g")
                        m3.metric(label="Sağlık Skoru", value="A Sınıfı", delta="Çok İyi")
            else:
                st.info("👈 Analize başlamak için lütfen sol taraftan bir yemek fotoğrafı yükleyin.")

    with tab2:
        st.subheader("💬 Diyetisyen Chatbot ile Görüşün")
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.chat_session = model.start_chat(history=[])

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_prompt := st.chat_input("Sorunuzu buraya yazın (Örn: Bugün ne yemeliyim?)..."):
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)

            with st.chat_message("assistant"):
                with st.spinner("Diyetisyeniniz yazıyor..."):
                    bot_instruction = f"Sen tecrübeli ve motive edici bir klinik diyetisyensin. Sadece beslenme ve sağlık konularında cevap ver. Soru: {user_prompt}"
                    response = st.session_state.chat_session.send_message(bot_instruction)
                    st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# ------------------------------------------------------------------------------
# 5c. DİYETİSYEN ROLÜ EKRANI (Yeni Ekran)
# ------------------------------------------------------------------------------
elif st.session_state.role == "diyetisyen":
    st.subheader("👩‍⚕️ Diyetisyen Yönetim Paneli")
    
    tab1, tab2 = st.tabs(["👥 Kullanıcı Listesi", "🔍 Son Analizleri İncele"])
    
    with tab1:
        st.subheader("Danışanlarınız")
        # Temsili Kullanıcı Listesi Verisi
        data = {
            "Kullanıcı Adı": ["ahmet_yilmaz", "ayse_demir", "fatma_kaya", "mehmet_oz"],
            "Son Giriş": ["1 saat önce", "Dün", "3 saat önce", "5 gün önce"],
            "Hedef": ["Kilo Verme", "Kas Kütlesi", "Kilo Koruma", "Kilo Verme"],
            "Analiz Sayısı": [12, 45, 8, 2]
        }
        st.table(data)
        st.divider()
        st.subheader("Kullanıcı Profili Detayı (Temsili Ahmet Yılmaz)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Mevcut Kilo", "85 kg", "-2 kg")
        c2.metric("Hedef Kilo", "78 kg")
        c3.metric("Günlük Kalori Hedefi", "2100 kcal")

    with tab2:
        st.subheader("Kullanıcıların Yüklediği Son Öğün Fotoğrafları")
        st.markdown("Burada kullanıcıların analiz ettiği son yemekleri ve yapay zekanın yorumlarını inceleyebilirsiniz.")
        # Diyetisyen ekranında chatbot veya analizör yok, sadece inceleme ekranı var.
        st.info("Veritabanı bağlandığında, Ahmet Yılmaz'ın yüklediği son 5 öğün fotoğrafı ve yorumları burada liste halinde görünecektir.")
