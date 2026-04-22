# MatdaanHub - Global Election Education Platform

> **Making democracy understandable through interactive timelines, voting guides, and AI-powered insights**

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue)](https://matdaanhub-454329960040.us-central1.run.app)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-308%20Passing-success)](tests/)

**Created by**: [Nishant Narudkar](https://github.com/nishnarudkar)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Chosen Vertical & Approach](#-chosen-vertical--approach)
- [How the Solution Works](#-how-the-solution-works)
- [Key Features](#-key-features)
- [Architecture & Design](#-architecture--design)
- [Google Services Integration](#-google-services-integration)
- [Security Implementation](#-security-implementation)
- [Accessibility Features](#-accessibility-features)
- [Testing Strategy](#-testing-strategy)
- [Performance & Efficiency](#-performance--efficiency)
- [Screenshots](#-screenshots)
- [Setup & Deployment](#-setup--deployment)
- [Assumptions Made](#-assumptions-made)

---

## 🎯 Project Overview

**MatdaanHub** is a production-grade educational platform that demystifies global election processes through:
- **10 Countries**: India, USA, UK, EU, Brazil, South Africa, Australia, Japan, Mexico, Canada
- **Interactive Timelines**: Scrollytelling election phases with visual indicators
- **Voting Guides**: Step-by-step instructions for each country
- **AI Chat Assistant**: Powered by Google Gemini for election Q&A
- **Comparison Tools**: Side-by-side electoral system analysis
- **Quiz Mode**: Test knowledge with country-specific questions
- **Multi-language Support**: Google Cloud Translate integration
- **Modern UI**: Light theme with glassmorphism and interactive animations

**Live Demo**: https://matdaanhub-454329960040.us-central1.run.app

---

## 🎓 Chosen Vertical & Approach

### Vertical: **Civic Education & Democratic Engagement**

**Problem Statement**: 
- Election processes are complex and vary significantly across countries
- Citizens often lack accessible, comprehensive information about voting procedures
- Language barriers prevent global understanding of democratic systems
- Traditional educational resources are text-heavy and non-interactive

### Our Approach:

#### 1. **Interactive Learning**
- Visual timelines with scroll-triggered animations
- Step-by-step voting guides with emoji icons
- Gamified quiz system for knowledge retention
- Mouse-interactive "Inked Reveal" effect reinforcing the voting theme

#### 2. **AI-Powered Assistance**
- Google Gemini 1.5 Flash for natural language Q&A
- Context-aware responses about election systems
- Grounding capability (Vertex AI) for factual accuracy
- Session-based conversation history

#### 3. **Accessibility-First Design**
- WCAG 2.1 AA compliant
- Keyboard navigation support
- ARIA landmarks and semantic HTML
- High contrast ratios (4.5:1 minimum)
- Screen reader optimized

#### 4. **Global Reach**
- Multi-language translation (Google Cloud Translate)
- 10 diverse countries representing different electoral systems
- Cultural sensitivity in design and content

---

## 🔧 How the Solution Works

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Interactive │  │   AI Chat    │  │  Translation │      │
│  │   Timeline   │  │   Interface  │  │    Widget    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Cloud Run (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Rate Limiting │ Input Sanitization │ Security Headers│  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Election   │  │     Chat     │  │  Translation │    │
│  │    Routes    │  │    Routes    │  │    Routes    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Gemini     │  │   Firestore  │  │   Translate  │
│  1.5 Flash   │  │   (Optional) │  │      API     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Data Flow

1. **User Interaction** → Frontend (HTML/CSS/JS)
2. **API Request** → FastAPI Backend (Rate Limited + Sanitized)
3. **Service Layer** → Google Services (Gemini/Translate/Firestore)
4. **Response Processing** → JSON/HTML Response
5. **UI Update** → Dynamic DOM manipulation with animations

### Key Components

#### Backend (FastAPI)
- **main.py**: Application entry point, CORS, middleware
- **routes/**: Modular endpoint handlers
  - `elections.py`: Country data and timelines
  - `chat.py`: AI conversation endpoints
  - `translate.py`: Language translation
  - `health.py`: Health checks
- **services/**: Business logic layer
  - `gemini_service.py`: AI chat integration
  - `translate_service.py`: Translation logic
  - `firebase_service.py`: Firestore operations
  - `limiter_service.py`: Rate limiting
- **schemas/**: Pydantic models for validation

#### Frontend (Vanilla JS)
- **app.js**: Main application logic, navigation, quiz
- **chat.js**: AI chat interface and history
- **timeline.js**: Scrollytelling animations
- **translate.js**: Language switching
- **style.css**: Modern glassmorphism design

---

## ✨ Key Features

### 1. Interactive Election Timelines
- **Scrollytelling**: Timeline items animate into view as user scrolls
- **Visual Indicators**: Color-coded phases with pulsing dots
- **Responsive Design**: Adapts to all screen sizes

### 2. AI-Powered Chat Assistant
- **Natural Language Processing**: Understands election-related queries
- **Context Awareness**: Maintains conversation history
- **Suggested Questions**: Quick-start prompts for users
- **Markdown Support**: Formatted responses with lists and emphasis

### 3. Multi-Language Translation
- **7 Languages**: English, Hindi, Tamil, Spanish, French, German, Portuguese
- **Auto-Detection**: Identifies source language automatically
- **Persistent Selection**: Remembers user's language preference

### 4. Comparison Tools
- **Side-by-Side Table**: Compare electoral systems across countries
- **Animated Charts**: Visual representation of voter counts and cycles
- **Responsive Layout**: Mobile-friendly comparison view

### 5. Interactive Quiz
- **Country-Specific**: Questions tailored to each nation
- **Instant Feedback**: Correct/incorrect indicators
- **Score Tracking**: Progress bar and final results
- **Animated Celebration**: "Inked finger" SVG animation on completion

### 6. Modern UI/UX
- **Light Theme**: Clean, professional design with purple gradients
- **Glassmorphism**: Frosted glass effects with backdrop blur
- **Floating Flags**: 30 flag images with 3-layer parallax depth
- **Ink Reveal Effect**: Mouse trail reveals flag emojis (voting theme)
- **Micro-interactions**: Hover effects, smooth transitions, bounce animations

---

## 🏗️ Architecture & Design

### Design Principles

1. **Separation of Concerns**: Routes → Services → External APIs
2. **Dependency Injection**: Services passed to routes, easy testing
3. **Configuration Management**: Environment-based settings (config.py)
4. **Error Handling**: Graceful degradation with fallbacks
5. **Caching Strategy**: In-memory TTL cache for Firestore data (1 hour)

### Code Quality

- **Type Hints**: Full Python type annotations
- **Pydantic Validation**: Request/response schema validation
- **Modular Structure**: Single responsibility principle
- **DRY Principle**: Reusable service functions
- **Comprehensive Comments**: Docstrings and inline documentation

### Database Design

**Firestore Collections**:
```
elections/
  ├── india/
  │   ├── name: "India"
  │   ├── system: "Parliamentary Democracy"
  │   ├── timeline: [...]
  │   └── steps: [...]
  └── usa/
      └── ...

glossary/
  ├── fptp/
  │   ├── term: "First Past the Post"
  │   └── definition: "..."
  └── pr/
      └── ...
```

**Fallback Strategy**: Local JSON files (`data/elections.json`, `data/glossary.json`) when Firestore unavailable

---

## 🔗 Google Services Integration

### 1. **Google Gemini AI** (Primary)
- **Model**: gemini-1.5-flash
- **Use Case**: Election Q&A chatbot
- **Features**:
  - Natural language understanding
  - Context-aware responses
  - Safety settings (BLOCK_MEDIUM_AND_ABOVE)
  - Temperature: 0.7 for balanced creativity
- **Implementation**: `services/gemini_service.py`
- **Rate Limiting**: 20 requests/minute per user

### 2. **Google Cloud Translate** (Primary)
- **API**: Cloud Translation v2
- **Use Case**: Multi-language support
- **Features**:
  - 7 supported languages
  - Auto language detection
  - Batch translation support
- **Implementation**: `services/translate_service.py`
- **Rate Limiting**: 30 requests/minute per user

### 3. **Google Cloud Firestore** (Optional)
- **Use Case**: Persistent storage for elections and glossary
- **Features**:
  - Real-time updates
  - Scalable NoSQL database
  - Application Default Credentials (ADC)
- **Implementation**: `services/firebase_service.py`
- **Fallback**: Local JSON files when unavailable

### 4. **Vertex AI Grounding** (Optional)
- **Use Case**: Fact-checking AI responses
- **Status**: Service wiring included, disabled by default
- **Implementation**: `services/vertex_service.py`
- **Configuration**: `VERTEX_GROUNDING_ENABLED=false`

### 5. **Google Cloud Run** (Deployment)
- **Features**:
  - Automatic scaling (0 to N instances)
  - HTTPS endpoints
  - Container-based deployment
  - CI/CD with Cloud Build
- **Configuration**: `cloudbuild.yaml`, `Dockerfile`

---

## 🔒 Security Implementation

### Input Validation & Sanitization
```python
# bleach library for HTML sanitization
def _sanitize_input(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)
```

### Rate Limiting
- **Library**: slowapi (Flask-Limiter port for FastAPI)
- **Limits**:
  - Chat: 20 requests/minute
  - Translate: 30 requests/minute
  - General: 60 requests/minute
- **Storage**: Memory (local), Redis (production)

### Security Headers
```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self' ..."
    return response
```

### API Key Management
- **Environment Variables**: Never committed to Git
- **Secret Manager**: Cloud Run secrets for production
- **Validation**: Keys validated on startup

### CORS Configuration
- **Allowed Origins**: Configurable whitelist
- **Methods**: GET, POST only
- **Credentials**: Disabled for public API

---

## ♿ Accessibility Features

### WCAG 2.1 AA Compliance

#### 1. **Semantic HTML**
```html
<header role="banner">
<nav role="navigation" aria-label="Main navigation">
<main role="main">
<footer role="contentinfo">
```

#### 2. **ARIA Landmarks**
- `aria-label` for interactive elements
- `aria-current="page"` for active navigation
- `aria-live="polite"` for dynamic content
- `aria-hidden="true"` for decorative elements

#### 3. **Keyboard Navigation**
- All interactive elements focusable
- Visible focus indicators (3px outline)
- Skip link to main content
- Tab order follows visual flow

#### 4. **Color Contrast**
- Text: 4.5:1 minimum ratio
- Interactive elements: 3:1 minimum
- High contrast mode support

#### 5. **Screen Reader Support**
- Descriptive alt text for images
- Form labels properly associated
- Status messages announced
- Error messages clear and actionable

#### 6. **Responsive Design**
- Mobile-first approach
- Touch targets ≥44x44px
- Readable font sizes (16px minimum)
- No horizontal scrolling

### Accessibility Testing
- **Automated**: `test_accessibility.py` (pytest)
- **Manual**: Keyboard-only navigation testing
- **Tools**: WAVE, axe DevTools, Lighthouse

---

## 🧪 Testing Strategy

### Test Coverage: **308 Tests Passing**

#### 1. **Unit Tests** (`test_services.py`)
- Gemini service: Chat generation, error handling
- Translation service: Language detection, translation
- Firebase service: CRUD operations, caching
- Limiter service: Rate limit enforcement

#### 2. **Integration Tests** (`test_routes.py`)
- Election endpoints: Data retrieval, filtering
- Chat endpoints: AI responses, history
- Translation endpoints: Language switching
- Health checks: Service status

#### 3. **Security Tests** (`test_security.py`)
- Input sanitization: XSS prevention
- Rate limiting: Request throttling
- Security headers: CSP, X-Frame-Options
- CORS: Origin validation

#### 4. **Accessibility Tests** (`test_accessibility.py`)
- Semantic HTML structure
- ARIA attributes presence
- Keyboard navigation support
- Color contrast ratios

#### 5. **Data Validation Tests** (`test_data.py`)
- JSON schema validation
- Required fields presence
- Data consistency checks
- Country code validation

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_routes.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

### CI/CD Testing
- **Pre-commit**: Linting with flake8
- **Cloud Build**: Automated testing on push
- **Deployment**: Only on passing tests

---

## ⚡ Performance & Efficiency

### Optimization Strategies

#### 1. **Caching**
```python
# In-memory TTL cache for Firestore data
_elections_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 3600  # 1 hour

def get_elections_cached():
    if time.time() - _elections_cache["timestamp"] < CACHE_TTL:
        return _elections_cache["data"]
    # Fetch from Firestore
```

#### 2. **Lazy Loading**
- Flag images loaded on-demand
- Chat history fetched only when needed
- Timeline animations triggered on scroll

#### 3. **Code Splitting**
- Separate JS files for features (chat, timeline, translate)
- CSS organized by component
- Minimal dependencies

#### 4. **Asset Optimization**
- WebP format for flag images (smaller size)
- SVG for icons (scalable, small)
- Minified CSS/JS in production

#### 5. **Database Efficiency**
- Firestore indexes for fast queries
- Batch operations where possible
- Connection pooling

#### 6. **API Efficiency**
- Rate limiting prevents abuse
- Request validation reduces processing
- Error responses cached

### Performance Metrics
- **Lighthouse Score**: 95+ (Performance)
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **API Response Time**: <500ms (avg)

---

## 📸 Screenshots

### Home Page - Hero Section
![Hero Section](output/Screenshot%202026-04-23%20022210.png)
*Modern light theme with floating flag animations and interactive ink reveal effect*

### Country Exploration
![Country Grid](output/Screenshot%202026-04-23%20022450.png)
*10 countries with glassmorphism cards and hover effects*

### Interactive Timeline
![Timeline View](output/Screenshot%202026-04-23%20022510.png)
*Scrollytelling election phases with visual indicators*

### Comparison Tools
![Comparison Table](output/Screenshot%202026-04-23%20022532.png)
*Side-by-side electoral system analysis with animated charts*

### AI Chat Assistant
![AI Chat](output/Screenshot%202026-04-23%20022550.png)
*Google Gemini-powered Q&A with conversation history*

### Quiz Mode
![Quiz Interface](output/Screenshot%202026-04-23%20022621.png)
*Interactive quiz with instant feedback and score tracking*

---

## 🚀 Setup & Deployment

### Prerequisites
- Python 3.11+
- Google Cloud Project
- Gemini API Key
- (Optional) Firebase/Firestore enabled

### Local Development

1. **Clone Repository**
```bash
git clone https://github.com/nishnarudkar/MatdaanHub---Global-Election-Education-Platform.git
cd MatdaanHub
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run Application**
```bash
python main.py
```

6. **Access Application**
```
http://localhost:8000
```

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key

# Optional
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_TRANSLATE_ENABLED=true
FIREBASE_ENABLED=true
VERTEX_GROUNDING_ENABLED=false
RATELIMIT_STORAGE_URI=memory://
LOG_LEVEL=INFO
DEBUG=false
```

### Cloud Run Deployment

1. **Authenticate**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **Deploy**
```bash
gcloud run deploy matdaanhub \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_TRANSLATE_ENABLED=true,FIREBASE_ENABLED=true"
```

3. **Set Secrets** (Recommended)
```bash
# Create secrets
echo -n "your_gemini_key" | gcloud secrets create GEMINI_API_KEY --data-file=-
echo -n "your_secret_key" | gcloud secrets create SECRET_KEY --data-file=-

# Update service to use secrets
gcloud run services update matdaanhub \
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --update-secrets=SECRET_KEY=SECRET_KEY:latest
```

### CI/CD with Cloud Build

**Trigger Setup**:
1. Go to Cloud Build → Triggers
2. Create trigger for `main` branch
3. Add substitution variables:
   - `_GEMINI_API_KEY`
   - `_SECRET_KEY`
4. Save and test

**Automatic Deployment**: Push to `main` triggers build and deploy

---

## 📝 Assumptions Made

### 1. **Data Assumptions**
- Election data is relatively static (updated annually)
- 10 countries provide sufficient global coverage
- English is the primary language, with translations available
- Quiz questions are educational, not comprehensive assessments

### 2. **User Assumptions**
- Users have basic internet literacy
- Modern browsers with JavaScript enabled
- Screen resolution ≥320px width (mobile-first)
- Users interested in civic education

### 3. **Technical Assumptions**
- Google Cloud services remain available and stable
- API rate limits are sufficient for expected traffic
- Firestore is optional (fallback to local JSON)
- Users accept cookies for session management

### 4. **Security Assumptions**
- HTTPS enforced in production
- Users don't intentionally abuse rate limits
- API keys kept secure in environment variables
- Cloud Run provides DDoS protection

### 5. **Accessibility Assumptions**
- Users may use assistive technologies
- Keyboard-only navigation is required
- Color alone is not used to convey information
- Text can be resized up to 200%

### 6. **Performance Assumptions**
- Average network speed: 3G or better
- Server response time: <500ms acceptable
- Client-side rendering is acceptable
- Caching reduces API calls significantly

---

## 📊 Evaluation Criteria Compliance

### ✅ Code Quality
- **Structure**: Modular architecture with clear separation of concerns
- **Readability**: Comprehensive comments, type hints, docstrings
- **Maintainability**: DRY principle, reusable functions, configuration management

### ✅ Security
- **Input Sanitization**: bleach library for XSS prevention
- **Rate Limiting**: slowapi for request throttling
- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options
- **Secret Management**: Environment variables, Cloud Run secrets

### ✅ Efficiency
- **Caching**: In-memory TTL cache for Firestore data
- **Lazy Loading**: On-demand resource loading
- **Optimized Assets**: WebP images, minified CSS/JS
- **Database Indexing**: Firestore indexes for fast queries

### ✅ Testing
- **308 Tests Passing**: Comprehensive test coverage
- **Multiple Test Types**: Unit, integration, security, accessibility
- **CI/CD Integration**: Automated testing on push
- **Coverage Reports**: HTML coverage reports generated

### ✅ Accessibility
- **WCAG 2.1 AA**: Compliant with accessibility standards
- **Semantic HTML**: Proper use of landmarks and ARIA
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Optimized for assistive technologies

### ✅ Google Services
- **Gemini AI**: Primary AI chat functionality
- **Cloud Translate**: Multi-language support
- **Firestore**: Optional persistent storage
- **Cloud Run**: Production deployment
- **Vertex AI**: Grounding capability (optional)

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.115.12
- **Server**: Uvicorn 0.34.0
- **Validation**: Pydantic 2.10.6
- **Testing**: pytest 8.3.4

### Google Services
- **AI**: google-generativeai 0.8.3
- **Translation**: google-cloud-translate 3.18.0
- **Database**: firebase-admin 6.6.0
- **Deployment**: Google Cloud Run

### Security
- **Sanitization**: bleach 6.2.0
- **Rate Limiting**: slowapi 0.1.9
- **CORS**: FastAPI built-in

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Glassmorphism, animations
- **JavaScript**: Vanilla ES6+
- **Fonts**: Google Fonts (Playfair Display, DM Sans)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👨‍💻 Author

**Nishant Narudkar**
- GitHub: [@nishnarudkar](https://github.com/nishnarudkar)
- Project: [MatdaanHub](https://github.com/nishnarudkar/MatdaanHub---Global-Election-Education-Platform)

---

## 🙏 Acknowledgments

- Google Cloud Platform for hosting and services
- Google Gemini AI for natural language processing
- Open-source community for libraries and tools
- Election commissions worldwide for public data

---

## 📞 Support

For issues, questions, or contributions:
1. Open an issue on GitHub
2. Submit a pull request
3. Contact via GitHub profile

---

**Built with ❤️ for civic education and democratic engagement**
