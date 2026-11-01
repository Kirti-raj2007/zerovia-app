"""
UI Components, Custom CSS animations, Plotly visualizers, and Multi-Tenant Layouts
for Zerovia Carbon Ledger.
"""

import base64
import os
import textwrap
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.config import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    CHAIN_NAME,
    SMART_CONTRACT_ADDRESS,
    ORACLE_ADDRESS,
    DEFAULT_SAFE_PPM,
    OFFSET_UNIT_PRICE_USD,
    CARBON_UNIT_TO_TONS
)


def get_logo_svg_content() -> str:
    """Read the vector logo SVG content."""
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.svg")
    if os.path.exists(logo_path):
        with open(logo_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def get_logo_data_uri() -> str:
    """Encode SVG logo as data URI for streamlit image / favicon."""
    svg = get_logo_svg_content()
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


def get_animated_earth_logo_html(size_px: int = 54) -> str:
    """
    Returns a highly realistic, CSS 3D-animated rotating Earth visualization
    with dynamic spherical curvature lighting, realistic continent topography,
    atmospheric Rayleigh scattering glow, drifting cloud layer, and orbiting IoT satellite.
    """
    sphere_size = int(size_px * 0.86)
    orbit_height = int(size_px * 0.46)
    html = f"""
    <div class="earth-3d-system" style="width: {size_px}px; height: {size_px}px;">
        <!-- Atmospheric Rayleigh Scattering Halo -->
        <div class="earth-3d-halo" style="width: {size_px}px; height: {size_px}px;"></div>

        <!-- 3D Earth Globe Sphere -->
        <div class="earth-3d-globe" style="width: {sphere_size}px; height: {sphere_size}px;">
            <!-- Deep Ocean Base -->
            <div class="earth-ocean-base"></div>

            <!-- Continents Map Layer (Seamless 360-degree rotation) -->
            <svg class="earth-3d-continents" viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="earth-land-grad" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stop-color="#00F5A0" stop-opacity="0.95"/>
                        <stop offset="60%" stop-color="#00D9F5" stop-opacity="0.85"/>
                        <stop offset="100%" stop-color="#059669" stop-opacity="0.90"/>
                    </linearGradient>
                </defs>
                <!-- World Map Cycle 1 -->
                <g fill="url(#earth-land-grad)">
                    <!-- North America -->
                    <path d="M14,24 Q22,14 36,20 Q44,28 34,42 Q22,46 16,36 Z"/>
                    <!-- South America -->
                    <path d="M30,48 Q42,50 38,72 Q28,82 24,66 Z"/>
                    <!-- Greenland -->
                    <path d="M40,10 Q48,8 46,18 Q38,18 40,10 Z"/>
                    <!-- Europe -->
                    <path d="M68,18 Q80,14 86,24 Q82,34 72,32 Q66,26 68,18 Z"/>
                    <!-- Africa -->
                    <path d="M70,36 Q86,34 90,52 Q84,72 74,72 Q66,54 70,36 Z"/>
                    <!-- Asia -->
                    <path d="M88,16 Q112,12 128,24 Q136,38 120,44 Q102,40 92,28 Z"/>
                    <!-- Australia -->
                    <path d="M120,60 Q134,56 136,68 Q128,78 118,74 Z"/>
                    <!-- Japan & Island Arc -->
                    <path d="M138,28 Q142,26 140,36 Q136,34 138,28 Z"/>
                </g>
                <!-- World Map Cycle 2 (for seamless infinite pan) -->
                <g fill="url(#earth-land-grad)" transform="translate(200, 0)">
                    <path d="M14,24 Q22,14 36,20 Q44,28 34,42 Q22,46 16,36 Z"/>
                    <path d="M30,48 Q42,50 38,72 Q28,82 24,66 Z"/>
                    <path d="M40,10 Q48,8 46,18 Q38,18 40,10 Z"/>
                    <path d="M68,18 Q80,14 86,24 Q82,34 72,32 Q66,26 68,18 Z"/>
                    <path d="M70,36 Q86,34 90,52 Q84,72 74,72 Q66,54 70,36 Z"/>
                    <path d="M88,16 Q112,12 128,24 Q136,38 120,44 Q102,40 92,28 Z"/>
                    <path d="M120,60 Q134,56 136,68 Q128,78 118,74 Z"/>
                    <path d="M138,28 Q142,26 140,36 Q136,34 138,28 Z"/>
                </g>
                <!-- Coordinate Latitude Grids -->
                <line x1="0" y1="25" x2="400" y2="25" stroke="rgba(0, 217, 245, 0.22)" stroke-width="0.7" stroke-dasharray="2 3"/>
                <line x1="0" y1="50" x2="400" y2="50" stroke="rgba(0, 245, 160, 0.30)" stroke-width="0.9" stroke-dasharray="3 3"/>
                <line x1="0" y1="75" x2="400" y2="75" stroke="rgba(0, 217, 245, 0.22)" stroke-width="0.7" stroke-dasharray="2 3"/>
                <!-- Pulsing IoT Environmental Monitoring Nodes -->
                <circle cx="28" cy="30" r="1.6" fill="#00F5A0" class="iot-node-ping"/>
                <circle cx="76" cy="24" r="1.6" fill="#00D9F5" class="iot-node-ping"/>
                <circle cx="112" cy="28" r="1.6" fill="#00F5A0" class="iot-node-ping"/>
                <circle cx="228" cy="30" r="1.6" fill="#00F5A0" class="iot-node-ping"/>
                <circle cx="276" cy="24" r="1.6" fill="#00D9F5" class="iot-node-ping"/>
                <circle cx="312" cy="28" r="1.6" fill="#00F5A0" class="iot-node-ping"/>
            </svg>

            <!-- Atmospheric Cloud Parallax Layer -->
            <svg class="earth-3d-clouds" viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
                <g fill="rgba(255, 255, 255, 0.28)">
                    <path d="M20,18 Q35,12 45,20 Q35,26 20,18 Z"/>
                    <path d="M60,40 Q80,32 95,44 Q75,50 60,40 Z"/>
                    <path d="M110,16 Q130,10 145,22 Q125,28 110,16 Z"/>
                    <path d="M15,65 Q35,58 50,68 Q30,74 15,65 Z"/>
                    <!-- Repeat for 200px offset -->
                    <path d="M220,18 Q235,12 245,20 Q235,26 220,18 Z"/>
                    <path d="M260,40 Q280,32 295,44 Q275,50 260,40 Z"/>
                    <path d="M310,16 Q330,10 345,22 Q325,28 310,16 Z"/>
                    <path d="M215,65 Q235,58 250,68 Q230,74 215,65 Z"/>
                </g>
            </svg>

            <!-- Photorealistic 3D Spherical Specular Shading & Night Shadow -->
            <div class="earth-3d-shading"></div>
        </div>

        <!-- Tilted 3D Satellite Orbit Ring -->
        <div class="earth-3d-orbit" style="width: {size_px}px; height: {orbit_height}px;">
            <div class="earth-3d-satellite"></div>
        </div>
    </div>
    """
    return sanitize_html(html)


# Custom CSS with Keyframe Animations, Glassmorphism, and Cyber-Industrial Aesthetic
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Montserrat:wght@700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg-deep-space-1: #0A0E17;
    --bg-deep-space-2: #0D131F;
    --bg-deep-space-3: #121824;
    --bg-surface: rgba(16, 24, 38, 0.75);
    --border-glow: rgba(0, 245, 160, 0.22);
    --border-accent: rgba(0, 217, 245, 0.25);
    --neon-green: #00F5A0;
    --neon-cyan: #00D9F5;
    --neon-amber: #F59E0B;
    --neon-crimson: #EF4444;
    --text-primary: #F8FAFC;
    --text-muted: #94A3B8;
}

