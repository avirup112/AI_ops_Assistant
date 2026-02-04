"""Verifier Agent - Validates execution results and formats final response."""
from typing import Dict, Any, List
from langchain.schema import HumanMessage, SystemMessage
from llm import get_llm

class VerifierAgent:
    """Agent responsible for validating execution results and formatting final response."""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
    
    def verify_and_format(self, execution_results: Dict[str, Any], original_task: str) -> Dict[str, Any]:
        """
        Verify execution results and format a clean final response.
        
        Args:
            execution_results: Results from the executor agent
            original_task: Original user task
            
        Returns:
            Dictionary with verification results and formatted response
        """
        try:
            # Extract key information
            results = execution_results.get("results", [])
            stats = execution_results.get("stats", {})
            overall_success = execution_results.get("success", False)
            
            # Analyze results
            analysis = self._analyze_results(results, stats, original_task)
            
            # Generate formatted response using LLM
            formatted_response = self._generate_formatted_response(
                results, analysis, original_task, overall_success
            )
            
            return {
                "success": True,
                "verification": analysis,
                "formatted_response": formatted_response,
                "raw_results": execution_results,
                "message": "Results verified and formatted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Verification failed: {str(e)}",
                "raw_results": execution_results,
                "message": "Failed to verify and format results"
            }
    
    def _analyze_results(self, results: List[Dict[str, Any]], stats: Dict[str, Any], original_task: str) -> Dict[str, Any]:
        """
        Analyze the execution results for completeness and quality.
        
        Args:
            results: List of step execution results
            stats: Execution statistics
            original_task: Original user task
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "completeness": "complete",
            "quality": "high",
            "issues": [],
            "successful_operations": [],
            "failed_operations": [],
            "data_summary": {}
        }
        
        # Analyze each result
        github_results = []
        weather_results = []
        
        for result in results:
            if not result.get("success", False):
                analysis["failed_operations"].append({
                    "step": result.get("step_number"),
                    "tool": result.get("tool_name"),
                    "error": result.get("error"),
                    "description": result.get("description")
                })
                analysis["issues"].append(f"Step {result.get('step_number')} failed: {result.get('error')}")
            else:
                analysis["successful_operations"].append({
                    "step": result.get("step_number"),
                    "tool": result.get("tool_name"),
                    "description": result.get("description")
                })
                
                # Collect data by tool type
                tool_name = result.get("tool_name")
                tool_result = result.get("result", {})
                
                if tool_name == "github_search" and tool_result.get("success"):
                    github_results.extend(tool_result.get("data", []))
                elif tool_name == "weather_current" and tool_result.get("success"):
                    weather_results.append(tool_result.get("data", {}))
        
        # Summarize collected data
        analysis["data_summary"] = {
            "github_repositories": len(github_results),
            "weather_locations": len(weather_results),
            "total_data_points": len(github_results) + len(weather_results)
        }
        
        # Determine completeness
        total_steps = stats.get("total_steps", 0)
        successful_steps = stats.get("successful_steps", 0)
        
        if successful_steps == 0:
            analysis["completeness"] = "failed"
            analysis["quality"] = "poor"
        elif successful_steps < total_steps:
            analysis["completeness"] = "partial"
            analysis["quality"] = "medium"
        
        return analysis
    
    def _generate_formatted_response(self, results: List[Dict[str, Any]], analysis: Dict[str, Any], 
                                   original_task: str, overall_success: bool) -> str:
        """
        Generate a formatted response using the LLM.
        
        Args:
            results: Execution results
            analysis: Analysis results
            original_task: Original user task
            overall_success: Whether execution was successful overall
            
        Returns:
            Formatted response string
        """
        try:
            # Prepare data for formatting
            github_data = []
            weather_data = []
            
            for result in results:
                if result.get("success") and result.get("tool_name") == "github_search":
                    tool_result = result.get("result", {})
                    if tool_result.get("success"):
                        github_data.extend(tool_result.get("data", []))
                
                elif result.get("success") and result.get("tool_name") == "weather_current":
                    tool_result = result.get("result", {})
                    if tool_result.get("success"):
                        weather_data.append(tool_result.get("data", {}))
            
            # Create system prompt
            system_prompt = """You are a Verifier Agent that formats execution results into clean, user-friendly responses.

