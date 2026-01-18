import streamlit as st
import google.generativeai as genai
import time
import json
import random
import os
import sys
import base64  # Thêm thư viện để xử lý ảnh nền

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Next Horizon - Hướng nghiệp",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="auto" # Để auto để trên mobile nó tự ẩn gọn gàng
)

# --- HÀM XỬ LÝ HÌNH NỀN (BACKGROUND) ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    """Hàm cài đặt hình nền cho toàn bộ ứng dụng"""
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
        
        /* Làm mờ nền trắng của các container để lộ background đẹp hơn */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95); /* Tăng độ mờ lên 0.95 cho dễ đọc trên mobile */
            border-radius: 15px;
            padding: 1rem !important; /* Padding nhỏ hơn cho mobile */
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: rgba(240, 242, 246, 0.95);
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# --- GỌI HÀM CÀI HÌNH NỀN ---
if os.path.exists("background.jpg"):
    set_background("background.jpg")
elif os.path.exists("background.png"):
    set_background("background.png")


# --- 2. CSS GIAO DIỆN (MOBILE FIRST OPTIMIZATION) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* ẨN CÁC THÀNH PHẦN KHÔNG CẦN THIẾT */
    header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"], div[data-testid="stDecoration"] {
        display: none !important;
        height: 0px !important;
    }
    button[title="View fullscreen"] { display: none !important; }
    .stDeployButton { display: none !important; }

    /* TỐI ƯU KHOẢNG TRỐNG */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100%;
    }

    /* --- TYPOGRAPHY RESPONSIVE --- */
    .main-header {
        font-size: 2.2rem !important; /* Mặc định nhỏ hơn xíu */
        font-weight: 900 !important; 
        background: -webkit-linear-gradient(45deg, #004A8D, #0088cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center; 
        margin-top: -10px !important;
        margin-bottom: 0rem !important;
        line-height: 1.2;
        text-transform: uppercase;
    }
    
    .sub-header {
        font-size: 1rem !important; 
        font-weight: 700 !important;
        color: #555 !important; 
        text-align: center; 
        margin-bottom: 15px !important;
    }

    /* MEDIA QUERY CHO MOBILE (Màn hình < 768px) */
    @media only screen and (max-width: 768px) {
        .main-header { font-size: 1.8rem !important; } /* Chữ nhỏ hơn trên đt */
        .sub-header { font-size: 0.9rem !important; }
        .quiz-container { padding: 1rem !important; } /* Giảm padding khung câu hỏi */
        
        /* Nút bấm to hơn trên điện thoại để dễ chạm */
        div[data-testid="stButton"] > button {
            height: 3.5rem !important; 
            font-size: 16px !important;
        }
        
        /* Ảnh chuyên gia xếp dọc đẹp hơn */
        .result-card { margin-bottom: 15px !important; }
    }

    /* --- BUTTON STYLING --- */
    div[data-testid="stButton"] > button {
        width: 100%; 
        border-radius: 12px; 
        height: 3rem; 
        font-weight: 600; 
        border: none;
        background-color: #ffffff;
        color: #004A8D;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 10px rgba(0,0,0,0.15); 
        border-color: #004A8D;
    }
    div[data-testid="stButton"] > button:active {
        background-color: #e3f2fd;
        transform: translateY(0);
    }

    /* --- QUIZ & FORM --- */
    .quiz-container {
        background-color: white; 
        padding: 1.5rem; 
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
        margin-bottom: 1rem; 
        border: 1px solid #f0f2f5;
    }
    .quiz-question { 
        font-size: 1.1rem; font-weight: 700; color: #2c3e50; margin-bottom: 10px; 
    }
    
    /* Radio Button Responsive */
    .stRadio > div { 
        background-color: #f8f9fa; 
        padding: 10px; 
        border-radius: 8px;
        display: flex;
        flex-direction: row; /* Mặc định ngang */
        gap: 10px;
        flex-wrap: wrap; /* Tự xuống dòng nếu hết chỗ */
    }

    div[data-testid="stImage"] { 
        display: block; margin-left: auto; margin-right: auto; border-radius: 12px;
    }
    .result-card {
        background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
        padding: 15px; border-radius: 12px; border-left: 5px solid #004A8D; margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .intro-text {
        font-family: 'Inter', sans-serif; line-height: 1.5; color: #333; text-align: justify;
        background: #fff; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05); border: 1px solid #eee;
        font-size: 0.95rem;
    }
    .ikigai-benefit {
        margin-bottom: 8px; padding-left: 10px; border-left: 3px solid #00C853;
        background-color: #f1fcf5; padding: 8px; border-radius: 0 6px 6px 0;
    }

    .footer {
        text-align: center; color: #999; font-size: 0.7rem; 
        margin-top: 10px; padding-top: 10px; border-top: 1px solid #f0f0f0;
    }
    hr { margin: 0.5rem 0 !important; } 
    div[data-testid="column"] { padding: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# --- 3. KHỞI TẠO STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'auth_error' not in st.session_state: st.session_state.auth_error = ""

# Dữ liệu điểm số
if 'holland_scores' not in st.session_state: st.session_state.holland_scores = None
if 'big_five_scores' not in st.session_state: st.session_state.big_five_scores = None
if 'ikigai_scores' not in st.session_state: st.session_state.ikigai_scores = None

# Trạng thái các bài test
if 'holland_questions_ai' not in st.session_state: st.session_state.holland_questions_ai = None
if 'ikigai_questions_ai' not in st.session_state: st.session_state.ikigai_questions_ai = None 
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'is_ai_mode' not in st.session_state: st.session_state.is_ai_mode = False

# Trạng thái quy trình (Steps)
if 'holland_step' not in st.session_state: st.session_state.holland_step = 'landing'
if 'big_five_step' not in st.session_state: st.session_state.big_five_step = 'landing'
if 'ikigai_step' not in st.session_state: st.session_state.ikigai_step = 'landing' 

# --- 4. HÀM XỬ LÝ LOGIC ---

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

def render_image_safe(image_name, width=None, fallback_icon="🖼️", caption=None):
    if os.path.exists(image_name):
        # TỰ ĐỘNG THAY ĐỔI: Nếu không truyền width cụ thể, hoặc đang trên mobile, ưu tiên container width
        if width and width > 300: 
             st.image(image_name, use_container_width=True, caption=caption)
        else:
             st.image(image_name, width=width, caption=caption)
    else:
        pass 

# --- DATA: CÂU HỎI TĨNH (STATIC) ---

def get_big_five_questions():
    return [
        {"text": "Tôi là người thích giao tiếp và tràn đầy năng lượng.", "trait": "E", "reverse": False},
        {"text": "Tôi thường hay lo lắng về những điều nhỏ nhặt.", "trait": "N", "reverse": False},
        {"text": "Tôi có trí tưởng tượng phong phú và thích những ý tưởng mới.", "trait": "O", "reverse": False},
        {"text": "Tôi thường quan tâm và đồng cảm với cảm xúc của người khác.", "trait": "A", "reverse": False},
        {"text": "Tôi làm việc có kế hoạch và luôn hoàn thành nhiệm vụ đúng hạn.", "trait": "C", "reverse": False},
        {"text": "Tôi thích sự yên tĩnh và ít nói khi ở chỗ đông người.", "trait": "E", "reverse": True},
        {"text": "Tôi là người bình tĩnh, ít khi bị căng thẳng.", "trait": "N", "reverse": True},
        {"text": "Tôi thích những thứ quen thuộc và thực tế hơn là trừu tượng.", "trait": "O", "reverse": True},
        {"text": "Tôi đôi khi cảm thấy khó khăn để quan tâm đến vấn đề của người khác.", "trait": "A", "reverse": True},
        {"text": "Tôi đôi khi hơi bừa bộn và làm việc ngẫu hứng.", "trait": "C", "reverse": True},
        {"text": "Tôi thích là trung tâm của sự chú ý trong các bữa tiệc.", "trait": "E", "reverse": False},
        {"text": "Tâm trạng của tôi thay đổi khá thất thường.", "trait": "N", "reverse": False},
        {"text": "Tôi thích tìm hiểu về nghệ thuật, âm nhạc hoặc văn học.", "trait": "O", "reverse": False},
        {"text": "Mọi người thường nhận xét tôi là người tốt bụng và đáng tin cậy.", "trait": "A", "reverse": False},
        {"text": "Tôi luôn chú ý đến các chi tiết nhỏ và sự chính xác.", "trait": "C", "reverse": False}
    ]

def get_static_holland_questions():
    return [
        {"text": "Thích sửa chữa các thiết bị điện tử, máy móc", "type": "R"},
        {"text": "Thích làm việc ngoài trời, vận động tay chân", "type": "R"},
        {"text": "Thích tìm hiểu, phân tích các vấn đề khoa học", "type": "I"},
        {"text": "Thích giải các bài toán khó hoặc chơi cờ trí tuệ", "type": "I"},
        {"text": "Thích vẽ tranh, chơi nhạc cụ hoặc viết lách", "type": "A"},
        {"text": "Thích sáng tạo ý tưởng mới, không thích khuôn mẫu", "type": "A"},
        {"text": "Thích lắng nghe và chia sẻ tâm tư với người khác", "type": "S"},
        {"text": "Thích tham gia các hoạt động tình nguyện, cộng đồng", "type": "S"},
        {"text": "Thích đứng trước đám đông thuyết trình", "type": "E"},
        {"text": "Thích kinh doanh, bán hàng hoặc thuyết phục người khác", "type": "E"},
        {"text": "Thích làm việc với các con số, sổ sách kế toán", "type": "C"},
        {"text": "Thích sắp xếp mọi thứ ngăn nắp, có quy trình", "type": "C"}
    ]

def get_static_ikigai_questions():
    return [
        {"text": "Tôi thường xuyên cảm thấy hạnh phúc và quên hết thời gian khi làm những việc mình thích.", "category": "Love"},
        {"text": "Tôi có những sở thích đặc biệt mà tôi luôn muốn dành thời gian cho chúng.", "category": "Love"},
        {"text": "Mọi người thường khen ngợi tôi về những kỹ năng hoặc tài lẻ mà tôi có.", "category": "Good"},
        {"text": "Tôi cảm thấy tự tin khi giải quyết các vấn đề thuộc sở trường của mình.", "category": "Good"},
        {"text": "Tôi quan tâm đến các vấn đề xã hội và muốn đóng góp sức mình để giải quyết chúng.", "category": "World"},
        {"text": "Tôi tin rằng công việc tương lai của mình sẽ mang lại giá trị tích cực cho cộng đồng.", "category": "World"},
        {"text": "Tôi có những kỹ năng mà thị trường lao động đang tìm kiếm và sẵn sàng trả lương.", "category": "Paid"},
        {"text": "Tôi ưu tiên lựa chọn những nghề nghiệp có tiềm năng thu nhập ổn định và phát triển.", "category": "Paid"}
    ]

ROADMAP_DATA = {
    "R": "**Nhóm Kỹ thuật (Realistic):**\n- Cấp 3: Giỏi Toán, Lý, Công nghệ.\n- ĐH: Cơ khí, Điện tử, Xây dựng.\n- Kỹ năng: Vận hành máy móc.",
    "I": "**Nhóm Nghiên cứu (Investigative):**\n- Cấp 3: Giỏi Toán, Lý, Hóa.\n- ĐH: CNTT, Y Dược, Khoa học.\n- Kỹ năng: Phân tích, tư duy.",
    "A": "**Nhóm Nghệ thuật (Artistic):**\n- Cấp 3: Năng khiếu Vẽ, Nhạc.\n- ĐH: Thiết kế, Truyền thông, Kiến trúc.\n- Kỹ năng: Sáng tạo.",
    "S": "**Nhóm Xã hội (Social):**\n- Cấp 3: Giỏi Văn, Sử, GDCD.\n- ĐH: Sư phạm, Tâm lý, Xã hội học.\n- Kỹ năng: Giao tiếp, thấu cảm.",
    "E": "**Nhóm Quản lý (Enterprising):**\n- Cấp 3: Hoạt động đoàn thể.\n- ĐH: QTKD, Marketing, Luật.\n- Kỹ năng: Lãnh đạo, thuyết phục.",
    "C": "**Nhóm Nghiệp vụ (Conventional):**\n- Cấp 3: Cẩn thận, giỏi Toán.\n- ĐH: Kế toán, Tài chính, Hành chính.\n- Kỹ năng: Tổ chức, tỉ mỉ."
}

# --- 5. LOGIC AI (KHÔNG THAY ĐỔI) ---
def get_ai_response(prompt, api_key):
    if not api_key: return None
    try: genai.configure(api_key=api_key)
    except: return None
    models_to_try = ['gemini-2.0-flash-exp', 'gemini-2.0-flash-thinking-exp', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except: continue
    return None

def generate_questions_logic(api_key):
    if not api_key: return get_static_holland_questions(), False
    seed = random.randint(1, 1000)
    prompt = f"""Tạo 12 câu trắc nghiệm Holland (RIASEC) ngắn gọn cho HSVN. Seed: {seed}. JSON Only: [{{"text": "...", "type": "R"}}]"""
    ai_text = get_ai_response(prompt, api_key)
    if ai_text:
        try:
            start = ai_text.find('[')
            end = ai_text.rfind(']') + 1
            if start != -1 and end != -1:
                questions = json.loads(ai_text[start:end])
                if len(questions) >= 6:
                    random.shuffle(questions)
                    return questions, True
        except: pass
    return get_static_holland_questions(), False

def generate_ikigai_questions_logic(api_key):
    if not api_key: return get_static_ikigai_questions(), False
    seed = random.randint(1, 1000)
    prompt = f"""
    Tạo 12 câu trắc nghiệm đánh giá Ikigai (4 yếu tố: Love, Good, World, Paid) cho học sinh.
    Mỗi yếu tố 3 câu. Dạng khẳng định "Tôi...".
    Seed: {seed}. Output JSON ONLY: [{{"text": "...", "category": "Love"}}, ...]
    """
    ai_text = get_ai_response(prompt, api_key)
    if ai_text:
        try:
            start = ai_text.find('[')
            end = ai_text.rfind(']') + 1
            if start != -1 and end != -1:
                questions = json.loads(ai_text[start:end])
                if len(questions) >= 8:
                    random.shuffle(questions)
                    return questions, True
        except: pass
    return get_static_ikigai_questions(), False

# --- 6. SIDEBAR ---
with st.sidebar:
    # --- HIỂN THỊ LOGO (MỚI THÊM) ---
    if os.path.exists("logo1.png") and os.path.exists("logo2.png"):
        c1, c2 = st.columns(2)
        with c1: st.image("logo1.png", use_container_width=True)
        with c2: st.image("logo2.png", use_container_width=True)
    elif os.path.exists("logo1.png"):
        st.image("logo1.png", width=120)
        
    # Tiêu đề Sidebar
    st.markdown('<div class="sidebar-title">🚀 Next Horizon</div>', unsafe_allow_html=True)
    
    # Input Key
    user_api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not user_api_key:
        user_api_key = st.text_input("🔑 Nhập API Key:", type="password")
    else:
        st.success("✅ Đã kết nối Key")
    
    st.markdown('<div class="custom-separator"></div>', unsafe_allow_html=True)

    if st.session_state.authenticated:
        if st.button("🏠 Trang chủ"): switch_page('welcome')
        st.caption("Công cụ")
        if st.button("🧩 Holland"): switch_page('holland')
        if st.button("🧠 Big Five"): switch_page('big_five')
        if st.button("🎯 IKIGAI"): switch_page('ikigai')
        st.caption("Tư vấn")
        if st.button("🔍 Tìm kiếm"): switch_page('search')
        if st.button("📈 Lộ trình phát triển bản thân"): switch_page('roadmap')
        if st.button("📊 Báo cáo"): switch_page('report')
        if st.button("👨‍🏫 Gặp chuyên gia"): switch_page('expert')
        
        st.markdown('<div class="custom-separator"></div>', unsafe_allow_html=True)
        
        if st.button("🤖 Chat AI"): switch_page('chat')
        if st.button("Đăng xuất"):
            st.session_state.authenticated = False
            st.rerun()

# --- 7. MÀN HÌNH CHÍNH ---

# --- LOGIN ---
if not st.session_state.authenticated:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        render_image_safe("login.png", width=150, fallback_icon="🔐")
        st.markdown("<h2 style='text-align: center; color: #004A8D;'>CỔNG ĐĂNG NHẬP</h2>", unsafe_allow_html=True)
        st.info("Chào mừng bạn đến với Ứng dụng Hướng nghiệp Next Horizon")
        
        # THÊM LINK KHẢO SÁT
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <a href="https://forms.gle/cJLw7QwrDXyAHM8m7" target="_blank" style="text-decoration: none; color: #004A8D; font-weight: bold; background-color: #e3f2fd; padding: 10px 15px; border-radius: 8px;">
                👉 Chưa có mã? Nhấn vào đây để đăng ký
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_input("Mời bạn nhập mã xác nhận vào đây:", key="input_code", on_change=verify_code, type="password")
        if st.session_state.auth_error: st.error(st.session_state.auth_error)

# --- WELCOME ---
elif st.session_state.page == 'welcome':
    st.markdown('<p class="main-header">NEXT HORIZON</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Câu lạc bộ định hướng nghề nghiệp - UK Academy</p>', unsafe_allow_html=True)
    
    # Hàng 1
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.info("🧩 **Trắc nghiệm Holland**\n\nTìm ra nhóm sở thích nghề nghiệp phù hợp nhất với bạn.")
        if st.button("Bắt đầu Holland", key="wc_h"): switch_page('holland')
    with r1c2:
        st.warning("🎯 :red[**Khám phá IKIGAI**]\n\n:red[Tìm điểm giao thoa của Đam mê, Kỹ năng và Nhu cầu xã hội.]")
        if st.button("Bắt đầu IKIGAI", key="wc_i"): switch_page('ikigai')

    # Hàng 2
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
        <div style="
            background-color: #FFF3E0; 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #FFE0B2;
            margin-bottom: 10px;
        ">
            <h4 style="color: #E65100; text-shadow: 1px 1px 1px rgba(0,0,0,0.1); font-weight: 800; margin: 0;">🤖 Trợ lý AI</h4>
            <p style="color: #BF360C; font-weight: 600; margin: 5px 0 0 0;">Hỏi đáp mọi lúc mọi nơi</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Chat với AI"): switch_page('chat')
        
    with r3c2:
        st.markdown("""
        <div style="
            background-color: #E3F2FD; 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #BBDEFB;
            margin-bottom: 10px;
        ">
            <h4 style="color: #0D47A1; text-shadow: 1px 1px 1px rgba(0,0,0,0.1); font-weight: 800; margin: 0;">👨‍🏫 Chuyên gia Tư vấn</h4>
            <p style="color: #01579B; font-weight: 600; margin: 5px 0 0 0;">Kết nối trực tiếp với thầy cô</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Gặp Chuyên gia"): switch_page('expert')

# --- HOLLAND ---
elif st.session_state.page == 'holland':
    if st.session_state.holland_step == 'landing':
        # --- NAV BAR (MOBILE FRIENDLY: 50/50) ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_l_h"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_l_h"): switch_page('welcome'); st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Mobile: Cột ảnh (1) sẽ tự động xếp trên cột chữ (1.5)
        col_img, col_text = st.columns([1, 1.5])
        with col_img: render_image_safe("holland.png", width=350, fallback_icon="🧩") # width=350 sẽ tự động bị override bởi use_container_width trong render_image_safe nếu trên mobile
        with col_text:
            st.markdown("<h1 style='color: #004A8D;'>Trắc nghiệm Holland (RIASEC)</h1>", unsafe_allow_html=True)
            st.markdown("""
            <div class='intro-text'>
            <b>Mật mã Holland:</b> Trắc nghiệm Holland chính là cơ sở để bạn đối chiếu sở thích, năng lực tự nhiên của mình với yêu cầu của các nhóm ngành nghề.
            <br><br>
            Kết quả bài trắc nghiệm giúp bạn tìm ra ba kiểu tính cách của bạn tương ứng với <b>3 mật mã Holland</b>.
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("Bắt đầu trắc nghiệm Holland", type="primary"):
                if user_api_key and not st.session_state.holland_questions_ai:
                    with st.spinner("AI đang soạn thảo câu hỏi Holland cho bạn..."):
                        q_data, is_ai = generate_questions_logic(user_api_key)
                        st.session_state.holland_questions_ai = q_data
                        st.session_state.is_ai_mode = is_ai
                elif not st.session_state.holland_questions_ai:
                     st.session_state.holland_questions_ai = get_static_holland_questions()
                st.session_state.holland_step = 'intro'
                st.rerun()

    elif st.session_state.holland_step == 'intro':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_i_h"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_i_h"): st.session_state.holland_step = 'landing'; st.rerun()
            
        st.markdown("<h2 style='text-align: center;'>Hướng dẫn kiểm tra</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("""
            <div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;'>
                <p style='font-size: 1.1rem; text-align: left;'>
                ✅ Đọc kỹ từng câu hỏi và xem xét mức độ hứng thú.<br>
                ✅ Lựa chọn phương án phù hợp nhất.<br>
                ✅ Hoàn thành toàn bộ câu hỏi.
                </p>
                <hr>
                <p><b>Hãy bắt đầu bằng cách chọn giới tính:</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.radio("Giới tính", ["Nam giới", "Nữ giới"], horizontal=True, label_visibility="collapsed", key="holland_gender")
            st.write("")
            if st.button("Bắt đầu kiểm tra ngay ➡️", type="primary", use_container_width=True):
                st.session_state.holland_step = 'quiz'
                st.rerun()

    elif st.session_state.holland_step == 'quiz':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_q_h"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_q_h"): st.session_state.holland_step = 'intro'; st.rerun()
            
        questions = st.session_state.holland_questions_ai if st.session_state.holland_questions_ai else get_static_holland_questions()
        if st.session_state.is_ai_mode: st.success("✨ Câu hỏi được tạo bởi AI")
        st.progress(50)
        with st.form("holland_quiz"):
            answers = {}
            for i, q in enumerate(questions):
                st.markdown(f"<div class='quiz-container'><b>Câu {i+1}:</b> {q['text']}</div>", unsafe_allow_html=True)
                # Radio button sẽ tự động wrap trên mobile nhờ CSS mới
                answers[i] = (st.radio(f"Lựa chọn {i}", ["👎 Không thích", "😐 Trung lập", "👍 Rất thích"], key=f"hq_{i}", horizontal=True, label_visibility="collapsed"), q['type'])
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ HOÀN THÀNH & XEM KẾT QUẢ", type="primary", use_container_width=True):
                scores = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
                for i, (ch, code) in answers.items():
                    if ch == "👍 Rất thích": scores[code] += 2
                    elif ch == "😐 Trung lập": scores[code] += 1
                st.session_state.holland_scores = scores
                st.session_state.holland_step = 'result'
                st.rerun()

    elif st.session_state.holland_step == 'result':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_r_h"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_r_h"): st.session_state.holland_step = 'landing'; st.rerun()
            
        scores = st.session_state.holland_scores
        st.success("Kết quả phân tích:")
        rc1, rc2 = st.columns([1, 1])
        with rc1: st.bar_chart(scores)
        with rc2:
            top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[0]
            st.info(f"🏆 Nhóm nổi bật nhất: **{top[0]}**")
            if user_api_key:
                with st.spinner("AI đang phân tích chi tiết..."):
                    cmt = get_ai_response(f"Giải thích nhóm Holland {top[0]} và gợi ý 3 nghề nghiệp phù hợp tại Việt Nam.", user_api_key)
                    if cmt: st.markdown(f"<div class='result-card'>{cmt}</div>", unsafe_allow_html=True)
        
        st.warning("⚠️ BẠN PHẢI HOÀN THÀNH ĐỦ 3 PHẦN TRẮC NGHIỆM: HOLLAND-BIG FIVE-IKIGAI, SAU ĐÓ BẤM VÀO NÚT BÁO CÁO ĐỂ NHẬN ĐƯỢC BÁO CÁO ĐẦY ĐỦ NHẤT")
                    
        if st.button("Làm lại"):
            st.session_state.holland_questions_ai = None
            st.session_state.holland_step = 'landing'
            st.rerun()
        if st.button("Về trang chủ"):
            st.session_state.page = 'welcome'
            st.rerun()

# --- BIG FIVE ---
elif st.session_state.page == 'big_five':
    if st.session_state.big_five_step == 'landing':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_l_b"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_l_b"): switch_page('welcome'); st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_img, col_text = st.columns([1, 1.5])
        with col_img: render_image_safe("bigfive.png", width=350, fallback_icon="🧠")
        with col_text:
            st.markdown("<h1 style='color: #004A8D;'>Khám phá tính cách BIG 5</h1>", unsafe_allow_html=True)
            st.markdown("""
            <div class='intro-text'>
            <b>Trắc nghiệm Big Five</b> (OCEAN) là công cụ đánh giá tâm lý học phổ biến, mô tả tính cách qua 5 nhóm đặc điểm:
            <br>🌊 <b>Cởi mở (Openness)</b> | 🎯 <b>Tận tâm (Conscientiousness)</b> | 🗣️ <b>Hướng ngoại (Extraversion)</b> | 🤝 <b>Dễ chịu (Agreeableness)</b> | ⚡ <b>Bất ổn cảm xúc (Neuroticism)</b>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("Bắt đầu bài kiểm tra BIG 5", type="primary"):
                st.session_state.big_five_step = 'intro'
                st.rerun()

    elif st.session_state.big_five_step == 'intro':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_i_b"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_i_b"): st.session_state.big_five_step = 'landing'; st.rerun()
            
        st.markdown("<h2 style='text-align: center;'>Hướng dẫn kiểm tra</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("""
            <div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;'>
                <p style='font-size: 1.1rem; text-align: left;'>
                ✅ Trả lời trung thực dựa trên quan điểm cá nhân.<br>
                ✅ Không có câu trả lời đúng hay sai.<br>
                ✅ Hoàn thành tất cả các câu hỏi.
                </p>
                <hr>
                <p><b>Chọn giới tính của bạn:</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.radio("Giới tính", ["Nam giới", "Nữ giới"], horizontal=True, label_visibility="collapsed")
            st.write("")
            if st.button("Bắt đầu kiểm tra ngay ➡️", type="primary", use_container_width=True):
                st.session_state.big_five_step = 'quiz'
                st.rerun()

    elif st.session_state.big_five_step == 'quiz':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_q_b"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_q_b"): st.session_state.big_five_step = 'intro'; st.rerun()
            
        st.markdown("<h3 style='text-align: center; color: #555;'>Mức độ đồng ý của bạn với các nhận định sau:</h3>", unsafe_allow_html=True)
        st.progress(50)
        questions = get_big_five_questions()
        with st.form("bigfive_quiz_form"):
            answers = {}
            options = ["🔴 Hoàn toàn không đồng ý", "🟠 Không đồng ý", "⚪ Trung lập", "🟢 Đồng ý", "🔵 Đồng ý mạnh mẽ"]
            for i, q in enumerate(questions):
                st.markdown(f"<div class='quiz-container' style='text-align: center;'><div class='quiz-question'>{q['text']}</div></div>", unsafe_allow_html=True)
                choice = st.radio(f"bf_q_{i}", options, index=2, horizontal=True, key=f"choice_{i}", label_visibility="collapsed")
                answers[i] = choice
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ HOÀN THÀNH & XEM KẾT QUẢ", type="primary", use_container_width=True):
                score_map = {"🔴 Hoàn toàn không đồng ý": 1, "🟠 Không đồng ý": 2, "⚪ Trung lập": 3, "🟢 Đồng ý": 4, "🔵 Đồng ý mạnh mẽ": 5}
                final_scores = {'O': 0, 'C': 0, 'E': 0, 'A': 0, 'N': 0}
                for i, q in enumerate(questions):
                    raw = score_map[answers[i]]
                    score = 6 - raw if q['reverse'] else raw
                    final_scores[q['trait']] += score
                st.session_state.big_five_scores = final_scores
                st.session_state.big_five_step = 'result'
                st.rerun()

    elif st.session_state.big_five_step == 'result':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_r_b"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_r_b"): st.session_state.big_five_step = 'landing'; st.rerun()
            
        st.balloons()
        st.markdown("<h2 style='text-align: center; color: #004A8D;'>Kết quả Big Five</h2>", unsafe_allow_html=True)
        scores = st.session_state.big_five_scores
        c1, c2 = st.columns([1, 1])
        with c1: st.bar_chart(scores)
        with c2:
            st.write(scores)
            dominant = max(scores, key=scores.get)
            st.info(f"🏆 Đặc điểm nổi bật: **{dominant}**")
        
        if user_api_key and st.button("🤖 Phân tích chi tiết bởi AI"):
            with st.spinner("AI đang viết..."):
                res = get_ai_response(f"Phân tích Big Five: {scores}", user_api_key)
                if res: st.markdown(f"<div class='result-card'>{res}</div>", unsafe_allow_html=True)
        
        st.warning("⚠️ BẠN PHẢI HOÀN THÀNH ĐỦ 3 PHẦN TRẮC NGHIỆM: HOLLAND-BIG FIVE-IKIGAI, SAU ĐÓ BẤM VÀO NÚT BÁO CÁO ĐỂ NHẬN ĐƯỢC BÁO CÁO ĐẦY ĐỦ NHẤT")
        if st.button("Về trang chủ"):
            st.session_state.page = 'welcome'
            st.rerun()

