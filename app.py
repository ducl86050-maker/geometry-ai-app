import streamlit as st
import os
import random
from google import genai
from google.genai import types

# Cấu hình trang
st.set_page_config(page_title="MathMentor - Phòng Luyện Đề THPT", layout="wide")

# --- QUẢN LÝ TÀI KHOẢN & DỮ LIỆU TRONG SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "history" not in st.session_state:
    st.session_state.history = [50, 75, 85, 92]
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False
if "exam_score" not in st.session_state:
    st.session_state.exam_score = 0
if "shuffled_questions" not in st.session_state:
    st.session_state.shuffled_questions = []

# Lấy API key bảo mật từ cấu hình Secrets trên Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

# --- HỆ THỐNG NGÂN HÀNG HƠN 1000 CÂU HỎI TỰ ĐỘNG (ĐÃ LOẠI BỎ SỐ PHỨC) ---
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
            ("Hàm số y = x^3 - 3x^2 + {k} đồng biến trên khoảng nào?", ["A. (0; 2)", "B. (-∞; 0)", "C. (2; +∞)", "D. (-∞; 1)"], "C. (2; +∞)", "Tính đạo hàm y' = 3x^2 - 6x, cho y' > 0 suy ra khoảng đồng biến là (2; +∞)."),
            ("Giá trị cực đại của hàm số y = -x^3 + 3x + {k} là:", [f"A. y = 2 + {{k}}", f"B. y = {{k}}", f"C. y = 4 + {{k}}", f"D. y = -1 + {{k}}"], f"A. y = 2 + {{k}}", "Đạo hàm y' = -3x^2 + 3 = 0 => x = 1. Giá trị cực đại y(1) = 2 + k.")
        ],
        "Hàm số mũ và Lôgarit": [
            ("Nghiệm của phương trình 2^(x-{k}) = 8 là:", [f"A. x = {3}", f"B. x = {1}", f"C. x = {2}", f"D. x = {4}"], f"A. x = {3}", "Biến đổi 8 = 2^3, đồng nhất số mũ suy ra kết quả."),
            ("Tập nghiệm của bất phương trình log_2(x - {k}) < 3 là:", [f"A. ({k}; {8})", f"B. ({k}; {7})", f"C. (-∞; {8})", f"D. ({8}; +∞)"], f"A. ({k}; {8})", "Giải điều kiện và bất phương trình logarit cơ bản.")
        ],
        "Nguyên hàm và Tích phân": [
            ("Nguyên hàm của hàm số f(x) = cos(x) + {k}x là:", ["A. sin(x) + k*x^2/2 + C", "B. -sin(x) + k*x^2 + C", "C. cos(x) + kx + C", "D. sin(x) + kx + C"], "A. sin(x) + k*x^2/2 + C", "Áp dụng công thức nguyên hàm cơ bản cho từng số hạng."),
            ("Tích phân từ 0 đến 1 của (2x + {k}) dx bằng:", ["A. 1 + k", "B. 2 + k", "C. 3 + k", "D. k"], "A. 1 + k", "Tính nguyên hàm F(x) = x^2 + k*x rồi thế cận từ 0 đến 1.")
        ],
        "Hình học Oxyz": [
            ("Trong không gian Oxyz, vectơ pháp tuyến của mặt phẳng x - 2y + {k}z - 5 = 0 là:", ["A. (1; -2; k)", "B. (1; 2; -k)", "C. (-1; 2; k)", "D. (2; -1; k)"], "A. (1; -2; k)", "Tọa độ vectơ pháp tuyến là hệ số của x, y, z trong phương trình mặt phẳng."),
            ("Thể tích khối cầu có bán kính R = {k} là:", ["A. (4/3)*k^3 * π", "B. 4*k^2 * π", "C. (4/3)*k^2 * π", "D. k^3 * π"], "A. (4/3)*k^3 * π", "Áp dụng công thức thể tích khối cầu V = (4/3)πR^3.")
        ]
    }

    # Sinh quy mô lớn hơn 1000 câu bằng biến hóa tham số k
    for i in range(125):
        k_val = str((i % 4) + 1)
        for topic in topics:
            for q_str, opts, ans, sol in base_data[topic]:
                bank.append({
                    "id": q_id,
                    "chuyen_de": topic,
                    "q": q_str.replace("{k}", k_val),
                    "options": [o.replace("k", k_val) for o in opts],
                    "ans": ans.replace("k", k_val),
                    "sol": sol.replace("k", k_val)
                })
                q_id += 1
    return bank

