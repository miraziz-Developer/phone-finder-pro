import uvicorn

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.presentation.api.app import create_api_app


def run_api() -> None:
    setup_logging()
    settings = get_settings()
    app = create_api_app(settings)
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run_api()
