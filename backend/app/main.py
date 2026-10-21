import uvicorn
from app.api.routes import app
from app.configuration.settings import settings


def main() -> None:
    uvicorn.run(
        "app.api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