/* Global Streamlit Deep Space Charcoal / Navy Slate Gradient (#0A0E17 to #121824) */
.stApp {
    background: linear-gradient(135deg, #0A0E17 0%, #0D131F 35%, #121824 70%, #0A0E17 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}

/* Sidebar Styling with matching deep space charcoal palette */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070B12 0%, #0A0E18 50%, #060910 100%) !important;
    border-right: 1px solid rgba(0, 245, 160, 0.18) !important;
    box-shadow: 4px 0 30px rgba(0, 0, 0, 0.6);
}

/* Enhanced Native Streamlit Glassmorphic Containers */
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(14, 20, 32, 0.72) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0, 245, 160, 0.18) !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 30px -8px rgba(0, 0, 0, 0.6), 0 0 1px 1px rgba(0, 245, 160, 0.12) !important;
    transition: all 0.25s ease-in-out !important;
    padding: 18px 20px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    border-color: rgba(0, 245, 160, 0.38) !important;
    box-shadow: 0 12px 36px -6px rgba(0, 245, 160, 0.15), 0 0 16px rgba(0, 217, 245, 0.12) !important;
    transform: translateY(-1px);
}

/* Tab Navigation Styling */
button[data-baseweb="tab"] {
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    padding: 10px 18px !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #00F5A0 !important;
    border-bottom: 2px solid #00F5A0 !important;
}

