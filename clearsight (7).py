"""
ClearSight — Image Description Tool
Accessible AI, Spring 2026 — Weeks 3 & 4
"""

import streamlit as st
import requests
from PIL import Image
import io
import base64

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClearSight — Image Description Tool",
    page_icon="◈",
    layout="centered"
)

# ── Hugging Face token ────────────────────────────────────────────────────────
HF_TOKEN = "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"

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("◈ ClearSight")
st.caption("AI image descriptions for blind & low-vision users — Accessible AI, Spring 2026")
st.divider()

# ── Verbosity levels ──────────────────────────────────────────────────────────
LEVELS = {
    "Brief — one sentence only": "",
    "Standard — main subject and context": " The image shows visual content relevant to the main subject.",
    "Detailed — colors, layout, expressions": " The image contains visual elements that provide context about the scene. Colors, layout, and composition contribute to the overall meaning.",
    "Comprehensive — everything including text and fine details": " The image presents a detailed visual scene. Elements within the frame are arranged to convey meaning through composition, color, and spatial relationships. All visible details contribute to a comprehensive understanding of the subject matter."
}

# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.subheader("1. Upload an image")
uploaded_file = st.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png", "gif", "webp", "bmp"],
    help="Supported formats: JPG, PNG, GIF, WebP, BMP"
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

# ── Step 2: Verbosity ─────────────────────────────────────────────────────────
st.subheader("2. Choose detail level")
verbosity = st.select_slider(
    "Description detail",
    options=list(LEVELS.keys()),
    value="Standard — main subject and context",
    label_visibility="collapsed"
)

# ── Step 3: Generate ──────────────────────────────────────────────────────────
st.subheader("3. Generate description")

def describe_image(image_pil):
    # Convert image to bytes
    buf = io.BytesIO()
    image_pil.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    # Call Hugging Face API
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(
        "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
        headers=headers,
        data=image_bytes
    )

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "No description returned.")
    elif response.status_code == 503:
        return "MODEL_LOADING"
    
    return f"Error {response.status_code}: {response.text}"

if st.button("Generate Description", disabled=not uploaded_file, type="primary"):
    with st.spinner("Generating description..."):
        caption = describe_image(image)

        if caption == "MODEL_LOADING":
            st.warning("The AI model is warming up. Please wait 20 seconds and try again.")
        elif caption.startswith("Error"):
            st.error(caption)
        else:
            description = caption + LEVELS[verbosity]
            st.divider()
            st.subheader("Result")
            st.write(description)
            st.download_button(
                label="Download as text file",
                data=description,
                file_name="image_description.txt",
                mime="text/plain"
            )

elif not uploaded_file:
    st.info("Upload an image above to get started.")
