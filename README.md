# Harsh Global Portfolio - Family Office

Corrected accounting package:
- Cost basis separated from live current value
- USD/INR fixed at approved 94.44
- No FX toggle / no MTM toggle
- Indian equity cost basis from sheet, live current value from Yahoo
- US securities quantities from IBKR screenshot
- US bonds use supplied broker marks
- UAE real estate fixed INR, USD equivalent displayed
- SGB uses base ₹24L cost basis and live gold proxy as current
- FDs 6.5%, Govt bonds 7.2%, UAE banks 1%

Main file path: app.py
Password secret: APP_PASSWORD = "Harsh@1985"


V2 fixes:
- US bond broker marks scaled correctly: 98.807 = 0.98807 in valuation.
- MF invested total aligned to submitted structure: ₹38,012,429.
- HDFC Flexi ₹300k excluded from base total because submitted HDFC total excludes it.
- USD/INR remains approved at ₹94.44, so USD asset INR value moves versus the older screenshot.

V3 fixes:
- Returns & Yield page shows total row and summary metrics.
- US Portfolio has Mixed Asset tab for SIP.
- ICICI/HDFC/Kotak/Parag mutual funds use AMFI live NAV through MF: tickers.
- Net Worth Growth chart/table shows ₹ symbols.