# --- IKIGAI ---
elif st.session_state.page == 'ikigai':
    if st.session_state.ikigai_step == 'landing':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_l_i"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_l_i"): switch_page('welcome'); st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_img, col_text = st.columns([1, 1.5])
        with col_img: render_image_safe("ikigai.png", width=350, fallback_icon="🎯")
        with col_text:
            st.markdown("<h1 style='color: #004A8D;'>Khám phá Lẽ sống IKIGAI</h1>", unsafe_allow_html=True)
            st.markdown("""
            <div class='intro-text'>
            <b>Trắc nghiệm Ikigai:</b> Là sự kết hợp hài hòa giữa 4 yếu tố:
            <br>❤️ <b>Yêu thích</b> | 🌟 <b>Giỏi</b> | 🌏 <b>Thế giới cần</b> | 💰 <b>Được trả công</b>
            <div class='ikigai-benefit'><b>Mục đích sống:</b> Xác định động lực phấn đấu.</div>
            <div class='ikigai-benefit'><b>Hạnh phúc & Sức khỏe:</b> Giảm căng thẳng, sống thọ hơn.</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("Bắt đầu khám phá Ikigai", type="primary"):
                if user_api_key and not st.session_state.ikigai_questions_ai:
                    with st.spinner("AI đang soạn thảo câu hỏi Ikigai..."):
                        q_data, is_ai = generate_ikigai_questions_logic(user_api_key)
                        st.session_state.ikigai_questions_ai = q_data
                        st.session_state.is_ai_mode = is_ai
                elif not st.session_state.ikigai_questions_ai:
                     st.session_state.ikigai_questions_ai = get_static_ikigai_questions()
                st.session_state.ikigai_step = 'intro'
                st.rerun()

    elif st.session_state.ikigai_step == 'intro':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_i_i"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_i_i"): st.session_state.ikigai_step = 'landing'; st.rerun()
            
        st.markdown("<h2 style='text-align: center;'>Hướng dẫn đánh giá</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("""
            <div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;'>
                <p style='font-size: 1.1rem; text-align: left;'>
                Chúng ta sẽ đánh giá mức độ phù hợp của bạn với 4 trụ cột Ikigai.<br>
                Hãy trả lời trung thực nhất.
                </p>
                <hr>
                <p><b>Chọn giới tính của bạn:</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.radio("Giới tính", ["Nam giới", "Nữ giới"], horizontal=True, label_visibility="collapsed")
            st.write("")
            if st.button("Bắt đầu ngay ➡️", type="primary", use_container_width=True):
                st.session_state.ikigai_step = 'quiz'
                st.rerun()

    elif st.session_state.ikigai_step == 'quiz':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_q_i"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_q_i"): st.session_state.ikigai_step = 'intro'; st.rerun()
            
        st.markdown("<h3 style='text-align: center;'>Mức độ đồng ý của bạn:</h3>", unsafe_allow_html=True)
        st.progress(50)
        questions = st.session_state.ikigai_questions_ai if st.session_state.ikigai_questions_ai else get_static_ikigai_questions()
        if st.session_state.is_ai_mode: st.success("✨ Câu hỏi AI")
        
        with st.form("ikigai_quiz_form"):
            answers = {}
            options = ["🔴 Hoàn toàn sai", "🟠 Sai", "⚪ Trung lập", "🟢 Đúng", "🔵 Hoàn toàn đúng"]
            for i, q in enumerate(questions):
                cat_map = {"Love": "❤️ ĐAM MÊ", "Good": "🌟 CHUYÊN MÔN", "World": "🌏 SỨ MỆNH", "Paid": "💰 SỰ NGHIỆP"}
                cat_label = cat_map.get(q.get('category'), "")
                st.markdown(f"""
                <div class='quiz-container' style='text-align: center;'>
                    <div style='color: #888; font-size: 0.9rem; margin-bottom: 5px;'>{cat_label}</div>
                    <div class='quiz-question'>{q['text']}</div>
                </div>
                """, unsafe_allow_html=True)
                choice = st.radio(f"ik_q_{i}", options, index=2, horizontal=True, key=f"ik_choice_{i}", label_visibility="collapsed")
                answers[i] = choice
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✅ XEM KẾT QUẢ IKIGAI", type="primary", use_container_width=True):
                score_map = {"🔴 Hoàn toàn sai": 1, "🟠 Sai": 2, "⚪ Trung lập": 3, "🟢 Đúng": 4, "🔵 Hoàn toàn đúng": 5}
                cat_totals = {'Love': 0, 'Good': 0, 'World': 0, 'Paid': 0}
                cat_counts = {'Love': 0, 'Good': 0, 'World': 0, 'Paid': 0}
                for i, q in enumerate(questions):
                    raw = score_map[answers[i]]
                    cat = q.get('category', 'Love')
                    if cat not in cat_totals: cat = 'Love'
                    cat_totals[cat] += raw
                    cat_counts[cat] += 1
                final_scores = {}
                display_map = {'Love': 'Yêu thích', 'Good': 'Giỏi', 'World': 'Xã hội cần', 'Paid': 'Thu nhập'}
                for cat in cat_totals:
                    avg = (cat_totals[cat] / cat_counts[cat]) * 2 if cat_counts[cat] > 0 else 0
                    final_scores[display_map[cat]] = avg
                st.session_state.ikigai_scores = final_scores
                st.session_state.ikigai_step = 'result'
                st.rerun()

    elif st.session_state.ikigai_step == 'result':
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="nav_h_r_i"): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="nav_b_r_i"): st.session_state.ikigai_step = 'landing'; st.rerun()
            
        st.balloons()
        st.markdown("<h2 style='text-align: center; color: #004A8D;'>Biểu đồ IKIGAI của bạn</h2>", unsafe_allow_html=True)
        scores = st.session_state.ikigai_scores
        c1, c2 = st.columns([1, 1])
        with c1: st.bar_chart(scores)
        with c2:
            avg = sum(scores.values()) / 4
            st.metric("Điểm trung bình", f"{avg:.1f}/10")
            if avg >= 8: st.success("Tuyệt vời! Bạn đang sống rất gần với Ikigai.")
            elif avg >= 5: st.info("Khá tốt! Hãy cải thiện các yếu tố còn thấp.")
            else: st.warning("Cần nỗ lực cân bằng hơn.")
        
        if user_api_key and st.button("🤖 Nhờ AI tư vấn"):
            with st.spinner("AI đang suy nghĩ..."):
                res = get_ai_response(f"Tư vấn Ikigai với điểm số: {scores}", user_api_key)
                if res: st.markdown(f"<div class='result-card'>{res}</div>", unsafe_allow_html=True)
        
        st.warning("⚠️ BẠN PHẢI HOÀN THÀNH ĐỦ 3 PHẦN TRẮC NGHIỆM: HOLLAND-BIG FIVE-IKIGAI, SAU ĐÓ BẤM VÀO NÚT BÁO CÁO ĐỂ NHẬN ĐƯỢC BÁO CÁO ĐẦY ĐỦ NHẤT")
        if st.button("Về trang chủ"):
            st.session_state.page = 'welcome'
            st.rerun()

