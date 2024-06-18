"""Config level module for fastapi application."""

import sys
from typing import Optional

from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    """Application configurations."""

    var_a: int = 33
    var_b: float = 22.0


class GlobalConfig(BaseSettings):
    """Global configurations."""

    # These variables will be loaded from the .env file. However, if
    # there is a shell environment variable having the same name,
    # that will take precedence.

    app_config: AppConfig = AppConfig()

    # define global variables with the Field class
    env_state: Optional[str] = Field(None)
    # environment specific variables do not need the Field class
    database_url: str
    log_level: str = "DEBUG"

    model_config = SettingsConfigDict(extra="ignore", env_file=".env")


class DevConfig(GlobalConfig):
    """Development configurations."""


class ProdConfig(GlobalConfig):
    """Production configurations."""


class FactoryConfig:
    """Returns a config instance depending on the ENV_STATE variable."""

    def __init__(self, env_state: Optional[str]):
        """Construct a FactoryConfig instance.

        Parameters
        ----------
        env_state : Optional[str]
            The environment state for the app, defaults to dev
        """
        self.env_state = env_state

    def __call__(self) -> GlobalConfig:
        """Return the appropriate config based on environment."""
        if self.env_state == "prod":
            return ProdConfig(env_prefix="PROD_")  # type: ignore [call-arg]

        return DevConfig(env_prefix="DEV_")  # type: ignore [call-arg]


def _initialize_logging() -> None:
    """Adjust the logging level if necessary."""
    level = GlobalConfig().log_level  # type: ignore [call-arg]
    if level != "DEBUG":
        logger.remove(0)
        logger.add(sys.stderr, level=level)


cfg = FactoryConfig(GlobalConfig().env_state)()  # type: ignore [call-arg]

templates = Jinja2Templates(directory="templates/")

_initialize_logging()
