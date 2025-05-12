import streamlit as st
import os
import io
from PIL import Image
import base64
import PyPDF2
import warnings
import google.generativeai as genai


# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try importing pdf2image, but provide fallback if not available/configured
try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

# Initialize Google Generative AI client
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Set model to use (from environment variable or default)
model_name = os.getenv("MODEL", "gemini-2.0-flash")

# Define show_debug at the beginning of the file
show_debug = False

# Configure Streamlit page
st.set_page_config(
    page_title="ATS Resume Expert",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #6C63FF;
        --primary-light: rgba(108, 99, 255, 0.1);
        --secondary-color: #4A4A8F;
        --bg-color: #0E1117;
        --card-bg: #1A1C24;
        --text-color: #F1F1F1;
        --text-secondary: #AFAFAF;
        --border-color: #2D2D3D;
        --success-color: #4CAF50;
        --warning-color: #FFC107;
        --error-color: #F44336;
    }
    
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header styles */
    .main-header {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 15px;
        text-align: center;
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }
    
    .subheader {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--text-color);
        margin-bottom: 25px;
        text-align: center;
        opacity: 0.9;
    }
    
    /* Card styles */
    .card {
        background-color: var(--card-bg);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
    }
    
    /* Input styles */
    div[data-testid="stFileUploader"] {
        padding: 20px;
        border: 2px dashed var(--primary-color);
        border-radius: 12px;
        margin-bottom: 20px;
        background-color: rgba(108, 99, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stFileUploader"]:hover {
        background-color: rgba(108, 99, 255, 0.08);
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2);
    }
    
    .stTextInput input, .stTextArea textarea {
        background-color: var(--card-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2);
    }
    
    /* Button styles */
    .stButton button {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 14px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(108, 99, 255, 0.4);
    }
    
    .stButton button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(108, 99, 255, 0.3);
    }
    
    /* Message styles */
    .chat-message {
        padding: 1.8rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        display: flex;
        animation: fadeIn 0.5s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message.user {
        background-color: #2D2F3A;
        color: var(--text-color);
    }
    
    .chat-message.assistant {
        background-color: #1E2030;
        border-left: 5px solid var(--primary-color);
        color: var(--text-color);
    }
    
    /* Status indicators */
    .status-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        animation: slideIn 0.3s ease-in-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-10px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .status-box.success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid var(--success-color);
    }
    
    .status-box.warning {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 4px solid var(--warning-color);
    }
    
    .status-box.error {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid var(--error-color);
    }
    
    .status-box.info {
        background-color: rgba(108, 99, 255, 0.1);
        border-left: 4px solid var(--primary-color);
    }
    
    /* Results section */
    .results-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--text-color);
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--primary-color);
    }
    
    .results-container {
        background-color: var(--card-bg);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-color);
        margin-top: 20px;
    }
    
    /* Footer styles */
    .footer {
        text-align: center;
        margin-top: 40px;
        padding: 20px;
        color: var(--text-secondary);
        font-size: 14px;
        border-top: 1px solid var(--border-color);
    }
    
    /* Sidebar styles */
    div[data-testid="stSidebarUserContent"] {
        background-color: var(--card-bg);
        padding: 20px;
    }
    
    div[data-testid="stSidebarUserContent"] .stExpander {
        background-color: rgba(108, 99, 255, 0.05);
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }
    
    /* Input labels */
    .stTextInput label, .stTextArea label, div[data-testid="stFileUploader"] label {
        color: var(--text-color);
        font-weight: 500;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    /* Section headers */
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        color: var(--text-color);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Progress bar */
    div[data-testid="stProgressBar"] {
        background-color: rgba(108, 99, 255, 0.2);
    }
    
    div[data-testid="stProgressBar"] > div {
        background-color: var(--primary-color);
    }
    
    /* Tab styling */
    button[data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px 10px 0 0;
        border: none;
        border-bottom: 2px solid transparent;
        padding: 10px 16px;
        margin-right: 2px;
        color: var(--text-secondary);
        transition: all 0.2s ease;
    }
    
    button[data-baseweb="tab"]:hover {
        background-color: rgba(108, 99, 255, 0.05);
        color: var(--text-color);
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(108, 99, 255, 0.1);
        border-bottom: 2px solid var(--primary-color);
        color: var(--primary-color);
        font-weight: 500;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: var(--card-bg);
        color: var(--text-color);
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-color);
        font-size: 14px;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loader {
        width: 100%;
        height: 4px;
        background-color: rgba(108, 99, 255, 0.2);
        overflow: hidden;
        position: relative;
    }
    
    .loader:before {
        content: "";
        position: absolute;
        height: 100%;
        width: 50%;
        background-color: var(--primary-color);
        animation: loading 1.5s infinite ease;
    }
    
    @keyframes loading {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(200%); }
    }
    
    /* Hide loader class for JavaScript manipulation */
    .hidden {
        display: none !important;
    }
    
    /* Responsive adjustments */
    @media screen and (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .subheader {
            font-size: 1.2rem;
        }
    }
    </style>
    
    <div class="main-header">ATS Resume Expert</div>
    <div class="subheader">Upload your resume and job description for AI-powered career insights</div>
    
    <!-- Loading indicator that can be controlled via session state -->
    <div id="loading-indicator" class="hidden">
        <div class="loader"></div>
        <p style="text-align: center; margin-top: 10px; color: var(--primary-color);">Processing your request...</p>
    </div>
    
    <script>
    // JavaScript to control the loading indicator
    function hideLoader() {
        document.getElementById('loading-indicator').classList.add('hidden');
    }
    
    function showLoader() {
        document.getElementById('loading-indicator').classList.remove('hidden');
    }
    </script>
    """, unsafe_allow_html=True)

# Initialize session state for managing loading state
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Create the main app UI with cards and sections
st.markdown('---', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Job Description</div>', unsafe_allow_html=True)
input_text = st.text_area("Paste the job description you're applying for:", 
                        placeholder="Enter the complete job description here...",
                        key="input", 
                        height=200)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('---', unsafe_allow_html=True)
st.markdown('<div class="section-title">📄 Your Resume</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your resume (PDF format):", type=["pdf"])

if uploaded_file is not None:
    
    st.write("✅ Resume uploaded successfully! Select an analysis option below.")
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

def input_pdf_setup(uploaded_file):
    """Convert PDF to images and prepare for API submission"""
    if uploaded_file is not None:
        try:
            if PDF2IMAGE_AVAILABLE:
                # Primary method: Convert PDF to image using pdf2image
                try:
                    images = pdf2image.convert_from_bytes(uploaded_file.read())
                    # Use the first page
                    first_page = images[0]
                    
                    # Convert to PIL Image for Gemini
                    return first_page
                except Exception as e:
                    st.warning(f"pdf2image failed: {str(e)}. Trying alternate method...")
                    # If pdf2image fails, fall back to text extraction
            
            # Fallback: Extract text from PDF
            uploaded_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                text_content += pdf_reader.pages[page_num].extract_text()
            
            st.markdown('<div class="status-box info">', unsafe_allow_html=True)
            st.write("ℹ️ Using text extraction instead of image processing. For best results, install Poppler.")
            st.markdown('</div>', unsafe_allow_html=True)
            return text_content
        except Exception as e:
            st.markdown('<div class="status-box error">', unsafe_allow_html=True)
            st.write(f"❌ Error processing PDF: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            raise
    else:
        raise FileNotFoundError("No file uploaded")

def analyze_resume(prompt, pdf_content, job_description):
    """Send resume and job description to Gemini API for analysis"""
    try:
        if not api_key:
            return "Error: GOOGLE_API_KEY environment variable not found! Please set it before using this application."
        
        # Initialize the model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"temperature": 0.2, "top_p": 0.95, "top_k": 64, "max_output_tokens": 2048},
        )
        
        # Build the prompt
        system_prompt = prompt
        user_prompt = f"Job Description: {job_description}\n\n"
        
        # Handle different content types (image vs text)
        if isinstance(pdf_content, Image.Image):
            # Image content from PDF
            content_parts = [
                system_prompt,
                user_prompt,
                pdf_content
            ]
            
            # Make the API call
            response = model.generate_content(content_parts)
            
        else:
            # Text content from PDF
            content_parts = [
                system_prompt,
                f"{user_prompt}Resume Content:\n{pdf_content}"
            ]
            
            # Make the API call
            response = model.generate_content(content_parts)
        
        # Debug response - we'll handle this outside the function
        
        # Extract the text from the response
        return response.text
        
    except Exception as e:
        st.markdown('<div class="status-box error">', unsafe_allow_html=True)
        st.write(f"❌ Error in API call: {type(e).__name__}")
        st.markdown('</div>', unsafe_allow_html=True)
        import traceback
        st.sidebar.expander("Error Details", expanded=False).code(traceback.format_exc())
        return f"Error in API call: {str(e)}"

# Create a tab-based interface for analysis options
st.markdown('---', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Analysis Options</div>', unsafe_allow_html=True)

analysis_tabs = st.tabs([
    "📊 Resume Review", 
    "🧩 Skills Analysis", 
    "⚡ Improvement Tips",
    "🎯 ATS Scoring"
])

# Prompts for different analyses
prompts = {
    "resume_review": """
    You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
    Please share your professional evaluation on whether the candidate's profile aligns with the role.
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    Provide a structured analysis with clear sections.
    """,
    
    "skill_gap": """
    You are an experienced Technical Human Resource Manager specializing in skill assessment.
    Extract all skills mentioned in the resume and compare them with the skills required in the job description.
    Identify skill gaps and provide recommendations on which skills the candidate should develop further.
    Format your response with clear sections for:
    1. Skills found in resume
    2. Skills required by job description
    3. Skill gaps identified
    4. Recommendations for improvement
    """,
    
    "improvement": """
    You are an expert Resume Consultant with deep experience in technical hiring.
    Analyze the provided resume against the job description and suggest specific improvements to make the resume more effective.
    Focus on:
    1. Content organization and structure
    2. Highlighting relevant experiences better
    3. Keyword optimization for ATS scanning
    4. Quantifying achievements
    5. Formatting and presentation suggestions
    """,
    
    "ats_score": """
    You are an expert ATS (Applicant Tracking System) scanner with deep understanding of how resume filtering works.
    Evaluate the resume against the provided job description and assign a percentage match score.
    Your response should have the following structure:
    1. ATS Match Score: [X]%
    2. Keywords Found: [list keywords found in both resume and job description]
    3. Keywords Missing: [list important keywords from job description not found in the resume]
    4. Recommendations: [specific suggestions to improve ATS matching]
    5. Final Thoughts: [brief conclusion about the candidate's chances]
    """
}

# Add buttons in the tabs and handle results
with analysis_tabs[0]:
    resume_review_btn = st.button("🔎 Analyze Resume Fit", key="review_btn", use_container_width=True)
    
with analysis_tabs[1]:
    skill_analysis_btn = st.button("🔎 Analyze Skills & Gaps", key="skills_btn", use_container_width=True)
    
with analysis_tabs[2]:
    improvement_btn = st.button("🔎 Get Improvement Tips", key="improve_btn", use_container_width=True)
    
with analysis_tabs[3]:
    ats_score_btn = st.button("🔎 Calculate ATS Score", key="ats_btn", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Add API key check
if not api_key:
    st.markdown('<div class="status-box error">', unsafe_allow_html=True)
    st.write("⚠️ GOOGLE_API_KEY environment variable not found! Please set it before using this application.")
    st.markdown('</div>', unsafe_allow_html=True)

# Create a container for results
results_container = st.container()

# Function to show loading indicator
def start_processing():
    st.session_state.processing = True
    st.markdown(
        """
        <script>
        showLoader();
        </script>
        """,
        unsafe_allow_html=True
    )

# Function to hide loading indicator
def end_processing():
    st.session_state.processing = False
    st.markdown(
        """
        <script>
        hideLoader();
        </script>
        """,
        unsafe_allow_html=True
    )

# Handle button clicks
if uploaded_file is None and (resume_review_btn or skill_analysis_btn or improvement_btn or ats_score_btn):
    st.markdown('<div class="status-box error">', unsafe_allow_html=True)
    st.write("❌ Please upload a resume (PDF) first.")
    st.markdown('</div>', unsafe_allow_html=True)
elif not input_text and (resume_review_btn or skill_analysis_btn or improvement_btn or ats_score_btn):
    st.markdown('<div class="status-box error">', unsafe_allow_html=True)
    st.write("❌ Please enter a job description.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    try:
        if resume_review_btn:
            with st.spinner(""):
                # Show loading indicator
                start_processing()
                
                progress_placeholder = results_container.empty()
                progress_placeholder.markdown("Analyzing resume alignment with job description...")
                
                pdf_content = input_pdf_setup(uploaded_file)
                response = analyze_resume(prompts["resume_review"], pdf_content, input_text)
                
                # Show debug info if enabled
                if show_debug:
                    st.sidebar.json(str(response))
                
                # Clear the placeholder with processing message
                progress_placeholder.empty()
                
                # Hide loading indicator
                end_processing()
                
                # Display results
                
                results_container.markdown('<div class="results-header">📊 Resume Analysis Results</div>', unsafe_allow_html=True)
                results_container.write(response)
                results_container.markdown('</div>', unsafe_allow_html=True)
                
        elif skill_analysis_btn:
            with st.spinner(""):
                # Show loading indicator
                start_processing()
                
                progress_placeholder = results_container.empty()
                progress_placeholder.markdown("Extracting skills and analyzing gaps...")
                
                pdf_content = input_pdf_setup(uploaded_file)
                response = analyze_resume(prompts["skill_gap"], pdf_content, input_text)
                
                # Show debug info if enabled
                if show_debug:
                    st.sidebar.json(str(response))
                
                # Clear the placeholder with processing message
                progress_placeholder.empty()
                
                # Hide loading indicator
                end_processing()
                
                # Display results
                
                results_container.markdown('<div class="results-header">🧩 Skills Analysis & Gap Assessment</div>', unsafe_allow_html=True)
                results_container.write(response)
                results_container.markdown('</div>', unsafe_allow_html=True)
                
        elif improvement_btn:
            with st.spinner(""):
                # Show loading indicator
                start_processing()
                
                progress_placeholder = results_container.empty()
                progress_placeholder.markdown("Generating improvement suggestions...")
                
                pdf_content = input_pdf_setup(uploaded_file)
                response = analyze_resume(prompts["improvement"], pdf_content, input_text)
                
                # Show debug info if enabled
                if show_debug:
                    st.sidebar.json(str(response))
                
                # Clear the placeholder with processing message
                progress_placeholder.empty()
                
                # Hide loading indicator
                end_processing()
                
                # Display results
                
                results_container.markdown('<div class="results-header">⚡ Improvement Suggestions</div>', unsafe_allow_html=True)
                results_container.write(response)
                results_container.markdown('</div>', unsafe_allow_html=True)
                
        elif ats_score_btn:
            with st.spinner(""):
                # Show loading indicator
                start_processing()
                
                progress_placeholder = results_container.empty()
                progress_placeholder.markdown("Calculating ATS compatibility score...")
                
                pdf_content = input_pdf_setup(uploaded_file)
                response = analyze_resume(prompts["ats_score"], pdf_content, input_text)
                
                # Show debug info if enabled
                if show_debug:
                    st.sidebar.json(str(response))
                
                # Clear the placeholder with processing message
                progress_placeholder.empty()
                
                # Hide loading indicator
                end_processing()
                
                # Display results
                
                results_container.markdown('<div class="results-header">🎯 ATS Compatibility Score</div>', unsafe_allow_html=True)
                results_container.write(response)
                results_container.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        # Ensure loading indicator is hidden even if an error occurs
        end_processing()
        
        st.markdown('<div class="status-box error">', unsafe_allow_html=True)
        st.write(f"❌ An error occurred: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# Add a sidebar with helpful information
with st.sidebar:
    st.markdown('<div class="section-title">ℹ️ About This Tool</div>', unsafe_allow_html=True)
    st.write("""
    This AI-powered tool helps you optimize your resume for specific job applications by analyzing your resume against job descriptions.
    
    The tool uses Google's Gemini AI to provide insights on resume alignment, skill gaps, ATS compatibility, and improvement suggestions.
    """)
    
    st.markdown('<div class="section-title">🔮 How It Works</div>', unsafe_allow_html=True)
    st.write("""
    1. Upload your resume (PDF format)
    2. Paste the job description
    3. Choose an analysis option
    4. Get AI-powered insights and recommendations
    """)

# Add footer with instructions
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("""
### ⚡ Features:

- **Resume Review**: General assessment of resume fit
- **Skills Analysis**: Identifies strengths and gaps in your skill set
- **Improvement Tips**: Specific resume enhancement suggestions
- **ATS Score**: Evaluate how well your resume will pass ATS filters

---

Need help setting up? Check the setup instructions below.
""")

# Add setup instructions
with st.expander("🔧 Setup Instructions"):
    st.markdown("""
    ### Required Setup
    
    This application requires:
    1. A Google API key set as the environment variable `GOOGLE_API_KEY`
    2. For PDF image processing (recommended for best results):
       - Poppler must be installed and available in your PATH
    
    #### Installing Poppler:
    
    **On Windows:**
    ```
    # Download from: https://github.com/oschwartz10612/poppler-windows/releases/
    # Extract to a folder (e.g., C:\\poppler-xx)
    # Add the bin folder to your PATH environment variable
    ```
    
    **On MacOS:**
    ```bash
    brew install poppler
    ```
    
    **On Ubuntu/Debian:**
    ```bash
    apt-get install poppler-utils
    ```
    
    **On CentOS/RHEL:**
    ```bash
    yum install poppler-utils
    ```
    
    If you can't install Poppler, the application will fall back to text extraction,
    but visual resume analysis capabilities will be limited.
    """)

st.markdown('</div>', unsafe_allow_html=True)