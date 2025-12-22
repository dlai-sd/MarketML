const axios = require('axios');
require('dotenv').config();
const GroqCompanyExtractor = require('./scrapers/groqCompanyData');

async function testFinancialDataSources() {
    const testCompanies = [
        { name: 'Yashus Digital Marketing', cin: 'U74120PN2015PTC157176' },
        { name: 'Tata Consultancy Services', cin: 'L22210MH1995PLC084781' }, // Large public company
        { name: 'Infosys', cin: 'L85110KA1981PLC013115' } // Another large company
    ];
    
    console.log('=' .repeat(80));
    console.log('TESTING FINANCIAL DATA SOURCES');
    console.log('='.repeat(80));
    
    for (const company of testCompanies) {
        console.log(`\n${'='.repeat(80)}`);
        console.log(`Company: ${company.name} (CIN: ${company.cin})`);
        console.log('='.repeat(80));
        
        // Source 1: Try Groq AI to find revenue
        console.log('\n1️⃣ Testing Groq AI for revenue extraction...');
        try {
            const extractor = new GroqCompanyExtractor();
            const groqResult = await extractor.extractCompanyData(company.name);
            
            if (groqResult.success && groqResult.data.latest_revenue) {
                console.log(`   ✅ Groq found revenue: ${groqResult.data.latest_revenue}`);
                console.log(`   Financial Year: ${groqResult.data.financial_year || 'Not specified'}`);
            } else {
                console.log(`   ❌ No revenue data from Groq`);
            }
        } catch (error) {
            console.log(`   ❌ Groq error: ${error.message}`);
        }
        
        // Source 2: Try MCA website scraping (company master data)
        console.log('\n2️⃣ Testing MCA website for financial data...');
        try {
            const mcaUrl = `https://www.mca.gov.in/mcafoportal/companyLLPMasterData.do`;
            console.log(`   ℹ️  MCA requires manual form submission - not suitable for API`);
        } catch (error) {
            console.log(`   ❌ MCA website error: ${error.message}`);
        }
        
        // Source 3: Check Zauba Corp (we already scrape this)
        console.log('\n3️⃣ Checking ZaubaCorp...');
        console.log(`   ℹ️  Already integrated in searchIndianCompany()`);
        console.log(`   URL: https://www.zaubacorp.com/company/${company.cin}`);
        
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    console.log('\n' + '='.repeat(80));
    console.log('SUMMARY & RECOMMENDATIONS');
    console.log('='.repeat(80));
    console.log('\n📊 Available Financial Data Sources:\n');
    console.log('1. Groq AI (Web Search) - Variable success, latest revenue from web');
    console.log('2. ZaubaCorp - Already scraped, has some financial data');
    console.log('3. MCA API - Registration data only, NO financial statements');
    console.log('4. Company Annual Reports - Manual download required');
    console.log('\n💡 Recommended Approach:');
    console.log('   - Enhance Groq prompt to specifically extract FY revenue');
    console.log('   - Add financial year context to extraction');
    console.log('   - Parse revenue in multiple formats (Crore, Lakh, Million)');
    console.log('   - For public companies, try stock market APIs (NSE/BSE)');
}

testFinancialDataSources().catch(console.error);
