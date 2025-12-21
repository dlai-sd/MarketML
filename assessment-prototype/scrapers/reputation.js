const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Brand reputation and authority analyzer
 */

async function analyzeReputation(companyName) {
    try {
        const results = await Promise.allSettled([
            searchNewsMedia(companyName),
            checkReviewSites(companyName),
            estimateBrandAuthority(companyName)
        ]);
        
        const news = results[0].status === 'fulfilled' ? results[0].value : {};
        const reviews = results[1].status === 'fulfilled' ? results[1].value : {};
        const authority = results[2].status === 'fulfilled' ? results[2].value : {};
        
        return {
            news_mentions: news.count || 0,
            recent_news: news.recent || false,
            review_count: reviews.total || 0,
            average_rating: reviews.avg_rating || 0,
            domain_authority: authority.score || 0,
            backlinks_estimate: authority.backlinks || 0,
            thought_leadership: authority.thought_leader || false
        };
        
    } catch (error) {
        console.error(`Reputation analysis failed for ${companyName}:`, error.message);
        return getDefaultReputationMetrics();
    }
}

async function searchNewsMedia(companyName) {
    try {
        // Search Google News
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(companyName)}&tbm=nws`;
        
        const response = await axios.get(searchUrl, {
            timeout: 5000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        
        // Count news results
        const newsItems = $('.SoaBEf').length || $('.xuvV6b').length;
        
        // Check for recent mentions (look for time indicators)
        const recentIndicators = ['hour ago', 'hours ago', 'day ago', 'days ago', 'yesterday'];
        const pageText = $('body').text().toLowerCase();
        const hasRecent = recentIndicators.some(indicator => pageText.includes(indicator));
        
        return {
            count: newsItems,
            recent: hasRecent
        };
        
    } catch (error) {
        console.error('News search failed:', error.message);
        return { count: 0, recent: false };
    }
}

async function checkReviewSites(companyName) {
    try {
        // Search for reviews on major platforms
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(companyName + ' reviews')}`;
        
        const response = await axios.get(searchUrl, {
            timeout: 5000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        const pageText = $('body').text();
        
        // Look for rating indicators
        const ratingMatch = pageText.match(/(\d+\.?\d*)\s*(?:stars?|\/5|out of 5)/i);
        const reviewCountMatch = pageText.match(/(\d+[\d,]*)\s*reviews?/i);
        
        // Check for review platforms
        const reviewPlatforms = ['g2.com', 'capterra', 'trustpilot', 'yelp', 'glassdoor', 'google reviews'];
        const platformMentions = reviewPlatforms.filter(platform => 
            pageText.toLowerCase().includes(platform)
        ).length;
        
        return {
            total: reviewCountMatch ? parseInt(reviewCountMatch[1].replace(/,/g, '')) : platformMentions * 10,
            avg_rating: ratingMatch ? parseFloat(ratingMatch[1]) : (platformMentions > 0 ? 4.0 : 0),
            platforms: platformMentions
        };
        
    } catch (error) {
        console.error('Review check failed:', error.message);
        return { total: 0, avg_rating: 0, platforms: 0 };
    }
}

async function estimateBrandAuthority(companyName) {
    try {
        // General web search to estimate authority
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(companyName)}`;
        
        const response = await axios.get(searchUrl, {
            timeout: 5000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        
        // Count result indicators
        const resultCount = $('.g').length;
        const hasKnowledgePanel = $('.kp-wholepage').length > 0 || $('.knowledge-panel').length > 0;
        
        // Look for thought leadership indicators
        const thoughtLeaderKeywords = ['founder', 'ceo', 'speaker', 'author', 'conference', 'expert', 'keynote'];
        const pageText = $('body').text().toLowerCase();
        const thoughtLeaderScore = thoughtLeaderKeywords.filter(keyword => pageText.includes(keyword)).length;
        
        // Estimate domain authority (0-100)
        let authorityScore = 10; // Base score
        if (hasKnowledgePanel) authorityScore += 30;
        if (resultCount > 8) authorityScore += 20;
        if (thoughtLeaderScore > 0) authorityScore += thoughtLeaderScore * 5;
        
        authorityScore = Math.min(authorityScore, 100);
        
        // Estimate backlinks based on result prominence
        const backlinksEstimate = resultCount * 1000 + (hasKnowledgePanel ? 50000 : 0);
        
        return {
            score: authorityScore,
            backlinks: backlinksEstimate,
            thought_leader: thoughtLeaderScore >= 3
        };
        
    } catch (error) {
        console.error('Brand authority estimation failed:', error.message);
        return { score: 0, backlinks: 0, thought_leader: false };
    }
}

function getDefaultReputationMetrics() {
    return {
        news_mentions: 0,
        recent_news: false,
        review_count: 0,
        average_rating: 0,
        domain_authority: 0,
        backlinks_estimate: 0,
        thought_leadership: false
    };
}

module.exports = {
    analyzeReputation
};
