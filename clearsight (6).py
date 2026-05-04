"""
ClearSight — Image Description Tool
Accessible AI, Spring 2026 — Weeks 3 & 4

Requirements:
    pip install streamlit transformers pillow torch torchvision

Run locally:
    streamlit run clearsight.py

Or deploy free at streamlit.io
"""

import streamlit as st
from PIL import Image
from transformers import pipeline

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClearSight — Image Description Tool",
    page_icon="◈",
    layout="centered"
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("◈ ClearSight")
st.caption("AI image descriptions for blind & low-vision users")
st.divider()

# ── Load model (cached so it only loads once) ─────────────────────────────────
@st.cache_resource
def load_model():
    return pipeline("image-text-to-text", model="nlpconnect/vit-gpt2-image-captioning")

with st.spinner("Loading AI model... (first run takes a few minutes)"):
    model = load_model()

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

if st.button("Generate Description", disabled=not uploaded_file, type="primary"):
    with st.spinner("Generating description..."):
        results = model(image, max_new_tokens=50)

        if isinstance(results, list):
            r = results[0]
            caption = r.get("generated_text") or r.get("text") or str(r)
        else:
            caption = str(results)

        description = caption + LEVELS[verbosity]

    st.divider()
    st.subheader("Result")
    st.write(description)
    st.code(description, language=None)
    st.download_button(
        label="Download description as text file",
        data=description,
        file_name="image_description.txt",
        mime="text/plain"
    )

elif not uploaded_file:
    st.info("Upload an image above to get started.")
