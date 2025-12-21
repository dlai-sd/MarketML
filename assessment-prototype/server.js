// Load environment variables
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');
const cheerio = require('cheerio');

// Import real scrapers
const { discoverCompetitors, searchCompanyMatches, extractRevenueFromWikipedia } = require('./scrapers/searchEngine');
const { discoverCompetitorsIntelligently } = require('./scrapers/intelligentCompetitorDiscovery');
const { analyzeWebsite } = require('./scrapers/website');
const { analyzeSocialMedia } = require('./scrapers/social');
const { analyzeReputation } = require('./scrapers/reputation');
const { searchIndianCompany, isValidCIN } = require('./scrapers/indianCompany');

// Import Groq-powered company data extractor
const GroqCompanyExtractor = require('./scrapers/groqCompanyData');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// In-memory job store
const jobs = {};

// Industry classification keywords
const INDUSTRY_KEYWORDS = {
    'SaaS/Tech': ['software', 'saas', 'platform', 'cloud', 'api', 'app', 'solution', 'technology', 'tech', 'digital'],
    'E-commerce': ['shop', 'store', 'buy', 'product', 'retail', 'cart', 'ecommerce', 'marketplace', 'online store'],
    'Professional Services': ['consulting', 'agency', 'services', 'expert', 'advisory', 'legal', 'accounting', 'marketing'],
    'Manufacturing': ['manufacturing', 'industrial', 'equipment', 'machinery', 'factory', 'production', 'supplier'],
    'Healthcare': ['health', 'medical', 'care', 'clinic', 'hospital', 'wellness', 'pharma', 'healthcare'],
    'Financial Services': ['finance', 'banking', 'investment', 'insurance', 'wealth', 'fintech', 'financial'],
    'Real Estate': ['real estate', 'property', 'homes', 'rental', 'listings', 'realty', 'housing'],
    'Education': ['education', 'learning', 'training', 'course', 'university', 'school', 'elearning'],
    'Media/Publishing': ['media', 'news', 'publishing', 'content', 'entertainment', 'broadcast', 'journalism'],
    'Hospitality': ['hotel', 'restaurant', 'travel', 'tourism', 'booking', 'hospitality', 'accommodation']
};

// Business model detection keywords
const BUSINESS_MODEL_KEYWORDS = {
    'B2B': ['enterprise', 'business', 'b2b', 'corporate', 'professional', 'organization', 'company'],
    'B2C': ['consumer', 'customer', 'personal', 'individual', 'b2c', 'buy now', 'shop now']
};

// Tier-dependent weights
const TIER_WEIGHTS = {
    small: {
        content_marketing: 0.20,
        seo_presence: 0.20,
        social_engagement: 0.15,
        conversion_signals: 0.20,
        brand_authority: 0.05,
        technical_optimization: 0.10,
        thought_leadership: 0.10
    },
    medium: {
        content_marketing: 0.20,
        seo_presence: 0.20,
        social_engagement: 0.15,
        conversion_signals: 0.15,
        brand_authority: 0.10,
        technical_optimization: 0.10,
        thought_leadership: 0.10
    },
    large: {
        content_marketing: 0.10,
        seo_presence: 0.20,
        social_engagement: 0.15,
        conversion_signals: 0.15,
        brand_authority: 0.20,
        technical_optimization: 0.10,
        thought_leadership: 0.10
    }
};

// Simple scoring thresholds (rule-based)
function scoreMetric(value, thresholds) {
    if (value >= thresholds[6]) return 7;
    if (value >= thresholds[5]) return 6;
    if (value >= thresholds[4]) return 5;
    if (value >= thresholds[3]) return 4;
    if (value >= thresholds[2]) return 3;
    if (value >= thresholds[1]) return 2;
    return 1;
}

