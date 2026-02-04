"""Executor Agent - Executes the planned steps and calls real APIs."""
import time
from typing import Dict, Any, List
from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool

class ExecutorAgent:
    """Agent responsible for executing planned steps and calling real APIs."""
    
    def __init__(self):
        self.github_tool = GitHubTool()
        self.weather_tool = WeatherTool()
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def execute_plan(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the planned steps with retry logic.
        
        Args:
            execution_plan: Dictionary containing the execution plan
            
        Returns:
            Dictionary with execution results
        """
        try:
            steps = execution_plan.get("steps", [])
            summary = execution_plan.get("summary", "")
            
            if not steps:
                return {
                    "success": False,
                    "error": "No steps found in execution plan",
                    "results": [],
                    "message": "Execution plan is empty"
                }
            
            results = []
            successful_steps = 0
            
            for i, step in enumerate(steps):
                step_number = i + 1
                print(f"Executing step {step_number}/{len(steps)}: {step.get('description', 'Unknown step')}")
                
                # Execute step with retry logic
                step_result = self._execute_step_with_retry(step, step_number)
                results.append(step_result)
                
                if step_result["success"]:
                    successful_steps += 1
                else:
                    print(f"Step {step_number} failed: {step_result.get('error', 'Unknown error')}")
            
            # Determine overall success
            overall_success = successful_steps > 0
            
            return {
                "success": overall_success,
                "results": results,
                "summary": summary,
                "stats": {
                    "total_steps": len(steps),
                    "successful_steps": successful_steps,
                    "failed_steps": len(steps) - successful_steps
                },
                "message": f"Executed {successful_steps}/{len(steps)} steps successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "results": [],
                "message": "Failed to execute plan"
            }
    
    def _execute_step_with_retry(self, step: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """
        Execute a single step with retry logic.
        
        Args:
            step: Step dictionary containing tool_name, parameters, and description
            step_number: Step number for logging
            
        Returns:
            Dictionary with step execution result
        """
        tool_name = step.get("tool_name")
        parameters = step.get("parameters", {})
        description = step.get("description", "")
        
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"  Attempt {attempt}/{self.max_retries}")
                
                # Execute the tool call
                result = self._call_tool(tool_name, parameters)
                
                if result["success"]:
                    return {
                        "success": True,
                        "step_number": step_number,
                        "tool_name": tool_name,
                        "description": description,
                        "parameters": parameters,
                        "result": result,
                        "attempts": attempt,
                        "message": f"Step {step_number} completed successfully"
                    }
                else:
                    last_error = result.get("error", "Tool call failed")
                    if attempt < self.max_retries:
                        print(f"    Failed: {last_error}. Retrying in {self.retry_delay}s...")
                        time.sleep(self.retry_delay)
                    
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    print(f"    Exception: {last_error}. Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
        
        # All retries failed
        return {
            "success": False,
            "step_number": step_number,
            "tool_name": tool_name,
            "description": description,
            "parameters": parameters,
            "error": last_error,
            "attempts": self.max_retries,
            "message": f"Step {step_number} failed after {self.max_retries} attempts"
        }
    
    def _call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the specified tool with given parameters.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Dictionary with tool execution result
        """
        if tool_name == "github_search":
            query = parameters.get("query", "")
            limit = parameters.get("limit", 5)
            
            if not query:
                return {
                    "success": False,
                    "error": "Missing required parameter: query",
                    "data": []
                }
            
            return self.github_tool.search_repositories(query, limit)
        
        elif tool_name == "weather_current":
            city = parameters.get("city", "")
            units = parameters.get("units", "metric")
            
            if not city:
                return {
                    "success": False,
                    "error": "Missing required parameter: city",
                    "data": {}
                }
            
            return self.weather_tool.get_current_weather(city, units)
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "data": None
            }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return ["github_search", "weather_current"]