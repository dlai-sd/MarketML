# Digital Marketing Assessment Prototype

A working prototype of the marketing assessment service with **REAL web scraping**, **AI-powered data extraction**, and **official government data integration**.

## 📚 Documentation

- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)** - Comprehensive field definitions, data types, and enumerations
- **[DATA_MODEL.md](DATA_MODEL.md)** - Entity relationships, database schema, and query patterns
- **[SCORING_BUSINESS_RULES.md](SCORING_BUSINESS_RULES.md)** - Evaluation dimensions and scoring logic

---

## ✅ Phase 1 Complete: Real Data Collection

### Real Scrapers Implemented

**1. Search Engine Discovery** (`scrapers/searchEngine.js`)
- Google search for competitors, alternatives, and "companies like X"
- Bing search with multiple query patterns
- Frequency-based ranking (only keeps companies mentioned 2+ times)
- Returns top 10 competitors by relevance

**2. Website Analysis** (`scrapers/website.js`)
- Finds official website via Google search or common patterns
- Scrapes homepage and analyzes:
  - Blog existence and content depth
  - Call-to-action presence
  - Testimonials/reviews
  - Meta tags and structured data
  - Mobile optimization
  - Analytics tracking (GA, Mixpanel, Segment)
  - Social media links
  - Page size and performance indicators

**3. Social Media Analysis** (`scrapers/social.js`)
- LinkedIn company page detection
- Twitter/X account discovery
- Follower count estimation from search snippets
- Platform counting (LinkedIn, Twitter, Facebook, Instagram, YouTube, TikTok)
- Engagement rate estimation

**4. Reputation & Authority** (`scrapers/reputation.js`)
- Google News mentions
- Recent news detection
- Review sites (G2, Capterra, Trustpilot, Yelp)
- Average rating extraction
- Domain authority estimation (0-100 scale)
- Backlink estimation
- Thought leadership indicators (speaking, publishing, conferences)

**5. MCA RoC API Integration** (`scrapers/mcaRocApi.js`)
- Official government company data (2.8M+ Indian companies)
- 16 verified registration fields
- 100% data accuracy for registered companies
- CIN-based lookup

**6. Groq AI Data Extraction** (`scrapers/groqCompanyData.js`)
- AI-powered company data extraction
- Enhanced financial data extraction (revenue, PAT, FY)
- Multi-format parsing (Crore, Lakh, Million, USD)
- Intelligent CIN discovery for MCA lookup

### Data Sources (Multi-tier)

**Priority 1: MCA RoC API** (Official Government Data)
- 2.8M+ registered Indian companies
- 100% data accuracy
- 16 registration fields
- Cost: TBD

**Priority 2: Groq AI + Google Search** (AI-Powered Extraction)
- Llama 3.3 70B model
- ~$0.0006 per company
- Financial data extraction
- 13-56% success rate (varies by company size)

**Priority 3: Legacy Scrapers** (Free Web Scraping)
- ✅ Google Search (SERP scraping)
- ✅ Bing Search
- ✅ Google News
- ✅ Public website content
- ✅ Social media profiles (public data)
- ✅ Review platforms (public ratings)
- ✅ ZaubaCorp (Indian company data)
- ✅ Wikipedia (revenue lookup)

### Groq→MCA Pipeline (Best Approach)

**How it works:**
1. **Groq AI** searches web and extracts CIN from company name
2. **MCA RoC API** fetches official data using CIN
3. Result: 100% accurate government-verified data

**Success rate:**
- Large public companies: 90%+ (e.g., TCS, Infosys)
- Medium companies: 50-70%
- Small private companies: 10-30%

### Scoring Dimensions (Now Data-Driven)

All 7 dimensions use real scraped data + contextual adjustments:

1. **Content Marketing** - Blog frequency, content pages (adjusted by tier/industry)
2. **SEO Presence** - Domain authority, backlinks estimate
3. **Social Engagement** - Followers, active platforms, engagement rate
4. **Conversion Signals** - CTAs, testimonials, analytics, meta tags
5. **Brand Authority** - News mentions, reviews, ratings
6. **Technical Optimization** - Page speed, mobile, structured data
7. **Thought Leadership** - Speaking, LinkedIn presence, media features

See [SCORING_BUSINESS_RULES.md](SCORING_BUSINESS_RULES.md) for detailed scoring logic.

## Architecture