// Real web scraping
async function scrapeEntity(entityName, jobId) {
    updateJobProgress(jobId, `Scraping data for ${entityName}...`);
    
    try {
        // Run all scrapers in parallel
        const [websiteData, socialData, reputationData] = await Promise.all([
            analyzeWebsite(entityName),
            analyzeSocialMedia(entityName),
            analyzeReputation(entityName)
        ]);
        
        // Combine all data
        const combinedData = {
            // Content Marketing
            blog_posts_per_month: estimateBlogFrequency(websiteData),
            content_pages: websiteData.content_pages || 0,
            
            // SEO Presence
            domain_authority: reputationData.domain_authority || 0,
            backlinks: reputationData.backlinks_estimate || 0,
            
            // Social Engagement
            social_followers: socialData.estimated_followers || 0,
            active_platforms: socialData.active_platforms || 0,
            engagement_rate: socialData.estimated_engagement || 0,
            
            // Conversion Signals
            conversion_indicators: calculateConversionScore(websiteData),
            has_cta: websiteData.has_cta,
            has_testimonials: websiteData.has_testimonials,
            
            // Brand Authority
            media_mentions: reputationData.news_mentions || 0,
            recent_news: reputationData.recent_news || false,
            review_count: reputationData.review_count || 0,
            average_rating: reputationData.average_rating || 0,
            
            // Technical Optimization
            page_speed: estimatePageSpeed(websiteData),
            mobile_optimized: websiteData.mobile_optimized,
            has_analytics: websiteData.has_analytics,
            structured_data: websiteData.has_structured_data,
            
            // Thought Leadership
            speaking_engagements: reputationData.thought_leadership ? 5 : 0,
            linkedin_presence: socialData.linkedin?.has_page || false,
            
            // Raw data for reference
            website: websiteData,
            social: socialData,
            reputation: reputationData
        };
        
        return combinedData;
        
    } catch (error) {
        console.error(`Scraping failed for ${entityName}:`, error);
        // Return minimal data on error
        return {
            blog_posts_per_month: 0,
            domain_authority: 0,
            social_followers: 0,
            conversion_indicators: 0,
            media_mentions: 0,
            page_speed: 50,
            speaking_engagements: 0
        };
    }
}

function estimateBlogFrequency(websiteData) {
    if (!websiteData.has_blog) return 0;
    // Estimate based on content pages
    const pages = websiteData.content_pages || 0;
    if (pages > 50) return 12; // Weekly+
    if (pages > 30) return 8;
    if (pages > 15) return 4;
    if (pages > 5) return 2;
    return 1;
}

function calculateConversionScore(websiteData) {
    let score = 0;
    if (websiteData.has_cta) score += 3;
    if (websiteData.has_testimonials) score += 2;
    if (websiteData.has_analytics) score += 2;
    if (websiteData.meta_description) score += 1;
    if (websiteData.social_links > 0) score += 1;
    return Math.min(score, 10);
}

function estimatePageSpeed(websiteData) {
    if (!websiteData.page_size) return 50;
    // Smaller pages generally faster
    if (websiteData.page_size < 100000) return 90;
    if (websiteData.page_size < 500000) return 75;
    if (websiteData.page_size < 1000000) return 60;
    return 50;
}

// Wrapper for intelligent competitor discovery
async function discoverCompetitorsWrapper(subject, jobId) {
    updateJobProgress(jobId, 'Analyzing business and discovering competitors...');
    
    try {
        // Use intelligent multi-dimensional discovery
        console.log(`[Server] Starting intelligent competitor discovery for: ${subject}`);
        const intelligentCompetitors = await discoverCompetitorsIntelligently(subject);
        
        if (intelligentCompetitors.length > 0) {
            console.log(`[Server] Intelligent discovery found ${intelligentCompetitors.length} competitors`);
            updateJobProgress(jobId, `Found ${intelligentCompetitors.length} competitors via intelligent analysis`);
            
            // Return in expected format
            return intelligentCompetitors.map(comp => comp.name);
        }
        
        // Fallback to Wikipedia-only if intelligent discovery fails
        console.log('[Server] Falling back to Wikipedia search...');
        updateJobProgress(jobId, 'Searching Wikipedia for competitors...');
        const wikiCompetitors = await discoverCompetitors(subject);
        
        if (wikiCompetitors.length > 0) {
            console.log(`[Server] Wikipedia found ${wikiCompetitors.length} competitors`);
            return wikiCompetitors;
        }
        
        // No competitors found from any source
        console.log('[Server] No competitors found from any source');
        updateJobProgress(jobId, 'No competitor data available');
        return [];
        
    } catch (error) {
        console.error('[Server] Competitor discovery failed:', error);
        return [];
    }
}

