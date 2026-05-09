from __future__ import annotations

DEFAULT_FX = {"USDINR": 91.58, "EURINR": 106.50, "AEDINR": 24.94}

HOLDINGS = [
    # Indian mutual funds - current values from provided portfolio
    ["INDIA", "Mutual Fund", "Hybrid Core", "ICICI Prudential Balanced Advantage Fund", "", "INR", 1, 3000383, 3000383, 0.09, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Hybrid Core", "ICICI Prudential Equity & Debt Fund", "", "INR", 1, 2672559, 2672559, 0.09, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Large Cap", "ICICI Prudential Bluechip Fund", "", "INR", 1, 3050379, 3050379, 0.10, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Multi Asset", "ICICI Prudential Multi-Asset Fund", "", "INR", 1, 2102627, 2102627, 0.09, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Hybrid", "HDFC Hybrid Equity Fund", "", "INR", 1, 1518000, 1518000, 0.09, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Large Cap", "HDFC Large Cap Fund", "", "INR", 1, 1039000, 1039000, 0.10, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Mid Cap", "HDFC Mid Cap Opportunities Fund", "", "INR", 1, 552000, 552000, 0.11, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Small Cap", "HDFC Small Cap Fund", "", "INR", 1, 752481, 752481, 0.12, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC Corporate Bond Fund", "", "INR", 1, 3700000, 3700000, 0.00, 0.073, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC Short Term Debt Fund", "", "INR", 1, 3725000, 3725000, 0.00, 0.071, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC Dynamic Bond Fund", "", "INR", 1, 1000000, 1000000, 0.00, 0.072, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC PSU Banking Debt Fund", "", "INR", 1, 5200000, 5200000, 0.00, 0.073, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Flexi Cap", "HDFC Flexi Cap", "", "INR", 1, 300000, 300000, 0.10, 0.00, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Flexi Cap", "Parag Parikh Flexi Cap", "", "INR", 8774, 91.1796, 91.1796, 0.10, 0.00, "Statement units / NAV fallback"],
    ["INDIA", "Mutual Fund", "Debt", "Kotak Banking & PSU Fund", "", "INR", 1, 3500000, 3500000, 0.00, 0.073, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Debt", "Kotak Corporate Bond Fund", "", "INR", 1, 3400000, 3400000, 0.00, 0.073, "Manual NAV fallback"],
    ["INDIA", "Mutual Fund", "Debt", "Kotak Short Term Debt Fund", "", "INR", 1, 2000000, 2000000, 0.00, 0.071, "Manual NAV fallback"],

    # Indian direct equity - quantities and fallback market values from provided portfolio
    ["INDIA", "Equity", "Stock", "Reliance Industries", "RELIANCE.NS", "INR", 2220, 1360, 1360, 0.10, 0.003, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Hindustan Aeronautics", "HAL.NS", "INR", 487, 3870, 3870, 0.10, 0.006, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Larsen & Toubro", "LT.NS", "INR", 957, 3610, 3610, 0.10, 0.006, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Siemens India", "SIEMENS.NS", "INR", 241, 3120, 3120, 0.10, 0.002, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "NTPC", "NTPC.NS", "INR", 2799, 378, 378, 0.09, 0.025, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Hindustan Unilever", "HINDUNILVR.NS", "INR", 387, 2180, 2180, 0.08, 0.015, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Tata Consumer", "TATACONSUM.NS", "INR", 430, 1100, 1100, 0.09, 0.006, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Sun Pharma", "SUNPHARMA.NS", "INR", 554, 1785, 1785, 0.09, 0.007, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "ONGC", "ONGC.NS", "INR", 1065, 283, 283, 0.07, 0.04, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Mahindra & Mahindra", "M&M.NS", "INR", 239, 3120, 3120, 0.10, 0.006, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Hindustan Copper", "HINDCOPPER.NS", "INR", 925, 470, 470, 0.10, 0.003, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "LIC India", "LICI.NS", "INR", 150, 830, 830, 0.08, 0.008, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Bharti Airtel", "BHARTIARTL.NS", "INR", 823, 1825, 1825, 0.10, 0.003, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "HDFC Bank", "HDFCBANK.NS", "INR", 1601, 835, 835, 0.09, 0.011, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Infosys", "INFY.NS", "INR", 764, 1265, 1265, 0.09, 0.025, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "ICICI Bank", "ICICIBANK.NS", "INR", 2884, 1285, 1285, 0.09, 0.008, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "Federal Bank", "FEDERALBNK.NS", "INR", 660, 290, 290, 0.09, 0.006, "Yahoo Finance"],
    ["INDIA", "Equity", "Stock", "NHPC", "NHPC.NS", "INR", 3600, 84, 84, 0.08, 0.02, "Yahoo Finance"],

    # India fixed income, balances, gold, real estate, liabilities - constant unless edited
    ["INDIA", "Cash", "Bank Balance", "India Bank Balances", "", "INR", 1, 5552232.37, 5552232.37, 0.00, 0.04, "Constant"],
    ["INDIA", "Fixed Income", "Govt Bond", "Govt of India Securities", "", "INR", 1, 12001000, 12001000, 0.00, 0.072, "Constant"],
    ["INDIA", "Fixed Income", "Bank FD", "Indian Bank Fixed Deposits", "", "INR", 1, 41277000, 41277000, 0.00, 0.065, "Constant"],
    ["INDIA", "Gold", "Sovereign Gold Bond", "Sovereign Gold Bonds 2023-24 - 160 Units", "SGB", "INR", 160, 6263, 6263, 0.06, 0.025, "SGB certificate / gold proxy fallback"],
    ["INDIA", "Gold", "Physical Gold", "Physical Gold", "", "INR", 1, 3387000, 3387000, 0.06, 0.00, "Constant"],
    ["INDIA", "Real Estate", "Property", "Maimuna House Salisbury Park Pune", "", "INR", 1, 10000000, 10000000, 0.00, 0.00, "Constant"],
    ["INDIA", "Real Estate", "Property", "Tribeca 3BHK Lullanagar Pune", "", "INR", 1, 9500000, 9500000, 0.00, 0.00, "Constant"],
    ["INDIA", "Real Estate", "Property", "Office Pune Gangadham", "", "INR", 1, 10000000, 10000000, 0.00, 0.00, "Constant"],
    ["INDIA", "Liability", "Loan", "India Liabilities", "", "INR", 1, -4490440, -4490440, 0.00, 0.09, "Constant"],

    # US / global portfolio - USD values
    ["US/GLOBAL", "Fixed Income", "Corporate Bond", "Athene Global Funding 4.721% Oct-2029", "US04686E4K56", "USD", 100000, 0.98787, 0.98807, 0.00, 0.04721, "Live bond mark / ISIN"],
    ["US/GLOBAL", "Fixed Income", "US Treasury", "US Treasury 3.5% Oct-2027", "US91282CPE56", "USD", 70000, 0.99533, 0.9946995, 0.00, 0.035, "Live bond mark / ISIN"],
    ["US/GLOBAL", "Fixed Income", "US Treasury", "US Treasury 4.5% Feb-2036", "US912810FT08", "USD", 125000, 1.01470, 1.01766, 0.00, 0.045, "Live bond mark / ISIN"],
    ["US/GLOBAL", "Fixed Income", "Corporate Bond", "Exxon Mobil 4.227% Mar-2040", "US30231GBF81", "USD", 75000, 0.91500, 0.90756, 0.00, 0.04227, "Live bond mark / ISIN"],
    ["US/GLOBAL", "Equity", "Stock", "JP Morgan", "JPM", "USD", 1, 4000, 4000, 0.08, 0.022, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "Core Global", "Vanguard FTSE All-World UCITS ETF", "VWRA.L", "USD", 1, 30000, 30000, 0.08, 0.015, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "Real Estate", "BlackRock Global Property", "IDWP.L", "USD", 1, 15000, 15000, 0.06, 0.035, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "Dividend ETF", "Schwab US Dividend Equity ETF", "SCHD", "USD", 1, 20000, 20000, 0.07, 0.035, "Yahoo Finance"],
    ["US/GLOBAL", "Equity", "Tech", "Microsoft", "MSFT", "USD", 1, 10000, 10000, 0.08, 0.007, "Yahoo Finance"],
    ["US/GLOBAL", "Equity", "Tech", "NVIDIA", "NVDA", "USD", 1, 9800, 9800, 0.10, 0.001, "Yahoo Finance"],
    ["US/GLOBAL", "Equity", "Tech", "Apple", "AAPL", "USD", 1, 10200, 10200, 0.07, 0.005, "Yahoo Finance"],
    ["US/GLOBAL", "Equity", "Tech", "Meta Platforms", "META", "USD", 1, 6000, 6000, 0.08, 0.004, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "Energy", "Energy ETF", "XLE", "USD", 1, 10000, 10000, 0.06, 0.03, "Yahoo Finance"],
    ["US/GLOBAL", "Equity", "Healthcare", "UnitedHealth Group", "UNH", "USD", 1, 5600, 5600, 0.07, 0.017, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "Nuclear", "Nuclear ETF", "NLR", "USD", 1, 8000, 8000, 0.07, 0.015, "Yahoo Finance"],
    ["US/GLOBAL", "Equity", "Retail", "Amazon", "AMZN", "USD", 1, 5100, 5100, 0.08, 0.00, "Yahoo Finance"],
    ["US/GLOBAL", "Equity", "Financial", "Visa", "V", "USD", 1, 5003, 5003, 0.07, 0.008, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "Aerospace & Defence", "VanEck Defense UCITS ETF", "DFND.L", "USD", 1, 14000, 14000, 0.07, 0.01, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "Small Caps", "Russell 2000 ETF", "IWM", "USD", 1, 5000, 5000, 0.07, 0.013, "Yahoo Finance"],
    ["US/GLOBAL", "ETF", "High Yield Debt", "Xtrackers USD High Yield Corporate Bond", "XUHY.L", "USD", 1, 10000, 10000, 0.00, 0.065, "Yahoo Finance"],
    ["US/GLOBAL", "Mixed Asset", "SIP", "Mixed Asset SIP", "", "USD", 1, 31000, 31000, 0.04, 0.03, "Constant"],
    ["US/GLOBAL", "Cash", "Bank FD", "ADCB Bank FD", "", "USD", 1, 21798.37, 21798.37, 0.00, 0.04, "Constant"],
    ["US/GLOBAL", "Cash", "Bank Balance", "ADCB Bank Balance", "", "USD", 1, 9536, 9536, 0.00, 0.00, "Constant"],
    ["US/GLOBAL", "Cash", "UAE Banks", "UAE Banks", "", "USD", 1, 27330.82, 27330.82, 0.00, 0.01, "Constant"],
    ["US/GLOBAL", "Fixed Income", "Sovereign Bond", "Oman 6.5% 2047", "", "USD", 25000, 1.0, 1.0, 0.00, 0.065, "Fallback + bond manual"],
    ["US/GLOBAL", "Fixed Income", "Corporate Bond", "GASCBM 6.51% 2042", "", "USD", 25000, 1.0, 1.0, 0.00, 0.0651, "Fallback + bond manual"],
    ["US/GLOBAL", "Liability", "Leverage", "Portfolio Leverage", "", "USD", 1, -28450, -28450, 0.00, 0.00, "Constant"],

    # UAE property in INR equivalent from provided data
    ["US/GLOBAL", "Real Estate", "Property", "UAE House Downtown Regalia 1.5BHK", "", "INR", 1, 30300000, 30300000, 0.00, 0.00, "Constant"],
]

COLUMNS = [
    "portfolio", "asset_class", "sub_class", "name", "ticker", "currency",
    "quantity", "invested_rate", "fallback_current_rate", "expected_return_pct",
    "yield_dividend_pct", "data_source"
]
