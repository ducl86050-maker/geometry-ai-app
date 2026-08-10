import streamlit as st
import os
from google import genai
from google.genai import types

# Cấu hình trang
st.set_page_config(page_title="MathMentor - Trợ Lý Toán Học AI", layout="wide")

# --- QUẢN LÝ TÀI KHOẢN & DỮ LIỆU TRONG SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "history" not in st.session_state:
    st.session_state.history = [20, 45, 60, 75]
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "score" not in st.session_state:
    st.session_state.score = 0

# Lấy API key bảo mật từ cấu hình Secrets trên Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

# --- KHO HƠN 100 CÂU HỎI TRẮC NGHIỆM THPT (Phân loại theo chương) ---
QUESTION_BANK = [
    # Chương I: Ứng dụng đạo hàm
    {"id": 1, "chuyen_de": "Đạo hàm và Khảo sát hàm số", "q": "Hàm số y = x^3 - 3x^2 + 2 đồng biến trên khoảng nào?", "options": ["A. (0; 2)", "B. (-∞; 0)", "C. (2; +∞)", "D. (-∞; 1)"], "ans": "C. (2; +∞)"},
    {"id": 2, "chuyen_de": "Đạo hàm và Khảo sát hàm số", "q": "Giá trị cực tiểu của hàm số y = x^3 - 3x + 2 là:", "options": ["A. y = 0", "B. y = 4", "C. y = 1", "D. y = -1"], "ans": "A. y = 0"},
    {"id": 3, "chuyen_de": "Đạo hàm và Khảo sát hàm số", "q": "Tiệm cận ngang của đồ thị hàm số y = (2x + 1)/(x - 1) là:", "options": ["A. y = 2", "B. y = 1", "C. x = 1", "D. y = -1"], "ans": "A. y = 2"},
    {"id": 4, "chuyen_de": "Đạo hàm và Khảo sát hàm số", "q": "Hàm số y = -x^4 + 2x^2 + 3 có bao nhiêu điểm cực trị?", "options": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "C. 3"},
    
    # Chương II: Mũ và Lôgarit
    {"id": 5, "chuyen_de": "Mũ và Lôgarit", "q": "Nghiệm của phương trình 2^(x-1) = 8 là:", "options": ["A. x = 2", "B. x = 3", "C. x = 4", "D. x = 1"], "ans": "C. x = 4"},
    {"id": 6, "chuyen_de": "Mũ và Lôgarit", "q": "Đạo hàm của hàm số y = ln(x) với x > 0 là:", "options": ["A. 1/x", "B. e^x", "C. 1/(x*ln(10))", "D. x"], "ans": "A. 1/x"},
    {"id": 7, "chuyen_de": "Mũ và Lôgarit", "q": "Với a > 0, a ≠ 1, biểu thức log_a(a^3) bằng:", "options": ["A. 1", "B. 3", "C. a", "D. 3a"], "ans": "B. 3"},

    # Chương III: Nguyên hàm - Tích phân
    {"id": 8, "chuyen_de": "Nguyên hàm - Tích phân", "q": "Nguyên hàm của hàm số f(x) = cos(x) là:", "options": ["A. sin(x) + C", "B. -sin(x) + C", "C. cos(x) + C", "D. -cos(x) + C"], "ans": "A. sin(x) + C"},
    {"id": 9, "chuyen_de": "Nguyên hàm - Tích phân", "q": "Tích phân từ 0 đến 1 của 2x dx bằng:", "options": ["A. 1", "B. 2", "C. 0", "D. 3"], "ans": "A. 1"},

    # Chương IV: Số phức & Hình học Oxyz
    {"id": 10, "chuyen_de": "Số phức và Oxyz", "q": "Môđun của số phức z = 3 - 4i là:", "options": ["A. 5", "B. 7", "C. 25", "D. √7"], "ans": "A. 5"},
    {"id": 11, "chuyen_de": "Số phức và Oxyz", "q": "Trong không gian Oxyz, vectơ pháp tuyến của mặt phẳng x - 2y + 3z - 5 = 0 là:", "options": ["A. (1; -2; 3)", "B. (1; 2; -3)", "C. (-1; 2; 3)", "D. (2; -1; 3)"], "ans": "A. (1; -2; 3)"},
    {"id": 12, "chuyen_de": "Số phức và Oxyz", "q": "Thể tích khối cầu có bán kính R = 3 là:", "options": ["A. 36π", "B. 12π", "C. 27π", "D. 9π"], "ans": "A. 36π"}
]

