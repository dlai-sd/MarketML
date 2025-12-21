const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Indian Company Data Scraper
 * Uses ZaubaCorp (aggregates MCA data) for CIN-based lookups
 */

/**
 * Validate CIN format (21 characters)
 * Format: LXXXXX[ST]YYYYPLCXXXXXX
 * L/U: Listed/Unlisted
 * XXXXX: Industry code
 * ST: State code
 * YYYY: Year of incorporation
 * PLC/PTC: Public/Private Limited Company
 * XXXXXX: Serial number
 */
function isValidCIN(cin) {
    if (!cin || typeof cin !== 'string') return false;
    
    // Must be exactly 21 characters
    if (cin.length !== 21) return false;
    
    // Pattern: [UL] + 5 digits + 2 letters + 4 digits + 3 letters + 6 digits
    const cinPattern = /^[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$/;
    return cinPattern.test(cin.toUpperCase());
}

/**
 * Search for company CIN on ZaubaCorp with flexible matching
 */
async function searchCompanyCIN(companyName) {
    try {
        console.log(`[CIN] Searching for ${companyName} on ZaubaCorp...`);
        
        // Try multiple search strategies
        const searchStrategies = [
            // Strategy 1: Full company name (cleaned)
            companyName.toLowerCase().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, '-'),
            // Strategy 2: Remove common suffixes
            companyName.toLowerCase()
                .replace(/\s+(private|pvt|limited|ltd|llp|llc|inc|corporation|corp)\s*$/gi, '')
                .replace(/[^a-z0-9\s]/g, '')
                .replace(/\s+/g, '-'),
            // Strategy 3: First significant word only (for partial match)
            companyName.toLowerCase()
                .split(/\s+/)
                .filter(word => word.length > 3)
                .slice(0, 2)
                .join('-')
                .replace(/[^a-z0-9-]/g, ''),
            // Strategy 4: Try with 'p' prefix (common pattern)
            'p/' + companyName.toLowerCase()
                .split(/\s+/)
                .filter(word => word.length > 3)
                .slice(0, 2)
                .join('-')
                .replace(/[^a-z0-9-]/g, '')
        ];
        
        let allResults = [];
        
        for (let idx = 0; idx < searchStrategies.length; idx++) {
            const searchName = searchStrategies[idx];
            if (!searchName || searchName.length < 3) continue;
            
            try {
                // Try direct company page first (more likely to work)
                const directUrl = `https://www.zaubacorp.com/company/${searchName}/COMPANY`;
                
                console.log(`[CIN] Trying direct: ${directUrl}`);
                
                const response = await axios.get(directUrl, {
                    headers: {
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Cache-Control': 'max-age=0'
                    },
                    timeout: 15000,
                    maxRedirects: 5,
                    validateStatus: function (status) {
                        return status < 500; // Accept 4xx errors to try next strategy
                    }
                });
                
                if (response.status === 200) {
                    const $ = cheerio.load(response.data);
                    
                    // Extract CIN from page
                    const pageText = $('body').text();
                    const cinMatch = pageText.match(/([UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6})/);
                    
                    if (cinMatch) {
                        const name = $('h1, .company-name').first().text().trim() || companyName;
                        let status = 'Unknown';
                        
                        if (pageText.toLowerCase().includes('active')) {
                            status = 'Active';
                        } else if (pageText.toLowerCase().includes('dissolved') || pageText.toLowerCase().includes('strike')) {
                            status = 'Dissolved';
                        }
                        
                        allResults.push({
                            name: name,
                            cin: cinMatch[1],
                            status: status,
                            source: 'MCA (ZaubaCorp)'
                        });
                        
                        console.log(`[CIN] Found match with direct URL!`);
                        break;
                    }
                }
                
                // Small delay between attempts
                await new Promise(resolve => setTimeout(resolve, 1500));
                
            } catch (strategyError) {
                console.log(`[CIN] Strategy ${idx + 1} failed: ${strategyError.message}, trying next...`);
                await new Promise(resolve => setTimeout(resolve, 1000));
                continue;
            }
        }
        
        // Remove duplicates based on CIN
        const uniqueResults = [];
        const seenCINs = new Set();
        for (const result of allResults) {
            if (!seenCINs.has(result.cin)) {
                seenCINs.add(result.cin);
                uniqueResults.push(result);
            }
        }
        
        console.log(`[CIN] Total unique matches: ${uniqueResults.length}`);
        return uniqueResults;
        
    } catch (error) {
        console.error(`[CIN] Search failed for ${companyName}:`, error.message);
        return [];
    }
}

