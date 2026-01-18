import streamlit as st
import google.generativeai as genai
import time
import json
import random
import os
import sys
import base64

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Next Horizon - Hướng nghiệp",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="auto" # Mobile tự đóng (hiện nút menu), PC tự mở
)

# --- HÀM XỬ LÝ HÌNH NỀN ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    try:
        bin_str = get_base64(png_file)
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem !important;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }}
        section[data-testid="stSidebar"] {{
            background-color: rgba(240, 242, 246, 0.95);
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

if os.path.exists("background.jpg"): set_background("background.jpg")
elif os.path.exists("background.png"): set_background("background.png")

# --- 2. CSS GIAO DIỆN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* --- HIỆN MENU 3 GẠCH --- */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        visibility: visible !important;
    }
    .stDeployButton { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    footer { display: none !important; }

    /* --- SIDEBAR NÚT ĐỀU NHAU --- */
    .sidebar-title {
        font-size: 1.5rem !important; font-weight: 800 !important;
        color: #004A8D !important; text-align: center !important;
        margin-bottom: 0.5rem !important;
    }
    /* CSS ép nút sidebar full width */
    section[data-testid="stSidebar"] .stButton button {
        width: 100% !important;
        text-align: center !important;
        justify-content: center !important;
        font-weight: 600 !important;
    }

    /* --- GIAO DIỆN CHUNG --- */
    .main-header {
        font-size: 2.8rem !important; font-weight: 900; 
        background: -webkit-linear-gradient(45deg, #004A8D, #0088cc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: -10px !important; margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.1rem !important; font-weight: 700; color: #555; 
        text-align: center; margin-bottom: 15px;
    }
    
    /* Nút bấm ở màn hình chính */
    .main .stButton button {
        width: 100%; border-radius: 10px; height: 3rem; font-weight: 600;
        border: 1px solid #e0e0e0; background-color: white; color: #004A8D;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .main .stButton button:hover {
        transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        background-color: #f8f9fa; color: #0066cc; border-color: #0066cc;
    }

    /* Cards */
    .quiz-container {
        background-color: white; padding: 1.5rem; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 1rem; border: 1px solid #f0f2f5;
    }
    .result-card {
        background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
        padding: 20px; border-radius: 12px; border-left: 5px solid #004A8D; margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .intro-text {
        font-family: 'Inter', sans-serif; line-height: 1.6; color: #333; text-align: justify;
        background: #fff; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #eee;
    }
    .ikigai-benefit {
        margin-bottom: 8px; padding-left: 10px; border-left: 3px solid #00C853;
        background-color: #f1fcf5; padding: 8px; border-radius: 0 6px 6px 0;
    }
    .footer {
        text-align: center; color: #999; font-size: 0.75rem; 
        margin-top: 5px; padding-top: 5px; border-top: 1px solid #f0f0f0;
    }
    
    /* Responsive Mobile */
    @media (max-width: 768px) {
        .main-header { font-size: 2rem !important; }
        .block-container { padding-top: 3rem !important; }
        .stRadio > div { flex-direction: column; gap: 10px; }
    }
    @media (min-width: 769px) {
        .stRadio > div { flex-direction: row; gap: 15px; flex-wrap: wrap; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'auth_error' not in st.session_state: st.session_state.auth_error = ""
if 'holland_scores' not in st.session_state: st.session_state.holland_scores = None
if 'big_five_scores' not in st.session_state: st.session_state.big_five_scores = None
if 'ikigai_scores' not in st.session_state: st.session_state.ikigai_scores = None
if 'holland_step' not in st.session_state: st.session_state.holland_step = 'landing'
if 'big_five_step' not in st.session_state: st.session_state.big_five_step = 'landing'
if 'ikigai_step' not in st.session_state: st.session_state.ikigai_step = 'landing'
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'holland_questions_ai' not in st.session_state: st.session_state.holland_questions_ai = None
if 'ikigai_questions_ai' not in st.session_state: st.session_state.ikigai_questions_ai = None
if 'is_ai_mode' not in st.session_state: st.session_state.is_ai_mode = False

# --- 4. LOGIC ---
def switch_page(page_name):
    st.session_state.page = page_name
    if page_name == 'holland': st.session_state.holland_step = 'landing'
    if page_name == 'big_five': st.session_state.big_five_step = 'landing'
    if page_name == 'ikigai': st.session_state.ikigai_step = 'landing'

def verify_code():
    if st.session_state.input_code.strip().upper() == "NEXT2025":
        st.session_state.authenticated = True
        st.session_state.auth_error = ""
    else:
        st.session_state.auth_error = "❌ Mã xác nhận không đúng."

def render_image_safe(image_name, width=None):
    if os.path.exists(image_name):
        if width: st.image(image_name, width=width)
        else: st.image(image_name, use_container_width=True)

# --- AI & DATA ---
def get_ai_response(prompt, api_key):
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text
    except: return None

def generate_questions_logic(api_key):
    if not api_key: return get_static_holland_questions(), False
    try:
        p = f"Tạo 12 câu trắc nghiệm Holland (RIASEC) ngắn gọn cho HSVN. Seed: {random.randint(1,1000)}. JSON Only: [{{'text': '...', 'type': 'R'}}]"
        res = get_ai_response(p, api_key)
        s, e = res.find('['), res.rfind(']') + 1
        return json.loads(res[s:e]), True
    except: return get_static_holland_questions(), False

def generate_ikigai_questions_logic(api_key):
    if not api_key: return get_static_ikigai_questions(), False
    try:
        p = f"Tạo 12 câu trắc nghiệm Ikigai (Love, Good, World, Paid). Seed: {random.randint(1,1000)}. JSON Only."
        res = get_ai_response(p, api_key)
        s, e = res.find('['), res.rfind(']') + 1
        return json.loads(res[s:e]), True
    except: return get_static_ikigai_questions(), False

def get_static_holland_questions():
    return [{"text": "Thích sửa chữa máy móc", "type": "R"}, {"text": "Thích giải toán khó", "type": "I"}, 
            {"text": "Thích vẽ tranh", "type": "A"}, {"text": "Thích giúp đỡ người khác", "type": "S"}, 
            {"text": "Thích lãnh đạo nhóm", "type": "E"}, {"text": "Thích làm việc sổ sách", "type": "C"},
            {"text": "Thích vận động tay chân", "type": "R"}, {"text": "Thích tìm hiểu khoa học", "type": "I"}, 
            {"text": "Thích chơi nhạc cụ", "type": "A"}, {"text": "Thích lắng nghe tâm sự", "type": "S"}, 
            {"text": "Thích kinh doanh", "type": "E"}, {"text": "Thích sự ngăn nắp", "type": "C"}]

def get_big_five_questions():
    return [{"text": "Tôi thích giao tiếp", "trait": "E", "reverse": False}, {"text": "Tôi hay lo lắng", "trait": "N", "reverse": False},
            {"text": "Tôi giàu trí tưởng tượng", "trait": "O", "reverse": False}, {"text": "Tôi quan tâm người khác", "trait": "A", "reverse": False},
            {"text": "Tôi làm việc có kế hoạch", "trait": "C", "reverse": False}, {"text": "Tôi thích yên tĩnh", "trait": "E", "reverse": True},
            {"text": "Tôi bình tĩnh", "trait": "N", "reverse": True}, {"text": "Tôi thực tế", "trait": "O", "reverse": True},
            {"text": "Tôi ít quan tâm người khác", "trait": "A", "reverse": True}, {"text": "Tôi hơi bừa bộn", "trait": "C", "reverse": True}]

def get_static_ikigai_questions():
    return [{"text": "Tôi hạnh phúc khi làm việc này", "category": "Love"}, {"text": "Tôi làm giỏi việc này", "category": "Good"},
            {"text": "Xã hội cần việc này", "category": "World"}, {"text": "Việc này kiếm ra tiền", "category": "Paid"},
            {"text": "Tôi quên thời gian khi làm", "category": "Love"}, {"text": "Mọi người khen tôi giỏi", "category": "Good"},
            {"text": "Việc này giúp ích cộng đồng", "category": "World"}, {"text": "Tôi ưu tiên thu nhập", "category": "Paid"}]

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo1.png") and os.path.exists("logo2.png"):
        c1, c2 = st.columns(2)
        with c1: st.image("logo1.png", use_container_width=True)
        with c2: st.image("logo2.png", use_container_width=True)
    elif os.path.exists("logo1.png"):
        st.image("logo1.png", width=120)
        
    st.markdown('<div class="sidebar-title">🚀 Next Horizon</div>', unsafe_allow_html=True)
    
    user_api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not user_api_key:
        user_api_key = st.text_input("🔑 Nhập API Key:", type="password")
    else:
        st.success("✅ Đã kết nối Key")
    
    st.markdown('<div class="custom-separator"></div>', unsafe_allow_html=True)

    if st.session_state.authenticated:
        if st.button("🏠 Trang chủ", use_container_width=True): switch_page('welcome'); st.rerun()
        
        st.caption("CÔNG CỤ ĐÁNH GIÁ")
        if st.button("🧩 Trắc nghiệm Holland", use_container_width=True): switch_page('holland'); st.rerun()
        if st.button("🧠 Trắc nghiệm Big Five", use_container_width=True): switch_page('big_five'); st.rerun()
        if st.button("🎯 Khám phá Ikigai", use_container_width=True): switch_page('ikigai'); st.rerun()
        
        st.caption("TƯ VẤN & HỖ TRỢ")
        if st.button("🔍 Tra cứu ngành nghề", use_container_width=True): switch_page('search'); st.rerun()
        if st.button("📈 Lộ trình phát triển", use_container_width=True): switch_page('roadmap'); st.rerun()
        if st.button("📊 Báo cáo tổng hợp", use_container_width=True): switch_page('report'); st.rerun()
        if st.button("🤖 Trợ lý AI", use_container_width=True): switch_page('chat'); st.rerun()
        if st.button("👨‍🏫 Gặp chuyên gia", use_container_width=True): switch_page('expert'); st.rerun()
        
        st.markdown('<div class="custom-separator"></div>', unsafe_allow_html=True)
        
        if st.button("🤖 Chat AI", use_container_width=True): switch_page('chat'); st.rerun()
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# --- 6. NỘI DUNG CHÍNH ---

# --- LOGIN ---
if not st.session_state.authenticated:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        render_image_safe("login.png", width=150)
        st.markdown("<h2 style='text-align: center; color: #004A8D;'>CỔNG ĐĂNG NHẬP</h2>", unsafe_allow_html=True)
        st.info("Chào mừng bạn đến với Ứng dụng Hướng nghiệp Next Horizon")
        st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><a href="https://forms.gle/cJLw7QwrDXyAHM8m7" target="_blank" style="text-decoration: none; color: #004A8D; font-weight: bold; background-color: #e3f2fd; padding: 10px 15px; border-radius: 8px;">👉 Chưa có mã? Nhấn vào đây để đăng ký</a></div>""", unsafe_allow_html=True)
        st.text_input("Mời bạn nhập mã xác nhận vào đây:", key="input_code", on_change=verify_code, type="password")
        if st.session_state.auth_error: st.error(st.session_state.auth_error)

# --- WELCOME ---
elif st.session_state.page == 'welcome':
    st.markdown('<p class="main-header">NEXT HORIZON</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Câu lạc bộ định hướng nghề nghiệp - UK Academy</p>', unsafe_allow_html=True)
    
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.info("🧩 **Trắc nghiệm Holland**\n\nTìm ra nhóm sở thích nghề nghiệp phù hợp nhất với bạn.")
        if st.button("Bắt đầu Holland", key="wc_h"): switch_page('holland')
    with r1c2:
        st.warning("🎯 **Khám phá IKIGAI**\n\n:red[Tìm điểm giao thoa của Đam mê, Kỹ năng và Nhu cầu xã hội.]")
        if st.button("Bắt đầu IKIGAI", key="wc_i"): switch_page('ikigai')

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.success("🧠 **Trắc nghiệm Big Five**\n\nHiểu rõ 5 đặc điểm tính cách cốt lõi của bản thân.")
        if st.button("Bắt đầu Big Five", key="wc_b"): switch_page('big_five')
    with r2c2:
        st.info("🔍 **Tìm kiếm Ngành nghề**\n\nTra cứu thông tin chi tiết về các ngành học và trường ĐH.")
        if st.button("Tìm kiếm Ngành nghề", key="wc_s"): switch_page('search')
    
    st.markdown('<div class="custom-separator"></div>', unsafe_allow_html=True)
    st.markdown("### 🤝 Dịch vụ Hỗ trợ & Tư vấn")
    r3c1, r3c2 = st.columns(2)
    
    with r3c1:
        st.markdown("""
        <div style="background-color: #FFF3E0; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #FFE0B2; margin-bottom: 10px;">
            <h4 style="color: #E65100; text-shadow: 1px 1px 1px rgba(0,0,0,0.1); font-weight: 800; margin: 0;">🤖 Trợ lý AI</h4>
            <p style="color: #BF360C; font-weight: 600; margin: 5px 0 0 0;">Hỏi đáp mọi lúc mọi nơi</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Chat với AI"): switch_page('chat')
        
    with r3c2:
        st.markdown("""
        <div style="background-color: #E3F2FD; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #BBDEFB; margin-bottom: 10px;">
            <h4 style="color: #0D47A1; text-shadow: 1px 1px 1px rgba(0,0,0,0.1); font-weight: 800; margin: 0;">👨‍🏫 Chuyên gia Tư vấn</h4>
            <p style="color: #01579B; font-weight: 600; margin: 5px 0 0 0;">Kết nối trực tiếp với thầy cô</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Gặp Chuyên gia"): switch_page('expert')

# --- HOLLAND ---
elif st.session_state.page == 'holland':
    if st.session_state.holland_step == 'landing':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="h_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="h_b", use_container_width=True): switch_page('welcome'); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1: render_image_safe("holland.png", 350)
        with c2:
            st.markdown("<h1 style='color: #004A8D;'>Trắc nghiệm Holland (RIASEC)</h1>", unsafe_allow_html=True)
            st.markdown("<div class='intro-text'><b>Mật mã Holland:</b> Trắc nghiệm Holland chính là cơ sở để bạn đối chiếu sở thích, năng lực tự nhiên của mình với yêu cầu của các nhóm ngành nghề.\n\nKết quả bài trắc nghiệm giúp bạn tìm ra ba kiểu tính cách của bạn tương ứng với 3 mật mã Holland.</div>", unsafe_allow_html=True)
            st.write("")
            if st.button("Bắt đầu trắc nghiệm Holland", type="primary"):
                if user_api_key and not st.session_state.holland_questions_ai:
                    with st.spinner("AI đang soạn thảo..."):
                        q, is_ai = generate_questions_logic(user_api_key)
                        st.session_state.holland_questions_ai = q
                        st.session_state.is_ai_mode = is_ai
                elif not st.session_state.holland_questions_ai:
                     st.session_state.holland_questions_ai = get_static_holland_questions()
                st.session_state.holland_step = 'intro'
                st.rerun()

    elif st.session_state.holland_step == 'intro':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="hi_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="hi_b", use_container_width=True): st.session_state.holland_step='landing'; st.rerun()
        st.markdown("<h2 style='text-align: center;'>Hướng dẫn kiểm tra</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;'><p>Hãy chọn giới tính:</p></div>", unsafe_allow_html=True)
            st.radio("Giới tính", ["Nam giới", "Nữ giới"], horizontal=True, label_visibility="collapsed")
            st.write("")
            if st.button("Bắt đầu kiểm tra ngay ➡️", type="primary", use_container_width=True):
                st.session_state.holland_step = 'quiz'; st.rerun()

    elif st.session_state.holland_step == 'quiz':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="hq_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="hq_b", use_container_width=True): st.session_state.holland_step='intro'; st.rerun()
        questions = st.session_state.holland_questions_ai or get_static_holland_questions()
        if st.session_state.is_ai_mode: st.success("✨ Câu hỏi AI")
        st.progress(50)
        with st.form("h_quiz"):
            scores = {'R':0,'I':0,'A':0,'S':0,'E':0,'C':0}
            for i, q in enumerate(questions):
                st.markdown(f"<div class='quiz-container'><b>Câu {i+1}:</b> {q['text']}</div>", unsafe_allow_html=True)
                ans = st.radio(f"Lựa chọn {i}", ["👎 Không thích", "😐 Trung lập", "👍 Rất thích"], key=f"h_{i}", horizontal=True, label_visibility="collapsed")
                if ans == "👍 Rất thích": scores[q['type']] += 2
                elif ans == "😐 Trung lập": scores[q['type']] += 1
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ HOÀN THÀNH", type="primary", use_container_width=True):
                st.session_state.holland_scores = scores
                st.session_state.holland_step = 'result'; st.rerun()

    elif st.session_state.holland_step == 'result':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="hr_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="hr_b", use_container_width=True): st.session_state.holland_step='landing'; st.rerun()
        st.success("Kết quả phân tích:")
        st.bar_chart(st.session_state.holland_scores)
        if user_api_key:
            with st.spinner("AI đang phân tích..."):
                top = sorted(st.session_state.holland_scores.items(), key=lambda x:x[1], reverse=True)[0]
                st.markdown(f"<div class='result-card'>{get_ai_response(f'Holland {top[0]}', user_api_key)}</div>", unsafe_allow_html=True)
        if st.button("Làm lại"): st.session_state.holland_questions_ai=None; st.session_state.holland_step='landing'; st.rerun()

# --- BIG FIVE ---
elif st.session_state.page == 'big_five':
    if st.session_state.big_five_step == 'landing':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="bl_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="bl_b", use_container_width=True): switch_page('welcome'); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1: render_image_safe("bigfive.png", 350)
        with c2:
            st.markdown("<h1 style='color: #004A8D;'>Khám phá tính cách BIG 5</h1>", unsafe_allow_html=True)
            st.markdown("<div class='intro-text'><b>Trắc nghiệm Big Five</b> (OCEAN) là công cụ đánh giá tâm lý học phổ biến, mô tả tính cách qua 5 nhóm đặc điểm:\n\n🌊 Cởi mở (Openness) | 🎯 Tận tâm (Conscientiousness) | 🗣️ Hướng ngoại (Extraversion) | 🤝 Dễ chịu (Agreeableness) | ⚡ Bất ổn cảm xúc (Neuroticism)</div>", unsafe_allow_html=True)
            st.write("")
            if st.button("Bắt đầu bài kiểm tra BIG 5", type="primary"):
                st.session_state.big_five_step = 'intro'; st.rerun()

    elif st.session_state.big_five_step == 'intro':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="bi_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="bi_b", use_container_width=True): st.session_state.big_five_step='landing'; st.rerun()
        st.markdown("<h2 style='text-align: center;'>Hướng dẫn</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div style='background-color: white; padding: 30px; border-radius: 15px; text-align: center;'><p>Chọn giới tính:</p></div>", unsafe_allow_html=True)
            st.radio("Giới tính", ["Nam", "Nữ"], horizontal=True, label_visibility="collapsed")
            if st.button("Bắt đầu ngay ➡️", type="primary", use_container_width=True):
                st.session_state.big_five_step = 'quiz'; st.rerun()

    elif st.session_state.big_five_step == 'quiz':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="bq_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="bq_b", use_container_width=True): st.session_state.big_five_step='intro'; st.rerun()
        st.progress(50)
        with st.form("b_quiz"):
            qs = get_big_five_questions()
            scores = {'O':0,'C':0,'E':0,'A':0,'N':0}
            map_s = {"🔴 Rất sai":1, "🟠 Sai":2, "⚪ Trung lập":3, "🟢 Đúng":4, "🔵 Rất đúng":5}
            for i, q in enumerate(qs):
                st.markdown(f"<div class='quiz-container'>{q['text']}</div>", unsafe_allow_html=True)
                ans = st.radio(f"b{i}", list(map_s.keys()), index=2, key=f"b_{i}", horizontal=True, label_visibility="collapsed")
                raw = map_s[ans]
                scores[q['trait']] += (6-raw if q['reverse'] else raw)
            if st.form_submit_button("✅ HOÀN THÀNH", type="primary", use_container_width=True):
                st.session_state.big_five_scores = scores
                st.session_state.big_five_step = 'result'; st.rerun()

    elif st.session_state.big_five_step == 'result':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="br_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="br_b", use_container_width=True): st.session_state.big_five_step='landing'; st.rerun()
        st.balloons()
        st.success("Kết quả Big Five:")
        st.bar_chart(st.session_state.big_five_scores)
        if st.button("Làm lại"): st.session_state.big_five_step='landing'; st.rerun()

# --- IKIGAI ---
elif st.session_state.page == 'ikigai':
    if st.session_state.ikigai_step == 'landing':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="il_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="il_b", use_container_width=True): switch_page('welcome'); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1: render_image_safe("ikigai.png", 350)
        with c2:
            st.markdown("<h1 style='color: #004A8D;'>Khám phá Lẽ sống IKIGAI</h1>", unsafe_allow_html=True)
            st.markdown("<div class='intro-text'><b>Trắc nghiệm Ikigai: Là sự kết hợp hài hòa giữa 4 yếu tố:\n\n❤️ Yêu thích | 🌟 Giỏi | 🌏 Thế giới cần | 💰 Được trả công\n\nMục đích sống: Xác định động lực phấn đấu.\n\nHạnh phúc & Sức khỏe: Giảm căng thẳng, sống thọ hơn.</b>...</div>", unsafe_allow_html=True)
            st.write("")
            if st.button("Bắt đầu khám phá Ikigai", type="primary"):
                if user_api_key and not st.session_state.ikigai_questions_ai:
                    with st.spinner("AI đang tạo đề..."):
                        q, is_ai = generate_ikigai_questions_logic(user_api_key)
                        st.session_state.ikigai_questions_ai = q
                        st.session_state.is_ai_mode = is_ai
                elif not st.session_state.ikigai_questions_ai:
                     st.session_state.ikigai_questions_ai = get_static_ikigai_questions()
                st.session_state.ikigai_step = 'intro'; st.rerun()

    elif st.session_state.ikigai_step == 'intro':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="ii_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="ii_b", use_container_width=True): st.session_state.ikigai_step='landing'; st.rerun()
        st.markdown("<h2 style='text-align: center;'>Hướng dẫn đánh giá</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div style='background-color: white; padding: 30px; text-align: center;'><p>Chọn giới tính:</p></div>", unsafe_allow_html=True)
            st.radio("Giới tính", ["Nam", "Nữ"], horizontal=True, label_visibility="collapsed")
            if st.button("Bắt đầu ngay ➡️", type="primary", use_container_width=True):
                st.session_state.ikigai_step = 'quiz'; st.rerun()

    elif st.session_state.ikigai_step == 'quiz':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="iq_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="iq_b", use_container_width=True): st.session_state.ikigai_step='intro'; st.rerun()
        qs = st.session_state.ikigai_questions_ai or get_static_ikigai_questions()
        if st.session_state.is_ai_mode: st.success("✨ Câu hỏi AI")
        with st.form("i_quiz"):
            scores = {'Love':0,'Good':0,'World':0,'Paid':0}
            counts = {'Love':0,'Good':0,'World':0,'Paid':0}
            map_s = {"🔴 Sai":1, "🟠 Hơi sai":2, "⚪ Trung lập":3, "🟢 Đúng":4, "🔵 Rất đúng":5}
            for i, q in enumerate(qs):
                st.markdown(f"<div class='quiz-container'>{q['text']}</div>", unsafe_allow_html=True)
                ans = st.radio(f"i{i}", list(map_s.keys()), index=2, key=f"i_{i}", horizontal=True, label_visibility="collapsed")
                cat = q.get('category','Love')
                scores[cat] += map_s[ans]
                counts[cat] += 1
            if st.form_submit_button("✅ XEM KẾT QUẢ", type="primary", use_container_width=True):
                final = {k: (v/counts[k])*2 if counts[k]>0 else 0 for k,v in scores.items()}
                st.session_state.ikigai_scores = final
                st.session_state.ikigai_step = 'result'; st.rerun()

    elif st.session_state.ikigai_step == 'result':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="ir_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="ir_b", use_container_width=True): st.session_state.ikigai_step='landing'; st.rerun()
        st.balloons()
        st.success("Biểu đồ Ikigai:")
        st.bar_chart(st.session_state.ikigai_scores)
        if st.button("Làm lại"): st.session_state.ikigai_questions_ai=None; st.session_state.ikigai_step='landing'; st.rerun()

# --- EXPERT ---
elif st.session_state.page == 'expert':
    # --- NAV BAR ---
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="e_h", use_container_width=True): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="e_b", use_container_width=True): switch_page('welcome'); st.rerun()
        
    # Banner
    st.markdown("""<div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px;"><h4 style="color: #2e7d32; margin: 0;">🎁 Quà tặng từ TS. Vũ Việt Anh</h4><p style="margin: 5px 0;">Chatbot GPT chuyên sâu hỗ trợ định hướng nghề nghiệp 24/7.</p></div>""", unsafe_allow_html=True)
    st.link_button("👉 Trò chuyện ngay với GPT TS. Vũ Việt Anh", "https://chatgpt.com/g/g-6942112d74cc8191860a9938ae29b14c-huong-nghiep-cung-ts-vu-viet-anh", type="primary", use_container_width=True)
    st.markdown("---")
    
    # 3 CỘT CHUYÊN GIA
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        st.markdown('<div class="result-card" style="height: 100%;">', unsafe_allow_html=True)
        if os.path.exists("nguyen_van_thanh.jpg"): st.image("nguyen_van_thanh.jpg", use_container_width=True)
        st.markdown("### TS. Nguyễn Văn Thanh\nChuyên gia tư vấn hướng nghiệp\n* SĐT: 0916.272.424\n* Email: nvthanh183@gmail.com")
        st.markdown('</div>', unsafe_allow_html=True)
    with ec2:
        st.markdown('<div class="result-card" style="height: 100%; border-left: 5px solid #2e7d32;">', unsafe_allow_html=True)
        if os.path.exists("vu_viet_anh.jpg"): st.image("vu_viet_anh.jpg", use_container_width=True)
        elif os.path.exists("vuvietanh.jpg"): st.image("vuvietanh.jpg", use_container_width=True)
        st.markdown("### TS. Vũ Việt Anh\nChuyên gia định hướng nghề nghiệp\nChủ tịch HĐ Cố vấn EDA INSTITUTE\n* SĐT: 098 4736999")
        st.markdown('</div>', unsafe_allow_html=True)
    with ec3:
        st.markdown('<div class="result-card" style="height: 100%;">', unsafe_allow_html=True)
        if os.path.exists("pham_cong_thanh.jpg"): st.image("pham_cong_thanh.jpg", use_container_width=True)
        st.markdown("### ThS. Phạm Công Thành\nChuyên gia định hướng nghề nghiệp\n* SĐT: 038.7315.722\n* Email: phamcongthanh92@gmail.com")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.link_button("💬 Chat ngay qua Messenger", "https://www.facebook.com/messages/t/100001857808197", use_container_width=True)

# --- CHAT ---
elif st.session_state.page == 'chat':
    # --- NAV BAR ---
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="c_h", use_container_width=True): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="c_b", use_container_width=True): switch_page('welcome'); st.rerun()
        
    st.header("🤖 Chat AI")
    for m in st.session_state.chat_history: st.chat_message(m["role"]).write(m["content"])
    if p := st.chat_input("Hỏi tôi..."):
        st.session_state.chat_history.append({"role":"user","content":p})
        st.chat_message("user").write(p)
        if user_api_key:
            res = get_ai_response(p, user_api_key)
            st.session_state.chat_history.append({"role":"assistant","content":res})
            st.chat_message("assistant").write(res)

# --- REPORT ---
elif st.session_state.page == 'report':
    # --- NAV BAR ---
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="r_h", use_container_width=True): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="r_b", use_container_width=True): switch_page('welcome'); st.rerun()
        
    st.header("📊 Báo cáo Tổng hợp")
    c1,c2,c3 = st.columns(3)
    with c1: st.write("Holland"); st.bar_chart(st.session_state.holland_scores)
    with c2: st.write("Big Five"); st.bar_chart(st.session_state.big_five_scores)
    with c3: st.write("Ikigai"); st.bar_chart(st.session_state.ikigai_scores)

# --- SEARCH & ROADMAP ---
elif st.session_state.page == 'search':
    # --- NAV BAR ---
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="s_h", use_container_width=True): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="s_b", use_container_width=True): switch_page('welcome'); st.rerun()
        
    render_image_safe("search.png", 100)
    st.header("Tìm kiếm Ngành nghề")
    q = st.text_input("Nhập ngành:")
    if q and st.button("Tìm kiếm"):
        if user_api_key: st.markdown(get_ai_response(f"Thông tin ngành {q} ở VN", user_api_key))
elif st.session_state.page == 'roadmap':
    # --- NAV BAR ---
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="rm_h", use_container_width=True): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="rm_b", use_container_width=True): switch_page('welcome'); st.rerun()
        
    render_image_safe("roadmap.png", 100)
    st.header("Lộ trình phát triển")
    if st.button("Lập lộ trình AI") and user_api_key:
        st.markdown(get_ai_response(f"Lộ trình phát triển cho Holland={st.session_state.holland_scores}", user_api_key))

# --- FOOTER ---
st.markdown("---")
st.markdown("""<div class='footer'>@2025 sản phẩm thuộc về Câu lạc bộ hướng nghiệp Next Horizon - UK Academy Hạ Long</div>""", unsafe_allow_html=True)
