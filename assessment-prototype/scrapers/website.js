const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Website content and technical analysis
 */

async function analyzeWebsite(companyName) {
    try {
        // Try to find website URL
        const websiteUrl = await findWebsiteUrl(companyName);
        
        if (!websiteUrl) {
            console.log(`No website found for ${companyName}`);
            return getDefaultWebsiteMetrics();
        }
        
        console.log(`Analyzing website: ${websiteUrl}`);
        
        // Fetch homepage
        const response = await axios.get(websiteUrl, {
            timeout: 10000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            maxRedirects: 5
        });
        
        const $ = cheerio.load(response.data);
        
        // Extract metrics
        const metrics = {
            has_blog: detectBlog($, websiteUrl),
            content_pages: estimateContentPages($),
            has_cta: detectCTA($),
            has_testimonials: detectTestimonials($),
            meta_description: $('meta[name="description"]').attr('content') || '',
            has_structured_data: $('script[type="application/ld+json"]').length > 0,
            mobile_optimized: $('meta[name="viewport"]').length > 0,
            page_size: response.data.length,
            has_analytics: detectAnalytics($),
            social_links: countSocialLinks($),
            revenue_mentioned: detectRevenueMention($),
            url: websiteUrl
        };
        
        return metrics;
        
    } catch (error) {
        console.error(`Website analysis failed for ${companyName}:`, error.message);
        return getDefaultWebsiteMetrics();
    }
}

async function findWebsiteUrl(companyName) {
    try {
        // Search for official website
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(companyName + ' official website')}`;
        
        const response = await axios.get(searchUrl, {
            timeout: 5000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        
        // Try to extract first result URL
        const firstLink = $('.yuRUbf a').first().attr('href');
        
        if (firstLink && (firstLink.startsWith('http://') || firstLink.startsWith('https://'))) {
            return firstLink;
        }
        
        // Fallback: construct common URL patterns
        const domain = companyName.toLowerCase().replace(/\s+/g, '');
        const possibleUrls = [
            `https://www.${domain}.com`,
            `https://${domain}.com`,
            `https://www.${domain}.io`,
            `https://${domain}.io`
        ];
        
        for (const url of possibleUrls) {
            try {
                await axios.head(url, { timeout: 3000 });
                return url;
            } catch (e) {
                // Try next URL
            }
        }
        
        return null;
        
    } catch (error) {
        return null;
    }
}

function detectBlog($, baseUrl) {
    const blogIndicators = ['/blog', '/news', '/articles', '/insights', '/resources'];
    let blogFound = false;
    
    $('a').each((i, elem) => {
        const href = $(elem).attr('href') || '';
        if (blogIndicators.some(indicator => href.includes(indicator))) {
            blogFound = true;
            return false;
        }
    });
    
    return blogFound;
}

function estimateContentPages($) {
    // Count internal links as proxy for content depth
    let internalLinks = 0;
    $('a').each((i, elem) => {
        const href = $(elem).attr('href') || '';
        if (href.startsWith('/') || (!href.startsWith('http') && href.length > 0)) {
            internalLinks++;
        }
    });
    return Math.min(internalLinks, 100); // Cap at 100
}

function detectCTA($) {
    const ctaKeywords = ['sign up', 'get started', 'free trial', 'contact us', 'demo', 'buy now', 'subscribe'];
    let ctaFound = false;
    
    $('button, a.btn, a.button, .cta').each((i, elem) => {
        const text = $(elem).text().toLowerCase();
        if (ctaKeywords.some(keyword => text.includes(keyword))) {
            ctaFound = true;
            return false;
        }
    });
    
    return ctaFound;
}

function detectTestimonials($) {
    const testimonialKeywords = ['testimonial', 'review', 'customer', 'client', 'what people say'];
    const text = $('body').text().toLowerCase();
    
    return testimonialKeywords.some(keyword => text.includes(keyword));
}

function detectAnalytics($) {
    const analyticsPatterns = [
        'google-analytics',
        'gtag',
        'ga(',
        'mixpanel',
        'segment',
        'amplitude'
    ];
    
    const scripts = $('script').map((i, elem) => $(elem).html()).get().join(' ');
    
    return analyticsPatterns.some(pattern => scripts.includes(pattern));
}

function countSocialLinks($) {
    const socialDomains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com', 'tiktok.com'];
    let socialCount = 0;
    
    $('a').each((i, elem) => {
        const href = $(elem).attr('href') || '';
        if (socialDomains.some(domain => href.includes(domain))) {
            socialCount++;
        }
    });
    
    return Math.min(socialCount, 6); // Max 6 platforms
}

function detectRevenueMention($) {
    const bodyText = $('body').text().toLowerCase();
    
    // Look for revenue patterns
    const revenuePatterns = [
        /revenue[:\s]+(?:us\$|usd|\$|€|£)?\s*[\d,.]+\s*(?:billion|million|trillion)/i,
        /\$[\d,.]+\s*(?:billion|million)\s+(?:in\s+)?revenue/i,
        /annual\s+revenue/i
    ];
    
    for (const pattern of revenuePatterns) {
        if (pattern.test(bodyText)) {
            return true;
        }
    }
    
    return false;
}

function getDefaultWebsiteMetrics() {
    return {
        has_blog: false,
        content_pages: 0,
        has_cta: false,
        has_testimonials: false,
        meta_description: '',
        has_structured_data: false,
        mobile_optimized: false,
        page_size: 0,
        has_analytics: false,
        social_links: 0,
        revenue_mentioned: false,
        url: null
    };
}

module.exports = {
    analyzeWebsite
};
