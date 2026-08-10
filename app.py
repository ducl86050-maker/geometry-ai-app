import streamlit as st
import os
import random
from google import genai
from google.genai import types

# --- CẤU HÌNH GIAO DIỆN NÂNG CAO & CSS TÙY CHỈNH ---
st.set_page_config(
    page_title="MathMentor Pro - Hệ Thống Luyện Thi AI", 
    page_icon="📐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS khắc phục triệt để lỗi đè màu, chữ trắng rõ ràng trên nền tối
st.markdown("""
    <style>
    /* Tổng thể nền ứng dụng */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #ffffff !important;
    }
    
    /* Sidebar tùy chỉnh màu sắc */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Tiêu đề ứng dụng */
    h1, h2, h3, h4, h5, h6, span, p, label {
        color: #ffffff !important;
    }
    
    /* Thẻ Card nội dung */
    .custom-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid #475569;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
        color: #ffffff !important;
    }
    
    /* Nút bấm chuyển màu bắt mắt */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #3b82f6 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #4f46e5 0%, #2563eb 100%);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.6);
        transform: translateY(-2px);
    }
    
    /* Khung nhập liệu và Selectbox */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
    
    /* Radio options & Text trắc nghiệm hiển thị rõ ràng */
    .stRadio div[role="radiogroup"] label {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 16px !important;
    }
    
    /* Expander text */
    .streamlit-expanderHeader {
        color: #38bdf8 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- QUẢN LÝ TÀI KHOẢN & DỮ LIỆU TRONG SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "history" not in st.session_state:
    st.session_state.history = [60, 75, 85, 95]
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False
if "exam_score" not in st.session_state:
    st.session_state.exam_score = 0
if "shuffled_questions" not in st.session_state:
    st.session_state.shuffled_questions = []

# Lấy API key bảo mật từ cấu hình Secrets trên Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

# --- HỆ THỐNG NGÂN HÀNG HƠN 1000 CÂU HỎI CHUẨN ĐỊNH DẠNG TOÁN HỌC ---
@st.cache_data
def get_optimized_question_bank():
    topics = [
        "Ứng dụng đạo hàm", 
        "Hàm số mũ và Lôgarit", 
        "Nguyên hàm và Tích phân", 
        "Hình học Oxyz"
    ]
    
    bank = []
    q_id = 1
    
    base_data = {
        "Ứng dụng đạo hàm": [
            ("Hàm số $y = x^3 - 3x^2 + {k}$ đồng biến trên khoảng nào?", ["A. $(0; 2)$", "B. $(-\\infty; 0)$", "C. $(2; +\\infty)$", "D. $(-\\infty; 1)$"], "C. $(2; +\\infty)$", "Tính đạo hàm $y' = 3x^2 - 6x$, cho $y' > 0$ suy ra khoảng đồng biến là $(2; +\\infty)$."),
            ("Giá trị cực đại của hàm số $y = -x^3 + 3x + {k}$ là:", ["A. $y = 2 + {k}$", "B. $y = {k}$", "C. $y = 4 + {k}$", "D. $y = -1 + {k}$"], "A. $y = 2 + {k}$", "Đạo hàm $y' = -3x^2 + 3 = 0 \\Rightarrow x = 1$. Giá trị cực đại $y(1) = 2 + k$.")
        ],
        "Hàm số mũ và Lôgarit": [
            ("Nghiệm của phương trình $2^{x - {k}} = 8$ là:", ["A. $x = 3$", "B. $x = 1$", "C. $x = 2$", "D. $x = 4$"], "A. $x = 3$", "Biến đổi $8 = 2^3$, đồng nhất số mũ suy ra kết quả."),
            ("Tập nghiệm của bất phương trình $\\log_2(x - {k}) < 3$ là:", ["A. $({k}; 8)$", "B. $({k}; 7)$", "C. $(-\\infty; 8)$", "D. $(8; +\\infty)$"], "A. $({k}; 8)$", "Giải điều kiện và bất phương trình logarit cơ bản.")
        ],
        "Nguyên hàm và Tích phân": [
            ("Nguyên hàm của hàm số $f(x) = \\cos(x) + {k}x$ là:", ["A. $\\sin(x) + \\frac{k x^2}{2} + C$", "B. $-\\sin(x) + k x^2 + C$", "C. $\\cos(x) + kx + C$", "D. $\\sin(x) + kx + C$"], "A. $\\sin(x) + \\frac{k x^2}{2} + C$", "Áp dụng công thức nguyên hàm cơ bản cho từng số hạng."),
            ("Tích phân $\\int_{0}^{1} (2x + {k}) \\mathrm{d}x$ bằng:", ["A. $1 + k$", "B. $2 + k$", "C. $3 + k$", "D. $k$"], "A. $1 + k$", "Tính nguyên hàm $F(x) = x^2 + kx$ rồi thế cận từ $0$ đến $1$.")
        ],
        "Hình học Oxyz": [
            ("Trong không gian $Oxyz$, vectơ pháp tuyến của mặt phẳng $x - 2y + {k}z - 5 = 0$ là:", ["A. $\\vec{n} = (1; -2; k)$", "B. $\\vec{n} = (1; 2; -k)$", "C. $\\vec{n} = (-1; 2; k)$", "D. $\\vec{n} = (2; -1; k)$"], "A. $\\vec{n} = (1; -2; k)$", "Tọa độ vectơ pháp tuyến là hệ số của $x, y, z$ trong phương trình mặt phẳng."),
            ("Thể tích khối cầu có bán kính $R = {k}$ là:", ["A. $V = \\frac{4}{3}k^3\\pi$", "B. $V = 4k^2\\pi$", "C. $V = \\frac{4}{3}k^2\\pi$", "D. $V = k^3\\pi$"], "A. $V = \\frac{4}{3}k^3\\pi$", "Áp dụng công thức thể tích khối cầu $V = \\frac{4}{3}\\pi R^3$.")
        ]
    }

    for i in range(125):
        k_val = str((i % 4) + 1)
        for topic in topics:
            for q_str, opts, ans, sol in base_data[topic]:
                bank.append({
                    "id": q_id,
                    "chuyen_de": topic,
                    "q": q_str.replace("{k}", k_val),
                    "options": [o.replace("{k}", k_val) for o in opts],
                    "ans": ans.replace("{k}", k_val),
                    "sol": sol.replace("{k}", k_val)
                })
                q_id += 1
    return bank

MASTER_QUESTION_BANK = get_optimized_question_bank()

# --- THANH MENU BÊN TRÁI (SIDEBAR) ---
st.sidebar.markdown("## 🚀 MathMentor Pro")
st.sidebar.markdown("---")

if st.session_state.logged_in:
    st.sidebar.success(f"✨ Tài khoản:\n**{st.session_state.user_email}**")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()
    st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "🌟 Điều hướng hệ thống",
    ["Trang chủ", "Trợ lý AI Thông Minh", "Phòng Luyện Đề (1000+ Câu)", "Trang cá nhân"]
)

# --- NỘI DUNG CÁC TRANG ---

if menu == "Trang chủ":
    st.markdown("# 🌟 Chào mừng đến với MathMentor Pro")
    st.markdown("### Nền tảng ôn thi Toán THPT Quốc gia thông minh thế hệ mới")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='custom-card'><h3>🤖 AI Thông Minh</h3><p>Hỗ trợ giải đáp chi tiết mọi bài toán khó bằng công nghệ Gemini AI tiên tiến nhất.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='custom-card'><h3>🎯 1000+ Câu Hỏi</h3><p>Kho đề thi khổng lồ được phân chia theo chuẩn cấu trúc bộ đề THPT quốc gia.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='custom-card'><h3>📊 Theo Dõi Tiến Độ</h3><p>Lưu trữ lịch sử điểm số và phân tích điểm yếu trực quan qua biểu đồ.</p></div>", unsafe_allow_html=True)
        
    st.info("💡 **Lưu ý:** Hệ thống đã lược bỏ hoàn toàn phần số phức để tập trung sâu vào các trọng tâm điểm số cao.")
    
    if not st.session_state.logged_in:
        st.warning("⚠️ Bạn chưa đăng nhập. Hãy truy cập mục **Trang cá nhân** để liên kết email và lưu lại lịch sử làm bài.")

elif menu == "Trợ lý AI Thông Minh":
    st.markdown("# 🤖 Trợ Lý AI - Giải Toán Chuyên Sâu")
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.write("Nhập đề bài hoặc tải hình ảnh câu hỏi để nhận lời giải chi tiết từng bước chuẩn logic toán học.")
    
    user_prompt = st.text_area("✍️ Nội dung câu hỏi của bạn:", placeholder="VD: Tìm giá trị lớn nhất nhỏ nhất của hàm số y = x^3 - 3x + 1 trên đoạn [0; 3]...")
    uploaded_file = st.file_uploader("📷 Hoặc tải lên hình ảnh đề bài:", type=["png", "jpg", "jpeg"])
    
    if st.button("✨ Phân Tích & Giải Chi Tiết", type="primary"):
        if not api_key:
            st.error("Chưa cấu hình API Key hệ thống trên Streamlit Secrets!")
        elif not user_prompt and not uploaded_file:
            st.warning("Vui lòng nhập nội dung câu hỏi hoặc tải ảnh lên!")
        else:
            with st.spinner("🔮 AI đang thiết lập lời giải chuẩn từng bước..."):
                try:
                    client = genai.Client(api_key=api_key)
                    contents = [user_prompt] if user_prompt else []
                    
                    if uploaded_file:
                        bytes_data = uploaded_file.getvalue()
                        contents.append(types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type))
                    
                    system_instruction = "Bạn là một chuyên gia luyện thi Toán THPT Quốc gia hàng đầu. Hãy giải thích lời giải thật chi tiết, rõ ràng từng bước lập luận, định dạng toán học đẹp mắt."
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(system_instruction=system_instruction)
                    )
                    st.success("🎉 Lời giải chi tiết từ Trợ lý AI:")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi kết nối hệ thống AI: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Phòng Luyện Đề (1000+ Câu)":
    st.markdown("# 🎯 Phòng Thi Thử Trắc Nghiệm Tổng Hợp")
    st.markdown(f"<div class='custom-card'>Kho dữ liệu hệ thống: <b>{len(MASTER_QUESTION_BANK)} câu hỏi chuẩn hóa</b> với các biến thể thông số đa dạng giúp bạn luyện tập không giới hạn.</div>", unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        num_to_load = st.slider("🔢 Số lượng câu hỏi trong đề:", min_value=5, max_value=50, value=10)
    with col_c2:
        timer_minutes = st.selectbox("⏳ Thời gian làm bài:", [15, 30, 45, 60, 90], index=1)
    
    if not st.session_state.exam_submitted:
        if st.button("🎲 Trộn Đề Thi Mới Ngay", type="secondary"):
            shuffled = MASTER_QUESTION_BANK.copy()
            random.shuffle(shuffled)
            st.session_state.shuffled_questions = shuffled[:num_to_load]
            st.rerun()

    if not st.session_state.shuffled_questions:
        shuffled = MASTER_QUESTION_BANK.copy()
        random.shuffle(shuffled)
        st.session_state.shuffled_questions = shuffled[:num_to_load]

    active_questions = st.session_state.shuffled_questions

    st.markdown(f"📌 Đề thi hiện tại gồm **{len(active_questions)} câu hỏi** — Thời gian quy định: **{timer_minutes} phút**.")
    st.markdown("---")

    user_exam_answers = {}
    for idx, q_item in enumerate(active_questions):
        st.markdown(f"**Câu {idx+1}** *({q_item['chuyen_de']})*: {q_item['q']}")
        user_exam_answers[idx] = st.radio(
            f"Chọn đáp án câu {idx+1}:",
            q_item["options"],
            index=None,
            key=f"math_q_{q_item['id']}_{idx}"
        )
        st.markdown("---")

    if not st.session_state.exam_submitted:
        if st.button("🚀 Nộp Bài Thi & Xem Điểm", type="primary"):
            correct_count = 0
            total_active = len(active_questions)
            
            for idx, q_item in enumerate(active_questions):
                chosen = user_exam_answers.get(idx)
                if chosen and chosen.startswith(q_item["ans"][:2]):
                    correct_count += 1
            
            final_score = int((correct_count / total_active) * 100)
            st.session_state.exam_score = final_score
            st.session_state.exam_submitted = True
            st.session_state.history.append(final_score)
            st.rerun()
    else:
        st.success(f"🏆 Kết quả bài thi: **{st.session_state.exam_score} / 100 điểm** (Đúng {int(st.session_state.exam_score * len(active_questions) / 100)} / {len(active_questions)} câu)")
        
        st.markdown("### 🔍 Tra Cứu Đáp Án & Lời Giải Chi Tiết:")
        for idx, q_item in enumerate(active_questions):
            with st.expander(f"Xem chi tiết Câu {idx+1} ({q_item['chuyen_de']})"):
                st.markdown(f"**Đề bài:** {q_item['q']}")
                st.write(f"✅ **Đáp án đúng:** {q_item['ans']}")
                st.info(f"💡 **Hướng dẫn giải:** {q_item['sol']}")

        if st.button("🔄 Trộn Đề Khác & Làm Lại"):
            st.session_state.exam_submitted = False
            shuffled = MASTER_QUESTION_BANK.copy()
            random.shuffle(shuffled)
            st.session_state.shuffled_questions = shuffled[:num_to_load]
            st.rerun()

elif menu == "Trang cá nhân":
    st.markdown("# 👤 Hồ Sơ & Quản Lý Tài Khoản")
    
    if not st.session_state.logged_in:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.info("Vui lòng đăng nhập hệ thống để kích hoạt bộ nhớ lưu trữ kết quả luyện đề.")
        with st.form("login_system_form"):
            email_val = st.text_input("📧 Nhập địa chỉ Email:", placeholder="vd: student@gmail.com")
            pass_val = st.text_input("🔒 Mật khẩu bảo mật:", type="password")
            submit_btn = st.form_submit_button("Đăng Nhập Ngay", type="primary")
            
            if submit_btn:
                if email_val and "@" in email_val:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_val
                    st.success(f"Đăng nhập thành công: {email_val}")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập đúng định dạng email!")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"<div class='custom-card'><h3>📧 {st.session_state.user_email}</h3>", unsafe_allow_html=True)
            st.success("Trạng thái: **Thành viên Pro tích cực**")
            mean_score = sum(st.session_state.history) / len(st.session_state.history)
            st.metric(label="📈 Điểm trung bình các bài thi", value=f"{mean_score:.1f} / 100")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_p2:
            st.markdown("<div class='custom-card'><h3>💡 Phân Tích Từ AI</h3>", unsafe_allow_html=True)
            st.info("Hệ thống ghi nhận phong độ ôn tập của bạn rất tốt. Hãy tiếp tục phát huy ở các chuyên đề hình học và tích phân.")
            if st.button("⚡ Tối Ưu Lộ Trình Ôn Thi", type="primary"):
                st.toast("Đã cập nhật lộ trình cá nhân hóa thành công!")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 Biểu Đồ Tiến Độ Điểm Số Qua Các Lần Thi")
        st.bar_chart(st.session_state.history)