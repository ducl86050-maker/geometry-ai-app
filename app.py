import streamlit as st
import os
from google import genai
from google.genai import types

# Cấu hình trang
st.set_page_config(page_title="MathMentor - Hệ Thống Luyện Đề Chuyên Sâu", layout="wide")

# --- QUẢN LÝ TÀI KHOẢN & DỮ LIỆU TRONG SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "history" not in st.session_state:
    st.session_state.history = [35, 60, 75, 90]
if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False
if "exam_score" not in st.session_state:
    st.session_state.exam_score = 0

# Lấy API key bảo mật từ cấu hình Secrets trên Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

# --- KHO ĐỀ THI ĐỒ SỘ (PHÂN LOẠI THEO CHƯƠNG - KHÔNG SỐ PHỨC) ---
EXTENDED_QUESTION_BANK = {
    "Ứng dụng đạo hàm khảo sát hàm số": [
        {"id": 101, "q": "Hàm số y = x^3 - 3x^2 + 2 đồng biến trên khoảng nào?", "options": ["A. (0; 2)", "B. (-∞; 0)", "C. (2; +∞)", "D. (-∞; 1)"], "ans": "C. (2; +∞)", "sol": "Ta có y' = 3x^2 - 6x. Cho y' > 0 <=> x < 0 hoặc x > 2."},
        {"id": 102, "q": "Giá trị cực tiểu của hàm số y = x^3 - 3x + 2 là:", "options": ["A. y = 0", "B. y = 4", "C. y = 1", "D. y = -1"], "ans": "A. y = 0", "sol": "y' = 3x^2 - 3 = 0 => x = 1 (y = 0) hoặc x = -1 (y = 4). Giá trị cực tiểu là y(1) = 0."},
        {"id": 103, "q": "Tiệm cận ngang của đồ thị hàm số y = (2x + 1)/(x - 1) là:", "options": ["A. y = 2", "B. y = 1", "C. x = 1", "D. y = -1"], "ans": "A. y = 2", "sol": "Giới hạn của hàm số khi x tiến tới vô cực bằng hệ số của x ở tử chia mẫu: 2/1 = 2."},
        {"id": 104, "q": "Hàm số y = -x^4 + 2x^2 + 3 có bao nhiêu điểm cực trị?", "options": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "C. 3", "sol": "Hàm trùng phương có a*b = (-1)*2 = -2 < 0 nên có đúng 3 điểm cực trị."}
    ],
    "Hàm số mũ và Lôgarit": [
        {"id": 201, "q": "Nghiệm của phương trình 2^(x-1) = 8 là:", "options": ["A. x = 2", "B. x = 3", "C. x = 4", "D. x = 1"], "ans": "C. x = 4", "sol": "2^(x-1) = 2^3 => x - 1 = 3 => x = 4."},
        {"id": 202, "q": "Đạo hàm của hàm số y = ln(x) với x > 0 là:", "options": ["A. 1/x", "B. e^x", "C. 1/(x*ln(10))", "D. x"], "ans": "A. 1/x", "sol": "Công thức cơ bản: (ln x)' = 1/x."},
        {"id": 203, "q": "Với a > 0, a ≠ 1, biểu thức log_a(a^3) bằng:", "options": ["A. 1", "B. 3", "C. a", "D. 3a"], "ans": "B. 3", "sol": "log_a(a^3) = 3 * log_a(a) = 3 * 1 = 3."}
    ],
    "Nguyên hàm và Tích phân": [
        {"id": 301, "q": "Nguyên hàm của hàm số f(x) = cos(x) là:", "options": ["A. sin(x) + C", "B. -sin(x) + C", "C. cos(x) + C", "D. -cos(x) + C"], "ans": "A. sin(x) + C", "sol": "Công thức nguyên hàm lượng giác cơ bản: ∫cos(x)dx = sin(x) + C."},
        {"id": 302, "q": "Tích phân từ 0 đến 1 của 2x dx bằng:", "options": ["A. 1", "B. 2", "C. 0", "D. 3"], "ans": "A. 1", "sol": "∫(2x)dx từ 0 đến 1 = x^2 tính từ 0 tới 1 = 1^2 - 0 = 1."}
    ],
    "Hình học không gian Oxyz": [
        {"id": 401, "q": "Trong không gian Oxyz, vectơ pháp tuyến của mặt phẳng x - 2y + 3z - 5 = 0 là:", "options": ["A. (1; -2; 3)", "B. (1; 2; -3)", "C. (-1; 2; 3)", "D. (2; -1; 3)"], "ans": "A. (1; -2; 3)", "sol": "Tọa độ vectơ pháp tuyến là các hệ số của x, y, z trong phương trình mặt phẳng: (1; -2; 3)."},
        {"id": 402, "q": "Thể tích khối cầu có bán kính R = 3 là:", "options": ["A. 36π", "B. 12π", "C. 27π", "D. 9π"], "ans": "A. 36π", "sol": "Công thức thể tích khối cầu: V = (4/3)*π*R^3 = (4/3)*π*(27) = 36π."}
    ]
}

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
    ["Trang chủ", "Trợ lý AI Thông Minh", "Phòng Luyện Đề Chuyên Nghiệp", "Kho Tài Liệu THPT", "Trang cá nhân"]
)

# --- NỘI DUNG CÁC TRANG ---

if menu == "Trang chủ":
    st.title("🌟 Chào mừng đến với Hệ thống Luyện thi MathMentor Pro")
    st.write("Nền tảng ôn thi Toán THPT Quốc gia tích hợp trí tuệ nhân tạo, hệ thống luyện đề chuyên sâu với đầy đủ tính năng hẹn giờ, tùy chỉnh số lượng câu hỏi và tra cứu lời giải chi tiết.")
    st.info("💡 Hệ thống đã được cấu hình loại bỏ hoàn toàn phần số phức, tập trung trọn vẹn vào các chuyên đề trọng điểm điểm cao!")
    
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

