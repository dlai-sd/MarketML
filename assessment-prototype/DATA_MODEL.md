# MarketML Data Model
**Entity Relationship Diagram & Schema Design**

Version: 1.0  
Last Updated: December 22, 2025

---

## Entity Relationship Diagram (ERD)

### Visual Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASSESSMENT JOB                                     │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ job_id: UUID                                                        │    │
│  │ status: enum (processing, completed, failed)                       │    │
│  │ created_at: timestamp                                              │    │
│  │ estimated_duration: integer                                        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                          │                                                   │
│                          │ 1:N                                              │
│                          ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         COMPANY                                      │   │
│  │  (Subject + Competitors)                                            │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ Primary Keys:                                                       │   │
│  │  • cin: string(21) [Unique]                                        │   │
│  │  • name: string                                                    │   │
│  │                                                                     │   │
│  │ Profile:                                                            │   │
│  │  • company_name                    • status                        │   │
│  │  • company_class                   • pan                           │   │
│  │  • company_category                • listing_status               │   │
│  │  • date_of_incorporation           • company_age                  │   │
│  │  • roc                             • nic_code                      │   │
│  │  • industrial_classification                                       │   │
│  │                                                                     │   │
│  │ Contact:                                                            │   │
│  │  • registered_address              • email                         │   │
│  │  • phone                           • website_url                   │   │
│  │                                                                     │   │
│  │ Metadata:                                                           │   │
│  │  • data_quality                    • data_source                   │   │
│  │  • extraction_confidence           • timestamp                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                │                │                │                          │
│                │                │                │                          │
│     ┌──────────┘                │                └──────────┐              │
│     │ 1:1                       │ 1:N                    1:1│              │
│     ▼                           ▼                           ▼              │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐        │
│  │  LOCATION    │    │    DIRECTORS     │    │    FINANCIAL     │        │
│  ├──────────────┤    ├──────────────────┤    ├──────────────────┤        │
│  │ • city       │    │ • name           │    │ • financial_year │        │
│  │ • region     │    │ • din            │    │ • authorized_cap │        │
│  │ • state      │    │ • appointment_dt │    │ • paid_up_cap    │        │
│  │ • state_code │    │                  │    │ • revenue_inr    │        │
│  │ • country    │    │                  │    │ • revenue_usd    │        │
│  │ • country_cd │    │                  │    │ • profit_after_  │        │
│  │ • globe      │    │                  │    │   tax            │        │
│  └──────────────┘    └──────────────────┘    │ • total_assets   │        │
│                                               │ • revenue_source │        │
│                                               └──────────────────┘        │
│                                                        │                    │
│                                                        │ 1:1                │
│                                                        ▼                    │
│                                      ┌──────────────────────────────┐      │
│                                      │   DIGITAL MARKETING METRICS  │      │
│                                      ├──────────────────────────────┤      │
│                                      │ Website Analytics:           │      │
│                                      │  • domain_authority          │      │
│                                      │  • backlinks                 │      │
│                                      │  • page_speed                │      │
│                                      │  • mobile_optimized          │      │
│                                      │                              │      │
│                                      │ Content Marketing:           │      │
│                                      │  • blog_posts_per_month      │      │
│                                      │  • content_pages             │      │
│                                      │  • has_blog                  │      │
│                                      │                              │      │
│                                      │ Social Media:                │      │
│                                      │  • social_followers          │      │
│                                      │  • active_platforms          │      │
│                                      │  • engagement_rate           │      │
│                                      │                              │      │
│                                      │ SEO:                         │      │
│                                      │  • organic_keywords          │      │
│                                      │  • organic_traffic           │      │
│                                      │                              │      │
│                                      │ Conversion:                  │      │
│                                      │  • has_cta                   │      │
│                                      │  • has_testimonials          │      │
│                                      │  • contact_forms             │      │
│                                      │                              │      │
│                                      │ Reputation:                  │      │
│                                      │  • media_mentions            │      │
│                                      │  • review_count              │      │
│                                      │  • average_rating            │      │
│                                      └──────────────────────────────┘      │
│                                                        │                    │
│                                                        │ 1:1                │
│                                                        ▼                    │
│                                      ┌──────────────────────────────┐      │
│                                      │   SCORING & EVALUATION       │      │
│                                      ├──────────────────────────────┤      │
│                                      │ Dimension Scores:            │      │
│                                      │  • content_marketing (1-7)   │      │
│                                      │  • seo_presence (1-7)        │      │
│                                      │  • social_engagement (1-7)   │      │
│                                      │  • conversion_signals (1-7)  │      │
│                                      │  • brand_authority (1-7)     │      │
│                                      │  • technical_optimization    │      │
│                                      │  • thought_leadership (1-7)  │      │
│                                      │                              │      │
│                                      │ Context:                     │      │
│                                      │  • tier (small/medium/large) │      │
│                                      │  • industry                  │      │
│                                      │  • business_model            │      │
│                                      │                              │      │
│                                      │ Aggregate:                   │      │
│                                      │  • score (weighted)          │      │
│                                      │  • notes                     │      │
│                                      └──────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema (MongoDB-style)

