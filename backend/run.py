"""AYUConnect Flask application factory and entry point."""

import os

from dotenv import load_dotenv

# Load environment variables from the project-root `.env` file.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(app.config.get("DEBUG")))