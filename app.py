"""
FlashQuiz+ - Instant Document-to-Quiz Platform
A Streamlit application that converts study documents into interactive quizzes using AI.
Optimized for minimal OpenAI API usage.
"""

import streamlit as st
from PyPDF2 import PdfReader
import docx
import json
import os
from openai import OpenAI
import random
import os
from dotenv import load_dotenv
load_dotenv()

# ========================================
# PAGE CONFIGURATION
# ========================================

st.set_page_config(
    page_title="FlashQuiz+ | AI-Powered Quiz Generator",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ========================================
# INITIALIZE SESSION STATE
# ========================================

if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False
if 'mcqs' not in st.session_state:
    st.session_state.mcqs = []
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'sentences' not in st.session_state:
    st.session_state.sentences = []

# ========================================
# OPENAI API CONFIGURATION
# ========================================

def get_openai_client():
    """
    Initialize OpenAI client with API key from environment variable or user input.
    Returns OpenAI client or None if not configured.
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.sidebar.warning("⚠️ OpenAI API Key not found")
        api_key = st.sidebar.text_input(
            "Enter your OpenAI API Key",
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys"
        ) 
    
    if api_key:
        try:
            client = OpenAI(api_key=api_key)  # FIXED: Pass as variable, not literal
            st.sidebar.success("✅ API Key configured")
            return client
        except Exception as e:
            st.sidebar.error(f"❌ API Key error: {str(e)}")
            return None
    return None
# ========================================
# TEXT EXTRACTION FUNCTIONS (NO AI)
# ========================================

def extract_text_from_pdf(file):
    """
    Extract text from PDF file using PyPDF2.
    Manual extraction - no AI used.
    """
    text = ""
    try:
        pdf = PdfReader(file)
        total_pages = len(pdf.pages)
        
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        return text, total_pages
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return "", 0

def extract_text_from_docx(file):
    """
    Extract text from DOCX file using python-docx.
    Manual extraction - no AI used.
    """
    text = ""
    try:
        doc = docx.Document(file)
        para_count = 0
        
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
                para_count += 1
        
        return text, para_count
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return "", 0

def extract_text_from_txt(file):
    """
    Extract text from TXT file.
    Manual extraction - no AI used.
    """
    try:
        text = file.read().decode("utf-8")
        line_count = len([line for line in text.split("\n") if line.strip()])
        return text, line_count
    except Exception as e:
        st.error(f"Error reading TXT: {str(e)}")
        return "", 0

def extract_text(file):
    """
    Main text extraction function that handles all file types.
    Routes to appropriate extraction function based on file type.
    """
    file_type = file.type
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    elif file_type == "text/plain":
        return extract_text_from_txt(file)
    else:
        st.error(f"Unsupported file type: {file_type}")
        return "", 0

# ========================================
# TEXT CLEANING FUNCTIONS (NO AI)
# ========================================

def clean_and_split_text(text, min_length=30, max_length=300):
    """
    Clean extracted text and split into meaningful sentences.
    Manual processing - no AI used.
    
    Args:
        text: Raw extracted text
        min_length: Minimum sentence length to keep
        max_length: Maximum sentence length to keep
    
    Returns:
        List of cleaned sentences
    """
    # Split by newlines and periods
    lines = text.replace(". ", ".\n").split("\n")
    
    cleaned_sentences = []
    
    for line in lines:
        # Strip whitespace
        line = line.strip()
        
        # Remove empty lines and very short lines
        if len(line) < min_length:
            continue
        
        # Skip lines that are likely headers/footers (all caps, too short, etc.)
        if line.isupper() and len(line) < 50:
            continue
        
        # Skip lines with too many special characters
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in line) / len(line)
        if special_char_ratio > 0.3:
            continue
        
        # Truncate very long sentences
        if len(line) > max_length:
            line = line[:max_length] + "..."
        
        cleaned_sentences.append(line)
    
    return cleaned_sentences

# ========================================
# AI-POWERED MCQ GENERATION (OPENAI API)
# ========================================

def generate_mcq_with_ai(client, learning_point, temperature=0.7):
    """
    Generate a single MCQ from a learning point using OpenAI API.
    This is the ONLY function that uses AI.
    
    Args:
        client: OpenAI client instance
        learning_point: Text content to generate MCQ from
        temperature: Creativity level (0-1)
    
    Returns:
        Dictionary with question, options, and correct answer
        or None if generation fails
    """
    try:
        prompt = f"""You are an expert quiz creator. Generate ONE multiple-choice question based on the following text:

"{learning_point}"

Return ONLY valid JSON in this exact format (no other text):
{{
    "question": "Your question here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Brief explanation of why this is correct"
}}

Rules:
- Question must test understanding of the key concept
- All 4 options must be plausible
- Only ONE option is correct
- Options should be concise (under 100 characters each)
- The correct_answer must exactly match one of the options"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-40-mini for cost efficiency
            messages=[
                {"role": "system", "content": "You are a helpful quiz generator that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=300  # Limit tokens for cost efficiency
        )
        
        # Extract and parse JSON response
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        mcq = json.loads(content.strip())
        
        # Validate structure
        required_keys = ["question", "options", "correct_answer"]
        if all(key in mcq for key in required_keys):
            if len(mcq["options"]) == 4:
                if mcq["correct_answer"] in mcq["options"]:
                    return mcq
        
        st.warning("Generated MCQ did not match expected format")
        return None
        
    except json.JSONDecodeError as e:
        st.warning(f"Failed to parse AI response as JSON: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error generating MCQ: {str(e)}")
        return None

def generate_quiz_batch(client, sentences, num_questions=5):
    """
    Generate multiple MCQs from sentences with progress tracking.
    Batches API calls efficiently.
    
    Args:
        client: OpenAI client
        sentences: List of learning points
        num_questions: Number of questions to generate
    
    Returns:
        List of MCQ dictionaries
    """
    mcqs = []
    
    # Select random sentences for variety
    selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))
    
    # Progress bar for API calls
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, sentence in enumerate(selected_sentences):
        status_text.text(f"Generating question {i+1}/{len(selected_sentences)}...")
        
        mcq = generate_mcq_with_ai(client, sentence)
        
        if mcq:
            mcqs.append(mcq)
        
        # Update progress
        progress_bar.progress((i + 1) / len(selected_sentences))
    
    progress_bar.empty()
    status_text.empty()
    
    return mcqs

