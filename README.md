# Harsh Global Portfolio - Family Office

Clean Streamlit family-office dashboard.

## Deploy
Main file path: `app.py`

Password secret:
```toml
APP_PASSWORD = "Harsh@1985"
```

## What is live / marked
- Indian listed shares: live via Yahoo/NSE symbols.
- Identified US bonds: marked from the ISIN bond-price table provided by the user.
- Mutual funds: statement units and NAV fallback; AMFI integration can be added with exact AMFI scheme codes.
- FDs, bank balances, real estate, physical gold, Oman and GASCBM: constant/fixed-yield unless edited.

## Fixed yield assumptions
- Indian FDs: 6.5%
- Govt of India securities: 7.2%
- UAE banks: 1.0%

## Do not upload
- `.pyc`
- `__pycache__`