Your job is to:
1. Present the results in a clear, organized manner
2. Handle partial failures gracefully
3. Provide useful information even when some operations fail
4. Use a professional but friendly tone

Format guidelines:
- Start with a brief summary
- Present GitHub repositories in a numbered list with name, stars, and description
- Present weather information clearly with temperature and conditions
- If there are failures, mention them briefly but focus on successful results
- End with a helpful conclusion"""

            # Create user prompt with data
            user_prompt = f"""Original Task: {original_task}

Execution Results:
- Overall Success: {overall_success}
- Successful Operations: {len(analysis['successful_operations'])}
- Failed Operations: {len(analysis['failed_operations'])}

GitHub Repositories Found: {len(github_data)}
{self._format_github_data_for_prompt(github_data)}

Weather Information: {len(weather_data)} location(s)
{self._format_weather_data_for_prompt(weather_data)}

Issues: {analysis['issues'] if analysis['issues'] else 'None'}

Please format this into a clean, user-friendly response that addresses the original task."""

            # Get formatted response from LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            # Fallback to basic formatting if LLM fails
            return self._create_fallback_response(results, analysis, original_task)
    
    def _format_github_data_for_prompt(self, github_data: List[Dict[str, Any]]) -> str:
        """Format GitHub data for the LLM prompt."""
        if not github_data:
            return "No repositories found."
        
        formatted = []
        for i, repo in enumerate(github_data[:5], 1):
            name = repo.get('name', 'Unknown')
            stars = repo.get('stars', 0)
            desc = repo.get('description', 'No description')
            formatted.append(f"{i}. {name} - {stars} stars - {desc}")
        
        return "\n".join(formatted)
    
    def _format_weather_data_for_prompt(self, weather_data: List[Dict[str, Any]]) -> str:
        """Format weather data for the LLM prompt."""
        if not weather_data:
            return "No weather information found."
        
        formatted = []
        for weather in weather_data:
            city = weather.get('city', 'Unknown')
            temp = weather.get('temperature', 'N/A')
            desc = weather.get('description', 'N/A')
            formatted.append(f"- {city}: {temp}°C, {desc}")
        
        return "\n".join(formatted)
    
    def _create_fallback_response(self, results: List[Dict[str, Any]], analysis: Dict[str, Any], original_task: str) -> str:
        """Create a basic formatted response as fallback."""
        response_parts = [f"Task: {original_task}\n"]
        
        # Add successful results
        github_repos = []
        weather_info = []
        
        for result in results:
            if result.get("success"):
                tool_result = result.get("result", {})
                if result.get("tool_name") == "github_search" and tool_result.get("success"):
                    github_repos.extend(tool_result.get("data", []))
                elif result.get("tool_name") == "weather_current" and tool_result.get("success"):
                    weather_info.append(tool_result.get("data", {}))
        
        # Show Github repos if we have any
        if github_repos:
            response_parts.append("GitHub Repositories:")
            for i, repo in enumerate(github_repos[:5], 1):
                response_parts.append(f"{i}. {repo.get('name', 'Unknown')} - {repo.get('stars', 0)} stars")
                if repo.get('description'):
                    response_parts.append(f"   {repo.get('description')}")
            response_parts.append("")
        
        # Show weather results
        if weather_info:
            response_parts.append("Weather Information:")
            for weather in weather_info:
                city = weather.get('city', 'Unknown')
                temp = weather.get('temperature', 'N/A')
                desc = weather.get('description', 'N/A')
                response_parts.append(f"- {city}: {temp}°C, {desc}")
            response_parts.append("")
        
        # Add issues if any
        if analysis.get("issues"):
            response_parts.append("Note: Some operations encountered issues:")
            for issue in analysis["issues"]:
                response_parts.append(f"- {issue}")
        
        return "\n".join(response_parts)