
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

try:
    from .detector import analyze_text
except ImportError:
    from detector import analyze_text


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"


app = Flask(__name__, static_folder=None)
CORS(
    app,
    resources={
        r"/analyze": {"origins": "*"},
        r"/ping": {"origins": "*"},
    },
)


@app.get("/ping")
def ping():
    return jsonify(
        {
            "status": "ok",
            "service": "bitr-ai-backend",
        }
    )


@app.post("/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()

    if not text:
        return (
            jsonify(
                {
                    "error": "Text is required.",
                    "manipulation_score": 0,
                    "authenticity_score": 0,
                    "risk_level": "Unavailable",
                    "risk_color": "gray",
                    "guidance": "Provide text to analyze.",
                    "category_scores": {},
                    "detected_tactics": {},
                    "language_detected": None,
                    "ml_score": None,
                    "hybrid_score": 0,
                }
            ),
            400,
        )

    result = analyze_text(text)
    status_code = 200 if not result.get("error") else 422
    return jsonify(result), status_code


@app.get("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:path>")
def serve_frontend_asset(path: str):
    return send_from_directory(FRONTEND_DIR, path)


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=True)
