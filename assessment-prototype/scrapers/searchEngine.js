const axios = require('axios');
const cheerio = require('cheerio');
const puppeteer = require('puppeteer');

/**
 * Real-time competitor discovery using Puppeteer and Wikipedia
 */

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Helper function to determine if a link text is likely a company name
 */
function isLikelyCompany(text, href, subject) {
    if (!text || !href) return false;
    
    // Exclude obviously non-company items
    const excludePatterns = [
        /^(the|a|an|and|or|of|in|on|at|to|for|with|by)\s/i,
        /^(list of|category:|wikipedia:|help:|portal:|file:|image:)/i,
        /^(january|february|march|april|may|june|july|august|september|october|november|december)/i,
        /^\d{4}$/, // Just years
        /^(CEO|CTO|CFO|founder|president|chairman|board|headquarters|revenue|income)$/i,
        /^(public|private|traded|stock|NYSE|NASDAQ|S&P|Russell|Dow Jones)$/i,
        /^(US\$|€|£|\$|USD|EUR|GBP)/,
        /^(million|billion|trillion)$/i,
        /citation needed/i
    ];
    
    // Check if matches exclude patterns
    if (excludePatterns.some(pattern => pattern.test(text))) {
        return false;
    }
    
    // Must not be the subject itself
    if (text.toLowerCase() === subject.toLowerCase()) {
        return false;
    }
    
    // Wikipedia meta pages
    if (href.includes(':') || href.includes('#')) {
        return false;
    }
    
    // Good indicators of company names
    const goodIndicators = [
        /Inc\.|Ltd\.|LLC|Corporation|Corp\.|Company|Co\./,
        /^[A-Z][a-z]+([A-Z][a-z]+)+$/, // CamelCase like HubSpot, MailChimp
        /\b(Software|Technologies|Systems|Solutions|Services)\b/i
    ];
    
    // Length checks
    if (text.length < 2 || text.length > 50) return false;
    
    // Must have at least one capital letter (company names are proper nouns)
    if (!/[A-Z]/.test(text)) return false;
    
    // Not just numbers
    if (/^\d+$/.test(text)) return false;
    
    // Bonus: Has good company indicators
    if (goodIndicators.some(pattern => pattern.test(text))) {
        return true;
    }
    
    // Default: seems reasonable
    return text.trim().length >= 3;
}

/**
 * Search Wikipedia for company competitors and alternatives
 */
async function searchWikipedia(subject) {
    try {
        console.log(`Searching Wikipedia for ${subject}...`);
        
        // Try direct page access first
        const pageUrl = `https://en.wikipedia.org/wiki/${encodeURIComponent(subject.replace(/\s+/g, '_'))}`;
        
        const response = await axios.get(pageUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            timeout: 15000
        });
        
        const $ = cheerio.load(response.data);
        const competitors = new Set();
        
        // Strategy 1: Look for "Competitors" or "Competition" sections
        let foundInSection = false;
        $('h2, h3').each((i, heading) => {
            const headingText = $(heading).text().toLowerCase();
            if (headingText.includes('competitor') || headingText.includes('competition') || 
                headingText.includes('similar') || headingText.includes('alternative')) {
                
                // Get all links in the next paragraphs after this heading
                let current = $(heading).next();
                let iterations = 0;
                while (current.length && iterations < 5) {
                    current.find('a[href^="/wiki/"]').each((j, link) => {
                        const text = $(link).text();
                        const href = $(link).attr('href');
                        if (isLikelyCompany(text, href, subject)) {
                            competitors.add(text.trim());
                            foundInSection = true;
                        }
                    });
                    
                    if (current.is('h2, h3')) break; // Stop at next heading
                    current = current.next();
                    iterations++;
                }
            }
        });
        
        // Strategy 2: Look for "See also" section (only if nothing found yet)
        if (!foundInSection || competitors.size < 3) {
            $('h2:contains("See also")').each((i, heading) => {
                $(heading).nextAll('ul').first().find('a[href^="/wiki/"]').each((j, link) => {
                    const text = $(link).text();
                    const href = $(link).attr('href');
                    if (isLikelyCompany(text, href, subject)) {
                        competitors.add(text.trim());
                    }
                });
            });
        }
        
        const result = Array.from(competitors);
        console.log(`Wikipedia found ${result.length} potential competitors in specific sections`);
        
        // If still nothing, return empty array - better than fake data
        if (result.length === 0) {
            console.log('No competitor data found in Wikipedia');
            return [];
        }
        
        return result.slice(0, 10);
        
    } catch (error) {
        console.error('Wikipedia search failed:', error.message);
        // Try alternate spellings or search
        try {
            const searchUrl = `https://en.wikipedia.org/w/index.php?search=${encodeURIComponent(subject)}`;
            const response = await axios.get(searchUrl, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
                timeout: 10000
            });
            
            const $ = cheerio.load(response.data);
            const competitors = new Set();
            
            $('.mw-search-result-heading a').each((i, link) => {
                const text = $(link).text();
                if (text && text !== subject) {
                    competitors.add(text.trim());
                }
            });
            
            return Array.from(competitors).slice(0, 10);
        } catch (fallbackError) {
            console.error('Wikipedia fallback failed:', fallbackError.message);
            return [];
        }
    }
}