/**
 * Get detailed company information using CIN
 */
async function getCompanyDetailsByCIN(cin, companyName = '') {
    try {
        if (!isValidCIN(cin)) {
            console.error(`[CIN] Invalid CIN format: ${cin}`);
            return null;
        }
        
        console.log(`[CIN] Fetching details for CIN: ${cin}`);
        
        // Build URL: https://www.zaubacorp.com/company/[CIN]/[COMPANY-NAME]
        const urlName = companyName
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+$/, '');
        
        const detailUrl = `https://www.zaubacorp.com/company/${cin}/${urlName || 'COMPANY'}`;
        
        const response = await axios.get(detailUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            timeout: 15000
        });
        
        const $ = cheerio.load(response.data);
        
        // Extract company details
        const details = {
            cin: cin,
            name: $('.company-name, h1').first().text().trim() || companyName,
            status: 'Unknown',
            revenue_inr_millions: null,
            financial_year: null,
            latest_revenue: null,
            paid_up_capital: null,
            authorized_capital: null,
            date_of_incorporation: null,
            registered_office: null,
            activity: null,
            email: null,
            phone: null,
            address: null,
            pan: null,
            directors: [],
            roc: null,
            company_class: null
        };
        
        // Parse company info table
        $('.table tr, .company-info tr, .details-table tr').each((i, row) => {
            const $row = $(row);
            const label = $row.find('th, td:first-child, .label').text().toLowerCase().trim();
            const value = $row.find('td:last-child, .value').text().trim();
            
            if (label.includes('status')) {
                details.status = value;
            } else if (label.includes('paid') && label.includes('capital')) {
                details.paid_up_capital = parseIndianCurrency(value);
            } else if (label.includes('authorized') && label.includes('capital')) {
                details.authorized_capital = parseIndianCurrency(value);
            } else if (label.includes('incorporation') || label.includes('registration')) {
                details.date_of_incorporation = value;
            } else if (label.includes('activity') || label.includes('business')) {
                details.activity = value;
            } else if (label.includes('office') || label.includes('address') || label.includes('registered')) {
                details.registered_office = value;
                details.address = value; // Also store as address
            } else if (label.includes('email') || label.includes('e-mail')) {
                details.email = value;
            } else if (label.includes('phone') || label.includes('mobile') || label.includes('contact')) {
                details.phone = value;
            } else if (label.includes('pan') || label.includes('permanent account')) {
                details.pan = value;
            } else if (label.includes('roc') || label.includes('registrar')) {
                details.roc = value;
            } else if (label.includes('class') || label.includes('category')) {
                details.company_class = value;
            }
        });
        
        // Extract email from page if not in table
        if (!details.email) {
            const emailMatch = $('body').text().match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/);
            if (emailMatch) {
                details.email = emailMatch[1];
            }
        }
        
        // Extract phone from page if not in table
        if (!details.phone) {
            const phonePatterns = [
                /(?:\+91|91)?[\s-]?[6-9]\d{9}/g,
                /\d{3}[-\s]?\d{3}[-\s]?\d{4}/g
            ];
            
            const bodyText = $('body').text();
            for (const pattern of phonePatterns) {
                const match = bodyText.match(pattern);
                if (match) {
                    details.phone = match[0].trim();
                    break;
                }
            }
        }
        
        // Extract PAN from page if not in table
        if (!details.pan) {
            const panMatch = $('body').text().match(/[A-Z]{5}[0-9]{4}[A-Z]{1}/g);
            if (panMatch) {
                details.pan = panMatch[0];
            }
        }
        
        // Extract directors information
        const directors = [];
        $('.directors-list tr, .director-item, [class*="director"] tr').each((i, row) => {
            const $row = $(row);
            const rowText = $row.text();
            
            // Skip header rows
            if (rowText.toLowerCase().includes('name') && rowText.toLowerCase().includes('din')) {
                return;
            }
            
            const directorName = $row.find('td:first-child, .director-name').text().trim();
            const din = rowText.match(/\b\d{8}\b/); // DIN is 8 digits
            
            if (directorName && directorName.length > 2) {
                const director = {
                    name: directorName,
                    din: din ? din[0] : null
                };
                
                // Try to extract designation
                const designation = $row.find('td:eq(1), .designation').text().trim();
                if (designation && designation.length > 0 && designation !== directorName) {
                    director.designation = designation;
                }
                
                // Try to extract shareholding
                const shareholdingMatch = rowText.match(/(\d+\.?\d*)\s*%/);
                if (shareholdingMatch) {
                    director.shareholding = parseFloat(shareholdingMatch[1]);
                }
                
                directors.push(director);
            }
        });
        
        // Also check for directors in a different format
        if (directors.length === 0) {
            $('[class*="director"]').each((i, elem) => {
                const text = $(elem).text();
                const nameMatch = text.match(/([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/);
                const dinMatch = text.match(/\b(\d{8})\b/);
                
                if (nameMatch && nameMatch[1].length > 5) {
                    const director = {
                        name: nameMatch[1].trim(),
                        din: dinMatch ? dinMatch[1] : null
                    };
                    
                    const shareholdingMatch = text.match(/(\d+\.?\d*)\s*%/);
                    if (shareholdingMatch) {
                        director.shareholding = parseFloat(shareholdingMatch[1]);
                    }
                    
                    directors.push(director);
                }
            });
        }
        
        details.directors = directors;
        
        // Extract financial data (revenue)
        const bodyText = $('body').text();
        
        // Extract financial year (FY 2023-24, FY2023, 2022-23, etc.)
        const fyPatterns = [
            /FY\s*(\d{4})[-]?(\d{2,4})?/i,
            /financial\s*year\s*(\d{4})[-]?(\d{2,4})?/i,
            /(\d{4})[-](\d{2,4})/
        ];
        
        for (const pattern of fyPatterns) {
            const match = bodyText.match(pattern);
            if (match) {
                details.financial_year = match[0];
                break;
            }
        }
        
        // Look for revenue patterns in financials section
        const revenuePatterns = [
            /revenue[:\s]+₹\s*([\d,.]+)\s*(crore|lakh|thousand)/i,
            /turnover[:\s]+₹\s*([\d,.]+)\s*(crore|lakh|thousand)/i,
            /sales[:\s]+₹\s*([\d,.]+)\s*(crore|lakh|thousand)/i
        ];
        
        for (const pattern of revenuePatterns) {
            const match = bodyText.match(pattern);
            if (match) {
                details.revenue_inr_millions = parseIndianCurrency(match[0]);
                details.latest_revenue = match[0]; // Store original format
                break;
            }
        }
        
        console.log(`[CIN] Details fetched for ${details.name}`);
        return details;
        
    } catch (error) {
        console.error(`[CIN] Failed to fetch details for ${cin}:`, error.message);
        return null;
    }
}

