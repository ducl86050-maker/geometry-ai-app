import streamlit as st
import os
from google import genai
from google.genai import types

# Cấu hình trang
st.set_page_config(page_title="MathMentor - Trợ Lý Toán Học AI", layout="wide")

# Khởi tạo lưu trữ lịch sử bài làm trong session của trình duyệt
if "history" not in st.session_state:
    st.session_state.history = [15, 27]  # Dữ liệu điểm số mẫu ban đầu giống hình 6

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
    st.write("Nền tảng học toán thông minh tích hợp Trợ lý AI, hệ thống luyện đề tự chấm điểm và công cụ trực quan hóa.")
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
    st.subheader("ĐỀ MINH HỌA THPT QG 2024")
    
    st.progress(0.25, text="Đề kiểm tra trắc nghiệm toán")
    
    # Câu hỏi 1
    st.markdown("### Câu 1: Hàm số $y = x^3 - 3x^2 + 2$ đồng biến trên khoảng nào dưới đây?")
    ans1 = st.radio(
        "Chọn đáp án câu 1:",
        ("A. $(0; 2)$", "B. $(-\\infty; 0)$", "C. $(2; +\\infty)$", "D. $(-\\infty; 1)$"),
        index=None,
        key="q1"
    )
    
    # Câu hỏi 2
    st.markdown("### Câu 2: Nghiệm của phương trình $2^{x-1} = 8$ là bao nhiêu?")
    ans2 = st.radio(
        "Chọn đáp án câu 2:",
        ("A. $x = 2$", "B. $x = 3$", "C. $x = 4$", "D. $x = 1$"),
        index=None,
        key="q2"
    )
    
    if not st.session_state.quiz_submitted:
        if st.button("Nộp bài & Chấm điểm", type="primary"):
            correct = 0
            # Đáp án đúng: Câu 1 là C ((2; +infty)), Câu 2 là C (x = 4 vì 2^(4-1) = 2^3 = 8)
            if ans1 and "C." in ans1:
                correct += 50
            if ans2 and "C." in ans2:
                correct += 50
            
            st.session_state.score = correct
            st.session_state.quiz_submitted = True
            st.session_state.history.append(correct)  # Lưu điểm vào lịch sử
            st.rerun()
    else:
        st.success(f"🎉 Bạn đã nộp bài! Điểm số của bạn là: **{st.session_state.score} / 100**")
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
        if st.button("Tạo bài tập mới từ chuyên đề này"):
            st.success("Đã tạo thành công bộ bài tập chuyên đề Đạo hàm để luyện tập!")

elif menu == "Trang cá nhân":
    st.title("👤 Hồ Sơ Người Dùng & Đánh Giá Năng Lực")
    
    col_u1, col_u2 = st.columns([1, 1])
    with col_u1:
        st.markdown("### 📧 giakhanhtran88@gmail.com")
        st.write("Trạng thái: **Đã đăng nhập**")
        
        # Tính điểm trung bình thực tế từ lịch sử làm bài
        avg_score = sum(st.session_state.history) / len(st.session_state.history)
        st.metric(label="Điểm trung bình các bài kiểm tra", value=f"{avg_score:.1f} / 100")
        st.error("Kỹ năng cần bồi dưỡng: Đề minh họa THPT QG 2024")
    
    with col_u2:
        st.markdown("### 💡 Gợi ý tiếp theo")
        st.info("Dựa trên kết quả bài kiểm tra gần nhất - Hãy xem lại lý thuyết và luyện thêm các bài tập tự luận nâng cao.")
        if st.button("Tạo đề phù hợp năng lực", type="primary"):
            st.toast("Đang tạo đề xuất đề thi riêng cho bạn...")
    
    st.markdown("---")
    st.subheader("📈 Xu hướng điểm số các lần làm bài (Cập nhật thực tế)")
    # Hiển thị biểu đồ cột theo dữ liệu lưu trữ thật trong session
    st.bar_chart(st.session_state.history)