// Determine business tier based on signals
function determineTier(data, companyName = '', revenue = null) {
    const name = companyName.toLowerCase();
    
    // Known large companies (Fortune 500, major tech)
    const knownLargeCompanies = ['google', 'microsoft', 'amazon', 'facebook', 'meta', 'apple', 'salesforce', 'hubspot', 'oracle', 'adobe', 'ibm', 'intel', 'cisco'];
    if (knownLargeCompanies.some(company => name.includes(company))) {
        return 'large';
    }
    
    // Revenue is the strongest signal (in millions USD)
    if (revenue !== null && revenue > 0) {
        if (revenue >= 1000) return 'large';      // $1B+ revenue
        if (revenue >= 100) return 'medium';      // $100M - $1B revenue
        if (revenue >= 10) return 'medium';       // $10M - $100M revenue
        return 'small';                           // < $10M revenue
    }
    
    // Domain Authority is a strong signal (0-100 scale)
    const da = data.domain_authority || 0;
    const followers = data.social_followers || 0;
    const mentions = data.media_mentions || 0;
    
    // High DA indicates established/large company
    if (da >= 70) return 'large';
    if (da >= 50) return 'medium';
    
    // Weighted scoring (DA is most reliable)
    const weightedScore = (da * 50) + followers + (mentions * 100);
    
    if (weightedScore > 5000) return 'large';
    if (weightedScore > 1000) return 'medium';
    return 'small';
}

// Detect industry from website content
function detectIndustry(websiteData, companyName) {
    const textContent = [
        websiteData.meta_description || '',
        companyName.toLowerCase(),
        JSON.stringify(websiteData).toLowerCase()
    ].join(' ');
    
    let maxMatches = 0;
    let detectedIndustry = 'General';
    
    for (const [industry, keywords] of Object.entries(INDUSTRY_KEYWORDS)) {
        const matches = keywords.filter(keyword => textContent.includes(keyword.toLowerCase())).length;
        if (matches > maxMatches) {
            maxMatches = matches;
            detectedIndustry = industry;
        }
    }
    
    return maxMatches >= 2 ? detectedIndustry : 'General';
}

// Detect business model (B2B, B2C, B2B2C)
function detectBusinessModel(websiteData) {
    const textContent = [
        websiteData.meta_description || '',
        JSON.stringify(websiteData).toLowerCase()
    ].join(' ');
    
    let b2bScore = 0;
    let b2cScore = 0;
    
    BUSINESS_MODEL_KEYWORDS['B2B'].forEach(keyword => {
        if (textContent.includes(keyword.toLowerCase())) b2bScore++;
    });
    
    BUSINESS_MODEL_KEYWORDS['B2C'].forEach(keyword => {
        if (textContent.includes(keyword.toLowerCase())) b2cScore++;
    });
    
    if (b2bScore > b2cScore * 1.5) return 'B2B';
    if (b2cScore > b2bScore * 1.5) return 'B2C';
    if (b2bScore > 0 && b2cScore > 0) return 'B2B2C';
    
    // Default to B2B if unclear (safer assumption)
    return 'B2B';
}

