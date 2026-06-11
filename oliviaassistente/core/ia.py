from google import genai
from dotenv import load_dotenv
import os

# Load environment variables from .env at project root
load_dotenv(dotenv_path=".env")

API_GEMINI = os.getenv("API_GEMINI")
if not API_GEMINI:
    raise RuntimeError(
        "Environment variable API_GEMINI not found. Add API_GEMINI=your_key to a .env file."
    )

client = genai.Client(API_GEMINI)


def explain_ai_short() -> str:
    """Return a short explanation of how AI works using the Gemini model."""
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Explain how AI works in a few words",
    )
    return getattr(response, "text", str(response))


if __name__ == "__main__":
    print(explain_ai_short())