import base64
import json
import re
import os
from openai import OpenAI
import streamlit as st


def get_client():
    api_key = (
        st.secrets.get("OPENROUTER_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
    )
    if not api_key:
        raise RuntimeError("No OPENROUTER_API_KEY found in secrets.toml or environment.")
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def pdf_to_base64_images(file_bytes: bytes) -> list:
    try:
        import fitz
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf")
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        images.append(base64.standard_b64encode(pix.tobytes("png")).decode("utf-8"))
    doc.close()
    return images


def build_extraction_prompt(fields: list) -> str:
    field_list = "\n".join(
        f'  - id: "{f["id"]}", label: "{f["label"]}", type: "{f["type"]}", required: {f["required"]}'
        + (f', options: [{f.get("options", "")}]' if f["type"] == "Dropdown" else "")
        for f in fields
    )
    return f"""You are an intelligent form-filling assistant.

The user has built a custom form with the following fields:
{field_list}

Your job:
1. Read the uploaded document carefully (may be multiple pages).
2. Extract the value that best matches each form field.
3. Return a JSON object where each key is the field's `id`.

For each field return:
{{
  "field_id": {{
    "value": "<extracted value or empty string if not found>",
    "confidence": "<high|medium|low|missing>"
  }}
}}

Rules:
- If you cannot find a value, set value to "" and confidence to "missing".
- Never guess or hallucinate — leave blank if uncertain.
- For Number fields, return only digits (no units or symbols).
- For Date fields, return ISO format: YYYY-MM-DD.
- For Dropdown fields, pick the closest matching option from the options list.
- For Checkbox fields, return "True" or "False".
- Return ONLY the JSON object, no other text, no markdown fences.
"""


def try_model(client, model: str, content: list) -> dict | None:
    """Try a single model. Returns parsed dict on success, None on any failure."""
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": content}],
        )

        # Validate response structure
        if (
            not response
            or not response.choices
            or not response.choices[0].message
            or not response.choices[0].message.content
        ):
            return None

        raw = response.choices[0].message.content.strip()
        if not raw:
            return None

        # Strip markdown fences
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        return json.loads(raw)

    except (json.JSONDecodeError, Exception):
        return None


def extract_fields_from_document(fields: list, file_bytes: bytes, file_type: str) -> dict:
    client = get_client()
    prompt = build_extraction_prompt(fields)
    content = []

    if file_type == "pdf":
        pages = pdf_to_base64_images(file_bytes)
        if not pages:
            raise RuntimeError("PDF appears to be empty.")
        for b64_img in pages:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64_img}", "detail": "high"}
            })
    else:
        b64 = base64.standard_b64encode(file_bytes).decode("utf-8")
        magic = file_bytes[:4]
        mime = "image/jpeg" if magic[:3] == b'\xff\xd8\xff' else "image/png"
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"}
        })

    content.append({"type": "text", "text": prompt})

    FREE_VISION_MODELS = [
        "google/gemma-4-31b-it:free",
        "meta-llama/llama-4-maverick:free",
        "nvidia/nemotron-nano-vl-8b-v1:free",
        "openrouter/free",
    ]

    for model in FREE_VISION_MODELS:
        result = try_model(client, model, content)
        if result is not None:
            return result

    # All models failed — return blank results instead of crashing
    return {f["id"]: {"value": "", "confidence": "missing"} for f in fields}
