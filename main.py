import streamlit as st
import requests
import json
import time
from datetime import datetime

# Ollama API Configuration
OLLAMA_URL = "http://localhost:11434"

class OllamaLLM:
    def __init__(self):
        self.models = ["llama2", "codellama", "mistral"]
        
    def check_ollama_status(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Get list of available models"""
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except:
            return []
    
    def generate_response(self, prompt, model="llama2", context=""):
        """Generate response using Ollama"""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
            if response.status_code == 200:
                return response.json().get('response', '')
            return "Error: Unable to generate response"
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    st.set_page_config(
        page_title="AI-Powered Local LLM",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI-Powered Local LLM Application")
    st.markdown("*Privacy-focused AI interactions using Ollama*")
    
    # Initialize LLM
    llm = OllamaLLM()
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check Ollama status
        if llm.check_ollama_status():
            st.success("✅ Ollama is running")
            available_models = llm.get_available_models()
            if available_models:
                selected_model = st.selectbox("Select Model", available_models)
            else:
                selected_model = st.selectbox("Select Model", ["llama2", "codellama", "mistral"])
                st.warning("⚠️ No models found. Please install models first.")
        else:
            st.error("❌ Ollama is not running")
            st.info("Please start Ollama service first")
            selected_model = "llama2"
        
        st.markdown("---")
        
        # Document Upload
        st.subheader("📄 Document Context")
        uploaded_file = st.file_uploader("Upload document for context", 
                                       type=['txt', 'md', 'py'])
        
        document_context = ""
        if uploaded_file:
            document_context = str(uploaded_file.read(), "utf-8")
            st.success(f"Document loaded: {len(document_context)} characters")
    
    # Main Interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("timestamp"):
                    st.caption(f"⏰ {message['timestamp']}")
        
        # Chat input
        if prompt := st.chat_input("Ask me anything..."):
            # Add user message
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt, 
                "timestamp": timestamp
            })
            
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(f"⏰ {timestamp}")
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = llm.generate_response(prompt, selected_model, document_context)
                
                st.markdown(response)
                response_time = datetime.now().strftime("%H:%M:%S")
                st.caption(f"⏰ {response_time}")
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response, 
                    "timestamp": response_time
                })
    
    with col2:
        st.subheader("📊 Session Info")
        
        # Session statistics
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        
        st.metric("Total Messages", total_messages)
        st.metric("User Messages", user_messages)
        st.metric("AI Responses", total_messages - user_messages)
        
        st.markdown("---")
        
        # Model Information
        st.subheader("🔧 Model Info")
        st.info(f"**Current Model:** {selected_model}")
        st.info(f"**Context Length:** {len(document_context)} chars")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💡 Ideas"):
                idea_prompt = "Give me 5 creative project ideas for a computer science student"
                st.session_state.quick_prompt = idea_prompt
        
        with col_b:
            if st.button("🔍 Explain"):
                explain_prompt = "Explain the concept of machine learning in simple terms"
                st.session_state.quick_prompt = explain_prompt
        
        # Handle quick prompts
        if hasattr(st.session_state, 'quick_prompt'):
            prompt = st.session_state.quick_prompt
            delattr(st.session_state, 'quick_prompt')
            
            # Process quick prompt (same logic as chat input)
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt, 
                "timestamp": timestamp
            })
            
            response = llm.generate_response(prompt, selected_model, document_context)
            response_time = datetime.now().strftime("%H:%M:%S")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "timestamp": response_time
            })
            
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        "**Features:** Local LLM Processing | Document Context | Privacy-Focused | Multi-Model Support"
    )

if __name__ == "__main__":
    main()