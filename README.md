# BITR 
## Binary Intelligence for Truth Reconstruction 

BITR is a light, hybrid NLP and rule-based heuristic system designed to analyze text messages, news snippets, and social media posts for psychological manipulation tactics, fake news signals, and credibility risks.

---

## Key Features

- **Multi-Vector Manipulation Detection**: Evaluates text across 5 distinct psychological manipulation tactics:
  1. **Fear Triggers**: Language designed to provoke panic or urgency.
  2. **Authority Impersonation**: Unauthorized or misleading claims of official backing (e.g., government, law enforcement, banking).
  3. **Scarcity & Urgency Pressure**: Time-bound pressure inducing hasty decision-making.
  4. **Social Proof Manipulation**: Artificial popularity claims encouraging chain shares.
  5. **Emotional Amplification**: Extreme sensation words aimed at shocking the reader.

- **Sentiment & Formatting Analysis**:
  - Leverages **VADER Sentiment Analysis** (`vaderSentiment`) to detect emotional intensity.
  - Applies **TextBlob** for basic natural language processing.
  - Implements **Credibility Penalties** for suspicious short links, excessive caps, and missing attribution.
- **RESTful Flask API**: Exposes clean JSON endpoints for automated text scoring and real-time frontend integration.
- **Interactive Radar Chart Dashboard**: Visualizes risk breakdown per category with Chart.js.

---

## System Architecture & Backend Flow

```
Input Text ──► Language Check (en) ──► Regex Tactic Matching (Fear, Urgency, Authority...)
                                           │
                                           ├─► VADER Sentiment Intensity Analysis
                                           ├─► Credibility & Formatting Checks
                                           ▼
                                Combined Hybrid Score Calculation
                                           │
                                           ▼
                                 JSON API Payload Output
```

---

## API Endpoints

### 1. `POST /analyze`
Analyzes input text and returns manipulation breakdown, authenticity scores, risk levels, and detected signals.

#### Request
```json
{
  "text": "URGENT: Your bank account will be blocked within 30 minutes unless you verify now."
}
```

#### Response (`200 OK`)
```json
{
  "manipulation_score": 57.31,
  "authenticity_score": 42.69,
  "risk_level": "Moderate Risk",
  "risk_color": "orange",
  "guidance": "Some manipulative patterns detected. Exercise caution and verify the source.",
  "category_scores": {
    "Fear Triggers": 4.55,
    "Authority Impersonation": 9.09,
    "Scarcity / Urgency": 4.55,
    "Social Proof Manipulation": 0.0,
    "Emotional Amplification": 0.0,
    "Sentiment Intensity": 1.11,
    "Credibility Penalty": 2.0
  },
  "detected_tactics": {
    "Fear Triggers": ["blocked"],
    "Authority Impersonation": ["cyber cell"],
    "Scarcity / Urgency": ["urgent"],
    "Social Proof Manipulation": [],
    "Emotional Amplification": []
  },
  "language_detected": "en",
  "hybrid_score": 57.31
}
```

### 2. `GET /ping`
Health check endpoint verifying backend service state.

---

## Setup & Local Installation

### Prerequisites
- Python 3.9+
- `pip3`

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/BITR.git
cd BITR-AI
pip install -r requirements.txt
```

### 2. Running the Backend
Start the Flask development server:
```bash
python backend/app.py
```
By default, the server runs on `http://127.0.0.1:5000`. You can customize host and port using environment variables:
```bash
HOST=0.0.0.0 PORT=8080 python backend/app.py
```

### 3. Accessing the Dashboard
Open `http://127.0.0.1:5000/` in your browser to view and interact with the web dashboard.

---

## License & Usage
Developed for research and prototype demonstration purposes.


## Authors & Credits
- **[J-Officia1](https://github.com/J-Officia1)**: Backend - Architecture design, Flask REST API, NLP manipulation scoring engine, VADER integration.
- **[CyberX-34](https://github.com/CyberX-34)**: Frontend — Dashboard UI layout, Chart.js radar integration, responsive styling.