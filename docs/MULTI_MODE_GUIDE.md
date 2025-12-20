# Multi-Mode Persona Generation Guide

## Overview

MarketML now supports **3 configurable modes** for persona generation, allowing you to balance between cost, quality, and data freshness.

## 🎯 Generation Modes

### 1. **Template Mode** (Free, Fast)
- **Cost:** ₹0 per persona
- **Speed:** ~1-2 seconds
- **Quality:** Good for testing and basic personas
- **Use When:** 
  - Testing the system
  - Budget constraints
  - High volume generation needed
  - Acceptable for initial outreach

### 2. **GPT-3.5-Turbo Mode** (Affordable, Balanced)
- **Cost:** ~₹0.60-1.20 per persona (~$0.01 USD)
- **Speed:** ~3-5 seconds
- **Quality:** High-quality narratives with natural language
- **Use When:**
  - Need compelling marketing copy
  - Mid-tier client proposals
  - Better engagement rates desired
  - Budget allows for AI enhancement

**Pricing Breakdown:**
- Input tokens: ~500 tokens @ $0.0005/1k = $0.00025
- Output tokens: ~800 tokens @ $0.0015/1k = $0.0012
- **Total: ~$0.0014 per persona (₹0.12)**

### 3. **GPT-4 Mode** (Premium, Best Quality)
- **Cost:** ~₹8-12 per persona (~$0.10-0.15 USD)
- **Speed:** ~5-8 seconds
- **Quality:** Best-in-class narratives with deep insights
- **Use When:**
  - Premium client presentations
  - Complex B2B personas
  - Executive-level proposals
  - Maximum ROI needed

**Pricing Breakdown:**
- Input tokens: ~500 tokens @ $0.01/1k = $0.005
- Output tokens: ~800 tokens @ $0.03/1k = $0.024
- **Total: ~$0.029 per persona (₹2.40)**

## 📊 Data Source Modes

### 1. **Mock Data** (Free, Instant)
- **Cost:** ₹0 per lookup
- **Speed:** Instant
- **Accuracy:** Template-based, good for demos
- **Data Freshness:** Static templates

### 2. **Google Search** (Free*, Rate Limited)
- **Cost:** ₹0 per search (*may hit rate limits)
- **Speed:** ~2-3 seconds per search
- **Accuracy:** Real company websites and public data
- **Data Freshness:** Current web data
- **Limitations:**
  - Rate limited (1-2 searches/sec)
  - May be blocked if overused
  - Requires `googlesearch-python` package

### 3. **Playwright Scraping** (Free, Slower)
- **Cost:** ₹0 per scrape
- **Speed:** ~5-10 seconds per page
- **Accuracy:** High - renders JavaScript
- **Data Freshness:** Real-time
- **Limitations:**
  - Requires Playwright browser installation
  - Higher resource usage
  - Slower for bulk operations
  - May trigger anti-bot detection

## 🔗 LinkedIn Modes

### 1. **Skip** (Free, No LinkedIn Data)
- **Cost:** ₹0
- **Speed:** N/A (no scraping)
- **Use When:** LinkedIn data not needed

### 2. **Basic** (Free, Limited Data)
- **Cost:** ₹0
- **Speed:** ~5-8 seconds
- **Data:** Public profile headline, location, current company
- **Limitations:**
  - Only works for public profiles
  - Requires Playwright setup
  - May be detected as bot
  - Limited data compared to Proxycurl

### 3. **Proxycurl** (Paid, Full Data)
- **Cost:** ₹25-42 per lookup (~$0.30-0.50 USD)
- **Speed:** ~2-3 seconds
- **Data:** Full profile (experience, education, skills, etc.)
- **Reliability:** Official API, no blocking
- **Pricing:** 
  - Standard: $0.30 per profile
  - Premium: $0.50 per profile with richer data

## 💰 Cost Comparison per Persona

| Mode Combination | Total Cost | Best For |
|-----------------|------------|----------|
| Template + Mock + Skip | **₹0** | Testing, demos, bulk generation |
| Template + Google + Skip | **₹0** | Real data, budget-conscious |
| GPT-3.5 + Google + Skip | **₹0.60-1.20** | Balanced quality & cost |
| GPT-4 + Google + Skip | **₹8-12** | Premium quality |
| GPT-3.5 + Google + Proxycurl | **₹25-43** | Full LinkedIn + AI copy |
| GPT-4 + Playwright + Proxycurl | **₹33-54** | Maximum quality & data |

## 🚀 Setup Instructions

### 1. OpenAI API Setup

