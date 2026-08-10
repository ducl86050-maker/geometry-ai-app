import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Hình Học Phẳng", layout="wide")

st.title("🤖 Trợ lý AI Hình Học Phẳng (Gemini & GeoGebra)")

# Nhập API Key (có thể cấu hình ẩn trên Streamlit Cloud sau)
api_key = st.os.environ.get("GEMINI_API_KEY") or st.text_input("Nhập Google Gemini API Key của bạn:", type="password")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Khung Hỏi Đáp AI")
    user_prompt = st.text_area("Nhập câu hỏi hình học của bạn:", placeholder="VD: Cho tam giác ABC vuông tại A...")
    uploaded_file = st.file_uploader("Hoặc tải lên hình ảnh đề bài:", type=["png", "jpg", "jpeg"])
    
    if st.button("Gửi & Phân Tích", type="primary"):
        if not api_key:
            st.error("Vui lòng nhập Gemini API Key!")
        elif not user_prompt and not uploaded_file:
            st.warning("Vui lòng nhập câu hỏi hoặc tải ảnh lên!")
        else:
            with st.spinner("AI đang phân tích..."):
                try:
                    client = genai.Client(api_key=api_key)
                    contents = [user_prompt]
                    
                    if uploaded_file:
                        # Lưu tạm file ảnh để gửi lên Gemini
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
    # Nhúng trực tiếp GeoGebra Web App vào Streamlit bằng iframe
    geogebra_html = """
    <iframe src="https://www.geogebra.org/geometry" width="100%" height="600px" style="border:1px solid #ccc; border-radius:8px;" allowfullscreen></iframe>
    """
    st.markdown(geogebra_html, unsafe_allow_html=True)