# 📘 FlashQuiz+ - AI-Powered Instant Quiz Generator

A hackathon-ready Streamlit application that transforms study documents into interactive quizzes using OpenAI. Designed for **minimal API usage** and **maximum learning efficiency**.

---

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Format Document Support**: Upload PDF, DOCX, or TXT files
- **Smart Text Extraction**: Automatic text extraction and cleaning (no AI used)
- **AI-Powered Quiz Generation**: High-quality MCQs generated using OpenAI
- **Interactive Quiz Interface**: Clean, student-friendly UI with radio buttons
- **Instant Scoring & Feedback**: Real-time results with detailed explanations
- **Weak Area Identification**: Highlights questions you got wrong with correct answers

### 💰 Cost-Optimized Design
- **AI used ONLY for MCQ generation** - not for text extraction or scoring
- **Batched API calls** with progress tracking
- **GPT-3.5-turbo** for cost efficiency
- **Token limits** to minimize API costs (~300 tokens per question)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone or download this repository**
   ```bash
   cd FlashQuizPlus
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key** (choose one method):
   
   **Option A: Environment Variable (Recommended)**
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="your_api_key_here"
   
   # Windows CMD
   set OPENAI_API_KEY=your_api_key_here
   
   # Linux/Mac
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   **Option B: .env File**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```
   
   **Option C: In-App Input**
   - Just run the app and enter your API key in the sidebar

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**
   - The app will automatically open at `http://localhost:8501`

---

## 📖 How to Use

### Step 1: Upload Document
- Click "Browse files" or drag-and-drop
- Supported formats: PDF, DOCX, TXT
- Examples: lecture slides, study notes, textbook chapters

### Step 2: Review Learning Points
- App extracts and cleans text automatically
- View extracted "learning points" (sentences)
- No AI used in this step - pure text processing

### Step 3: Generate Quiz
- Configure number of questions (3-15)
- Click "Generate AI Quiz"
- AI creates MCQs with 4 options each
- Progress bar shows generation status

### Step 4: Take Quiz
- Answer all questions using radio buttons
- Each question has 4 options (1 correct + 3 distractors)
- Take your time - no timer

### Step 5: Submit & Review
- Click "Submit Quiz" when ready
- See your score, percentage, and performance feedback
- Review wrong answers with explanations
- Option to start a new quiz

---

## 🏗️ Project Structure

```
FlashQuizPlus/
│
├── app.py                 # Main application (complete, runnable)
├── requirements.txt       # Python dependencies
├── .env.example          # API key template
├── README.md             # This file
│
└── (generated at runtime)
    └── .streamlit/       # Streamlit config (optional)
```

---

## 🛠️ Technical Details

### Architecture
```
User Uploads File
    ↓
Text Extraction (PyPDF2/python-docx) - NO AI
    ↓
Text Cleaning & Splitting - NO AI
    ↓
AI MCQ Generation (OpenAI API) - ONLY AI STEP
    ↓
Quiz Display (Streamlit) - NO AI
    ↓
Scoring & Feedback - NO AI
```

### API Usage Breakdown
- **Text Extraction**: Manual (0 API calls)
- **Text Cleaning**: Rule-based (0 API calls)
- **MCQ Generation**: ~1 API call per question
- **Scoring**: Manual calculation (0 API calls)

**Example**: 5-question quiz = ~5 API calls (~$0.01-0.02 total cost)

### Key Technologies
| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend/UI | Streamlit | Interactive web interface |
| PDF Processing | PyPDF2 | Extract text from PDFs |
| DOCX Processing | python-docx | Extract text from Word docs |
| AI Generation | OpenAI (GPT-3.5) | Generate high-quality MCQs |
| State Management | Streamlit Session State | Track quiz progress |

---

## 📝 Code Highlights

### Well-Structured & Commented
```python
# Every function has clear docstrings
def extract_text_from_pdf(file):
    """
    Extract text from PDF file using PyPDF2.
    Manual extraction - no AI used.
    """
    # Implementation with error handling
```

### Session State Management
```python
# Tracks quiz state across reruns
st.session_state.quiz_generated
st.session_state.mcqs
st.session_state.user_answers
```

### Error Handling
- Invalid file formats
- API failures with graceful fallback
- JSON parsing errors
- Missing API keys

---

## 🎓 Use Cases

