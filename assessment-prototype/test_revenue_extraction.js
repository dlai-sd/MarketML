require('dotenv').config();
const GroqCompanyExtractor = require('./scrapers/groqCompanyData');

async function testRevenueExtraction() {
    const testCompanies = [
        'Infosys',
        'Wipro',
        'DLAI Satellite Data',
        'Yashus Digital Marketing',
        'Nature Prime'
    ];
    
    console.log('=' .repeat(80));
    console.log('REVENUE EXTRACTION TEST - Multiple Companies');
    console.log('='.repeat(80));
    
    const extractor = new GroqCompanyExtractor();
    
    for (const company of testCompanies) {
        console.log(`\n${'='.repeat(80)}`);
        console.log(`Company: ${company}`);
        console.log('='.repeat(80));
        
        try {
            const result = await extractor.extractCompanyData(company);
            
            if (result.success) {
                const d = result.data;
                console.log(`\n✅ Extraction successful`);
                console.log(`   Official Name: ${d.company_name}`);
                console.log(`   CIN: ${d.cin}`);
                console.log(`\n   💰 FINANCIAL DATA:`);
                console.log(`      Latest Revenue: ${d.latest_revenue}`);
                console.log(`      Revenue (USD M): ${d.revenue_usd_millions || 'Not available'}`);
                console.log(`      Financial Year: ${d.financial_year}`);
                console.log(`      PAT: ${d.profit_after_tax || 'Not available'}`);
                console.log(`      Total Assets: ${d.total_assets || 'Not available'}`);
            } else {
                console.log(`\n❌ Extraction failed: ${result.error}`);
            }
        } catch (error) {
            console.log(`\n❌ Error: ${error.message}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    console.log('\n' + '='.repeat(80));
    console.log('TEST COMPLETE');
    console.log('='.repeat(80));
}

testRevenueExtraction().catch(console.error);