// Score each dimension with context-aware adjustments
function scoreDimensions(data, tier, industry, businessModel, companyData = {}) {
    // Base scores
    const baseScores = {
        content_marketing: scoreMetric(data.blog_posts_per_month, [0, 1, 3, 5, 8, 12, 16]),
        seo_presence: scoreMetric(data.domain_authority, [0, 20, 35, 50, 65, 75, 85]),
        social_engagement: scoreMetric(data.social_followers, [0, 1000, 5000, 15000, 40000, 75000, 100000]),
        conversion_signals: scoreMetric(data.conversion_indicators, [0, 1, 2, 4, 6, 8, 9]),
        brand_authority: scoreMetric(data.media_mentions, [0, 2, 5, 10, 20, 35, 45]),
        technical_optimization: scoreMetric(data.page_speed, [0, 50, 60, 70, 80, 90, 95]),
        thought_leadership: scoreMetric(data.speaking_engagements, [0, 1, 2, 4, 7, 10, 13])
    };
    
    // Apply content marketing adjustments based on context
    baseScores.content_marketing = adjustContentMarketingScore(
        baseScores.content_marketing,
        data.blog_posts_per_month,
        tier,
        industry,
        businessModel,
        companyData
    );
    
    // Apply social engagement adjustments for B2B
    if (businessModel === 'B2B') {
        baseScores.social_engagement = Math.min(7, Math.ceil(baseScores.social_engagement * 1.3));
    }
    
    return baseScores;
}

// Context-aware content marketing scoring with company financials
function adjustContentMarketingScore(baseScore, postsPerMonth, tier, industry, businessModel, companyData = {}) {
    let adjustedScore = baseScore;
    
    // B2B adjustment: Lower frequency expectations
    if (businessModel === 'B2B' && postsPerMonth >= 4) {
        adjustedScore = Math.min(7, adjustedScore + 1);
    }
    
    // Industry-specific adjustments
    const lowFrequencyIndustries = ['Professional Services', 'Manufacturing', 'Healthcare', 'Financial Services'];
    if (lowFrequencyIndustries.includes(industry) && postsPerMonth >= 4) {
        adjustedScore = Math.min(7, adjustedScore + 1);
    }
    
    // Small tier bonus for any consistent content
    if (tier === 'small' && postsPerMonth >= 2) {
        adjustedScore = Math.min(7, adjustedScore + 0.5);
    }
    
    // NEW: Company maturity bonus (from incorporation date)
    if (companyData.age_years) {
        // Startups (< 3 years): More lenient scoring
        if (companyData.age_years < 3 && postsPerMonth >= 2) {
            adjustedScore = Math.min(7, adjustedScore + 1);
        }
        // Established companies (> 10 years): Higher expectations
        else if (companyData.age_years > 10 && postsPerMonth < 4) {
            adjustedScore = Math.max(1, adjustedScore - 0.5);
        }
    }
    
    // NEW: Financial health indicator
    if (companyData.revenue_millions) {
        // High revenue companies should have consistent content
        if (companyData.revenue_millions > 50 && postsPerMonth < 4) {
            adjustedScore = Math.max(1, adjustedScore - 1);
        }
        // Growing companies with good content get boost
        else if (companyData.revenue_millions > 5 && companyData.revenue_millions < 50 && postsPerMonth >= 4) {
            adjustedScore = Math.min(7, adjustedScore + 0.5);
        }
    }
    
    // NEW: Company status check (for Indian companies)
    if (companyData.status === 'Active' && companyData.cin) {
        // Active registered company gets credibility bonus
        if (postsPerMonth >= 2) {
            adjustedScore = Math.min(7, adjustedScore + 0.5);
        }
    }
    
    // NEW: Leadership indicator (directors count)
    if (companyData.directors_count) {
        // Multiple directors = larger org = higher expectations
        if (companyData.directors_count >= 3 && postsPerMonth < 4) {
            adjustedScore = Math.max(1, adjustedScore - 0.5);
        }
        // Solo/small team with consistent content gets boost
        else if (companyData.directors_count <= 2 && postsPerMonth >= 4) {
            adjustedScore = Math.min(7, adjustedScore + 0.5);
        }
    }
    
    return Math.round(adjustedScore);
}