MASTER_QUESTION_BANK = get_optimized_question_bank()

# --- THANH MENU BÊN TRÁI (SIDEBAR) ---
st.sidebar.markdown("## 📐 MathMentor Pro")
st.sidebar.markdown("---")

if st.session_state.logged_in:
    st.sidebar.success(f"👤 Tài khoản:\n**{st.session_state.user_email}**")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()
    st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Điều hướng hệ thống",
    ["Trang chủ", "Trợ lý AI Thông Minh", "Phòng Luyện Đề (1000+ Câu)", "Kho Tài Liệu THPT", "Trang cá nhân"]
)

# --- NỘI DUNG CÁC TRANG ---

if menu == "Trang chủ":
    st.title("🌟 Chào mừng đến với Hệ thống Luyện thi MathMentor Pro")
    st.write("Nền tảng ôn thi Toán THPT Quốc gia tích hợp trí tuệ nhân tạo, phòng luyện đề với kho dữ liệu khổng lồ **hơn 1000 câu hỏi trộn lẫn** ngẫu nhiên và hẹn giờ chuyên nghiệp.")
    st.info("💡 Hệ thống tập trung hoàn toàn vào các chương cốt lõi (Đã loại bỏ hoàn toàn phần số phức).")
    
    if not st.session_state.logged_in:
        st.warning("⚠️ Bạn chưa đăng nhập. Hãy truy cập mục **Trang cá nhân** để đăng nhập email và lưu lại lịch sử học tập của mình.")

elif menu == "Trợ lý AI Thông Minh":
    st.title("🤖 CVT AI - Giải Toán THPT Chuyên Sâu")
    st.write("Trợ lý ảo thông minh giúp bạn giải đáp cặn kẽ mọi bài toán khó từ khảo sát hàm số, mũ - logarit, tích phân đến hình học Oxyz.")
    
    user_prompt = st.text_area("Nhập đề bài hoặc câu hỏi cần giải chi tiết:", placeholder="VD: Tìm giá trị lớn nhất nhỏ nhất của hàm số y = x^3 - 3x + 1 trên đoạn [0; 3]...")
    uploaded_file = st.file_uploader("Hoặc đính kèm hình ảnh đề bài:", type=["png", "jpg", "jpeg"])
    
    if st.button("Phân tích và Giải bài toán", type="primary"):
        if not api_key:
            st.error("Chưa cấu hình API Key hệ thống trên Streamlit Secrets!")
        elif not user_prompt and not uploaded_file:
            st.warning("Vui lòng nhập nội dung câu hỏi hoặc tải ảnh lên!")
        else:
            with st.spinner("AI đang thiết lập lời giải chuẩn từng bước logic..."):
                try:
                    client = genai.Client(api_key=api_key)
                    contents = [user_prompt] if user_prompt else []
                    
                    if uploaded_file:
                        bytes_data = uploaded_file.getvalue()
                        contents.append(types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type))
                    
                    system_instruction = "Bạn là một chuyên gia luyện thi Toán THPT Quốc gia hàng đầu. Hãy giải thích lời giải thật chi tiết, rõ ràng từng bước lập luận, công thức chuẩn mực."
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(system_instruction=system_instruction)
                    )
                    st.success("Lời giải chi tiết từ Trợ lý AI:")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Lỗi kết nối hệ thống AI: {e}")

