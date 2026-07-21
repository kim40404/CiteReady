# CiteReady 🚀
**Enterprise AI Search Visibility & Semantic Scorer**

![CiteReady Dashboard](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/FastAPI-Next.js-blue?style=for-the-badge&logo=next.js)
![AI](https://img.shields.io/badge/Ollama-Llama_3.1-purple?style=for-the-badge)

## 📖 What is CiteReady?
In the modern era, traditional keyword-based SEO is becoming obsolete. Internet users now seek direct answers through AI search engines like **ChatGPT, Perplexity, and Google AI Overviews**.

**CiteReady** is a B2B SaaS application designed to score **GEO (Generative Engine Optimization)**. It acts as an intelligent auditor that reads your website's content exactly like an AI would. Its primary goal is to tell you specifically **"what to fix so your content gets cited and used as a primary reference source by AI Search Engines."**

## ✨ Key Features
1. **Technical SEO Scoring:** Analyzes HTML structure (H1, Meta Tags, Schema JSON-LD) to ensure search engines can easily crawl and index the content.
2. **AI Semantic Analysis:** Utilizes **Llama 3.1 (Local via Ollama)** to read the content and evaluate 3 core pillars:
   - *Authority* (Expert Credibility)
   - *Fact Density* (Richness of Data & Facts)
   - *Clarity* (Directness of the Answer)
3. **Priority Fixes & AI Insights:** Generates an instant "Report Card" filled with constructive feedback and actionable steps writers must take to improve their GEO score.
4. **Modern Solid UI:** A highly performant, clean, and accessibility-focused dashboard (*High-Contrast Dark Mode*).

## 🛠️ Technology Stack (Full-Stack)
This application is built on an Enterprise Two-Tier Architecture:

- **Backend (Python):** 
  - `FastAPI` (High-Performance REST API)
  - `SQLAlchemy` + `SQLite` (Audit Trail Database)
  - `LiteLLM` + `Tenacity` (Resilient LLM connection with timeout safety)
- **Frontend (TypeScript):**
  - `Next.js 15` (App Router)
  - `Tailwind CSS v4` + `shadcn/ui` (UI Design System)
  - `Recharts` (Data Score Visualization)
- **AI Engine (100% Local & Private):**
  - `Ollama` running the **Llama 3.1** model locally without external API costs ($0 Cost).

---

## 🚀 How to Run the Project Locally

Because this is a Full-Stack system with a Local AI, you need to run 3 components in parallel (each in a separate terminal).

### Phase 1: Run the AI Engine (Ollama)
Ensure you have installed [Ollama](https://ollama.com/) on your machine.
1. Open a new terminal and run the Ollama server (if it isn't already running in the background).
2. Ensure the Llama 3.1 model is downloaded:
   ```bash
   ollama pull llama3.1
   ```

### Phase 2: Run the Backend API (FastAPI)
Open a new terminal, navigate to the main `citeready` folder, and run:
```bash
# 1. Activate Virtual Environment (Windows)
.venv\Scripts\activate

# 2. Install dependencies (If not already installed)
pip install -r requirements.txt

# 3. Run the server on port 8000
python -m uvicorn app.main:app --reload --port 8000
```
*The API is now running at `http://localhost:8000`*

### Phase 3: Run the Frontend UI (Next.js)
Open a new terminal, navigate into the `citeready/frontend` folder, and run:
```bash
# 1. Enter the frontend directory
cd frontend

# 2. Install Node.js dependencies
npm install

# 3. Run the web server
npm run dev
```
*The Web Dashboard is now running at `http://localhost:3000`*

---

## 🌍 Production Deployment

CiteReady is engineered for a decoupled containerized deployment. While Local Development relies on Ollama for cost-free testing, **Production should utilize a Cloud AI Provider (like OpenAI or Anthropic)** via the LiteLLM proxy for maximum stability and speed.

### Phase 1: Deploy Backend to Google Cloud Run
The backend includes a `Dockerfile` ready for Google Cloud Run.
1. Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
2. Authenticate and configure your project:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. Deploy the container:
   ```bash
   gcloud run deploy citeready-api --source . --port 8080 --allow-unauthenticated
   ```
4. In the Cloud Run Console, set these **Environment Variables**:
   ```env
   FRONTEND_CORS_ORIGINS=https://citeready.yourdomain.com
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4o-mini
   LLM_API_KEY=sk-proj-your-api-key
   LLM_TIMEOUT=15
   ```
   *Note: If the AI provider fails or rate-limits, the API will gracefully fall back to returning baseline technical SEO scores so your UI does not crash.*

### Phase 2: Deploy Frontend to Vercel
1. Push this repository to GitHub.
2. Log into [Vercel](https://vercel.com/) and click **Add New -> Project**.
3. Import your GitHub repository.
4. Set the **Framework Preset** to `Next.js`.
5. Set the **Root Directory** to `frontend`.
6. Add the following **Environment Variable**:
   ```env
   NEXT_PUBLIC_API_URL=https://citeready-api-xyz.a.run.app  # (Your Cloud Run URL)
   ```
7. Click **Deploy**.

---

## 💡 Workflow Usage
1. Open your browser and visit `http://localhost:3000`.
2. Enter the URL of the website or blog post you want to test (e.g., `https://example.com`).
3. Click the **Analyze Content** button.
4. Wait a few seconds while FastAPI scrapes the content and Llama 3.1 performs the semantic dissection.
5. Receive your final **Blended GEO Score** along with priority fix recommendation cards!

---

### Connect with Me
- **GitHub:** [kim40404](https://github.com/kim40404)
- **LinkedIn:** [Kimsang Silalahi](https://www.linkedin.com/in/kimsang-silalahi-3a8b13308/)
- **Hugging Face:** [Kimsang Silalahi](https://huggingface.co/Kimsang766)