// Calculate weighted average score
function calculateOverallScore(dimensions, tier) {
    const weights = TIER_WEIGHTS[tier];
    let weightedSum = 0;
    
    for (const [dimension, score] of Object.entries(dimensions)) {
        weightedSum += score * weights[dimension];
    }
    
    return Math.round(weightedSum * 10) / 10; // Round to 1 decimal
}

// Analyze a single entity
async function analyzeEntity(entityName, jobId) {
    const data = await scrapeEntity(entityName, jobId);
    
    // Try to get revenue from multiple sources
    let revenue = null;
    let revenueSource = null;
    let cin = null;
    let revenueINR = null;
    let revenueDisplay = null;
    let companyStatus = null;
    let companyAddress = null;
    let companyEmail = null;
    let companyPhone = null;
    let companyPAN = null;
    let companyDirectors = [];
    let authorizedCapital = null;
    let paidUpCapital = null;
    let dateOfIncorporation = null;
    let companyROC = null;
    let companyClass = null;
    let financialYear = null;
    
    // First try Indian company CIN lookup (most accurate for Indian companies)
    try {
        const indianResults = await searchIndianCompany(entityName);
        if (indianResults.length > 0) {
            const indianCompany = indianResults[0];
            cin = indianCompany.cin;
            companyStatus = indianCompany.status;
            companyAddress = indianCompany.address;
            companyEmail = indianCompany.email;
            companyPhone = indianCompany.phone;
            companyPAN = indianCompany.pan;
            companyDirectors = indianCompany.directors || [];
            authorizedCapital = indianCompany.authorized_capital;
            paidUpCapital = indianCompany.paid_up_capital;
            dateOfIncorporation = indianCompany.date_of_incorporation;
            companyROC = indianCompany.roc;
            companyClass = indianCompany.company_class;
            financialYear = indianCompany.financial_year;
            
            if (indianCompany.revenue_usd_millions) {
                revenue = indianCompany.revenue_usd_millions;
                revenueINR = indianCompany.revenue_inr_millions;
                revenueDisplay = indianCompany.revenue_display;
                revenueSource = 'MCA (CIN)';
                console.log(`[Revenue] ${entityName}: $${revenue}M (from CIN: ${cin})`);
            }
        }
    } catch (error) {
        console.error(`Failed to extract CIN revenue for ${entityName}:`, error.message);
    }
    
    // Fallback to Wikipedia if no CIN revenue
    if (!revenue) {
        try {
            revenue = await extractRevenueFromWikipedia(entityName);
            if (revenue) {
                revenueSource = 'Wikipedia';
                console.log(`[Revenue] ${entityName}: $${revenue}M (from Wikipedia)`);
            }
        } catch (error) {
            console.error(`Failed to extract Wikipedia revenue for ${entityName}:`, error.message);
        }
    }
    
    const tier = determineTier(data, entityName, revenue);
    
    // Detect industry and business model
    const industry = detectIndustry(data.website || {}, entityName);
    let businessModel = detectBusinessModel(data.website || {});
    
    // Format business model with slashes for readability
    if (businessModel === 'B2B2C') {
        businessModel = 'B2B/B2C';
    }
    
    // Calculate company age from incorporation date
    let companyAge = null;
    if (dateOfIncorporation) {
        try {
            // Parse date (handles formats like "15/03/2015", "15-03-2015", "2015-03-15")
            const parts = dateOfIncorporation.split(/[/-]/);
            let year;
            if (parts[0].length === 4) {
                year = parseInt(parts[0]);
            } else if (parts[2].length === 4) {
                year = parseInt(parts[2]);
            }
            if (year) {
                companyAge = new Date().getFullYear() - year;
            }
        } catch (e) {
            console.log(`[Age] Failed to parse date: ${dateOfIncorporation}`);
        }
    }
    
    // Prepare company data for scoring
    const companyData = {
        revenue_millions: revenue,
        status: companyStatus,
        cin: cin,
        directors_count: companyDirectors.length,
        age_years: companyAge,
        authorized_capital: authorizedCapital,
        paid_up_capital: paidUpCapital
    };
    
    // Score with context awareness (now includes company data)
    const dimensions = scoreDimensions(data, tier, industry, businessModel, companyData);
    const score = calculateOverallScore(dimensions, tier);
    
    return {
        name: entityName,
        tier: tier,
        industry: industry,
        business_model: businessModel,
        cin: cin,
        status: companyStatus,
        address: companyAddress,
        email: companyEmail,
        phone: companyPhone,
        pan: companyPAN,
        directors: companyDirectors,
        authorized_capital: authorizedCapital,
        paid_up_capital: paidUpCapital,
        date_of_incorporation: dateOfIncorporation,
        company_age: companyAge,
        roc: companyROC,
        company_class: companyClass,
        financial_year: financialYear,
        revenue_millions: revenue,
        revenue_inr_millions: revenueINR,
        revenue_display: revenueDisplay,
        revenue_source: revenueSource,
        score: score,
        scoring_points: dimensions,
        raw_data: data
    };
}

