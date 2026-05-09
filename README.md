# Harsh Global Portfolio - Family Office

Final accounting fix package.

## Main file path
`app.py`

## Password secret
```toml
APP_PASSWORD = "Harsh@1985"
```

## Key fixes
- Mutual fund invested/gross totals match the submitted structure: ICICI ₹10,825,948, HDFC ₹17,486,481, Parag ₹800,000, Kotak ₹8,900,000.
- Mutual fund current values are live: AMFI NAV × exact units.
- Sovereign Gold Bond: 160 units, cost ₹10,02,080, 2.5% coupon; live gold proxy for current value.
- US bonds use broker marks from your screenshot and ISINs.
- US/global real estate remains fixed INR but shows USD equivalent using live USDINR.
- No FX or MTM toggle. Live valuation is automatic where identifiers exist.

## Deploy
Upload all files to GitHub root and deploy on Streamlit Cloud with main file path `app.py`.
