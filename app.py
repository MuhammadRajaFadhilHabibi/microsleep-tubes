import streamlit as st
import cv2
from ultralytics import YOLO
import tempfile
from PIL import Image
import time
import numpy as np
import os

# ==========================================
# 0. KONFIGURASI DEPLOYMENT
# ==========================================
DEPLOYMENT_MODE = True  # Set True untuk Upload ke Cloud, False untuk Local

# Handling Audio
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

def play_sound():
    """Memainkan suara beep jika di Windows & Mode Local"""
    if HAS_SOUND and not DEPLOYMENT_MODE:
        try:
            winsound.Beep(2000, 150)
        except:
            pass

# ==========================================
# 1. KONFIGURASI TAMPILAN
# ==========================================
st.set_page_config(
    page_title="Microsleep Detection System",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05), transparent);
        transform: rotate(45deg);
        transition: all 0.5s ease;
    }

    .metric-card:hover::before {
        left: 100%;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 8px 0;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-top: 5px;
    }

    .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 5px;
        filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
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

    .stCheckbox {
        background: rgba(102, 126, 234, 0.1);
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    .stRadio > div {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
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

    .stCaption, .caption {
        color: #a0aec0 !important;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.5px;
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
    if not os.path.exists('best.pt'): return None
    try:
        model = YOLO('best.pt')
        return model
    except: return None

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def process_frame(frame, model, conf_threshold):
    results = model(frame, conf=conf_threshold, verbose=False)
    status = "awake"
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            if model.names[cls_id] == 'drowsy':
                status = "drowsy"
    annotated_frame = results[0].plot()
    return annotated_frame, status

def draw_hud_overlay(frame, status, elapsed_time, alert_count, alarm_trigger):
    height, width, _ = frame.shape
    overlay = frame.copy()
    
    safe_color = (0, 255, 127)   
    warn_color = (0, 165, 255)   
    danger_color = (0, 0, 255)   
    
    if status == "drowsy":
        if elapsed_time > alarm_trigger:
            red_tint = np.zeros_like(frame, dtype=np.uint8)
            red_tint[:] = (0, 0, 200)
            cv2.addWeighted(red_tint, 0.5, overlay, 0.5, 0, overlay)
            
            if int(time.time() * 5) % 2 == 0: 
                cv2.rectangle(overlay, (0, 0), (width, height), danger_color, 30)
            
            text = "WAKE UP!"
            font_scale = 2.5
            font_thick = 5
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thick)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2
            
            cv2.putText(overlay, text, (text_x+4, text_y+4), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0,0,0), font_thick+2)
            cv2.putText(overlay, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255,255,255), font_thick)

        else:
            bar_width = int((elapsed_time / alarm_trigger) * width)
            cv2.rectangle(overlay, (0, height-20), (bar_width, height), warn_color, -1)
            cv2.putText(overlay, f"DROWSINESS DETECTED... {elapsed_time:.1f}s", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, warn_color, 2)
            cv2.rectangle(overlay, (0,0), (width, height), warn_color, 5)

    else:
        cv2.line(overlay, (20, 20), (100, 20), safe_color, 3)
        cv2.line(overlay, (20, 20), (20, 100), safe_color, 3)
        cv2.line(overlay, (width-20, 20), (width-100, 20), safe_color, 3)
        cv2.line(overlay, (width-20, 20), (width-20, 100), safe_color, 3)
        cv2.putText(overlay, "SYSTEM ACTIVE - SAFE", (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, safe_color, 2)

    cv2.putText(overlay, f"ALERTS: {alert_count}", (width - 200, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    return overlay

# ==========================================
# 4. MAIN APPLICATION
# ==========================================
def main():
    st.markdown("<h1>👁️ Microsleep Detection System</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>REAL-TIME DROWSINESS MONITORING</p>", unsafe_allow_html=True)
    st.markdown("---")

    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 30px 20px; margin-bottom: 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)); border-radius: 20px; border: 1px solid rgba(102, 126, 234, 0.3);'>
            <div style='font-size: 3.5rem; margin-bottom: 10px;'>👁️</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #ffffff; font-family: Space Grotesk, sans-serif;'>Microsleep</div>
            <div style='font-size: 0.75rem; color: #a0aec0; letter-spacing: 2px; margin-top: 5px;'>DETECTION SYSTEM</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>⚙️ Detection Mode</div>", unsafe_allow_html=True)
        if DEPLOYMENT_MODE:
            available_modes = ["📹 Video Analysis", "🖼️ Image Analysis"]
            st.warning("☁️ Cloud Mode: Webcam Disabled")
        else:
            available_modes = ["🎥 Live Webcam", "📹 Video Analysis", "🖼️ Image Analysis"]
            
        mode = st.radio("Mode", available_modes, label_visibility="collapsed")

        st.markdown("---")
        st.markdown("<div class='section-header'>🎯 Model Sensitivity</div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #a0aec0; font-size: 0.85rem; margin-bottom: 10px;'>Adjust detection confidence threshold</p>", unsafe_allow_html=True)
        conf_threshold = st.slider("Confidence", 0.0, 1.0, 0.40, 0.05, label_visibility="collapsed")
        st.markdown(f"<div class='info-box'>Confidence: <strong>{conf_threshold:.0%}</strong> {'🟢 High' if conf_threshold > 0.6 else '🟡 Medium' if conf_threshold > 0.3 else '🔴 Low'}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>🚨 Alert System</div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #a0aec0; font-size: 0.85rem; margin-bottom: 10px;'>Set alarm trigger delay</p>", unsafe_allow_html=True)
        alarm_trigger = st.slider("Duration (Sec)", 1.0, 5.0, 3.0, 0.5, label_visibility="collapsed")
        st.markdown(f"<div class='info-box'>⏰ Alarm triggers after: <strong>{alarm_trigger}s</strong> of continuous drowsiness</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>⚙️ Frame Processing</div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #a0aec0; font-size: 0.85rem; margin-bottom: 10px;'>Control processing speed (higher = faster but less accurate)</p>", unsafe_allow_html=True)
        
        frame_skip = st.select_slider(
            "Process every N frames",
            options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            value=3,
            label_visibility="collapsed"
        )
        
        if frame_skip == 1:
            st.markdown("<div class='info-box'>📊 Processing: <strong>Every frame</strong><br>⚡ Speed: Slowest | 🎯 Accuracy: Highest</div>", unsafe_allow_html=True)
        elif frame_skip <= 3:
            st.markdown(f"<div class='info-box'>📊 Processing: <strong>Every {frame_skip} frames</strong><br>⚡ Speed: Medium | 🎯 Accuracy: High</div>", unsafe_allow_html=True)
        elif frame_skip <= 5:
            st.markdown(f"<div class='info-box'>📊 Processing: <strong>Every {frame_skip} frames</strong><br>⚡ Speed: Fast | 🎯 Accuracy: Medium</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='info-box'>📊 Processing: <strong>Every {frame_skip} frames</strong><br>⚡ Speed: Very Fast | 🎯 Accuracy: Lower</div>", unsafe_allow_html=True)

    model = load_model()
    if not model:
        st.error("❌ MODEL NOT FOUND (best.pt)")
        st.stop()

    if "Image" not in mode:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-icon'>🎯</div>
                <div class='metric-label'>DRIVER STATUS</div>
            """, unsafe_allow_html=True)
            st_status = st.empty()
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-icon'>⏱️</div>
                <div class='metric-label'>DROWSY TIMER</div>
            """, unsafe_allow_html=True)
            st_timer = st.empty()
            st.markdown("</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-icon'>⚡</div>
                <div class='metric-label'>SYSTEM FPS</div>
            """, unsafe_allow_html=True)
            st_fps = st.empty()
            st.markdown("</div>", unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-icon'>📊</div>
                <div class='metric-label'>TOTAL ALERTS</div>
            """, unsafe_allow_html=True)
            st_alert_count = st.empty()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------
    # MODE 1: LIVE WEBCAM
    # -------------------------------------------------------
    if mode == "🎥 Live Webcam" and not DEPLOYMENT_MODE:
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            start_btn = st.checkbox("🔴 START DETECTION SYSTEM", value=False)
        
        st.markdown("<br>", unsafe_allow_html=True)
        frame_window = st.empty()
        
        if start_btn:
            camera = cv2.VideoCapture(0)
            drowsy_start = None
            alert_count = 0
            
            while True:
                ret, frame = camera.read()
                if not ret: break
                frame = cv2.flip(frame, 1)
                
                start_t = time.time()
                frame_result, status = process_frame(frame, model, conf_threshold)
                fps = 1.0 / (time.time() - start_t)
                
                curr_time = time.time()
                elapsed = 0.0
                
                if status == "drowsy":
                    if drowsy_start is None: drowsy_start = curr_time
                    elapsed = curr_time - drowsy_start
                    
                    if elapsed > alarm_trigger:
                        st_status.markdown(f'<div class="metric-value" style="color:#ff6b6b">⚠️ DROWSY</div>', unsafe_allow_html=True)
                        st_timer.markdown(f'<div class="metric-value" style="color:#ff6b6b">{elapsed:.1f}s</div>', unsafe_allow_html=True)
                        play_sound()
                    else:
                        st_status.markdown(f'<div class="metric-value" style="color:#fbbf24">⚠️ WARNING</div>', unsafe_allow_html=True)
                        st_timer.markdown(f'<div class="metric-value" style="color:#fbbf24">{elapsed:.1f}s</div>', unsafe_allow_html=True)
                else:
                    drowsy_start = None
                    st_status.markdown(f'<div class="metric-value" style="color:#00d4aa">✓ AWAKE</div>', unsafe_allow_html=True)
                    st_timer.markdown(f'<div class="metric-value">0.0s</div>', unsafe_allow_html=True)

                frame_overlay = draw_hud_overlay(frame_result, status, elapsed, alert_count, alarm_trigger)
                st_fps.markdown(f'<div class="metric-value">{int(fps)}</div>', unsafe_allow_html=True)
                
                if status == "drowsy" and elapsed > alarm_trigger:
                    pass 
                
                st_alert_count.markdown(f'<div class="metric-value">{alert_count}</div>', unsafe_allow_html=True)
                frame_window.image(cv2.cvtColor(frame_overlay, cv2.COLOR_BGR2RGB), use_container_width=True)
            camera.release()