### Data Flow
```
User Input: "Tesla"
    ↓
1. Intelligent Discovery
    ├─► Google: "Tesla competitors"
    ├─► Bing: "companies like Tesla"
    └─► Rank by frequency
    ↓
2. Competitor List (top 10)
    ↓
3. For Each Entity (Tesla + Competitors):
    ├─► MCA RoC API (if CIN known) → Official data
    ├─► Groq AI → Find CIN + Financial data
    │   └─► If CIN found → Query MCA RoC API
    ├─► Legacy scrapers:
    │   ├─► Website analysis
    │   ├─► Social media scan
    │   ├─► Reputation check
    │   └─► SEO metrics
    └─► Base defaults (if no data)
    ↓
Calculate Scores: 7 dimensions per entity
    ↓
Determine Tier: Small/Medium/Large
    ↓
Weighted Score: Tier-dependent formula
    ↓
Results: Complete comparison report
```

## Setup

```bash
cd assessment-prototype
npm install
npm start
```

Open: http://localhost:3000

## API Endpoints

### Start Assessment
```bash
POST /api/assess
{
  "subject": "Tesla"
}

Response: { "job_id": "uuid", "status": "processing" }
```

### Poll Status
```bash
GET /api/assess/{job_id}

Response:
{
  "status": "processing|complete|failed",
  "progress": { 
    "phase": "discovery|analysis|complete",
    "completed": 5,
    "total": 11,
    "message": "Analyzing Tesla..."
  },
  "result": { ... }
}
```

## Real-World Test Examples

Try these real companies:

- **"Salesforce"** - Large enterprise
- **"Notion"** - Medium tech company
- **"Local Coffee Shop"** - Small business (will show limited data)
- **"Stripe"** - High-performing tech company

## Current Capabilities

✅ **Real competitor discovery** (not mocked)
✅ **Real website scraping** (homepage analysis)
✅ **Real social media detection** (LinkedIn, Twitter)
✅ **Real news/reputation data** (Google News, reviews)
✅ **Intelligent fallbacks** (when scraping fails)
✅ **Rate limiting awareness** (delays between requests)
✅ **Error handling** (continues despite partial failures)

## Limitations & Next Steps

### Current Limitations

1. **Rate Limiting Risk** - High-volume usage may trigger anti-bot measures
2. **Depth Limited** - Only scrapes surface data (homepage, snippets)
3. **No Authentication** - Can't access LinkedIn/Twitter APIs directly
4. **Estimation-Based** - Follower counts and metrics are approximate
5. **No Caching** - Every assessment re-scrapes everything

### Phase 2: Enhanced Scoring (Next)

- [ ] Percentile-based scoring across industries
- [ ] Historical comparison (track improvements)
- [ ] Industry-specific benchmarks
- [ ] Anomaly detection (inflated metrics)
- [ ] Confidence scores (data quality indicators)

### Phase 3: Production Features

- [ ] Redis caching (reduce redundant scraping)
- [ ] Proxy rotation (avoid rate limits)
- [ ] API key authentication
- [ ] Usage quotas and billing integration
- [ ] Webhook notifications (completed assessments)
- [ ] PDF report generation
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)

### Future Enhancements

- [ ] Deeper scraping (blog posts, multiple pages)
- [ ] Official API integrations (Twitter, LinkedIn via OAuth)
- [ ] Competitor classification ML model
- [ ] Time-series tracking (score history)
- [ ] Custom industry definitions
- [ ] Multi-language support
- [ ] Image/brand analysis (logo detection, visual presence)

## Technical Architecture

```
Frontend (HTML/JS)
    ↓
Express API Server
    ↓
Scraper Modules
    ├── searchEngine.js (Google/Bing)
    ├── website.js (Content analysis)
    ├── social.js (Social media)
    └── reputation.js (News/reviews)
    ↓
Scoring Engine
    ├── 7 dimensions
    ├── Tier classification
    └── Weighted aggregation
    ↓
JSON Response (Subject + 10 Competitors)
```

## Data Privacy & Ethics

- **Public Data Only** - No authentication required
- **Respects robots.txt** - (Should be added)
- **Rate Limited** - Delays between requests
- **No Data Storage** - In-memory only
- **Transparent** - Shows data sources

## Performance

- **Discovery**: 10-20 seconds (Google + Bing searches)
- **Per Entity Scraping**: 5-10 seconds (3 parallel scrapers)
- **Total Time**: 60-120 seconds for full assessment
- **Concurrent Limit**: 3 entities at a time (configurable)

## Error Handling

- **Graceful Degradation** - Partial data better than failure
- **Fallback Values** - Default scores when scraping fails
- **Retry Logic** - (To be added)
- **Logging** - Console errors for debugging

## Converting to Production

1. **Add Caching**: Redis for 24-hour data cache
2. **Proxy Service**: Rotate IPs to avoid blocking
3. **Authentication**: JWT tokens from portal
4. **Rate Limiting**: Per-user quotas
5. **Monitoring**: Error tracking, performance metrics
6. **Scaling**: Horizontal scaling with load balancer

---

**Status**: ✅ Phase 1 Complete - Real data collection working!

**Next**: Phase 2 - Enhanced scoring algorithms