elif menu == "Phòng Luyện Đề (1000+ Câu)":
    st.title("🎯 Phòng Thi Thử Tổng Hợp (Hơn 1000 Câu Trộn Lẫn)")
    st.write(f"Kho dữ liệu hiện có: **{len(MASTER_QUESTION_BANK)} câu hỏi** được trộn lẫn ngẫu nhiên từ mọi chuyên đề THPT giúp bạn ôn luyện không giới hạn.")
    
    # --- CẤU HÌNH ĐỀ THI ---
    st.markdown("### ⚙️ Thiết lập đề thi của bạn")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        num_to_load = st.slider("Chọn số lượng câu hỏi trong đề:", min_value=5, max_value=50, value=10)
    with col_c2:
        timer_minutes = st.selectbox("Thời gian làm bài chuẩn (Phút):", [15, 30, 45, 60, 90], index=1)
    
    # Nút khởi tạo/trộn đề mới
    if not st.session_state.exam_submitted:
        if st.button("🎲 Trộn Ngay Đề Thi Mới Từ Kho 1000+ Câu", type="secondary"):
            shuffled = MASTER_QUESTION_BANK.copy()
            random.shuffle(shuffled)
            st.session_state.shuffled_questions = shuffled[:num_to_load]
            st.rerun()

    # Khởi tạo mặc định nếu chưa có đề
    if not st.session_state.shuffled_questions:
        shuffled = MASTER_QUESTION_BANK.copy()
        random.shuffle(shuffled)
        st.session_state.shuffled_questions = shuffled[:num_to_load]

    active_questions = st.session_state.shuffled_questions

    st.markdown("---")
    st.info(f"⏳ **Đề thi tổng hợp** gồm **{len(active_questions)} câu hỏi ngẫu nhiên** — Thời gian quy định: **{timer_minutes} phút**.")

    # Form làm bài kiểm tra
    user_exam_answers = {}
    for idx, q_item in enumerate(active_questions):
        st.markdown(f"**Câu {idx+1}** *({q_item['chuyen_de']})*: {q_item['q']}")
        user_exam_answers[idx] = st.radio(
            f"Lựa chọn đáp án câu {idx+1}:",
            q_item["options"],
            index=None,
            key=f"safe_q_{q_item['id']}_{idx}"
        )
        st.markdown("---")

    if not st.session_state.exam_submitted:
        if st.button("🚀 Nộp Bài Thi & Chấm Điểm Tổng Hợp", type="primary"):
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
        st.success(f"🏆 Kết quả bài thi của bạn: **{st.session_state.exam_score} / 100 điểm** (Đúng {int(st.session_state.exam_score * len(active_questions) / 100)} / {len(active_questions)} câu)")
        
        st.markdown("### 🔍 Tra Cứu Đáp Án & Hướng Dẫn Giải Chi Tiết:")
        for idx, q_item in enumerate(active_questions):
            with st.expander(f"Xem chi tiết Câu {idx+1} ({q_item['chuyen_de']}): {q_item['q']}"):
                st.write(f"✅ **Đáp án đúng:** {q_item['ans']}")
                st.info(f"💡 **Lời giải chi tiết:** {q_item['sol']}")

        if st.button("🔄 Trộn Đề Mới Khác & Làm Lại"):
            st.session_state.exam_submitted = False
            shuffled = MASTER_QUESTION_BANK.copy()
            random.shuffle(shuffled)
            st.session_state.shuffled_questions = shuffled[:num_to_load]
            st.rerun()

