import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime

# ==========================================
# 1. SAYFA AYARLARI VE TASARIM
# ==========================================
st.set_page_config(
    page_title="AI Dijital Diyetisyen Portalı", 
    page_icon="🍏", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS ile arayüzü biraz daha güzelleştirelim
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #2E7D32; font-weight: bold; }
    .sub-header { font-size: 1.2rem; color: #555555; margin-bottom: 20px; }
    .login-box { background-color: #f8f9fa; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API YAPILANDIRMASI (DOĞRU MODEL EKLENDİ)
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Dedektif modunda bulduğumuz, senin API anahtarına özel model adı:
    model = genai.GenerativeModel('gemini-2.0-flash-001')
except Exception as e:
    st.warning("⚠️ API Anahtarı bulunamadı! Lütfen `.streamlit/secrets.toml` dosyanızı kontrol edin.")
    st.info("💡 Uygulamanın arayüzünü görebilmeniz için şu an 'Test Modu'nda çalışıyor (Yapay zeka yanıt vermeyecektir).")
    model = None

# ==========================================
# 3. OTURUM (SESSION) YÖNETİMİ
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# ==========================================
# 4. GİRİŞ EKRANI (LOGIN)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown('<p class="main-header">🍏 AI Dijital Diyetisyen Portalı</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Yapay Zeka Destekli Kişiselleştirilmiş Beslenme Asistanı</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.subheader("🔐 Sisteme Giriş Yapın")
            st.info("Kullanıcı için: kullanıcı / kullanıcı123 \nDiyetisyen için: diyetisyen / diyetisyen123")
            
            username_input = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı girin...")
            password_input = st.text_input("Şifre", type="password", placeholder="Şifrenizi girin...")
            submitted = st.form_submit_button("Giriş Yap", use_container_width=True) 
            
            if submitted:
                if username_input == "kullanıcı" and password_input == "kullanıcı123":
                    st.session_state.logged_in = True
                    st.session_state.role = "kullanici"
                    st.session_state.username = "Emin Kaya"
                    st.rerun()
                elif username_input == "diyetisyen" and password_input == "diyetisyen123":
                    st.session_state.logged_in = True
                    st.session_state.role = "diyetisyen"
                    st.session_state.username = "Dyt. Ayşe Abla"
                    st.rerun()
                else:
                    st.error("❌ Hatalı kullanıcı adı veya şifre!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. YAN MENÜ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=100)
    st.title("Hoş geldiniz,")
    st.subheader(f"👋 {st.session_state.username}")
    
    rol_badge = "👨‍⚕️ Uzman Diyetisyen" if st.session_state.role == "diyetisyen" else "👤 Danışan"
    st.caption(f"**Yetki:** {rol_badge}")
    st.divider()
    
    if st.session_state.role == "kullanici":
        st.write("🎯 **Güncel Hedef:** Kilo Verme")
        st.write("🔥 **Günlük Hedef:** 2100 kcal")
        st.progress(65, text="Günlük Kalori Alımı (%65)")
        st.divider()
        
    if st.button("🚪 Güvenli Çıkış Yap", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        # Oturum verilerini temizle
        if "chat_session" in st.session_state:
            del st.session_state["chat_session"]
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.rerun()

# ==========================================
# 6. ANA DASHBOARD İÇERİĞİ
# ==========================================
st.markdown('<p class="main-header">Gösterge Paneli</p>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6A. KULLANICI (DANIŞAN) EKRANI
# ------------------------------------------------------------------------------
if st.session_state.role == "kullanici":
    tab1, tab2, tab3 = st.tabs(["📸 Akıllı Yemek Analizi", "💬 Diyetisyen Chatbot", "📈 Gelişim Grafiğim"])

    # TAB 1: YEMEK ANALİZİ
    with tab1:
        st.subheader("🍽️ Öğününüzü Yapay Zeka ile Analiz Edin")
        st.write("Yediğiniz yemeğin fotoğrafını yükleyin, yapay zeka kalori ve makro değerlerini anında hesaplasın.")
        
        col_img, col_res = st.columns([1, 1.5], gap="large")
        
        with col_img:
            hedef = st.selectbox("Mevcut Hedefiniz:", ["Kilo Verme", "Kilo Alma", "Kas Geliştirme", "Sağlıklı Yaşam"])
            uploaded_file = st.file_uploader("Bir fotoğraf seçin...", type=["jpg", "png", "jpeg"])
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Yüklenen Öğün", use_container_width=True)

        with col_res:
            if uploaded_file is not None:
                if st.button("🔍 Besin Değerlerini Analiz Et", type="primary", use_container_width=True):
                    if model:
                        with st.spinner("🤖 Yapay zeka fotoğrafı inceliyor... Lütfen bekleyin."):
                            prompt = (
                                f"Sen uzman bir klinik diyetisyensin. Danışanının güncel hedefi: {hedef}. "
                                "Bu fotoğraftaki yemeği detaylı analiz et. "
                                "1. Yemeğin içindeki muhtemel malzemeleri say.\n"
                                "2. Tahmini toplam kalori, protein (g), karbonhidrat (g) ve yağ (g) miktarlarını ver.\n"
                                f"3. {hedef} hedefine uygun olup olmadığını değerlendir ve kısa bir tavsiye ver. "
                                "Yanıtını Markdown formatında, şık ve okunaklı yap."
                            )
                            try:
                                response = model.generate_content([prompt, image])
                                st.success("✅ Analiz başarıyla tamamlandı!")
                                
                                # Metrikleri temsili olarak gösteriyoruz (AI'dan JSON da istenebilir)
                                st.markdown("### 📊 Hızlı Makro Özeti (Tahmini)")
                                m1, m2, m3, m4 = st.columns(4)
                                m1.metric(label="🔥 Kalori", value="~450 kcal")
                                m2.metric(label="🥩 Protein", value="~24g")
                                m3.metric(label="🥖 Karb.", value="~40g")
                                m4.metric(label="🥑 Yağ", value="~15g")
                                st.divider()
                                
                                st.markdown("### 🧠 Detaylı AI Yorumu")
                                st.markdown(response.text)
                            except Exception as e:
                                st.error(f"Analiz sırasında bir hata oluştu: {e}")
                    else:
                        st.error("API Anahtarı eksik olduğu için analiz yapılamıyor.")
            else:
                st.info("👈 Analize başlamak için lütfen sol taraftan bir yemek fotoğrafı yükleyin.")

    # TAB 2: CHATBOT
    with tab2:
        st.subheader("💬 AI Diyetisyeninize Danışın")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "chat_session" not in st.session_state and model is not None:
            st.session_state.chat_session = model.start_chat(history=[])

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).markdown(msg["content"])
            
        if prompt := st.chat_input("Sorunuzu yazın..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                if model:
                    with st.spinner("Yazıyor..."):
                        try:
                            bot_instruction = f"Sen tecrübeli bir diyetisyensin. Soru: {prompt}"
                            res = st.session_state.chat_session.send_message(bot_instruction)
                            st.markdown(res.text)
                            st.session_state.messages.append({"role": "assistant", "content": res.text})
                        except Exception as e:
                            st.error(f"Bir hata oluştu: {str(e)}")
                            # Hata durumunda oturumu sıfırla ki kilitlenmesin
                            st.session_state.chat_session = model.start_chat(history=[])
                else:
                    st.error("Sistem test modunda, mesaj gönderilemiyor.")

    # TAB 3: GELİŞİM GRAFİĞİ (Temsili Arayüz)
    with tab3:
        st.subheader("📈 Kilo ve Kalori Takibiniz")
        chart_data = pd.DataFrame({
            "Tarih": pd.date_range(start="2023-09-01", periods=10),
            "Kilo (kg)": [85, 84.5, 84.1, 83.8, 83.5, 83.2, 83.0, 82.5, 82.1, 81.8]
        }).set_index("Tarih")
        
        st.line_chart(chart_data, y="Kilo (kg)", color="#2E7D32")

# ------------------------------------------------------------------------------
# 6B. DİYETİSYEN EKRANI
# ------------------------------------------------------------------------------
elif st.session_state.role == "diyetisyen":
    tab1, tab2 = st.tabs(["👥 Danışan Yönetimi", "🔍 Son Analizler (Loglar)"])
    
    with tab1:
        st.subheader("Aktif Danışanlarınız")
        
        # ✅ İSİMLER GÜNCELLENDİ
        df_users = pd.DataFrame({
            "Danışan Adı Soyadı": ["Emin", "Esat", "İbrahim", "Eyüp", "Sami"],
            "Kayıt Tarihi": ["01.08.2023", "15.08.2023", "10.09.2023", "12.09.2023", "05.10.2023"],
            "Hedef": ["Kilo Verme", "Kas Geliştirme", "Kilo Koruma", "Kilo Verme", "Sağlıklı Yaşam"],
            "Başlangıç (kg)": [90, 55, 65, 105, 78],
            "Güncel (kg)": [85, 57, 64.5, 99, 76.5],
            "Uyum Skoru": ["🟢 %90", "🟡 %75", "🟢 %88", "🔴 %45", "🟢 %82"]
        })
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # ✅ Emin detayı korundu, istenirse diğerleri için de eklenebilir
        st.subheader("🔎 Detaylı Danışan Profili: Emin")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mevcut Kilo", "85 kg", "-5 kg (Toplam)")
        c2.metric("Hedef Kilo", "78 kg")
        c3.metric("Günlük Kalori Hedefi", "2100 kcal")
        c4.metric("Su Tüketimi", "2.5 Litre", "Hedefe Uygun")
        
        st.info("💡 **Diyetisyen Notu:** Emin son 2 haftadır antrenman öncesi karbonhidrat alımını ihmal ediyor. Bir sonraki görüşmede hatırlatılacak.")

    with tab2:
        st.subheader("Kullanıcıların AI Destekli Son Öğün Analizleri")
        st.write("Sistemdeki danışanların gün içinde yükledikleri öğünleri ve AI'nin verdiği geri bildirimleri buradan denetleyebilirsiniz.")
        
        with st.expander("📸 Emin - Kahvaltı (Bugün 09:15)", expanded=True):
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.image("https://images.unsplash.com/photo-1525385133512-2f3bdd039054?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80", caption="Yulaf ve Meyve")
            with col_b:
                st.markdown("**AI Analizi:** ~350 kcal, 12g Protein, 55g Karbonhidrat, 8g Yağ.")
                st.markdown("**AI Yorumu:** Harika bir enerji kaynağı! Ancak protein miktarını artırmak için yanına 1 adet haşlanmış yumurta eklenebilir.")
                st.button("Diyetisyen Olarak Yorum Yap", key="btn_emin")

        with st.expander("📸 Esat - Öğle Yemeği (Dün 13:30)"):
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.image("https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80", caption="Karışık Salata")
            with col_b:
                st.markdown("**AI Analizi:** ~200 kcal, 5g Protein, 20g Karbonhidrat, 10g Yağ.")
                st.markdown("**AI Yorumu:** Çok hafif bir öğün, ancak Esat'ın kas geliştirme hedefine (57kg) göre protein çok yetersiz. Tavuk veya ton balığı eklenmeli.")
                st.button("Diyetisyen Olarak Yorum Yap", key="btn_esat")
