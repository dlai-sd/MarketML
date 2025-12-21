# Groq-Powered Company Data Extractor

## 🎯 Overview

AI-powered Indian company data extraction using Groq API + web search - **99% cheaper** than traditional MCA API services.

## 💰 Cost Comparison (500 companies/day = 15,000/month)

| Provider | Monthly Cost | Per Company | Notes |
|----------|--------------|-------------|-------|
| **Groq + Web Search** | **$5-15** | **$0.001** | ✅ Recommended |
| API Setu Enterprise | ₹120K-180K ($1,500-2,200) | ₹8-12 | Too expensive |
| Private API Providers | ₹15K-30K ($180-360) | ₹1-2 | Medium cost |
| MCA21 Direct | ₹750K+ ($9,000+) | ₹50 | Not suitable for bulk |

## ⚡ Architecture

```
Company Name → Google Search (4 queries) → Groq AI Extraction → Structured JSON
```

### Search Queries (per company):
1. `{Company} MCA India CIN registration`
2. `{Company} directors revenue financial year`
3. `{Company} authorized capital paid up capital`
4. `{Company} ZaubaCorp company details`

### Groq Processing:
- Model: `llama-3.3-70b-versatile`
- Speed: 300+ tokens/second
- Cost: $0.59 per 1M tokens (~$0.0006 per company)
- Response: Structured JSON with validated data

## 📊 Data Extracted

```json
{
  "cin": "U12345XX2020PTC123456",
  "company_name": "Official registered name",
  "registration_date": "DD-MM-YYYY",
  "status": "Active/Strike Off/Amalgamated",
  "roc": "Registrar of Companies location",
  "company_class": "Private/Public",
  "authorized_capital": "Amount in INR",
  "paid_up_capital": "Amount in INR",
  "financial_year": "FY 2023-24",
  "latest_revenue": "Revenue in INR Crores",
  "pan": "PAN number",
  "directors": [
    {
      "name": "Director name",
      "din": "Director Identification Number",
      "appointment_date": "DD-MM-YYYY"
    }
  ],
  "address": "Registered office address",
  "email": "Contact email",
  "phone": "Contact phone",
  "confidence": "high/medium/low"
}
```

## 🚀 Quick Start

### 1. Get Groq API Key (Free!)
```bash
# Visit: https://console.groq.com/keys
# Sign up and create API key
# Free tier: Generous rate limits
```

### 2. Set Environment Variable
```bash
export GROQ_API_KEY="gsk_your_api_key_here"
```

### 3. Start Server
```bash
cd assessment-prototype
npm install
node server.js
```

### 4. Test the Service

**Web Interface:**
```bash
# Open in browser:
http://localhost:3000/groq-test.html
```

**Command Line:**
```bash
# Test with Yashus Digital Marketing
curl -X POST http://localhost:3000/api/company-data/groq \
  -H "Content-Type: application/json" \
  -d '{"companyName":"Yashus Digital Marketing"}'

# Test with DLAI Satellite Data
curl -X POST http://localhost:3000/api/company-data/groq \
  -H "Content-Type: application/json" \
  -d '{"companyName":"DLAI Satellite Data"}'
```

**JavaScript/Node.js:**
```javascript
const axios = require('axios');

async function getCompanyData(companyName) {
    const response = await axios.post('http://localhost:3000/api/company-data/groq', {
        companyName: companyName
    });
    
    return response.data;
}

// Usage
const data = await getCompanyData('Yashus Digital Marketing');
console.log(data);
```

**Python:**
```python
import requests

def get_company_data(company_name):
    response = requests.post(
        'http://localhost:3000/api/company-data/groq',
        json={'companyName': company_name}
    )
    return response.json()

# Usage
data = get_company_data('Yashus Digital Marketing')
print(data)
```

## 📁 File Structure

```
assessment-prototype/
├── scrapers/
│   └── groqCompanyData.js      # Main extractor class
├── public/
│   └── groq-test.html          # Test web interface
├── server.js                    # API endpoint
└── README_GROQ.md              # This file
```

## 🔧 API Endpoints

### Extract Company Data
```
POST /api/company-data/groq
Content-Type: application/json

{
  "companyName": "Yashus Digital Marketing"
}
```