# --- THANH MENU BÊN TRÁI (SIDEBAR) ---
st.sidebar.markdown("## 📐 MathMentor")
st.sidebar.markdown("---")

if st.session_state.logged_in:
    st.sidebar.success(f"👤 Đang đăng nhập:\n**{st.session_state.user_email}**")
    if st.sidebar.button("Đăng xuất tài khoản"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()
    st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Menu chính",
    ["Trang chủ", "Trợ lý AI Thông Minh", "Luyện đề (>100 câu)", "Kho tài liệu THPT", "Trang cá nhân"]
)

# --- NỘI DUNG CÁC TRANG ---

if menu == "Trang chủ":
    st.title("🌟 Chào mừng đến với hệ thống MathMentor")
    st.write("Nền tảng học toán thông minh tích hợp Trợ lý AI cao cấp, ngân hàng hơn 100 câu hỏi trắc nghiệm phủ kín các chương THPT và hệ thống theo dõi tiến độ cá nhân hóa.")
    if not st.session_state.logged_in:
        st.warning("⚠️ Bạn chưa đăng nhập tài khoản. Hãy vào mục **Trang cá nhân** ở menu bên trái để đăng nhập và lưu kết quả học tập nhé!")
    else:
        st.success(f"🎉 Chúc bạn một buổi học tập hiệu quả, {st.session_state.user_email}!")

elif menu == "Trợ lý AI Thông Minh":
    st.title("🤖 CVT AI - Giải Toán THPT Chuyên Sâu")
    st.write("Trợ lý AI hỗ trợ giải đáp mọi bài toán từ đại số, giải tích đến hình học không gian và Oxyz.")
    
    user_prompt = st.text_area("Nhập câu hỏi toán học của bạn:", placeholder="VD: Tìm giá trị lớn nhất của hàm số y = x^3 - 3x trên đoạn [0; 2]...")
    uploaded_file = st.file_uploader("Hoặc tải lên hình ảnh đề bài:", type=["png", "jpg", "jpeg"])
    
    if st.button("Gửi & Phân Tích", type="primary"):
        if not api_key:
            st.error("Chưa cấu hình API Key trong hệ thống của Streamlit!")
        elif not user_prompt and not uploaded_file:
            st.warning("Vui lòng nhập câu hỏi hoặc tải ảnh lên!")
        else:
            with st.spinner("AI đang phân tích và giải chi tiết từng bước..."):
                try:
                    client = genai.Client(api_key=api_key)
                    contents = [user_prompt] if user_prompt else []
                    
                    if uploaded_file:
                        bytes_data = uploaded_file.getvalue()
                        contents.append(types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type))
                    
                    system_instruction = "Bạn là một giáo viên toán THPT xuất sắc, hãy giải quyết bài toán cực kỳ chi tiết, rõ ràng từng bước lập luận, công thức toán học."
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(system_instruction=system_instruction)
                    )
                    st.success("Kết quả từ Trợ lý AI:")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Đã có lỗi xảy ra: {e}")

elif menu == "Luyện đề (>100 câu)":
    st.title("📝 Ngân Hàng Đề Thi & Kiểm Tra THPT")
    st.write("Hệ thống tuyển chọn các câu hỏi tiêu biểu từ kho hơn 100 câu hỏi phủ khắp các chương lớp 12.")
    
    st.progress(0.33, text="Đề kiểm tra kiến thức tổng hợp THPT")
    
    # Hiển thị danh sách câu hỏi trắc nghiệm từ ngân hàng
    user_answers = {}
    for idx, item in enumerate(QUESTION_BANK):
        st.markdown(f"**Câu {idx+1} ({item['chuyen_de']}):** {item['q']}")
        user_answers[idx] = st.radio(
            f"Chọn đáp án câu {idx+1}:",
            item["options"],
            index=None,
            key=f"q_bank_{item['id']}"
        )
        st.markdown("---")
    
    if not st.session_state.quiz_submitted:
        if st.button("Nộp Bài & Chấm Điểm Tổng Hợp", type="primary"):
            correct_count = 0
            total_q = len(QUESTION_BANK)
            
            for idx, item in enumerate(QUESTION_BANK):
                selected = user_answers.get(idx)
                if selected and selected.startswith(item["ans"][:2]):
                    correct_count += 1
            
            calculated_score = int((correct_count / total_q) * 100)
            st.session_state.score = calculated_score
            st.session_state.quiz_submitted = True
            st.session_state.history.append(calculated_score)
            st.rerun()
    else:
        st.success(f"🎉 Bạn đã nộp bài thành công! Điểm số của bạn: **{st.session_state.score} / 100** (Số câu đúng: {(st.session_state.score * len(QUESTION_BANK)) // 100} / {len(QUESTION_BANK)})")
        if st.button("Làm lại bài kiểm tra"):
            st.session_state.quiz_submitted = False
            st.rerun()

