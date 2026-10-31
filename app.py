import streamlit as st
import google.generativeai as genai
import time
import json
import random
import os
import base64

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Next Horizon - Hướng nghiệp",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
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
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.96); 
            border-radius: 15px;
            padding: 2rem !important;
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        section[data-testid="stSidebar"] {{
            background-color: rgba(245, 247, 250, 0.96);
            border-right: 1px solid #ddd;
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
    html, body, [class*="css"], .stMarkdown, .stText, p, div { 
        font-family: 'Inter', sans-serif; 
        color: #111111 !important;
    }
    header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"], div[data-testid="stDecoration"] {
        display: none !important;
    }
    .main-header {
        font-size: 3rem !important; font-weight: 900 !important;
        background: -webkit-linear-gradient(45deg, #004A8D, #0088cc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: -20px !important; margin-bottom: 0rem !important;
        text-transform: uppercase; letter-spacing: -1px;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem !important; font-weight: 700 !important; color: #333 !important;
        text-align: center; margin-bottom: 15px !important;
    }
    .sidebar-title {
        font-size: 1.5rem !important; font-weight: 800 !important; color: #004A8D !important;
        text-align: center !important; margin-bottom: 0.5rem !important;
    }
    div[data-testid="stButton"] > button {
        width: 100%; border-radius: 10px; height: 3rem; font-weight: 600;
        border: 1px solid #ccc; background-color: #ffffff; color: #004A8D !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        background-color: #f0f7ff !important; color: #003366 !important; border-color: #003366;
    }
    .result-card {
        background: #ffffff; padding: 20px; border-radius: 12px; 
        border-left: 5px solid #004A8D; margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); color: #000 !important;
    }
    .footer {
        text-align: center; color: #555 !important; font-size: 0.8rem; font-weight: 600;
        margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd;
    }
    /* Style riêng cho bảng câu hỏi Big Five */
    .bigfive-row {
        padding: 10px 0; border-bottom: 1px solid #eee;
    }
    @media (max-width: 768px) {
        .main-header { font-size: 2rem !important; }
        .block-container { padding: 1rem !important; }
        .stRadio > div { flex-direction: column; gap: 10px; }
    }
    @media (min-width: 769px) {
        .stRadio > div { flex-direction: row; gap: 15px; flex-wrap: wrap; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. KHỞI TẠO STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'auth_error' not in st.session_state: st.session_state.auth_error = ""

if 'holland_scores' not in st.session_state: st.session_state.holland_scores = None
if 'big_five_scores' not in st.session_state: st.session_state.big_five_scores = None
if 'ikigai_scores' not in st.session_state: st.session_state.ikigai_scores = None

if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'holland_step' not in st.session_state: st.session_state.holland_step = 'landing'
if 'big_five_step' not in st.session_state: st.session_state.big_five_step = 'landing'
if 'ikigai_step' not in st.session_state: st.session_state.ikigai_step = 'landing'
if 'holland_questions_ai' not in st.session_state: st.session_state.holland_questions_ai = None
if 'ikigai_questions_ai' not in st.session_state: st.session_state.ikigai_questions_ai = None
if 'is_ai_mode' not in st.session_state: st.session_state.is_ai_mode = False

# --- 4. HÀM LOGIC ---
def switch_page(page_name):
    st.session_state.page = page_name
    if page_name == 'holland': st.session_state.holland_step = 'landing'
    if page_name == 'big_five': st.session_state.big_five_step = 'landing'
    if page_name == 'ikigai': st.session_state.ikigai_step = 'landing'

def verify_code():
    code = st.session_state.input_code.strip().upper() if "input_code" in st.session_state else ""
    if code in ["NEXT2025", "NEXT2026"]: 
        st.session_state.authenticated = True
        st.session_state.auth_error = ""
    else:
        st.session_state.auth_error = "❌ Mã xác nhận không đúng."

def render_image_safe(image_name, width=None):
    if os.path.exists(image_name):
        st.image(image_name, width=width)

# Lấy API Key an toàn từ biến môi trường (Render/OS) hoặc Streamlit secrets, tránh crash nếu không có secrets.toml
api_key = os.environ.get("GEMINI_API_KEY", None)
if not api_key:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None
if not api_key and "api_key" in st.session_state:
    api_key = st.session_state["api_key"]

def get_ai_response(prompt, api_key_val=None):
    key_to_use = api_key_val if api_key_val else api_key
    if not key_to_use: return None
    try:
        genai.configure(api_key=key_to_use)
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and hasattr(response, 'text') and response.text:
                    return response.text
            except Exception:
                continue
        return None
    except Exception:
        return None

def generate_questions_logic(api_key_val):
    if not api_key_val: return get_static_holland_questions(), False
    try:
        p = f"Tạo 12 câu trắc nghiệm Holland (RIASEC) ngắn gọn cho HSVN. Seed: {random.randint(1,1000)}. JSON Only: [{{'text': '...', 'type': 'R'}}]"
        res = get_ai_response(p, api_key_val)
        if res:
            s = res.find('[')
            e = res.rfind(']') + 1
            if s != -1 and e != -1:
                return json.loads(res[s:e]), True
    except: pass
    return get_static_holland_questions(), False

def generate_ikigai_questions_logic(api_key_val):
    if not api_key_val: return get_static_ikigai_questions(), False
    try:
        p = f"Tạo 12 câu trắc nghiệm Ikigai (Love, Good, World, Paid). Seed: {random.randint(1,1000)}. JSON Only."
        res = get_ai_response(p, api_key_val)
        if res:
            s = res.find('[')
            e = res.rfind(']') + 1
            if s != -1 and e != -1:
                return json.loads(res[s:e]), True
    except: pass
    return get_static_ikigai_questions(), False

# --- DỮ LIỆU CÂU HỎI ---
def get_holland_detailed_questions():
    return {
        "R": [
            "Tự mua và lắp ráp máy vi tính theo ý mình",
            "Lắp ráp tủ theo hướng dẫn của sách hướng dẫn hoặc trang mạng",
            "Trang điểm cho mình hay cho bạn theo hướng dẫn của sách hướng dẫn hoặc trang mạng",
            "Cắt tỉa cây cảnh",
            "Tháo mở điện thoại di động hay máy tính ra để tìm hiểu",
            "Tham gia một chuyến du lịch thám hiểm (như khám phá hang động, núi rừng)",
            "Chăm sóc vật nuôi",
            "Sửa xe, như xe đạp, xe máy (các lỗi nhỏ)",
            "Làm đồ nội thất",
            "Lắp ráp máy vi tính",
            "Leo núi",
            "Đóng gói đồ đạc vào thùng",
            "Chơi một môn thể thao",
            "Tham gia chuyến đạp xe xuyên quốc gia (từ TPHCM ra Hà Nội, từ Hà Nội vào TPHCM)"
        ],
        "I": [
            "Tham quan bảo tàng",
            "Tìm hiểu sự hình thành của các vì sao và vũ trụ",
            "Tìm hiểu về văn hóa một quốc gia mà mình thích",
            "Tìm hiểu về tâm lý con người",
            "Đọc một cuốn sách về tương lai của loài người trong một triệu năm nữa",
            "Đọc sách, báo hay xem trang tin tức về khoa học",
            "Tìm hiểu về cảm xúc con người",
            "Được xem một ca mổ tim",
            "Tìm hiểu nguồn gốc của một dịch bệnh, nguồn gốc loài người, v.v",
            "Đọc các bài báo về ảnh hưởng của AI (trí tuệ nhân tạo) lên nghề nghiệp tương lai",
            "Tìm hiểu về thế giới động vật (qua các kênh tìm hiểu khoa học)",
            "Phát minh xe điện",
            "Tiến hành thí nghiệm hóa học",
            "Nghiên cứu về chế độ dinh dưỡng"
        ],
        "A": [
            "Tạo ra một tác phẩm nghệ thuật, tranh, câu chuyện",
            "Viết truyện ngắn",
            "Chứng tỏ năng lực nghệ thuật của bản thân với người khác (nói lên suy nghĩ/quan điểm qua tác phẩm nghệ thuật)",
            "Chơi trong một ban nhạc",
            "Chỉnh sửa phim",
            "Thuyết trình hoặc thiết kế, theo ý tưởng của mình",
            "Vẽ phim hoạt hình",
            "Hát trong một ban nhạc",
            "Biểu diễn nhảy hiện đại",
            "Dẫn chương trình (MC) cho một sự kiện",
            "Độc thoại hay kể chuyện trên đài phát thanh/phần mềm",
            "Viết kịch bản cho phim hoặc chương trình truyền hình",
            "Chụp ảnh cho các sự kiện trong cuộc sống hoặc sự kiện nghệ thuật",
            "Viết một bài phê bình phim cho bộ phim mình thích/ghét nhất"
        ],
        "S": [
            "Giúp người khác chọn nghề nghiệp phù hợp",
            "Kết nối hai người bạn với nhau",
            "Dạy cho bạn mình cách giảm cân qua ăn uống đúng cách",
            "Tham gia ngày trái đất bằng cách lượm rác hay tắt điện",
            "Hướng dẫn khách nước ngoài chỗ ăn ngon",
            "Cứu động vật bị bỏ rơi ngoài đường",
            "Tham gia vào một cuộc thảo luận nhóm nhỏ",
            "Kể chuyện cười cho bạn bè nghe",
            "Dạy em nhỏ chơi một trò chơi hay một môn thể thao",
            "Lắng nghe bạn bè tâm sự về vấn đề cá nhân của họ",
            "Giúp bạn bè giải quyết vấn đề liên quan đến tình yêu",
            "Tham gia một chuyến đi từ thiện",
            "Giúp một dự án cộng đồng trong sức của mình",
            "Sẵn sàng giúp thầy cô, bạn bè khi thấy họ cần"
        ],
        "E": [
            "Tham gia ban đại diện học sinh ở trường",
            "Làm cán bộ lớp",
            "Bán hàng trực tuyến",
            "Quản lý một cửa hàng trực tuyến",
            "Học về thị trường chứng khoán (bitcoin, cổ phiếu, tiền tệ, v.v.)",
            "Tham gia một khóa học về quản lý tài chính",
            "Tham dự một trại huấn luyện kỹ năng lãnh đạo dành cho lứa tuổi thanh thiếu niên",
            "Lập kế hoạch làm việc cho thành viên nhóm",
            "Kiếm tiền bằng cách kinh doanh trực tuyến",
            "Nói trước đám đông về một đề tài mình thích",
            "Tham gia xây dựng các luật lệ mới cho lớp/trường",
            "Thuyết phục cha mẹ theo ý mình",
            "Tổ chức đi chơi cho một nhóm bạn",
            "Kiếm tiền bằng cách làm thêm"
        ],
        "C": [
            "Mở tài khoản tiết kiệm",
            "Lập kế hoạch chi tiêu hàng tháng",
            "Chuẩn bị ngân sách cho chuyến đi chơi tập thể lớp",
            "Chuẩn bị cho buổi trình bày trước lớp",
            "Lập kế hoạch cho kỳ nghỉ hè/Tết",
            "Đếm và sắp xếp tiền",
            "Sắp xếp lại bàn học",
            "Viết kế hoạch học tập cho học kỳ mới",
            "Hoàn tất bài tập theo đúng hạn được giao",
            "Dò lỗi chính tả cho phụ đề của một phim ưa thích",
            "Học một khóa vi tính văn phòng và biết cách sắp xếp văn bản, thư mục sao cho chỉn chu",
            "Làm thủ quỹ cho lớp",
            "Sắp xếp lại tủ quần áo cá nhân",
            "Giúp ba/mẹ quản lý tiền chợ của gia đình (mua gì, mua khi nào, mua bao nhiêu)"
        ]
    }

def get_static_holland_questions():
    # Placeholder for potential fallback, though detailed list is preferred
    return get_holland_detailed_questions()

# --- BỘ 120 CÂU HỎI BIG FIVE ---
def get_big_five_120_questions():
    # Chuỗi câu hỏi do người dùng cung cấp
    raw_questions = [
        "Tôi là người hay lo lắng.", "Tôi dễ dàng kết bạn với người khác.", "Tôi có trí tưởng tượng phong phú.", "Tôi tin tưởng người khác.", "Tôi thường hoàn thành công việc một cách hiệu quả.",
        "Tôi dễ nổi giận.", "Tôi thực sự thích những buổi tiệc và các cuộc tụ họp đông người.", "Tôi cho rằng nghệ thuật là quan trọng.", "Đôi khi tôi lừa dối người khác để đạt được mục đích của mình.", "Tôi không thích sự bừa bộn – tôi thích mọi thứ gọn gàng, ngăn nắp.",
        "Tôi thường cảm thấy buồn.", "Tôi thích nắm quyền chủ động trong các tình huống và sự kiện.", "Tôi trải nghiệm những cảm xúc sâu sắc và đa dạng.", "Tôi thích giúp đỡ người khác.", "Tôi luôn giữ lời hứa.",
        "Tôi thấy khó khăn khi chủ động tiếp cận người khác.", "Tôi luôn bận rộn – lúc nào cũng trong trạng thái vận động.", "Tôi thích sự đa dạng hơn là lối sống lặp lại theo thói quen.", "Tôi thích tranh luận gay gắt hoặc đối đầu.", "Tôi làm việc rất chăm chỉ.",
        "Đôi khi tôi nuông chiều bản thân quá mức.", "Tôi yêu thích sự kích thích và cảm giác mạnh.", "Tôi thích đọc những cuốn sách và bài viết mang tính thử thách trí tuệ.", "Tôi tin rằng mình giỏi hơn người khác.", "Tôi luôn chuẩn bị kỹ lưỡng cho mọi việc.",
        "Tôi dễ hoảng loạn.", "Tôi là người vui vẻ, lạc quan.", "Tôi có xu hướng ủng hộ sự tiến bộ và cải cách.", "Tôi cảm thông với những người vô gia cư.", "Tôi rất bộc phát – thường hành động mà không suy nghĩ kỹ.",
        "Tôi thường lo sợ những điều tồi tệ nhất sẽ xảy ra.", "Tôi cảm thấy thoải mái khi ở xung quanh người khác.", "Tôi thích những tưởng tượng bay bổng, táo bạo.", "Tôi tin rằng nhìn chung con người có những ý định tốt.", "Khi tôi làm việc gì, tôi luôn cố gắng làm thật tốt.",
        "Tôi dễ bị cáu gắt.", "Trong các buổi tiệc, tôi thường trò chuyện với rất nhiều người khác nhau.", "Tôi nhìn thấy vẻ đẹp trong những điều mà người khác có thể không để ý.", "Tôi không ngại gian lận để tiến xa hơn.", "Tôi thường quên đặt đồ vật về đúng vị trí của chúng.",
        "Đôi khi tôi không thích chính bản thân mình.", "Tôi cố gắng nắm quyền chủ động, dẫn dắt người khác.", "Tôi là người giàu sự đồng cảm – tôi cảm nhận được cảm xúc của người khác.", "Tôi quan tâm đến người khác.", "Tôi luôn nói sự thật.",
        "Tôi ngại thu hút sự chú ý về phía mình.", "Tôi không bao giờ ngồi yên – lúc nào cũng vận động.", "Tôi thích gắn bó với những điều quen thuộc hơn là thử cái mới.", "Tôi quát mắng, la hét với người khác.", "Tôi làm nhiều hơn những gì được mong đợi ở mình.",
        "Tôi hiếm khi nuông chiều bản thân quá mức.", "Tôi chủ động tìm kiếm những cuộc phiêu lưu.", "Tôi tránh các cuộc thảo luận mang tính triết học.", "Tôi đánh giá cao bản thân mình.", "Tôi hoàn thành công việc và thực hiện đúng kế hoạch đã đề ra.",
        "Tôi dễ bị choáng ngợp bởi các sự kiện.", "Tôi có rất nhiều niềm vui trong cuộc sống.", "Tôi tin rằng không có đúng – sai tuyệt đối.", "Tôi cảm thấy thương cảm với những người kém may mắn hơn mình.", "Tôi thường đưa ra quyết định bốc đồng.",
        "Tôi sợ nhiều thứ.", "Tôi tránh tiếp xúc với người khác nếu có thể.", "Tôi thích mơ mộng, suy tưởng.", "Tôi tin vào những gì người khác nói.", "Tôi xử lý công việc một cách có hệ thống.",
        "Tôi thường xuyên nổi nóng.", "Tôi thích ở một mình.", "Tôi không thích thơ ca.", "Đôi khi tôi lợi dụng người khác.", "Đôi khi tôi để mọi thứ bừa bộn.",
        "Đôi khi tôi cảm thấy chán nản, buồn bực.", "Tôi thường kiểm soát và làm chủ các tình huống.", "Tôi hiếm khi để ý đến phản ứng và cảm xúc của chính mình.", "Tôi thờ ơ với cảm xúc của người khác.", "Tôi phá vỡ các quy tắc.",
        "Tôi chỉ thực sự cảm thấy thoải mái khi ở bên bạn bè.", "Tôi làm rất nhiều việc trong thời gian rảnh.", "Tôi không thích sự thay đổi.", "Tôi xúc phạm người khác.", "Tôi chỉ làm vừa đủ để hoàn thành yêu cầu.",
        "Tôi dễ dàng kiểm soát những cám dỗ.", "Tôi thích mạo hiểm.", "Tôi gặp khó khăn khi hiểu các ý tưởng trừu tượng.", "Tôi có đánh giá cao về bản thân.", "Tôi lãng phí thời gian.",
        "Tôi cảm thấy mình không đủ khả năng giải quyết mọi việc.", "Tôi yêu cuộc sống.", "Tôi tin rằng pháp luật cần được thực thi một cách nghiêm khắc.", "Tôi không quan tâm đến vấn đề của người khác.", "Tôi lao vào hành động quá nhanh.",
        "Tôi thường cảm thấy lo lắng.", "Tôi dễ dàng kết bạn.", "Tôi có trí tưởng tượng phong phú.", "Tôi tin rằng hầu hết mọi người đều có ý tốt.", "Tôi hoàn thành công việc một cách cẩn thận.",
        "Tôi dễ bị kích động, cáu gắt.", "Tôi không thích tụ tập đông người.", "Tôi yêu thích nghệ thuật.", "Tôi sẵn sàng lợi dụng người khác để đạt được mục tiêu.", "Tôi luôn giữ mọi thứ ngăn nắp, trật tự.",
        "Tôi thường cảm thấy buồn bã.", "Tôi có khả năng dẫn dắt và gây ảnh hưởng đến người khác.", "Tôi nhạy cảm với cảm xúc của bản thân.", "Tôi quan tâm đến cảm xúc và nhu cầu của người khác.", "Tôi luôn tuân thủ các quy tắc.",
        "Tôi cảm thấy thoải mái khi là trung tâm của sự chú ý.", "Tôi sống rất năng động.", "Tôi thích sự ổn định và quen thuộc.", "Tôi dễ làm tổn thương người khác bằng lời nói.", "Tôi luôn cố gắng làm nhiều hơn mức được yêu cầu.",
        "Tôi có khả năng tự kiểm soát bản thân rất tốt.", "Tôi thích những trải nghiệm mới và mạo hiểm.", "Tôi hiểu tốt các ý tưởng phức tạp và trừu tượng.", "Tôi hài lòng với chính mình.", "Tôi sử dụng thời gian một cách hiệu quả.",
        "Tôi tự tin vào khả năng giải quyết vấn đề của mình.", "Tôi cảm thấy hạnh phúc và lạc quan.", "Tôi tôn trọng luật pháp và các chuẩn mực xã hội.", "Tôi sẵn sàng giúp đỡ người khác khi họ gặp khó khăn.", "Tôi suy nghĩ kỹ trước khi hành động."
    ]
    
    # Quy tắc gán nhóm tính cách (Chu kỳ 5: N, E, O, A, C)
    traits_order = ['N', 'E', 'O', 'A', 'C']
    formatted_questions = []
    
    for i, text in enumerate(raw_questions):
        trait = traits_order[i % 5]
        formatted_questions.append({"text": text, "trait": trait})
        
    return formatted_questions

def get_static_ikigai_questions():
    return [
        {"text": "Tôi thường xuyên cảm thấy hạnh phúc khi làm những việc mình thích.", "category": "Love"},
        {"text": "Tôi có những sở thích đặc biệt muốn dành thời gian cho chúng.", "category": "Love"},
        {"text": "Mọi người thường khen ngợi kỹ năng của tôi.", "category": "Good"},
        {"text": "Tôi tự tin giải quyết vấn đề thuộc sở trường.", "category": "Good"},
        {"text": "Tôi quan tâm đến các vấn đề xã hội.", "category": "World"},
        {"text": "Tôi muốn công việc mang lại giá trị cho cộng đồng.", "category": "World"},
        {"text": "Tôi có kỹ năng mà thị trường sẵn sàng trả lương.", "category": "Paid"},
        {"text": "Tôi ưu tiên nghề nghiệp có thu nhập ổn định.", "category": "Paid"}
    ]

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo1.png"): st.image("logo1.png", width=120)
    st.markdown('<div class="sidebar-title">🚀 Next Horizon</div>', unsafe_allow_html=True)
    
    if not api_key:
        user_key = st.text_input("🔑 Nhập API Key:", type="password", key="user_api_key_input", help="Nhập Gemini API Key để kích hoạt tính năng AI")
        if user_key:
            api_key = user_key
            st.session_state["api_key"] = user_key
    
    st.markdown("---")
    if st.session_state.authenticated:
        if st.button("🏠 Trang chủ", use_container_width=True): switch_page('welcome'); st.rerun()
        
        st.caption("CÔNG CỤ ĐÁNH GIÁ")
        if st.button("🧩 Holland", use_container_width=True): switch_page('holland'); st.rerun()
        if st.button("🧠 Big Five", use_container_width=True): switch_page('big_five'); st.rerun()
        if st.button("🎯 Ikigai", use_container_width=True): switch_page('ikigai'); st.rerun()
        
        st.caption("TƯ VẤN & HỖ TRỢ")
        if st.button("🔍 Tra cứu ngành nghề", use_container_width=True): switch_page('search'); st.rerun()
        if st.button("📈 Lộ trình phát triển", use_container_width=True): switch_page('roadmap'); st.rerun()
        if st.button("📊 Báo cáo tổng hợp", use_container_width=True): switch_page('report'); st.rerun()
        if st.button("👨‍🏫 Gặp chuyên gia", use_container_width=True): switch_page('expert'); st.rerun()
        
        st.markdown("---")
        if st.button("🤖 Chat AI", use_container_width=True): switch_page('chat'); st.rerun()
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# --- 6. GIAO DIỆN CHÍNH ---

# --- LOGIN ---
if not st.session_state.authenticated:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if os.path.exists("login_icon.png"):
            render_image_safe("login_icon.png", width=150)
        elif os.path.exists("login.png"):
            render_image_safe("login.png", width=150)
        st.markdown("<h2 style='text-align: center; color: #004A8D;'>CỔNG ĐĂNG NHẬP</h2>", unsafe_allow_html=True)
        st.info("Chào mừng bạn đến với Ứng dụng Hướng nghiệp Next Horizon")
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <a href="https://forms.gle/cJLw7QwrDXyAHM8m7" target="_blank" style="text-decoration: none; color: #004A8D; font-weight: bold; background-color: #e3f2fd; padding: 10px 15px; border-radius: 8px;">
                👉 Chưa có mã? Nhấn vào đây để đăng ký
            </a>
        </div>
        """, unsafe_allow_html=True)
        st.text_input("Mời bạn nhập mã xác nhận vào đây:", key="input_code", on_change=verify_code, type="password")
        if st.button("Đăng nhập 🚀", type="primary", use_container_width=True):
            verify_code()
            if st.session_state.authenticated:
                st.rerun()
        if st.session_state.auth_error: st.error(st.session_state.auth_error)

# --- WELCOME ---
elif st.session_state.page == 'welcome':
    st.markdown('<p class="main-header">NEXT HORIZON</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Câu lạc bộ định hướng nghề nghiệp - UK Academy</p>', unsafe_allow_html=True)
    
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.info("🧩 **Trắc nghiệm Holland**\n\nTìm ra nhóm sở thích nghề nghiệp phù hợp nhất với bạn.")
        if st.button("Bắt đầu Holland", key="wc_h"): switch_page('holland'); st.rerun()
    with r1c2:
        st.warning("🎯 **Khám phá IKIGAI**\n\n:red[Tìm điểm giao thoa của Đam mê, Kỹ năng và Nhu cầu xã hội.]")
        if st.button("Bắt đầu IKIGAI", key="wc_i"): switch_page('ikigai'); st.rerun()

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.success("🧠 **Trắc nghiệm Big Five**\n\nHiểu rõ 5 đặc điểm tính cách cốt lõi của bản thân.")
        if st.button("Bắt đầu Big Five", key="wc_b"): switch_page('big_five'); st.rerun()
    with r2c2:
        st.info("🔍 **Tìm kiếm Ngành nghề**\n\nTra cứu thông tin chi tiết về các ngành học và trường ĐH.")
        if st.button("Tìm kiếm Ngành nghề", key="wc_s"): switch_page('search'); st.rerun()
    
    st.markdown("---")
    r3c1, r3c2 = st.columns(2)
    with r3c1:
        st.markdown("""
        <div style="background-color: #FFF3E0; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #FFE0B2; margin-bottom: 10px;">
            <h4 style="color: #E65100; text-shadow: 1px 1px 1px rgba(0,0,0,0.1); font-weight: 800; margin: 0;">🤖 Trợ lý AI</h4>
            <p style="color: #BF360C; font-weight: 600; margin: 5px 0 0 0;">Hỏi đáp mọi lúc mọi nơi</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Chat với AI"): switch_page('chat'); st.rerun()
        
    with r3c2:
        st.markdown("""
        <div style="background-color: #E3F2FD; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #BBDEFB; margin-bottom: 10px;">
            <h4 style="color: #0D47A1; text-shadow: 1px 1px 1px rgba(0,0,0,0.1); font-weight: 800; margin: 0;">👨‍🏫 Chuyên gia Tư vấn</h4>
            <p style="color: #01579B; font-weight: 600; margin: 5px 0 0 0;">Kết nối trực tiếp với thầy cô</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Gặp Chuyên gia"): switch_page('expert'); st.rerun()
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #666;'>Sản phẩm thuộc về Câu lạc bộ hướng nghiệp Next Horizon - UK Academy Hạ Long</div>", unsafe_allow_html=True)

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
        
        st.progress(100)
        # Sử dụng dictionary R, I, A, S, E, C
        detailed_questions = get_holland_detailed_questions()
        groups = {
            "R": "Nhóm Kỹ thuật (Realistic)",
            "I": "Nhóm Nghiên cứu (Investigative)",
            "A": "Nhóm Nghệ thuật (Artistic)",
            "S": "Nhóm Xã hội (Social)",
            "E": "Nhóm Quản lý (Enterprising)",
            "C": "Nhóm Nghiệp vụ (Conventional)"
        }
        
        # Tạo Tabs cho 6 nhóm
        tabs = st.tabs(list(groups.values()))
        
        # Lưu kết quả
        map_h = {"Rất không thích": 1, "Không thích": 2, "Bình thường": 3, "Thích": 4, "Rất thích": 5}
        options_h = list(map_h.keys())
        
        with st.form("holland_detailed_form"):
            scores = {g: 0 for g in groups.keys()}
            
            # Duyệt qua từng tab tương ứng với từng nhóm
            for i, group_code in enumerate(groups.keys()):
                with tabs[i]:
                    st.subheader(f"Câu hỏi cho {groups[group_code]}")
                    st.caption("Nếu có đầy đủ cơ hội và nguồn lực, tôi...")
                    
                    group_questions = detailed_questions[group_code]
                    for j, q_text in enumerate(group_questions):
                        st.markdown(f"**{j+1}. {q_text}**")
                        ans = st.radio(f"{group_code}_{j}", options_h, index=2, horizontal=True, key=f"h_{group_code}_{j}", label_visibility="collapsed")
                        st.markdown("---")
                        scores[group_code] += map_h[ans]
            
            if st.form_submit_button("✅ HOÀN THÀNH & XEM KẾT QUẢ", type="primary", use_container_width=True):
                st.session_state.holland_scores = scores
                st.session_state.holland_step = 'result'
                st.rerun()

    elif st.session_state.holland_step == 'result':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="hr_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="hr_b", use_container_width=True): st.session_state.holland_step='landing'; st.rerun()
        st.success("Kết quả phân tích Holland:")
        st.bar_chart(st.session_state.holland_scores)
        if api_key:
            with st.spinner("AI đang phân tích..."):
                # Sắp xếp lấy top nhóm cao điểm nhất
                sorted_scores = sorted(st.session_state.holland_scores.items(), key=lambda x:x[1], reverse=True)
                top_3 = ", ".join([f"{k} ({v} điểm)" for k, v in sorted_scores[:3]])
                
                prompt = f"""
                Học sinh vừa hoàn thành bài trắc nghiệm Holland 6 nhóm (R-I-A-S-E-C).
                Top 3 nhóm cao điểm nhất là: {top_3}.
                Hãy phân tích ngắn gọn về đặc điểm nghề nghiệp của học sinh này và gợi ý 5 ngành nghề cụ thể phù hợp nhất tại Việt Nam.
                """
                ai_res = get_ai_response(prompt, api_key)
                if ai_res:
                    st.markdown(f"<div class='result-card'>{ai_res}</div>", unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Không thể kết nối với AI để phân tích. Vui lòng kiểm tra lại API Key hoặc thử lại sau.")
        else:
            st.info("💡 Bạn có thể nhập Gemini API Key ở menu bên trái để nhận gợi ý nghề nghiệp chuyên sâu từ AI.")
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
            if st.button("Bắt đầu bài kiểm tra BIG 5 (120 câu)", type="primary"):
                st.session_state.big_five_step = 'intro'; st.rerun()

    elif st.session_state.big_five_step == 'intro':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="bi_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="bi_b", use_container_width=True): st.session_state.big_five_step='landing'; st.rerun()
        st.markdown("<h2 style='text-align: center;'>Hướng dẫn</h2>", unsafe_allow_html=True)
        st.markdown("""
        <div class='intro-text'>
        Đây là bài trắc nghiệm chuyên sâu gồm <b>120 câu hỏi</b>.
        <br>⏱️ Thời gian dự kiến: 15-20 phút.
        <br>💡 Hãy trả lời trung thực nhất với con người hiện tại của bạn.
        </div>
        """, unsafe_allow_html=True)
        if st.button("Bắt đầu ngay ➡️", type="primary", use_container_width=True):
            st.session_state.big_five_step = 'quiz'; st.rerun()

    elif st.session_state.big_five_step == 'quiz':
        # --- NAV BAR ---
        n1, n2 = st.columns(2)
        with n1:
            if st.button("🏠 Trang chủ", key="bq_h", use_container_width=True): switch_page('welcome'); st.rerun()
        with n2:
            if st.button("⬅️ Quay lại", key="bq_b", use_container_width=True): st.session_state.big_five_step='intro'; st.rerun()
        
        st.progress(100)
        st.caption("Hãy chọn mức độ đồng ý của bạn với từng câu:")
        
        questions = get_big_five_120_questions()
        map_s = {"Hoàn toàn không đồng ý": 1, "Không đồng ý": 2, "Trung lập": 3, "Đồng ý": 4, "Hoàn toàn đồng ý": 5}
        options = list(map_s.keys())
        
        with st.form("b_quiz_120"):
            scores = {'O':0, 'C':0, 'E':0, 'A':0, 'N':0}
            
            # Hiển thị 120 câu hỏi
            for i, q in enumerate(questions):
                st.markdown(f"**{i+1}. {q['text']}**")
                ans = st.radio(f"q_{i}", options, index=2, horizontal=True, key=f"bf_{i}", label_visibility="collapsed")
                st.markdown("---")
                # Cộng điểm thô (để AI xử lý sau)
                scores[q['trait']] += map_s[ans]
            
            if st.form_submit_button("✅ HOÀN THÀNH & XEM KẾT QUẢ", type="primary", use_container_width=True):
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
        st.success("Kết quả Big Five (IPIP-NEO-120):")
        st.bar_chart(st.session_state.big_five_scores)
        
        # Gửi điểm số thô cho AI phân tích
        if api_key:
            with st.spinner("Chuyên gia AI đang phân tích hồ sơ tính cách chi tiết..."):
                prompt = f"""
                Tôi vừa hoàn thành bài trắc nghiệm Big Five 120 câu (IPIP-NEO-120).
                Tổng điểm thô của tôi cho từng nhóm (Range mỗi nhóm: 24 - 120 điểm):
                - Neuroticism (N): {st.session_state.big_five_scores['N']}
                - Extraversion (E): {st.session_state.big_five_scores['E']}
                - Openness (O): {st.session_state.big_five_scores['O']}
                - Agreeableness (A): {st.session_state.big_five_scores['A']}
                - Conscientiousness (C): {st.session_state.big_five_scores['C']}
                
                Hãy đóng vai chuyên gia tâm lý, phân tích chi tiết tính cách của tôi dựa trên điểm số này. 
                Đưa ra lời khuyên về điểm mạnh, điểm yếu và môi trường làm việc phù hợp.
                """
                res = get_ai_response(prompt, api_key)
                if res: st.markdown(f"<div class='result-card'>{res}</div>", unsafe_allow_html=True)
                else: st.error("Không thể kết nối AI. Vui lòng kiểm tra lại API Key.")
        else:
            st.info("💡 Bạn có thể nhập Gemini API Key ở menu bên trái để nhận phân tích tính cách chuyên sâu từ AI.")
        
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
                if api_key and not st.session_state.ikigai_questions_ai:
                    with st.spinner("AI đang tạo đề..."):
                        q, is_ai = generate_ikigai_questions_logic(api_key)
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
        if api_key:
            with st.spinner("AI đang phân tích lẽ sống Ikigai của bạn..."):
                prompt = f"""
                Học sinh vừa hoàn thành bài trắc nghiệm Ikigai với điểm số từng trụ cột (thang điểm 10):
                - Đam mê (Yêu thích - Love): {st.session_state.ikigai_scores.get('Love', 0):.1f}/10
                - Sở trường (Giỏi - Good): {st.session_state.ikigai_scores.get('Good', 0):.1f}/10
                - Nhu cầu xã hội (Thế giới cần - World): {st.session_state.ikigai_scores.get('World', 0):.1f}/10
                - Thu nhập (Được trả tiền - Paid): {st.session_state.ikigai_scores.get('Paid', 0):.1f}/10
                
                Hãy đóng vai chuyên gia hướng nghiệp, phân tích ngắn gọn điểm giao thoa và đưa ra lời khuyên giúp học sinh cân bằng các yếu tố này để tìm được Ikigai nghề nghiệp của mình.
                """
                ai_res = get_ai_response(prompt, api_key)
                if ai_res:
                    st.markdown(f"<div class='result-card'>{ai_res}</div>", unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Không thể kết nối với AI. Vui lòng kiểm tra lại API Key.")
        else:
            st.info("💡 Bạn có thể nhập Gemini API Key ở menu bên trái để nhận phân tích Ikigai từ AI.")
        if st.button("Làm lại"): st.session_state.ikigai_questions_ai=None; st.session_state.ikigai_step='landing'; st.rerun()

# --- EXPERT ---
elif st.session_state.page == 'expert':
    # --- NAV BAR ---
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="e_h", use_container_width=True): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="e_b", use_container_width=True): switch_page('welcome'); st.rerun()
        
    # Banner GPT TS Vũ Việt Anh (GIỮ LẠI THEO YÊU CẦU)
    st.markdown("""<div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px;"><h4 style="color: #2e7d32; margin: 0;">🎁 Quà tặng từ TS. Vũ Việt Anh</h4><p style="margin: 5px 0;">Chatbot GPT chuyên sâu hỗ trợ định hướng nghề nghiệp 24/7.</p></div>""", unsafe_allow_html=True)
    st.link_button("👉 Trò chuyện ngay với GPT TS. Vũ Việt Anh", "https://chatgpt.com/g/g-6942112d74cc8191860a9938ae29b14c-huong-nghiep-cung-ts-vu-viet-anh", type="primary", use_container_width=True)
    
    # Đã xóa dòng st.markdown("---") ở đây để bỏ thanh gạch ngang vô duyên

    # 2 CỘT CHUYÊN GIA
    ec1, ec2 = st.columns(2)
    with ec1:
        if os.path.exists("vu_viet_anh.jpg"): st.image("vu_viet_anh.jpg", use_container_width=True)
        elif os.path.exists("vuvietanh.jpg"): st.image("vuvietanh.jpg", use_container_width=True)
        st.markdown("### TS. Vũ Việt Anh\nChuyên gia định hướng nghề nghiệp\nChủ tịch HĐ Cố vấn EDA INSTITUTE\n* SĐT: 098 4736999")
    with ec2:
        if os.path.exists("pham_cong_thanh.jpg"): st.image("pham_cong_thanh.jpg", use_container_width=True)
        st.markdown("### ThS. Phạm Công Thành\nChuyên gia định hướng nghề nghiệp\n* SĐT: 038.7315.722\n* Email: phamcongthanh92@gmail.com")
    
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
    if p := st.chat_input("Hỏi tôi bất cứ điều gì về định hướng nghề nghiệp..."):
        st.session_state.chat_history.append({"role":"user","content":p})
        st.chat_message("user").write(p)
        if api_key:
            with st.spinner("Trợ lý AI đang suy nghĩ..."):
                res = get_ai_response(p, api_key)
            if res:
                st.session_state.chat_history.append({"role":"assistant","content":res})
                st.chat_message("assistant").write(res)
            else:
                err = "Xin lỗi, hiện tại tôi không thể kết nối tới máy chủ AI. Vui lòng kiểm tra lại API Key hoặc thử lại sau."
                st.session_state.chat_history.append({"role":"assistant","content":err})
                st.chat_message("assistant").write(err)
        else:
            notice = "💡 Vui lòng nhập Gemini API Key ở thanh menu bên trái để trò chuyện cùng trợ lý AI."
            st.session_state.chat_history.append({"role":"assistant","content":notice})
            st.chat_message("assistant").write(notice)

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
    with c1:
        st.subheader("🧩 Holland")
        if st.session_state.holland_scores: st.bar_chart(st.session_state.holland_scores)
        else: st.info("Chưa làm bài trắc nghiệm")
    with c2:
        st.subheader("🧠 Big Five")
        if st.session_state.big_five_scores: st.bar_chart(st.session_state.big_five_scores)
        else: st.info("Chưa làm bài trắc nghiệm")
    with c3:
        st.subheader("🎯 Ikigai")
        if st.session_state.ikigai_scores: st.bar_chart(st.session_state.ikigai_scores)
        else: st.info("Chưa làm bài trắc nghiệm")
        
    has_results = bool(st.session_state.holland_scores or st.session_state.big_five_scores or st.session_state.ikigai_scores)
    if has_results:
        st.markdown("---")
        if st.button("📄 Phân tích tổng hợp bằng AI", type="primary"):
            if api_key:
                with st.spinner("AI đang tổng hợp và phân tích hồ sơ..."):
                    h_val = st.session_state.holland_scores or "Chưa làm"
                    b_val = st.session_state.big_five_scores or "Chưa làm"
                    i_val = st.session_state.ikigai_scores or "Chưa làm"
                    p = f"Tổng hợp hồ sơ học sinh: Holland={h_val}, BigFive={b_val}, Ikigai={i_val}. Phân tích điểm mạnh cốt lõi, môi trường làm việc phù hợp nhất và top 3 nghề nghiệp lý tưởng tại Việt Nam."
                    res = get_ai_response(p, api_key)
                    if res:
                        st.markdown(f"<div class='result-card'>{res}</div>", unsafe_allow_html=True)
                    else:
                        st.error("Không thể kết nối AI.")
            else:
                st.warning("Vui lòng nhập API Key ở menu bên trái để AI phân tích tổng hợp.")

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
    q = st.text_input("Nhập ngành nghề bạn quan tâm:")
    if q and st.button("Tìm kiếm 🔍", type="primary"):
        if api_key:
            with st.spinner("Đang tra cứu thông tin ngành nghề..."):
                res = get_ai_response(f"Thông tin chi tiết về ngành {q} ở Việt Nam: tổng quan ngành, cơ hội việc làm, các trường đại học đào tạo uy tín, tổ hợp môn xét tuyển và mức thu nhập tham khảo.", api_key)
                if res:
                    st.markdown(f"<div class='result-card'>{res}</div>", unsafe_allow_html=True)
                else:
                    st.error("Không thể kết nối với AI. Vui lòng kiểm tra lại API Key.")
        else:
            st.warning("Vui lòng nhập Gemini API Key ở menu bên trái để tra cứu AI.")
elif st.session_state.page == 'roadmap':
    # --- NAV BAR ---
    n1, n2 = st.columns(2)
    with n1:
        if st.button("🏠 Trang chủ", key="rm_h", use_container_width=True): switch_page('welcome'); st.rerun()
    with n2:
        if st.button("⬅️ Quay lại", key="rm_b", use_container_width=True): switch_page('welcome'); st.rerun()
        
    render_image_safe("roadmap.png", 100)
    st.header("Lộ trình phát triển")
    if st.button("Lập lộ trình AI 🚀", type="primary"):
        if api_key:
            with st.spinner("Chuyên gia AI đang lập lộ trình cá nhân hóa..."):
                holland_info = str(st.session_state.holland_scores) if st.session_state.holland_scores else "Chưa làm trắc nghiệm Holland"
                bigfive_info = str(st.session_state.big_five_scores) if st.session_state.big_five_scores else "Chưa làm trắc nghiệm Big Five"
                ikigai_info = str(st.session_state.ikigai_scores) if st.session_state.ikigai_scores else "Chưa làm trắc nghiệm Ikigai"
                prompt = f"""
                Hãy đóng vai chuyên gia định hướng nghề nghiệp, xây dựng một Lộ trình phát triển bản thân (Roadmap) chi tiết cho học sinh THPT dựa trên các kết quả đánh giá:
                - Kết quả Holland: {holland_info}
                - Kết quả Big Five: {bigfive_info}
                - Kết quả Ikigai: {ikigai_info}
                
                Lộ trình gồm các giai đoạn rõ ràng:
                1. Giai đoạn lớp 10-11: Rèn luyện kỹ năng, khám phá sở thích, hoạt động ngoại khóa.
                2. Giai đoạn lớp 12: Chọn ngành, chọn khối thi và trường đại học mục tiêu.
                3. Giai đoạn Đại học: Xây dựng kỹ năng chuyên môn, thực tập và định hình sự nghiệp.
                """
                res = get_ai_response(prompt, api_key)
                if res:
                    st.markdown(f"<div class='result-card'>{res}</div>", unsafe_allow_html=True)
                else:
                    st.error("Không thể kết nối với AI. Vui lòng kiểm tra lại API Key.")
        else:
            st.warning("Vui lòng nhập Gemini API Key ở menu bên trái để lập lộ trình AI.")

# --- FOOTER ---
st.markdown("---")
st.markdown("""<div class='footer'>@2025 sản phẩm thuộc về Câu lạc bộ hướng nghiệp Next Horizon - UK Academy Hạ Long</div>""", unsafe_allow_html=True)
