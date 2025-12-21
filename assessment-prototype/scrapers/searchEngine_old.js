const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Search engines scraper for competitor discovery
 */

// Known competitors database for major companies
const KNOWN_COMPETITORS = {
    'hubspot': ['Salesforce', 'Marketo', 'Pardot', 'ActiveCampaign', 'Mailchimp', 'Constant Contact', 'GetResponse', 'ConvertKit', 'Drip', 'Klaviyo'],
    'salesforce': ['Microsoft Dynamics', 'Oracle', 'SAP', 'HubSpot', 'Zoho CRM', 'Pipedrive', 'SugarCRM', 'Freshsales', 'Insightly', 'Monday.com'],
    'microsoft': ['Google', 'Apple', 'Amazon', 'IBM', 'Oracle', 'SAP', 'Salesforce', 'Adobe', 'ServiceNow', 'Workday'],
    'google': ['Microsoft', 'Amazon', 'Apple', 'Meta', 'Salesforce', 'Oracle', 'IBM', 'Adobe', 'Zoom', 'Slack'],
    'mailchimp': ['Constant Contact', 'SendGrid', 'Campaign Monitor', 'AWeber', 'GetResponse', 'ActiveCampaign', 'ConvertKit', 'MailerLite', 'SendinBlue', 'Klaviyo'],
    'shopify': ['WooCommerce', 'BigCommerce', 'Magento', 'Wix', 'Squarespace', 'Volusion', 'PrestaShop', '3dcart', 'OpenCart', 'Ecwid'],
    'amazon': ['Walmart', 'Target', 'Alibaba', 'eBay', 'Costco', 'Best Buy', 'Home Depot', 'Wayfair', 'Etsy', 'Rakuten'],
    'meta': ['Google', 'Twitter', 'TikTok', 'Snapchat', 'LinkedIn', 'Pinterest', 'Reddit', 'Discord', 'Telegram', 'WeChat'],
    'zoom': ['Microsoft Teams', 'Google Meet', 'Cisco Webex', 'GoToMeeting', 'Skype', 'BlueJeans', 'Slack', 'Discord', 'RingCentral', '8x8'],
    'slack': ['Microsoft Teams', 'Discord', 'Zoom', 'Google Chat', 'Mattermost', 'Rocket.Chat', 'Twist', 'Chanty', 'Flock', 'Workplace'],
    'adobe': ['Canva', 'Figma', 'Sketch', 'Affinity', 'CorelDRAW', 'GIMP', 'Procreate', 'Pixlr', 'PaintShop Pro', 'Photopea'],
    'semrush': ['Ahrefs', 'Moz', 'SpyFu', 'Serpstat', 'Ubersuggest', 'Majestic', 'SE Ranking', 'Mangools', 'BrightEdge', 'Searchmetrics'],
    'asana': ['Monday.com', 'Trello', 'Jira', 'ClickUp', 'Wrike', 'Basecamp', 'Notion', 'Smartsheet', 'Teamwork', 'Airtable']
};

// User agents to rotate
const USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
];

function getRandomUserAgent() {
    return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Search Google for competitors
 */
async function searchGoogle(subject) {
    try {
        const queries = [
            `${subject} competitors`,
            `${subject} alternatives`,
            `companies like ${subject}`
        ];
        
        const allCompetitors = new Set();
        
        for (const query of queries) {
            await delay(1000 + Math.random() * 2000); // Random delay to avoid blocking
            
            const url = `https://www.google.com/search?q=${encodeURIComponent(query)}&num=20`;
            
            const response = await axios.get(url, {
                headers: {
                    'User-Agent': getRandomUserAgent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                },
                timeout: 10000
            });
            
            const $ = cheerio.load(response.data);
            
            // Extract company names from search results
            $('h3').each((i, elem) => {
                const text = $(elem).text();
                // Simple extraction - look for capitalized words
                const matches = text.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*/g);
                if (matches) {
                    matches.forEach(match => {
                        if (match.length > 2 && match !== subject) {
                            allCompetitors.add(match.trim());
                        }
                    });
                }
            });
            
            // Also extract from snippets
            $('.VwiC3b').each((i, elem) => {
                const text = $(elem).text();
                const matches = text.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}/g);
                if (matches) {
                    matches.forEach(match => {
                        if (match.length > 2 && match !== subject) {
                            allCompetitors.add(match.trim());
                        }
                    });
                }
            });
        }
        
        return Array.from(allCompetitors);
        
    } catch (error) {
        console.error('Google search failed:', error.message);
        return [];
    }
}

/**
 * Search Bing for competitors
 */