### For Students
- **Pre-Exam Practice**: Test yourself on lecture notes
- **Active Learning**: Convert passive reading into active recall
- **Weak Area Identification**: Focus study time on gaps

### For Educators
- **Quick Quiz Creation**: Generate quizzes from teaching materials
- **Student Assessment**: Create custom quizzes for any topic
- **Flipped Classroom**: Assign quiz generation as homework

### For Hackathons
- **Demo-Ready**: Works out of the box with minimal setup
- **Extensible**: Easy to add features (timer, leaderboard, etc.)
- **Well-Documented**: Clear code structure for team collaboration

---

## 🔧 Customization Options

### Adjust Quiz Settings
```python
# In sidebar (app.py, line ~445)
num_questions = st.slider(
    "Number of Questions",
    min_value=3,
    max_value=15,  # Increase for more questions
    value=5
)
```

### Change AI Model
```python
# In generate_mcq_with_ai() (app.py, line ~232)
model="gpt-3.5-turbo",  # Change to "gpt-4" for better quality
```

### Modify Text Cleaning
```python
# In clean_and_split_text() (app.py, line ~159)
def clean_and_split_text(text, min_length=30, max_length=300):
    # Adjust min_length and max_length as needed
```

---

## 🐛 Troubleshooting

### Issue: "OpenAI API Key not found"
**Solution**: Set environment variable or enter key in sidebar

### Issue: "Failed to generate quiz"
**Solutions**:
- Check API key validity
- Verify internet connection
- Ensure you have OpenAI API credits
- Check OpenAI service status

### Issue: "No valid learning points found"
**Solutions**:
- Use a document with more text content
- Reduce `min_length` in `clean_and_split_text()`
- Check if document has extractable text (not scanned image)

### Issue: App runs slowly
**Solutions**:
- Reduce number of questions
- Use smaller documents
- Check internet speed (API calls require connectivity)

---

## 💡 Tips for Best Results

### Document Quality
✅ **Good**: Well-formatted PDFs with clear paragraphs  
✅ **Good**: Lecture notes with complete sentences  
❌ **Avoid**: Scanned images (text not extractable)  
❌ **Avoid**: Documents with mostly tables/charts  

### Number of Questions
- **3-5 questions**: Quick review (< 30 seconds)
- **5-10 questions**: Standard practice (1-2 minutes)
- **10-15 questions**: Comprehensive test (2-3 minutes)

### API Cost Management
- Start with 3-5 questions while testing
- Use GPT-3.5-turbo (not GPT-4) for cost efficiency
- Monitor usage at [OpenAI Platform](https://platform.openai.com/usage)

---

## 🚧 Future Enhancements (Ideas for Hackathons)

### Features to Add
- [ ] **Timer**: Add countdown for timed quizzes
- [ ] **Difficulty Levels**: Easy/Medium/Hard questions
- [ ] **Topic Extraction**: Categorize questions by topic
- [ ] **Export Results**: Download quiz results as PDF
- [ ] **Multi-User**: Leaderboard and user accounts
- [ ] **Question Bank**: Save generated questions for reuse
- [ ] **Spaced Repetition**: Smart review scheduling
- [ ] **Dark Mode**: UI theme options

### Advanced Features
- [ ] **Voice Questions**: Text-to-speech for accessibility
- [ ] **Image Support**: Generate questions from diagrams
- [ ] **Collaborative**: Share quizzes with classmates
- [ ] **Analytics**: Track learning progress over time

---

## 📄 License

This project is open source and available for educational purposes.

---

## 🤝 Contributing

Feel free to fork, modify, and improve! Suggested improvements:
- Better text extraction algorithms
- Support for more file formats (PPT, HTML, etc.)
- Enhanced UI/UX design
- Multi-language support

---

## 👨‍💻 Author

Built for hackathons and educational projects.

**Need help?** Check the code comments - every function is documented!

---

## 📞 Support

### For Technical Issues
1. Check the Troubleshooting section above
2. Review error messages in the app
3. Verify all dependencies are installed

### For API Issues
- [OpenAI Documentation](https://platform.openai.com/docs)
- [OpenAI Community Forum](https://community.openai.com)

---

## 🎉 Acknowledgments

- **Streamlit** - For the amazing UI framework
- **OpenAI** - For powerful AI capabilities
- **PyPDF2 & python-docx** - For document processing

---

**Happy Learning! 📚✨**

Transform your study materials into interactive quizzes in seconds!
