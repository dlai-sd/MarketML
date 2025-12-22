# MarketML Quick Reference
**Essential Field Guide for Developers**

---

## Company Identity

| Field | Type | Example | Source |
|-------|------|---------|--------|
| `cin` | string(21) | U74120PN2015PTC157176 | MCA |
| `company_name` | string | YASHUS DIGITAL MARKETING PVT LTD | MCA |
| `pan` | string(10) | AABCY1234C | Groq |
| `status` | enum | Active, Strike Off | MCA |

---

## Location Filtering

**City-level** (15-50 competitors)
```javascript
{ "location.city": "Pune", "location.state_code": "maharashtra" }
```

**State-level** (50-100 competitors)
```javascript
{ "location.state_code": "maharashtra" }
```

**Country-level** (75-100+ competitors)
```javascript
{ "location.country": "India" }
```

**Globe** (no filter)
```javascript
{ "location.globe": true }
```

---

## Financial Data

### Current Year
| Field | Type | Format | Conversion |
|-------|------|--------|------------|
| `revenue_inr_millions` | decimal | Crores | 1 Cr = 1.0 |
| `revenue_millions` | decimal | USD M | Cr ÷ 83 |
| `financial_year` | string | FY 2023-24 | - |
| `authorized_capital` | decimal | INR | - |
| `paid_up_capital` | decimal | INR | - |

### Historical Revenue (5 Years)
```javascript
revenue_history: [
  {
    financial_year: "FY 2023-24",
    year_numeric: 2024,
    revenue_inr_crores: 1234.00,
    revenue_usd_millions: 14.87,
    growth_rate_yoy: 15.5,
    confidence: "high"
  },
  // ... up to 5 years
]
```

### Growth Metrics
| Field | Type | Calculation |
|-------|------|-------------|
| `revenue_cagr_3y` | decimal | 3-year compound growth |
| `revenue_cagr_5y` | decimal | 5-year compound growth |
| `revenue_trend` | enum | growing/stable/declining |
| `years_with_data` | integer | Count of FYs |

**Currency Conversions:**
- INR to USD: `inr / 83`
- Lakh to Crore: `lakh / 100`
- Million USD to Crore: `million_usd * 8.3`

---

## Digital Marketing Metrics

### Quick Stats
```javascript
{
  "domain_authority": 0-100,        // Moz DA score
  "social_followers": 0-10000000+,  // Total across platforms
  "blog_posts_per_month": 0-30+,    // Posting frequency
  "media_mentions": 0-10000+,       // News articles
  "review_count": 0-100000+,        // Online reviews
  "average_rating": 0-5.0           // Avg review rating
}
```

### Boolean Flags
```javascript
{
  "has_blog": true,
  "has_cta": true,
  "has_testimonials": true,
  "mobile_optimized": true,
  "has_analytics": true
}
```

---

## Scoring Dimensions (1-7 scale)

| Dimension | Weight | Key Metrics |
|-----------|--------|-------------|
| Content Marketing | 20% | blog_posts_per_month, content_pages |
| SEO Presence | 20% | domain_authority, backlinks |
| Social Engagement | 15% | social_followers, active_platforms |
| Conversion Signals | 15% | has_cta, has_testimonials |
| Brand Authority | 15% | media_mentions, review_count |
| Technical Optimization | 10% | page_speed, mobile_optimized |
| Thought Leadership | 5% | linkedin_presence, speaking |

**Overall Score:**
```javascript
score = Σ(dimension × weight)
// Range: 1.0 - 7.0
```

---

## Tier Classification

| Tier | Threshold | Characteristics |
|------|-----------|----------------|
| small | < 1,000 | signals = followers + DA + mentions |
| medium | 1K-10K | Standard expectations |
| large | > 10K | Higher standards |

**Calculation:**
```javascript
tier_signal_total = social_followers + domain_authority + media_mentions

if (tier_signal_total < 1000) tier = "small"
else if (tier_signal_total < 10000) tier = "medium"
else tier = "large"
```

---

## Industry Categories

| Industry | NIC Codes | Keywords |
|----------|-----------|----------|
| SaaS/Tech | 62xxx, 63xxx | software, platform, cloud, API |
| E-commerce | 47xxx | shop, store, buy, retail, cart |
| Professional Services | 69xxx-74xxx | consulting, agency, services |
| Manufacturing | 10xxx-33xxx | manufacturing, industrial |
| Healthcare | 86xxx | health, medical, care, clinic |
| Financial Services | 64xxx-66xxx | finance, banking, investment |

---

## Data Quality Levels

| Level | Description | Source | Use Case |
|-------|-------------|--------|----------|
| `complete` | All MCA fields | MCA RoC API | Verified data |
| `partial` | Some fields | Groq AI / ZaubaCorp | Public data |
| `limited` | Base defaults | Assumed values | Fallback |

---

## Common Queries

### Get Top 50 Competitors in Pune
```javascript
// MongoDB
db.companies.find({
  "location.city": "Pune",
  "profile.status": "Active",
  "scoring.aggregate.score": { $gt: 0 }
})
.sort({ "scoring.aggregate.score": -1 })
.limit(50)
```

### Get Companies by Revenue Range
```javascript
db.companies.find({
  "financial.revenue_millions": { $gte: 1, $lte: 10 }  // $1M-$10M
})
```

### Get Companies with Historical Revenue Data
```javascript
db.companies.find({
  "financial.revenue_history": { $exists: true, $ne: [] },
  "financial.years_with_data": { $gte: 3 }  // At least 3 years
})
```

