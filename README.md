
# 📄 ATS Resume Expert

**ATS Resume Expert** is an AI-powered web app built with Python and Streamlit that helps you optimize your resume for Applicant Tracking Systems (ATS). Upload your PDF resume and a job description to get instant feedback on:

- **Resume Fit**: General assessment of how well your resume matches the role  
- **Skill Gap Analysis**: Skills found vs. skills required  
- **Improvement Tips**: Actionable suggestions for formatting, keywords, and content  
- **ATS Match Score**: Percentage score plus keywords found/missing  

---

## 🚀 Tech Stack

- **Python 3.8+**  
- [Streamlit](https://streamlit.io/) for UI  
- [Google Gemini API](https://developers.generativeai.google/) for AI analysis  
- **PDF Processing**: `pdf2image` (with Poppler) or `PyPDF2` fallback  
- Environment management: `python-dotenv`

---

## 🔧 Prerequisites

1. **Python 3.8+**  
2. **Google API Key** (set as `GOOGLE_API_KEY`)  
3. **Poppler** (optional, for PDF→image conversion)  
   - **Windows**: Download from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) and add `…/poppler/bin` to your PATH  
   - **macOS**: `brew install poppler`  
   - **Ubuntu/Debian**: `sudo apt-get install poppler-utils`  

---

## ⚙️ Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/naakaarafr/ATS-Resume-Expert.git
   cd ATS-Resume-Expert


2. **Create & activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Google API key**

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

---

## ▶️ Usage

```bash
streamlit run app.py
```

1. Open the link shown in your browser.
2. Paste the target **Job Description**.
3. Upload your **Resume PDF**.
4. Choose one of the four analysis tabs and click the button to get instant AI feedback.

---

## 🛠️ Configuration

* **MODEL** environment variable to change the Gemini model (default: `gemini-2.0-flash`).
* Toggle debug logs by setting `show_debug = True` in `app.py`.

---

## 📁 File Structure

```
├── app.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/xyz`)
3. Commit your changes (`git commit -m "Add xyz"`)
4. Push to the branch (`git push origin feature/xyz`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