# ========================================
# QUIZ UI COMPONENTS
# ========================================

def display_quiz(mcqs):
    """
    Display quiz questions with radio buttons for answers.
    """
    st.subheader("📝 Quiz Time!")
    st.write(f"Answer all {len(mcqs)} questions and submit to see your score.")
    
    st.markdown("---")
    
    for i, mcq in enumerate(mcqs):
        st.markdown(f"### Question {i+1}")
        st.write(mcq['question'])
        
        # Radio button for answer selection
        answer = st.radio(
            "Choose your answer:",
            mcq['options'],
            key=f"q_{i}",
            index=None  # No default selection
        )
        
        # Store answer in session state
        st.session_state.user_answers[i] = answer
        
        st.markdown("---")

def calculate_score(mcqs, user_answers):
    """
    Calculate quiz score and identify weak areas.
    Manual calculation - no AI used.
    
    Returns:
        Dictionary with score details
    """
    correct_count = 0
    wrong_questions = []
    
    for i, mcq in enumerate(mcqs):
        user_answer = user_answers.get(i)
        correct_answer = mcq['correct_answer']
        
        if user_answer == correct_answer:
            correct_count += 1
        else:
            wrong_questions.append({
                'question_num': i + 1,
                'question': mcq['question'],
                'user_answer': user_answer if user_answer else "Not answered",
                'correct_answer': correct_answer,
                'explanation': mcq.get('explanation', 'N/A')
            })
    
    total_questions = len(mcqs)
    wrong_count = total_questions - correct_count
    percentage = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    return {
        'total': total_questions,
        'correct': correct_count,
        'wrong': wrong_count,
        'percentage': percentage,
        'wrong_questions': wrong_questions
    }

