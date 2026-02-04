"""Streamlit interface for the AI Operations Assistant."""
import os
import streamlit as st
import time
from datetime import datetime
from dotenv import load_dotenv
from graph import AIOperationsGraph

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Operations Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ["GROQ_API_KEY", "OPENWEATHER_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def display_config_status():
    """Display configuration status in sidebar."""
    st.sidebar.header("🔧 Configuration")
    
    # Check environment variables
    env_vars = {
        "GROQ_API_KEY": "Groq API Key",
        "OPENWEATHER_API_KEY": "OpenWeather API Key", 
        "GITHUB_TOKEN": "GitHub Token (optional)"
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            if "KEY" in var or "TOKEN" in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else value
            else:
                display_value = value
            st.sidebar.success(f"✅ {description}")
        else:
            if var == "GITHUB_TOKEN":
                st.sidebar.info(f"ℹ️ {description} (Optional)")
            else:
                st.sidebar.error(f"❌ {description}")
    
    # LLM Configuration
    st.sidebar.subheader("🧠 LLM Configuration")
    st.sidebar.info("**Provider:** Groq")
    st.sidebar.info("**Model:** Llama 3.3 70B Versatile")
    st.sidebar.info("**Features:** Fast inference, Free tier")
    
    # Performance Analytics
    if "response_times" in st.session_state and st.session_state.response_times:
        st.sidebar.subheader("📊 Performance Analytics")
        response_times = st.session_state.response_times
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        st.sidebar.metric("Average Response", f"{avg_time:.2f}s")
        st.sidebar.metric("Fastest Response", f"{min_time:.2f}s")
        st.sidebar.metric("Slowest Response", f"{max_time:.2f}s")
        st.sidebar.metric("Total Requests", len(response_times))

def display_api_info():
    """Display API information in sidebar."""
    st.sidebar.header("🛠️ Integrated APIs")
    
    with st.sidebar.expander("GitHub API"):
        st.write("**Endpoint:** `api.github.com`")
        st.write("**Features:**")
        st.write("• Repository search")
        st.write("• Star counts & descriptions")
        st.write("• Language information")
        st.write("**Rate Limits:** 60/hour (5000 with token)")
    
    with st.sidebar.expander("OpenWeather API"):
        st.write("**Endpoint:** `openweathermap.org`")
        st.write("**Features:**")
        st.write("• Current weather data")
        st.write("• Temperature & conditions")
        st.write("• Humidity & pressure")
        st.write("**Rate Limits:** 1000/day (free tier)")

def display_examples():
    """Display example prompts."""
    st.header("📝 Example Prompts")
    
    examples = [
        "Find trending Python repositories and weather in Bangalore",
        "Get popular ML repos and temperature in Delhi",
        "Search Django projects and weather in Mumbai",
        "Show me React repositories and current weather in Chennai",
        "Find JavaScript frameworks and weather in Pune"
    ]
    
    cols = st.columns(2)
    
    for i, example in enumerate(examples):
        col = cols[i % 2]
        with col:
            if st.button(f"📋 {example}", key=f"example_{i}", use_container_width=True):
                st.session_state.user_input = example
                st.rerun()

def format_github_results(github_data):
    """Format GitHub repository results for display."""
    if not github_data:
        return "No repositories found."
    
    formatted = []
    for i, repo in enumerate(github_data[:5], 1):
        name = repo.get('name', 'Unknown')
        stars = repo.get('stars', 0)
        description = repo.get('description', 'No description available')
        language = repo.get('language', 'Unknown')
        url = repo.get('url', '#')
        
        formatted.append(f"""
**{i}. [{name}]({url})**
- ⭐ **{stars:,} stars**
- 💻 **Language:** {language}
- 📝 **Description:** {description}
        """)
    
    return "\n".join(formatted)

def format_weather_results(weather_data):
    """Format weather results for display."""
    if not weather_data:
        return "No weather information found."
    
    formatted = []
    for weather in weather_data:
        city = weather.get('city', 'Unknown')
        country = weather.get('country', '')
        temp = weather.get('temperature', 'N/A')
        desc = weather.get('description', 'N/A')
        humidity = weather.get('humidity', 'N/A')
        feels_like = weather.get('feels_like', 'N/A')
        
        location = f"{city}, {country}" if country else city
        
        formatted.append(f"""
**🌍 {location}**
- 🌡️ **Temperature:** {temp}°C (feels like {feels_like}°C)
- ☁️ **Conditions:** {desc}
- 💧 **Humidity:** {humidity}%
        """)
    
    return "\n".join(formatted)

def process_results(result, response_time=None):
    """Process and display results from the AI assistant."""
    if not result.get("success"):
        st.error("❌ **Error occurred during processing**")
        error_msg = result.get("formatted_response", result.get("error", "Unknown error"))
        st.error(error_msg)
        return
    
    # Display response time if available
    if response_time:
        st.success(f"⚡ **Response Time:** {response_time:.2f} seconds")
    
    # Extract data from results
    github_data = []
    weather_data = []
    
    raw_results = result.get("raw_results", {})
    execution_results = raw_results.get("results", [])
    
    for exec_result in execution_results:
        if exec_result.get("success") and exec_result.get("tool_name") == "github_search":
            tool_result = exec_result.get("result", {})
            if tool_result.get("success"):
                github_data.extend(tool_result.get("data", []))
        
        elif exec_result.get("success") and exec_result.get("tool_name") == "weather_current":
            tool_result = exec_result.get("result", {})
            if tool_result.get("success"):
                weather_data.append(tool_result.get("data", {}))
    
    # Display results in columns
    if github_data or weather_data:
        col1, col2 = st.columns(2)
        
        with col1:
            if github_data:
                st.subheader("🐙 GitHub Repositories")
                st.markdown(format_github_results(github_data))
        
        with col2:
            if weather_data:
                st.subheader("🌤️ Weather Information")
                st.markdown(format_weather_results(weather_data))
    
    # Display formatted response
    st.subheader("📋 Summary")
    formatted_response = result.get("formatted_response", "No summary available")
    st.info(formatted_response)
    
    # Display verification stats if available
    verification = result.get("verification", {})
    if verification:
        with st.expander("📊 Execution Details"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Completeness", verification.get("completeness", "unknown").title())
            
            with col2:
                st.metric("Quality", verification.get("quality", "unknown").title())
            
            with col3:
                data_summary = verification.get("data_summary", {})
                total_points = data_summary.get("total_data_points", 0)
                st.metric("Data Points", total_points)
            
            with col4:
                if response_time:
                    st.metric("Response Time", f"{response_time:.2f}s")

def main():
    """Main Streamlit application."""
    # Header
    st.title("🤖 AI Operations Assistant")
    st.markdown("**Multi-agent system for GitHub and Weather operations**")
    st.markdown("---")
    
    # Check environment configuration
    missing_vars = check_environment()
    
    if missing_vars:
        st.error("❌ **Configuration Error**")
        st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        st.info("Please set these variables in your `.env` file and restart the application.")
        
        with st.expander("🔧 Setup Instructions"):
            st.markdown("""
            1. Copy `.env.example` to `.env`
            2. Add your API keys:
               - **GROQ_API_KEY**: Get from [Groq Console](https://console.groq.com/)
               - **OPENWEATHER_API_KEY**: Get from [OpenWeatherMap](https://openweathermap.org/api)
            3. Restart the application
            """)
        
        # Display sidebar info even with missing config
        display_config_status()
        display_api_info()
        return
    
    # Initialize session state
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    if "ai_graph" not in st.session_state:
        try:
            st.session_state.ai_graph = AIOperationsGraph()
        except Exception as e:
            st.error(f"❌ **Failed to initialize AI Operations Assistant:** {str(e)}")
            st.info("Please check your configuration and try again.")
            display_config_status()
            display_api_info()
            return
    
    # Sidebar
    display_config_status()
    display_api_info()
    
    # Main interface
    st.header("💬 Enter Your Task")
    
    # Input form
    with st.form("task_form", clear_on_submit=False):
        user_input = st.text_area(
            "What would you like me to help you with?",
            value=st.session_state.user_input,
            height=100,
            placeholder="e.g., Find trending Python repositories and weather in Bangalore"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("🚀 Execute", use_container_width=True)
        with col2:
            if st.form_submit_button("🧪 Test Example", use_container_width=True):
                user_input = "Find trending Python repositories and weather in Bangalore"
                submit_button = True
    
    # Process task
    if submit_button and user_input.strip():
        st.session_state.processing = True
        
        # Start timing
        start_time = time.time()
        
        # Display processing status
        with st.spinner("🤖 Processing your request..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress updates
            status_text.text("🧠 Planning phase: Converting task to execution plan...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("⚡ Execution phase: Calling APIs and collecting data...")
            progress_bar.progress(50)
            
            try:
                # Execute the task
                result = st.session_state.ai_graph.run(user_input.strip())
                
                # Calculate response time
                end_time = time.time()
                response_time = end_time - start_time
                
                progress_bar.progress(75)
                status_text.text("🔍 Verification phase: Validating and formatting results...")
                time.sleep(0.5)
                
                progress_bar.progress(100)
                status_text.text(f"✅ Task completed in {response_time:.2f} seconds!")
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display results with response time
                st.markdown("---")
                st.header("📊 Results")
                process_results(result, response_time)
                
                # Store response time in session state for analytics
                if "response_times" not in st.session_state:
                    st.session_state.response_times = []
                st.session_state.response_times.append(response_time)
                
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ **An error occurred after {response_time:.2f} seconds:** {str(e)}")
        
        st.session_state.processing = False
    
    elif submit_button and not user_input.strip():
        st.warning("⚠️ Please enter a task to execute.")
    
    # Display examples
    st.markdown("---")
    display_examples()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Built with ❤️ using LangGraph, Groq Llama 3.3 70B, and Streamlit**",
        help="This AI Operations Assistant uses a multi-agent architecture to process your requests."
    )

if __name__ == "__main__":
    main()