/* Realistic 3D Earth Visualization Animations */
@keyframes earthPan3D {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

@keyframes cloudsPan3D {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

@keyframes orbitSpin3D {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes haloPulse3D {
    0% { transform: scale(1); opacity: 0.65; }
    50% { transform: scale(1.05); opacity: 0.90; }
    100% { transform: scale(1); opacity: 0.65; }
}

@keyframes beaconFlash {
    0%, 100% { opacity: 0.2; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1.3); }
}

.earth-3d-system {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.earth-3d-halo {
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 217, 245, 0.28) 0%, rgba(0, 245, 160, 0.14) 50%, rgba(0, 0, 0, 0) 72%);
    animation: haloPulse3D 5s ease-in-out infinite;
    pointer-events: none;
}

.earth-3d-globe {
    border-radius: 50%;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 20px rgba(0, 217, 245, 0.45), inset -8px -8px 18px rgba(0, 0, 0, 0.95), inset 6px 6px 14px rgba(0, 245, 160, 0.4);
    border: 1px solid rgba(0, 245, 160, 0.35);
    box-sizing: border-box;
    background: #040e1b;
}

.earth-ocean-base {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background: radial-gradient(circle at 35% 30%, #0d3b66 0%, #071f3a 50%, #020b18 100%);
}

.earth-3d-continents {
    width: 200%;
    height: 100%;
    position: absolute;
    left: 0;
    top: 0;
    animation: earthPan3D 12s linear infinite;
}

.earth-3d-clouds {
    width: 200%;
    height: 100%;
    position: absolute;
    left: 0;
    top: 0;
    animation: cloudsPan3D 8.5s linear infinite;
    pointer-events: none;
}

.earth-3d-shading {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 28%, rgba(255,255,255,0.32) 0%, rgba(255,255,255,0.06) 35%, rgba(0,0,0,0) 60%, rgba(2, 6, 14, 0.88) 100%);
    pointer-events: none;
}

.earth-3d-orbit {
    position: absolute;
    border-radius: 50%;
    border: 1.5px solid rgba(0, 217, 245, 0.38);
    transform: rotate(-28deg);
    pointer-events: none;
    animation: orbitSpin3D 7s linear infinite;
    box-sizing: border-box;
}

.earth-3d-satellite {
    position: absolute;
    top: -4px;
    left: 50%;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00F5A0;
    box-shadow: 0 0 8px #00F5A0, 0 0 16px #00D9F5;
    transform: translateX(-50%);
}

.iot-node-ping {
    animation: beaconFlash 2s ease-in-out infinite;
}

/* Hero Section Container with Deep Space Palette */
.hero-banner {
    position: relative;
    padding: 24px 28px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.14) 45%, rgba(14, 20, 32, 0.92) 100%) !important;
    border: 1px solid rgba(0, 245, 160, 0.28) !important;
    box-shadow: 0 20px 40px -15px rgba(0, 245, 160, 0.16) !important;
    margin-bottom: 20px;
    backdrop-filter: blur(16px);
    overflow: hidden;
}

.hero-title-row {
    display: flex;
    align-items: center;
    gap: 20px;
}

/* Premium Deep Black Sparkling Aesthetic for "Zerovia" */
@keyframes diamondGlintBeam {
    0% { left: -120%; }
    40%, 100% { left: 180%; }
}

