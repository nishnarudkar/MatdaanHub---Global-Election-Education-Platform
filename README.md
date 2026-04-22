# MatdaanHub - Global Election Education Platform

Making democracy understandable with interactive timelines, voting guides, and AI-powered Q&A.

## Project Overview

MatdaanHub is a production-grade educational platform featuring:
- 5 countries: India, USA, UK, EU, Brazil
- Interactive election timelines
- Step-by-step voting guides
- Election system comparison view
- Country quiz mode
- AI chat powered by Google Gemini
- Translation support powered by Google Cloud Translate
- Accessibility-first frontend design
- Cloud Run deployment with CI/CD

## Tech Stack

- Backend: Flask 3.1.0 (Python 3.11+)
- AI: Google Gemini 1.5 Flash
- Translation: Google Cloud Translate v2
- Storage: Firebase Admin / Firestore
- Grounding: Vertex AI (service wiring included)
- Deployment: Google Cloud Run
- Testing: pytest

## Project Structure

```text
matdaanhub/
  app.py
  config.py
  requirements.txt
  Dockerfile
  cloudbuild.yaml
  data/
    elections.json
    glossary.json
  routes/
    health.py
    elections.py
    chat.py
    translate.py
  services/
    gemini_service.py
    translate_service.py
    firebase_service.py
    vertex_service.py
  templates/
    index.html
  static/
    css/style.css
    js/app.js
    js/chat.js
    js/timeline.js
    js/translate.js
  tests/
    test_routes.py
    test_services.py
    test_security.py
    test_accessibility.py
    test_data.py
```

## API Endpoints

- GET /health
- GET /api/elections
- GET /api/elections/<country_id>
- GET /api/elections/<country_id>/timeline
- GET /api/elections/<country_id>/voting-steps
- GET /api/glossary
- GET /api/glossary/<term>
- POST /api/chat
- POST /api/chat/grounded
- GET /api/chat/history/<session_id>
- POST /api/translate
- POST /api/translate/detect
- GET /api/languages

## Security

- Input sanitization with bleach
- Rate limiting with Flask-Limiter
- Security headers including CSP, X-Frame-Options, and X-Content-Type-Options
- Configurable limiter backend via RATELIMIT_STORAGE_URI
  - Local default: memory://
  - Production recommendation: Redis URI

## Accessibility

- ARIA landmarks and semantic structure
- Keyboard-friendly interaction patterns
- Visible focus states
- Skip link support
- High contrast editorial theme

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Current status:
- 299 tests passing

## Deployment

Deployed Cloud Run service URL:
- https://matdaanhub-253750832620.us-central1.run.app

Health endpoint:
- https://matdaanhub-253750832620.us-central1.run.app/health

Deploy command:

```bash
gcloud run deploy matdaanhub \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

## Local Setup

```bash
pip install -r requirements.txt
python app.py
```

## Environment Variables

- GEMINI_API_KEY
- GOOGLE_CLOUD_PROJECT
- GOOGLE_TRANSLATE_ENABLED
- FIREBASE_ENABLED
- FIREBASE_CREDENTIALS_PATH
- VERTEX_GROUNDING_ENABLED
- RATELIMIT_STORAGE_URI
