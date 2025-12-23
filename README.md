# 📘 FlashQuiz+ – Instant AI Quiz Generator

**FlashQuiz+** is a Streamlit app that turns your study documents (PDF, DOCX, TXT) into interactive quizzes using OpenAI’s GPT-4o-mini model. It’s optimized for minimal API usage and is perfect for students and educators.

---

## ✨ Features

- **Upload PDF, DOCX, or TXT** files
- **Automatic text extraction & cleaning** (no AI used)
- **AI-powered MCQ generation** (OpenAI GPT-4o-mini, 1 call per question)
- **Interactive quiz interface** with instant scoring and feedback
- **Review weak areas** with explanations

---

## 🚀 Setup & Usage

1. **Install dependencies:**
   ```bash
   pip install streamlit PyPDF2 python-docx openai python-dotenv
   ```

2. **Set your OpenAI API key:**
   - **Recommended:**  
     ```bash
     # Windows PowerShell
     $env:OPENAI_API_KEY="your_api_key_here"
     streamlit run app.py
     ```
   - Or, create a `.env` file with  
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - Or, enter your key in the app sidebar.

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser:**  
   Go to [http://localhost:8501](http://localhost:8501)

---

## 📝 How It Works

1. **Upload** your document.
2. **Review** extracted learning points.
3. **Generate** a quiz (choose number of questions).
4. **Take** the quiz and submit answers.
5. **See** your score and review mistakes.

---

## 🛠️ Tech Stack

- Python 3.x, Streamlit
- PyPDF2, python-docx
- OpenAI (GPT-4o-mini)
- No database required

---

**Happy learning!**
