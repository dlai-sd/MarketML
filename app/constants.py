"""
Centralized constants and path management for MarketML.
All hardcoded paths, routes, and magic numbers should be defined here.
"""

from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
ENRICHMENT_DATA_DIR = DATA_DIR / "enrichment"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Database Paths
ENRICHMENT_DB_LOCATIONS = ENRICHMENT_DATA_DIR / "locations.db"
ENRICHMENT_DB_INDUSTRIES = ENRICHMENT_DATA_DIR / "industries.db"
ENRICHMENT_DB_COMPETITORS = ENRICHMENT_DATA_DIR / "competitors.db"
ENRICHMENT_DB_KEYWORDS = ENRICHMENT_DATA_DIR / "keywords.db"

# Model Paths
MODEL_XGBOOST = MODELS_DIR / "xgboost_v1.pkl"
MODEL_RANDOM_FOREST = MODELS_DIR / "random_forest_v1.pkl"
MODEL_LINEAR = MODELS_DIR / "linear_model_v1.pkl"
MODEL_SCALER = MODELS_DIR / "scaler_v1.pkl"

# API Routes
API_V1_PREFIX = "/v1"
ROUTE_HEALTH = "/health"
ROUTE_ROOT = "/"
ROUTE_METRICS = "/metrics"

# API Endpoints
ENDPOINT_PERSONAS_GENERATE = "/personas/generate"
ENDPOINT_PERSONAS_GET = "/personas/{persona_id}"
ENDPOINT_PERSONAS_BY_PERSON = "/personas/by-person/{person_id}"
ENDPOINT_JOBS_STATUS = "/jobs/{job_id}"
ENDPOINT_FEEDBACK_SUBMIT = "/feedback/"

# Scraping Limits
DEFAULT_SCRAPER_TIMEOUT = 30
DEFAULT_SCRAPER_RETRIES = 3
DEFAULT_RATE_LIMIT_SECONDS = 1.0
MAX_CONCURRENT_SCRAPERS = 5

# Processing Limits
MAX_PROFILE_SCORE = 10.0
MIN_CONFIDENCE_THRESHOLD = 0.3
DEFAULT_QUALITY_THRESHOLD = 0.7

# Cache TTL (seconds)
CACHE_TTL_PERSONA = 3600  # 1 hour
CACHE_TTL_PROFILE = 1800  # 30 minutes
CACHE_TTL_ENRICHMENT = 86400  # 24 hours

# Indian Market Data
TIER_1_CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", 
    "Kolkata", "Pune", "Ahmedabad"
]

TIER_2_CITIES = [
    "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
    "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna"
]

MAJOR_INDUSTRIES = [
    "Technology", "Healthcare", "Education", "Real Estate",
    "Retail", "Manufacturing", "Financial Services", "Hospitality",
    "Construction", "Agriculture", "E-commerce", "Logistics"
]

# Template Paths (for persona generation)
TEMPLATE_PERSONA_NARRATIVE = "persona_narrative.jinja2"
TEMPLATE_MARKETING_INSIGHTS = "marketing_insights.jinja2"

# Validation Rules
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
MIN_DESCRIPTION_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 5000

# Feature Engineering
FEATURE_COUNT_EXPECTED = 50
TEMPORAL_FEATURES = [
    "day_of_week", "hour_of_day", "is_weekend", "is_business_hours",
    "season", "quarter", "month", "year", "day_of_month", "week_of_year"
]

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Database
DEFAULT_DB_URL = "sqlite:///./marketml.db"
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30

# Celery
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Monitoring
METRICS_COLLECTION_INTERVAL = 15  # seconds
HEALTH_CHECK_TIMEOUT = 5  # seconds

# Version
API_VERSION = "0.1.0"