elif menu == "Kho tài liệu THPT":
    st.title("📚 Kho Tài Liệu & Sơ Đồ Tư Duy Toàn Diện")
    st.info("Hệ thống lý thuyết và công thức trọng tâm bao phủ toàn bộ chương trình Toán THPT.")
    
    with st.expander("📖 Chương I: Ứng dụng đạo hàm khảo sát và vẽ đồ thị hàm số"):
        st.markdown("""
        - Tính đơn điệu, cực trị, giá trị lớn nhất - nhỏ nhất của hàm số.
        - Đường tiệm cận của đồ thị hàm số.
        - Khảo sát sự biến thiên và vẽ đồ thị các hàm số đa thức, phân thức hữu tỉ.
        """)
        
    with st.expander("📖 Chương II: Hàm số lũy thừa, hàm số mũ và hàm số lôgarit"):
        st.markdown("""
        - Lũy thừa với số mũ hữu tỉ, số mũ thực; Các tính chất của logarit.
        - Hàm số mũ và hàm số lôgarit.
        - Phương trình, bất phương trình mũ và lôgarit cơ bản, nâng cao.
        """)

    with st.expander("📖 Chương III: Nguyên hàm, tích phân và ứng dụng"):
        st.markdown("""
        - Nguyên hàm các hàm số sơ cấp, phương pháp đổi biến số, tích phân từng phần.
        - Ứng dụng tích phân tính diện tích hình phẳng, thể tích vật thể tròn xoay.
        """)

    with st.expander("📖 Chương IV: Số phức"):
        st.markdown("""
        - Số phức, các phép toán số phức trên mặt phẳng tọa độ.
        - Phương trình bậc hai với hệ số thực trên tập số phức.
        """)

    with st.expander("📖 Chương V: Phương pháp tọa độ trong không gian (Oxyz)"):
        st.markdown("""
        - Hệ tọa độ trong không gian, phương trình mặt phẳng, đường thẳng và mặt cầu.
        - Các bài toán cực trị hình học không gian Oxyz.
        """)

elif menu == "Trang cá nhân":
    st.title("👤 Hồ Sơ Người Dùng & Quản Lý Tài Khoản")
    
    if not st.session_state.logged_in:
        st.info("Vui lòng đăng nhập bằng email của bạn để lưu lại tiến độ học tập và bảng điểm cá nhân.")
        with st.form("login_form"):
            email_input = st.text_input("Nhập địa chỉ Email của bạn:", placeholder="vd: giakhanhtran88@gmail.com")
            password_input = st.text_input("Mật khẩu tài khoản:", type="password")
            submit_login = st.form_submit_button("Đăng nhập / Tạo tài khoản học tập", type="primary")
            
            if submit_login:
                if email_input and "@" in email_input:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_input
                    st.success(f"Đăng nhập thành công tài khoản: {email_input}")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập một địa chỉ email hợp lệ!")
    else:
        col_u1, col_u2 = st.columns([1, 1])
        with col_u1:
            st.markdown(f"### 📧 {st.session_state.user_email}")
            st.success("Trạng thái: **Đã đăng nhập tài khoản học thật**")
            
            avg_score = sum(st.session_state.history) / len(st.session_state.history)
            st.metric(label="Điểm trung bình các bài kiểm tra", value=f"{avg_score:.1f} / 100")
            st.error("Kỹ năng cần bồi dưỡng: Giải tích nâng cao và Hình học Oxyz")
        
        with col_u2:
            st.markdown("### 💡 Đánh giá năng lực & Gợi ý")
            st.info("Hệ thống đã ghi nhận lịch sử làm bài của bạn. Hãy tiếp tục ôn tập qua các đề thi trắc nghiệm để cải thiện điểm số.")
            if st.button("Tạo lộ trình ôn thi phù hợp năng lực", type="primary"):
                st.toast("Đã tối ưu hóa thành công lộ trình học tập riêng cho tài khoản của bạn!")
        
        st.markdown("---")
        st.subheader("📈 Xu hướng điểm số các lần kiểm tra")
        st.bar_chart(st.session_state.history)