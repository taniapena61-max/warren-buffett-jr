"""Configuration loader for wbj compute engine."""

from dataclasses import dataclass, field
from pathlib import Path
from dotenv import dotenv_values


def _find_repo_root() -> Path:
    """Derive repo_root: two parents up from wbj/ directory."""
    # wbj package is at engine/wbj/
    wbj_dir = Path(__file__).parent  # engine/wbj/
    engine_dir = wbj_dir.parent  # engine/
    repo_root = engine_dir.parent  # repo_root
    return repo_root


@dataclass(repr=False)
class Settings:
    """Warren Buffett Jr settings, never repr keys."""

    fmp_api_key: str | None = None
    finnhub_api_key: str | None = None
    fred_api_key: str | None = None
    anthropic_api_key: str | None = None
    # Charles Schwab (read-only market data, OAuth) — real-time price source.
    schwab_app_key: str | None = None
    schwab_app_secret: str | None = None
    schwab_callback_url: str = "https://127.0.0.1"
    # Gmail IMAP (solo lectura) — para leer alertas de MarketSnack.
    gmail_address: str | None = None
    gmail_app_password: str | None = None
    marketsnack_sender: str | None = None
    # Model for the qualitative judgment agent; override to cut cost (e.g.
    # "claude-haiku-4-5"). Default per the Anthropic SDK guidance.
    judge_model: str = "claude-opus-4-8"
    repo_root: Path = field(default_factory=_find_repo_root)
    cache_dir: Path = field(default_factory=lambda: _find_repo_root() / "engine" / "cache")
    reports_dir: Path = field(default_factory=lambda: _find_repo_root() / "Reportes")

    @property
    def schwab_token_path(self) -> Path:
        """Gitignored token store for Schwab OAuth tokens (under API/)."""
        return self.repo_root / "API" / "schwab_tokens.json"

    def __repr__(self) -> str:
        """Custom repr that never includes secret keys."""
        return (
            f"Settings(fmp_api_key={'*' * 8 if self.fmp_api_key else None}, "
            f"finnhub_api_key={'*' * 8 if self.finnhub_api_key else None}, "
            f"fred_api_key={'*' * 8 if self.fred_api_key else None}, "
            f"repo_root={self.repo_root}, "
            f"cache_dir={self.cache_dir}, "
            f"reports_dir={self.reports_dir})"
        )


def load_settings(env_file: Path | None = None) -> Settings:
    """Load settings from env file, with defaults.

    Args:
        env_file: Path to .env file. Defaults to <repo_root>/API/.env.

    Returns:
        Settings instance with keys from env file (or None if missing/empty).
    """
    repo_root = _find_repo_root()

    if env_file is None:
        env_file = repo_root / "API" / ".env"

    # Load env file if it exists; otherwise return defaults
    env_vars = {}
    if env_file.exists():
        env_vars = dotenv_values(env_file)

    # Map empty strings to None
    fmp_api_key = env_vars.get("FMP_API_KEY") or None
    finnhub_api_key = env_vars.get("FINNHUB_API_KEY") or None
    fred_api_key = env_vars.get("FRED_API_KEY") or None
    # ANTHROPIC_API_KEY may also come from the real environment (SDK convention).
    import os

    anthropic_api_key = (
        env_vars.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or None
    )
    judge_model = env_vars.get("JUDGE_MODEL") or "claude-opus-4-8"
    schwab_app_key = env_vars.get("SCHWAB_APP_KEY") or None
    schwab_app_secret = env_vars.get("SCHWAB_APP_SECRET") or None
    schwab_callback_url = env_vars.get("SCHWAB_CALLBACK_URL") or "https://127.0.0.1"
    gmail_address = env_vars.get("GMAIL_ADDRESS") or env_vars.get("EMAIL_TO") or None
    gmail_app_password = env_vars.get("GMAIL_APP_PASSWORD") or None
    marketsnack_sender = env_vars.get("MARKETSNACK_SENDER") or None

    return Settings(
        fmp_api_key=fmp_api_key,
        finnhub_api_key=finnhub_api_key,
        fred_api_key=fred_api_key,
        anthropic_api_key=anthropic_api_key,
        schwab_app_key=schwab_app_key,
        schwab_app_secret=schwab_app_secret,
        schwab_callback_url=schwab_callback_url,
        gmail_address=gmail_address,
        gmail_app_password=gmail_app_password,
        marketsnack_sender=marketsnack_sender,
        judge_model=judge_model,
        repo_root=repo_root,
        cache_dir=repo_root / "engine" / "cache",
        reports_dir=repo_root / "Reportes",
    )
