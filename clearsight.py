"""
ClearSight — Image Description Tool
Accessible AI, Spring 2026 — Weeks 3 & 4
"""

import streamlit as st
import anthropic
import base64
from PIL import Image
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClearSight — Image Description Tool",
    page_icon="◈",
    layout="centered"
)

# ── Anthropic client ──────────────────────────────────────────────────────────
API_KEY = "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"

client = anthropic.Anthropic(api_key=API_KEY)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("◈ ClearSight")
st.caption("AI image descriptions for blind & low-vision users — Accessible AI, Spring 2026")
st.divider()

# ── Verbosity levels ──────────────────────────────────────────────────────────
LEVELS = {
    "Brief — one sentence only": "Describe this image in exactly one sentence. Be concise — only the most essential information. Never start with 'This image shows'.",
    "Standard — main subject and context": "Describe this image in 2-3 sentences. Cover the main subject, setting, and important context. Never start with 'This image shows'.",
    "Detailed — colors, layout, expressions": "Describe this image in a full paragraph. Include colors, layout, spatial relationships, and facial expressions if present. Never start with 'This image shows'.",
    "Comprehensive — everything including text and fine details": "Give a comprehensive description. Include all visible text, colors, layout, mood, people and their expressions, and everything a blind user needs to fully understand the image. Never start with 'This image shows'."
}

# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.subheader("1. Upload an image")
uploaded_file = st.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png", "webp", "bmp"],
    help="Supported formats: JPG, PNG, WebP, BMP"
)

image = None
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

def describe_image(pil_image, prompt):
    # Convert image to base64
    buf = io.BytesIO()
    pil_image.save(buf, format="JPEG")
    image_b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system="You are an expert image describer for blind and low-vision users. Write clear, specific descriptions.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    return message.content[0].text.strip()

if st.button("Generate Description", disabled=not uploaded_file, type="primary"):
    with st.spinner("Generating description..."):
        try:
            prompt = LEVELS[verbosity]
            description = describe_image(image, prompt)

            st.divider()
            st.subheader("Result")
            st.write(description)
            st.download_button(
                label="Download as text file",
                data=description,
                file_name="image_description.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif not uploaded_file:
    st.info("Upload an image above to get started.")