# --- SEARCH ---
elif st.session_state.page == 'search':
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="nav_h_s"): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="nav_b_s"): switch_page('welcome'); st.rerun()
        
    render_image_safe("search.png", width=100, fallback_icon="🔍")
    st.header("Tìm kiếm Ngành nghề")
    q = st.text_input("Nhập ngành:")
    if q and st.button("Tìm kiếm"):
        if user_api_key:
            res = get_ai_response(f"Thông tin ngành {q} ở VN", user_api_key)
            if res: st.markdown(res)
            else: st.error("Lỗi AI.")
        else: st.warning("Cần Key.")

# --- ROADMAP ---
elif st.session_state.page == 'roadmap':
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="nav_h_rm"): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="nav_b_rm"): switch_page('welcome'); st.rerun()
        
    render_image_safe("roadmap.png", width=100, fallback_icon="📈")
    st.header("Lộ trình phát triển bản thân")
    
    holland = st.session_state.holland_scores
    bigfive = st.session_state.big_five_scores
    ikigai = st.session_state.ikigai_scores
    
    if not (holland and bigfive and ikigai):
        st.warning("⚠️ Để xây dựng lộ trình chính xác nhất, bạn cần hoàn thành đủ 3 bài trắc nghiệm.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"- Holland: {'✅' if holland else '❌'}")
            if not holland and st.button("Làm Holland ngay"): switch_page('holland')
        with c2:
            st.write(f"- Big Five: {'✅' if bigfive else '❌'}")
            if not bigfive and st.button("Làm Big Five ngay"): switch_page('big_five')
        with c3:
            st.write(f"- Ikigai: {'✅' if ikigai else '❌'}")
            if not ikigai and st.button("Làm Ikigai ngay"): switch_page('ikigai')
    else:
        st.success("✅ Bạn đã hoàn thành đủ các bài đánh giá! Hệ thống sẵn sàng phân tích.")
        if st.button("🚀 Lập lộ trình phát triển chuyên sâu với AI", type="primary"):
            if user_api_key:
                with st.spinner("Chuyên gia AI đang phân tích..."):
                    prompt = f"""
                    Dựa trên kết quả: Holland={holland}, Big Five={bigfive}, Ikigai={ikigai}.
                    Hãy đóng vai Mentor, thiết kế 'Lộ trình phát triển bản thân' chiến lược:
                    1. Gợi ý 3 vị trí công việc.
                    2. Phân tích điểm mạnh/yếu.
                    3. Kế hoạch hành động (3 tháng, 1 năm, 3 năm).
                    Trình bày chuyên nghiệp.
                    """
                    res = get_ai_response(prompt, user_api_key)
                    if res: st.markdown(res)
                    else: st.error("Lỗi AI.")
            else: st.warning("Cần API Key.")

# --- REPORT ---
elif st.session_state.page == 'report':
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="nav_h_rp"): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="nav_b_rp"): switch_page('welcome'); st.rerun()
        
    render_image_safe("report.png", width=100, fallback_icon="📊")
    st.header("Báo cáo Tổng hợp")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Holland**")
        if st.session_state.holland_scores: st.bar_chart(st.session_state.holland_scores, height=150)
        else: st.caption("Chưa làm")
    with c2:
        st.markdown("**Big Five**")
        if st.session_state.big_five_scores: st.bar_chart(st.session_state.big_five_scores, height=150)
        else: st.caption("Chưa làm")
    with c3:
        st.markdown("**Ikigai**")
        if st.session_state.ikigai_scores: st.bar_chart(st.session_state.ikigai_scores, height=150)
        else: st.caption("Chưa làm")
    
    st.divider()
    if user_api_key and st.button("Phân tích tổng hợp bằng AI"):
        with st.spinner("AI đang viết..."):
            prompt = f"Tổng hợp: Holland={st.session_state.holland_scores}, BigFive={st.session_state.big_five_scores}, Ikigai={st.session_state.ikigai_scores}. Gợi ý nghề."
            res = get_ai_response(prompt, user_api_key)
            if res: st.success(res)
            else: st.error("Lỗi AI.")