// Main assessment function
async function runAssessment(jobId, subject) {
    try {
        jobs[jobId].status = 'processing';
        jobs[jobId].progress = { phase: 'discovery', completed: 0, total: 11 };
        
        // Phase 1: Discover competitors
        const competitors = await discoverCompetitorsWrapper(subject, jobId);
        jobs[jobId].progress = { 
            phase: 'analysis', 
            completed: 0, 
            total: 11,
            message: `Found ${competitors.length} competitors` 
        };
        
        // Phase 2: Analyze subject first and make it available immediately
        const subjectResult = await analyzeEntity(subject, jobId);
        jobs[jobId].progress.completed = 1;
        jobs[jobId].progress.message = `Analyzed ${subject}`;
        
        // Make subject result available immediately for progressive rendering
        jobs[jobId].partial_result = {
            subject: subjectResult,
            competitors: []
        };
        
        // Phase 3: Analyze competitors in parallel (batches of 3)
        const competitorResults = [];
        for (let i = 0; i < competitors.length; i += 3) {
            const batch = competitors.slice(i, i + 3);
            const batchResults = await Promise.all(
                batch.map(comp => analyzeEntity(comp, jobId))
            );
            competitorResults.push(...batchResults);
            
            jobs[jobId].progress.completed = 1 + competitorResults.length;
            jobs[jobId].progress.message = `Analyzed ${competitorResults.length}/${competitors.length} competitors`;
            
            // Update partial results as each batch completes
            jobs[jobId].partial_result = {
                subject: subjectResult,
                competitors: competitorResults
            };
        }
        
        // Complete
        jobs[jobId].status = 'complete';
        jobs[jobId].result = {
            subject: subjectResult,
            competitors: competitorResults
        };
        jobs[jobId].progress = { phase: 'complete', completed: 11, total: 11 };
        
        // Clean up after 1 hour
        setTimeout(() => {
            delete jobs[jobId];
        }, 3600000);
        
    } catch (error) {
        console.error('Assessment failed:', error);
        jobs[jobId].status = 'failed';
        jobs[jobId].error = error.message;
    }
}

function updateJobProgress(jobId, message) {
    if (jobs[jobId] && jobs[jobId].progress) {
        jobs[jobId].progress.message = message;
    }
}

// API Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        active_jobs: Object.keys(jobs).length,
        timestamp: new Date().toISOString()
    });
});

