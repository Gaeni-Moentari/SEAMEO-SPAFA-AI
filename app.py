import streamlit as st
import os
from dotenv import load_dotenv
from crew_manager import crew_manager
import time

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SEAMEO SPAFA Help Center",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        line-height: 1.6;
    }
    
    .user-message {
        border-left-color: #0284c7 !important;
        margin-left: 2rem;
    }
    
    .assistant-message {
        border-left-color: #0ea5e9 !important;
        margin-right: 2rem;
    }
    
    .chat-message strong {
        color: #1e40af;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .chat-message p {
        margin: 0.5rem 0;
    }
    
    .warning-box {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #dbeafe;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "first_visit" not in st.session_state:
        st.session_state.first_visit = True

def display_header():
    """Display main header"""
    # Create centered columns for logo
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("gema-spafa.png", width=500)
    
    st.markdown("""
    <div class="main-header">
        <h1>SEAMEO SPAFA SUPPORT Center</h1>
        <p>Southeast Asian Ministers of Education Organization<br>
        Regional Centre for Archaeology and Fine Arts</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with information"""
    with st.sidebar:
        
        st.header("ℹ️ About SEAMEO SPAFA")
        
        st.markdown("""
        **SEAMEO SPAFA** is the regional centre for archaeology and fine arts under the 
        Southeast Asian Ministers of Education Organization.
        
        **Help Center Services:**
        - 📚 Program and research information
        - 🎨 Arts and cultural activities
        - 🏺 Archaeology and cultural heritage
        - 📖 Publications and resources
        - 📅 Events and workshops
        """)
        
        st.divider()
        
        st.header("📋 Example Questions")
        example_questions = [
            "What is SEAMEO SPAFA?",
            "What programs are available?",
            "How to join research activities?",
            "When is the next archaeology workshop?",
            "Where is SEAMEO SPAFA office located?",
            "What are the latest publications?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}", use_container_width=True):
                st.session_state.example_question = question



def display_chat_history():
    """Display chat history"""
    for message in st.session_state.messages:
        css_class = "user-message" if message["role"] == "user" else "assistant-message"
        icon = "👤" if message["role"] == "user" else "🤖"
        
        # Format content to handle line breaks
        content = message["content"].replace('\n', '<br>')
        
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{icon} {message["role"].title()}:</strong><br><br>
            <div style="margin-top: 0.5rem;">{content}</div>
        </div>
        """, unsafe_allow_html=True)

def process_user_input(user_question: str):
    """Process user input and get AI response"""
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": user_question,
        "timestamp": time.time()
    })
    
    # Validate question
    validation = crew_manager.validate_question(user_question)
    
    if not validation["valid"]:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"❌ {validation['message']}",
            "timestamp": time.time()
        })
        return
    
    # Process question with CrewAI
    with st.spinner("🤖 Processing your question..."):
        result = crew_manager.process_question(user_question)
    
    if result["success"]:
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "timestamp": time.time()
        })
    else:
        error_message = f"""
        ❌ **An error occurred while processing your question.**
        
        **Error Details:** {result.get('error', 'Unknown error')}
        
        Please try again or contact the administrator if the problem persists.
        """
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_message,
            "timestamp": time.time()
        })

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Display sidebar
    display_sidebar()
    
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
        st.markdown("""
        <div class="warning-box">
            <h3>⚠️ API Keys Configuration Required</h3>
            <p>To use this application, you need to configure API keys:</p>
            <ol>
                <li>Create a <code>.env</code> file in the application directory</li>
                <li>Add your API keys:
                    <br><code>OPENAI_API_KEY=your_openai_key_here</code>
                    <br><code>SERPER_API_KEY=your_serper_key_here</code>
                </li>
                <li>Restart the application</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display chat history
    display_chat_history()
    
    # Handle example question from sidebar
    if hasattr(st.session_state, 'example_question'):
        user_input = st.session_state.example_question
        del st.session_state.example_question
        process_user_input(user_input)
        st.rerun()
    
    # Chat input
    user_input = st.chat_input("Ask something about SEAMEO SPAFA...")
    
    if user_input:
        process_user_input(user_input)
        st.rerun()
    
    # Clear chat button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.first_visit = True
            st.rerun()

if __name__ == "__main__":
    main()