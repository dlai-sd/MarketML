/**
 * Groq-powered Indian Company Data Extractor
 * Uses Groq API + web search to extract company information
 * Cost: ~$0.001 per company vs ₹8-12 for API Setu
 */

const axios = require('axios');
const cheerio = require('cheerio');

class GroqCompanyExtractor {
    constructor() {
        // Groq API configuration
        this.groqApiKey = process.env.GROQ_API_KEY || '';
        this.groqBaseUrl = 'https://api.groq.com/openai/v1';
        this.model = 'llama-3.3-70b-versatile'; // Fast and accurate
        
        // Search configuration
        this.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';
    }

    /**
     * Main function: Extract company data from name
     * @param {string} companyName - Company name (e.g., "Yashus Digital Marketing")
     * @returns {Promise<Object>} Extracted company data
     */
    async extractCompanyData(companyName) {
        console.log(`\n🔍 Extracting data for: ${companyName}`);
        
        try {
            // Step 1: Search for company information
            const searchResults = await this.searchCompanyInfo(companyName);
            
            // Step 2: Use Groq to extract structured data
            const extractedData = await this.extractWithGroq(companyName, searchResults);
            
            return {
                success: true,
                company_name: companyName,
                data: extractedData,
                sources: searchResults.map(r => r.url),
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error(`❌ Error extracting data for ${companyName}:`, error.message);
            return {
                success: false,
                company_name: companyName,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Search for company information from multiple sources
     * @param {string} companyName 
     * @returns {Promise<Array>} Search results
     */
    async searchCompanyInfo(companyName) {
        const searches = [
            `${companyName} MCA India CIN registration`,
            `${companyName} company directors revenue financial year`,
            `${companyName} authorized capital paid up capital`,
            `${companyName} ZaubaCorp company details`
        ];

        const results = [];
        
        for (const query of searches) {
            try {
                const searchData = await this.googleSearch(query);
                if (searchData.length > 0) {
                    results.push(...searchData.slice(0, 3)); // Top 3 results per query
                }
                await this.delay(1000); // Rate limiting
            } catch (error) {
                console.log(`  ⚠️  Search failed for: ${query}`);
            }
        }

        console.log(`  ✅ Found ${results.length} search results`);
        return results;
    }

    /**
     * Perform Google search and extract results
     * @param {string} query 
     * @returns {Promise<Array>}
     */
    async googleSearch(query) {
        try {
            const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
            const response = await axios.get(searchUrl, {
                headers: {
                    'User-Agent': this.userAgent
                },
                timeout: 10000
            });

            const $ = cheerio.load(response.data);
            const results = [];

            // Extract search results
            $('div.g').each((i, element) => {
                const title = $(element).find('h3').first().text();
                const snippet = $(element).find('.VwiC3b').first().text();
                const link = $(element).find('a').first().attr('href');

                if (title && snippet) {
                    results.push({
                        title,
                        snippet,
                        url: link || '',
                        query: query
                    });
                }
            });

            return results;
        } catch (error) {
            console.log(`  ⚠️  Google search error: ${error.message}`);
            return [];
        }
    }

    /**
     * Use Groq API to extract structured data from search results
     * @param {string} companyName 
     * @param {Array} searchResults 
     * @returns {Promise<Object>}
     */
    async extractWithGroq(companyName, searchResults) {
        if (!this.groqApiKey) {
            throw new Error('GROQ_API_KEY not configured. Please set it in environment variables.');
        }

        // Prepare context from search results
        const context = searchResults.map((result, idx) => 
            `[Result ${idx + 1}]\nTitle: ${result.title}\nSnippet: ${result.snippet}\nURL: ${result.url}\n`
        ).join('\n');

        const prompt = `You are an expert at extracting Indian company information from web search results.

Company Name: ${companyName}

Search Results:
${context}

Extract the following information in JSON format:
{
  "cin": "Corporate Identification Number (format: U12345XX2020PTC123456)",
  "company_name": "Official registered name",
  "registration_date": "DD-MM-YYYY",
  "status": "Active/Strike Off/Amalgamated/etc",
  "roc": "Registrar of Companies location",
  "company_class": "Private/Public/etc",
  "authorized_capital": "Amount in INR",
  "paid_up_capital": "Amount in INR",
  "financial_year": "FY 2023-24 or latest",
  "latest_revenue": "Revenue in INR Crores for latest FY",
  "pan": "PAN number if available",
  "directors": [
    {
      "name": "Director name",
      "din": "Director Identification Number",
      "appointment_date": "DD-MM-YYYY"
    }
  ],
  "address": "Registered office address",
  "email": "Contact email if available",
  "phone": "Contact phone if available",
  "confidence": "high/medium/low based on data quality"
}

Instructions:
1. Extract ONLY information explicitly mentioned in the search results
2. Use "Not available" for missing fields
3. For revenue, convert to Crores if needed (e.g., "₹1.87 Crore")
4. Ensure CIN format is correct if found
5. Return ONLY valid JSON, no explanations`;

        try {
            console.log('  🤖 Querying Groq API...');
            
            const response = await axios.post(
                `${this.groqBaseUrl}/chat/completions`,
                {
                    model: this.model,
                    messages: [
                        {
                            role: 'system',
                            content: 'You are a precise data extraction assistant. Return only valid JSON.'
                        },
                        {
                            role: 'user',
                            content: prompt
                        }
                    ],
                    temperature: 0.1,
                    max_tokens: 2000,
                    response_format: { type: 'json_object' }
                },
                {
                    headers: {
                        'Authorization': `Bearer ${this.groqApiKey}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 30000
                }
            );

            const extracted = JSON.parse(response.data.choices[0].message.content);
            console.log('  ✅ Groq extraction complete');
            
            // Add metadata
            extracted.extraction_confidence = extracted.confidence || 'medium';
            extracted.extraction_method = 'groq_web_search';
            extracted.token_usage = response.data.usage;

            return extracted;

        } catch (error) {
            console.error('  ❌ Groq API error:', error.message);
            
            // Fallback: basic extraction from search results
            return this.fallbackExtraction(companyName, searchResults);
        }
    }

    /**
     * Fallback extraction without Groq (basic regex/pattern matching)
     * @param {string} companyName 
     * @param {Array} searchResults 
     * @returns {Object}
     */
    fallbackExtraction(companyName, searchResults) {
        console.log('  ℹ️  Using fallback extraction');
        
        const fullText = searchResults.map(r => `${r.title} ${r.snippet}`).join(' ');
        
        // Basic pattern matching
        const cinMatch = fullText.match(/CIN[:\s]*([A-Z0-9]{21})/i);
        const revenueMatch = fullText.match(/₹\s*([\d.]+)\s*Crore/i);
        const fyMatch = fullText.match(/FY\s*(\d{4}-\d{2,4})/i);
        
        return {
            company_name: companyName,
            cin: cinMatch ? cinMatch[1] : 'Not available',
            latest_revenue: revenueMatch ? `₹${revenueMatch[1]} Crore` : 'Not available',
            financial_year: fyMatch ? fyMatch[1] : 'Not available',
            status: 'Not available',
            directors: [],
            confidence: 'low',
            extraction_method: 'fallback_regex',
            note: 'Limited data - Groq API not available'
        };
    }

    /**
     * Utility: Delay function
     * @param {number} ms 
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Validate extracted data
     * @param {Object} data 
     * @returns {boolean}
     */
    validateData(data) {
        // Check if CIN format is valid
        if (data.cin && data.cin !== 'Not available') {
            const cinRegex = /^[A-Z][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$/;
            if (!cinRegex.test(data.cin)) {
                console.warn('  ⚠️  Invalid CIN format');
            }
        }
        
        return true;
    }
}

// Export for use in other modules
module.exports = GroqCompanyExtractor;

// Test function (run directly)
if (require.main === module) {
    const extractor = new GroqCompanyExtractor();
    
    const testCompanies = [
        'Yashus Digital Marketing',
        'DLAI Satellite Data'
    ];
    
    (async () => {
        for (const company of testCompanies) {
            const result = await extractor.extractCompanyData(company);
            console.log('\n📊 Result:', JSON.stringify(result, null, 2));
            console.log('\n' + '='.repeat(80) + '\n');
            await extractor.delay(2000); // Delay between companies
        }
    })();
}
