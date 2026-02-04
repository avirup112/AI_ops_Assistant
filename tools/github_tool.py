"""GitHub API tool for searching repositories."""
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class GitHubTool:
    """Tool for interacting with GitHub API."""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Ops-Assistant"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def search_repositories(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search GitHub repositories by query.
        
        Args:
            query: Search query string
            limit: Maximum number of repositories to return (default: 5)
            
        Returns:
            Dictionary with success status and repository data
        """
        try:
            # Construct search URL
            url = f"{self.base_url}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            }
            
            # Make API request
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            repositories = []
            for repo in data.get("items", []):
                repositories.append({
                    "name": repo["full_name"],
                    "description": repo["description"] or "No description available",
                    "stars": repo["stargazers_count"],
                    "language": repo["language"],
                    "url": repo["html_url"],
                    "updated_at": repo["updated_at"]
                })
            
            return {
                "success": True,
                "data": repositories,
                "total_count": data.get("total_count", 0),
                "message": f"Found {len(repositories)} repositories for query: {query}"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "data": [],
                "error": f"GitHub API request failed: {str(e)}",
                "message": f"Failed to search repositories for query: {query}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "error": f"Unexpected error: {str(e)}",
                "message": f"Failed to search repositories for query: {query}"
            }
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with repository information
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "data": {
                    "name": data["full_name"],
                    "description": data["description"] or "No description available",
                    "stars": data["stargazers_count"],
                    "forks": data["forks_count"],
                    "language": data["language"],
                    "url": data["html_url"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"]
                },
                "message": f"Retrieved information for {owner}/{repo}"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "data": {},
                "error": f"GitHub API request failed: {str(e)}",
                "message": f"Failed to get repository info for {owner}/{repo}"
            }