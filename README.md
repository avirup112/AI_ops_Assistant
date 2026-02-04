# AI Operations Assistant

A sophisticated multi-agent AI system built with LangGraph that processes natural language tasks and executes operations using real APIs. The system follows a strict **Planner → Executor → Verifier** architecture for reliable and structured task execution.

## 🏗️ Architecture

The system implements a multi-agent architecture using LangGraph for orchestration:

```
User Input → Planner Agent → Executor Agent → Verifier Agent → Formatted Response
```

### Agent Responsibilities

- **🧠 Planner Agent**: Converts natural language tasks into structured JSON execution plans using LLM with Pydantic schemas
- **⚡ Executor Agent**: Executes planned steps by calling real third-party APIs with retry logic (3 attempts per tool)
- **🔍 Verifier Agent**: Validates results, handles partial failures gracefully, and formats clean structured responses

### Tools Integration

- **GitHub API**: Search repositories by query, return top results with stars and descriptions
- **OpenWeather API**: Fetch current weather by city with temperature and conditions

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or create the project directory
cd ai_ops_assistant

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# For OpenAI (default)
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
LLM_PROVIDER=openai

# OR for Groq (faster, free tier available)
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
LLM_PROVIDER=groq

# Optional (for higher GitHub rate limits)
GITHUB_TOKEN=your_github_token_here
```

### 3. Get API Keys

- **Groq API Key** (recommended): Get from [Groq Console](https://console.groq.com/) - Free tier available!
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys) - Paid service
- **OpenWeather API Key**: Get from [OpenWeatherMap](https://openweathermap.org/api) - Free tier available
- **GitHub Token** (optional): Get from [GitHub Settings](https://github.com/settings/tokens)

### 4. Run the Assistant

**One command to run locally:**

```bash
python main.py "Find trending Python repositories and weather in Bangalore"
```

## 📖 Usage Examples

### Command Line Interface

```bash
# Single task execution
python main.py "Get popular ML repos and temperature in Delhi"

# Interactive mode
python main.py --interactive

# Show examples
python main.py --examples

# Test the system
python main.py --test

# Check configuration
python main.py --config

# Verbose output
python main.py "Search Django projects and weather in Mumbai" --verbose

# Help
python main.py --help
```

### Example Prompts

1. **"Find trending Python repositories and weather in Bangalore"**
   - Searches for popular Python repositories on GitHub
   - Gets current weather information for Bangalore

2. **"Get popular ML repos and temperature in Delhi"**
   - Finds machine learning repositories
   - Retrieves Delhi weather conditions

3. **"Search Django projects and weather in Mumbai"**
   - Looks for Django-related projects
   - Fetches Mumbai weather data

4. **"Show me React repositories and current weather in Chennai"**
   - Searches for React.js repositories
   - Gets Chennai weather information

5. **"Find JavaScript frameworks and weather in Pune"**
   - Discovers JavaScript framework repositories
   - Retrieves Pune weather conditions

## 🛠️ Technical Implementation

### Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── planner.py      # Planner Agent - LLM-powered task planning
│   ├── executor.py     # Executor Agent - API calls with retry logic
│   └── verifier.py     # Verifier Agent - Result validation & formatting
├── tools/
│   ├── github_tool.py  # GitHub API integration
│   └── weather_tool.py # OpenWeather API integration
├── graph.py            # LangGraph orchestration & state management
├── llm.py             # LLM configuration (OpenAI/Groq)
├── main.py            # CLI interface with Rich formatting
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variables template
└── README.md         # This file
```

### Key Technologies

- **LangGraph**: State-based workflow orchestration
- **Pydantic**: Structured data validation and parsing
- **LangChain**: LLM integration and prompt management
- **Typer**: Modern CLI framework
- **Rich**: Beautiful terminal formatting
- **Requests**: HTTP API calls

### State Management

The system uses TypedDict for state management across agents:

```python
class AssistantState(TypedDict):
    user_task: str
    execution_plan: Dict[str, Any]
    execution_results: Dict[str, Any]
    final_response: Dict[str, Any]
    error: str
    current_step: str
```

### Error Handling

- **Retry Logic**: 3 attempts per API call with exponential backoff
- **Graceful Degradation**: Partial failures don't stop the entire workflow
- **Comprehensive Logging**: Detailed error messages and execution tracking
- **Fallback Responses**: Basic formatting when LLM formatting fails

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM operations |
| `OPENWEATHER_API_KEY` | Yes | OpenWeather API key for weather data |
| `GITHUB_TOKEN` | No | GitHub token for higher rate limits |
| `LLM_PROVIDER` | No | LLM provider: `openai` or `groq` (default: openai) |
| `GROQ_API_KEY` | No | Groq API key (if using Groq) |

### Supported LLM Providers

- **Groq**: Mixtral-8x7b-32768 (recommended - fast inference, free tier available)
- **OpenAI**: GPT-3.5-turbo (paid service)

## 🎯 APIs Used

### GitHub API
- **Endpoint**: `https://api.github.com/search/repositories`
- **Features**: Repository search, star counts, descriptions, languages
- **Rate Limits**: 60 requests/hour (unauthenticated), 5000/hour (authenticated)

### OpenWeather API
- **Endpoint**: `https://api.openweathermap.org/data/2.5/weather`
- **Features**: Current weather, temperature, humidity, conditions
- **Rate Limits**: 1000 requests/day (free tier)

## ⚠️ Known Limitations & Tradeoffs

### Limitations

1. **API Rate Limits**: 
   - GitHub: 60 requests/hour without token
   - OpenWeather: 1000 requests/day on free tier

2. **LLM Dependencies**: 
   - Requires OpenAI API key (paid service)
   - Planning quality depends on LLM performance

3. **Network Dependencies**: 
   - Requires internet connection for all operations
   - No offline mode available

4. **Language Support**: 
   - Currently optimized for English language tasks
   - Limited multilingual support

### Tradeoffs

1. **Accuracy vs Speed**: 
   - Uses lower temperature (0.1) for consistent planning
   - May be slower but more reliable than higher temperature settings

2. **Robustness vs Complexity**: 
   - Multi-agent architecture adds complexity but improves reliability
   - Retry logic increases execution time but handles transient failures

3. **Flexibility vs Structure**: 
   - Structured Pydantic schemas ensure consistency
   - May be less flexible for highly creative or unusual tasks

4. **Cost vs Capability**: 
   - Uses premium LLM services for better results
   - Higher cost compared to rule-based systems

## 🧪 Testing

```bash
# Run built-in test
python main.py test

# Test specific functionality
python main.py "Find Python repositories" --verbose

# Check configuration
python main.py config
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Missing API Keys**: Run `python main.py config` to check configuration
2. **Rate Limit Errors**: Add GitHub token or wait for rate limit reset
3. **Network Errors**: Check internet connection and API service status
4. **LLM Errors**: Verify OpenAI API key and account credits

### Getting Help

- Check the configuration with `python main.py config`
- Run in verbose mode with `--verbose` flag
- Test with `python main.py test`
- Review error messages in the formatted output

---

**Built with ❤️ using LangGraph, OpenAI, and modern Python tools.**