/**
 * Parse Indian currency formats to millions INR
 * Examples:
 * - "₹5.6 crore" -> 56 million INR
 * - "₹2.3 lakh" -> 0.23 million INR
 * - "₹100 crore" -> 1000 million INR
 * - "Rs. 50,000" -> 0.05 million INR
 */
function parseIndianCurrency(text) {
    if (!text) return null;
    
    const cleaned = text.toLowerCase()
        .replace(/₹|rs\.?|inr/g, '')
        .replace(/,/g, '')
        .trim();
    
    // Extract number
    const numberMatch = cleaned.match(/([\d.]+)/);
    if (!numberMatch) return null;
    
    const baseNumber = parseFloat(numberMatch[1]);
    if (isNaN(baseNumber)) return null;
    
    // Determine multiplier (convert to millions INR)
    let multiplier = 1;
    
    if (cleaned.includes('crore') || cleaned.includes('cr')) {
        multiplier = 10; // 1 crore = 10 million
    } else if (cleaned.includes('lakh') || cleaned.includes('lac')) {
        multiplier = 0.1; // 1 lakh = 0.1 million
    } else if (cleaned.includes('thousand') || cleaned.includes('k')) {
        multiplier = 0.001; // 1 thousand = 0.001 million
    } else if (cleaned.includes('billion')) {
        multiplier = 1000; // 1 billion = 1000 million
    } else {
        // Assume base value is in rupees, convert to millions
        multiplier = 0.000001;
    }
    
    const revenueInMillions = baseNumber * multiplier;
    
    // Sanity check (between 0.01M and 10,000,000M INR)
    if (revenueInMillions < 0.01 || revenueInMillions > 10000000) {
        return null;
    }
    
    return Math.round(revenueInMillions * 100) / 100; // Round to 2 decimals
}