**Response:**
```json
{
  "success": true,
  "company_name": "Yashus Digital Marketing",
  "data": {
    "cin": "U74999DL2020PTC123456",
    "company_name": "Yashus Digital Marketing Private Limited",
    "status": "Active",
    "latest_revenue": "₹1.87 Crore",
    "financial_year": "FY 2023-24",
    "directors": [...],
    ...
  },
  "sources": ["https://...", "https://..."],
  "timestamp": "2025-12-21T10:30:00.000Z"
}
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required for Groq extraction
GROQ_API_KEY=gsk_your_api_key_here

# Optional: Alternative model
GROQ_MODEL=llama-3.3-70b-versatile  # Default, fastest
# Or: mixtral-8x7b-32768  # Even cheaper ($0.24/M tokens)
```

### Rate Limits
- **Google Search**: ~10 requests/minute (self-imposed)
- **Groq API**: 
  - Free tier: 30 requests/minute
  - Paid: Up to 400+ requests/minute

## 🎯 Use Cases

### 1. Lead Enrichment
```javascript
const leads = ['Company A', 'Company B', 'Company C'];

for (const company of leads) {
    const data = await extractor.extractCompanyData(company);
    // Save to CRM with CIN, revenue, directors
}
```

### 2. Due Diligence
```javascript
// Verify company status and financials
const data = await extractor.extractCompanyData('Target Company');
if (data.success && data.data.status === 'Active') {
    console.log(`Revenue: ${data.data.latest_revenue}`);
    console.log(`Directors: ${data.data.directors.length}`);
}
```

### 3. Market Research
```javascript
// Analyze competitor financials
const competitors = ['Comp1', 'Comp2', 'Comp3'];
const analysis = await Promise.all(
    competitors.map(c => extractor.extractCompanyData(c))
);
```

## 🔍 Data Quality

### Confidence Levels
- **High**: CIN found, multiple sources confirm data
- **Medium**: Partial data, 1-2 sources
- **Low**: Limited data, fallback extraction used

### Validation
- CIN format: `^[A-Z][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$`
- Revenue converted to standard format (Crores/Millions)
- Director DIN validated when available

## 🐛 Troubleshooting

### "GROQ_API_KEY not configured"
```bash
# Set the environment variable
export GROQ_API_KEY="your_key_here"

# Or add to .env file
echo "GROQ_API_KEY=your_key_here" >> .env
```

### "No search results found"
- Company name might be misspelled
- Try with full registered name
- Check if company exists in public records

### "Rate limit exceeded"
- Add delays between requests
- Upgrade to Groq paid tier
- Implement request queuing

## 📈 Performance

### Typical Extraction Time
- Google searches: 4-8 seconds
- Groq processing: 2-4 seconds
- **Total: 6-12 seconds per company**

### Optimization Tips
1. **Batch processing**: Process multiple companies in parallel
2. **Caching**: Store results for 24-48 hours
3. **Smart search**: Skip search if CIN is known

## 💡 Advanced Usage

### Custom Search Strategies
```javascript
// Override search queries
extractor.customSearches = [
    `${companyName} site:zaubacorp.com`,
    `${companyName} MCA India`,
    `${companyName} company revenue FY2024`
];
```

### Fallback to Regex Extraction
```javascript
// If Groq fails, basic regex extraction is used
const data = await extractor.extractCompanyData(company);
// data.extraction_method will show 'fallback_regex' or 'groq_web_search'
```

## 🔐 Security Notes

- Never commit API keys to git
- Use environment variables for credentials
- Implement rate limiting for production
- Add request validation and sanitization

## 📝 License

MIT - Use freely for commercial and non-commercial projects

## 🤝 Support

For issues or questions:
1. Check server logs: `node server.js`
2. Test with web interface: `/groq-test.html`
3. Verify GROQ_API_KEY is set correctly

## 🚀 Next Steps

1. Add caching layer (Redis)
2. Implement retry logic
3. Add webhook notifications
4. Create bulk processing queue
5. Build dashboard for monitoring

---

**Built with ❤️ using Groq AI and modern web scraping**
