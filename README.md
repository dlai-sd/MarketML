# MarketML - AI-Powered Marketing Persona Builder

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

MarketML is a sophisticated ML system that builds comprehensive business personas from multi-source data aggregation, intelligent analysis, and predictive modeling. Designed for digital marketing agencies serving SMBs (0-1Cr revenue), it automates persona generation with 20-30 second latency while maintaining high accuracy.

## 📚 Documentation Hub

**New to MarketML? Start here:**

- 🚀 **[Quick Reference](QUICK_REFERENCE.md)** - Get started in 2 minutes
- 📊 **[Status Snapshot](STATUS_SNAPSHOT.md)** - Visual project status dashboard
- 📋 **[Executive Summary](EXECUTIVE_SUMMARY.md)** - For stakeholders and decision-makers
- 📖 **[Getting Up to Speed](GETTING_UP_TO_SPEED.md)** - Comprehensive project overview (30 min read)
- ⚡ **[Quick Start Guide](QUICKSTART.md)** - Step-by-step setup and testing
- 📈 **[Progress Log](PROGRESS.md)** - Development history and milestones

**Current Status:** 95% Complete | 71 files | 8,100+ lines | Ready for testing

## 🎯 Key Features

- **Multi-Source Data Aggregation**: Scrapes LinkedIn, company websites, and news sources in parallel
- **Advanced NLP**: SpaCy-based entity extraction with custom models for Indian market
- **Contextual Enrichment**: Geographic, industry, and competitive intelligence layering
- **ML-Powered Scoring**: XGBoost ensemble for business maturity, marketing readiness, and budget capacity
- **Template-Based Generation**: Produces structured JSON + natural narratives (15-word + full)
- **Quality Validation**: Multi-level validation with confidence scoring
- **Progressive UI Feedback**: Real-time status updates during 20-30s generation process
- **Async Processing**: Celery-based job queue for scalability (500+ personas/day)
- **Incremental Learning**: Automatic model retraining from user feedback
- **Production-Ready**: Docker, monitoring, CI/CD, Azure deployment configs

## 🏗️ Architecture

```
┌─────────────┐
│  Check-in   │ → User provides name + location
│  Counter    │
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│           PERSONA BUILDER PIPELINE                      │
│                                                          │
│  1. Scraping (0-10s)                                    │
│     ├── LinkedIn (public profiles)                      │
│     ├── Company Websites                                │
│     ├── News Articles                                   │
│     └── Parallel execution with rate limiting           │
│                                                          │
│  2. Extraction (10-15s)                                 │
│     ├── SpaCy NER (persons, orgs, locations)           │
│     ├── Contact info extraction                         │
│     └── Structured data parsing                         │
│                                                          │
│  3. Enrichment (15-20s)                                 │
│     ├── Geographic context (affluence, tier, market)    │
│     ├── Industry intelligence                           │
│     ├── Competitive analysis                            │
│     └── 10 temporal attributes                          │
│                                                          │
│  4. Feature Engineering (20-22s)                        │
│     ├── 50+ computed features                           │
│     ├── Digital footprint scoring                       │
│     └── Readiness indicators                            │
│                                                          │
│  5. ML Scoring (22-25s)                                 │
│     ├── XGBoost ensemble (60% weight)                   │
│     ├── Random Forest (30%)                             │
│     ├── Linear model (10%)                              │
│     └── Outputs: maturity, readiness, budget, tier      │
│                                                          │
│  6. Generation (25-28s)                                 │
│     ├── Template-based narrative creation               │
│     ├── Marketing insights generation                   │
│     ├── Recommendations based on tier                   │
│     └── 15-word summary for UI                          │
│                                                          │
│  7. Validation (28-30s)                                 │
│     ├── Completeness checks                             │
│     ├── Consistency validation                          │
│     ├── Confidence calibration                          │
│     └── Quality issue flagging                          │
│                                                          │
└────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │ → Stores personas, feedback, jobs
│  Redis       │ → Caching + Celery queue
│  Qdrant      │ → Vector search for similar personas
└──────────────┘
```

## 📊 Technology Stack

**Backend:**
- Python 3.11
- FastAPI (async web framework)
- Celery (distributed task queue)
- SQLAlchemy (async ORM)
- Redis (caching + queue)

**ML/NLP:**
- SpaCy (NER)
- Sentence-Transformers (embeddings)
- XGBoost (scoring models)
- Scikit-learn (feature engineering)

**Data:**
- SQLite (development, upgradeable to PostgreSQL)
- Qdrant (vector database)
- Playwright (web scraping)
- BeautifulSoup4 (HTML parsing)

**DevOps:**
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- Prometheus + Grafana (monitoring)
- Azure (deployment target)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- 8GB+ RAM
- Git

### Local Development

1. **Clone repository**
```bash
git clone https://github.com/dlai-sd/MarketML.git
cd MarketML
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- API: http://localhost:8000/v1/docs
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

### Manual Setup (without Docker)

1. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
playwright install chromium
```

3. **Start services**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: API
uvicorn app.main:app --reload

