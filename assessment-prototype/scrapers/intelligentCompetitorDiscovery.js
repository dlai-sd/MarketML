const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Intelligent Competitor Discovery Service
 * Modular component for multi-dimensional competitor analysis
 * Can be deployed as standalone microservice
 */

// Configuration
const CONFIG = {
    MAX_COMPETITORS: 15,
    SEARCH_TIMEOUT: 10000,
    MIN_CONFIDENCE_SCORE: 0.3,
    DELAY_BETWEEN_REQUESTS: 500
};

/**
 * Main entry point - discover competitors intelligently
 * @param {string} companyName - Company name to analyze
 * @param {string} companyUrl - Company website URL (optional)
 * @returns {Promise<Array>} - Array of competitor objects with scores
 */
async function discoverCompetitorsIntelligently(companyName, companyUrl = null) {
    console.log(`[IntelligentDiscovery] Starting analysis for: ${companyName}`);
    
    try {
        // Phase 1: Extract Business Intelligence
        const businessIntel = await extractBusinessIntelligence(companyName, companyUrl);
        console.log(`[IntelligentDiscovery] Business Intel:`, businessIntel);
        
        // Phase 2: Generate Multi-Dimensional Search Queries
        const searchQueries = generateSearchQueries(companyName, businessIntel);
        console.log(`[IntelligentDiscovery] Generated ${searchQueries.length} search queries`);
        
        // Phase 3: Execute Searches Across Multiple Sources
        const rawResults = await executeMultiSourceSearch(searchQueries);
        console.log(`[IntelligentDiscovery] Found ${rawResults.length} raw results`);
        
        // Phase 4: Aggregate and Score Results
        const scoredCompetitors = aggregateAndScore(rawResults, companyName, businessIntel);
        console.log(`[IntelligentDiscovery] Scored ${scoredCompetitors.length} potential competitors`);
        
        // Phase 5: Validate and Filter
        const validatedCompetitors = filterAndValidate(scoredCompetitors);
        
        // Phase 6: Enrich with Context
        const enrichedCompetitors = enrichWithContext(validatedCompetitors, businessIntel);
        
        console.log(`[IntelligentDiscovery] Final result: ${enrichedCompetitors.length} competitors`);
        return enrichedCompetitors.slice(0, CONFIG.MAX_COMPETITORS);
        
    } catch (error) {
        console.error('[IntelligentDiscovery] Error:', error.message);
        return [];
    }
}

/**
 * Phase 1: Extract business intelligence from company
 */