async function searchBing(subject) {
    try {
        const queries = [
            `${subject} competitors`,
            `${subject} vs`,
            `alternative to ${subject}`
        ];
        
        const allCompetitors = new Set();
        
        for (const query of queries) {
            await delay(1000 + Math.random() * 2000);
            
            const url = `https://www.bing.com/search?q=${encodeURIComponent(query)}&count=20`;
            
            const response = await axios.get(url, {
                headers: {
                    'User-Agent': getRandomUserAgent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                timeout: 10000
            });
            
            const $ = cheerio.load(response.data);
            
            // Extract from Bing results
            $('h2 a').each((i, elem) => {
                const text = $(elem).text();
                const matches = text.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*/g);
                if (matches) {
                    matches.forEach(match => {
                        if (match.length > 2 && match !== subject) {
                            allCompetitors.add(match.trim());
                        }
                    });
                }
            });
            
            // Extract from descriptions
            $('.b_caption p').each((i, elem) => {
                const text = $(elem).text();
                const matches = text.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}/g);
                if (matches) {
                    matches.forEach(match => {
                        if (match.length > 2 && match !== subject) {
                            allCompetitors.add(match.trim());
                        }
                    });
                }
            });
        }
        
        return Array.from(allCompetitors);
        
    } catch (error) {
        console.error('Bing search failed:', error.message);
        return [];
    }
}

/**
 * Discover competitors using both Google and Bing
 */
async function discoverCompetitors(subject) {
    console.log(`Discovering competitors for: ${subject}`);
    
    try {
        // First check if we have known competitors for this company
        const subjectLower = subject.toLowerCase().replace(/\s+/g, '');
        for (const [company, competitors] of Object.entries(KNOWN_COMPETITORS)) {
            if (subjectLower.includes(company) || company.includes(subjectLower)) {
                console.log(`Found known competitors for ${subject}: ${competitors.length} competitors`);
                return competitors;
            }
        }
        
        // Run searches in parallel
        const [googleResults, bingResults] = await Promise.all([
            searchGoogle(subject),
            searchBing(subject)
        ]);
        
        console.log(`Google found: ${googleResults.length} potential competitors`);
        console.log(`Bing found: ${bingResults.length} potential competitors`);
        
        // Combine and rank by frequency
        const competitorCounts = {};
        
        [...googleResults, ...bingResults].forEach(competitor => {
            const normalized = competitor.toLowerCase().trim();
            // Filter out common words and the subject itself
            if (normalized.length > 2 && 
                !normalized.includes(subject.toLowerCase()) &&
                !['company', 'business', 'service', 'agency'].includes(normalized)) {
                competitorCounts[normalized] = (competitorCounts[normalized] || 0) + 1;
            }
        });
        
        // Sort by frequency
        const rankedCompetitors = Object.entries(competitorCounts)
            .sort((a, b) => b[1] - a[1])
            .map(([name, count]) => ({
                name: name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
                mentions: count
            }));
        
        console.log(`Total unique competitors found: ${rankedCompetitors.length}`);
        
        // If we found competitors, return top 10 with at least 1 mention (relaxed from 2)
        if (rankedCompetitors.length > 0) {
            const filtered = rankedCompetitors.filter(c => c.mentions >= 1);
            console.log(`After filtering: ${filtered.length} competitors`);
            return filtered.slice(0, 10).map(c => c.name);
        }
        
        // If still nothing, try industry-based search
        console.log('No competitors found, trying industry-based search...');
        const industryResults = await searchByIndustry(subject);
        if (industryResults.length > 0) {
            return industryResults.slice(0, 10);
        }
        
        return [];
        
    } catch (error) {
        console.error('Competitor discovery failed:', error);
        return [];
    }
}

/**
 * Try to find competitors by industry/category
 */
async function searchByIndustry(subject) {
    try {
        // Extract potential industry keywords
        const industryKeywords = ['digital marketing', 'marketing agency', 'seo', 'social media', 
                                  'advertising', 'consulting', 'software', 'saas', 'technology'];
        
        let industry = null;
        for (const keyword of industryKeywords) {
            if (subject.toLowerCase().includes(keyword)) {
                industry = keyword;
                break;
            }
        }
        
        if (!industry) {
            // Default to generic search
            industry = 'companies';
        }
        
        console.log(`Searching for top ${industry} companies...`);
        
        const query = `top ${industry} companies`;
        const url = `https://www.google.com/search?q=${encodeURIComponent(query)}&num=20`;
        
        await delay(1000);
        
        const response = await axios.get(url, {
            headers: {
                'User-Agent': getRandomUserAgent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        const companies = new Set();
        
        // Extract company names
        $('h3, .LC20lb').each((i, elem) => {
            const text = $(elem).text();
            const matches = text.match(/[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}/g);
            if (matches) {
                matches.forEach(match => {
                    if (match.length > 2 && match !== subject) {
                        companies.add(match.trim());
                    }
                });
            }
        });
        
        const result = Array.from(companies);
        console.log(`Industry search found: ${result.length} companies`);
        return result;
        
    } catch (error) {
        console.error('Industry search failed:', error);
        return [];
    }
}

module.exports = {
    discoverCompetitors,
    searchGoogle,
    searchBing
};
