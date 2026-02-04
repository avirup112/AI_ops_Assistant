"""Main CLI interface for the AI Operations Assistant."""
import os
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv
from graph import AIOperationsGraph

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

def check_environment() -> bool:
    """Check if required environment variables are set."""
    required_vars = ["GROQ_API_KEY", "OPENWEATHER_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        console.print(Panel(
            f"❌ Missing required environment variables:\n" + 
            "\n".join(f"• {var}" for var in missing_vars) +
            "\n\nPlease set these variables in your .env file or environment.",
            title="Configuration Error",
            border_style="red"
        ))
        return False
    
    return True

def display_welcome():
    """Display welcome message and instructions."""
    welcome_text = Text()
    welcome_text.append("🤖 AI Operations Assistant\n", style="bold blue")
    welcome_text.append("Multi-agent system for GitHub and Weather operations\n\n", style="dim")
    welcome_text.append("Supported operations:\n", style="bold")
    welcome_text.append("• Search GitHub repositories\n", style="green")
    welcome_text.append("• Get current weather information\n", style="green")
    welcome_text.append("• Combined operations (repos + weather)\n", style="green")
    
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))

def display_examples():
    """Display example prompts."""
    examples = [
        "Find trending Python repositories and weather in Bangalore",
        "Get popular ML repos and temperature in Delhi", 
        "Search Django projects and weather in Mumbai",
        "Show me React repositories and current weather in Chennai",
        "Find JavaScript frameworks and weather in Pune"
    ]
    
    examples_text = Text()
    examples_text.append("Example prompts you can try:\n\n", style="bold")
    
    for i, example in enumerate(examples, 1):
        examples_text.append(f"{i}. ", style="dim")
        examples_text.append(f'"{example}"\n', style="italic cyan")
    
    console.print(Panel(examples_text, title="Examples", border_style="green"))

def process_task(ai_graph: AIOperationsGraph, task: str, verbose: bool = False):
    """Process a single task using the AI Operations Assistant."""
    try:
        console.print(f"\n🎯 Task: {task}", style="bold")
        console.print("─" * 60)
        
        # Run the assistant
        with console.status("🤖 Processing your request...", spinner="dots"):
            if not verbose:
                # Suppress print statements during execution
                import io
                import contextlib
                
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    result = ai_graph.run(task)
            else:
                result = ai_graph.run(task)
        
        console.print()  # Add spacing
        
        # Display results
        if result.get("success"):
            # Display formatted response
            formatted_response = result.get("formatted_response", "No response generated")
            console.print(Panel(
                formatted_response,
                title="✅ Results",
                border_style="green"
            ))
            
            # Show verification info if verbose
            if verbose and "verification" in result:
                verification = result["verification"]
                stats_text = f"Completeness: {verification.get('completeness', 'unknown')}\n"
                stats_text += f"Quality: {verification.get('quality', 'unknown')}\n"
                stats_text += f"Data points: {verification.get('data_summary', {}).get('total_data_points', 0)}"
                
                console.print(Panel(
                    stats_text,
                    title="📊 Verification Stats",
                    border_style="blue"
                ))
        
        else:
            # Display error
            error_message = result.get("formatted_response", result.get("error", "Unknown error"))
            console.print(Panel(
                error_message,
                title="❌ Error",
                border_style="red"
            ))
    
    except Exception as e:
        console.print(Panel(
            f"Critical error occurred: {str(e)}",
            title="❌ Critical Error",
            border_style="red"
        ))

