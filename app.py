import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="Dijital Diyetisyen Asistanı", layout="centered")
st.title("🍏 Dijital Diyetisyen Asistanı (MVP)")

st.sidebar.header("⚙️ Sistem Ayarları")
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)


# Güvenlik ve Sistem Kuralları
system_instruction = """
Sen uzman bir dijital diyetisyen asistanısın. Görevin hastanın yüklediği yemekleri analiz etmek ve beslenme sorularını yanıtlamaktır.

KESİN GÜVENLİK KURALLARI:
1. Sen bir doktor değilsin. Tıbbi teşhis koyma, ilaç önerme.
2. Kesin konuşma ("Tahmini olarak", "Yaklaşık" kullan).
3. Riskli durumlarda "Lütfen bu durumu kendi diyetisyenine danış" de.
"""

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
    
    # 1. BÖLÜM: FOTOĞRAF ANALİZİ
    st.header("📸 Öğün Analizi")
    uploaded_file = st.file_uploader("Yemek fotoğrafı yükle", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Yüklenen Fotoğraf", use_container_width=True)
        
        if st.button("Yemeği Analiz Et"):
            with st.spinner("Yapay zeka inceliyor..."):
                try:
                    # Sadece JSON dönmesi için prompt
                    json_prompt = """Bu fotoğraftaki yemeği analiz et ve SADECE şu formatta JSON ver: 
                    {"detected_foods": ["yemek 1"], "calories": 450, "protein_g": 20, "carbs_g": 50, "fat_g": 15, "confidence_score": 85}"""
                    response = model.generate_content([json_prompt, image])
                    cleaned_response = response.text.replace("```json", "").replace("```", "")
                    st.json(json.loads(cleaned_response))
                except Exception as e:
                    st.error("Bir hata oluştu, lütfen tekrar dene.")

    st.divider()

    # 2. BÖLÜM: CHATBOT
    st.header("💬 Diyetisyenine Sor")
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    user_input = st.chat_input("Örn: Bugün fazla mı yedim?")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Yanıtlanıyor..."):
                response = st.session_state.chat_session.send_message(user_input)
                st.markdown(response.text)
else:
    st.warning("Siz davet edilmediniz.")
