# FormAI — AI-Powered Form Builder & Document Autofill

> **Tecnots AI Engineer Internship Assessment — Question 1**

Build forms from scratch, upload a document, and let AI extract and fill your form automatically.

LINK-https://ai-powered-form-builder-and-document-autofill-ldydslc3jhyz7azl.streamlit.app

---

## ✨ Features

- **Dynamic Form Builder** — add, label, type, reorder, and remove fields at runtime
- **Field Types** — single-line text, multi-line text, number, date, dropdown, checkbox
- **Required / Optional** toggle per field
- **Live Preview** — see your form render in real time as you build it
- **Document Upload** — PDF, PNG, JPG, JPEG (up to 10 MB)
- **AI Extraction** — Claude reads the document and fills every field based on your schema
- **Confidence Indicators** — High / Medium / Low / Not found per field
- **Review & Edit** — manually fix any extracted value before saving
- **Required Field Highlighting** — orange border on unfilled required fields
- **Export / Import Form Schema** — save and reload your form structure as JSON
- **Export Filled Form** — download the completed form as JSON
- **Edge case handling** — corrupted files, missing values, unsupported types, empty submissions

---

## 🗂 Project Structure

```
form_builder/
├── app.py                  # Main Streamlit app + routing
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Dark theme configuration
└── utils/
    ├── __init__.py
    ├── form_utils.py       # Field management, builder UI, preview, review
    ├── upload_utils.py     # File upload, validation, preview
    └── ai_utils.py         # Anthropic API call, prompt construction, parsing
```

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd form_builder
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # macOS / Linux
set ANTHROPIC_API_KEY=sk-ant-...        # Windows CMD
$env:ANTHROPIC_API_KEY="sk-ant-..."     # Windows PowerShell
```

> Get your key at https://console.anthropic.com

### 5. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

The simplest zero-cost deployment option.

### Steps

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/<your-username>/form-ai.git
   git push -u origin main
   ```

2. **Go to** https://share.streamlit.io and sign in with GitHub.

3. **Click "New app"** → select your repository, branch (`main`), and set the main file to `app.py`.

4. **Add your secret** under *Advanced settings → Secrets*:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

5. **Click Deploy.** Streamlit handles everything else.

6. You'll get a public URL like `https://your-app.streamlit.app`.

---

## ☁️ Deploy to Railway (Recommended for Production)

### Steps

1. Install the Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Create a new project: `railway init`
4. Add a `Procfile`:
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
5. Set environment variable in Railway dashboard:
   - `ANTHROPIC_API_KEY` = your key
6. Deploy:
   ```bash
   railway up
   ```

---

## ☁️ Deploy to Render

1. Create a new **Web Service** on https://render.com
2. Connect your GitHub repo
3. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Add environment variable: `ANTHROPIC_API_KEY`
5. Deploy.

---

## ☁️ Deploy to AWS / GCP / Azure (Docker)

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and push to any container registry, then run on any cloud VM or managed container service.

---

## 🧠 Technology Choices

| Technology | Why |
|---|---|
| **Python** | Rapid prototyping, rich ecosystem for AI/ML tasks |
| **Streamlit** | Instant interactive UI with no frontend code; built-in widgets cover all field types |
| **Anthropic Claude (claude-sonnet-4-6)** | Best-in-class document understanding, supports PDF and image natively via the Messages API; structured JSON output is reliable |
| **`anthropic` SDK** | Official, well-maintained, handles auth and retries |
| **Base64 encoding** | Required for sending binary files to the Claude API |

---

## ⚖️ Assumptions & Trade-offs

- **No persistent database** — form schemas and results live in Streamlit session state; for multi-user production use, add a backend (Supabase, SQLite, Postgres).
- **Synchronous extraction** — the AI call blocks until complete; for very large PDFs consider streaming or async via `asyncio`.
- **Single document per session** — uploading a new file clears the previous extraction.
- **Dropdown matching** — the AI picks the closest matching option; edge cases with unusual values default to the first option.
- **No auth** — authentication is out of scope for this assessment.
- **Max file size 10 MB** — large PDFs should be compressed before upload.

---

## 📸 Screenshots

> Add screenshots of each step here after running the app.

---

## 📄 License

For assessment purposes only — Tecnots AI Engineer Internship 2025.
