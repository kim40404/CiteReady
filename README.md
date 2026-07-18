# CiteReady 🚀
**Enterprise AI Search Visibility & Semantic Scorer**

![CiteReady Dashboard](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/FastAPI-Next.js-blue?style=for-the-badge&logo=next.js)
![AI](https://img.shields.io/badge/Ollama-Llama_3.1-purple?style=for-the-badge)

## 📖 Apa itu CiteReady?
Di era modern, SEO tradisional (berbasis *keyword*) sudah mulai ditinggalkan. Pengguna internet kini mencari jawaban langsung melalui mesin pencari AI seperti **ChatGPT, Perplexity, dan Google AI Overviews**.

**CiteReady** adalah aplikasi SaaS B2B penilai **GEO (Generative Engine Optimization)**. Aplikasi ini bertindak sebagai auditor cerdas yang membaca konten *website* Anda layaknya sebuah mesin AI. Tujuannya adalah untuk memberi tahu Anda secara spesifik **"Apa yang harus diperbaiki agar konten Anda dikutip (cited) dan dijadikan sumber referensi utama oleh AI Search Engines."**

## ✨ Fitur Utama
1. **Technical SEO Scoring:** Membedah struktur HTML (H1, Meta Tags, Schema JSON-LD) untuk memastikan mesin pencari dapat mengindeks konten dengan mudah.
2. **AI Semantic Analysis:** Menggunakan **Llama 3.1 (Lokal via Ollama)** untuk membaca konten dan menilai 3 pilar utama:
   - *Authority* (Kredibilitas Pakar)
   - *Fact Density* (Kepadatan Data & Fakta)
   - *Clarity* (Kejelasan Jawaban)
3. **Priority Fixes & AI Insights:** Menghasilkan "Buku Rapot" instan berisi kritik konstruktif dan langkah perbaikan yang harus dilakukan penulis agar skor GEO mereka meningkat.
4. **Modern Solid UI:** Dashboard berkinerja tinggi, bersih, dan berfokus pada aksesibilitas (*High-Contrast Dark Mode*).

## 🛠️ Arsitektur Teknologi (Full-Stack)
Aplikasi ini dirancang dengan standar Enterprise *Two-Tier Architecture*:

- **Backend (Python):** 
  - `FastAPI` (REST API Berkecepatan Tinggi)
  - `SQLAlchemy` + `SQLite` (Audit Trail Database)
  - `LiteLLM` + `Tenacity` (Konektor LLM yang aman dari *timeout*)
- **Frontend (TypeScript):**
  - `Next.js 15` (App Router)
  - `Tailwind CSS v4` + `shadcn/ui` (Sistem Desain UI)
  - `Recharts` (Visualisasi Skor Data)
- **AI Engine (100% Local & Private):**
  - `Ollama` menjalankan model **Llama 3.1** secara lokal tanpa biaya API eksternal ($0 Cost).

---

## 🚀 Cara Menjalankan Project Secara Lokal

Karena ini adalah sistem *Full-Stack* dengan AI Lokal, Anda perlu menjalankan 3 komponen secara paralel (masing-masing di terminal yang terpisah).

### Tahap 1: Jalankan Mesin AI (Ollama)
Pastikan Anda telah menginstal [Ollama](https://ollama.com/) di komputer Anda.
1. Buka terminal baru dan jalankan server Ollama (jika belum berjalan di latar belakang).
2. Pastikan model Llama 3.1 sudah terunduh:
   ```bash
   ollama pull llama3.1
   ```

### Tahap 2: Jalankan API Backend (FastAPI)
Buka terminal baru, arahkan ke folder utama `citeready`, dan jalankan:
```bash
# 1. Aktifkan Virtual Environment (Windows)
.venv\Scripts\activate

# 2. Instal dependensi (Jika belum)
pip install -r requirements.txt

# 3. Jalankan server di port 8000
python -m uvicorn app.main:app --reload --port 8000
```
*API sekarang berjalan di `http://localhost:8000`*

### Tahap 3: Jalankan UI Frontend (Next.js)
Buka terminal baru, arahkan ke dalam folder `citeready/frontend`, dan jalankan:
```bash
# 1. Masuk ke folder frontend
cd frontend

# 2. Instal dependensi Node.js
npm install

# 3. Jalankan server web
npm run dev
```
*Dashboard Web sekarang berjalan di `http://localhost:3000`*

---

## 💡 Cara Penggunaan (Workflow)
1. Buka browser dan kunjungi `http://localhost:3000`.
2. Masukkan URL *website* atau *blog post* yang ingin diuji coba (contoh: `https://example.com`).
3. Tekan tombol **Analyze Content**.
4. Tunggu beberapa detik selagi FastAPI men-*scrape* konten dan Llama 3.1 melakukan pembedahan semantik.
5. Dapatkan skor **Blended GEO Score** akhir Anda beserta kartu rekomendasi perbaikan!

---
*Developed as part of Advanced Agentic Coding Architecture Portfolio.*