/**
 * Use Puppeteer to search Google with real browser
 */
async function searchGoogleWithBrowser(subject) {
    let browser;
    try {
        console.log(`Launching browser for Google search: ${subject}...`);
        
        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        });
        
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Set realistic user agent
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        const competitors = new Set();
        
        // Search for competitors
        const query = `${subject} competitors alternatives`;
        console.log(`Searching Google: ${query}`);
        
        await page.goto(`https://www.google.com/search?q=${encodeURIComponent(query)}`, {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // Wait for results to load
        await delay(2000);
        
        // Extract company names from search results
        const results = await page.evaluate(() => {
            const companies = [];
            
            // Get text from result titles and descriptions
            document.querySelectorAll('h3, .VwiC3b, .lyLwlc, cite, .yuRUbf').forEach(elem => {
                const text = elem.textContent;
                // Look for capitalized company names (1-3 words)
                const matches = text.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b/g);
                if (matches) {
                    matches.forEach(match => {
                        if (match.length > 2 && match.length < 30) {
                            companies.push(match.trim());
                        }
                    });
                }
            });
            
            return companies;
        });
        
        results.forEach(company => {
            if (company !== subject && 
                !company.includes('Google') && 
                !company.includes('Search') &&
                !company.includes('Results') &&
                !company.includes('Web') &&
                !company.includes('News')) {
                competitors.add(company);
            }
        });
        
        console.log(`Browser search found ${competitors.size} competitors`);
        return Array.from(competitors);
        
    } catch (error) {
        console.error('Browser search failed:', error.message);
        return [];
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

/**
 * Discover competitors using Wikipedia only (skip browser for now)
 */
async function discoverCompetitors(subject) {
    console.log(`Discovering competitors for: ${subject} (Wikipedia only)`);
    
    try {
        // Use Wikipedia only - it's faster and doesn't get blocked as much
        const wikiCompetitors = await searchWikipedia(subject);
        
        if (wikiCompetitors.length > 0) {
            console.log(`Wikipedia found ${wikiCompetitors.length} competitors`);
            return wikiCompetitors.slice(0, 10);
        }
        
        // If nothing found, return empty (no fake data)
        console.log('No competitors found from Wikipedia');
        return [];
        
    } catch (error) {
        console.error('Competitor discovery failed:', error);
        return [];
    }
}

/**
 * Search Google for company information
 */
async function searchGoogle(query) {
    try {
        console.log(`Searching Google for: ${query}`);
        await delay(500); // Small delay to avoid rate limiting
        
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query + ' company official website')}`;
        
        const response = await axios.get(searchUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        const results = [];
        
        // Try multiple selectors for Google results
        const selectors = ['div.g', 'div[data-sokoban-container]', 'div.Gx5Zad'];
        
        for (const selector of selectors) {
            $(selector).each((i, elem) => {
                if (results.length >= 10) return false;
                
                const $elem = $(elem);
                const titleElem = $elem.find('h3, a h3').first();
                const title = titleElem.text().trim();
                const linkElem = $elem.find('a[href^="http"]').first();
                let link = linkElem.attr('href');
                
                // Clean up Google redirect URLs
                if (link && link.includes('google.com/url?')) {
                    const urlMatch = link.match(/[?&]url=([^&]+)/);
                    if (urlMatch) {
                        link = decodeURIComponent(urlMatch[1]);
                    }
                }
                
                const snippet = $elem.find('div[data-sncf], div[style*="-webkit-line-clamp"], .VwiC3b').first().text().trim();
                
                if (title && link && link.startsWith('http')) {
                    try {
                        const domain = new URL(link).hostname.replace('www.', '');
                        
                        results.push({
                            name: title,
                            description: snippet || 'Official website',
                            url: link,
                            domain: domain,
                            source: 'Google'
                        });
                    } catch (urlError) {
                        // Skip invalid URLs
                    }
                }
            });
            
            if (results.length > 0) break;
        }
        
        console.log(`Google found ${results.length} results`);
        return results;
        
    } catch (error) {
        if (error.response?.status === 429) {
            console.error('Google rate limit - trying with minimal results');
            // Return empty array but don't fail completely
            return [];
        }
        console.error('Google search failed:', error.message);
        return [];
    }
}

/**
 * Search Bing for company information
 */
async function searchBing(query) {
    try {
        console.log(`Searching Bing for: ${query}`);
        await delay(500); // Small delay
        
        const searchUrl = `https://www.bing.com/search?q=${encodeURIComponent(query + ' company official website')}`;
        
        const response = await axios.get(searchUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        const results = [];
        
        // Extract Bing results - multiple selectors
        const selectors = ['li.b_algo', '#b_results > li'];
        
        for (const selector of selectors) {
            $(selector).each((i, elem) => {
                if (results.length >= 10) return false;
                
                const $elem = $(elem);
                const title = $elem.find('h2 a, a').first().text().trim();
                const link = $elem.find('h2 a, a').first().attr('href');
                const snippet = $elem.find('p, .b_caption p, .b_algoSlug').first().text().trim();
                
                if (title && link && link.startsWith('http')) {
                    try {
                        const domain = new URL(link).hostname.replace('www.', '');
                        
                        results.push({
                            name: title,
                            description: snippet || 'Official website',
                            url: link,
                            domain: domain,
                            source: 'Bing'
                        });
                    } catch (urlError) {
                        // Skip invalid URLs
                    }
                }
            });
            
            if (results.length > 0) break;
        }
        
        console.log(`Bing found ${results.length} results`);
        return results;
        
    } catch (error) {
        if (error.response?.status === 429) {
            console.error('Bing rate limit - trying with minimal results');
            return [];
        }
        console.error('Bing search failed:', error.message);
        return [];
    }
}

