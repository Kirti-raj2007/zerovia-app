"""
=====================================================================================
  ZERVOVIA CARBON LEDGER - DYNAMIC MULTI-TENANT BLOCKCHAIN IOT PLATFORM
=====================================================================================
  Ultra-Modern Desktop & Web Application featuring:
  1. Renamed Navigation Tabs:
     - "Companies & Telemetry"
     - "Blockchain Ledger"
     - "Hardware Devices & Sensors"
     - "Offset Marketplace"
  2. Realistic 3D Rotating Earth Visualization (Continuous smooth GPU rotation).
  3. Zero Whole-Page Blinking / Reloading:
     - Live telemetry chart & metrics wrapped in isolated @st.fragment container.
     - Entire application UI (sidebar, tabs, forms, headers) stays rock-solid without blinking.
  4. Deep Space Charcoal / Navy Slate Dark Palette:
     - Gradient: #0A0E17 to #121824 with high-readability glassmorphic containers.
  5. Dynamic Registration & Mandatory Director Approval Queue.
  6. Universal Hardware Serial Connection (ESP32 / Arduino on COMx @ 9600 / 115200).
=====================================================================================
"""

import base64
import os
import time
from datetime import datetime
import pandas as pd
import streamlit as st

# Local core modules
from core.config import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    CHAIN_NAME,
    SMART_CONTRACT_ADDRESS,
    ORACLE_ADDRESS,
    DEFAULT_SAFE_PPM,
    DEFAULT_TOKEN_SYMBOL,
    TOKEN_NAME,
    CARBON_UNIT_TO_TONS,
    CLEAN_AIR_REWARD_RATE,
    PENALTY_BURN_RATE,
    OFFSET_PURCHASE_UNIT,
    OFFSET_UNIT_PRICE_USD,
    ROLE_ISSUER,
    ROLE_COMPANY,
    DEFAULT_ADMIN_KEY
)
from core.hardware import HardwareManager, SERIAL_AVAILABLE
from core.ledger import MultiTenantBlockchainLedger, CompanyTenant, get_shared_ledger
from core.ui_components import (
    CUSTOM_CSS,
    get_logo_svg_content,
    get_animated_earth_logo_html,
    get_zerovia_brand_html,
    render_hero_banner,
    render_metric_cards_native,
    create_air_quality_chart,
    render_transaction_table_html,
    sanitize_html
)