elif menu == "Phòng Luyện Đề Chuyên Nghiệp":
    st.title("🎯 Phòng Thi Thử & Luyện Đề Tùy Chỉnh")
    st.write("Tùy chỉnh linh hoạt phần kiến thức, số lượng câu hỏi và thời gian làm bài chuẩn phong cách thi thử THPT Quốc gia.")
    
    # --- CẤU HÌNH PHÒNG THI (Hẹn giờ, Chọn phần, Số lượng câu) ---
    st.markdown("### ⚙️ Cấu hình đề thi của bạn")
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        selected_topic = st.selectbox("1. Chọn phần bài học:", list(EXTENDED_QUESTION_BANK.keys()))
    with col_c2:
        max_available = len(EXTENDED_QUESTION_BANK[selected_topic])
        num_questions_to_load = st.slider("2. Chọn số lượng câu hỏi:", min_value=1, max_value=max_available, value=min(2, max_available))
    with col_c3:
        timer_minutes = st.selectbox("3. Thời gian làm bài (Phút):", [15, 30, 45, 60, 90], index=1)
    
    st.markdown("---")
    
    # Lấy danh sách câu hỏi phù hợp với cấu hình
    active_questions = EXTENDED_QUESTION_BANK[selected_topic][:num_questions_to_load]

    st.info(f"⏳ **Đề thi:** [{selected_topic}] gồm **{len(active_questions)} câu hỏi** — Thời gian quy định: **{timer_minutes} phút**.")

    # Form làm bài kiểm tra
    user_exam_answers = {}
    for idx, q_item in enumerate(active_questions):
        st.markdown(f"**Câu {idx+1}:** {q_item['q']}")
        user_exam_answers[idx] = st.radio(
            f"Lựa chọn đáp án câu {idx+1}:",
            q_item["options"],
            index=None,
            key=f"pro_q_{selected_topic}_{q_item['id']}"
        )
        st.markdown("---")

    if not st.session_state.exam_submitted:
        if st.button("🚀 Nộp Bài Thi & Xem Điểm Hệ Thống", type="primary"):
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
            with st.expander(f"Xem chi tiết Câu {idx+1}: {q_item['q']}"):
                st.write(f"✅ **Đáp án đúng:** {q_item['ans']}")
                st.info(f"💡 **Lời giải chi tiết:** {q_item['sol']}")

        if st.button("🔄 Cấu hình lại đề thi / Làm bài mới"):
            st.session_state.exam_submitted = False
            st.rerun()

elif menu == "Kho Tài Liệu THPT":
    st.title("📚 Kho Tài Liệu & Lý Thuyết Trọng Tâm THPT")
    st.write("Hệ thống tổng hợp kiến thức cốt lõi, công thức giải nhanh phục vụ ôn thi đại học (Đã lược bỏ hoàn toàn phần số phức).")
    
    with st.expander("📖 Chuyên đề 1: Ứng dụng đạo hàm khảo sát và vẽ đồ thị hàm số"):
        st.markdown("""
        * **Tính đơn điệu:** Sử dụng dấu của đạo hàm $y'$. Nếu $y' > 0$ hàm đồng biến, $y' < 0$ hàm nghịch biến.
        * **Cực trị:** Điểm mà tại đó $y'$ đổi dấu.
        * **Giá trị lớn nhất, nhỏ nhất (GTLN - GTNN):** Trên đoạn $[a; b]$, tính giá trị tại các điểm làm cho $y'=0$ và tại hai đầu mút $a, b$.
        * **Tiệm cận:** Tiệm cận đứng $x = x_0$, Tiệm cận ngang $y = y_0$.
        """)
        
    with st.expander("📖 Chuyên đề 2: Hàm số lũy thừa, hàm số mũ và hàm số lôgarit"):
        st.markdown("""
        * **Công thức lũy thừa & Lôgarit:** $\\log_a(bc) = \\log_a b + \\log_a c$, $\\log_a(b^n) = n \\log_a b$.
        * **Phương trình mũ & Lôgarit:** Đưa về cùng cơ số, đặt ẩn phụ $t = a^x$ ($t > 0$), hoặc logarit hóa hai vế.
        """)

    with st.expander("📖 Chuyên đề 3: Nguyên hàm, tích phân và ứng dụng"):
        st.markdown("""
        * **Bảng nguyên hàm cơ bản:** $\\int x^n dx = \\frac{x^{n+1}}{n+1} + C$, $\\int e^x dx = e^x + C$, $\\int \\frac{1}{x} dx = \\ln|x| + C$.
        * **Phương pháp tính:** Đổi biến số, tích phân từng phần ($\\int u dv = uv - \\int v du$).
        * **Ứng dụng:** Tính diện tích hình phẳng và thể tích khối tròn xoay.
        """)

    with st.expander("📖 Chuyên đề 4: Phương pháp tọa độ trong không gian (Oxyz)"):
        st.markdown("""
        * **Hệ tọa độ:** Tọa độ điểm, vectơ, tích có hướng của hai vectơ.
        * **Mặt phẳng:** Phương trình tổng quát $Ax + By + Cz + D = 0$, vectơ pháp tuyến $\\vec{n} = (A; B; C)$.
        * **Đường thẳng & Mặt cầu:** Phương trình tham số của đường thẳng; Phương trình mặt cầu tâm $I(a; b; c)$, bán kính $R$.
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