# Terminal 3: Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 4: Celery beat (optional, for scheduled tasks)
celery -A app.tasks.celery_app beat --loglevel=info
```

## 📖 API Usage

### Generate Persona (Async)

```bash
curl -X POST "http://localhost:8000/v1/personas/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Yogesh Khandge",
    "location": "Pune, Maharashtra",
    "description": "Furniture business owner"
  }'
```

Response:
```json
{
  "job_id": "uuid-here",
  "status": "pending",
  "progress": 0,
  "current_step": "Queued for processing",
  "created_at": "2025-12-20T10:00:00Z"
}
```

### Check Job Status

```bash
curl "http://localhost:8000/v1/jobs/{job_id}"
```

### Get Generated Persona

```bash
curl "http://localhost:8000/v1/personas/{persona_id}"
```

Response:
```json
{
  "persona_id": "uuid",
  "confidence_score": 0.87,
  "structured": {
    "name": "Yogesh Khandge",
    "title": "Founder",
    "company": "Noya Furniture",
    "location": {
      "city": "Pune",
      "affluence_score": 7.2,
      "market_context": "Tier-1 metropolitan area..."
    },
    "scores": {
      "maturity": 65,
      "marketing_readiness": 72,
      "budget_capacity": 58,
      "recommended_tier": 2
    }
  },
  "short_narrative": "Furniture entrepreneur in Pune, growing business with digital focus",
  "narrative": "Full narrative...",
  "marketing_insights": [...],
  "recommended_actions": [...]
}
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test types
pytest -m unit
pytest -m integration
pytest -m model
```

### Load Testing
```bash
locust -f tests/load/locustfile.py --users 50 --spawn-rate 5
```

## 📁 Project Structure

```
MarketML/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── api/v1/                    # API endpoints
│   ├── core/                      # Database, schemas
│   ├── scrapers/                  # Web scrapers
│   ├── extractors/                # Entity extraction
│   ├── enrichment/                # Context enrichment
│   ├── features/                  # Feature engineering
│   ├── scoring/                   # ML models
│   ├── generation/                # Persona generation
│   ├── validation/                # Quality validation
│   └── tasks/                     # Celery tasks
├── data/                          # Enrichment databases
├── models/                        # Trained ML models
├── tests/                         # Test suite
├── frontend/                      # Test UI (TODO)
├── monitoring/                    # Prometheus/Grafana configs
├── docker-compose.yml             # Docker orchestration
├── Dockerfile                     # Container definition
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🎨 Test UI

(Coming soon - Week 2 of development)

Interactive web interface for:
- Real-time persona generation with progress bar
- Visual display of structured data
- Editing and feedback submission
- A/B testing different generation strategies

## 🔄 CI/CD Pipeline

GitHub Actions workflow:
1. **Lint & Format**: Black, Flake8, MyPy
2. **Unit Tests**: pytest with coverage
3. **Integration Tests**: End-to-end API tests
4. **Model Tests**: Validate ML model performance
5. **Build Docker Image**: Multi-stage build
6. **Push to Azure Container Registry**
7. **Deploy to Azure App Service**

## ☁️ Azure Deployment

### Prerequisites
- Azure subscription
- Azure CLI installed
- Resource group created

### Deploy
```bash
# Login to Azure
az login

# Create resources (first time only)
./scripts/azure_setup.sh

# Deploy application
./scripts/azure_deploy.sh
```

See `docs/AZURE_DEPLOYMENT.md` for detailed instructions.

## 📈 Monitoring

**Prometheus Metrics:**
- `personas_generated_total`: Total personas generated
- `persona_generation_seconds`: Generation latency histogram
- `scrape_duration_seconds`: Scraper performance by source
- `avg_confidence_score`: Average persona confidence

**Grafana Dashboards:**
- System Overview: CPU, memory, request rates
- Pipeline Performance: Stage-by-stage latency
- ML Model Metrics: Score distributions, prediction accuracy
- Business Metrics: Conversion rates, user satisfaction

Access Grafana at `http://localhost:3000` (admin/admin)

## 🔧 Configuration

Key environment variables:

```bash
# Application
APP_ENV=development
APP_DEBUG=True
API_V1_PREFIX=/v1

# Database
DATABASE_URL=sqlite:///./marketml.db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Scraping
SCRAPER_TIMEOUT=30
SCRAPER_RATE_LIMIT=1

# LLM (optional fallback)
DEEPSEEK_API_KEY=your-key-here

# Feature Flags
ENABLE_LLM_FALLBACK=true
ENABLE_CACHING=true
ENABLE_MONITORING=true
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Test cases: Yogesh Khandge, Noya Furniture, Yashus Digital Marketing
- Target market: Indian SMBs (0-1Cr revenue)
- Deployment region: Azure Central India

## 📞 Support

For questions or issues:
- Open GitHub Issue
- Check `PROGRESS.md` for development updates
- See `docs/` for detailed documentation

---

**Built with ❤️ for MarketML - Empowering Digital Marketing with AI**
MarketML
