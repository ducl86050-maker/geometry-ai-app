import streamlit as st
import os
from google import genai
from google.genai import types

# Cấu hình trang
st.set_page_config(page_title="MathMentor - Trợ Lý Toán Học AI", layout="wide")

# Khởi tạo dữ liệu lịch sử và điểm số trong session
if "history" not in st.session_state:
    st.session_state.history = [15, 27, 40]

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "score" not in st.session_state:
    st.session_state.score = 0

# Lấy API key bảo mật từ cấu hình Secrets trên Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

# --- THANH MENU BÊN TRÁI (SIDEBAR) ---
st.sidebar.markdown("## 📐 MathMentor")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Menu chính",
    ["Trang chủ", "Trợ lý AI & GeoGebra", "Luyện đề & Kiểm tra", "Kho tài liệu", "Trang cá nhân"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("Học tập")
history_tab = st.sidebar.selectbox("Lịch sử làm bài", ["Xem lịch sử gần đây", "Thống kê tiến độ"])

# --- NỘI DUNG TỪNG TRANG ---

if menu == "Trang chủ":
    st.title("🌟 Chào mừng bạn đến với MathMentor")
    st.write("Nền tảng học toán thông minh tích hợp Trợ lý AI, kho đề thi đa dạng và công cụ trực quan hóa hình học.")
    st.info("👈 Hãy chọn các mục trong menu bên trái để bắt đầu khám phá các tính năng!")

elif menu == "Trợ lý AI & GeoGebra":
    st.title("🤖 CVT AI - Giải Toán THPT")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Khung Hỏi Đáp AI")
        user_prompt = st.text_area("Nhập câu hỏi hình học/đại số của bạn:", placeholder="VD: Cho tam giác ABC vuông tại A...")
        uploaded_file = st.file_uploader("Hoặc tải lên hình ảnh đề bài:", type=["png", "jpg", "jpeg"])
        
        if st.button("Gửi & Phân Tích", type="primary"):
            if not api_key:
                st.error("Chưa cấu hình API Key trong hệ thống của Streamlit!")
            elif not user_prompt and not uploaded_file:
                st.warning("Vui lòng nhập câu hỏi hoặc tải ảnh lên!")
            else:
                with st.spinner("AI đang phân tích bài toán..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        contents = [user_prompt] if user_prompt else []
                        
                        if uploaded_file:
                            bytes_data = uploaded_file.getvalue()
                            contents.append(types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type))
                        
                        system_instruction = "Bạn là một giáo viên toán giỏi chuyên gia về hình học và giải tích THPT, hãy giải quyết bài toán chi tiết, rõ ràng từng bước."
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents,
                            config=types.GenerateContentConfig(system_instruction=system_instruction)
                        )
                        st.success("Kết quả từ AI:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Đã có lỗi xảy ra: {e}")

    with col2:
        st.subheader("Bảng vẽ GeoGebra Tương Tác")
        st.write("Mở bảng vẽ không gian/hình học lớn để tương tác trực quan:")
        st.markdown(
            """
            <a href="https://www.geogebra.org/geometry" target="_blank">
                <button style="background-color:#1976d2; color:white; padding:12px 20px; border:none; border-radius:6px; font-size:16px; cursor:pointer; font-weight:bold;">
                    🌐 Mở Bảng Vẽ GeoGebra Lớn
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=600&q=80", caption="Hỗ trợ hình học trực quan", use_container_width=True)

elif menu == "Luyện đề & Kiểm tra":
    st.title("📝 Kiểm tra & Luyện Đề THPT QG")
    st.subheader("ĐỀ MINH HỌA THPT QG - TỔNG HỢP NHIỀU CÂU HỎI")
    
    st.progress(0.25, text="Phần thi trắc nghiệm kiến thức toán học")
    
    # Danh sách nhiều câu hỏi đa dạng
    ans1 = st.radio(
        "**Câu 1:** Hàm số $y = x^3 - 3x^2 + 2$ đồng biến trên khoảng nào dưới đây?",
        ("A. $(0; 2)$", "B. $(-\\infty; 0)$", "C. $(2; +\\infty)$", "D. $(-\\infty; 1)$"),
        index=None, key="q1"
    )
    
    ans2 = st.radio(
        "**Câu 2:** Nghiệm của phương trình $2^{x-1} = 8$ là bao nhiêu?",
        ("A. $x = 2$", "B. $x = 3$", "C. $x = 4$", "D. $x = 1$"),
        index=None, key="q2"
    )

    ans3 = st.radio(
        "**Câu 3:** Cho cấp số cộng $(u_n)$ có số hạng đầu $u_1 = 2$ và công sai $d = 3$. Số hạng thứ 5 của cấp số cộng là:",
        ("A. $u_5 = 14$", "B. $u_5 = 11$", "C. $u_5 = 17$", "D. $u_5 = 12$"),
        index=None, key="q3"
    )

    ans4 = st.radio(
        "**Câu 4:** Thể tích $V$ của khối lập phương có cạnh bằng $a$ là:",
        ("A. $V = a^3$", "B. $V = 3a^3$", "C. $V = \\frac{1}{3}a^3$", "D. $V = a^2$"),
        index=None, key="q4"
    )
    
    if not st.session_state.quiz_submitted:
        if st.button("Nộp bài & Chấm điểm tổng hợp", type="primary"):
            correct_count = 0
            total_questions = 4
            
            # Đáp án đúng: Câu 1: C, Câu 2: C, Câu 3: B (u5 = u1 + 4d = 2 + 12 = 14 -> chờ chút: u1=2, u2=5, u3=8, u4=11, u5=14 -> Đáp án A), Câu 4: A (V = a^3)
            if ans1 and "C." in ans1: correct_count += 1
            if ans2 and "C." in ans2: correct_count += 1
            if ans3 and "A." in ans3: correct_count += 1
            if ans4 and "A." in ans4: correct_count += 1
            
            calculated_score = int((correct_count / total_questions) * 100)
            st.session_state.score = calculated_score
            st.session_state.quiz_submitted = True
            st.session_state.history.append(calculated_score)
            st.rerun()
    else:
        st.success(f"🎉 Bạn đã hoàn thành bài kiểm tra! Số điểm đạt được: **{st.session_state.score} / 100** (Số câu đúng: {st.session_state.score // 25}/4)")
        if st.button("Làm lại bài kiểm tra"):
            st.session_state.quiz_submitted = False
            st.rerun()

elif menu == "Kho tài liệu":
    st.title("📚 Kho Tài Liệu & Sơ Đồ Tư Duy")
    st.info("Tổng hợp các chuyên đề luyện thi Toán THPT trọng tâm.")
    
    with st.expander("📖 CHƯƠNG I: ỨNG DỤNG ĐẠO HÀM ĐỂ KHẢO SÁT VÀ VẼ ĐỒ THỊ HÀM SỐ"):
        st.markdown("""
        * **1. Miễn Xác Định & Tính Liên Tục:** Xác định tập giá trị $D$ mà hàm số có nghĩa.
        * **2. Tính Đơn Điệu của Hàm Số:** Sử dụng đạo hàm bậc nhất ($f'(x)$) để xác định chiều biến thiên.
            * Nếu $f'(x) > 0$ trên $(a, b)$ thì hàm số đồng biến.
            * Nếu $f'(x) < 0$ trên $(a, b)$ thì hàm số nghịch biến.
        * **3. Cực Trị của Hàm Số:** Tìm điểm mà tại đó đạo hàm đổi dấu.
        """)
        if st.button("Tạo bài tập mới từ chuyên đề Đạo hàm"):
            st.success("Đã tạo thành công bộ bài tập chuyên đề Đạo hàm nâng cao!")

    with st.expander("📖 CHƯƠNG II: HÀM SỐ LŨY THỪA, MŨ VÀ LOGARIT"):
        st.markdown("""
        * **1. Lũy thừa và tính chất:** Các công thức biến đổi lũy thừa với số mũ thực.
        * **2. Lôgarit:** Định nghĩa và các tính chất cơ bản $\\log_a(bc) = \\log_a b + \\log_a c$.
        * **3. Phương trình - Bất phương trình mũ và lôgarit:** Các phương pháp đặt ẩn phụ, lôgarit hóa.
        """)
        if st.button("Tạo bài tập mới từ chuyên đề Mũ - Logarit"):
            st.success("Đã tạo thành công bộ bài tập chuyên đề Mũ - Logarit!")

elif menu == "Trang cá nhân":
    st.title("👤 Hồ Sơ Người Dùng & Đánh Giá Năng Lực")
    
    col_u1, col_u2 = st.columns([1, 1])
    with col_u1:
        st.markdown("?")
        st.write("Trạng thái: **Đã đăng nhập**")
        
        avg_score = sum(st.session_state.history) / len(st.session_state.history)
        st.metric(label="Điểm trung bình các bài kiểm tra", value=f"{avg_score:.1f} / 100")
        st.error("Kỹ năng cần bồi dưỡng: Giải tích và Hình học không gian")
    
    with col_u2:
        st.markdown("### 💡 Gợi ý tiếp theo")
        st.info("Dựa trên kết quả lịch sử làm bài - Hãy xem lại lý thuyết hàm số mũ và luyện thêm các bài tập trắc nghiệm.")
        if st.button("Tạo đề phù hợp năng lực", type="primary"):
            st.toast("Đang tạo đề xuất đề thi riêng tối ưu theo năng lực...")
    
    st.markdown("---")
    st.subheader("📈 Xu hướng điểm số các lần luyện tập")
    st.bar_chart(st.session_state.history)