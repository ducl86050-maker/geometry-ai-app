import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Hình Học Phẳng", layout="wide")

st.title("🤖 Trợ lý AI Hình Học Phẳng (Gemini & GeoGebra)")

# Lấy API key bảo mật từ cấu hình Secrets trên Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Khung Hỏi Đáp AI")
    user_prompt = st.text_area("Nhập câu hỏi hình học của bạn:", placeholder="VD: Cho tam giác ABC vuông tại A...")
    uploaded_file = st.file_uploader("Hoặc tải lên hình ảnh đề bài:", type=["png", "jpg", "jpeg"])
    
    if st.button("Gửi & Phân Tích", type="primary"):
        if not api_key:
            st.error("Chưa cấu hình API Key trong hệ thống của Streamlit!")
        elif not user_prompt and not uploaded_file:
            st.warning("Vui lòng nhập câu hỏi hoặc tải ảnh lên!")
        else:
            with st.spinner("AI đang phân tích..."):
                try:
                    client = genai.Client(api_key=api_key)
                    contents = [user_prompt] if user_prompt else []
                    
                    if uploaded_file:
                        bytes_data = uploaded_file.getvalue()
                        contents.append(types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type))
                    
                    system_instruction = "Bạn là một chuyên gia về hình học phẳng, hãy giải quyết bài toán chi tiết, rõ ràng bước làm."
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
    st.info("Bấm vào nút bên dưới để mở bảng vẽ GeoGebra lớn và đầy đủ tính năng:")
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
    st.image("https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=600&q=80", caption="Công cụ hỗ trợ trực quan hình học", use_container_width=True)