### Collection: `assessments`

```javascript
{
  _id: ObjectId,
  job_id: UUID,
  status: "processing" | "completed" | "failed",
  created_at: ISODate,
  updated_at: ISODate,
  estimated_duration: Number,
  progress: {
    phase: String,
    message: String,
    completed: Number,
    total: Number
  },
  subject: String,  // Company name searched
  result: {
    subject: { /* Company Schema */ },
    competitors: [ /* Array of Company Schema */ ]
  },
  error: String  // If status = failed
}
```

### Collection: `companies` (Normalized)

```javascript
{
  _id: ObjectId,
  cin: String(21),  // Unique index
  name: String,
  company_name: String,
  
  // Profile
  profile: {
    status: String,
    company_class: String,
    company_category: String,
    company_subcategory: String,
    date_of_incorporation: Date,
    company_age: Number,
    roc: String,
    roc_code: String,
    listing_status: String,
    indian_foreign: String,
    pan: String,
    nic_code: String,
    industrial_classification: String
  },
  
  // Location
  location: {
    city: String,
    region: String,
    state: String,
    state_code: String,
    country: String,
    country_code: String,
    globe: Boolean,
    registered_address: String
  },
  
  // Contact
  contact: {
    email: String,
    phone: String,
    website_url: String
  },
  
  // Directors
  directors: [
    {
      name: String,
      din: String,
      appointment_date: Date
    }
  ],
  
  // Financial
  financial: {
    authorized_capital: Number,
    paid_up_capital: Number,
    financial_year: String,
    revenue_inr_millions: Number,
    revenue_millions: Number,
    revenue_display: String,
    revenue_source: String,
    profit_after_tax: String,
    total_assets: String
  },
  
  // Digital Marketing Metrics
  digital_metrics: {
    website: {
      domain_authority: Number,
      backlinks: Number,
      page_speed: Number,
      mobile_optimized: Boolean,
      has_analytics: Boolean,
      structured_data: Boolean,
      has_ssl: Boolean
    },
    content: {
      blog_posts_per_month: Number,
      content_pages: Number,
      has_blog: Boolean,
      has_case_studies: Boolean,
      has_whitepapers: Boolean,
      video_content: Boolean
    },
    social: {
      social_followers: Number,
      active_platforms: Number,
      engagement_rate: Number,
      linkedin_followers: Number,
      twitter_followers: Number,
      facebook_likes: Number,
      instagram_followers: Number,
      youtube_subscribers: Number
    },
    seo: {
      organic_keywords: Number,
      organic_traffic: Number,
      top_10_keywords: Number,
      meta_description: String,
      meta_keywords: Array
    },
    conversion: {
      has_cta: Boolean,
      has_testimonials: Boolean,
      has_pricing: Boolean,
      has_demo: Boolean,
      contact_forms: Number,
      chat_widget: Boolean
    },
    reputation: {
      media_mentions: Number,
      recent_news: Boolean,
      review_count: Number,
      average_rating: Number,
      awards: Array,
      certifications: Array
    }
  },
  
  // Scoring
  scoring: {
    dimensions: {
      content_marketing: Number(1-7),
      seo_presence: Number(1-7),
      social_engagement: Number(1-7),
      conversion_signals: Number(1-7),
      brand_authority: Number(1-7),
      technical_optimization: Number(1-7),
      thought_leadership: Number(1-7)
    },
    context: {
      tier: String,
      tier_signal_total: Number,
      industry: String,
      business_model: String,
      service_complexity: String
    },
    aggregate: {
      score: Number,
      notes: String
    }
  },
  
  // Metadata
  metadata: {
    data_quality: String,
    data_source: String,
    extraction_confidence: String,
    extraction_method: String,
    timestamp: ISODate,
    last_updated: ISODate
  }
}
```

---

## Relational Schema (PostgreSQL)

### Table: `assessments`