def display_results(score_data):
    """
    Display quiz results with detailed feedback.
    """
    st.balloons()
    
    st.subheader("🎯 Quiz Results")
    
    # Score summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Questions", score_data['total'])
    with col2:
        st.metric("Correct ✅", score_data['correct'])
    with col3:
        st.metric("Wrong ❌", score_data['wrong'])
    
    # Percentage score with progress bar
    st.markdown("### Your Score")
    st.progress(score_data['percentage'] / 100)
    st.markdown(f"## {score_data['percentage']}%")
    
    # Performance feedback
    if score_data['percentage'] >= 80:
        st.success("🎉 Excellent! You've mastered this material!")
    elif score_data['percentage'] >= 60:
        st.info("👍 Good job! A bit more practice will make you perfect!")
    else:
        st.warning("📚 Keep studying! Review the weak areas below.")
    
    # Weak areas / review
    if score_data['wrong_questions']:
        st.markdown("---")
        st.subheader("📌 Review Your Mistakes")
        st.write("Learn from these questions to improve your understanding:")
        
        for wrong in score_data['wrong_questions']:
            with st.expander(f"❌ Question {wrong['question_num']}: {wrong['question'][:80]}..."):
                st.write(f"**Question:** {wrong['question']}")
                st.write(f"**Your Answer:** {wrong['user_answer']}")
                st.write(f"**Correct Answer:** ✅ {wrong['correct_answer']}")
                if wrong['explanation'] != 'N/A':
                    st.info(f"**Explanation:** {wrong['explanation']}")
    else:
        st.success("🌟 Perfect score! You didn't miss any questions!")

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    # Header
    st.title("📘 FlashQuiz+")
    st.markdown("### AI-Powered Instant Quiz Generator")
    st.write("Upload your study documents and test your knowledge with AI-generated quizzes!")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API setup
        client = get_openai_client()
        
        st.markdown("---")
        
        # Quiz settings
        st.header("📊 Quiz Settings")
        num_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=15,
            value=5,
            help="More questions = more API calls"
        )
        
        st.info(f"💡 This will make ~{num_questions} API calls")
        
        st.markdown("---")
        
        # Instructions
        with st.expander("📖 How to Use"):
            st.markdown("""
            1. **Upload** a PDF, DOCX, or TXT file
            2. **Review** extracted learning points
            3. **Generate** AI-powered quiz
            4. **Answer** all questions
            5. **Submit** to see results and feedback
            """)
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **FlashQuiz+** uses:
            - Manual text extraction (PyPDF2, python-docx)
            - AI for MCQ generation only
            - Minimal API usage for cost efficiency
            
            Built for hackathons with ❤️
            """)
    
    # Main content area
    st.markdown("---")
    
    # Step 1: File Upload
    st.header("1️⃣ Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        help="Upload your study notes, lecture slides, or any educational document"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        
        # Extract text
        with st.spinner("📄 Extracting text from document..."):
            text, count = extract_text(uploaded_file)
            st.session_state.extracted_text = text
        
        if text:
            st.info(f"📊 Extracted content from {count} pages/paragraphs/lines")
            
            # Clean and split text
            with st.spinner("🧹 Processing and cleaning text..."):
                sentences = clean_and_split_text(text)
                st.session_state.sentences = sentences
            
            if sentences:
                st.success(f"✅ Found **{len(sentences)}** learning points")
                
                # Step 2: Preview Learning Points
                st.markdown("---")
                st.header("2️⃣ Preview Learning Points")
                
                with st.expander(f"View all {len(sentences)} learning points"):
                    for i, sentence in enumerate(sentences[:20], 1):  # Show first 20
                        st.write(f"{i}. {sentence}")
                    if len(sentences) > 20:
                        st.info(f"... and {len(sentences) - 20} more")
                
                # Step 3: Generate Quiz
                st.markdown("---")
                st.header("3️⃣ Generate Quiz")
                
                if not client:
                    st.error("⚠️ Please configure OpenAI API key in the sidebar to generate quiz")
                else:
                    if st.button("🚀 Generate AI Quiz", type="primary"):
                        if len(sentences) < num_questions:
                            st.warning(f"Only {len(sentences)} learning points found. Generating {len(sentences)} questions.")
                            actual_questions = len(sentences)
                        else:
                            actual_questions = num_questions
                        
                        with st.spinner(f"🤖 Generating {actual_questions} questions using AI..."):
                            mcqs = generate_quiz_batch(client, sentences, actual_questions)
                            
                            if mcqs:
                                st.session_state.mcqs = mcqs
                                st.session_state.quiz_generated = True
                                st.session_state.quiz_submitted = False
                                st.session_state.user_answers = {}
                                st.success(f"✅ Generated {len(mcqs)} questions!")
                            else:
                                st.error("Failed to generate quiz. Please try again.")
                
                # Step 4: Take Quiz
                if st.session_state.quiz_generated and st.session_state.mcqs:
                    st.markdown("---")
                    st.header("4️⃣ Take Quiz")
                    
                    display_quiz(st.session_state.mcqs)
                    
                    # Submit button
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("📤 Submit Quiz", type="primary", use_container_width=True):
                            # Check if all questions are answered
                            unanswered = []
                            for i in range(len(st.session_state.mcqs)):
                                if i not in st.session_state.user_answers or st.session_state.user_answers[i] is None:
                                    unanswered.append(i + 1)
                            
                            if unanswered:
                                st.warning(f"⚠️ Please answer all questions. Missing: {', '.join(map(str, unanswered))}")
                            else:
                                st.session_state.quiz_submitted = True
                                st.rerun()
                
                # Step 5: Show Results
                if st.session_state.quiz_submitted:
                    st.markdown("---")
                    st.header("5️⃣ Results & Feedback")
                    
                    score_data = calculate_score(st.session_state.mcqs, st.session_state.user_answers)
                    display_results(score_data)
                    
                    # Reset button
                    st.markdown("---")
                    if st.button("🔄 Start New Quiz", type="secondary"):
                        st.session_state.quiz_generated = False
                        st.session_state.mcqs = []
                        st.session_state.user_answers = {}
                        st.session_state.quiz_submitted = False
                        st.rerun()
            else:
                st.error("❌ No valid learning points found in the document. Please try a different file.")
        else:
            st.error("❌ Failed to extract text from the document. Please check the file format.")
    else:
        # Welcome message when no file uploaded
        st.info("👆 Please upload a document to get started!")
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📄 Multi-Format")
            st.write("Supports PDF, DOCX, and TXT files")
        
        with col2:
            st.markdown("### 🤖 AI-Powered")
            st.write("Smart MCQs using OpenAI")
        
        with col3:
            st.markdown("### 💰 Cost-Efficient")
            st.write("Minimal API usage")

# ========================================
# RUN APPLICATION
# ========================================

if __name__ == "__main__":
    main()