/**
 * Search DuckDuckGo for company information (less restrictive)
 */
async function searchDuckDuckGo(query) {
    try {
        console.log(`Searching DuckDuckGo for: ${query}`);
        const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query + ' company official website')}`;
        
        const response = await axios.get(searchUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        const results = [];
        
        // Extract DuckDuckGo results
        $('.result, .results_links').each((i, elem) => {
            if (results.length >= 10) return false;
            
            const $elem = $(elem);
            const title = $elem.find('.result__title, .result__a').text().trim();
            const link = $elem.find('.result__url, .result__a').attr('href');
            const snippet = $elem.find('.result__snippet').text().trim();
            
            if (title && link) {
                // Clean up DuckDuckGo redirect
                let cleanUrl = link;
                if (link.startsWith('//duckduckgo.com/l/?')) {
                    const urlMatch = link.match(/uddg=([^&]+)/);
                    if (urlMatch) {
                        cleanUrl = decodeURIComponent(urlMatch[1]);
                    }
                }
                
                if (cleanUrl.startsWith('http')) {
                    try {
                        const domain = new URL(cleanUrl).hostname.replace('www.', '');
                        
                        results.push({
                            name: title,
                            description: snippet || 'Official website',
                            url: cleanUrl,
                            domain: domain,
                            source: 'DuckDuckGo'
                        });
                    } catch (urlError) {
                        // Skip invalid URLs
                    }
                }
            }
        });
        
        console.log(`DuckDuckGo found ${results.length} results`);
        return results;
        
    } catch (error) {
        console.error('DuckDuckGo search failed:', error.message);
        return [];
    }
}

/**
 * Determine if a search result is likely a company
 */
function isLikelyCompanyResult(result) {
    const text = (result.name + ' ' + result.description).toLowerCase();
    
    // Strong company indicators
    const companyIndicators = [
        /\b(company|corporation|inc\.|ltd\.|llc|enterprise|business)\b/i,
        /\b(founded|headquarters|ceo|employees|revenue)\b/i,
        /\b(software|technology|services|solutions|platform)\b/i,
        /\b(manufacturer|provider|supplier|developer)\b/i,
        /\.(com|io|co|net|org)\b/i  // Company website domains
    ];
    
    // Exclude non-company content
    const excludePatterns = [
        /\b(wikipedia|youtube|facebook|twitter|linkedin|instagram)\.(com|org)/i,  // Social media (but extract info)
        /\b(news|article|blog|press release)\b/i,
        /\b(video|watch|episode|movie)\b/i,
        /\b(download|pdf|doc)\b/i
    ];
    
    // Check if it has company indicators
    const hasCompanyIndicator = companyIndicators.some(pattern => pattern.test(text));
    
    // Check if it's excluded content
    const isExcluded = excludePatterns.some(pattern => pattern.test(text + ' ' + result.url));
    
    // Special handling for official company domains
    const isCompanyDomain = result.domain && !result.domain.includes('wikipedia') && 
                           !result.domain.includes('youtube') && 
                           !result.domain.includes('news') &&
                           (result.url === result.url.match(/^https?:\/\/[^\/]+\/?$/)?.[0] || 
                            result.url.includes('/about') || 
                            result.url.includes('/company'));
    
    return (hasCompanyIndicator || isCompanyDomain) && !isExcluded;
}

/**
 * Check if a Wikipedia page is about a company
 */
async function isCompanyPage(url) {
    try {
        const response = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            timeout: 8000
        });
        
        const $ = cheerio.load(response.data);
        const pageText = $('body').text().toLowerCase();
        const infoboxText = $('.infobox').text().toLowerCase();
        
        // Exclude patterns - these are NOT companies
        const excludePatterns = [
            /\b(born|died|birth|death)\b.*\d{4}/i,  // Biographical dates
            /\bfilm\b.*\b(directed|starring|release)\b/i,
            /\balbum\b.*\b(released|track|song)\b/i,
            /\b(family|dynasty|clan)\b/i,
            /\b(species|genus|animal|plant)\b/i,
            /\bevents?\b.*\b(occurred|happened)\b/i,
            /\bperson\b|\bindividual\b|\bbiography\b/i
        ];
        
        // Check if matches exclude patterns
        if (excludePatterns.some(pattern => pattern.test(pageText.substring(0, 1000)))) {
            return false;
        }
        
        // Check categories for non-company indicators
        const categories = [];
        $('a[href*="/wiki/Category:"]').each((i, link) => {
            categories.push($(link).text().toLowerCase());
        });
        
        const badCategories = [
            'births', 'deaths', 'people', 'actors', 'musicians', 'directors',
            'films', 'movies', 'albums', 'songs', 'families', 'dynasties',
            'living people', 'biographical'
        ];
        
        if (categories.some(cat => badCategories.some(bad => cat.includes(bad)))) {
            return false;
        }
        
        // Strong company indicators in infobox
        const companyIndicators = [
            /\btype\b.*\b(public|private|subsidiary|division)\b/i,
            /\bfounded\b.*\d{4}/i,
            /\bindustry\b/i,
            /\bheadquarters\b/i,
            /\bproducts\b/i,
            /\bservices\b/i,
            /\brevenue\b/i,
            /\bemployees\b/i,
            /\bparent\b.*\b(company|corporation)\b/i,
            /\btraded as\b/i,
            /\bnyse|nasdaq|stock\b/i
        ];
        
        // Check first paragraph and infobox
        const firstPara = $('.mw-parser-output > p').first().text();
        const combinedText = (firstPara + ' ' + infoboxText).toLowerCase();
        
        if (companyIndicators.some(pattern => pattern.test(combinedText))) {
            return true;
        }
        
        // Look for company keywords in first paragraph
        const companyKeywords = [
            'company', 'corporation', 'inc.', 'ltd.', 'llc', 
            'enterprise', 'business', 'firm', 'organization',
            'software', 'technology', 'manufacturer', 'provider'
        ];
        
        if (companyKeywords.some(keyword => combinedText.includes(keyword))) {
            return true;
        }
        
        return false;
        
    } catch (error) {
        console.error('Error checking company page:', error.message);
        return false; // Exclude on error
    }
}

/**
 * Search for potential company matches to disambiguate user input
 * Combines Wikipedia, Google, and Bing results for comprehensive coverage
 */
async function searchCompanyMatches(query) {
    try {
        console.log(`Searching for company matches: ${query}`);
        const allMatches = [];
        
        // Search all sources in parallel
        const [wikiResults, googleResults, bingResults, ddgResults] = await Promise.all([
            searchWikipediaForCompanies(query),
            searchGoogle(query).catch(() => []),
            searchBing(query).catch(() => []),
            searchDuckDuckGo(query).catch(() => [])
        ]);
        
        // Process Wikipedia results (high confidence)
        wikiResults.forEach(result => {
            allMatches.push({
                ...result,
                confidence: 'high',
                priority: 1
            });
        });
        
        // Process Google results (medium-high confidence)
        googleResults.filter(isLikelyCompanyResult).forEach((result, idx) => {
            // Check if domain already exists in matches
            const existingMatch = allMatches.find(m => 
                m.url === result.url || 
                (m.domain && result.domain && m.domain === result.domain)
            );
            
            if (!existingMatch) {
                allMatches.push({
                    ...result,
                    confidence: idx === 0 ? 'high' : 'medium',
                    priority: idx === 0 ? 2 : 3
                });
            }
        });
        
        // Process Bing results (medium confidence)
        bingResults.filter(isLikelyCompanyResult).forEach((result, idx) => {
            // Check if domain already exists
            const existingMatch = allMatches.find(m => 
                m.url === result.url || 
                (m.domain && result.domain && m.domain === result.domain)
            );
            
            if (!existingMatch) {
                allMatches.push({
                    ...result,
                    confidence: idx === 0 ? 'high' : 'medium',
                    priority: idx === 0 ? 2 : 4
                });
            }
        });
        
        // Process DuckDuckGo results (medium confidence)
        ddgResults.filter(isLikelyCompanyResult).forEach((result, idx) => {
            // Check if domain already exists
            const existingMatch = allMatches.find(m => 
                m.url === result.url || 
                (m.domain && result.domain && m.domain === result.domain)
            );
            
            if (!existingMatch) {
                allMatches.push({
                    ...result,
                    confidence: idx === 0 ? 'high' : 'medium',
                    priority: idx === 0 ? 2 : 4
                });
            }
        });
        
        // Sort by priority and confidence, then limit to 10
        allMatches.sort((a, b) => {
            if (a.priority !== b.priority) return a.priority - b.priority;
            const confOrder = { high: 1, medium: 2, low: 3 };
            return confOrder[a.confidence] - confOrder[b.confidence];
        });
        
        const finalMatches = allMatches.slice(0, 10).map(m => ({
            name: m.name,
            description: m.description,
            url: m.url,
            source: m.source,
            confidence: m.confidence
        }));
        
        console.log(`Combined search found ${finalMatches.length} company matches (Wikipedia: ${wikiResults.length}, Google: ${googleResults.filter(isLikelyCompanyResult).length}, Bing: ${bingResults.filter(isLikelyCompanyResult).length}, DuckDuckGo: ${ddgResults.filter(isLikelyCompanyResult).length})`);
        return finalMatches;
        
    } catch (error) {
        console.error('Company search failed:', error.message);
        return [];
    }
}

/**
 * Search Wikipedia specifically for companies
 */
async function searchWikipediaForCompanies(query) {
    try {
        const potentialMatches = [];
        const searchUrl = `https://en.wikipedia.org/w/index.php?search=${encodeURIComponent(query)}&limit=10`;
        
        const response = await axios.get(searchUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        
        // Check if redirected to exact match
        if ($('.mw-parser-output').length > 0 && $('.mw-search-results').length === 0) {
            const url = response.request.res.responseUrl;
            const isCompany = await isCompanyPage(url);
            
            if (isCompany) {
                const title = $('#firstHeading').text().trim();
                const description = $('.mw-parser-output > p').first().text().trim().substring(0, 200);
                
                return [{
                    name: title,
                    description: description + '...',
                    url: url,
                    source: 'Wikipedia',
                    domain: 'wikipedia.org'
                }];
            }
        } else {
            // Multiple results
            $('.mw-search-result').each((i, result) => {
                if (i >= 10) return false;
                
                const title = $(result).find('.mw-search-result-heading a').text().trim();
                const snippet = $(result).find('.searchresult').text().trim();
                const relativeUrl = $(result).find('.mw-search-result-heading a').attr('href');
                
                if (title && !title.match(/^(List of|Category:|Wikipedia:|Help:)/i)) {
                    potentialMatches.push({
                        title: title,
                        snippet: snippet,
                        url: `https://en.wikipedia.org${relativeUrl}`
                    });
                }
            });
        }
        
        // Verify each is a company (limit parallel requests)
        const matches = [];
        for (const match of potentialMatches.slice(0, 5)) {
            try {
                const isCompany = await isCompanyPage(match.url);
                if (isCompany) {
                    matches.push({
                        name: match.title,
                        description: match.snippet,
                        url: match.url,
                        source: 'Wikipedia',
                        domain: 'wikipedia.org'
                    });
                }
            } catch (err) {
                // Skip on error
            }
        }
        
        return matches;
        
    } catch (error) {
        console.error('Wikipedia search failed:', error.message);
        return [];
    }
}

