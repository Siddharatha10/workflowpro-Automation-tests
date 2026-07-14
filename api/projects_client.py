import requests

from config import API_BASE_URL


class ProjectsClient:
    def __init__(self, token: str, tenant: str):
        self.headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": tenant}

    def create(self, name: str, description: str = "", team_members=None) -> dict:
        resp = requests.post(
            f"{API_BASE_URL}/api/v1/projects",
            headers=self.headers,
            json={"name": name, "description": description, "team_members": team_members or []},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get(self, project_id: int) -> requests.Response:
        return requests.get(
            f"{API_BASE_URL}/api/v1/projects/{project_id}",
            headers=self.headers,
            timeout=10,
        )

    def delete(self, project_id: int) -> None:
        requests.delete(
            f"{API_BASE_URL}/api/v1/projects/{project_id}",
            headers=self.headers,
            timeout=10,
        )