def main():
    """Main entry point for the AI Operations Assistant."""
    import sys
    
    # Parse command line arguments manually for simpler interface
    args = sys.argv[1:]
    
    # Handle special flags
    if "--help" in args or "-h" in args:
        console.print("""
🤖 AI Operations Assistant

Usage:
    python main.py "Your task here"                    # Execute a task
    python main.py --interactive                       # Interactive mode
    python main.py --examples                          # Show examples
    python main.py --test                             # Run test
    python main.py --config                           # Show configuration

Examples:
    python main.py "Find trending Python repositories and weather in Bangalore"
    python main.py "Get popular ML repos and temperature in Delhi"
    python main.py "Search Django projects and weather in Mumbai"
        """)
        return
    
    if "--examples" in args:
        display_examples()
        return
    
    if "--config" in args:
        show_config()
        return
    
    if "--test" in args:
        run_test()
        return
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Display welcome message
    display_welcome()
    
    # Initialize the AI Operations Graph
    try:
        console.print("🔧 Initializing AI Operations Assistant...", style="dim")
        ai_graph = AIOperationsGraph()
        console.print("✅ Assistant initialized successfully!\n", style="green")
    except Exception as e:
        console.print(Panel(
            f"❌ Failed to initialize assistant: {str(e)}\n\nPlease check your configuration and try again.",
            title="Initialization Error",
            border_style="red"
        ))
        sys.exit(1)
    
    # Interactive mode
    if "--interactive" in args or "-i" in args:
        console.print("💬 Interactive mode - Type 'quit' or 'exit' to stop\n", style="dim")
        
        while True:
            try:
                # Get user input
                user_task = input("\n🎯 Enter your task: ")
                
                # Check for quit commands
                if user_task.lower() in ['quit', 'exit', 'q']:
                    console.print("👋 Goodbye!", style="blue")
                    break
                
                # Process the task
                verbose = "--verbose" in args or "-v" in args
                process_task(ai_graph, user_task, verbose)
                
            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!", style="blue")
                break
            except Exception as e:
                console.print(f"❌ Error: {str(e)}", style="red")
    
    # Single task mode
    elif args and not any(arg.startswith("--") for arg in args):
        task = " ".join(args)
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        process_task(ai_graph, task, verbose)
    
    # No arguments - show help
    else:
        console.print("💬 No task provided. Use --interactive for interactive mode or --help for usage.", style="dim")
        console.print("Example: python main.py \"Find trending Python repositories and weather in Bangalore\"", style="cyan")

def run_test():
    """Test the AI Operations Assistant with a sample task."""
    if not check_environment():
        sys.exit(1)
    
    console.print("🧪 Running test with sample task...\n", style="blue")
    
    try:
        ai_graph = AIOperationsGraph()
        test_task = "Find trending Python repositories and weather in Bangalore"
        
        console.print(f"Test task: {test_task}", style="dim")
        process_task(ai_graph, test_task, verbose=True)
        
    except Exception as e:
        console.print(f"❌ Test failed: {str(e)}", style="red")
        sys.exit(1)

def show_config():
    """Show current configuration and environment status."""
    console.print("🔧 AI Operations Assistant Configuration\n", style="bold blue")
    
    # Check environment variables
    env_vars = {
        "GROQ_API_KEY": "Groq API Key",
        "OPENWEATHER_API_KEY": "OpenWeather API Key", 
        "GITHUB_TOKEN": "GitHub Token (optional)"
    }
    
    config_text = Text()
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            if "KEY" in var or "TOKEN" in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else value
            else:
                display_value = value
            config_text.append(f"✅ {description}: {display_value}\n", style="green")
        else:
            config_text.append(f"❌ {description}: Not set\n", style="red")
    
    console.print(Panel(config_text, title="Environment Variables", border_style="blue"))
    
    # Show LLM info
    llm_text = Text()
    llm_text.append("• Provider: Groq (Llama 3.3 70B Versatile)\n", style="green")
    llm_text.append("• Fast inference with free tier\n", style="green")
    
    console.print(Panel(llm_text, title="LLM Configuration", border_style="green"))
    
    # Show available tools
    tools_text = Text()
    tools_text.append("• GitHub Repository Search\n", style="green")
    tools_text.append("• Current Weather Information\n", style="green")
    
    console.print(Panel(tools_text, title="Available Tools", border_style="green"))

if __name__ == "__main__":
    main()