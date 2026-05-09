from __future__ import annotations

DEFAULT_FX = {"USDINR": 91.58, "EURINR": 106.50, "AEDINR": 24.94}

# NOTE:
# Mutual funds are now unit-based. Ticker field uses MF:<scheme search text> so market_data.py fetches AMFI latest NAV.
# SGB uses ticker SGB so market_data.py fetches live gold INR/gram proxy. One SGB unit = 1 gram gold.
# US bonds use ISINs and broker marks from market_data.py.

HOLDINGS = [
    # ICICI mutual funds from ICICI statement as on 05-May-2026
    ["INDIA", "Mutual Fund", "Large Cap", "ICICI Prudential Large Cap Fund Direct Plan Growth", "MF:ICICI Prudential Large Cap Fund Direct Plan Growth", "INR", 26211.494, 3050379.98/26211.494, 118.34, 0.10, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Hybrid Core", "ICICI Prudential Balanced Advantage Fund Direct Plan Growth", "MF:ICICI Prudential Balanced Advantage Fund Direct Plan Growth", "INR", 35789.746, 3000385.93/35789.746, 85.12, 0.09, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Hybrid Core", "ICICI Prudential Equity & Debt Fund Direct Plan Growth", "MF:ICICI Prudential Equity and Debt Fund Direct Plan Growth", "INR", 6028.756, 2672559.97/6028.756, 447.08, 0.09, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Multi Asset", "ICICI Prudential Multi-Asset Fund Direct Plan Growth", "MF:ICICI Prudential Multi Asset Fund Direct Plan Growth", "INR", 2376.605, 2102627.07/2376.605, 887.1161, 0.09, 0.00, "Live AMFI NAV"],

    # HDFC mutual funds aggregated from HDFC statements
    ["INDIA", "Mutual Fund", "Hybrid", "HDFC Hybrid Equity Fund Direct Growth", "MF:HDFC Hybrid Equity Fund Direct Plan Growth Option", "INR", 12352.052, 1513982.12/12352.052, 121.828, 0.09, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Large Cap", "HDFC Large Cap Fund Direct Growth", "MF:HDFC Large Cap Fund Direct Plan Growth Option", "INR", 876.803, 1038629.79/876.803, 1192.367, 0.10, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Flexi Cap", "HDFC Flexi Cap Fund Direct Growth", "MF:HDFC Flexi Cap Fund Direct Plan Growth Option", "INR", 135.716, 300000/135.716, 2149.495, 0.10, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Mid Cap", "HDFC Mid Cap Fund Direct Growth", "MF:HDFC Mid Cap Fund Direct Plan Growth Option", "INR", 2565.635, 558213.43/2565.635, 218.531, 0.11, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Small Cap", "HDFC Small Cap Fund Direct Growth", "MF:HDFC Small Cap Fund Direct Growth Plan", "INR", 5029.742, 752481.21/5029.742, 152.253, 0.12, 0.00, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC Short Term Debt Fund Direct Growth", "MF:HDFC Short Term Debt Fund Direct Plan Growth Option", "INR", 107886.965, 3725000/107886.965, 34.5572, 0.00, 0.071, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC Banking & PSU Debt Fund Direct Growth", "MF:HDFC Banking and PSU Debt Fund Direct Growth Option", "INR", 210127.463, 5221507.30/210127.463, 24.8676, 0.00, 0.073, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC Corporate Bond Fund Direct Growth", "MF:HDFC Corporate Bond Fund Direct Plan Growth Option", "INR", 107521.148, 3697261.17/107521.148, 34.3754, 0.00, 0.073, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Debt", "HDFC Dynamic Debt Fund Direct Growth", "MF:HDFC Dynamic Debt Fund Direct Growth Option", "INR", 9959.615, 1000000/9959.615, 100.7292, 0.00, 0.072, "Live AMFI NAV"],

    # Parag Parikh - units supplied by user; fallback value preserves earlier ₹8L until live AMFI NAV fetched
    ["INDIA", "Mutual Fund", "Flexi Cap", "Parag Parikh Flexi Cap Fund Direct Growth", "MF:Parag Parikh Flexi Cap Fund Direct Growth", "INR", 8774, 800000/8774, 800000/8774, 0.10, 0.00, "Live AMFI NAV"],

    # Kotak mutual funds aggregated from Kotak statements
    ["INDIA", "Mutual Fund", "Debt", "Kotak Banking & PSU Debt Fund Direct Growth", "MF:Kotak Banking and PSU Debt Fund Direct Growth", "INR", 49361.988, 3500000/49361.988, 71.0540, 0.00, 0.073, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Debt", "Kotak Corporate Bond Fund Direct Growth", "MF:Kotak Corporate Bond Fund Direct Growth", "INR", 830.408, 3400430.99/830.408, 4104.4029, 0.00, 0.073, "Live AMFI NAV"],
    ["INDIA", "Mutual Fund", "Debt", "Kotak Bond Short Term Direct Growth", "MF:Kotak Bond Fund Short Term Direct Plan Growth", "INR", 33350.635, 1996200.44/33350.635, 59.8961, 0.00, 0.071, "Live AMFI NAV"],

    # Indian direct equity
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

    # India fixed income, balances, gold, real estate, liabilities
    ["INDIA", "Cash", "Bank Balance", "India Bank Balances", "", "INR", 1, 5552232.37, 5552232.37, 0.00, 0.04, "Constant"],
    ["INDIA", "Fixed Income", "Govt Bond", "Govt of India Securities", "", "INR", 1, 12001000, 12001000, 0.00, 0.072, "Constant"],
    ["INDIA", "Fixed Income", "Bank FD", "Indian Bank Fixed Deposits", "", "INR", 1, 41277000, 41277000, 0.00, 0.065, "Constant"],
    ["INDIA", "Gold", "Sovereign Gold Bond", "Sovereign Gold Bonds - 160 Units", "SGB", "INR", 160, 1002080/160, 1002080/160, 0.00, 0.025, "Live SGB gold proxy"],
    ["INDIA", "Gold", "Physical Gold", "Physical Gold", "", "INR", 1, 3387000, 3387000, 0.06, 0.00, "Constant"],
    ["INDIA", "Real Estate", "Property", "Maimuna House Salisbury Park Pune", "", "INR", 1, 10000000, 10000000, 0.00, 0.00, "Constant"],
    ["INDIA", "Real Estate", "Property", "Tribeca 3BHK Lullanagar Pune", "", "INR", 1, 9500000, 9500000, 0.00, 0.00, "Constant"],
    ["INDIA", "Real Estate", "Property", "Office Pune Gangadham", "", "INR", 1, 10000000, 10000000, 0.00, 0.00, "Constant"],
    ["INDIA", "Liability", "Loan", "India Liabilities", "", "INR", 1, -4490440, -4490440, 0.00, 0.09, "Constant"],

    # US / global portfolio - bonds now use ISIN and broker marks
    ["US/GLOBAL", "Fixed Income", "US Treasury", "US Treasury 3.5% Oct 2027", "US91282CPE56", "USD", 70000, 99.39/100, 99.470/100, 0.00, 0.035, "Broker bond mark"],
    ["US/GLOBAL", "Fixed Income", "Corporate Bond", "Athene 4.721% Oct 2029", "US04686E4K56", "USD", 100000, 98.79/100, 98.807/100, 0.00, 0.04721, "Broker bond mark"],
    ["US/GLOBAL", "Fixed Income", "US Treasury", "US Treasury 4.5% Feb 2036", "US912810FT08", "USD", 125000, 101.47/100, 101.766/100, 0.00, 0.045, "Broker bond mark"],
    ["US/GLOBAL", "Fixed Income", "Corporate Bond", "Exxon Mobil 4.227% Mar 2040", "US30231GBF81", "USD", 75000, 91.50/100, 90.756/100, 0.00, 0.04227, "Broker bond mark"],

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
    ["US/GLOBAL", "Cash", "Bank Balance", "ADCB Bank Balance", "", "USD", 1, 9536, 9536, 0.00, 0.01, "Constant"],
    ["US/GLOBAL", "Cash", "UAE Banks", "UAE Banks", "", "USD", 1, 27330.82, 27330.82, 0.00, 0.01, "Constant"],
    ["US/GLOBAL", "Fixed Income", "Sovereign Bond", "Oman 6.5% 2047", "", "USD", 25000, 1.0, 1.0, 0.00, 0.065, "Constant/manual"],
    ["US/GLOBAL", "Fixed Income", "Corporate Bond", "GASCBM 6.51% 2042", "", "USD", 25000, 1.0, 1.0, 0.00, 0.0651, "Constant/manual"],
    ["US/GLOBAL", "Liability", "Leverage", "Portfolio Leverage", "", "USD", 1, -28450, -28450, 0.00, 0.00, "Constant"],
    ["US/GLOBAL", "Real Estate", "Property", "UAE House Downtown Regalia 1.5BHK", "", "INR", 1, 30300000, 30300000, 0.00, 0.00, "Constant"],
]

COLUMNS = [
    "portfolio", "asset_class", "sub_class", "name", "ticker", "currency",
    "quantity", "invested_rate", "fallback_current_rate", "expected_return_pct",
    "yield_dividend_pct", "data_source"
]

SEED_VERSION = "2026-05-09-live-mf-sgb-bonds-v1"
