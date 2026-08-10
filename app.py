import streamlit as st
import os
from google import genai
from google.genai import types

# Cấu hình trang
st.set_page_config(page_title="MathMentor - Trợ Lý Toán Học AI", layout="wide")

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
    st.write("Nền tảng học toán thông minh tích hợp Trợ lý AI và công cụ trực quan hóa hình học hàng đầu.")
    st.info("👈 Hãy chọn các mục trong menu bên trái để bắt đầu trải nghiệm các tính năng!")

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
        st.write("Do trình duyệt chặn khung nhúng trực tiếp, bạn hãy bấm nút bên dưới để mở bảng vẽ không gian/hình học lớn:")
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
        st.image("https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=600&q=80", caption="Công cụ hỗ trợ trực quan", use_container_width=True)

elif menu == "Luyện đề & Kiểm tra":
    st.title("📝 Kiểm tra & Luyện Đề THPT QG")
    st.subheader("ĐỀ MINH HỌA THPT QG 2024")
    
    # Giao diện làm bài kiểm tra giả lập (Hình 5)
    st.progress(0.08, text="8% hoàn thành (Câu 1 / 12)")
    
    st.markdown("### Câu 1: Hàm số $y = x^3 - 3x^2 + 2$ đồng biến trên khoảng nào dưới đây?")
    
    ans = st.radio(
        "Chọn đáp án đúng:",
        ("A. $(0; 2)$", "B. $(-\\infty; 0)$", "C. $(2; +\\infty)$", "D. $(-\\infty; 1)$"),
        index=None
    )
    
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        st.button("⬅️ Câu trước")
    with col_next:
        st.button("Câu tiếp ➡️", type="primary")

elif menu == "Kho tài liệu":
    st.title("📚 Kho Tài Liệu & Sơ Đồ Tư Duy")
    st.info("Tổng hợp các chuyên đề luyện thi Toán THPT trọng tâm.")
    
    with st.expander("📖 CHƯƠNG I: ƯNG DỤNG ĐẠO HÀM ĐỂ KHẢO SÁT VÀ VẼ ĐỒ THỊ HÀM SỐ"):
        st.markdown("""
        * **1. Miễn Xác Định & Tính Liên Tục:** Xác định tập giá trị $D$ mà hàm số có nghĩa.
        * **2. Tính Đơn Điệu của Hàm Số:** Sử dụng đạo hàm bậc nhất ($f'(x)$) để xác định chiều biến thiên.
            * Nếu $f'(x) > 0$ trên $(a, b)$ thì hàm số đồng biến.
            * Nếu $f'(x) < 0$ trên $(a, b)$ thì hàm số nghịch biến.
        * **3. Cực Trị của Hàm Số:** Tìm điểm mà tại đó đạo hàm đổi dấu.
        """)
        if st.button("Tạo bài tập mới từ chuyên đề này"):
            st.success("Đã tạo đề luyện tập riêng cho chương này!")

elif menu == "Trang cá nhân":
    st.title("👤 Hồ Sơ Người Dùng & Đánh Giá Năng Lực")
    
    col_u1, col_u2 = st.columns([1, 1])
    with col_u1:
        st.markdown("### 📧 giakhanhtran88@gmail.com")
        st.write("Trạng thái: **Đã đăng nhập**")
        st.metric(label="Điểm trung bình các bài kiểm tra", value="22.0 / 100")
        st.error("Kỹ năng cần bồi dưỡng: Đề minh họa THPT QG 2024")
    
    with col_u2:
        st.markdown("### 💡 Gợi ý tiếp theo")
        st.info("Dựa trên lịch sử bài kiểm tra gần nhất: Độ chính xác 21.7% - Hãy xem lại lý thuyết và luyện thêm 2-3 bài tự luận.")
        st.button("Tạo đề phù hợp năng lực", type="primary")
    
    st.markdown("---")
    st.subheader("📈 Xu hướng điểm số gần đây")
    # Biểu đồ mẫu mô phỏng hình 6
    chart_data = [15, 27]
    st.bar_chart(chart_data)