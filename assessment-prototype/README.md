# Digital Marketing Assessment Prototype

A working prototype of the marketing assessment service with **REAL web scraping** and polling API.

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

### Data Sources (All Free)

- ✅ Google Search (SERP scraping)
- ✅ Bing Search
- ✅ Google News
- ✅ Public website content
- ✅ Social media profiles (public data)
- ✅ Review platforms (public ratings)

### Scoring Dimensions (Now Data-Driven)

All 7 dimensions now use real scraped data:

1. **Content Marketing** - Blog frequency, content pages
2. **SEO Presence** - Domain authority, backlinks estimate
3. **Social Engagement** - Followers, active platforms, engagement rate
4. **Conversion Signals** - CTAs, testimonials, analytics, meta tags
5. **Brand Authority** - News mentions, reviews, ratings
6. **Technical Optimization** - Page speed, mobile, structured data
7. **Thought Leadership** - Speaking, LinkedIn presence, media features

## How It Works

```
User Input: "Tesla"
    ↓
Google & Bing: Search "Tesla competitors"
    ↓
Discovery: Ford, GM, Rivian, Lucid, etc. (top 10)
    ↓
Parallel Scraping: 11 entities (Tesla + 10 competitors)
    ↓
For Each Entity:
  - Find website → Scrape content
  - Find social → Estimate followers
  - Search news → Count mentions
  - Check reviews → Get ratings
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