@keyframes sparkleTwinkleA {
    0%, 100% { opacity: 0.35; transform: scale(0.75) rotate(0deg); }
    50% { opacity: 1; transform: scale(1.35) rotate(90deg); filter: drop-shadow(0 0 8px #ffffff) drop-shadow(0 0 14px #00F5A0); }
}

@keyframes sparkleTwinkleB {
    0%, 100% { opacity: 0.9; transform: scale(1.2) rotate(45deg); filter: drop-shadow(0 0 10px #ffffff); }
    50% { opacity: 0.25; transform: scale(0.65) rotate(135deg); }
}

@keyframes diamondPlinthPulse {
    0%, 100% { 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255, 255, 255, 0.4), 0 0 12px rgba(255, 255, 255, 0.15), 0 0 24px rgba(0, 245, 160, 0.15);
        border-color: rgba(255, 255, 255, 0.38);
    }
    50% { 
        box-shadow: 0 6px 28px rgba(0, 0, 0, 0.9), inset 0 1px 2px rgba(255, 255, 255, 0.7), 0 0 22px rgba(255, 255, 255, 0.35), 0 0 38px rgba(0, 217, 245, 0.28);
        border-color: rgba(255, 255, 255, 0.65);
    }
}

/* Luxury Diamond Frosted Glass Plinth Container */
.zerovia-sparkle-container {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 7px 22px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.14) 0%, rgba(15, 20, 30, 0.85) 50%, rgba(0, 245, 160, 0.09) 100%) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.38) !important;
    border-radius: 9999px !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    overflow: hidden !important;
    vertical-align: middle !important;
    animation: diamondPlinthPulse 4s ease-in-out infinite !important;
    user-select: none !important;
    white-space: nowrap !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

.zerovia-container-sidebar {
    padding: 3px 10px !important;
    gap: 6px !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    max-width: 100% !important;
}

/* Sweeping Diamond Shimmer Beam */
.zerovia-sparkle-container::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -120%;
    width: 60%;
    height: 200%;
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.35) 45%,
        rgba(0, 245, 160, 0.25) 70%,
        rgba(255, 255, 255, 0) 100%
    );
    transform: rotate(25deg);
    animation: diamondGlintBeam 4.5s ease-in-out infinite;
    pointer-events: none;
}

/* Core Deep Black Sparkling Typography for Zerovia */
.zerovia-deep-black-text,
.zerovia-sparkle-brand {
    font-family: 'Montserrat', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    display: inline-block !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    
    /* Razor-sharp diamond facet rim & starlight diamond aura */
    text-shadow: 
        -1px -1px 0 rgba(255, 255, 255, 0.95),
         1px -1px 0 rgba(255, 255, 255, 0.95),
        -1px  1px 0 rgba(255, 255, 255, 0.95),
         1px  1px 0 rgba(255, 255, 255, 0.95),
         0 0 10px rgba(255, 255, 255, 0.75),
         0 0 20px rgba(0, 245, 160, 0.45),
         0 0 35px rgba(0, 217, 245, 0.30) !important;
         
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.zerovia-deep-black-text:hover,
.zerovia-sparkle-brand:hover {
    text-shadow: 
        -1.5px -1.5px 0 #FFFFFF,
         1.5px -1.5px 0 #FFFFFF,
        -1.5px  1.5px 0 #FFFFFF,
         1.5px  1.5px 0 #FFFFFF,
         0 0 15px rgba(255, 255, 255, 0.95),
         0 0 28px rgba(0, 245, 160, 0.70),
         0 0 45px rgba(0, 217, 245, 0.50) !important;
    transform: scale(1.02);
}

.zerovia-brand-hero {
    font-size: 2.2rem !important;
    line-height: 1.15 !important;
    margin: 0 !important;
}

.zerovia-brand-sidebar {
    font-size: 0.92rem !important;
    letter-spacing: 0.08em !important;
    line-height: 1 !important;
    white-space: nowrap !important;
    margin: 0 !important;
}

.zerovia-brand-login {
    font-size: 2.5rem !important;
    line-height: 1.15 !important;
    margin-bottom: 4px !important;
}

/* Twinkling Diamond Sparkle Elements */
.sparkle-group {
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
}

.sparkle-diamond,
.sparkle-star {
    color: #FFFFFF !important;
    display: inline-block !important;
    filter: drop-shadow(0 0 6px #FFFFFF) drop-shadow(0 0 12px rgba(0, 245, 160, 0.8)) !important;
    user-select: none !important;
}

.sparkle-twinkle-1 {
    font-size: 1.1rem !important;
    animation: sparkleTwinkleA 2.6s ease-in-out infinite !important;
}

.sparkle-twinkle-2 {
    font-size: 0.75rem !important;
    animation: sparkleTwinkleB 3.4s ease-in-out infinite !important;
}

.hero-title {
    margin: 0;
    padding: 0;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 0.94rem;
    margin-top: 5px;
    font-weight: 400;
    max-width: 860px;
    line-height: 1.5;
}

.hero-badges-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 16px;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 12px;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(0, 245, 160, 0.28);
    border-radius: 9999px;
    font-size: 0.78rem;
    color: #E2E8F0;
    font-family: 'JetBrains Mono', monospace;
}

.hero-pill .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--neon-green);
    box-shadow: 0 0 8px var(--neon-green);
}

