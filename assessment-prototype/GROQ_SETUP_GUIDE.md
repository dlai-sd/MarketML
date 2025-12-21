# Groq AI + Google Custom Search - Quick Setup Guide

## 🎯 What's Working

Cost-effective AI-powered Indian company data extraction:
- **Groq API**: Llama 3.3 70B for AI extraction ($0.001/company)
- **Google Custom Search API**: Web search (100 free queries/day)
- **Cost**: 99% cheaper than API Setu (₹8-12 → $0.001 per company)

## ⚡ Quick Start

### 1. Configure API Keys

Edit `/assessment-prototype/.env`:

```bash
# Groq API (for AI extraction)
GROQ_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE

# Google Custom Search API (for web search)
GOOGLE_API_KEY=AIzaSy_YOUR_GOOGLE_API_KEY
GOOGLE_CX=YOUR_SEARCH_ENGINE_ID
```

### 2. Start Server

```bash
cd assessment-prototype
node server.js
```

### 3. Access Application

**Local**: http://localhost:3000/simple.html
**Codespace**: https://[codespace]-3000.app.github.dev/simple.html

## 🔧 Google Custom Search Setup

### Get API Key

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create credentials → API key
3. Enable API: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
4. Restrict to: Custom Search API

### Get Search Engine ID (CX)

1. Go to: https://programmablesearchengine.google.com/controlpanel/all
2. Click "Add" → Create search engine
3. Enable "Search the entire web"
4. Copy Search Engine ID

## 📊 How It Works

### Automatic Fallback Chain

1. **ZaubaCorp CIN Lookup** → Free, fastest
2. **Groq AI + Google Search** → $0.001/company (if no CIN found)
3. **Base Defaults** → For new/unknown companies

### Data Extraction

- CIN, Company Name, Registration Date
- Directors (DIN, appointment dates)
- Authorized/Paid-up Capital
- Revenue, Financial Year
- Status, ROC, Class
- Contact details (address, email, phone)

### Smart Rating

**Complete Data** (CIN found):
```json
{
  "cin": "L85110KA1981PLC013115",
  "company_name": "INFOSYS LIMITED",
  "data_quality": "complete"
}
```

**Limited Data** (new/unknown company):
```json
{
  "status": "Active (Assumed)",
  "authorized_capital": "100000",
  "data_quality": "limited",
  "notes": "Rating based on assumptions"
}
```

## 🎯 Test Companies

- ✅ **Infosys** → Full CIN data
- ✅ **Yashus Digital Marketing** → CIN: U74120PN2015PTC157176
- ✅ **DLAI Satellite Data** → Limited data, base defaults applied

## 💰 Cost Savings

| Solution | Per Company | Monthly (500/day) |
|----------|-------------|-------------------|
| Groq + Google | $0.001 | $5-15 |
| API Setu | ₹8-12 | ₹120K-180K |
| **Savings** | **99%** | **$1,500-2,200** |

## 📁 Key Files

- `scrapers/groqCompanyData.js` - AI extractor (353 lines)
- `server.js` - Backend API (enhanced with Groq)
- `public/simple.html` - Assessment UI (shows 🤖 badges)
- `.env` - API keys configuration

## ✅ Status

- ✅ Groq API working
- ✅ Google Custom Search API enabled
- ✅ Fallback chain implemented
- ✅ Base defaults for limited data
- ✅ Data quality indicators added
- ✅ UI showing AI-enhanced results

## 🚀 Next Steps

When formal API provider available:
1. System auto-switches to real API
2. Base defaults replaced with actual data
3. Data quality upgrades to 'complete'

---

**Last Updated**: Dec 21, 2025
**Working Environment**: GitHub Codespaces
