# 🚀 MarketML - Quick Start Card

## Application URL
🌐 **https://fuzzy-space-orbit-5gj4r4x5j44637q97-8000.app.github.dev/working.html**

---

## 🎯 Mode Selection Cheat Sheet

### For Testing/Demos (₹0)
```
Generation Mode: Template
Data Source:     Mock Data
LinkedIn Mode:   Skip
```
⚡ Speed: ~1 second  
💰 Cost: Free  
✅ Perfect for: Testing, demos, bulk generation

### For Production (₹1/persona)
```
Generation Mode: GPT-3.5-turbo
Data Source:     Google Search
LinkedIn Mode:   Skip
```
⚡ Speed: ~5 seconds  
💰 Cost: ~₹1  
✅ Perfect for: Most production use cases

### For Premium Clients (₹10/persona)
```
Generation Mode: GPT-4
Data Source:     Google Search
LinkedIn Mode:   Skip
```
⚡ Speed: ~8 seconds  
💰 Cost: ~₹10  
✅ Perfect for: High-value deals, executive personas

### For Maximum Quality (₹45/persona)
```
Generation Mode: GPT-4
Data Source:     Playwright
LinkedIn Mode:   Proxycurl
```
⚡ Speed: ~15 seconds  
💰 Cost: ~₹45  
✅ Perfect for: Enterprise clients, detailed research

---

## 🔧 Setup Commands

### Start Services
```bash
cd /workspaces/MarketML
bash start-simple.sh
```

### Stop Services
```bash
bash stop.sh
```

### Test All Modes
```bash
./test_modes.sh
```

### View Logs
```bash
tail -f logs/celery-worker.log
```

---

## 🔑 API Keys (Optional)

### Enable OpenAI (GPT-3.5/GPT-4)
```bash
# Edit .env file:
OPENAI_API_KEY=sk-proj-your-actual-key-here
```
Get key: https://platform.openai.com/api-keys  
Cost: $5-10/month for testing

### Enable Proxycurl (LinkedIn)
```bash
# Edit .env file:
PROXYCURL_API_KEY=your-proxycurl-key-here
```
Get key: https://nubela.co/proxycurl/  
Cost: $0.30-0.50 per lookup

### Install Playwright (Browser Automation)
```bash
pip install playwright
playwright install chromium
```

---

## 📊 Cost Calculator

| Volume | Template | GPT-3.5 | GPT-4 | GPT-4+Proxycurl |
|--------|----------|---------|-------|-----------------|
| 10     | ₹0       | ₹10     | ₹100  | ₹450            |
| 50     | ₹0       | ₹50     | ₹500  | ₹2,250          |
| 100    | ₹0       | ₹100    | ₹1,000| ₹4,500          |
| 500    | ₹0       | ₹500    | ₹5,000| ₹22,500         |

---

## 🧪 Test Sample Request

```bash
curl -X POST 'http://localhost:8000/v1/personas/generate' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Rahul Sharma",
    "location": "Mumbai, Maharashtra",
    "description": "Digital marketing agency owner",
    "generation_mode": "template",
    "data_source": "mock",
    "linkedin_mode": "skip"
  }'
```

---

## 📚 Documentation

- **Complete Guide:** [docs/MULTI_MODE_GUIDE.md](docs/MULTI_MODE_GUIDE.md)
- **Implementation:** [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)
- **API Docs:** https://your-domain/v1/docs
- **Quick Reference:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🔍 Monitoring

### Check OpenAI Usage
https://platform.openai.com/usage

### Check Proxycurl Credits
https://nubela.co/proxycurl/dashboard

### Check Job Status
```bash
curl http://localhost:8000/v1/jobs/{job_id}
```

### View Persona
```bash
curl http://localhost:8000/v1/personas/{persona_id}
```

---

## ⚠️ Important Notes

1. **Default Mode is FREE** - Template + Mock + Skip
2. **OpenAI Key Optional** - System works without it
3. **Automatic Fallback** - GPT modes fallback to Template
4. **No Breaking Changes** - Existing API calls still work
5. **Start Simple** - Test with free mode first

---

## 🎯 Recommended Workflow

### Day 1: Testing
- Use Template + Mock mode
- Test with 10-20 personas
- Verify UI and API working
- Cost: ₹0

### Day 2: Add OpenAI
- Get OpenAI API key ($5 credit)
- Test GPT-3.5 mode
- Compare quality with Template
- Cost: ~₹50-100 for 50-100 tests

### Day 3: Production
- Use GPT-3.5 for 80% of personas
- Use GPT-4 for premium clients
- Monitor costs daily
- Expected: ~₹500-1000/month for 500 personas

---

## 🆘 Troubleshooting

### Services Not Starting?
```bash
bash stop.sh
sleep 3
bash start-simple.sh
```

### OpenAI Not Working?
```bash
# Check if key is set
grep OPENAI_API_KEY .env

# View logs
tail -f logs/celery-worker.log
```

### Slow Performance?
- Use Template mode (1s vs 5-8s)
- Disable LinkedIn lookup
- Use Mock data source

---

## 📞 Quick Support

**Services Running?**
```bash
ps aux | grep -E "celery|uvicorn" | grep -v grep
```

**Redis Working?**
```bash
redis-cli ping
# Should return: PONG
```

**Database OK?**
```bash
ls -lh marketml.db
# Should exist and have size
```

---

**Last Updated:** 2025-12-20  
**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Commit:** 89be1fd