/**
 * Extract revenue information from Wikipedia infobox
 */
async function extractRevenueFromWikipedia(companyName) {
    try {
        console.log(`Extracting revenue from Wikipedia for ${companyName}...`);
        
        const pageUrl = `https://en.wikipedia.org/wiki/${encodeURIComponent(companyName.replace(/\s+/g, '_'))}`;
        
        const response = await axios.get(pageUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        
        // Look for revenue in infobox
        let revenue = null;
        
        // Strategy 1: Find the "Revenue" row in infobox
        $('.infobox tr').each((i, row) => {
            const header = $(row).find('th').text().toLowerCase().trim();
            if (header.includes('revenue')) {
                const valueText = $(row).find('td').text().trim();
                revenue = parseRevenue(valueText);
                return false; // break
            }
        });
        
        // Strategy 2: Look for revenue in text
        if (!revenue) {
            const bodyText = $('.mw-parser-output').text();
            const revenueMatch = bodyText.match(/revenue[:\s]+(?:US\$|USD|\$|€|£)?\s*([\d,.]+)\s*(billion|million|trillion)/i);
            if (revenueMatch) {
                revenue = parseRevenue(revenueMatch[0]);
            }
        }
        
        return revenue;
        
    } catch (error) {
        console.error(`Failed to extract revenue from Wikipedia: ${error.message}`);
        return null;
    }
}

/**
 * Parse revenue string to millions USD
 * Examples: "$5.6 billion" -> 5600, "€2.3B" -> 2300, "1.2 million" -> 1.2
 */
function parseRevenue(revenueText) {
    if (!revenueText) return null;
    
    const text = revenueText.toLowerCase().replace(/,/g, '');
    
    // Extract number
    const numberMatch = text.match(/([\d.]+)/);
    if (!numberMatch) return null;
    
    const baseNumber = parseFloat(numberMatch[1]);
    if (isNaN(baseNumber)) return null;
    
    // Determine multiplier
    let multiplier = 1;
    if (text.includes('trillion') || text.includes('tn')) {
        multiplier = 1000000; // trillion to million
    } else if (text.includes('billion') || text.includes('bn') || text.includes('b')) {
        multiplier = 1000; // billion to million
    } else if (text.includes('million') || text.includes('mn') || text.includes('m')) {
        multiplier = 1;
    } else if (text.includes('thousand') || text.includes('k')) {
        multiplier = 0.001; // thousand to million
    }
    
    const revenueInMillions = baseNumber * multiplier;
    
    // Sanity check (revenue between $0.1M and $1 trillion)
    if (revenueInMillions < 0.1 || revenueInMillions > 1000000) {
        return null;
    }
    
    return Math.round(revenueInMillions);
}

module.exports = {
    discoverCompetitors,
    searchWikipedia,
    searchGoogleWithBrowser,
    searchCompanyMatches,
    extractRevenueFromWikipedia
};
