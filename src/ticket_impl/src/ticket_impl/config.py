"""Runtime settings for Jira Cloud + OAuth."""
import os

from pydantic import BaseModel


class Settings(BaseModel):
    """Container for environment-based configuration."""

    # Jira Cloud
    jira_cloud_id: str = os.environ["JIRA_CLOUD_ID"]
    jira_api_base: str = os.environ.get(
        "JIRA_API_BASE",
        f"https://api.atlassian.com/ex/jira/{os.environ['JIRA_CLOUD_ID']}",
    )

    # Atlassian OAuth 2.0 (3LO)
    oauth_client_id: str = os.environ["OAUTH_CLIENT_ID"]
    oauth_client_secret: str = os.environ["OAUTH_CLIENT_SECRET"]
    oauth_redirect_uri: str = os.environ["OAUTH_REDIRECT_URI"]

    # Token & mapping DB
    db_url: str = os.environ.get("DB_URL", "sqlite:///./jira_tokens.db")


settings = Settings()