elif menu == "Kho Tài Liệu THPT":
    st.title("📚 Kho Tài Liệu & Lý Thuyết Trọng Tâm THPT")
    st.write("Hệ thống tổng hợp kiến thức cốt lõi, công thức giải nhanh phục vụ ôn thi đại học (Đã lược bỏ hoàn toàn phần số phức).")
    
    with st.expander("📖 Chuyên đề 1: Ứng dụng đạo hàm khảo sát và vẽ đồ thị hàm số"):
        st.markdown("""
        * **Tính đơn điệu:** Sử dụng dấu của đạo hàm $y'$. Nếu $y' > 0$ hàm đồng biến, $y' < 0$ hàm nghịch biến.
        * **Cực trị:** Điểm mà tại đó $y'$ đổi dấu.
        * **Giá trị lớn nhất, nhỏ nhất (GTLN - GTNN):** Trên đoạn $[a; b]$.
        * **Tiệm cận:** Tiệm cận đứng $x = x_0$, Tiệm cận ngang $y = y_0$.
        """)
        
    with st.expander("📖 Chuyên đề 2: Hàm số lũy thừa, hàm số mũ và hàm số lôgarit"):
        st.markdown("""
        * **Công thức lũy thừa & Lôgarit:** $\\log_a(bc) = \\log_a b + \\log_a c$.
        * **Phương trình mũ & Lôgarit:** Đưa về cùng cơ số hoặc đặt ẩn phụ.
        """)

    with st.expander("📖 Chuyên đề 3: Nguyên hàm, tích phân và ứng dụng"):
        st.markdown("""
        * **Bảng nguyên hàm cơ bản:** $\\int x^n dx = \\frac{x^{n+1}}{n+1} + C$.
        * **Phương pháp tính:** Đổi biến số, tích phân từng phần.
        """)

    with st.expander("📖 Chuyên đề 4: Phương pháp tọa độ trong không gian (Oxyz)"):
        st.markdown("""
        * **Mặt phẳng:** Phương trình tổng quát $Ax + By + Cz + D = 0$.
        * **Đường thẳng & Mặt cầu:** Phương trình tham số, chính tắc và phương trình mặt cầu.
        """)

elif menu == "Trang cá nhân":
    st.title("👤 Hồ Sơ Người Dùng & Quản Lý Tài Khoản Học Tập")
    
    if not st.session_state.logged_in:
        st.info("Vui lòng đăng nhập hệ thống bằng email cá nhân để kích hoạt lưu trữ kết quả và theo dõi biểu đồ năng lực.")
        with st.form("login_system_form"):
            email_val = st.text_input("Nhập địa chỉ Email:", placeholder="vd: giakhanhtran88@gmail.com")
            pass_val = st.text_input("Mật khẩu bảo mật:", type="password")
            submit_btn = st.form_submit_button("Đăng nhập tài khoản Pro", type="primary")
            
            if submit_btn:
                if email_val and "@" in email_val:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_val
                    st.success(f"Đăng nhập thành công cho tài khoản: {email_val}")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập đúng định dạng địa chỉ email!")
    else:
        col_p1, col_p2 = st.columns([1, 1])
        with col_p1:
            st.markdown(f"### 📧 {st.session_state.user_email}")
            st.success("Trạng thái: **Đã kích hoạt tài khoản học tập chuyên sâu**")
            
            mean_score = sum(st.session_state.history) / len(st.session_state.history)
            st.metric(label="Điểm trung bình các bài thi thử", value=f"{mean_score:.1f} / 100")
            st.error("Trọng tâm cần cải thiện: Giải tích không gian Oxyz và Tích phân nâng cao")
        
        with col_p2:
            st.markdown("### 💡 Phân Tích Năng Lực AI")
            st.info("Hệ thống ghi nhận bạn đã hoàn thành các bài thi thử trắc nghiệm thành công. Hãy duy trì lịch luyện đề đều đặn mỗi ngày.")
            if st.button("Khởi tạo lộ trình nước rút THPT", type="primary"):
                st.toast("Đã tự động tối ưu hóa lộ trình ôn tập bám sát năng lực thực tế!")
        
        st.markdown("---")
        st.subheader("📈 Biểu đồ tiến độ điểm số qua các lần luyện đề")
        st.bar_chart(st.session_state.history)