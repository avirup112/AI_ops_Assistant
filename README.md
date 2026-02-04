# AI Operations Assistant

A sophisticated multi-agent AI system built with LangGraph that processes natural language tasks and executes operations using real third-party APIs. The system follows a strict **Planner → Executor → Verifier** architecture for reliable and structured task execution.

## 🏗️ Architecture Overview

The system implements a multi-agent architecture using LangGraph for orchestration:

```
User Input → Planner Agent → Executor Agent → Verifier Agent → Formatted Response
```

### 🤖 Agent Responsibilities

- **🧠 Planner Agent**: 
  - Uses Llama 3.3 70B (via Groq) with structured outputs
  - Converts natural language tasks into JSON execution plans
  - Uses Pydantic schemas for validation
  - Dynamically selects appropriate tools

- **⚡ Executor Agent**: 
  - Executes planned steps by calling real third-party APIs
  - Implements retry logic (3 attempts per tool)
  - Handles partial failures gracefully
  - Collects and aggregates results

- **🔍 Verifier Agent**: 
  - Uses LLM to validate execution completeness
  - Handles partial failures gracefully
  - Formats clean, structured final responses
  - Provides quality assessment

### 🛠️ Integrated APIs

1. **GitHub API** (`https://api.github.com`)
   - Search repositories by query
   - Return top 5 results with stars, descriptions, and metadata
   - Optional authentication for higher rate limits

2. **OpenWeather API** (`https://api.openweathermap.org`)
   - Fetch current weather by city name
   - Return temperature, conditions, humidity, and more
   - Supports multiple units (metric, imperial, kelvin)

### 🔧 Technology Stack

- **Streamlit**: Modern web interface for AI applications
- **LangGraph**: State-based workflow orchestration
- **Groq**: Fast LLM inference with Llama 3.3 70B Versatile
- **Pydantic**: Structured data validation and parsing
- **LangChain**: LLM integration and prompt management
- **Requests**: HTTP API calls

## 🚀 Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd ai_ops_assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
```

Required environment variables in `.env`:
```env
# Groq API Key (required) - Get from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# OpenWeather API Key (required) - Get from https://openweathermap.org/api  
OPENWEATHER_API_KEY=your_openweather_api_key_here

# GitHub API Token (optional but recommended)
GITHUB_TOKEN=your_github_token_here
```

### 4. Get API Keys

- **Groq API Key**: Visit [Groq Console](https://console.groq.com/) - Free tier available!
- **OpenWeather API Key**: Visit [OpenWeatherMap](https://openweathermap.org/api) - Free tier available
- **GitHub Token** (optional): Visit [GitHub Settings](https://github.com/settings/tokens)

## 🎯 Running the Project

**One command to run locally:**

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Additional Commands

```bash
# Run with custom port
streamlit run app.py --server.port 8502

# Run with custom host
streamlit run app.py --server.address 0.0.0.0

# Run in development mode
streamlit run app.py --server.runOnSave true
```

## 📝 Example Prompts to Test

1. **"Find trending Python repositories and weather in Bangalore"**
   - Searches for popular Python repositories on GitHub
   - Gets current weather information for Bangalore, India

2. **"Get popular ML repos and temperature in Delhi"**
   - Finds machine learning repositories
   - Retrieves Delhi weather conditions

3. **"Search Django projects and weather in Mumbai"**
   - Looks for Django web framework projects
   - Fetches Mumbai weather data

4. **"Show me React repositories and current weather in Chennai"**
   - Searches for React.js repositories
   - Gets Chennai weather information

5. **"Find JavaScript frameworks and weather in Pune"**
   - Discovers JavaScript framework repositories
   - Retrieves Pune weather conditions

## 🌟 Streamlit Interface Features

### 🎨 **Modern Web UI**
- **Clean, intuitive interface** with sidebar configuration
- **Real-time processing status** with progress indicators
- **Responsive design** that works on desktop and mobile
- **Interactive example prompts** for quick testing

### 📊 **Rich Data Visualization**
- **Side-by-side results** for GitHub repos and weather
- **Formatted repository cards** with stars, languages, and descriptions
- **Weather information panels** with temperature, conditions, and humidity
- **Execution metrics** showing completeness and quality scores

### 🔧 **Configuration Management**
- **Live configuration status** in sidebar
- **Environment variable validation** with clear error messages
- **API information panels** with rate limits and features
- **Setup instructions** for missing configuration

### 🚀 **User Experience**
- **One-click example execution** with pre-filled prompts
- **Custom task input** with large text area
- **Processing animations** with step-by-step status updates
- **Error handling** with helpful troubleshooting messages

## 🔍 System Validation

- **Multi-agent Design**: ✅ Planner → Executor → Verifier architecture
- **LLM with Structured Outputs**: ✅ Llama 3.3 70B with Pydantic schemas
- **Real Third-party APIs**: ✅ GitHub API + OpenWeather API
- **Complete End-to-End Results**: ✅ Full workflow from input to formatted output
- **No Hard-coded Responses**: ✅ All responses generated from real API data

### 🧪 Testing the System

```bash
# Start the application
streamlit run app.py

# Use the web interface to:
# 1. Check configuration status in sidebar
# 2. Click example prompts to test
# 3. Enter custom tasks in the text area
# 4. View real-time processing status
```

## ⚠️ Known Limitations & Tradeoffs

### Limitations

1. **API Rate Limits**:
   - GitHub: 60 requests/hour (unauthenticated), 5000/hour (with token)
   - OpenWeather: 1000 requests/day (free tier) with a rate limit of 60 calls per minute
   - Groq: Rate limits apply to free tier

2. **Network Dependencies**:
   - Requires stable internet connection
   - No offline mode available
   - API service availability affects functionality

3. **Language Support**:
   - Optimized for English language tasks
   - Limited multilingual support for city names

4. **Geographic Limitations**:
   - Weather API requires exact city names
   - May not work with very small towns or villages

### Tradeoffs

1. **Accuracy vs Speed**:
   - Uses lower temperature (0.1) for consistent planning
   - Prioritizes reliability over creative responses
   - 3-retry logic increases execution time but improves success rate

2. **Robustness vs Complexity**:
   - Multi-agent architecture adds complexity
   - Better error handling and partial failure recovery
   - More moving parts but higher reliability

3. **Cost vs Performance**:
   - Uses Groq (free tier) for cost efficiency
   - Excellent performance with Llama 3.3 70B
   - High-quality results without premium costs

4. **Flexibility vs Structure**:
   - Structured Pydantic schemas ensure consistency
   - May be less flexible for highly creative tasks
   - Optimized for operational/informational queries

## 🛠️ Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── planner.py      # Planner Agent with LLM planning
│   ├── executor.py     # Executor Agent with API calls
│   └── verifier.py     # Verifier Agent with result validation
├── tools/
│   ├── github_tool.py  # GitHub API integration
│   └── weather_tool.py # OpenWeather API integration
├── graph.py            # LangGraph orchestration
├── llm.py             # Groq LLM configuration
├── app.py             # Streamlit web interface
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variables template
├── .gitignore        # Git ignore rules
└── README.md         # This documentation
```

## 🔧 Development

### Adding New Tools

1. Create tool class in `tools/` directory
2. Implement API integration with error handling
3. Add tool to `ExecutorAgent._call_tool()` method
4. Update `PlannerAgent.available_tools` dictionary

### Extending Agents

- **Planner**: Modify system prompts and tool definitions
- **Executor**: Add new API integrations and retry logic
- **Verifier**: Enhance result validation and formatting