```sql
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    estimated_duration INTEGER,
    subject VARCHAR(255) NOT NULL,
    error TEXT,
    INDEX idx_job_id (job_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

### Table: `companies`

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    cin VARCHAR(21) UNIQUE,
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(500),
    
    -- Profile
    status VARCHAR(50),
    company_class VARCHAR(50),
    company_category VARCHAR(100),
    company_subcategory VARCHAR(100),
    date_of_incorporation DATE,
    company_age INTEGER,
    roc VARCHAR(100),
    roc_code VARCHAR(50),
    listing_status VARCHAR(50),
    indian_foreign VARCHAR(20),
    pan VARCHAR(10),
    nic_code VARCHAR(10),
    industrial_classification VARCHAR(200),
    
    -- Contact
    registered_address TEXT,
    email VARCHAR(255),
    phone VARCHAR(50),
    website_url VARCHAR(500),
    
    -- Metadata
    data_quality VARCHAR(20),
    data_source VARCHAR(100),
    extraction_confidence VARCHAR(20),
    extraction_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_cin (cin),
    INDEX idx_status (status),
    INDEX idx_company_class (company_class),
    INDEX idx_nic_code (nic_code)
);
```

### Table: `company_locations`

```sql
CREATE TABLE company_locations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    city VARCHAR(100),
    region VARCHAR(100),
    state VARCHAR(100),
    state_code VARCHAR(50),
    country VARCHAR(100),
    country_code CHAR(2),
    globe BOOLEAN DEFAULT FALSE,
    
    INDEX idx_company_id (company_id),
    INDEX idx_city (city),
    INDEX idx_state (state),
    INDEX idx_state_code (state_code)
);
```

### Table: `directors`

```sql
CREATE TABLE directors (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    din VARCHAR(8),
    appointment_date DATE,
    
    INDEX idx_company_id (company_id),
    INDEX idx_din (din)
);
```

### Table: `company_financials`

```sql
CREATE TABLE company_financials (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    financial_year VARCHAR(20),
    authorized_capital DECIMAL(20,2),
    paid_up_capital DECIMAL(20,2),
    revenue_inr_millions DECIMAL(20,2),
    revenue_millions DECIMAL(20,2),
    revenue_display VARCHAR(100),
    revenue_source VARCHAR(100),
    profit_after_tax VARCHAR(100),
    total_assets VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_company_id (company_id),
    INDEX idx_financial_year (financial_year),
    UNIQUE(company_id, financial_year)
);
```

### Table: `digital_metrics`

```sql
CREATE TABLE digital_metrics (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    
    -- Website
    domain_authority INTEGER,
    backlinks INTEGER,
    page_speed INTEGER,
    mobile_optimized BOOLEAN,
    has_analytics BOOLEAN,
    structured_data BOOLEAN,
    
    -- Content
    blog_posts_per_month DECIMAL(5,2),
    content_pages INTEGER,
    has_blog BOOLEAN,
    
    -- Social
    social_followers INTEGER,
    active_platforms INTEGER,
    engagement_rate DECIMAL(5,2),
    
    -- SEO
    organic_keywords INTEGER,
    organic_traffic INTEGER,
    
    -- Conversion
    has_cta BOOLEAN,
    has_testimonials BOOLEAN,
    
    -- Reputation
    media_mentions INTEGER,
    review_count INTEGER,
    average_rating DECIMAL(3,2),
    
    measured_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_company_id (company_id)
);
```

### Table: `scoring_results`

```sql
CREATE TABLE scoring_results (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    assessment_id INTEGER REFERENCES assessments(id),
    
    -- Dimension Scores
    content_marketing INTEGER CHECK (content_marketing BETWEEN 1 AND 7),
    seo_presence INTEGER CHECK (seo_presence BETWEEN 1 AND 7),
    social_engagement INTEGER CHECK (social_engagement BETWEEN 1 AND 7),
    conversion_signals INTEGER CHECK (conversion_signals BETWEEN 1 AND 7),
    brand_authority INTEGER CHECK (brand_authority BETWEEN 1 AND 7),
    technical_optimization INTEGER CHECK (technical_optimization BETWEEN 1 AND 7),
    thought_leadership INTEGER CHECK (thought_leadership BETWEEN 1 AND 7),
    
    -- Context
    tier VARCHAR(20),
    tier_signal_total INTEGER,
    industry VARCHAR(50),
    business_model VARCHAR(20),
    
    -- Aggregate
    score DECIMAL(4,2),
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_company_id (company_id),
    INDEX idx_assessment_id (assessment_id),
    INDEX idx_tier (tier),
    INDEX idx_industry (industry),
    INDEX idx_score (score)
);
```

### Table: `assessment_companies` (Junction Table)

```sql
CREATE TABLE assessment_companies (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    company_id INTEGER REFERENCES companies(id),
    role VARCHAR(20) NOT NULL,  -- 'subject' or 'competitor'
    
    UNIQUE(assessment_id, company_id),
    INDEX idx_assessment_id (assessment_id),
    INDEX idx_company_id (company_id),
    INDEX idx_role (role)
);
```