// 2FA: Request OTP (mock implementation)
app.post('/api/request-otp', async (req, res) => {
    const { phone, email } = req.body;
    
    if (!phone && !email) {
        return res.status(400).json({ error: 'Phone or email is required' });
    }
    
    try {
        console.log(`[2FA] OTP requested for: ${phone || email}`);
        
        // Mock OTP generation - always 123456 for now
        const otp = '123456';
        const otpId = uuidv4();
        
        // In production: Send SMS via Twilio/MSG91 or email via SendGrid
        // For now: Just return success
        
        res.json({
            success: true,
            otp_id: otpId,
            message: `OTP sent to ${phone ? 'phone' : 'email'}`,
            // TEMP: Show OTP in response for testing
            debug_otp: otp
        });
    } catch (error) {
        console.error('[2FA] OTP request failed:', error);
        res.status(500).json({ error: 'Failed to send OTP', message: error.message });
    }
});

// 2FA: Verify OTP (mock implementation)
app.post('/api/verify-otp', async (req, res) => {
    const { otp_id, otp, phone, email } = req.body;
    
    if (!otp) {
        return res.status(400).json({ error: 'OTP is required' });
    }
    
    try {
        console.log(`[2FA] Verifying OTP: ${otp} for ${phone || email}`);
        
        // Mock verification - always accept 123456
        if (otp === '123456') {
            res.json({
                success: true,
                verified: true,
                message: 'OTP verified successfully'
            });
        } else {
            res.status(400).json({
                success: false,
                verified: false,
                message: 'Invalid OTP'
            });
        }
    } catch (error) {
        console.error('[2FA] OTP verification failed:', error);
        res.status(500).json({ error: 'Failed to verify OTP', message: error.message });
    }
});

// Search for company matches (disambiguation) - ENHANCED WITH GROQ
app.post('/api/search', async (req, res) => {
    const { query, useGroq } = req.body; // Added useGroq flag
    
    if (!query) {
        return res.status(400).json({ error: 'Query is required' });
    }
    
    try {
        console.log(`[API] Searching for: ${query}${useGroq ? ' (with Groq enhancement)' : ''}`);
        
        // Try Indian company search first (CIN-based)
        let indianResults = [];
        try {
            indianResults = await searchIndianCompany(query);
            console.log(`[API] Found ${indianResults.length} Indian companies with CIN`);
        } catch (error) {
            console.error('[API] Indian company search failed:', error.message);
        }
        
        // NEW: If no Indian results and Groq is available, try Groq extraction
        let groqEnhancedData = null;
        if (indianResults.length === 0 && useGroq !== false && process.env.GROQ_API_KEY) {
            try {
                console.log(`[API] No CIN results found, trying Groq AI extraction...`);
                const extractor = new GroqCompanyExtractor();
                const groqResult = await extractor.extractCompanyData(query);
                
                if (groqResult.success && groqResult.data) {
                    groqEnhancedData = groqResult.data;
                    console.log(`[API] ✅ Groq found data: CIN=${groqEnhancedData.cin}, Revenue=${groqEnhancedData.latest_revenue}`);
                    
                    // Add Groq result as a high-confidence match
                    indianResults.push({
                        name: groqEnhancedData.company_name || query,
                        cin: groqEnhancedData.cin,
                        status: groqEnhancedData.status,
                        revenue_display: groqEnhancedData.latest_revenue,
                        date_of_incorporation: groqEnhancedData.registration_date,
                        activity: groqEnhancedData.company_class,
                        source: 'Groq AI (Web Search)',
                        url: groqEnhancedData.cin ? `https://www.zaubacorp.com/company/${groqEnhancedData.cin}/` : null,
                        groq_enhanced: true,
                        full_data: groqEnhancedData // Include all extracted data
                    });
                }
            } catch (groqError) {
                console.error('[API] Groq enhancement failed:', groqError.message);
                // Continue without Groq data
            }
        }
        
        // Also search global companies
        const globalResults = await searchCompanyMatches(query);
        console.log(`[API] Found ${globalResults.length} global companies`);
        
        // Combine results: Indian companies first (they have CIN = verified)
        const allResults = [
            ...indianResults.map(r => ({
                name: r.name,
                url: r.url || (r.cin ? `https://www.zaubacorp.com/company/${r.cin}/` : null),
                domain: r.cin ? `CIN: ${r.cin}` : null,
                description: buildIndianCompanyDescription(r),
                source: r.source,
                confidence: r.groq_enhanced ? 'high' : 'high',
                verified: true,
                cin: r.cin,
                revenue_inr_millions: r.revenue_inr_millions,
                revenue_usd_millions: r.revenue_usd_millions,
                status: r.status,
                groq_enhanced: r.groq_enhanced || false,
                full_data: r.full_data || null // Include Groq full data if available
            })),
            ...globalResults.map(r => ({
                ...r,
                verified: false,
                groq_enhanced: false
            }))
        ];
        
        // Limit to top 10 total results
        const matches = allResults.slice(0, 10);
        
        res.json({
            query: query,
            matches: matches,
            count: matches.length,
            groq_used: !!groqEnhancedData,
            groq_available: !!process.env.GROQ_API_KEY
        });
    } catch (error) {
        console.error('Search error:', error);
        res.status(500).json({ error: 'Search failed', message: error.message });
    }
});