# -------------------------------------------------------
# -------------------------------------------------------
    # MODE 2: VIDEO ANALYSIS (REVISI FINAL: AKURASI TINGGI + ANTI LAG)
    # -------------------------------------------------------
    elif mode == "📹 Video Analysis":
        st.markdown("""
        <div style='background: rgba(102, 126, 234, 0.1); padding: 25px; border-radius: 16px; border: 1px solid rgba(102, 126, 234, 0.2); margin-bottom: 25px;'>
            <h3 style='color: #e2e8f0; margin: 0 0 10px 0;'>📹 Video Analysis Mode</h3>
            <p style='color: #a0aec0; margin: 0; font-size: 0.9rem;'>Upload a video file to analyze drowsiness patterns.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_video = st.file_uploader("Upload Video", type=['mp4', 'avi', 'mov', 'mkv'], label_visibility="collapsed")
        
        if uploaded_video:
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                start_video = st.button("▶️ START VIDEO ANALYSIS", use_container_width=True)
            
            if start_video:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(uploaded_video.read())
                tfile.close()
                
                vf = cv2.VideoCapture(tfile.name)
                
                if not vf.isOpened():
                    st.error("❌ Failed to open video. Please try another file.")
                    st.stop()
                
                total_frames = int(vf.get(cv2.CAP_PROP_FRAME_COUNT))
                fps_video = vf.get(cv2.CAP_PROP_FPS)
                
                st.info(f"📊 Original Video: {total_frames} frames @ {fps_video:.1f} FPS")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                st_video = st.empty()
                
                drowsy_start = None
                alert_count = 0
                frame_count = 0
                processed_count = 0
                
                # --- KONFIGURASI PENTING ---
                # 1. Target Width 640: Standar YOLO. Jangan dikecilkan lagi agar mata terbaca.
                target_width = 640 
                
                # 2. Skip Rate: Mengikuti settingan sidebar kamu.
                skip_rate = frame_skip 
                
                # 3. Display Ratio: Ini kunci ANTI LAG.
                # Kita hanya update gambar di layar setiap 3 frame yang selesai diproses.
                # Backend kerja keras, tapi Internet kerja santai.
                display_every_n = 3 
                
                while vf.isOpened():
                    ret, frame = vf.read()
                    if not ret: 
                        break
                    
                    frame_count += 1
                    
                    # LOGIC 1: SKIP FRAME (Untuk mempercepat durasi total)
                    if frame_count % skip_rate != 0:
                        continue
                    
                    processed_count += 1
                    
                    # LOGIC 2: RESIZE KE 640 (Standar Akurasi)
                    height, width = frame.shape[:2]
                    if width > 640: # Hanya resize jika gambar aslinya kegedean
                        aspect_ratio = width / height
                        new_width = target_width
                        new_height = int(new_width / aspect_ratio)
                        frame = cv2.resize(frame, (new_width, new_height))
                    
                    # LOGIC 3: DETEKSI YOLO (Tanpa kompresi imgsz)
                    start_t = time.time()
                    # Kita hapus 'imgsz=320' agar AI tidak rabun
                    results = model(frame, conf=conf_threshold, verbose=False)
                    
                    # Cek hasil deteksi
                    status = "awake"
                    for r in results:
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            # Cek nama class
                            if hasattr(model, 'names') and model.names[cls_id] == 'drowsy':
                                status = "drowsy"
                            # Fallback ID (Jaga-jaga jika names tidak load)
                            elif cls_id == 1: 
                                status = "drowsy"
                    
                    # Hitung Durasi Ngantuk
                    elapsed = 0.0
                    if status == "drowsy":
                        if drowsy_start is None: drowsy_start = time.time()
                        elapsed = time.time() - drowsy_start
                        
                        if elapsed > alarm_trigger:
                            if elapsed > alarm_trigger and elapsed < alarm_trigger + 0.2: 
                                alert_count += 1
                    else:
                        drowsy_start = None

                    # LOGIC 4: VISUALISASI
                    annotated_frame = results[0].plot()
                    frame_overlay = draw_hud_overlay(annotated_frame, status, elapsed, alert_count, alarm_trigger)
                    
                    # LOGIC 5: UPDATE UI (THROTTLED - AGAR TIDAK LAG)
                    
                    # Update Progress Bar (Setiap 5 frame)
                    if processed_count % 5 == 0:
                        progress_bar.progress(min(frame_count / total_frames, 1.0))
                        status_text.text(f"Processing... {int((frame_count/total_frames)*100)}%")
                    
                    # Update Gambar Video (Setiap 'display_every_n' frame)
                    # Ini mencegah browser keberatan load gambar
                    if processed_count % display_every_n == 0:
                        st_video.image(cv2.cvtColor(frame_overlay, cv2.COLOR_BGR2RGB), use_container_width=True)
                        
                        # Update Angka/Teks (Real-time is fine here)
                        if status == "drowsy":
                             st_status.markdown(f'<div class="metric-value" style="color:#ff6b6b">⚠️ DROWSY</div>', unsafe_allow_html=True)
                        else:
                             st_status.markdown(f'<div class="metric-value" style="color:#00d4aa">✓ SAFE</div>', unsafe_allow_html=True)
                        
                        st_timer.markdown(f'<div class="metric-value">{elapsed:.1f}s</div>', unsafe_allow_html=True)
                        st_alert_count.markdown(f'<div class="metric-value">{alert_count}</div>', unsafe_allow_html=True)

                vf.release()
                os.unlink(tfile.name)
                progress_bar.progress(1.0)
                status_text.text("✅ Analysis Complete")
                st.balloons()

    # -------------------------------------------------------
    # MODE 3: IMAGE ANALYSIS
    # -------------------------------------------------------
    elif mode == "🖼️ Image Analysis":
        st.markdown("""
        <div style='background: rgba(102, 126, 234, 0.1); padding: 25px; border-radius: 16px; border: 1px solid rgba(102, 126, 234, 0.2); margin-bottom: 25px;'>
            <h3 style='color: #e2e8f0; margin: 0 0 10px 0;'>🖼️ Image Analysis Mode</h3>
            <p style='color: #a0aec0; margin: 0; font-size: 0.9rem;'>Upload a single image to detect drowsiness. Supported formats: JPG, PNG, JPEG</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_img = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
        if uploaded_img:
            col_l, col_r = st.columns(2)
            image = Image.open(uploaded_img)
            with col_l:
                st.markdown("<h3 style='text-align: center; color: #e2e8f0; margin-bottom: 15px;'>📸 Original Image</h3>", unsafe_allow_html=True)
                st.image(image, use_container_width=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                btn = st.button("🔍 ANALYZE IMAGE", use_container_width=True)
            
            if btn:
                with st.spinner("🔄 Processing image..."):
                    time.sleep(0.5)
                    res = model(image, conf=conf_threshold)
                    res_plotted = res[0].plot()
                    status_final = "awake"
                    confidence_score = 0.0
                    for r in res:
                        for box in r.boxes:
                            if model.names[int(box.cls[0])] == 'drowsy': 
                                status_final = "drowsy"
                                confidence_score = float(box.conf[0])
                    
                    with col_r:
                        st.markdown("<h3 style='text-align: center; color: #e2e8f0; margin-bottom: 15px;'>🤖 Detection Result</h3>", unsafe_allow_html=True)
                        st.image(cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB), use_container_width=True)
                        
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
                                    All Clear
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

if __name__ == "__main__":

    main()