---

## Indexing Strategy

### Primary Indexes
- `companies.cin` (UNIQUE) - Fast CIN lookup
- `companies.id` (PRIMARY) - Sequential access
- `assessments.job_id` (UNIQUE) - Job status lookup

### Secondary Indexes
- `company_locations.state_code` - Location filtering
- `scoring_results.tier` + `industry` - Comparative analysis
- `digital_metrics.domain_authority` - Ranking
- `company_financials.financial_year` - Temporal queries

### Composite Indexes
- `(state_code, industry, tier)` - Competitive filtering
- `(assessment_id, role)` - Subject vs competitor separation
- `(cin, financial_year)` - Historical financial data

---

## Query Patterns

### 1. Get Top 50 Competitors by Location

```javascript
// MongoDB
db.companies.find({
  "location.state_code": "maharashtra",
  "location.city": "pune",
  "profile.status": "Active",
  "scoring.aggregate.score": { $gt: 0 }
})
.sort({ "scoring.aggregate.score": -1 })
.limit(50);
```

```sql
-- PostgreSQL
SELECT c.*, sr.score
FROM companies c
JOIN company_locations cl ON c.id = cl.company_id
JOIN scoring_results sr ON c.id = sr.company_id
WHERE cl.state_code = 'maharashtra'
  AND cl.city = 'Pune'
  AND c.status = 'Active'
  AND sr.score > 0
ORDER BY sr.score DESC
LIMIT 50;
```

### 2. Get Financial Trends

```sql
SELECT 
  financial_year,
  AVG(revenue_millions) as avg_revenue,
  COUNT(*) as company_count
FROM company_financials
WHERE financial_year IN ('FY 2023-24', 'FY 2024-25')
GROUP BY financial_year
ORDER BY financial_year;
```

### 3. Industry Benchmarks

```sql
SELECT 
  sr.industry,
  sr.tier,
  AVG(sr.content_marketing) as avg_content_score,
  AVG(sr.seo_presence) as avg_seo_score,
  AVG(sr.score) as avg_total_score,
  COUNT(*) as companies
FROM scoring_results sr
WHERE sr.created_at > NOW() - INTERVAL '30 days'
GROUP BY sr.industry, sr.tier
ORDER BY sr.industry, sr.tier;
```

---

## Data Flow Diagram

```
┌─────────────┐
│   User      │
│  Request    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐      ┌──────────────────┐
│  POST /api/     │      │  Create Job      │
│  assess         ├─────►│  UUID            │
│                 │      │  Status=process  │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌────────────────────┐
                         │  Scrape Subject    │
                         │  Company           │
                         └────────┬───────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Legacy CIN      │    │ Groq→MCA         │    │ Base Defaults   │
│ Lookup          │    │ Pipeline         │    │                 │
│ (ZaubaCorp)     │    │ (AI + Official)  │    │ (Fallback)      │
└────────┬────────┘    └────────┬─────────┘    └────────┬────────┘
         │                      │                        │
         └──────────────────────┼────────────────────────┘
                                ▼
                       ┌─────────────────┐
                       │  Merge Company  │
                       │  Data           │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Discover       │
                       │  Competitors    │
                       └────────┬────────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
                     ▼                     ▼
          ┌──────────────────┐  ┌──────────────────┐
          │ Intelligent      │  │ Wikipedia        │
          │ Discovery        │  │ Fallback         │
          └──────┬───────────┘  └─────────┬────────┘
                 │                        │
                 └────────────┬───────────┘
                              ▼
                     ┌──────────────────┐
                     │ For Each         │
                     │ Competitor       │
                     └────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
     │ Scrape      │  │ Scrape      │  │ Scrape      │
     │ Website     │  │ Social      │  │ Reputation  │
     └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
            │                │                │
            └────────────────┼────────────────┘
                             ▼
                    ┌──────────────────┐
                    │ Calculate        │
                    │ Scores           │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ Return Results   │
                    │ Subject +        │
                    │ Competitors      │
                    └──────────────────┘
```

---

## Scalability Considerations

### Horizontal Scaling
- **Sharding by State**: Partition companies by `state_code`
- **Read Replicas**: For competitor discovery queries
- **Caching**: Redis for frequent CIN lookups

### Vertical Optimization
- **Denormalization**: Embed location in company document (MongoDB)
- **Materialized Views**: Pre-computed industry benchmarks
- **Partial Indexes**: Only index Active companies

### Data Archival
- Archive assessments older than 90 days
- Compress historical financial data
- Soft delete Strike Off companies from active queries

---

## Version Control

| Version | Date | Schema Changes |
|---------|------|----------------|
| 1.0 | 2025-12-22 | Initial schema |

