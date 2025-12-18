import streamlit as st
import cv2
from PIL import Image
import time
import numpy as np
import os
import sys

# Import Library dengan Error Handling
try:
    from ultralytics import YOLO
except ImportError:
    st.error("Library Ultralytics belum terinstall. Cek requirements.txt")
    st.stop()

# ==========================================
# 1. KONFIGURASI TAMPILAN
# ==========================================
st.set_page_config(
    page_title="Microsleep Detection - Cloud Edition",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling Modern Premium (Sama seperti code kedua)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d35 50%, #0f1419 100%);
        background-attachment: fixed;
    }

    h1 {
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        text-align: center;
        letter-spacing: -1px;
        font-size: 3rem;
        margin-bottom: 0;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
    }

    .subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }

    /* Sidebar Premium */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d35 0%, #0f1419 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
        margin: 30px 0;
    }

    .stFileUploader {
        background: rgba(102, 126, 234, 0.05);
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 30px;
        transition: all 0.3s ease;
    }

    .stFileUploader:hover {
        border-color: rgba(102, 126, 234, 0.6);
        background: rgba(102, 126, 234, 0.1);
    }

    .stImage {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    .section-header {
        color: #e2e8f0;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 25px 0 15px 0;
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.5px;
    }

    .info-box {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
        color: #cbd5e0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOAD MODEL
# ==========================================
@st.cache_resource
def load_model():
    if not os.path.exists('best.pt'): 
        return None
    try:
        model = YOLO('best.pt')
        return model
    except Exception as e:
        return None

# ==========================================
# 3. MAIN APPLICATION
# ==========================================
def main():
    st.markdown("<h1>👁️ Microsleep Detection</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>CLOUD DEPLOYMENT VERSION</p>", unsafe_allow_html=True)
    st.markdown("---")

    # --- SIDEBAR PREMIUM ---
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 30px 20px; margin-bottom: 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)); border-radius: 20px; border: 1px solid rgba(102, 126, 234, 0.3);'>
            <div style='font-size: 3.5rem; margin-bottom: 10px;'>👁️</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #ffffff; font-family: Space Grotesk, sans-serif;'>Microsleep</div>
            <div style='font-size: 0.75rem; color: #a0aec0; letter-spacing: 2px; margin-top: 5px;'>DETECTION SYSTEM</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("<div class='section-header'>🎯 Model Sensitivity</div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #a0aec0; font-size: 0.85rem; margin-bottom: 10px;'>Adjust detection confidence threshold</p>", unsafe_allow_html=True)
        conf_threshold = st.slider("Confidence", 0.0, 1.0, 0.25, 0.05, label_visibility="collapsed")
        st.markdown(f"<div class='info-box'>Confidence: <strong>{conf_threshold:.0%}</strong> {'🟢 High' if conf_threshold > 0.6 else '🟡 Medium' if conf_threshold > 0.3 else '🔴 Low'}</div>", unsafe_allow_html=True)

    # --- LOAD MODEL ---
    model = load_model()
    if not model:
        st.error("❌ MODEL NOT FOUND (best.pt). Pastikan file model sudah diupload ke GitHub.")
        st.stop()

    # --- MAIN UI (IMAGE ANALYSIS) ---
    st.markdown("""
    <div style='background: rgba(102, 126, 234, 0.1); padding: 25px; border-radius: 16px; border: 1px solid rgba(102, 126, 234, 0.2); margin-bottom: 25px;'>
        <h3 style='color: #e2e8f0; margin: 0 0 10px 0;'>🖼️ Image Analysis Mode</h3>
        <p style='color: #a0aec0; margin: 0; font-size: 0.9rem;'>Upload a single image to detect drowsiness (Microsleep). Supported formats: JPG, PNG, JPEG</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_img = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
    
    if uploaded_img:
        col_l, col_r = st.columns(2)
        image = Image.open(uploaded_img)
        
        with col_l:
            st.markdown("<h3 style='text-align: center; color: #e2e8f0; margin-bottom: 15px;'>📸 Original Image</h3>", unsafe_allow_html=True)
            st.image(image, use_container_width=True)
        
        # Tombol Analisis di tengah
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            btn = st.button("🔍 ANALYZE IMAGE", use_container_width=True)
        
        if btn:
            with st.spinner("🔄 Processing image on Cloud CPU..."):
                time.sleep(0.5) # Simulasi loading sebentar agar smooth
                
                # YOLO Process
                res = model(image, conf=conf_threshold)
                res_plotted = res[0].plot()
                
                status_final = "awake"
                confidence_score = 0.0
                
                # Logic penentuan status
                for r in res:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        # Cek nama class
                        if hasattr(model, 'names') and model.names[cls_id] == 'drowsy':
                            status_final = "drowsy"
                            confidence_score = float(box.conf[0])
                        # Fallback ID (Jaga-jaga)
                        elif cls_id == 1:
                            status_final = "drowsy"
                            confidence_score = float(box.conf[0])
                
                with col_r:
                    st.markdown("<h3 style='text-align: center; color: #e2e8f0; margin-bottom: 15px;'>🤖 Detection Result</h3>", unsafe_allow_html=True)
                    st.image(cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB), use_container_width=True)
                    
                    # Tampilkan hasil dengan kotak warna premium
                    if status_final == 'drowsy':
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                                        color: white; padding: 20px; border-radius: 12px; 
                                        text-align: center; font-weight: 700; font-size: 1.2rem;
                                        box-shadow: 0 8px 24px rgba(255, 107, 107, 0.6);
                                        margin-top: 15px;'>
                            ⚠️ MICROSLEEP DETECTED!
                            <div style='font-size: 0.9rem; margin-top: 8px; opacity: 0.9;'>
                                Confidence: {confidence_score:.1%}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%); 
                                        color: white; padding: 20px; border-radius: 12px; 
                                        text-align: center; font-weight: 700; font-size: 1.2rem;
                                        box-shadow: 0 8px 24px rgba(0, 212, 170, 0.4);
                                        margin-top: 15px;'>
                            ✅ AWAKE / SAFE
                            <div style='font-size: 0.9rem; margin-top: 8px; opacity: 0.9;'>
                                No signs of drowsiness
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