# --- CHAT ---
elif st.session_state.page == 'chat':
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="nav_h_c"): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="nav_b_c"): switch_page('welcome'); st.rerun()
        
    render_image_safe("chat.png", width=100, fallback_icon="🤖")
    st.header("Chat AI")
    for m in st.session_state.chat_history: st.chat_message(m["role"]).write(m["content"])
    if p := st.chat_input("Hỏi tôi..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        st.chat_message("user").write(p)
        if user_api_key:
            with st.spinner("Chuyên gia hướng nghiệp AI đang suy nghĩ..."):
                r = get_ai_response(p, user_api_key)
            if r:
                st.session_state.chat_history.append({"role": "assistant", "content": r})
                st.chat_message("assistant").write(r)
            else: st.error("Lỗi AI.")

# --- EXPERT ---
elif st.session_state.page == 'expert':
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="nav_h_e"): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="nav_b_e"): switch_page('welcome'); st.rerun()
        
    st.header("👨‍🏫 Gặp gỡ Chuyên gia Hướng nghiệp")
    
    # Banner cho GPT TS Vũ Việt Anh
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px;">
        <h4 style="color: #2e7d32; margin: 0;">🎁 Quà tặng từ TS. Vũ Việt Anh</h4>
        <p style="margin: 5px 0;">Chatbot GPT chuyên sâu hỗ trợ định hướng nghề nghiệp 24/7.</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("👉 Trò chuyện ngay với GPT TS. Vũ Việt Anh", "https://chatgpt.com/g/g-6942112d74cc8191860a9938ae29b14c-huong-nghiep-cung-ts-vu-viet-anh", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    ec1, ec2, ec3 = st.columns(3)

    with ec1:
        st.markdown('<div class="result-card" style="height: 100%;">', unsafe_allow_html=True)
        if os.path.exists("nguyen_van_thanh.jpg"): 
            st.image("nguyen_van_thanh.jpg", use_container_width=True)
        st.markdown("### TS. Nguyễn Văn Thanh\nChuyên gia tư vấn hướng nghiệp\n* SĐT: 0916.272.424\n* Email: nvthanh183@gmail.com")
        st.markdown('</div>', unsafe_allow_html=True)

    with ec2:
        st.markdown('<div class="result-card" style="height: 100%; border-left: 5px solid #2e7d32;">', unsafe_allow_html=True)
        if os.path.exists("vu_viet_anh.jpg"): 
            st.image("vu_viet_anh.jpg", use_container_width=True)
        elif os.path.exists("vuvietanh.jpg"):
             st.image("vuvietanh.jpg", use_container_width=True)
             
        st.markdown("""
        ### TS. Vũ Việt Anh
        Chuyên gia định hướng nghề nghiệp  
        Chủ tịch Hội đồng Cố vấn EDA INSTITUTE  
        * SĐT: 098 4736999
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with ec3:
        st.markdown('<div class="result-card" style="height: 100%;">', unsafe_allow_html=True)
        if os.path.exists("pham_cong_thanh.jpg"): 
            st.image("pham_cong_thanh.jpg", use_container_width=True)
        st.markdown("### ThS. Phạm Công Thành\nChuyên gia định hướng nghề nghiệp\n* SĐT: 038.7315.722\n* Email: phamcongthanh92@gmail.com")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.link_button("💬 Chat ngay qua Messenger", "https://www.facebook.com/messages/t/100001857808197", use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""<div class='footer'>@2025 sản phẩm thuộc về Câu lạc bộ hướng nghiệp Next Horizon - UK Academy Hạ Long</div>""", unsafe_allow_html=True)

