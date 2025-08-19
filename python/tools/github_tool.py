from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from dataclasses import dataclass
import json
import aiohttp
from typing import Optional, Dict, Any, List
import base64
import urllib.parse


@dataclass
class GitHubTool(Tool):
    """
    GitHub integration tool for Pareng Boyong
    Provides access to GitHub API for repository management, issues, PRs, and more
    """
    
    async def execute(self, **kwargs):
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "").lower()
        api_key = self.args.get("api_key", "")
        
        try:
            if operation == "list_repos":
                result = await self.list_repositories(
                    api_key,
                    self.args.get("org"),
                    self.args.get("user"),
                    self.args.get("type", "all"),
                    self.args.get("sort", "updated"),
                    self.args.get("per_page", 30)
                )
            elif operation == "get_repo":
                result = await self.get_repository(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo")
                )
            elif operation == "create_repo":
                result = await self.create_repository(
                    api_key,
                    self.args.get("name"),
                    self.args.get("description"),
                    self.args.get("private", False),
                    self.args.get("auto_init", True)
                )
            elif operation == "list_issues":
                result = await self.list_issues(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo"),
                    self.args.get("state", "open"),
                    self.args.get("labels"),
                    self.args.get("assignee")
                )
            elif operation == "create_issue":
                result = await self.create_issue(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo"),
                    self.args.get("title"),
                    self.args.get("body"),
                    self.args.get("labels"),
                    self.args.get("assignees")
                )
            elif operation == "list_prs":
                result = await self.list_pull_requests(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo"),
                    self.args.get("state", "open"),
                    self.args.get("sort", "created"),
                    self.args.get("direction", "desc")
                )
            elif operation == "create_pr":
                result = await self.create_pull_request(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo"),
                    self.args.get("title"),
                    self.args.get("head"),
                    self.args.get("base"),
                    self.args.get("body")
                )
            elif operation == "get_file":
                result = await self.get_file_content(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo"),
                    self.args.get("path"),
                    self.args.get("ref")
                )
            elif operation == "create_file":
                result = await self.create_or_update_file(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo"),
                    self.args.get("path"),
                    self.args.get("content"),
                    self.args.get("message"),
                    self.args.get("branch"),
                    self.args.get("sha")
                )
            elif operation == "search":
                result = await self.search_github(
                    api_key,
                    self.args.get("query"),
                    self.args.get("type", "repositories"),
                    self.args.get("sort"),
                    self.args.get("order", "desc"),
                    self.args.get("per_page", 30)
                )
            elif operation == "list_branches":
                result = await self.list_branches(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo")
                )
            elif operation == "create_branch":
                result = await self.create_branch(
                    api_key,
                    self.args.get("owner"),
                    self.args.get("repo"),
                    self.args.get("branch"),
                    self.args.get("from_branch", "main")
                )
            elif operation == "get_user":
                result = await self.get_user_info(
                    api_key,
                    self.args.get("username")
                )
            else:
                result = {
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "list_repos", "get_repo", "create_repo",
                        "list_issues", "create_issue",
                        "list_prs", "create_pr",
                        "get_file", "create_file",
                        "search", "list_branches", "create_branch",
                        "get_user"
                    ]
                }
                
            return Response(
                message=json.dumps(result, indent=2),
                break_loop=False
            )
            
        except Exception as e:
            PrintStyle.error(f"GitHub operation failed: {str(e)}")
            return Response(
                message=f"Error: {str(e)}",
                break_loop=False
            )
    
    async def _make_request(self, method: str, url: str, api_key: str, 
                          data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to GitHub API"""
        headers = {
            "Authorization": f"token {api_key}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Pareng-Boyong-AI"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, 
                json=data, params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                result = await response.json()
                if response.status >= 400:
                    raise Exception(f"GitHub API error: {result.get('message', 'Unknown error')}")
                return result
    
    async def list_repositories(self, api_key: str, org: Optional[str] = None, 
                               user: Optional[str] = None, type: str = "all", 
                               sort: str = "updated", per_page: int = 30) -> Dict:
        """List repositories for authenticated user, org, or specific user"""
        if org:
            url = f"https://api.github.com/orgs/{org}/repos"
        elif user:
            url = f"https://api.github.com/users/{user}/repos"
        else:
            url = "https://api.github.com/user/repos"
        
        params = {
            "type": type,
            "sort": sort,
            "per_page": per_page
        }
        
        repos = await self._make_request("GET", url, api_key, params=params)
        
        # Simplify response
        return {
            "count": len(repos),
            "repositories": [
                {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "private": repo["private"],
                    "url": repo["html_url"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "updated": repo["updated_at"]
                }
                for repo in repos
            ]
        }
    
    async def get_repository(self, api_key: str, owner: str, repo: str) -> Dict:
        """Get detailed information about a specific repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        return await self._make_request("GET", url, api_key)
    
    async def create_repository(self, api_key: str, name: str, description: str = "",
                               private: bool = False, auto_init: bool = True) -> Dict:
        """Create a new repository"""
        url = "https://api.github.com/user/repos"
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init
        }
        return await self._make_request("POST", url, api_key, data=data)
    
    async def list_issues(self, api_key: str, owner: str, repo: str, 
                         state: str = "open", labels: Optional[str] = None,
                         assignee: Optional[str] = None) -> Dict:
        """List issues for a repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {"state": state}
        if labels:
            params["labels"] = labels
        if assignee:
            params["assignee"] = assignee
            
        issues = await self._make_request("GET", url, api_key, params=params)
        
        return {
            "count": len(issues),
            "issues": [
                {
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "author": issue["user"]["login"],
                    "labels": [label["name"] for label in issue["labels"]],
                    "created": issue["created_at"],
                    "url": issue["html_url"]
                }
                for issue in issues
            ]
        }
    
    async def create_issue(self, api_key: str, owner: str, repo: str,
                          title: str, body: str = "", labels: Optional[List[str]] = None,
                          assignees: Optional[List[str]] = None) -> Dict:
        """Create a new issue"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        data = {
            "title": title,
            "body": body
        }
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
            
        return await self._make_request("POST", url, api_key, data=data)
    
    async def list_pull_requests(self, api_key: str, owner: str, repo: str,
                                state: str = "open", sort: str = "created",
                                direction: str = "desc") -> Dict:
        """List pull requests for a repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "sort": sort,
            "direction": direction
        }
        
        prs = await self._make_request("GET", url, api_key, params=params)
        
        return {
            "count": len(prs),
            "pull_requests": [
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "state": pr["state"],
                    "author": pr["user"]["login"],
                    "created": pr["created_at"],
                    "head": pr["head"]["ref"],
                    "base": pr["base"]["ref"],
                    "url": pr["html_url"]
                }
                for pr in prs
            ]
        }
    
    async def create_pull_request(self, api_key: str, owner: str, repo: str,
                                 title: str, head: str, base: str, body: str = "") -> Dict:
        """Create a new pull request"""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        return await self._make_request("POST", url, api_key, data=data)
    
    async def get_file_content(self, api_key: str, owner: str, repo: str,
                              path: str, ref: Optional[str] = None) -> Dict:
        """Get file content from repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        params = {}
        if ref:
            params["ref"] = ref
            
        result = await self._make_request("GET", url, api_key, params=params)
        
        # Decode content if it's a file
        if result.get("type") == "file" and result.get("content"):
            content = base64.b64decode(result["content"]).decode("utf-8")
            result["decoded_content"] = content
            
        return result
    
    async def create_or_update_file(self, api_key: str, owner: str, repo: str,
                                   path: str, content: str, message: str,
                                   branch: Optional[str] = None, sha: Optional[str] = None) -> Dict:
        """Create or update a file in repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        # Encode content to base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        data = {
            "message": message,
            "content": encoded_content
        }
        if branch:
            data["branch"] = branch
        if sha:
            data["sha"] = sha
            
        return await self._make_request("PUT", url, api_key, data=data)
    
    async def search_github(self, api_key: str, query: str, type: str = "repositories",
                           sort: Optional[str] = None, order: str = "desc",
                           per_page: int = 30) -> Dict:
        """Search GitHub (repositories, code, issues, users)"""
        type_map = {
            "repositories": "repositories",
            "code": "code",
            "issues": "issues",
            "users": "users",
            "commits": "commits"
        }
        
        if type not in type_map:
            raise ValueError(f"Invalid search type. Must be one of: {list(type_map.keys())}")
            
        url = f"https://api.github.com/search/{type_map[type]}"
        params = {
            "q": query,
            "order": order,
            "per_page": per_page
        }
        if sort:
            params["sort"] = sort
            
        return await self._make_request("GET", url, api_key, params=params)
    
    async def list_branches(self, api_key: str, owner: str, repo: str) -> Dict:
        """List all branches in a repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/branches"
        branches = await self._make_request("GET", url, api_key)
        
        return {
            "count": len(branches),
            "branches": [
                {
                    "name": branch["name"],
                    "protected": branch["protected"],
                    "commit_sha": branch["commit"]["sha"]
                }
                for branch in branches
            ]
        }
    
    async def create_branch(self, api_key: str, owner: str, repo: str,
                           branch: str, from_branch: str = "main") -> Dict:
        """Create a new branch from existing branch"""
        # First get the SHA of the source branch
        ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{from_branch}"
        ref_data = await self._make_request("GET", ref_url, api_key)
        sha = ref_data["object"]["sha"]
        
        # Create new branch
        create_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch}",
            "sha": sha
        }
        return await self._make_request("POST", create_url, api_key, data=data)
    
    async def get_user_info(self, api_key: str, username: Optional[str] = None) -> Dict:
        """Get user information (authenticated user if no username provided)"""
        if username:
            url = f"https://api.github.com/users/{username}"
        else:
            url = "https://api.github.com/user"
            
        return await self._make_request("GET", url, api_key)