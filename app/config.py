import os


class Settings:
    """Centralized environment configuration for the app (DB, OAuth, switches)."""

    # Data backend: "file" (default) or "sql"
    DATA_BACKEND: str = os.getenv("DATA_BACKEND", "file").lower()

    # Auth backend: "local" (default) or "google"
    AUTH_BACKEND: str = os.getenv("AUTH_BACKEND", "local").lower()

    # Cloud SQL / Postgres connection
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_HOST: str = os.getenv("DB_HOST", "")  # Optional for direct TCP
    CLOUD_SQL_CONNECTION_NAME: str = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")

    # Optional local fallback (developer machine) – SQLite path
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "data/local.db")

    # Google OAuth 2.0
    OAUTH_CLIENT_ID: str = os.getenv("OAUTH_CLIENT_ID", "")
    OAUTH_CLIENT_SECRET: str = os.getenv("OAUTH_CLIENT_SECRET", "")
    OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "")
    OAUTH_SCOPES = [
        "openid",
        "email",
        "profile",
    ]


settings = Settings()