### Get Fast-Growing Companies (CAGR > 20%)
```javascript
db.companies.find({
  "financial.revenue_cagr_3y": { $gte: 20.0 },
  "financial.revenue_trend": "growing"
})
.sort({ "financial.revenue_cagr_3y": -1 })
```

### Get Revenue History for Specific Company
```javascript
db.companies.findOne(
  { "cin": "U74120PN2015PTC157176" },
  { "financial.revenue_history": 1, "financial.revenue_cagr_5y": 1 }
)
```

### Get High-Performing Companies by Industry
```javascript
db.companies.find({
  "scoring.context.industry": "SaaS/Tech",
  "scoring.aggregate.score": { $gte: 5.0 }
})
```

---

## API Endpoints

### Start Assessment
```bash
POST /api/assess
{
  "subject": "Company Name"
}
# Returns: { job_id, status, estimated_duration }
```

### Get Assessment Status
```bash
GET /api/assess/:jobId
# Returns: { status, progress, result }
```

### Get Company Data (Groq AI)
```bash
POST /api/company-data/groq
{
  "companyName": "Company Name"
}
# Returns: { success, data: { cin, revenue, ... }, sources }
```

---

## Environment Variables

```bash
# Required
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIzaSy...
GOOGLE_CX=b1536af...
MCA_API_KEY=579b464...
MCA_RESOURCE_ID=4dbe5667...

# Optional
PORT=3000
NODE_ENV=development
```

---

## State Codes Reference

| State | State Code |
|-------|------------|
| Maharashtra | maharashtra |
| Karnataka | karnataka |
| Delhi | delhi |
| Tamil Nadu | tamil nadu |
| Gujarat | gujarat |
| Telangana | telangana |
| West Bengal | west bengal |

*See [DATA_DICTIONARY.md](DATA_DICTIONARY.md#indian-states-state-codes) for complete list*

---

## Response Time Estimates

| Operation | Time | Notes |
|-----------|------|-------|
| MCA Direct Lookup | 1-2s | Single CIN query |
| Groq AI Extraction | 3-5s | 6 search queries + AI |
| Website Scraping | 2-4s | Per company |
| Full Assessment (1+10) | 60-120s | Subject + 10 competitors |

---

## File Structure

```
assessment-prototype/
├── DATA_DICTIONARY.md       # Complete field definitions
├── DATA_MODEL.md            # Schema & relationships
├── SCORING_BUSINESS_RULES.md # Evaluation logic
├── server.js                # Main API server
├── scrapers/
│   ├── mcaRocApi.js        # MCA official data
│   ├── groqCompanyData.js  # AI extraction
│   ├── searchEngine.js     # Competitor discovery
│   ├── website.js          # Website analysis
│   ├── social.js           # Social media
│   └── reputation.js       # Reviews & news
└── .env                    # API keys
```

---

## Common Patterns

### Parse Revenue String
```javascript
function parseRevenue(revenueStr) {
  // "₹1,234 Crore" → 1234
  const croreMatch = revenueStr.match(/₹?\s*([\d.,]+)\s*Crore/i);
  if (croreMatch) {
    return parseFloat(croreMatch[1].replace(/,/g, ''));
  }
  
  // "₹187 Lakh" → 1.87
  const lakhMatch = revenueStr.match(/₹?\s*([\d.,]+)\s*Lakh/i);
  if (lakhMatch) {
    return parseFloat(lakhMatch[1].replace(/,/g, '')) / 100;
  }
  
  return null;
}
```

### Calculate CAGR (Compound Annual Growth Rate)
```javascript
function calculateCAGR(startRevenue, endRevenue, years) {
  // CAGR = ((End/Start)^(1/years) - 1) * 100
  if (!startRevenue || !endRevenue || years <= 0) return null;
  
  const growthFactor = endRevenue / startRevenue;
  const cagr = (Math.pow(growthFactor, 1/years) - 1) * 100;
  
  return parseFloat(cagr.toFixed(2));
}

// Example: Calculate 3-year CAGR
const cagr3y = calculateCAGR(
  revenueHistory[2].revenue_inr_crores,  // 3 years ago
  revenueHistory[0].revenue_inr_crores,  // current
  3
);
```

### Determine Revenue Trend
```javascript
function determineRevenueTrend(revenueHistory) {
  if (revenueHistory.length < 2) return "stable";
  
  let growingCount = 0;
  let decliningCount = 0;
  
  for (let i = 0; i < revenueHistory.length - 1; i++) {
    const current = revenueHistory[i].revenue_inr_crores;
    const previous = revenueHistory[i + 1].revenue_inr_crores;
    
    if (current > previous * 1.05) growingCount++;
    else if (current < previous * 0.95) decliningCount++;
  }
  
  if (growingCount > decliningCount) return "growing";
  if (decliningCount > growingCount) return "declining";
  return "stable";
}
```

### Calculate Company Age
```javascript
function calculateAge(incorporationDate) {
  // "09-11-2015" → 10 years
  const parts = incorporationDate.split(/[/-]/);
  let year;
  if (parts[0].length === 4) year = parseInt(parts[0]);
  else if (parts[2].length === 4) year = parseInt(parts[2]);
  
  return new Date().getFullYear() - year;
}
```

### Location Parser
```javascript
function parseLocation(address) {
  // Extract city, state, pincode from registered address
  const pinMatch = address.match(/(\d{6})/);
  const stateMatch = address.match(/,\s*([A-Za-z\s]+),\s*\d{6}/);
  
  return {
    city: null,  // Complex logic needed
    state: stateMatch ? stateMatch[1].trim() : null,
    pincode: pinMatch ? pinMatch[1] : null
  };
}
```

---

**Last Updated:** December 22, 2025  
**Version:** 1.0

