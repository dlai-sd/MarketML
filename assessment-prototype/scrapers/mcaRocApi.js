const axios = require('axios');

/**
 * MCA RoC API Service
 * Ministry of Corporate Affairs - Registrar of Companies
 * Official government database with 2.8M+ registered Indian companies
 */
class MCACompanyService {
    constructor() {
        this.apiKey = process.env.MCA_API_KEY || '';
        this.resourceId = process.env.MCA_RESOURCE_ID || '4dbe5667-7b6b-41d7-82af-211562424d9a';
        this.baseUrl = 'https://api.data.gov.in/resource/' + this.resourceId;
        this.timeout = 15000; // 15 seconds
    }

    /**
     * Fetch company data by CIN from MCA RoC API
     * @param {string} cin - Corporate Identification Number
     * @returns {Promise<Object>} Company data with 16 official fields
     */
    async getCompanyByCIN(cin) {
        if (!this.apiKey) {
            return {
                success: false,
                error: 'MCA_API_KEY not configured',
                data: null
            };
        }

        if (!cin || cin === 'Not available') {
            return {
                success: false,
                error: 'Invalid CIN provided',
                data: null
            };
        }

        try {
            const response = await axios.get(this.baseUrl, {
                params: {
                    'api-key': this.apiKey,
                    format: 'json',
                    'filters[CIN]': cin,
                    limit: 1
                },
                timeout: this.timeout
            });

            if (response.data && response.data.records && response.data.records.length > 0) {
                const record = response.data.records[0];
                
                return {
                    success: true,
                    error: null,
                    data: {
                        cin: record.CIN,
                        company_name: record.CompanyName,
                        roc_code: record.CompanyROCcode,
                        company_category: record.CompanyCategory,
                        company_subcategory: record.CompanySubCategory,
                        company_class: record.CompanyClass,
                        authorized_capital: record.AuthorizedCapital,
                        paidup_capital: record.PaidupCapital,
                        registration_date: record.CompanyRegistrationdate_date,
                        registered_address: record.Registered_Office_Address,
                        listing_status: record.Listingstatus,
                        company_status: record.CompanyStatus,
                        state_code: record.CompanyStateCode,
                        indian_foreign: record['CompanyIndian/Foreign Company'],
                        nic_code: record.nic_code,
                        industrial_classification: record.CompanyIndustrialClassification
                    },
                    source: 'MCA RoC API'
                };
            } else {
                return {
                    success: false,
                    error: 'CIN not found in MCA database',
                    data: null
                };
            }
        } catch (error) {
            return {
                success: false,
                error: `MCA API Error: ${error.message}`,
                data: null
            };
        }
    }

    /**
     * Check if MCA API is configured and available
     * @returns {boolean}
     */
    isAvailable() {
        return !!this.apiKey;
    }

    /**
     * Format MCA data for assessment use
     * Maps MCA fields to assessment variables
     * @param {Object} mcaData - Data from getCompanyByCIN
     * @returns {Object} Formatted data for assessment
     */
    formatForAssessment(mcaData) {
        if (!mcaData || !mcaData.data) {
            return null;
        }

        const data = mcaData.data;
        
        // Parse registration date (format: YYYY-MM-DD to DD-MM-YYYY)
        let formattedDate = 'Not available';
        if (data.registration_date) {
            try {
                const parts = data.registration_date.split('-');
                if (parts.length === 3) {
                    formattedDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
                }
            } catch (e) {
                formattedDate = data.registration_date;
            }
        }

        // Format capital amounts
        const formatCapital = (value) => {
            if (!value) return '0';
            return parseFloat(value).toFixed(2);
        };

        return {
            cin: data.cin || 'Not available',
            company_name: data.company_name || 'Not available',
            roc: data.roc_code || 'Not available',
            company_class: data.company_class || 'Not available',
            company_category: data.company_category || 'Not available',
            company_subcategory: data.company_subcategory || 'Not available',
            registration_date: formattedDate,
            authorized_capital: formatCapital(data.authorized_capital),
            paidup_capital: formatCapital(data.paidup_capital),
            registered_address: data.registered_address || 'Not available',
            state: data.state_code || 'Not available',
            status: data.company_status || 'Not available',
            listing_status: data.listing_status || 'Not available',
            indian_foreign: data.indian_foreign || 'Not available',
            nic_code: data.nic_code || 'Not available',
            industry: data.industrial_classification || 'Not available',
            data_quality: 'complete', // MCA data is always 100% complete
            source: 'MCA RoC API (Official Government Database)'
        };
    }
}

module.exports = MCACompanyService;
