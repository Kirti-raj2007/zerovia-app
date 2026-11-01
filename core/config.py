"""
Configuration and constants for Zerovia Carbon Ledger.
Supports Multi-Tenant Company Isolation, 1 Unit = 1 Ton Tokenomics, and 400 PPM Baseline.
"""

APP_NAME = "Zerovia"
APP_SUBTITLE = "Decentralized IoT Air Quality & Automated Multi-Tenant Carbon Tokenomics"
APP_VERSION = "v3.0.0-MultiTenant-zkEVM"
CHAIN_NAME = "Zerovia Eco-Chain (zkEVM L2)"
SMART_CONTRACT_ADDRESS = "0x8F3a92C48eB2d07A574189280d9A42C128d549B1"
ORACLE_ADDRESS = "0x3Eb5730248a8A90BcC4A24754B4BfcF3C1299971"

# Air Quality Thresholds (PPM)
# Safe baseline is set to 400 PPM.
# <= 400 PPM: Rewards clean air micro-credits.
# > 400 PPM: Triggers automated credit burn penalty.
DEFAULT_SAFE_PPM = 400.0

# Carbon Unit Tokenomics: 1 Carbon Unit precisely equals 1 Ton of CO2 emission/offset
CARBON_UNIT_TO_TONS = 1.0            # 1 Z Credit = 1 Metric Ton CO2 equivalent (tCO2e)
DEFAULT_TOKEN_SYMBOL = "ZC"
TOKEN_NAME = "Z Credit"
TOKEN_UNIT_DESCRIPTION = "1 Z Credit (ZC) = 1 Metric Ton CO2e"

# Rewards & Penalties (in Z Credits / Tons of CO2e)
CLEAN_AIR_REWARD_RATE = 0.25          # Z Credit units (+0.25 Tons CO2) rewarded per clean cycle (<= 400 PPM)
PENALTY_BURN_RATE = 0.50             # Z Credit units (-0.50 Tons CO2) burned per penalty cycle (> 400 PPM)
OFFSET_PURCHASE_UNIT = 100.0         # 100.0 Z Credits (+100.0 Tons CO2 offset)
OFFSET_UNIT_PRICE_USD = 18.50        # USD price per Z Credit (per Ton CO2)

# Multi-Tenant Pre-configured Demo Companies
# Clean initial state: zero pre-listed companies. The registry is empty until dynamic onboarding.
DEFAULT_TENANTS = []

# Roles & Access Authentication
ROLE_ISSUER = "Issuer / Director (Admin)"
ROLE_COMPANY = "Customer / Enterprise Tenant"
DEFAULT_ADMIN_KEY = "ADMIN2026"

# UI Refresh and Stream settings
DEFAULT_REFRESH_INTERVAL_SEC = 2.0
MAX_HISTORY_POINTS = 50
MAX_TRANSACTION_LOGS = 150