async function extractBusinessIntelligence(companyName, companyUrl) {
    const intel = {
        industry: [],
        offerings: [],
        customers: [],
        keywords: [],
        technology: [],
        geography: []
    };
    
    // Try to find company URL if not provided
    if (!companyUrl) {
        companyUrl = await findCompanyWebsite(companyName);
    }
    
    if (!companyUrl) {
        console.log('[IntelligentDiscovery] No website found, using name-based analysis');
        // Extract intelligence from company name
        intel.keywords = extractKeywordsFromName(companyName);
        return intel;
    }
    
    try {
        // Scrape company website
        const response = await axios.get(companyUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        
        // Extract meta description
        const description = $('meta[name="description"]').attr('content') || 
                          $('meta[property="og:description"]').attr('content') || '';
        
        // Extract title
        const title = $('title').text() || '';
        
        // Extract main content
        const mainContent = $('main, article, .content, #content').text() || $('body').text();
        const combinedText = (title + ' ' + description + ' ' + mainContent.substring(0, 2000)).toLowerCase();
        
        // Industry detection
        const industryPatterns = {
            'agriculture|farming|crop|agri-tech|precision agriculture': 'Agriculture Technology',
            'satellite|remote sensing|geospatial|earth observation': 'Satellite Data & Remote Sensing',
            'software|saas|platform|cloud': 'Software/SaaS',
            'marketing|digital marketing|seo|social media': 'Digital Marketing',
            'ecommerce|e-commerce|online shop|retail': 'E-commerce',
            'finance|fintech|banking|payment': 'Financial Technology',
            'health|healthcare|medical|telemedicine': 'Healthcare',
            'education|edtech|learning|training': 'Education Technology'
        };
        
        for (const [pattern, industry] of Object.entries(industryPatterns)) {
            if (new RegExp(pattern, 'i').test(combinedText)) {
                intel.industry.push(industry);
            }
        }
        
        // Offerings detection
        const offeringPatterns = [
            'crop monitoring', 'yield prediction', 'satellite imagery', 'farm management',
            'analytics platform', 'data visualization', 'api service', 'mobile app',
            'consulting services', 'advisory', 'insights', 'intelligence',
            'automation', 'monitoring', 'tracking', 'reporting'
        ];
        
        offeringPatterns.forEach(offering => {
            if (combinedText.includes(offering)) {
                intel.offerings.push(offering);
            }
        });
        
        // Customer segments
        const customerPatterns = [
            'farmers', 'enterprises', 'small business', 'startups', 'government',
            'agriculture companies', 'cooperatives', 'growers', 'landowners'
        ];
        
        customerPatterns.forEach(customer => {
            if (combinedText.includes(customer)) {
                intel.customers.push(customer);
            }
        });
        
        // Technology stack
        const techPatterns = [
            'machine learning', 'ai', 'artificial intelligence', 'deep learning',
            'computer vision', 'satellite data', 'apis', 'cloud computing',
            'iot', 'sensors', 'ndvi', 'sentinel', 'landsat'
        ];
        
        techPatterns.forEach(tech => {
            if (combinedText.includes(tech)) {
                intel.technology.push(tech);
            }
        });
        
        // Geography
        const geoPatterns = [
            'india', 'pune', 'asia', 'global', 'worldwide', 'international',
            'united states', 'europe', 'africa', 'latin america'
        ];
        
        geoPatterns.forEach(geo => {
            if (combinedText.includes(geo)) {
                intel.geography.push(geo);
            }
        });
        
        // Extract important keywords
        intel.keywords = extractImportantKeywords(combinedText);
        
    } catch (error) {
        console.error('[IntelligentDiscovery] Website extraction failed:', error.message);
        intel.keywords = extractKeywordsFromName(companyName);
    }
    
    return intel;
}

/**
 * Find company website from name
 */
async function findCompanyWebsite(companyName) {
    try {
        const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(companyName + ' official website')}`;
        const response = await axios.get(searchUrl, {
            headers: { 'User-Agent': 'Mozilla/5.0' },
            timeout: 8000
        });
        
        const $ = cheerio.load(response.data);
        const firstResult = $('.result__url, .result__a').first().attr('href');
        
        if (firstResult && firstResult.startsWith('http')) {
            return firstResult;
        }
    } catch (error) {
        console.error('[IntelligentDiscovery] Website search failed:', error.message);
    }
    
    return null;
}

/**
 * Extract keywords from company name
 */
function extractKeywordsFromName(companyName) {
    const keywords = [];
    const name = companyName.toLowerCase();
    
    // Common technology/industry keywords
    const techKeywords = ['satellite', 'data', 'tech', 'software', 'solutions', 'systems', 
                         'services', 'platform', 'digital', 'smart', 'ai', 'ml'];
    
    techKeywords.forEach(keyword => {
        if (name.includes(keyword)) {
            keywords.push(keyword);
        }
    });
    
    return keywords.length > 0 ? keywords : [companyName.split(' ')[0]];
}

/**
 * Extract important keywords from text
 */
function extractImportantKeywords(text) {
    const words = text.match(/\b[a-z]{4,}\b/g) || [];
    const frequency = {};
    
    // Stop words to exclude
    const stopWords = ['this', 'that', 'with', 'from', 'have', 'more', 'will', 'about', 
                       'their', 'there', 'which', 'when', 'what', 'some', 'other'];
    
    words.forEach(word => {
        if (!stopWords.includes(word)) {
            frequency[word] = (frequency[word] || 0) + 1;
        }
    });
    
    // Get top keywords
    return Object.entries(frequency)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([word]) => word);
}

/**
 * Phase 2: Generate multi-dimensional search queries
 */
function generateSearchQueries(companyName, businessIntel) {
    const queries = [];
    
    // 1. Direct competitor search
    queries.push(`${companyName} competitors`);
    queries.push(`companies like ${companyName}`);
    queries.push(`alternatives to ${companyName}`);
    
    // 2. Industry-based queries
    if (businessIntel.industry.length > 0) {
        businessIntel.industry.forEach(industry => {
            queries.push(`${industry} companies`);
            queries.push(`top ${industry} platforms`);
        });
    }
    
    // 3. Offering-based queries
    if (businessIntel.offerings.length > 0) {
        const topOfferings = businessIntel.offerings.slice(0, 3);
        topOfferings.forEach(offering => {
            queries.push(`${offering} companies`);
            queries.push(`${offering} providers`);
        });
    }
    
    // 4. Customer-based queries
    if (businessIntel.customers.length > 0) {
        const topCustomers = businessIntel.customers.slice(0, 2);
        topCustomers.forEach(customer => {
            queries.push(`platforms for ${customer}`);
            queries.push(`solutions for ${customer}`);
        });
    }
    
    // 5. Technology-based queries
    if (businessIntel.technology.length > 0) {
        const topTech = businessIntel.technology.slice(0, 2);
        topTech.forEach(tech => {
            queries.push(`${tech} companies`);
        });
    }
    
    // 6. Geography + Industry
    if (businessIntel.geography.length > 0 && businessIntel.industry.length > 0) {
        const geo = businessIntel.geography[0];
        const industry = businessIntel.industry[0];
        queries.push(`${industry} companies in ${geo}`);
    }
    
    // 7. Keyword-based queries
    if (businessIntel.keywords.length > 0) {
        const topKeywords = businessIntel.keywords.slice(0, 2);
        topKeywords.forEach(keyword => {
            queries.push(`${keyword} companies`);
        });
    }
    
    // Deduplicate and limit
    return [...new Set(queries)].slice(0, 12);
}

/**
 * Phase 3: Execute searches across multiple sources
 */
async function executeMultiSourceSearch(queries) {
    const allResults = [];
    
    for (const query of queries) {
        console.log(`[IntelligentDiscovery] Searching: "${query}"`);
        
        // Search DuckDuckGo (most reliable, less rate limiting)
        const ddgResults = await searchDuckDuckGo(query);
        allResults.push(...ddgResults.map(r => ({ ...r, query, source: 'DuckDuckGo' })));
        
        // Small delay to avoid rate limiting
        await delay(CONFIG.DELAY_BETWEEN_REQUESTS);
    }
    
    return allResults;
}

/**
 * Search DuckDuckGo
 */
async function searchDuckDuckGo(query) {
    try {
        const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
        const response = await axios.get(searchUrl, {
            headers: { 'User-Agent': 'Mozilla/5.0' },
            timeout: CONFIG.SEARCH_TIMEOUT
        });
        
        const $ = cheerio.load(response.data);
        const results = [];
        
        $('.result, .results_links').each((i, elem) => {
            if (i >= 5) return false; // Limit to top 5 per query
            
            const $elem = $(elem);
            const title = $elem.find('.result__title, .result__a').text().trim();
            const snippet = $elem.find('.result__snippet').text().trim();
            let url = $elem.find('.result__url, .result__a').attr('href');
            
            // Clean up DuckDuckGo redirect
            if (url && url.includes('uddg=')) {
                const match = url.match(/uddg=([^&]+)/);
                if (match) url = decodeURIComponent(match[1]);
            }
            
            if (title && url && url.startsWith('http')) {
                try {
                    const domain = new URL(url).hostname.replace('www.', '');
                    results.push({ title, snippet, url, domain });
                } catch (e) {
                    // Skip invalid URLs
                }
            }
        });
        
        return results;
        
    } catch (error) {
        console.error(`[IntelligentDiscovery] DuckDuckGo search failed for "${query}":`, error.message);
        return [];
    }
}

/**
 * Phase 4: Aggregate and score results
 */
function aggregateAndScore(rawResults, companyName, businessIntel) {
    const competitorMap = new Map();
    const companyLower = companyName.toLowerCase();
    
    rawResults.forEach(result => {
        // Extract potential company name from title
        const potentialName = extractCompanyName(result.title);
        if (!potentialName) return;
        
        const nameLower = potentialName.toLowerCase();
        
        // Skip if it's the original company
        if (nameLower === companyLower || nameLower.includes(companyLower)) {
            return;
        }
        
        // Skip non-companies
        if (isNonCompany(potentialName, result.url)) {
            return;
        }
        
        // Aggregate by domain
        const key = result.domain || nameLower;
        
        if (!competitorMap.has(key)) {
            competitorMap.set(key, {
                name: potentialName,
                domain: result.domain,
                url: result.url,
                mentions: 0,
                relevanceScore: 0,
                contexts: [],
                sources: new Set()
            });
        }
        
        const competitor = competitorMap.get(key);
        competitor.mentions++;
        competitor.sources.add(result.source);
        
        // Calculate relevance score
        let score = 1; // Base score for appearing
        
        // Boost for multiple mentions
        score += Math.min(competitor.mentions * 0.3, 2);
        
        // Boost for industry keywords
        const combinedText = (result.title + ' ' + result.snippet).toLowerCase();
        businessIntel.industry.forEach(industry => {
            if (combinedText.includes(industry.toLowerCase())) score += 0.5;
        });
        
        // Boost for offering keywords
        businessIntel.offerings.forEach(offering => {
            if (combinedText.includes(offering)) score += 0.3;
        });
        
        // Boost for technology keywords
        businessIntel.technology.forEach(tech => {
            if (combinedText.includes(tech)) score += 0.2;
        });
        
        competitor.relevanceScore = Math.max(competitor.relevanceScore, score);
        competitor.contexts.push(result.snippet);
    });
    
    // Convert to array and sort by score
    return Array.from(competitorMap.values())
        .sort((a, b) => b.relevanceScore - a.relevanceScore);
}

/**
 * Extract company name from title
 */
function extractCompanyName(title) {
    // Remove common suffixes
    let name = title
        .replace(/\s*[-–|:]\s*.*/g, '') // Remove everything after dash, pipe, or colon
        .replace(/\s*(Inc\.|Ltd\.|LLC|Corp\.|Company|Corporation)\s*/gi, '')
        .trim();
    
    // Must be reasonable length
    if (name.length < 2 || name.length > 60) return null;
    
    return name;
}

/**
 * Check if result is non-company
 */
function isNonCompany(name, url) {
    const nameLower = name.toLowerCase();
    const urlLower = url.toLowerCase();
    
    // Exclude non-company sites
    const excludeDomains = ['wikipedia', 'youtube', 'facebook', 'twitter', 'linkedin', 
                           'instagram', 'reddit', 'quora', 'medium', 'forbes', 'techcrunch'];
    
    if (excludeDomains.some(domain => urlLower.includes(domain))) {
        return true;
    }
    
    // Exclude list/article titles
    const excludePatterns = ['top 10', 'best of', 'list of', 'guide to', 'how to', 
                            'what is', 'review of', 'comparison'];
    
    if (excludePatterns.some(pattern => nameLower.includes(pattern))) {
        return true;
    }
    
    return false;
}

/**
 * Phase 5: Filter and validate
 */
function filterAndValidate(competitors) {
    return competitors.filter(comp => {
        // Minimum confidence threshold
        if (comp.relevanceScore < CONFIG.MIN_CONFIDENCE_SCORE) return false;
        
        // Must have valid name and domain
        if (!comp.name || !comp.domain) return false;
        
        // Must have been mentioned at least once
        if (comp.mentions < 1) return false;
        
        return true;
    });
}

/**
 * Phase 6: Enrich with context
 */
function enrichWithContext(competitors, businessIntel) {
    return competitors.map(comp => {
        // Determine why they're a competitor
        const reasons = [];
        
        if (comp.mentions >= 3) {
            reasons.push('Frequently mentioned in searches');
        }
        
        const contextText = comp.contexts.join(' ').toLowerCase();
        
        businessIntel.industry.forEach(industry => {
            if (contextText.includes(industry.toLowerCase())) {
                reasons.push(`Same industry: ${industry}`);
            }
        });
        
        businessIntel.offerings.slice(0, 2).forEach(offering => {
            if (contextText.includes(offering)) {
                reasons.push(`Similar offering: ${offering}`);
            }
        });
        
        return {
            name: comp.name,
            domain: comp.domain,
            url: comp.url,
            confidence: mapScoreToConfidence(comp.relevanceScore),
            relevanceScore: Math.round(comp.relevanceScore * 10) / 10,
            mentions: comp.mentions,
            reason: reasons[0] || 'Industry competitor',
            sources: Array.from(comp.sources)
        };
    });
}

/**
 * Map numeric score to confidence level
 */
function mapScoreToConfidence(score) {
    if (score >= 2.5) return 'high';
    if (score >= 1.5) return 'medium';
    return 'low';
}

/**
 * Utility: Delay function
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Export main function
module.exports = {
    discoverCompetitorsIntelligently,
    CONFIG
};