/**
 * Convert INR millions to USD millions
 * Using approximate rate: 1 USD = 83 INR
 */
function convertINRtoUSD(inrMillions) {
    if (!inrMillions || inrMillions <= 0) return null;
    const exchangeRate = 83;
    return Math.round((inrMillions / exchangeRate) * 100) / 100;
}

/**
 * Format Indian currency for display
 */
function formatIndianCurrency(millions) {
    if (!millions || millions <= 0) return null;
    
    if (millions >= 10) {
        // Display in crores
        return `₹${(millions / 10).toFixed(1)} Cr`;
    } else if (millions >= 0.1) {
        // Display in lakhs
        return `₹${(millions / 0.1).toFixed(0)} L`;
    } else {
        // Display in thousands
        return `₹${(millions * 1000).toFixed(0)} K`;
    }
}

/**
 * Main function: Search and get Indian company data
 */
async function searchIndianCompany(companyName) {
    try {
        console.log(`[Indian Company] Searching for: ${companyName}`);
        
        // Step 1: Search for CIN
        const searchResults = await searchCompanyCIN(companyName);
        
        if (searchResults.length === 0) {
            console.log(`[Indian Company] No CIN found for ${companyName}`);
            return [];
        }
        
        // Step 2: Enhance results with detailed data
        const enhancedResults = [];
        
        for (const result of searchResults.slice(0, 5)) { // Limit to top 5
            const details = await getCompanyDetailsByCIN(result.cin, result.name);
            
            if (details) {
                enhancedResults.push({
                    name: details.name || result.name,
                    cin: result.cin,
                    status: details.status || result.status,
                    revenue_inr_millions: details.revenue_inr_millions,
                    revenue_usd_millions: convertINRtoUSD(details.revenue_inr_millions),
                    revenue_display: formatIndianCurrency(details.revenue_inr_millions),
                    financial_year: details.financial_year,
                    latest_revenue: details.latest_revenue,
                    paid_up_capital: details.paid_up_capital,
                    authorized_capital: details.authorized_capital,
                    date_of_incorporation: details.date_of_incorporation,
                    activity: details.activity,
                    address: details.address || details.registered_office,
                    email: details.email,
                    phone: details.phone,
                    pan: details.pan,
                    directors: details.directors || [],
                    roc: details.roc,
                    company_class: details.company_class,
                    source: 'MCA (ZaubaCorp)',
                    verified: true
                });
            } else {
                // Include basic result even if details fetch failed
                enhancedResults.push({
                    ...result,
                    verified: true
                });
            }
            
            // Small delay to avoid rate limiting
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        return enhancedResults;
        
    } catch (error) {
        console.error(`[Indian Company] Search failed:`, error.message);
        return [];
    }
}

module.exports = {
    searchIndianCompany,
    searchCompanyCIN,
    getCompanyDetailsByCIN,
    isValidCIN,
    parseIndianCurrency,
    convertINRtoUSD,
    formatIndianCurrency
};