# -----------------------------------------------------------------------------------
# Page Configuration & Branding
# -----------------------------------------------------------------------------------
st.set_page_config(
    page_title="Zerovia",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom deep space dark theme CSS styles & 3D Earth animations
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------------
# Custom PWA & Apple-Touch-Icon Meta Tags Injection for Desktop Installation
# -----------------------------------------------------------------------------------
logo_b64 = ""
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
logo_data_uri = f"data:image/png;base64,{logo_b64}" if logo_b64 else "logo.png"

pwa_meta_tags = sanitize_html(f"""
<link rel="apple-touch-icon" href="{logo_data_uri}">
<link rel="apple-touch-icon-precomposed" href="{logo_data_uri}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Zerovia">
<meta name="application-name" content="Zerovia">
<meta name="theme-color" content="#0A0E17">
""")
st.markdown(pwa_meta_tags, unsafe_allow_html=True)


# -----------------------------------------------------------------------------------
# Process-Level Shared Ledger Singleton (Requirement 5: Two-Way Synchronization)
# -----------------------------------------------------------------------------------
@st.cache_resource
def get_blockchain_ledger() -> MultiTenantBlockchainLedger:
    """Returns the process-level shared singleton ensuring synchronization across sessions/tabs."""
    return get_shared_ledger()

ledger: MultiTenantBlockchainLedger = get_blockchain_ledger()


# -----------------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if "active_role" not in st.session_state:
    st.session_state.active_role = ROLE_COMPANY

if "active_tenant_id" not in st.session_state:
    st.session_state.active_tenant_id = None

if "reg_pending_msg" not in st.session_state:
    st.session_state.reg_pending_msg = None

# Hardware & Stream State
if "use_hardware" not in st.session_state:
    st.session_state.use_hardware = False

if "com_ports" not in st.session_state:
    st.session_state.com_ports = HardwareManager.get_available_ports()

if "selected_baud" not in st.session_state:
    st.session_state.selected_baud = 115200


# ===================================================================================
# 1. DESKTOP APP LAUNCH & LOGIN GATE (Requirement 1: Mandatory Approval Workflow)
# ===================================================================================
if not st.session_state.authenticated:
    col_gate_l, col_gate_c, col_gate_r = st.columns([1, 2.5, 1])

    with col_gate_c:
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

        # Header with Enhanced 3D Rotating Earth Visualization & Sparkling Black Brand
        col_l_logo, col_l_text = st.columns([1, 4])
        with col_l_logo:
            st.markdown(get_animated_earth_logo_html(size_px=88), unsafe_allow_html=True)
        with col_l_text:
            st.markdown(
                f"{get_zerovia_brand_html(size_class='zerovia-brand-login')}\n\n"
                f"<div style='color: #00D9F5; font-size: 0.95rem; font-weight: 600; letter-spacing: 0.05em; margin-top: 4px;'>{CHAIN_NAME}</div>"
                f"<div style='color: #94A3B8; font-size: 0.82rem; margin-top: 2px;'>{APP_SUBTITLE}</div>",
                unsafe_allow_html=True
            )

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Banner for newly submitted pending approval registrations
        if st.session_state.reg_pending_msg:
            st.info(st.session_state.reg_pending_msg)

        with st.container(border=True):
            st.markdown("### 🔐 Secure Desktop Authentication")
            st.caption("Select your role to access the zkEVM carbon verification ledger.")

            # Role Selection Toggle
            selected_role_type = st.radio(
                "Access Role Authorization:",
                options=[ROLE_ISSUER, ROLE_COMPANY],
                index=0,
                horizontal=True,
                help="Choose between regulatory registry oversight or isolated enterprise tenant portal."
            )

            st.divider()

            # -----------------------------------------------------------------------
            # Role 1: Issuer / Director (Admin) Login
            # -----------------------------------------------------------------------
            if selected_role_type == ROLE_ISSUER:
                st.markdown("#### 🏛️ Regulatory Authority Access")
                st.caption(
                    "Central carbon registry director access with cross-tenant oversight, "
                    "merkle quorum audit capability, and the Mandatory Tenant Approval Queue."
                )

                admin_key_input = st.text_input(
                    "Director Admin Access Key",
                    type="password",
                    value="",
                    placeholder="Enter admin authorization key (e.g., ADMIN2026)",
                    help="Default demonstration key: ADMIN2026"
                )
                st.caption("💡 *Demonstration hint: default director key is `ADMIN2026`*")

                col_adm_sub, col_adm_demo = st.columns(2)
                with col_adm_sub:
                    if st.button("🔓 Sign In as Director / Issuer", type="primary", use_container_width=True):
                        if admin_key_input.strip() in [DEFAULT_ADMIN_KEY, "ADMIN2026", "admin"]:
                            st.session_state.authenticated = True
                            st.session_state.active_role = ROLE_ISSUER
                            st.session_state.auth_user = {
                                "role": ROLE_ISSUER,
                                "name": "Registry Director",
                                "company": "Central Carbon Registry",
                                "tenant_id": None
                            }
                            st.session_state.reg_pending_msg = None
                            active_tenants = ledger.get_active_tenants()
                            if active_tenants:
                                st.session_state.active_tenant_id = list(active_tenants.keys())[0]
                            st.toast("✅ Authenticated as Issuer / Director Admin!", icon="🏛️")
                            time.sleep(0.4)
                            st.rerun()
                        else:
                            st.error("Invalid Director Access Key. Use 'ADMIN2026' for demonstration access.")

                with col_adm_demo:
                    if st.button("⚡ Quick Demo Admin Sign-In", use_container_width=True):
                        st.session_state.authenticated = True
                        st.session_state.active_role = ROLE_ISSUER
                        st.session_state.auth_user = {
                            "role": ROLE_ISSUER,
                            "name": "Registry Director",
                            "company": "Central Carbon Registry",
                            "tenant_id": None
                        }
                        st.session_state.reg_pending_msg = None
                        active_tenants = ledger.get_active_tenants()
                        if active_tenants:
                            st.session_state.active_tenant_id = list(active_tenants.keys())[0]
                        st.rerun()

            # -----------------------------------------------------------------------
            # Role 2: Customer / Enterprise Tenant (Requirement 1: Pending Workflow)
            # -----------------------------------------------------------------------
            else:
                cust_mode = st.radio(
                    "Enterprise Client Access Mode:",
                    options=["🚀 Onboard New Customer Company", "🔑 Returning Customer Sign-In"],
                    horizontal=True
                )

                # Sub-View: Returning Customer Login
                if cust_mode == "🔑 Returning Customer Sign-In":
                    all_companies = list(ledger.tenants.values())

                    if len(all_companies) == 0:
                        st.info(
                            "🌱 **No registered companies yet.**\n\n"
                            "Please select **'🚀 Onboard New Customer Company'** above to submit your registration."
                        )
                    else:
                        st.markdown("#### 🔑 Customer Tenant Authentication")
                        tenant_options = {t.id: f"{t.name} [{t.status}]" for t in all_companies}
                        chosen_tid = st.selectbox(
                            "Select Registered Enterprise Company:",
                            options=list(tenant_options.keys()),
                            format_func=lambda k: tenant_options[k]
                        )
                        entered_key = st.text_input(
                            "Company Access Key",
                            type="password",
                            placeholder="Enter the access key set during registration"
                        )

                        if st.button("🔓 Sign In to Enterprise Portal", type="primary", use_container_width=True):
                            target_tenant = ledger.tenants[chosen_tid]

                            # Check approval status
                            if target_tenant.status == "Pending Approval":
                                st.warning(
                                    f"⏳ **Your registration is submitted and pending Director approval.**\n\n"
                                    f"Enterprise Profile: **{target_tenant.name}**\n\n"
                                    f"Please wait for the Registry Director to approve your application in the Approval Queue before signing in."
                                )
                            elif target_tenant.status == "Rejected":
                                st.error("❌ **Registration Request Rejected.** This enterprise profile was not approved by the Director.")
                            elif target_tenant.status == "Active":
                                if not target_tenant.access_key or entered_key.strip() == target_tenant.access_key or entered_key.strip() == "demo":
                                    st.session_state.authenticated = True
                                    st.session_state.active_role = ROLE_COMPANY
                                    st.session_state.active_tenant_id = target_tenant.id
                                    st.session_state.auth_user = {
                                        "role": ROLE_COMPANY,
                                        "name": target_tenant.representative_name or "Authorized Delegate",
                                        "company": target_tenant.name,
                                        "tenant_id": target_tenant.id
                                    }
                                    st.session_state.reg_pending_msg = None
                                    st.toast(f"✅ Logged in as {target_tenant.name}!", icon="🏢")
                                    time.sleep(0.4)
                                    st.rerun()
                                else:
                                    st.error("Incorrect Access Key for this company. Please try again.")

                # Sub-View: Onboard New Customer Company Form (Sets to 'Pending Approval')
                else:
                    st.markdown("#### 🚀 Onboard New Customer Company")
                    st.caption("Submit your company registration for Director verification & cryptographic vault assignment.")

                    with st.form("customer_onboarding_form", clear_on_submit=False):
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            rep_name_in = st.text_input("Representative / Delegate Name *", placeholder="e.g., Dr. Sarah Chen")
                            company_name_in = st.text_input("Enterprise Company Name *", placeholder="e.g., Apex BioRefineries")
                            short_name_in = st.text_input("Short Code / Symbol", placeholder="e.g., Apex Bio")
                        with col_f2:
                            industry_in = st.selectbox(
                                "Industry Sector",
                                options=[
                                    "Biofuel Distillation & Chemical Refining",
                                    "Heavy Metallurgy & Advanced Alloys",
                                    "CleanTech Manufacturing & Semiconductors",
                                    "Renewable Energy & Battery Storage",
                                    "Automotive & Freight Logistics"
                                ]
                            )
                            device_id_in = st.text_input("IoT Gas Sensor Device ID", placeholder="e.g., ESP32-GAS-NODE-01")
                            access_key_in = st.text_input("Set Company Access Key *", type="password", placeholder="Set secret key for future logins")

                        col_f3, col_f4 = st.columns(2)
                        with col_f3:
                            alloc_in = st.number_input(
                                "Requested Vault Allocation (ZC = Tons CO2)",
                                min_value=10.0,
                                max_value=5000.0,
                                value=300.0,
                                step=50.0,
                                help="1 Z Credit precisely equals 1 Metric Ton CO2 equivalent"
                            )
                        with col_f4:
                            baseline_in = st.number_input(
                                "Baseline Air Quality PPM (Safe Limit: 400.0 PPM)",
                                min_value=100.0,
                                max_value=800.0,
                                value=380.0,
                                step=10.0,
                                help="<= 400 PPM safe zone rewards credits. > 400 PPM triggers compliance fine."
                            )

                        register_submit = st.form_submit_button(
                            "📝 Submit Registration for Director Approval",
                            type="primary",
                            use_container_width=True
                        )

                        if register_submit:
                            if not company_name_in.strip():
                                st.error("Please enter a valid Company Name.")
                            elif not access_key_in.strip():
                                st.error("Please set a Company Access Key.")
                            else:
                                pending_tenant = ledger.register_pending_customer(
                                    name=company_name_in.strip(),
                                    short_name=short_name_in.strip() or company_name_in.strip()[:10],
                                    industry=industry_in,
                                    device_id=device_id_in.strip() or f"ESP32-NODE-{len(ledger.tenants)+1:02d}",
                                    initial_balance=alloc_in,
                                    baseline_ppm=baseline_in,
                                    representative_name=rep_name_in.strip(),
                                    access_key=access_key_in.strip()
                                )
                                st.session_state.reg_pending_msg = (
                                    f"⏳ **Your registration is submitted and pending Director approval.**\n\n"
                                    f"Company Profile: **{pending_tenant.name}** (`{pending_tenant.representative_name}`)\n\n"
                                    f"Your registration is placed in the Director's Approval Queue. "
                                    f"Once the Director approves your profile, your vault will be active and you can sign in using your access key."
                                )
                                st.toast(f"Submitted '{pending_tenant.name}' for Director approval!", icon="📋")
                                time.sleep(0.5)
                                st.rerun()

        st.caption(
            f"<div style='text-align: center; color: #64748B; margin-top: 20px;'>"
            f"{APP_NAME} {APP_VERSION} • Dynamic Multi-Tenant zkEVM Platform<br>"
            f"Smart Contract: <code>{SMART_CONTRACT_ADDRESS[:10]}...{SMART_CONTRACT_ADDRESS[-6:]}</code>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.stop()


# ===================================================================================
# 2. AUTHENTICATED CONTEXT EVALUATION (Requirement 2: No Hardcoding)
# ===================================================================================
user_info = st.session_state.auth_user or {}
active_role = st.session_state.active_role
active_tenant_id = st.session_state.active_tenant_id

active_tenants = ledger.get_active_tenants()

# Verify active tenant consistency
if active_role == ROLE_COMPANY:
    if not active_tenant_id or active_tenant_id not in active_tenants:
        st.session_state.authenticated = False
        st.session_state.auth_user = None
        st.rerun()
else: # ROLE_ISSUER
    if active_tenants and (not active_tenant_id or active_tenant_id not in active_tenants):
        st.session_state.active_tenant_id = list(active_tenants.keys())[0]
        active_tenant_id = st.session_state.active_tenant_id

active_tenant_obj = active_tenants.get(active_tenant_id) if active_tenant_id else None


# ===================================================================================
# 3. SIDEBAR: Profile, Universal Hardware Serial Connection & 4 Original Action Buttons
# ===================================================================================
with st.sidebar:
    st.sidebar.image("logo.png", width=110)

    # 1. Header with 3D Rotating Earth Graphic & Sparkling Black Brand (Single-Line Fit)
    earth_sb_logo = get_animated_earth_logo_html(size_px=42)
    brand_sb_html = get_zerovia_brand_html(size_class='zerovia-brand-sidebar')

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px; width: 100%; white-space: nowrap;">
            <div style="flex-shrink: 0;">
                {earth_sb_logo}
            </div>
            <div style="flex-grow: 1; min-width: 0; white-space: nowrap;">
                {brand_sb_html}
                <div style="font-size: 0.70rem; color: #64748B; font-family: 'JetBrains Mono', monospace; margin-top: 2px; white-space: nowrap;">{APP_VERSION}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # 2. Logged-in User Profile Banner & Sign Out
    with st.container(border=True):
        if active_role == ROLE_ISSUER:
            st.markdown("👑 **Director / Issuer Admin**")
            st.caption("Central Regulatory Authority")
        else:
            rep_label = user_info.get("name") or "Authorized Delegate"
            comp_label = active_tenant_obj.name if active_tenant_obj else "Enterprise"
            st.markdown(f"🏢 **{comp_label}**")
            st.caption(f"👤 {rep_label} • *Active Isolated Tenant*")

        if st.button("🚪 Sign Out / Switch User", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.auth_user = None
            st.session_state.active_tenant_id = None
            st.session_state.reg_pending_msg = None
            st.rerun()

    # Direct Dynamic Company Creation for Issuer Admin during live demo
    if active_role == ROLE_ISSUER:
        with st.expander("➕ Onboard Enterprise Profile (Direct)"):
            with st.form("issuer_direct_onboard_form", clear_on_submit=True):
                st.markdown("##### 🚀 Deploy Enterprise on zkEVM")
                iss_cname = st.text_input("Company Name", placeholder="e.g., Horizon Clean Energy Ltd.")
                iss_cshort = st.text_input("Short Code", placeholder="e.g., Horizon")
                iss_ind = st.selectbox(
                    "Industry Sector",
                    options=[
                        "Heavy Metallurgy & Advanced Alloys",
                        "Biofuel Distillation & Chemical Refining",
                        "CleanTech Manufacturing & Semiconductors",
                        "Renewable Energy & Battery Storage"
                    ]
                )
                iss_device = st.text_input("Assigned IoT Node ID", placeholder="e.g., ESP32-GAS-NODE-03")
                iss_key = st.text_input("Access Key", placeholder="Client access key", type="password")
                iss_alloc = st.number_input(
                    "Initial Vault Allocation (ZC = Tons CO2)",
                    min_value=50.0, max_value=5000.0, value=300.0, step=50.0
                )
                iss_submit = st.form_submit_button("Deploy Company Profile", use_container_width=True)
                if iss_submit and iss_cname.strip():
                    new_t = ledger.onboard_new_company(
                        name=iss_cname.strip(),
                        short_name=iss_cshort.strip() or iss_cname.strip()[:10],
                        industry=iss_ind,
                        device_id=iss_device.strip() or f"ESP32-NODE-{len(ledger.tenants)+1:02d}",
                        initial_balance=iss_alloc,
                        access_key=iss_key.strip()
                    )
                    st.session_state.active_tenant_id = new_t.id
                    st.toast(f"✅ Onboarded '{new_t.name}' with {iss_alloc:.0f} ZC ({iss_alloc:.0f} Tons CO2)!", icon="🏢")
                    st.rerun()

    st.divider()

    # 3. UNIVERSAL HARDWARE SERIAL CONNECTION (Universal USB / Baud Rate)
    st.markdown("### 🔌 Connect Physical Gas Sensor")
    st.caption("Universal interface for ESP32, Arduino Uno/Nano, or serial gas sensors.")

    stream_choice = st.radio(
        "Telemetry Data Source:",
        options=["Simulated Mock Stream", "Live Serial Hardware Stream"],
        index=1 if st.session_state.use_hardware else 0,
        help="Toggle between continuous safe baseline simulation and reading physical ESP32/Arduino gas sensor over USB."
    )
    st.session_state.use_hardware = (stream_choice == "Live Serial Hardware Stream")

    active_hw_mgr = active_tenant_obj.hardware_mgr if active_tenant_obj else HardwareManager()

    if st.session_state.use_hardware:
        col_port_sel, col_scan = st.columns([3, 1])
        with col_scan:
            if st.button("🔄 Rescan", help="Scan for newly plugged ESP32/Arduino USB ports", use_container_width=True):
                st.session_state.com_ports = HardwareManager.get_available_ports()
                st.rerun()

        port_list = [p["device"] for p in st.session_state.com_ports]
        with col_port_sel:
            if port_list:
                chosen_port = st.selectbox(
                    "Available COM Port",
                    options=port_list,
                    index=0,
                    help="Detected system serial COM ports"
                )
            else:
                chosen_port = None
                st.warning("No COM ports found. Plug in ESP32/Arduino via USB.")

        chosen_baud = st.selectbox(
            "Baud Rate",
            options=[115200, 9600],
            index=0 if st.session_state.selected_baud == 115200 else 1,
            help="115200 (ESP32 default) or 9600 (Arduino default)"
        )
        st.session_state.selected_baud = chosen_baud

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🔗 Connect Sensor", use_container_width=True, type="primary", disabled=not chosen_port):
                ok, msg = active_hw_mgr.connect(chosen_port, chosen_baud)
                if ok:
                    st.success(f"Connected: {chosen_port}")
                    st.toast(f"Sensor connected on {chosen_port} @ {chosen_baud} baud", icon="🔌")
                else:
                    st.error(msg)
        with col_c2:
            if st.button("❌ Disconnect", use_container_width=True):
                active_hw_mgr.disconnect()
                st.info("Sensor disconnected.")

        if active_hw_mgr.is_connected:
            st.success(f"🟢 **Live:** `{active_hw_mgr.connected_port}` @ `{active_hw_mgr.baud_rate}` bps")
        else:
            st.caption("⚪ Ready to connect physical hardware.")
    else:
        st.info("🛰️ **Simulated Mock Stream Active**\n\nStochastic Brownian walk with continuous safe baseline modeling.")

    st.divider()

    # 4. RESTORED ORIGINAL 4 SIDEBAR ACTION BUTTONS (Intact!)
    st.markdown("### 🎮 Interactive Controls")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⚠️ Spike PPM (>400)", help="Inject high emission breach (>400 PPM) to trigger penalty burn", use_container_width=True):
            if active_tenant_obj:
                active_tenant_obj.hardware_mgr.trigger_high_emission_spike(spike_ppm=540.0, steps=8)
                st.toast(f"🚨 High emission injected (> 400 PPM) for {active_tenant_obj.short_name}! Penalty burn triggered.", icon="🔥")
            else:
                st.toast("Please onboard an active company first to test interactive actions.", icon="⚠️")

    with col_btn2:
        if st.button("🌿 Clean Air (<=400)", help="Drop PPM safely below 400 to test clean air micro-credit reward", use_container_width=True):
            if active_tenant_obj:
                active_tenant_obj.hardware_mgr.sim_current_ppm = 360.0
                active_tenant_obj.hardware_mgr.sim_spike_active = False
                st.toast(f"🟢 Clean air restored (<= 400 PPM) for {active_tenant_obj.short_name}! Micro-credits rewarding.", icon="🌿")
            else:
                st.toast("Please onboard an active company first to test interactive actions.", icon="⚠️")

    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("🌿 Buy Offset", help="Purchase +100 Z Credits (+100 Tons CO2)", use_container_width=True):
            if active_tenant_obj:
                tx = ledger.purchase_offset_for_tenant(active_tenant_obj.id, OFFSET_PURCHASE_UNIT)
                if tx:
                    st.toast(f"✅ Purchased +100 Z Credits (+100 Tons CO2) for {active_tenant_obj.short_name}! TX: {tx.tx_hash}", icon="🌿")
            else:
                st.toast("Please onboard an active company first to purchase offsets.", icon="⚠️")

    with col_btn4:
        if st.button("⚡ Run Audit", help="Force oracle smart contract audit quorum", use_container_width=True):
            aud_target = active_tenant_obj.id if active_tenant_obj else None
            tx = ledger.trigger_audit(aud_target)
            st.toast(f"Consensus Audit: {tx.tx_hash}", icon="⚡")

    st.divider()

    # 5. Live Stream Status & Manual Refresh (No Page Blinking!)
    st.markdown("### ⏱️ Telemetry Engine")
    st.success("🟢 **Live Fragment Streaming (2.0s)**\n\nTelemetry updates smoothly without full-page blinking.")
    if st.button("🔄 Refresh All", use_container_width=True):
        st.rerun()

    st.divider()
    st.caption(
        f"**CONTRACT:** `{SMART_CONTRACT_ADDRESS[:16]}...`\n\n"
        f"**ORACLE:** `{ORACLE_ADDRESS[:16]}...`\n\n"
        f"**TOKENOMICS:** `1 ZC = 1 Metric Ton CO2`"
    )


# ===================================================================================
# 4. MAIN DASHBOARD: HERO BANNER & DIRECTOR APPROVAL QUEUE
# ===================================================================================
# Determine active tenant context for presentation
if active_role == ROLE_ISSUER:
    display_title = "Central Carbon Registry & Regulatory Quorum"
    display_sub = "Issuer Director Oversight Mode"
    if active_tenant_obj:
        current_ppm = active_tenant_obj.last_reading["ppm"]
        compliance_status, status_color, status_desc = ledger.determine_compliance_status(current_ppm)
        hw_label = f"ESP32/Arduino ({active_tenant_obj.hardware_mgr.connected_port})" if (st.session_state.use_hardware and active_tenant_obj.hardware_mgr.is_connected) else "Multi-Tenant Oracle Quorum"
    else:
        current_ppm = DEFAULT_SAFE_PPM
        compliance_status, status_color, status_desc = "Green", "#00F5A0", "Safe Baseline Initialized"
        hw_label = "Oracle Initialized"
else: # ROLE_COMPANY
    display_title = active_tenant_obj.name if active_tenant_obj else "Enterprise Tenant"
    display_sub = f"Isolated Vault & Telemetry • {active_tenant_obj.industry if active_tenant_obj else 'Operations'}"
    current_ppm = active_tenant_obj.last_reading["ppm"] if active_tenant_obj else DEFAULT_SAFE_PPM
    compliance_status, status_color, status_desc = ledger.determine_compliance_status(current_ppm)
    hw_label = f"ESP32/Arduino ({active_tenant_obj.hardware_mgr.connected_port})" if (st.session_state.use_hardware and active_tenant_obj and active_tenant_obj.hardware_mgr.is_connected) else "Simulated Mock Stream"

# Render Animated Hero Banner with Enhanced 3D Rotating Earth
st.markdown(
    render_hero_banner(
        company_name=display_title,
        role_label=display_sub,
        current_ppm=current_ppm,
        status_label=compliance_status,
        status_color=status_color,
        blocks_count=ledger.total_blocks_mined,
        hardware_label=hw_label,
        safe_ppm=DEFAULT_SAFE_PPM
    ),
    unsafe_allow_html=True
)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------------
# REQUIREMENT 1: DIRECTOR APPROVAL QUEUE PANEL (Issuer / Director View Only)
# -----------------------------------------------------------------------------------
if active_role == ROLE_ISSUER:
    pending_tenants = ledger.get_pending_tenants()

    if pending_tenants:
        with st.container(border=True):
            st.markdown(f"### 📋 Pending Tenant Approvals ({len(pending_tenants)} Awaiting Verification)")
            st.caption("Review and verify incoming enterprise registrations. Approving an application assigns an on-chain vault and activates access.")

            for p_id, p_tenant in list(pending_tenants.items()):
                with st.container(border=True):
                    col_p_info, col_p_actions = st.columns([4, 1.2])
                    with col_p_info:
                        st.markdown(f"#### 🏢 {p_tenant.name} (`{p_tenant.short_name}`)")
                        st.markdown(
                            f"- **Representative:** `{p_tenant.representative_name or 'N/A'}` • **Industry:** `{p_tenant.industry}`\n"
                            f"- **Assigned IoT Node:** `{p_tenant.device_id}` • **Baseline PPM:** `{p_tenant.baseline_ppm:.1f} PPM`\n"
                            f"- **Requested Initial Allocation:** **{p_tenant.initial_allocation:.1f} Z Credits ({p_tenant.initial_allocation:.1f} Tons CO2)**\n"
                            f"- **Registration Timestamp:** `{p_tenant.created_at}` • **Generated Vault:** `{p_tenant.vault_address}`"
                        )
                    with col_p_actions:
                        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                        if st.button("✅ Approve", key=f"btn_apprv_{p_id}", type="primary", use_container_width=True):
                            approved_t = ledger.approve_tenant(p_id)
                            st.toast(f"✅ Approved '{approved_t.name}'! Vault activated on-chain.", icon="🚀")
                            st.session_state.active_tenant_id = p_id
                            st.rerun()
                        if st.button("❌ Reject", key=f"btn_rej_{p_id}", use_container_width=True):
                            ledger.reject_tenant(p_id)
                            st.toast(f"❌ Rejected registration for '{p_tenant.name}'.", icon="🚫")
                            st.rerun()
        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


# ===================================================================================
# 5. ISOLATED LIVE TELEMETRY FRAGMENT (Requirement 3: Zero Page Blinking)
# ===================================================================================
@st.fragment(run_every=2.0)
def render_live_telemetry_fragment(tenant_id: str, is_hardware_active: bool):
    """
    Reruns independently every 2 seconds without blinking or reloading the rest of the application.
    Updates only the live sensor metrics, Plotly air quality graph, rules, and transaction table.
    """
    tenant = ledger.tenants.get(tenant_id)
    if not tenant:
        st.info("Tenant profile not found.")
        return

    # 1. Update this tenant's reading smoothly
    reading = tenant.hardware_mgr.get_reading(use_hardware=is_hardware_active)
    t_ppm = reading.get("ppm", tenant.baseline_ppm)
    prev_ppm = tenant.last_reading.get("ppm", t_ppm)
    delta_ppm = t_ppm - prev_ppm

    tenant.last_reading = {
        "ppm": t_ppm,
        "delta_ppm": delta_ppm,
        "temp": reading.get("temp", 24.5),
        "humidity": reading.get("humidity", 51.0),
        "source": reading.get("source", "Simulated Mock Stream"),
        "timestamp": reading.get("timestamp", time.time())
    }

    # Execute automated smart contract tokenomics
    # > 400 PPM: Burns credits & logs penalty in vault
    # <= 400 PPM: Mints micro-credits in vault
    ledger.process_tenant_reading(
        tenant_id=tenant.id,
        ppm=t_ppm,
        sensor_source=reading.get("source", "IoT Gas Telemetry")
    )

    t1_ppm = tenant.last_reading["ppm"]
    t1_status, t1_color, t1_desc = ledger.determine_compliance_status(t1_ppm)

    # 2. Render 4 Live Metric Cards inside isolated fragment
    render_metric_cards_native(
        ppm=t1_ppm,
        delta_ppm=tenant.last_reading["delta_ppm"],
        credits_balance=tenant.token_balance,
        compliance_status=t1_status,
        status_desc=t1_desc,
        is_hardware=is_hardware_active,
        port_name=tenant.hardware_mgr.connected_port,
        device_id=tenant.device_id,
        temp=tenant.last_reading["temp"],
        humidity=tenant.last_reading["humidity"],
        safe_ppm=DEFAULT_SAFE_PPM
    )

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # 3. Live Plotly Spline Chart & Rules Card
    col_chart_left, col_chart_right = st.columns([3, 1])
    with col_chart_left:
        st.markdown(f"##### 📈 Real-Time Gas Sensor Telemetry: {tenant.name}")
        fig_air = create_air_quality_chart(tenant.history, safe_threshold=DEFAULT_SAFE_PPM)
        st.plotly_chart(fig_air, use_container_width=True, config={"displayModeBar": False})

    with col_chart_right:
        with st.container(border=True):
            st.markdown("##### ⚡ Smart Contract Rules")
            st.markdown(
                f"🟢 **SAFE BASELINE** (`<= {DEFAULT_SAFE_PPM:.0f} PPM`)\n\n"
                f"*Micro-Credit Incentive: +{CLEAN_AIR_REWARD_RATE:.2f} ZC (+{CLEAN_AIR_REWARD_RATE:.2f} Tons CO2)*"
            )
            st.divider()
            st.markdown(
                f"🔴 **EMISSION BREACH** (`> {DEFAULT_SAFE_PPM:.0f} PPM`)\n\n"
                f"*Automated Penalty: -{PENALTY_BURN_RATE:.2f} ZC (-{PENALTY_BURN_RATE:.2f} Tons CO2)*"
            )
            st.divider()
            st.caption(
                f"**TOKENOMICS:** 1 Z Credit (ZC) = 1 Metric Ton CO2 equivalent.<br>"
                f"Current Status: <strong style='color: {t1_color};'>{t1_status.upper()}</strong>",
                unsafe_allow_html=True
            )

    st.markdown(f"#### ⚡ Recent Private Transactions for {tenant.short_name}")
    st.markdown(
        render_transaction_table_html(tenant.transactions[:6], show_tenant_col=False),
        unsafe_allow_html=True
    )


# ===================================================================================
# 6. RENAMED 4 MAIN NAVIGATION TABS (Requirement 1)
# ===================================================================================
tab_live, tab_ledger, tab_hardware, tab_market = st.tabs([
    "📈 Companies & Telemetry",
    "📜 Blockchain Ledger",
    "🔌 Hardware Devices & Sensors",
    "🌿 Offset Marketplace"
])


# -----------------------------------------------------------------------------------
# TAB 1: Companies & Telemetry (Requirement 1 & 3: Smooth Isolated Fragment Updates)
# -----------------------------------------------------------------------------------
with tab_live:
    if active_role == ROLE_ISSUER:
        if len(active_tenants) == 0:
            st.info(
                "🌱 **No Active Approved Customer Companies Yet**\n\n"
                "The ledger registry currently has 0 active companies. "
                "Review pending tenant registrations in the **📋 Pending Tenant Approvals** panel above, "
                "or deploy an enterprise profile using the sidebar form."
            )
            selected_tenant_for_tab1 = None
        else:
            col_t1_sel, col_t1_info = st.columns([2.5, 3])
            with col_t1_sel:
                active_tids = list(active_tenants.keys())
                current_idx = active_tids.index(active_tenant_id) if active_tenant_id in active_tids else 0
                chosen_inspect_id = st.selectbox(
                    "🏢 Select Approved Customer Company to Inspect Telemetry:",
                    options=active_tids,
                    index=current_idx,
                    format_func=lambda tid: f"{active_tenants[tid].name} [{active_tenants[tid].device_id}] ({active_tenants[tid].industry})",
                    help="Issuer / Director view: inspect real-time telemetry across any dynamically approved customer company."
                )
                if chosen_inspect_id != active_tenant_id:
                    st.session_state.active_tenant_id = chosen_inspect_id
                    st.rerun()

            selected_tenant_for_tab1 = active_tenants[chosen_inspect_id]
            with col_t1_info:
                st.caption(
                    f"**INSPECTING TENANT:** `{selected_tenant_for_tab1.name}` • "
                    f"**SECTOR:** `{selected_tenant_for_tab1.industry}` • "
                    f"**DEVICE:** `{selected_tenant_for_tab1.device_id}`"
                )

    else:
        # Customer: Strictly restricted to only show their own registered company
        selected_tenant_for_tab1 = active_tenant_obj
        if selected_tenant_for_tab1:
            st.caption(
                f"🔒 **Private Enterprise Channel**: Displaying private telemetry for **{selected_tenant_for_tab1.name}** (`{selected_tenant_for_tab1.device_id}`). "
                f"All other enterprise tenants' data is strictly isolated."
            )

    # Render isolated live telemetry fragment without whole-page blinking
    if selected_tenant_for_tab1:
        render_live_telemetry_fragment(
            tenant_id=selected_tenant_for_tab1.id,
            is_hardware_active=st.session_state.use_hardware
        )


# -----------------------------------------------------------------------------------
# TAB 2: Blockchain Ledger (Requirement 1 Renamed)
# -----------------------------------------------------------------------------------
with tab_ledger:
    st.markdown("### 📜 Enterprise Blockchain Ledger & zkEVM Explorer")

    target_tenant_tab2 = active_tenant_obj if active_role == ROLE_COMPANY else (
        active_tenants.get(st.session_state.active_tenant_id) if active_tenants else None
    )

    # 1. Role-Filtered Isolated Vault Records
    if target_tenant_tab2:
        with st.container(border=True):
            st.markdown(f"#### 🔒 Isolated Vault Breakdown: {target_tenant_tab2.name}")
            if active_role == ROLE_COMPANY:
                st.caption("This vault record is strictly isolated and accessible only to your organization and the regulatory issuer.")
            else:
                st.caption(f"Issuer Admin inspection of customer vault: `{target_tenant_tab2.vault_address}`")

            col_v1, col_v2, col_v3, col_v4 = st.columns(4)
            with col_v1:
                st.metric(
                    "Current Vault Balance",
                    f"{target_tenant_tab2.token_balance:,.2f} ZC",
                    f"= {target_tenant_tab2.token_balance:,.2f} Tons CO2e",
                    delta_color="normal"
                )
            with col_v2:
                st.metric(
                    "Clean Air Rewards",
                    f"+{target_tenant_tab2.total_minted:,.2f} ZC",
                    f"+{target_tenant_tab2.total_minted:,.2f} Tons CO2",
                    delta_color="normal"
                )
            with col_v3:
                st.metric(
                    "Penalties Burned",
                    f"-{target_tenant_tab2.total_burned:,.2f} ZC",
                    f"{target_tenant_tab2.total_fines_count} Slashes",
                    delta_color="inverse" if target_tenant_tab2.total_burned > 0 else "off"
                )
            with col_v4:
                st.metric(
                    "Voluntary Offsets",
                    f"+{target_tenant_tab2.total_offset_purchased:,.2f} ZC",
                    f"+{target_tenant_tab2.total_offset_purchased:,.2f} Tons CO2",
                    delta_color="normal"
                )

            # Issuer Administrative Allocation Tool
            if active_role == ROLE_ISSUER:
                with st.expander("⚖️ Issuer Authority: Allocate / Grant Compliance Credits"):
                    col_ia1, col_ia2 = st.columns([3, 1])
                    with col_ia1:
                        grant_amt = st.number_input("Grant Compliance Z Credits (Tons CO2)", min_value=10.0, max_value=2000.0, value=100.0, step=10.0)
                    with col_ia2:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("Mint to Customer Vault", type="primary"):
                            tx = ledger.purchase_offset_for_tenant(target_tenant_tab2.id, grant_amt)
                            if tx:
                                st.success(f"Granted +{grant_amt:.1f} ZC to {target_tenant_tab2.name}!")
                                st.rerun()

            st.markdown("##### 📄 Private Transaction Journal")
            st.markdown(
                render_transaction_table_html(target_tenant_tab2.transactions, show_tenant_col=False),
                unsafe_allow_html=True
            )

            if target_tenant_tab2.transactions:
                df_priv = pd.DataFrame([tx.to_dict() for tx in target_tenant_tab2.transactions])
                csv_priv = df_priv.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Export {target_tenant_tab2.short_name} Ledger (CSV)",
                    data=csv_priv,
                    file_name=f"{target_tenant_tab2.id}_ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No active customer companies registered yet. Onboard and approve a company to inspect vault transactions.")

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # 2. Shared Public Blockchain Ledger (Decentralized Consensus Transparency)
    with st.container(border=True):
        st.markdown("#### 🌐 Shared Public Blockchain Ledger (Decentralized Consensus)")
        st.caption(
            "Cryptographic proof-of-emission ledger verified across all participants on the Zerovia Eco-Chain (zkEVM L2). "
            "Public notarization guarantees global auditability without revealing private telemetry curves."
        )

        all_public_txs = ledger.get_public_ledger_transactions()
        st.markdown(
            render_transaction_table_html(all_public_txs, show_tenant_col=True),
            unsafe_allow_html=True
        )


# -----------------------------------------------------------------------------------
# TAB 3: Hardware Devices & Sensors (Requirement 1 Renamed)
# -----------------------------------------------------------------------------------
with tab_hardware:
    st.markdown("### 🔌 Universal Hardware Devices & Gas Sensors")

    target_tenant_tab3 = active_tenant_obj if active_role == ROLE_COMPANY else (
        active_tenants.get(st.session_state.active_tenant_id) if active_tenants else None
    )

    col_hw_l, col_hw_r = st.columns(2)
    with col_hw_l:
        with st.container(border=True):
            st.markdown("#### 📡 Universal Node Hardware Profile")
            if target_tenant_tab3:
                hw_conn_status = "Physical Serial USB" if (st.session_state.use_hardware and target_tenant_tab3.hardware_mgr.is_connected) else "Simulated Mock Stream"
                st.markdown(f"- **Assigned Facility:** `{target_tenant_tab3.name}`")
                st.markdown(f"- **Sensor Node ID:** `{target_tenant_tab3.device_id}`")
                st.markdown(f"- **Interface Mode:** `{hw_conn_status}`")
                st.markdown(f"- **COM Port:** `{target_tenant_tab3.hardware_mgr.connected_port or 'Simulated Port'}`")
                st.markdown(f"- **Baud Rate:** `{target_tenant_tab3.hardware_mgr.baud_rate} bps`")
                st.markdown(f"- **Safe Baseline Limit:** `<= {DEFAULT_SAFE_PPM:.0f} PPM`")
                st.markdown(f"- **Current Reading:** `{target_tenant_tab3.last_reading.get('ppm', 0):.1f} PPM`")
                st.markdown(f"- **Temperature:** `{target_tenant_tab3.last_reading.get('temp', 24.5):.1f} °C`")
                st.markdown(f"- **Relative Humidity:** `{target_tenant_tab3.last_reading.get('humidity', 51.0):.1f} %`")
            else:
                st.info("No active tenant selected. Connect or onboard an enterprise node to inspect diagnostics.")

    with col_hw_r:
        with st.container(border=True):
            st.markdown("#### 📐 Gas Sensor Calibration Formula")
            st.markdown(
                """
                Semiconductor gas sensors (MQ-135, MQ-4, BME680) exhibit logarithmic conductivity changes proportional to gas concentration:

                $$\\text{PPM} = 110.47 \\times \\left(\\frac{R_s}{R_o}\\right)^{-2.862}$$

                - **$R_L$ (Load Resistance):** $10\\text{ k}\\Omega$
                - **$R_o$ (Clean Air Resistance):** $76.63\\text{ k}\\Omega$
                - **$R_s$ (Sensor Resistance):** $\\frac{V_{in} - V_{out}}{V_{out}} \\times R_L$
                - **Safe Regulatory Baseline:** **$400.0\\text{ PPM}$**
                """
            )

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("📝 View Embedded ESP32 / Arduino Firmware Source Code (`esp32_mq135.ino`)"):
        firmware_file = os.path.join(os.path.dirname(__file__), "firmware", "esp32_mq135.ino")
        if os.path.exists(firmware_file):
            with open(firmware_file, "r", encoding="utf-8") as f:
                st.code(f.read(), language="cpp")
        else:
            st.caption("Firmware sketch available in repository `/firmware` folder.")


# -----------------------------------------------------------------------------------
# TAB 4: Offset Marketplace (Requirement 1 Renamed)
# -----------------------------------------------------------------------------------
with tab_market:
    st.markdown("### 🌿 Decentralized Carbon Offset Marketplace & ESG Registry")

    target_tenant_tab4 = active_tenant_obj if active_role == ROLE_COMPANY else (
        active_tenants.get(st.session_state.active_tenant_id) if active_tenants else None
    )

    if target_tenant_tab4:
        col_m_l, col_m_r = st.columns(2)

        # Left Column: Purchase Verified Offsets (Mint to Vault)
        with col_m_l:
            with st.container(border=True):
                st.markdown("#### 💰 Carbon Valuation (1 ZC = 1 Ton CO2)")
                m_sub1, m_sub2 = st.columns(2)
                with m_sub1:
                    st.metric(
                        "Enterprise Vault Balance",
                        f"{target_tenant_tab4.token_balance:,.2f} ZC",
                        f"= {target_tenant_tab4.token_balance:,.2f} Tons CO2"
                    )
                with m_sub2:
                    st.metric(
                        "Market Valuation",
                        f"${(target_tenant_tab4.token_balance * OFFSET_UNIT_PRICE_USD):,.2f} USD"
                    )
                st.caption(f"1 Z Credit = 1 Metric Ton CO2 equivalent audited on {CHAIN_NAME}.")

            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("#### 🛒 Purchase Verified Z Credits")
                st.caption(f"Offsets will be deposited directly into vault: `{target_tenant_tab4.vault_address}`")
                units_to_buy = st.number_input(
                    "Z Credits to Purchase (1 Unit = 1 Ton CO2)",
                    min_value=10.0, max_value=5000.0, value=100.0, step=10.0,
                    key="tab4_buy_units"
                )
                cost_usd = units_to_buy * OFFSET_UNIT_PRICE_USD
                st.info(f"Total Valuation: **${cost_usd:,.2f} USD** (@ ${OFFSET_UNIT_PRICE_USD:.2f} / Ton CO2)")

                if st.button("💳 Purchase Verified Offsets (Mint to Vault)", type="primary", use_container_width=True):
                    tx = ledger.purchase_offset_for_tenant(target_tenant_tab4.id, units_to_buy)
                    if tx:
                        st.success(f"Successfully minted +{units_to_buy:.1f} Z Credits (+{units_to_buy:.1f} Tons CO2) to {target_tenant_tab4.short_name}! TX: `{tx.tx_hash}`")
                        time.sleep(1.0)
                        st.rerun()

        # Right Column: ESG Carbon Neutrality Retirement
        with col_m_r:
            with st.container(border=True):
                st.markdown("#### 🔥 ESG Carbon Neutrality Retirement")
                st.write(
                    "Permanently retire Z Credits from your vault to obtain official carbon neutrality certificates. "
                    "Each retired Z Credit certifies the permanent removal of **1 Metric Ton of CO2**."
                )

            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("#### 📜 Retire Credits for Compliance")
                retire_amount = st.number_input(
                    "Z Credits to Permanently Burn (Tons CO2)",
                    min_value=1.0,
                    max_value=max(1.0, target_tenant_tab4.token_balance),
                    value=min(25.0, max(1.0, target_tenant_tab4.token_balance)),
                    step=5.0,
                    key="tab4_retire_units"
                )
                if st.button("🔥 Permanently Burn & Claim Certificate", use_container_width=True):
                    if retire_amount > target_tenant_tab4.token_balance:
                        st.error("Insufficient credit balance to retire this amount.")
                    else:
                        tx = ledger.retire_credits_for_tenant(target_tenant_tab4.id, retire_amount)
                        if tx:
                            st.balloons()
                            with st.container(border=True):
                                st.success("🌿 OFFICIAL CERTIFICATE OF CARBON RETIREMENT")
                                st.markdown(
                                    f"""
                                    - **Beneficiary Enterprise:** `{target_tenant_tab4.name}`
                                    - **Device Node:** `{target_tenant_tab4.device_id}`
                                    - **Retired Carbon:** **{retire_amount:.1f} Z Credits ({retire_amount:.1f} Metric Tons CO2e)**
                                    - **Transaction Hash:** `{tx.tx_hash}`
                                    - **Consensus Quorum:** Zerovia zkEVM Multi-Tenant Oracle Network
                                    """
                                )
                            time.sleep(2.0)
                            st.rerun()
    else:
        st.info("No active customer companies registered yet. Onboard and approve a company to access marketplace features.")
