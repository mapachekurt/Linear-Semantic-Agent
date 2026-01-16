"""
Linear MCP Server client via Composio.
Implements authenticated access to Linear API.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import settings
from src.config.constants import LINEAR_MAX_RETRIES, LINEAR_TIMEOUT_SECONDS
from src.models.project import LinearProject, LinearIssue
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LinearMCPError(Exception):
    """Base exception for Linear MCP errors."""
    pass


class LinearAuthError(LinearMCPError):
    """Authentication error."""
    pass


class LinearAPIError(LinearMCPError):
    """API error."""
    pass


class LinearMCPClient:
    """Client for Linear MCP Server via Composio."""

    def __init__(self):
        """Initialize Linear MCP client."""
        self.mcp_url = settings.linear_mcp_url
        self.api_key = settings.linear_api_key
        self.workspace_id = settings.linear_workspace_id

        if not self.api_key:
            logger.warning("Linear API key not configured")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        logger.info("Linear MCP client initialized")

    @retry(
        stop=stop_after_attempt(LINEAR_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Linear API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data

        Raises:
            LinearAPIError: On API errors
        """
        url = f"{self.mcp_url}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(timeout=LINEAR_TIMEOUT_SECONDS) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=data)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=self.headers, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise LinearAuthError(f"Authentication failed: {e}")
            else:
                raise LinearAPIError(f"API error: {e}")
        except Exception as e:
            logger.error("Request failed", error=str(e), exc_info=True)
            raise LinearAPIError(f"Request failed: {e}")

    async def list_projects(self) -> List[LinearProject]:
        """
        Fetch all projects from Linear.

        Returns:
            List of Linear projects
        """
        logger.info("Fetching Linear projects")

        try:
            # Note: This is a simplified implementation
            # In production, use the actual Linear GraphQL API
            response = await self._make_request("GET", "/projects")

            projects = []
            for item in response.get("data", []):
                project = LinearProject(
                    id=item.get("id"),
                    name=item.get("name"),
                    description=item.get("description"),
                    team=item.get("team", {}).get("name"),
                    status=item.get("state"),
                    lead=item.get("lead"),
                    created_at=self._parse_datetime(item.get("createdAt")),
                    updated_at=self._parse_datetime(item.get("updatedAt")),
                    raw_data=item
                )
                projects.append(project)

            logger.info("Fetched projects", count=len(projects))
            return projects

        except Exception as e:
            logger.error("Failed to fetch projects", error=str(e), exc_info=True)
            raise

    async def get_project(self, project_id: str) -> LinearProject:
        """
        Get detailed project information.

        Args:
            project_id: Linear project ID

        Returns:
            Linear project
        """
        logger.info("Fetching project", project_id=project_id)

        response = await self._make_request("GET", f"/projects/{project_id}")

        item = response.get("data", {})
        project = LinearProject(
            id=item.get("id"),
            name=item.get("name"),
            description=item.get("description"),
            team=item.get("team", {}).get("name"),
            status=item.get("state"),
            lead=item.get("lead"),
            created_at=self._parse_datetime(item.get("createdAt")),
            updated_at=self._parse_datetime(item.get("updatedAt")),
            raw_data=item
        )

        return project

    async def list_issues(self, project_id: Optional[str] = None) -> List[LinearIssue]:
        """
        List issues, optionally filtered by project.

        Args:
            project_id: Optional project ID filter

        Returns:
            List of Linear issues
        """
        logger.info("Fetching issues", project_id=project_id)

        params = {}
        if project_id:
            params["projectId"] = project_id

        response = await self._make_request("GET", "/issues", data=params)

        issues = []
        for item in response.get("data", []):
            issue = LinearIssue(
                id=item.get("identifier"),
                title=item.get("title"),
                description=item.get("description"),
                status=item.get("state", {}).get("name"),
                project_id=item.get("project", {}).get("id"),
                priority=item.get("priority"),
                created_at=self._parse_datetime(item.get("createdAt")),
                updated_at=self._parse_datetime(item.get("updatedAt")),
                raw_data=item
            )
            issues.append(issue)

        logger.info("Fetched issues", count=len(issues))
        return issues

    async def search_issues(self, query: str) -> List[LinearIssue]:
        """
        Full-text search across issues.

        Args:
            query: Search query

        Returns:
            List of matching issues
        """
        logger.info("Searching issues", query=query)

        response = await self._make_request("GET", "/issues/search", data={"query": query})

        issues = []
        for item in response.get("data", []):
            issue = LinearIssue(
                id=item.get("identifier"),
                title=item.get("title"),
                description=item.get("description"),
                status=item.get("state", {}).get("name"),
                project_id=item.get("project", {}).get("id"),
                priority=item.get("priority"),
                created_at=self._parse_datetime(item.get("createdAt")),
                updated_at=self._parse_datetime(item.get("updatedAt")),
                raw_data=item
            )
            issues.append(issue)

        logger.info("Search results", count=len(issues))
        return issues

    async def get_issue_details(self, issue_id: str) -> LinearIssue:
        """
        Get full issue details including comments, attachments.

        Args:
            issue_id: Linear issue ID

        Returns:
            Linear issue
        """
        logger.info("Fetching issue details", issue_id=issue_id)

        response = await self._make_request("GET", f"/issues/{issue_id}")

        item = response.get("data", {})
        issue = LinearIssue(
            id=item.get("identifier"),
            title=item.get("title"),
            description=item.get("description"),
            status=item.get("state", {}).get("name"),
            project_id=item.get("project", {}).get("id"),
            priority=item.get("priority"),
            created_at=self._parse_datetime(item.get("createdAt")),
            updated_at=self._parse_datetime(item.get("updatedAt")),
            raw_data=item
        )

        return issue

    async def create_issue(
        self,
        project_id: str,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new Linear issue.

        Args:
            project_id: Project ID
            title: Issue title
            description: Issue description
            metadata: Additional metadata

        Returns:
            Created issue ID
        """
        logger.info("Creating issue", project_id=project_id, title=title)

        data = {
            "projectId": project_id,
            "title": title,
            "description": description,
            **(metadata or {})
        }

        response = await self._make_request("POST", "/issues", data=data)

        issue_id = response.get("data", {}).get("id")
        logger.info("Created issue", issue_id=issue_id)

        return issue_id

    async def update_issue(self, issue_id: str, data: Dict[str, Any]) -> None:
        """
        Update existing issue.

        Args:
            issue_id: Issue ID
            data: Update data
        """
        logger.info("Updating issue", issue_id=issue_id)

        await self._make_request("PUT", f"/issues/{issue_id}", data=data)

        logger.info("Updated issue", issue_id=issue_id)

    async def link_issues(
        self,
        source_id: str,
        target_id: str,
        relationship: str
    ) -> None:
        """
        Create relationship between issues.

        Args:
            source_id: Source issue ID
            target_id: Target issue ID
            relationship: Relationship type (duplicate_of, relates_to, blocks, depends_on)
        """
        logger.info(
            "Linking issues",
            source=source_id,
            target=target_id,
            relationship=relationship
        )

        data = {
            "sourceId": source_id,
            "targetId": target_id,
            "type": relationship
        }

        await self._make_request("POST", "/issue-relations", data=data)

        logger.info("Linked issues")

    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return None