function buildIndianCompanyDescription(company) {
    const parts = [];
    
    if (company.status) {
        parts.push(`Status: ${company.status}`);
    }
    
    if (company.revenue_display) {
        parts.push(`Revenue: ${company.revenue_display}`);
    }
    
    if (company.date_of_incorporation) {
        parts.push(`Incorporated: ${company.date_of_incorporation}`);
    }
    
    if (company.activity) {
        parts.push(company.activity);
    }
    
    return parts.length > 0 ? parts.join(' | ') : 'Indian registered company with verified CIN';
}

app.post('/api/assess', async (req, res) => {
    const { subject } = req.body;
    
    if (!subject) {
        return res.status(400).json({ error: 'Subject is required' });
    }
    
    const jobId = uuidv4();
    jobs[jobId] = {
        status: 'processing',
        progress: { phase: 'starting', completed: 0, total: 11 },
        result: null,
        created_at: new Date()
    };
    
    // Start assessment in background
    runAssessment(jobId, subject);
    
    res.status(202).json({
        job_id: jobId,
        status: 'processing',
        estimated_duration: 120
    });
});

app.get('/api/assess/:jobId', (req, res) => {
    const { jobId } = req.params;
    
    if (!jobs[jobId]) {
        return res.status(404).json({ error: 'Job not found or expired' });
    }
    
    res.json(jobs[jobId]);
});

// NEW: Groq-powered company data extraction endpoint
app.post('/api/company-data/groq', async (req, res) => {
    const { companyName } = req.body;
    
    if (!companyName) {
        return res.status(400).json({ error: 'companyName is required' });
    }
    
    try {
        console.log(`[GROQ API] Extracting data for: ${companyName}`);
        
        const extractor = new GroqCompanyExtractor();
        const result = await extractor.extractCompanyData(companyName);
        
        res.json(result);
        
    } catch (error) {
        console.error('[GROQ API] Extraction failed:', error);
        res.status(500).json({ 
            success: false,
            error: 'Data extraction failed', 
            message: error.message 
        });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        active_jobs: Object.keys(jobs).length,
        groq_api_configured: !!process.env.GROQ_API_KEY,
        timestamp: new Date()
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Assessment API running on port ${PORT}`);
    console.log(`Open http://localhost:${PORT} to test`);
    console.log(`\nNew Groq endpoint: POST /api/company-data/groq`);
    console.log(`Test with: curl -X POST http://localhost:${PORT}/api/company-data/groq -H "Content-Type: application/json" -d '{"companyName":"Yashus Digital Marketing"}'`);
});