.badge-mint {
    background: rgba(0, 245, 160, 0.15);
    color: #00F5A0;
    border: 1px solid rgba(0, 245, 160, 0.35);
    padding: 3px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-fine {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 3px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-offset {
    background: rgba(6, 182, 212, 0.15);
    color: #00D9F5;
    border: 1px solid rgba(6, 182, 212, 0.4);
    padding: 3px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-tenant {
    background: rgba(168, 85, 247, 0.15);
    color: #C084FC;
    border: 1px solid rgba(168, 85, 247, 0.4);
    padding: 3px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
}

.tx-hash-code {
    font-family: 'JetBrains Mono', monospace;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8rem;
}

/* Interactive button glows */
div.stButton > button:first-child {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.25s ease;
    border: 1px solid rgba(0, 245, 160, 0.4);
}
div.stButton > button:first-child:hover {
    border-color: #00F5A0;
    box-shadow: 0 0 15px rgba(0, 245, 160, 0.4);
    transform: translateY(-1px);
}
</style>
"""


def sanitize_html(html_str: str) -> str:
    """Removes leading indentation and blank lines so Streamlit's Markdown parser never treats HTML as code blocks."""
    return "".join(line.strip() for line in html_str.splitlines() if line.strip())


def get_zerovia_brand_html(size_class: str = "zerovia-brand-hero", extra_style: str = "") -> str:
    """Returns the custom styled 'Zerovia' brand text in sparkling deep black diamond aesthetic."""
    if "sidebar" in size_class:
        # Compact single-sparkle badge optimized for sidebar column constraints
        html = f"""
        <span class="zerovia-sparkle-container zerovia-container-sidebar" style="{extra_style}">
            <span class="sparkle-diamond sparkle-twinkle-1" style="font-size: 0.68rem;">&#10022;</span>
            <span class="zerovia-deep-black-text {size_class}">Zerovia</span>
            <span class="sparkle-diamond sparkle-twinkle-1" style="font-size: 0.68rem; animation-delay: 1.3s;">&#10022;</span>
        </span>
        """
    else:
        # Full multi-sparkle luxury badge for hero section and login gate
        html = f"""
        <span class="zerovia-sparkle-container" style="{extra_style}">
            <span class="sparkle-group">
                <span class="sparkle-diamond sparkle-twinkle-1">&#10022;</span>
                <span class="sparkle-diamond sparkle-twinkle-2">&#10023;</span>
            </span>
            <span class="zerovia-deep-black-text {size_class}">Zerovia</span>
            <span class="sparkle-group">
                <span class="sparkle-diamond sparkle-twinkle-2">&#10023;</span>
                <span class="sparkle-diamond sparkle-twinkle-1" style="animation-delay: 1.3s;">&#10022;</span>
            </span>
        </span>
        """
    return sanitize_html(html)


def render_hero_banner(
    company_name: str,
    role_label: str,
    current_ppm: float,
    status_label: str,
    status_color: str,
    blocks_count: int,
    hardware_label: str,
    safe_ppm: float = DEFAULT_SAFE_PPM
) -> str:
    """Render the animated welcome dashboard hero section with tenant branding."""
    earth_logo = get_animated_earth_logo_html(size_px=68)
    zerovia_brand = get_zerovia_brand_html(size_class="zerovia-brand-hero")
    
    html = f"""
    <div class="hero-banner">
        <div class="hero-title-row">
            <div>
                {earth_logo}
            </div>
            <div>
                <h1 class="hero-title">{zerovia_brand}</h1>
                <div class="hero-subtitle">
                    Multi-Tenant IoT Carbon Ledger & Automated zkEVM Tokenomics.
                    <strong>1 Z Credit (ZC) = 1 Metric Ton CO2</strong> emission or verified offset.
                    Safe Baseline set to <strong>{safe_ppm:.0f} PPM</strong>.
                </div>
            </div>
        </div>

        <div class="hero-badges-row">
            <div class="hero-pill" style="border-color: rgba(168, 85, 247, 0.5);">
                <span class="dot" style="background-color: #A855F7; box-shadow: 0 0 8px #A855F7;"></span>
                <span>TENANT: <strong>{company_name}</strong></span>
            </div>
            <div class="hero-pill">
                <span class="dot" style="background-color: #00D9F5; box-shadow: 0 0 8px #00D9F5;"></span>
                <span>ROLE: <strong>{role_label}</strong></span>
            </div>
            <div class="hero-pill">
                <span class="dot" style="background-color: {status_color}; box-shadow: 0 0 8px {status_color};"></span>
                <span>STATUS: <strong>{status_label.upper()}</strong></span>
            </div>
            <div class="hero-pill">
                <span style="color: #00D9F5;">#BLOCKS:</span>
                <span><strong>{blocks_count:,}</strong></span>
            </div>
            <div class="hero-pill">
                <span style="color: #94A3B8;">FEED:</span>
                <span><strong>{hardware_label}</strong></span>
            </div>
            <div class="hero-pill">
                <span style="color: #94A3B8;">TOKENOMICS:</span>
                <span style="color: #00F5A0; font-weight: 700;">1 ZC = 1 Ton CO2</span>
            </div>
        </div>
    </div>
    """
    return sanitize_html(html)


def render_metric_cards_native(
    ppm: float,
    delta_ppm: float,
    credits_balance: float,
    compliance_status: str,
    status_desc: str,
    is_hardware: bool,
    port_name: Optional[str],
    device_id: str,
    temp: float,
    humidity: float,
    safe_ppm: float = DEFAULT_SAFE_PPM
):
    """
    Renders 4 responsive, clean metric cards using Streamlit's native components.
    Guarantees no raw HTML escapes, displays 1 ZC = 1 Ton CO2 conversions and 400 PPM safe baseline rules.
    """
    col1, col2, col3, col4 = st.columns(4)

    # 1. Air Quality Gas Monitor PPM
    with col1:
        with st.container(border=True):
            st.caption("AIR QUALITY GAS MONITOR")
            delta_str = f"{delta_ppm:+.1f} PPM" if abs(delta_ppm) >= 0.1 else "Stable"
            st.metric(
                label="Gas Telemetry",
                value=f"{ppm:.1f} PPM",
                delta=delta_str,
                delta_color="inverse" if delta_ppm > 0 else "normal"
            )
            st.caption(f"Safe Baseline: <= {safe_ppm:.0f} PPM")

    # 2. Active Z Credits (Tons CO2)
    with col2:
        with st.container(border=True):
            st.caption("ACTIVE Z CREDITS (VAULT)")
            tons_co2 = credits_balance * CARBON_UNIT_TO_TONS
            usd_val = credits_balance * OFFSET_UNIT_PRICE_USD
            st.metric(
                label="Carbon Balance",
                value=f"{credits_balance:,.2f} ZC",
                delta=f"= {tons_co2:,.2f} Tons CO2e",
                delta_color="off"
            )
            st.caption(f"≈ ${usd_val:,.2f} USD (@ $18.50/Ton)")

    # 3. Compliance Ledger State (400 PPM threshold)
    with col3:
        with st.container(border=True):
            st.caption("SMART CONTRACT STATE")
            status_icon = "🟢" if compliance_status == "Green" else "🔴"
            action_label = "Clean Air Reward (+0.25 ZC)" if compliance_status == "Green" else "Penalty Burn (-0.50 ZC)"
            st.metric(
                label="Compliance Status",
                value=f"{status_icon} {compliance_status}",
                delta=action_label,
                delta_color="normal" if compliance_status == "Green" else "inverse"
            )
            st.caption(status_desc)

    # 4. Telemetry Node & Device ID
    with col4:
        with st.container(border=True):
            st.caption("IOT TELEMETRY SOURCE")
            node_label = f"ESP32 ({port_name})" if (is_hardware and port_name) else "Simulated Mock Stream"
            st.metric(
                label="Hardware Link",
                value=node_label,
                delta=f"{temp:.1f}°C • {humidity:.1f}% RH",
                delta_color="off"
            )
            st.caption(f"Node ID: `{device_id}`")


def create_air_quality_chart(history_records: List[Dict], safe_threshold: float = DEFAULT_SAFE_PPM):
    """
    Create a real-time animated Plotly dark theme chart for air quality telemetry.
    Highlights the 400 PPM Safe Baseline boundary clearly:
    - <= 400 PPM: Safe Zone (Green) - Micro-credit rewards active
    - > 400 PPM: Fine Zone (Red) - Penalty burns enforced
    """
    if not history_records:
        df = pd.DataFrame([{"timestamp": "00:00:00", "ppm": safe_threshold - 20.0, "status": "Green"}])
    else:
        df = pd.DataFrame(history_records)

    fig = go.Figure()

    # Green Safe Zone Band (<= 400 PPM)
    fig.add_hrect(
        y0=0, y1=safe_threshold,
        fillcolor="rgba(0, 245, 160, 0.08)",
        layer="below", line_width=0,
        annotation_text=f"🟢 SAFE ZONE (<= {safe_threshold:.0f} PPM: Clean Air Micro-Credit Reward)",
        annotation_position="top left",
        annotation_font=dict(color="rgba(0, 245, 160, 0.75)", size=11)
    )

    # Penalty Zone Band (> 400 PPM)
    fig.add_hrect(
        y0=safe_threshold, y1=1200,
        fillcolor="rgba(239, 68, 68, 0.12)",
        layer="below", line_width=0,
        annotation_text=f"🔴 EMISSION PENALTY ZONE (> {safe_threshold:.0f} PPM: Automated Credit Burn)",
        annotation_position="top left",
        annotation_font=dict(color="rgba(239, 68, 68, 0.85)", size=11)
    )

    # 400 PPM Safe Baseline threshold marker
    fig.add_hline(
        y=safe_threshold,
        line_dash="dash",
        line_color="#EF4444",
        line_width=2,
        annotation_text=f"SAFE BASELINE ({safe_threshold:.0f} PPM)",
        annotation_position="bottom right",
        annotation_font=dict(color="#EF4444", size=10)
    )

    # Sensor Trend Line
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["ppm"],
            mode="lines+markers",
            name="Air Quality Gas Telemetry (PPM)",
            line=dict(color="#00F5A0", width=3, shape="spline"),
            marker=dict(size=6, color="#00D9F5", line=dict(color="#090D16", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(0, 245, 160, 0.12)",
            hovertemplate="<b>%{x}</b><br>Reading: <b>%{y:.1f} PPM</b><extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13, 19, 34, 0.85)",
        margin=dict(l=20, r=20, t=30, b=20),
        height=340,
        font=dict(family="Inter, sans-serif", color="#94A3B8"),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            tickangle=-30,
            showline=True,
            linecolor="rgba(255, 255, 255, 0.1)",
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="Gas Telemetry (PPM)", font=dict(size=12, color="#94A3B8")),
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            range=[250, max(650.0, float(df["ppm"].max()) + 60.0)],
            zeroline=False
        ),
        showlegend=False,
        hovermode="x unified"
    )

    return fig


def render_transaction_table_html(transactions: List, show_tenant_col: bool = True) -> str:
    """Format smart contract transaction logs into a futuristic responsive ledger table."""
    if not transactions:
        return "<p style='color: #64748B;'>No transactions recorded yet.</p>"

    rows_html = ""
    for tx in transactions[:30]:
        tx_dict = tx.to_dict() if hasattr(tx, "to_dict") else tx

        tx_type = tx_dict.get("tx_type", "EVENT")
        amt = tx_dict.get("amount", 0.0)
        tons = tx_dict.get("tons_co2", amt * CARBON_UNIT_TO_TONS)

        if tx_type == "MINT_REWARD":
            badge = '<span class="badge-mint">MINT REWARD</span>'
            amt_display = f'<span style="color: #00F5A0; font-weight: 700;">+{amt:.2f} ZC (+{tons:.2f} t)</span>'
        elif tx_type == "PENALTY_BURN":
            badge = '<span class="badge-fine">PENALTY BURN</span>'
            amt_display = f'<span style="color: #EF4444; font-weight: 700;">{amt:.2f} ZC ({tons:.2f} t)</span>'
        elif tx_type == "OFFSET_PURCHASE":
            badge = '<span class="badge-offset">OFFSET BUY</span>'
            amt_display = f'<span style="color: #00D9F5; font-weight: 700;">+{amt:.1f} ZC (+{tons:.1f} t)</span>'
        elif tx_type == "RETIRE_CREDIT":
            badge = '<span class="badge-mint">ESG RETIRE</span>'
            amt_display = f'<span style="color: #38BDF8; font-weight: 700;">{amt:.1f} ZC ({tons:.1f} t)</span>'
        elif tx_type == "ONBOARD_COMPANY":
            badge = '<span class="badge-tenant">ONBOARD</span>'
            amt_display = f'<span style="color: #C084FC; font-weight: 700;">+{amt:.1f} ZC</span>'
        else:
            badge = f'<span class="badge-mint">{tx_type}</span>'
            amt_display = f'<span>{amt:.2f} ZC</span>'

        ppm_val = tx_dict.get("ppm_recorded")
        ppm_str = f"{ppm_val:.1f} PPM" if ppm_val is not None else "—"
        tenant_str = tx_dict.get("company_id", "system")

        tenant_td = f"""<td style="padding: 10px 12px; font-family: 'JetBrains Mono', monospace; color: #C084FC;">{tenant_str}</td>""" if show_tenant_col else ""

        rows_html += f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.82rem;">
            <td style="padding: 10px 12px; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
                {tx_dict.get("timestamp", "")[-8:]}
            </td>
            <td style="padding: 10px 12px;">
                <span class="tx-hash-code">{tx_dict.get("tx_hash", "")}</span>
            </td>
            <td style="padding: 10px 12px; font-family: 'JetBrains Mono', monospace; color: #94A3B8;">
                #{tx_dict.get("block_number", "")}
            </td>
            {tenant_td}
            <td style="padding: 10px 12px;">
                {badge}
            </td>
            <td style="padding: 10px 12px;">
                {amt_display}
            </td>
            <td style="padding: 10px 12px; font-family: 'JetBrains Mono', monospace; color: #CBD5E1;">
                {ppm_str}
            </td>
            <td style="padding: 10px 12px; color: #94A3B8; max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                {tx_dict.get("notes", "")}
            </td>
        </tr>
        """

    tenant_th = """<th style="padding: 12px;">Tenant</th>""" if show_tenant_col else ""

    table_html = f"""
    <div style="overflow-x: auto; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(10, 15, 29, 0.5);">
        <table style="width: 100%; text-align: left; border-collapse: collapse;">
            <thead>
                <tr style="background: rgba(16, 24, 40, 0.85); border-bottom: 1px solid rgba(0, 245, 160, 0.2); color: #00F5A0; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em;">
                    <th style="padding: 12px;">Time</th>
                    <th style="padding: 12px;">TX Hash</th>
                    <th style="padding: 12px;">Block</th>
                    {tenant_th}
                    <th style="padding: 12px;">Action Type</th>
                    <th style="padding: 12px;">Carbon Delta (ZC / Tons)</th>
                    <th style="padding: 12px;">Gas (PPM)</th>
                    <th style="padding: 12px;">Execution Notes</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    return sanitize_html(table_html)