```bash
# Get API key from https://platform.openai.com/api-keys
# Add to .env file:
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**Cost Control Tips:**
- Use GPT-3.5 for routine generation (10x cheaper than GPT-4)
- Set monthly spending limits in OpenAI dashboard
- Monitor usage at https://platform.openai.com/usage
- Start with $5-10/month test budget

### 2. Google Search Setup

```bash
# Install package
pip install googlesearch-python

# No API key needed, but:
# - Limited to 1-2 requests/sec
# - May be blocked if overused
# - Consider Google Custom Search API for production
```

### 3. Playwright Setup

```bash
# Install Playwright
pip install playwright

# Install browsers
playwright install chromium

# Optional: Install all browsers
playwright install
```

### 4. Proxycurl Setup (Optional)

```bash
# Get API key from https://nubela.co/proxycurl/
# Add to .env:
PROXYCURL_API_KEY=your-proxycurl-key-here
```

**Proxycurl Pricing:**
- Pay-as-you-go: $0.30-0.50 per profile
- Subscription plans available
- Free tier: 10 credits for testing

## 📈 Recommended Configurations

### For Development/Testing
```javascript
generation_mode: "template"
data_source: "mock"
linkedin_mode: "skip"
// Cost: ₹0, Speed: <2s
```

### For Production (Budget)
```javascript
generation_mode: "gpt-3.5"
data_source: "google"
linkedin_mode: "skip"
// Cost: ~₹1, Speed: ~5s
```

### For Production (Premium)
```javascript
generation_mode: "gpt-4"
data_source: "google"
linkedin_mode: "basic"
// Cost: ~₹10, Speed: ~10s
```

### For Maximum Quality
```javascript
generation_mode: "gpt-4"
data_source: "playwright"
linkedin_mode: "proxycurl"
// Cost: ~₹45, Speed: ~15s
```

## 🔧 Configuration File

Update `.env` with your API keys:

```bash
# Required for GPT modes
OPENAI_API_KEY=sk-proj-your-key-here

# Optional for LinkedIn Proxycurl mode
PROXYCURL_API_KEY=your-proxycurl-key-here

# Google Search (no key needed, uses free search)
# Playwright (no key needed, uses browser automation)
```

## 📊 Monthly Cost Estimates

### Scenario 1: Small Business (50 personas/month)
- **Template + Mock:** ₹0/month
- **GPT-3.5 + Google:** ₹30-60/month
- **GPT-4 + Google:** ₹400-600/month
- **GPT-4 + Proxycurl:** ₹1,650-2,700/month

### Scenario 2: Agency (500 personas/month)
- **Template + Mock:** ₹0/month
- **GPT-3.5 + Google:** ₹300-600/month
- **GPT-4 + Google:** ₹4,000-6,000/month
- **GPT-4 + Proxycurl:** ₹16,500-27,000/month

### Scenario 3: Enterprise (5000 personas/month)
- **Template + Mock:** ₹0/month
- **GPT-3.5 + Google:** ₹3,000-6,000/month
- **GPT-4 + Google:** ₹40,000-60,000/month
- **Mixed (70% GPT-3.5, 30% GPT-4):** ₹14,000-20,000/month

## ⚡ Performance Benchmarks

| Configuration | Speed | Quality Score | Cost Efficiency |
|--------------|-------|---------------|-----------------|
| Template + Mock | ⭐⭐⭐⭐⭐ (1s) | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| GPT-3.5 + Google | ⭐⭐⭐⭐ (5s) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| GPT-4 + Google | ⭐⭐⭐ (8s) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GPT-4 + Proxycurl | ⭐⭐⭐ (10s) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🛡️ Best Practices

1. **Start with Template mode** for testing
2. **Use GPT-3.5 for 80% of personas** (cost-effective)
3. **Reserve GPT-4 for premium clients** (high-value deals)
4. **Monitor OpenAI usage** regularly
5. **Set spending alerts** in OpenAI dashboard
6. **Cache results** to avoid re-generating same persona
7. **Batch process** during off-peak hours
8. **Use Proxycurl sparingly** (most expensive option)

## 🔍 Debugging

### Check which mode was used:
```bash
curl http://localhost:8000/v1/personas/{persona_id} | jq '.generation_mode_used'
```

### Test modes:
```bash
# Run test script
./test_modes.sh
```

### Monitor costs:
- OpenAI: https://platform.openai.com/usage
- Proxycurl: https://nubela.co/proxycurl/dashboard

## 📞 Support

For issues or questions:
- Check logs: `logs/celery-worker.log`
- API docs: https://your-domain/v1/docs
- Test modes: `bash test_modes.sh`

---

**Last Updated:** 2025-12-20
**Version:** 1.0.0
