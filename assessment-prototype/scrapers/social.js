const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Social media presence analyzer
 */

async function analyzeSocialMedia(companyName) {
    try {
        const results = await Promise.allSettled([
            getLinkedInData(companyName),
            getTwitterData(companyName),
            estimateSocialPresence(companyName)
        ]);
        
        const linkedin = results[0].status === 'fulfilled' ? results[0].value : {};
        const twitter = results[1].status === 'fulfilled' ? results[1].value : {};
        const estimates = results[2].status === 'fulfilled' ? results[2].value : {};
        
        return {
            linkedin: linkedin,
            twitter: twitter,
            estimated_followers: estimates.total_followers || 0,
            estimated_engagement: estimates.engagement_rate || 0,
            active_platforms: estimates.platforms || 0
        };
        
    } catch (error) {
        console.error(`Social media analysis failed for ${companyName}:`, error.message);
        return getDefaultSocialMetrics();
    }
}

async function getLinkedInData(companyName) {
    try {
        // Search for LinkedIn company page
        const searchUrl = `https://www.google.com/search?q=site:linkedin.com/company ${encodeURIComponent(companyName)}`;
        
        const response = await axios.get(searchUrl, {
            timeout: 5000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        
        // Check if LinkedIn page exists
        const linkedinLink = $('a[href*="linkedin.com/company"]').first().attr('href');
        
        if (linkedinLink) {
            // Try to get follower count from search snippet
            const snippet = $('.VwiC3b').first().text();
            const followerMatch = snippet.match(/(\d+[\d,]*)\s*followers/i);
            
            return {
                has_page: true,
                url: linkedinLink,
                estimated_followers: followerMatch ? parseInt(followerMatch[1].replace(/,/g, '')) : 1000,
                verified: snippet.toLowerCase().includes('verified')
            };
        }
        
        return { has_page: false };
        
    } catch (error) {
        console.error('LinkedIn data fetch failed:', error.message);
        return { has_page: false };
    }
}

async function getTwitterData(companyName) {
    try {
        // Search for Twitter profile
        const searchUrl = `https://www.google.com/search?q=site:twitter.com ${encodeURIComponent(companyName)}`;
        
        const response = await axios.get(searchUrl, {
            timeout: 5000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        
        const twitterLink = $('a[href*="twitter.com"]').first().attr('href');
        
        if (twitterLink && !twitterLink.includes('/status/')) {
            return {
                has_account: true,
                url: twitterLink,
                estimated_followers: 500 // Base estimate
            };
        }
        
        return { has_account: false };
        
    } catch (error) {
        console.error('Twitter data fetch failed:', error.message);
        return { has_account: false };
    }
}

async function estimateSocialPresence(companyName) {
    try {
        // Search for social media presence
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(companyName + ' social media')}`;
        
        const response = await axios.get(searchUrl, {
            timeout: 5000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        const pageText = $('body').text();
        
        // Count platform mentions
        const platforms = {
            linkedin: pageText.includes('LinkedIn'),
            twitter: pageText.includes('Twitter') || pageText.includes('X.com'),
            facebook: pageText.includes('Facebook'),
            instagram: pageText.includes('Instagram'),
            youtube: pageText.includes('YouTube'),
            tiktok: pageText.includes('TikTok')
        };
        
        const platformCount = Object.values(platforms).filter(v => v).length;
        
        // Estimate based on search result count
        const resultCount = $('.g').length;
        const estimatedFollowers = resultCount * 500; // Rough estimate
        
        return {
            platforms: platformCount,
            total_followers: estimatedFollowers,
            engagement_rate: platformCount > 0 ? (platformCount * 0.5) : 0
        };
        
    } catch (error) {
        console.error('Social presence estimation failed:', error.message);
        return {
            platforms: 0,
            total_followers: 0,
            engagement_rate: 0
        };
    }
}

function getDefaultSocialMetrics() {
    return {
        linkedin: { has_page: false },
        twitter: { has_account: false },
        estimated_followers: 0,
        estimated_engagement: 0,
        active_platforms: 0
    };
}

module.exports = {
    analyzeSocialMedia
};
