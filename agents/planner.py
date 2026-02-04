"""Planner Agent - Converts natural language tasks into structured execution plans."""
import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain.schema import HumanMessage, SystemMessage
from llm import get_llm

class ToolCall(BaseModel):
    """Represents a single tool call in the execution plan."""
    tool_name: str = Field(description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(description="Parameters to pass to the tool")
    description: str = Field(description="Human-readable description of what this step does")

class ExecutionPlan(BaseModel):
    """Structured execution plan with multiple tool calls."""
    steps: List[ToolCall] = Field(description="List of tool calls to execute in order")
    summary: str = Field(description="Brief summary of the overall plan")

class PlannerAgent:
    """Agent responsible for converting natural language tasks into structured execution plans."""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.1)

        # Define available tools and their specs
        self.available_tools = {
            "github_search": {
                "description": "Search GitHub repositories by query",
                "parameters": {
                    "query": "Search query string (e.g., 'python machine learning', 'django web framework')",
                    "limit": "Maximum number of repositories to return (default: 5)"
                }
            },
            "weather_current": {
                "description": "Get current weather for a city",
                "parameters": {
                    "city": "City name (e.g., 'Bangalore', 'Delhi', 'Mumbai')",
                    "units": "Temperature units: 'metric' (Celsius), 'imperial' (Fahrenheit), or 'kelvin'"
                }
            }
        }
    
    def create_plan(self, user_task: str) -> Dict[str, Any]:
        """
        Convert a natural language task into a structured execution plan.
        
        Args:
            user_task: Natural language description of the task
            
        Returns:
            Dictionary containing the execution plan or error information
        """
        try:
            # Create the system prompt
            system_prompt = self._create_system_prompt()
            
            # Create the user prompt
            user_prompt = f"""
Task: {user_task}

Analyze this task and create a structured execution plan. Return ONLY a valid JSON object with the following structure:

{{
    "steps": [
        {{
            "tool_name": "github_search",
            "parameters": {{"query": "python", "limit": 5}},
            "description": "Search for Python repositories"
        }},
        {{
            "tool_name": "weather_current", 
            "parameters": {{"city": "Bangalore", "units": "metric"}},
            "description": "Get current weather in Bangalore"
        }}
    ],
    "summary": "Search for Python repositories and get weather in Bangalore"
}}

Important:
- Use only the available tools: github_search, weather_current
- Extract city names and search queries from the user task
- Return ONLY the JSON object, no additional text
- Ensure all required parameters are included
"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Try to Parse the JSON response
            try:
                plan_data = json.loads(response_text)
                
                # Validate the plan structure
                execution_plan = ExecutionPlan(**plan_data)
                
                return {
                    "success": True,
                    "plan": execution_plan.dict(),
                    "message": f"Created execution plan with {len(execution_plan.steps)} steps"
                }
                
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse LLM response as JSON: {str(e)}",
                    "raw_response": response_text,
                    "message": "LLM did not return valid JSON"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Plan validation failed: {str(e)}",
                    "raw_response": response_text,
                    "message": "Generated plan does not match expected structure"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Planning failed: {str(e)}",
                "message": "Failed to create execution plan"
            }
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the planner agent."""
        tools_description = ""
        for tool_name, tool_info in self.available_tools.items():
            tools_description += f"\n- {tool_name}: {tool_info['description']}\n"
            for param, desc in tool_info['parameters'].items():
                tools_description += f"  - {param}: {desc}\n"
        
        return f"""You are a Planner Agent in an AI Operations Assistant system. Your job is to convert natural language tasks into structured execution plans.

Available Tools:{tools_description}

Your responsibilities:
1. Analyze the user's natural language task
2. Identify which tools are needed and in what order
3. Extract parameters from the task (cities, search queries, etc.)
4. Return a structured JSON execution plan

Rules:
- ONLY return valid JSON, no additional text or explanations
- Use only the available tools listed above
- Extract specific parameters from the user task (e.g., city names, search terms)
- If a task mentions multiple cities or searches, create separate steps for each
- Default to 5 repositories for GitHub searches unless specified otherwise
- Use 'metric' units for weather unless specified otherwise
- Be specific in step descriptions

Example task: "Find trending Python repositories and weather in Delhi"
Expected output:
{{
    "steps": [
        {{
            "tool_name": "github_search",
            "parameters": {{"query": "python trending", "limit": 5}},
            "description": "Search for trending Python repositories"
        }},
        {{
            "tool_name": "weather_current",
            "parameters": {{"city": "Delhi", "units": "metric"}},
            "description": "Get current weather in Delhi"
        }}
    ],
    "summary": "Search for trending Python repositories and get current weather in Delhi"
}}"""