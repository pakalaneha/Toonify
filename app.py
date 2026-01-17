import streamlit as st
import auth
import database
from datetime import date, timedelta
from image_processor import apply_cartoon_filter 
from watercolor_filter import apply_watercolor_style
from low_poly import apply_low_poly_style
from tiled_mosaic import apply_tiled_mosaic_style
import io
import os
import anime_filter 
import time
from io import BytesIO 
from PIL import Image
import string
import re
# --- Page Configuration ---
st.set_page_config(
    page_title="Toonify Me!",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Initialize Database ---
database.create_users_table()
database.create_history_table() 
# --- App State Management ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'
if 'processed_image_bytes' not in st.session_state:
    st.session_state['processed_image_bytes'] = None
if 'original_image_bytes' not in st.session_state:
    st.session_state['original_image_bytes'] = None
if 'original_mime_type' not in st.session_state:
    st.session_state['original_mime_type'] = None
if 'last_upload_bytes' not in st.session_state:
    st.session_state['last_upload_bytes'] = None

# State for Download Gate Modal
if 'show_download_gate' not in st.session_state:
    st.session_state['show_download_gate'] = False
# State to track if the current image has been paid for
if 'download_cleared' not in st.session_state:
    st.session_state['download_cleared'] = False

# Payment state
if 'payment_success' not in st.session_state:
    st.session_state['payment_success'] = False
if 'transaction_id' not in st.session_state:
    st.session_state['transaction_id'] = None
if 'payment_plan' not in st.session_state:
    st.session_state['payment_plan'] = 'Pro Plan - Monthly'
if 'payment_amount' not in st.session_state:
    st.session_state['payment_amount'] = '14.99'
if 'show_crypto_qr' not in st.session_state:
    st.session_state['show_crypto_qr'] = False
if 'show_upi_qr' not in st.session_state:
    st.session_state['show_upi_qr'] = False


# --- UI Styling ---
# In app.py, replace the entire load_css() function content with this:

# --- UI Styling ---
def load_css():
    """Injects custom CSS for a clean, light (white/blue) theme with animations and glowing gallery cards."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
        
        /* 1. Global & Streamlit Theme Overrides (White Background, Blue Accents) */
        * {
            font-family: 'Poppins', 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        /* Force White Background on ALL main Streamlit components */
        .main, .stApp, header, .st-emotion-cache-1cypcdp, .st-emotion-cache-16txto3 {
            background-color: #FFFFFF !important;
        }
        
        /* Set all general text to a dark color for contrast */
        h1, h2, h3, h4, p, div, label, span, .stMarkdown {
            color: #333333 !important;
        }
        
        /* Streamlit Headings - Use the Primary Blue */
        h1, h2, h3, h4 {
            color: #1E88E5 !important;
            font-weight: 700;
        }
        /* --- NEW SIZE FOR TOONIFY ME! HERO TITLE --- */
        .app-main-title {
            font-size: 5rem !important; /* FORCED LARGE SIZE */
            font-weight: 900 !important; 
            color: #0d47a1; 
            letter-spacing: -4px; 
            text-align: center;
            padding-bottom: 20px;
            text-shadow: 4px 4px 6px rgba(0, 0, 0, 0.2); 
        }

        /* On smaller screens (optional, but recommended for mobile) */
        @media (max-width: 768px) {
            .app-main-title {
                font-size: 4rem !important; /* Also needs !important for mobile */
                letter-spacing: -2px;
            }
        }
        
        /* 2. Navigation Bar (Clean White) */
        .fixed-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999; 
            padding: 10px 0;
            background-color: #FFFFFF;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08); 
        }
        
        .navbar-brand {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1E88E5 !important;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .navbar button[kind="primary"]:hover {
            transform: translateY(-2px);
        }
        
        /* 3. General Content Cards (Clean and Animated Lift) */
        .content-container, .pricing-card, .feature-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
            border: 1px solid #E0E0E0;
            transition: all 0.3s ease-in-out;
            color: #333333;
        }
        
        .content-container:hover, .pricing-card:hover, .feature-card:hover {
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
            transform: translateY(-4px);
        }
        
        /* 4. ***NEW: Gallery Card Glow Effect*** */
        
        /* Defines the animated glow */
        @keyframes blue-glow-pulse {
            0% { box-shadow: 0 0 10px rgba(30, 136, 229, 0.2), 0 0 0px rgba(30, 136, 229, 0.1); }
            50% { box-shadow: 0 0 15px rgba(30, 136, 229, 0.4), 0 0 5px rgba(30, 136, 229, 0.2); }
            100% { box-shadow: 0 0 10px rgba(30, 136, 229, 0.2), 0 0 0px rgba(30, 136, 229, 0.1); }
        }
        @keyframes slideInFromLeft {
            0% { opacity: 0; transform: translateX(-50px); }
            100% { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideInFromRight {
            0% { opacity: 0; transform: translateX(50px); }
            100% { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        .gallery-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 15px; /* Smaller padding for image content */
            border: 1px solid #E0E0E0;
            transition: all 0.3s ease-in-out;
            animation: blue-glow-pulse 3s infinite ease-in-out; /* Apply the glow */
            /* Ensure the image fits nicely */
            height: 100%; 
        }

        .gallery-card:hover {
            animation: none; /* Stop pulse on hover */
            box-shadow: 0 0 20px rgba(30, 136, 229, 0.6); /* Stronger glow on hover */
            transform: scale(1.03); /* Subtle scale up */
        }
        

        /* In app.py, inside the <style> block of def load_css(): */

/* In app.py, inside the <style> block of def load_css(): */

/* --- CRITICAL FIX: Image Sizing and Fitting (Using 1:1 Square Ratio) --- */

.gallery-image-box {
    height: 0 !important; 
    padding-bottom: 100% !important; /* Sets the aspect ratio to 1:1 (Perfect Square) */
    position: relative;
    overflow: hidden; 
    border-radius: 8px;
    margin-bottom: 15px; 
}

/* 1. Target the Streamlit wrapper div (st-emotion-cache-*) */
.gallery-image-box > div:first-child {
    width: 100% !important;
    height: 100% !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
}

/* 2. Target the final <img> tag inside the wrapper */
.gallery-image-box img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important; /* FORCES the image to fill the container, cropping excess */
    border-radius: 8px !important; 
    display: block !important;
}
/* -------------------------------------------------------------------- */
        
        /* 5. Hero Section 'How it Works' Text Animation */
        @keyframes subtle-blue-pulse {
            0% { text-shadow: 0 0 0px rgba(30, 136, 229, 0.2); }
            50% { text-shadow: 0 0 5px rgba(30, 136, 229, 0.4); }
            100% { text-shadow: 0 0 0px rgba(30, 136, 229, 0.2); }
        }

        .hero-title .accent {
            color: #1E88E5 !important;
            animation: subtle-blue-pulse 3s infinite ease-in-out;
        }

        /* Ensure primary buttons across the app have the lift animation */
        .stButton button[kind="primary"] {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-2px);
        }
        .price-box {
        background-color: #0d47a1; /* Darker blue background */
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: inline-block; /* Makes the box wrap tightly around the price */
        font-size: 1.5rem; /* Larger font size */
        font-weight: 700;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
        .feature-card-home, .step-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
            border: 1px solid #E0E0E0;
            transition: all 0.3s ease-in-out;
            color: #333333;
            /* Initial state for animation */
            opacity: 0;
        }

        .feature-card-home:hover, .step-card:hover {
            box-shadow: 0 8px 20px rgba(30, 136, 229, 0.2);
            transform: translateY(-5px); /* Stronger lift on hover */
        }

        /* Delay classes for staggered animation */
        .animated-card-0 { animation: slideInFromLeft 0.6s ease-out forwards; }
        .animated-card-1 { animation: slideInFromLeft 0.6s ease-out 0.15s forwards; }
        .animated-card-2 { animation: slideInFromLeft 0.6s ease-out 0.3s forwards; }
        .animated-card-3 { animation: slideInFromLeft 0.6s ease-out 0.45s forwards; }
        .animated-card-4 { animation: slideInFromRight 0.6s ease-out forwards; }
        .animated-card-5 { animation: slideInFromRight 0.6s ease-out 0.15s forwards; }
        .animated-card-6 { animation: slideInFromRight 0.6s ease-out 0.3s forwards; }
        .stButton button[kind="primary"] {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 4px 6px rgba(30, 136, 229, 0.3); /* Add subtle shadow to button */
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-3px); /* Increased lift */
            box-shadow: 0 6px 10px rgba(30, 136, 229, 0.5); /* Increased shadow */
        }
        .fotor-hero-title {
            font-size: 3.5rem !important; 
            font-weight: 900 !important; 
            color: #0d47a1 !important; /* Dark Blue from your original theme */
            letter-spacing: -2px; 
            text-align: left !important; /* CRITICAL: Left align the title */
            margin-bottom: 1.5rem;
            padding-top: 1rem;
            line-height: 1.1;
        }

        /* Image container styling for the right column */
        .hero-demo-home-container {
            display: flex;
            justify-content: center; /* Center the image in its column */
            align-items: center;
            padding: 20px;
        }

        /* The Demo Image itself */
        .hero-demo-home-image {
            max-width: 100%; /* Ensure it fits the column */
            height: auto;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease-in-out;
        }

        .hero-demo-home-image:hover {
            transform: scale(1.03); /* Subtle zoom on hover */
        }

        .stImage > div {
            max-height: 250px !important; 
            overflow: hidden !important; 
            
            /* Keep styling for the card look */
            background-color: var(--fotor-dark-accent) !important; 
            border-radius: 8px !important;
            padding: 5px !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5) !important;
            transition: transform 0.3s ease-in-out;
        }

        /* Ensures the image inside covers the fixed height container */
        .stImage img {
            height: 100% !important; 
            width: 100% !important; 
            object-fit: cover !important; 
            border-radius: 4px !important;
            display: block !important;
        }

        /* Retain the hover effect */
        .stImage > div:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.7);
        }

        /* --- Override CSS for Transform/App Page ONLY --- */
        .transform-image-reset {
            /* Set the maximum width for the image display area */
            max-width: 600px; /* Adjust this value (e.g., 500px, 700px) to your preferred size */
            margin: 0 auto; /* Center the image container */
        }

        /* This block UNDOES the fixed height and card styling inside the reset wrapper */
        .transform-image-reset .stImage > div {
            max-height: none !important; /* Remove fixed max height */
            overflow: visible !important; /* Restore normal overflow */
            padding: 0 !important; /* Remove padding/background for the clean look */
            background-color: transparent !important;
            box-shadow: none !important;
        }

        .transform-image-reset .stImage img {
            height: 500px !important; /* Restore auto height */
            width: 100% !important; /* Keep 100% width relative to the new max-width container */
            object-fit: contain !important; /* Restore natural scaling */
            border-radius: 4px !important;
        }
        .transform-comparison-area {
            /* DECREASED WIDTH: Shrink the total space for both images */
            max-width: 450px; 
            margin: 0 auto; /* Center the container horizontally */
        }

        /* This block UNDOES the fixed height and card styling ONLY for images inside the new wrapper */
        .transform-comparison-area .stImage > div {
            max-height: none !important; 
            overflow: visible !important; 
            padding: 0 !important; 
            background-color: transparent !important;
            box-shadow: none !important;
            border: none !important; 
            
            /* INCREASED HEIGHT: Forces the image containers to be taller */
            min-height: 300px; 
            display: flex; /* Helps center the image vertically */
            align-items: center; 
        }

        /* Ensures the image inside scales naturally within the column */
        .transform-comparison-area .stImage img {
            height: auto !important; 
            width: 100% !important; 
            object-fit: contain !important; 
            border-radius: 4px !important;
            border: 1px solid #E0E0E0; 
        }
        .stImage > div {
            max-height: 250px !important; 
            overflow: hidden !important; 
            /* ... other styling (background, border-radius, etc.) ... */
        }

        /* Ensures the image inside covers the fixed height container */
        .stImage img {
            height: 100% !important; 
            width: 100% !important; 
            object-fit: cover !important; 
            /* ... other styling ... */
        }

        /* --- Override CSS for Transform/App Page ONLY --- */
        /* NEW: Wrapper to constrain the image comparison area */
        .transform-image-wrapper {
            /* Set the maximum width and center it within the Streamlit column */
            max-width: 400px; /* Adjust this value (e.g., 400px, 500px) to your preferred size */
            margin: 0 auto; 
        }

        /* This block UNDOES the fixed height and card styling ONLY for images inside the wrapper */
        .transform-image-wrapper .stImage > div {
            max-height: none !important; /* Remove fixed max height */
            overflow: visible !important; /* Restore normal overflow */
            padding: 0 !important; /* Remove padding/background for the clean look */
            background-color: transparent !important;
            box-shadow: none !important;
        }

        .transform-image-wrapper .stImage img {
            height: auto !important; /* Restore auto height */
            width: 100% !important; /* Keep 100% width relative to the new max-width container */
            object-fit: contain !important; /* Restore natural scaling */
            border-radius: 4px !important;
        }
        /* --- ANIMATION KEYFRAMES for Hero Section --- */
            @keyframes slideInFromLeft {
            0% { transform: translateX(-100px); opacity: 0; }
            100% { transform: translateX(0); opacity: 1; }
        }

        @keyframes slideInFromRight {
            0% { transform: translateX(100px); opacity: 0; }
            100% { transform: translateX(0); opacity: 1; }
        }

        /* Base animation classes: Start Hidden and Apply Animation */
        .animated-hero-left {
            opacity: 0; /* Start hidden */
            animation: slideInFromLeft 1s ease-out 0.2s forwards; /* Play animation */
        }

        .animated-hero-right {
            opacity: 0; /* Start hidden */
            animation: slideInFromRight 1s ease-out 0.5s forwards; /* Staggered delay for image */
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

# --- Top Navigation Bar ---
def navigation_bar(placeholder):
    """Renders the top navigation bar into the placeholder."""
    with placeholder.container():
        st.markdown('<div class="navbar">', unsafe_allow_html=True)
        
        # Three column layout: Logo | Nav Links | Auth Buttons
        col1, col2, col3 = st.columns([1, 2, 1.2])

        with col1:
            st.markdown('<div class="navbar-brand">Toonify</div>', unsafe_allow_html=True)
        
        with col2:
            # Center navigation links
            if st.session_state.get('logged_in'):
                nav_cols = st.columns(4)
                if nav_cols[0].button("Home", use_container_width=True, key="nav_home"):
                    st.session_state.page = 'Home'
                    st.rerun()
                if nav_cols[1].button("Transform", use_container_width=True, key="nav_transform"):
                    st.session_state.page = 'App'
                    st.rerun()
                if nav_cols[2].button("Gallery", use_container_width=True, key="nav_gallery"):
                    st.session_state.page = 'Gallery'  # Placeholder
                    st.rerun()
                if nav_cols[3].button("Pricing", use_container_width=True, key="nav_pricing"):
                    st.session_state.page = 'Pricing'
                    st.rerun()
                # if nav_cols[4].button("About", use_container_width=True, key="nav_about"):
                #     st.session_state.page = 'Home'  # Scroll to About section
                #     st.rerun()
            else:
                nav_cols = st.columns(4)
                if nav_cols[0].button("Home", use_container_width=True, key="nav_home_guest"):
                    st.session_state.page = 'Home'
                    st.rerun()
                if nav_cols[1].button("Transform", use_container_width=True, key="nav_transform_guest"):
                    st.session_state.page = 'Login'
                    st.rerun()
                if nav_cols[2].button("Gallery", use_container_width=True, key="nav_gallery_guest"):
                    st.session_state.page = 'Gallery'
                    st.rerun()
                if nav_cols[3].button("Pricing", use_container_width=True, key="nav_pricing_guest"):
                    st.session_state.page = 'Pricing'
                    st.rerun()
                # if nav_cols[4].button("About", use_container_width=True, key="nav_about_guest"):
                #     st.session_state.page = 'Home'  # Scroll to About section
                #     st.rerun()
        
        with col3:
            # Right side auth buttons
            if st.session_state.get('logged_in'):
                auth_cols = st.columns(2)
                with auth_cols[0]:
                    if st.button("Profile", use_container_width=True, key="nav_profile"):
                        st.session_state.page = 'Profile'
                        st.rerun()
                with auth_cols[1]:
                    if st.button("Logout", use_container_width=True, key="nav_logout"):
                        st.session_state['logged_in'] = False
                        st.session_state['user_info'] = None
                        st.session_state['page'] = 'Home'
                        st.session_state['processed_image_bytes'] = None
                        st.session_state['original_image_bytes'] = None
                        st.rerun()
            else:
                auth_cols = st.columns(2)
                with auth_cols[0]:
                    if st.button("Sign In", use_container_width=True, key="nav_signin"):
                        st.session_state.page = 'Login'
                        st.rerun()
                with auth_cols[1]:
                    if st.button("Get Started", use_container_width=True, type="primary", key="nav_getstarted"):
                        st.session_state.page = 'Signup'
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


# --- Page Views ---
# --- Page Views ---
# --- Page Views ---
def show_home_page():
    # Paths for the Before/After images
    BEFORE_IMAGE_PATH = "gallery_assets/girl.png" 
    AFTER_IMAGE_PATH = "gallery_assets/cartoon_sample.png"

    st.markdown('<div class="content-container" style="padding-top: 2rem;">', unsafe_allow_html=True)

    # Use columns to split the Hero section: 3 parts for text, 2 parts for the image container
    col_text, col_image_container = st.columns([3, 2])
    
    with col_text:
        # WRAPPER FOR LEFT SLIDE-IN ANIMATION
        st.markdown('<div class="animated-hero-left">', unsafe_allow_html=True) 

        # ORIGINAL TITLE TEXT RESTORED
        st.markdown(
            """
            <h1 class="fotor-hero-title">
                Toonify Me! <span style='color: var(--fotor-primary-blue);'></span>
            </h1>
            """, 
            unsafe_allow_html=True
        )
        
        # ORIGINAL SUBTITLE TEXT RESTORED
        st.markdown("""
            <p style='font-size: 1.5rem; font-weight: 500; color: var(--fotor-text-light); margin-bottom: 30px; line-height: 1.4;'>
            Turn your everyday photos into stunning animated masterpieces. Experience true AI-powered art with a single click.
            </p>
        """, unsafe_allow_html=True)
        
        # FOTOR CTA Button
        if st.button("Toonify Your Photo", type="primary", key="home_hero_cta_fotor"):
            if st.session_state.get('logged_in'):
                st.session_state.page = 'App'
            else:
                st.session_state.page = 'Signup'
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True) # Close animated wrapper

    with col_image_container:
        # WRAPPER FOR RIGHT SLIDE-IN ANIMATION
        st.markdown('<div class="animated-hero-right">', unsafe_allow_html=True) 

        # --- BEFORE/AFTER SPLIT VIEW using nested columns ---
        col_before, col_after = st.columns(2)
        
        with col_before:
            st.markdown('<p style="text-align: center; font-weight: bold; color: var(--fotor-text-light);">Original</p>', unsafe_allow_html=True)
            st.image(
                BEFORE_IMAGE_PATH,
                caption="", 
                use_container_width=True 
            )
            
        with col_after:
            st.markdown('<p style="text-align: center; font-weight: bold; color: var(--fotor-text-light);">Cartoon</p>', unsafe_allow_html=True)
            st.image(
                AFTER_IMAGE_PATH,
                caption="", 
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True) # Close animated wrapper
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Rest of the home page content below the hero section ---

    # --- 2. FEATURES GRID (Animated Cards) ---
    st.markdown('<div style="margin: 3rem 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-bottom: 2rem; animation: slideInFromLeft 1s ease-out forwards;">Why Choose Toonify?</h2>', unsafe_allow_html=True)
    
    feature_cols = st.columns(4)
    features = [
        {"icon": "✨", "title": "AI-Powered Magic", "desc": "Advanced AI algorithms create stunning artistic styles instantly."},
        {"icon": "⚡", "title": "Lightning Fast", "desc": "Get your transformed images in seconds. Optimized for speed and performance."},
        {"icon": "🎨", "title": "Multiple Styles", "desc": "Pencil, Anime, Watercolor, Oil, and more creative effects to choose from."},
        {"icon": "⬇️", "title": "High Quality Output", "desc": "Download your creations in high resolution, perfect for printing or sharing."}
    ]
    
    for i, feature in enumerate(features):
        with feature_cols[i]:
            # Use new animated class and index for staggered delay
            st.markdown(f'''
                <div class="feature-card-home animated-card-{i}" style="min-height: 220px; text-align: center;">
                    <div style="font-size: 2.5rem; margin-bottom: 10px; color: #1E88E5 !important;">{feature["icon"]}</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #1E88E5; margin-bottom: 5px;">{feature["title"]}</div>
                    <div style="font-size: 0.95rem; color: #616161;">{feature["desc"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<hr style='border: none; border-top: 2px solid #E0E0E0;'>", unsafe_allow_html=True)

    # --- 3. HOW IT WORKS / ABOUT SECTION (Structured and Animated) ---
    st.markdown('<div style="margin: 3rem 0;">', unsafe_allow_html=True)
    
    # Title Row
    st.markdown('<h2 style="text-align: center; margin-bottom: 2rem; animation: slideInFromRight 1s ease-out forwards;">Simple Steps to Your Masterpiece</h2>', unsafe_allow_html=True)
    
    how_it_works_cols = st.columns(3)
    steps = [
        {"num": "1", "title": "Upload Your Photo", "desc": "Select a clear image (JPG or PNG) from your device.", "icon": "📤"},
        {"num": "2", "title": "Choose a Style", "desc": "Pick your favorite effect: Cartoon, Sketch, Anime, or Painting.", "icon": "✨"},
        {"num": "3", "title": "Download & Share", "desc": "Review the result and download your high-quality artistic creation.", "icon": "⬇️"}
    ]
    
    for i, step in enumerate(steps):
        with how_it_works_cols[i]:
            # Use new animated class and index for staggered delay
            st.markdown(f'''
                <div class="step-card animated-card-{i+4}" style="text-align: center; padding: 2rem 1.5rem; min-height: 250px;">
                    <div style="font-size: 2rem; font-weight: 800; color: #1E88E5; margin-bottom: 10px;">{step["num"]}</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #333333; margin-bottom: 0.75rem;">{step["title"]}</div>
                    <div style="font-size: 1rem; color: #616161; line-height: 1.6;">{step["desc"]}</div>
                    <div style="font-size: 3rem; margin-top: 15px; color: #1E88E5 !important;">{step["icon"]}</div>
                </div>
            ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<hr style='border: none; border-top: 2px solid #E0E0E0;'>", unsafe_allow_html=True)

    # --- FINAL CTA (Animated) ---
    st.markdown('<div style="text-align: center; margin: 4rem 0 2rem; animation: fadeIn 1.2s ease-out 0.2s forwards; opacity: 0;">', unsafe_allow_html=True)
    st.markdown('<h2 style="margin-bottom: 1.5rem;">Ready to See the Magic?</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.1rem; color: #616161; margin-bottom: 2rem;">Sign up now and transform your first photo for free!</p>', unsafe_allow_html=True)
    
    col_cta_final1, col_cta_final2, col_cta_final3 = st.columns([1.5, 1, 1.5])
    with col_cta_final2:
        if st.button("Create My Account", type="primary", use_container_width=True, key="home_final_cta"):
            if st.session_state.get('logged_in'):
                st.session_state.page = 'App'
            else:
                st.session_state.page = 'Signup'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Gallery Page ---
# In app.py, replace the existing show_gallery_page() function with this:

# --- Gallery Page ---
# --- Gallery Page ---
# In app.py, replace the entire def show_gallery_page(): function with this:

# --- Gallery Page ---
# In app.py, replace the entire def show_gallery_page(): function with this:

# --- Gallery Page ---
# --- Gallery Page ---
def show_gallery_page():
    # Use padding for fixed nav space
    st.markdown('<div style="padding-top: 70px;">', unsafe_allow_html=True) 
    st.header("✨ Filter Gallery Showcase")
    st.markdown("""
        <p style='color: #616161; font-size: 1.1rem;'>
        Browse the artistic styles your photos can be transformed into!
        </p>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # --- GALLERY DATA ---
    GALLERY_ASSETS_DIR = "gallery_assets"
    
    gallery_data = [
        {"title": "Classic Cartoon", "caption": "The main bold outline style.", "file": "Classic_Cartoon.png"}, 
        {"title": "Anime Style", "caption": "Vibrant, Japanese animation aesthetic.", "file": "cartoon_sample.png"}, 
        {"title": "Pencil Sketch", "caption": "Detailed black and white drawing.", "file": "Pencil_Sketch.png"},
        {"title": "Oil Painting", "caption": "Thick, expressive brush strokes.", "file": "Oil_Painting.png"},
        {"title": "Watercolor Painting", "caption": "Soft, diffused colors and wet edges.", "file": "Watercolor.png"},
        {"title": "Low-Poly Art", "caption": "Modern geometric triangle design.", "file": "Low_poly_art.png"},
        {"title": "Tiled Mosaic", "caption": "Clean, simplified square tiles.", "file": "Tiled_mosaic.png"},
        # {"title": "Placeholder Style", "caption": "Your next filter idea!", "file": "anime_sample.png"}, 
    ]
    # ---------------------------------------------

    # Display items in a responsive grid (3 columns wide)
    num_columns = 3
    
    # Use st.columns() to create a new row of columns for every batch of 3 images
    # We will iterate through the data and assign content to the columns in sequence.
    
    cols = st.columns(num_columns)
    
    for i, item in enumerate(gallery_data):
        # Determine the current column (0, 1, or 2)
        current_col_index = i % num_columns
        
        with cols[current_col_index]:
            
            # Use a Streamlit container for visual separation instead of custom HTML cards
            with st.container(border=True): 
                st.subheader(item["title"])
                
                image_path = os.path.join(GALLERY_ASSETS_DIR, item['file'])
                
                try:
                    from PIL import Image
                    
                    # Load and display the image
                    sample_image = Image.open(image_path)
                    
                    # NOTE: use_container_width=True ensures the image scales to the column width
                    # and will align neatly in batches.
                    st.image(sample_image, use_container_width=True) 
                    
                except FileNotFoundError:
                    st.warning(f"Image not found: {item['file']}")
                except Exception as e:
                    st.error(f"Error loading image {item['file']}: {e}")
                
                st.caption(item["caption"])
                
                # Add a 'Try Now' button
                if st.button(f"Try {item['title'].split()[0]}", key=f"gallery_try_{i}", use_container_width=True, type="primary"):
                    st.session_state.page = 'App'
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)   
def show_login_page():
    """Displays the login form."""
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.header("Welcome Back!")
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="youremail@example.com")
        password = st.text_input("Password", type="password", placeholder="********")
        submitted = st.form_submit_button("Login")

        if submitted:
            result = auth.login_user(email, password)
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = result
                st.session_state['page'] = 'App'
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def check_field(value, field_name, min_len=1, max_len=None):
    """Checks if a field is not empty and meets length requirements."""
    if not value or len(str(value).strip()) < min_len:
        return f"{field_name} is required."
    if max_len and len(str(value).strip()) > max_len:
        return f"{field_name} is too long (max {max_len} characters)."
    return "" # Success

def is_valid_email_structure(email: str) -> str:
    """Checks email against format and length constraints."""
    
    # 1. Total Length Constraint (RFC 5321: Max 254 characters)
    if len(email) > 254:
        return "Email address is too long (max 254 characters)."

    # 2. Format Constraint (@ and . position rules)
    # Allows alphanumeric, dots, underscores, percents, pluses, and hyphens
    # Enforces the single '@' and a domain.tld structure
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.fullmatch(email_pattern, email):
        return "Invalid email format. Must be in the form 'user@domain.com'."
    
    return "" # Empty string means success

def check_password_strength(password: str) -> list:
    """Checks password against a set of strength rules."""
    errors = []
    # Constraint 1: Minimum length
    if len(password) < 8:
        errors.append("Must be at least 8 characters long.")
    # Constraint 2: Uppercase letter
    if not re.search(r'[A-Z]', password):
        errors.append("Must contain at least one uppercase letter.")
    # Constraint 3: Lowercase letter
    if not re.search(r'[a-z]', password):
        errors.append("Must contain at least one lowercase letter.")
    # Constraint 4: Digit
    if not re.search(r'\d', password):
        errors.append("Must contain at least one digit (0-9).")
    # Constraint 5: Special character
    if not re.search(r'[^a-zA-Z0-9\s]', password):
        errors.append("Must contain at least one special character (e.g., !@#$%^&*).")
    return errors

# =========================================================================
# --- STREAMLIT PAGE FUNCTION ---
# =========================================================================

def show_signup_page():
    """Displays the detailed signup form with all validation constraints."""
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.header("Create Your Toonify Account")
    
    # A list to collect all validation errors
    validation_errors = []

    with st.form("signup_form"):
        st.write("#### Account Credentials")
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username*")
            password = st.text_input("Password*", type="password")
        with col2:
            email = st.text_input("Email*")
            confirm_password = st.text_input("Confirm Password*", type="password")

        st.write("---")
        st.write("#### Personal Details")
        col3, col4 = st.columns(2)
        with col3:
            first_name = st.text_input("First Name*")
            # Age Constraint: User must be at least 13 years old
            dob = st.date_input("Date of Birth*",
                                min_value=date.today() - timedelta(days=365*100),
                                max_value=date.today() - timedelta(days=365*13))
        with col4:
            last_name = st.text_input("Last Name*")
            gender = st.selectbox("Gender*", ["Male", "Female", "Other", "Prefer not to say"])

        phone_number = st.text_input("Phone Number (Optional)")
        address = st.text_area("Address (Optional)")

        submitted = st.form_submit_button("Create Account")

        if submitted:
            # --- 1. Basic Required Field Checks (including length) ---
            validation_errors.append(check_field(username, "Username", min_len=3, max_len=20))
            validation_errors.append(check_field(password, "Password"))
            validation_errors.append(check_field(email, "Email"))
            validation_errors.append(check_field(first_name, "First Name"))
            validation_errors.append(check_field(last_name, "Last Name"))
            validation_errors.append(check_field(gender, "Gender"))
            validation_errors.append(check_field(dob, "Date of Birth"))

            # --- 2. Email Constraints (Format and Length) ---
            email_error = is_valid_email_structure(email)
            if email_error:
                validation_errors.append(f"Email: {email_error}")

            # --- 3. Password Match and Strength Constraints ---
            if password != confirm_password:
                validation_errors.append("Passwords do not match!")
            
            # Check strength only if password is not empty and matches (to avoid double errors)
            if password and password == confirm_password:
                strength_errors = check_password_strength(password)
                if strength_errors:
                    validation_errors.append("Password is too weak. Please fix the following issues:")
                    # Append each strength error as a sub-bullet point
                    validation_errors.extend([f" - {err}" for err in strength_errors])
            
            # --- 4. Final Error Display ---
            # Filter out empty strings from successful checks
            final_errors = [err for err in validation_errors if err and err != " - "]

            if final_errors:
                st.error("Please correct the following errors before creating your account:")
                # Use st.markdown to display the sub-bullet points for password strength
                for err in final_errors:
                    st.markdown(f"- {err}")
                return # Stop execution if there are errors

            # --- 5. Proceed with Signup (No Errors) ---
            st.success("Account created successfully! You can now log in.")
            
            # NOTE: You should uncomment the actual signup logic below:
            # message = auth.signup_user(
            #     username, email, password, first_name,
            #     last_name, address, dob, gender, phone_number
            # )
            # if "Success" in message:
            #     st.success(message)
            #     st.session_state['page'] = 'Login'
            #     st.session_state['logged_in'] = False # Ensure user has to log in
            #     st.rerun()
            # else:
            #     st.error(message)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Pricing Page ---
# --- Pricing Page ---
def show_pricing_page():
    st.markdown('<div style="padding-top: 70px;">', unsafe_allow_html=True)
    st.header("💸 Credit Packs & Pricing")
    st.markdown("""
        <p style='font-size: 1.1rem; color: #444;'>
        Purchase credits to transform your photos. Each filter application costs **1 credit**.
        </p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    pricing_data = [
        # Prices converted to USD for demo
        {"name": "Starter Pack", "credits": 25, "price": "$1.99", "best_value": False},
        {"name": "Creator Pack", "credits": 75, "price": "$4.99", "best_value": True},
        {"name": "Pro Pack", "credits": 200, "price": "$9.99", "best_value": False},
    ]
    
    cols = st.columns(3)
    
    for i, pack in enumerate(pricing_data):
        with cols[i]:
            card_class = "pricing-card" if not pack['best_value'] else "pricing-card best-value-glow"
            
            # Custom styling for the best value badge
            best_value_badge = ""
            if pack['best_value']:
                best_value_badge = '<div style="background-color: #FFC107; color: #333; padding: 5px 10px; border-radius: 6px; font-weight: 700; position: absolute; top: -15px; right: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">BEST VALUE</div>'
            
            st.markdown(f'<div class="{card_class}" style="position: relative;">', unsafe_allow_html=True)
            st.markdown(best_value_badge, unsafe_allow_html=True)
            
            st.markdown(f"<h2>{pack['name']}</h2>", unsafe_allow_html=True)
            
            # --- START: Price in Box ---
            st.markdown(f'<div class="price-box">{pack["price"]}</div>', unsafe_allow_html=True)
            # --- END: Price in Box ---

            st.markdown(f"<h3>Includes {pack['credits']} Credits</h3>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("* Ideal for casual users")
            st.markdown("* No expiry")
            
            if st.session_state.get('logged_in'):
                if st.button(f"Purchase {pack['name']}", key=f"buy_{i}", use_container_width=True, type="primary"):
                    st.session_state.page = 'Payment_Demo'
                    st.session_state.selected_pack = pack # Store pack for payment page
                    st.rerun()
            else:
                st.markdown("""
                <div style="margin-top: 20px; padding: 10px; background-color: #E3F2FD; border-radius: 6px; text-align: center;">
                    **Log in to purchase**
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Payment / Upgrade Page (Redesigned to match template) ---
# --- Payment / Upgrade Page (Complete Code with Dynamic Flows and Credit Update Fix) ---
def show_upgrade_page():
    # Initialize dynamic payment states
    if 'show_upi_qr' not in st.session_state:
        st.session_state['show_upi_qr'] = False
    if 'show_netbanking_redirect' not in st.session_state:
        st.session_state['show_netbanking_redirect'] = False
        
    st.markdown('<div style="padding-top: 70px;">', unsafe_allow_html=True)
    st.header("💳 Secure Checkout (Demo Gateway)")

    # --- Setup and Data Check ---
    pack = st.session_state.get('selected_pack') 
    user_info = st.session_state.get('user_info')

    if not pack or not user_info:
        st.warning("No credit pack selected or user info missing. Redirecting to pricing...")
        time.sleep(1) 
        st.session_state.page = 'Pricing'
        st.rerun()
        return

    st.markdown(f"**You are purchasing:** **{pack['name']}**")
    st.markdown(f"**Price:** {pack['price']} | **Credits:** {pack['credits']}")
    st.markdown("---")
    
    st.subheader("Select Payment Method")
    st.warning("⚠️ This is a DEMO. No actual transaction will occur. Payment success is simulated.")

    # --- Payment Success Handler ---
    def handle_payment_success():
        # NOTE: Assumes database.add_credits_to_user and database.get_user_data_by_id are imported
        user_id = user_info['id']
        credits_to_add = pack['credits']
        
        with st.spinner(f"Processing {pack['name']} purchase..."):
            time.sleep(1.5) 

        # --- IMPORTANT: REAL DATABASE TRANSACTION LOGIC ---
        
        # 1. Update the database credits using your existing function
        success = database.add_credits_to_user(user_id, credits_to_add)
        
        if success:
            
            # 2. Retrieve the fresh user data from the database
            # This ensures we get the *actual* new credit count
            new_user_info = database.get_user_data_by_id(user_id)
            
            if new_user_info:
                # 3. Update the session state with the fresh data
                st.session_state['user_info'] = new_user_info
                
                st.success(f"🎉 Purchase Successful! {credits_to_add} credits added to your account. Your new balance is: {new_user_info['credits']}")
                st.balloons()

                # Reset states and redirect to Profile
                st.session_state.show_upi_qr = False
                st.session_state.show_netbanking_redirect = False
                st.session_state.page = 'Profile'
                st.rerun()
            else:
                # Critical error: Database updated, but fetching the user record failed.
                st.error("Purchase succeeded, but failed to retrieve updated user data from the database. Please refresh the page or check the logs.")
        else:
            # Database update failed (e.g., connection error, rollback occurred)
            st.error("Purchase failed due to a database error while adding credits. Please try again.")


    # --- Tabbed Payment Interface ---
    card_tab, upi_tab, netbanking_tab = st.tabs(["💳 Card", "📲 UPI", "🏦 Net Banking"])
    
    # 1. CARD TAB
    with card_tab:
        st.markdown("##### Credit / Debit Card")
        with st.form("card_payment_form"):
            card_number = st.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX", max_chars=16, help="Enter 16 digits (Demo Only)")
            col_exp, col_cvv = st.columns(2)
            with col_exp:
                card_expiry = st.text_input("Expiry (MM/YY)", placeholder="MM/YY", max_chars=5)
            with col_cvv:
                card_cvv = st.text_input("CVV", placeholder="XXX", type="password", max_chars=3)
            
            name_on_card = st.text_input("Name on Card", value=f"{user_info['first_name']} {user_info['last_name']}")
            
            submitted_card = st.form_submit_button(f"Pay {pack['price']} via Card", type="primary", use_container_width=True)

            if submitted_card:
                if len(card_number) < 16 or len(card_expiry) < 5 or len(card_cvv) < 3:
                    st.error("Please enter valid (demo) card details.")
                else:
                    handle_payment_success()


    # 2. UPI TAB (Dynamic QR Code)
    with upi_tab:
        st.markdown("##### UPI (Unified Payments Interface)")
        st.info(f"Payment Amount: **{pack['price']}**")

        # --- View 1: UPI ID Entry and QR Generation Button (Initial View) ---
        if not st.session_state.show_upi_qr:
            with st.form("upi_id_form"):
                upi_id = st.text_input("Enter UPI ID", placeholder="yourname@bank", key="upgrade_upi_id_input")

                col_submit, col_qr_gen = st.columns(2)
                
                with col_submit:
                    if st.form_submit_button(f"Pay {pack['price']} via UPI ID", type="primary", use_container_width=True):
                        if upi_id:
                            handle_payment_success() 
                        else:
                            st.error("Please enter a UPI ID to proceed.")

                with col_qr_gen:
                    if st.form_submit_button("Generate QR Code", type="secondary", use_container_width=True):
                        st.session_state.show_upi_qr = True
                        st.rerun() 
        
        # --- View 2: QR Code Display and Payment Confirmation (After 'Generate' click) ---
        else:
            st.warning("Please scan the code below. Do not refresh this page after scanning.")
            
            # Mock QR Code Image Placeholder
            st.image(
                "gallery_assets/sampleqr.jpg", 
                caption=f"Scan to Pay {pack['price']} to TOONIFY@DEMO",
                width=250
            )
            
            st.markdown("---")
            
            col_paid, col_back = st.columns(2)
            
            with col_paid:
                if st.button("I have paid (Simulate Success)", key="confirm_qr_pay", type="primary", use_container_width=True):
                    handle_payment_success() 

            with col_back:
                if st.button("Pay via UPI ID (Go Back)", key="go_back_to_upi_id", use_container_width=True):
                    st.session_state.show_upi_qr = False
                    st.rerun() 


    # 3. NET BANKING TAB (Dynamic Redirection)
    with netbanking_tab:
        st.markdown("##### Net Banking / Bank Transfer")
        st.info(f"Payment Amount: **{pack['price']}**")

        # --- View 1: Select Bank (Initial View) ---
        if not st.session_state.show_netbanking_redirect:
            with st.form("netbanking_select_form"):
                selected_bank = st.selectbox(
                    "Select Your Bank", 
                    ["HDFC Bank", "ICICI Bank", "Axis Bank", "State Bank of India", "Others"], 
                    key="upgrade_bank_select"
                )
                
                if st.form_submit_button(f"Proceed to {selected_bank}", type="primary", use_container_width=True):
                    st.session_state.show_netbanking_redirect = True
                    st.rerun()
        
        # --- View 2: Simulated Bank Login Screen (After 'Proceed' click) ---
        else:
            st.warning("Redirecting to Bank... (Simulated Bank Login Screen)")
            
            # Simulated Bank Login Form Look
            st.markdown(
                f"""
                <div style='border: 1px solid #ffcc00; padding: 20px; margin-top: 15px; background-color: #fffacd; border-radius: 5px;'>
                    <h5 style='color: #856404;'>{st.session_state.get("upgrade_bank_select", "Your Bank")} Portal Login</h5>
                    <p style='font-size: 0.9rem; color: #856404;'>Enter demo credentials to authorize payment of {pack['price']}.</p>
                    <input type="text" placeholder="Username" style="width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px;">
                    <input type="password" placeholder="Password" style="width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px;">
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown("---")
            
            col_paid, col_back = st.columns(2)
            
            with col_paid:
                if st.button("Simulate Bank Login & Pay", key="confirm_bank_pay", type="primary", use_container_width=True):
                    handle_payment_success() 
            
            with col_back:
                if st.button("Cancel Redirection", key="go_back_to_bank_select", use_container_width=True):
                    st.session_state.show_netbanking_redirect = False
                    st.rerun() 


    st.markdown("---")
    if st.button("Cancel & Back to Pricing", use_container_width=True):
        st.session_state.page = 'Pricing'
        st.session_state.show_upi_qr = False
        st.session_state.show_netbanking_redirect = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def check_password_strength(password):
    """Checks password against common strength rules (lower, upper, number, special)."""
    min_length = 8
    errors = []

    if len(password) < min_length:
        errors.append(f"Must be at least {min_length} characters long.")
    if not any(c.islower() for c in password):
        errors.append("Must contain at least one lowercase letter.")
    if not any(c.isupper() for c in password):
        errors.append("Must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        errors.append("Must contain at least one number.")
    
    # Define common special characters (using string.punctuation)
    special_chars = string.punctuation
    if not any(c in special_chars for c in password):
        errors.append("Must contain at least one special character (e.g., !@#$%^&*)")

    return errors
# --- Download Gating Modal Function ---
def show_download_gate_modal():
    """Modal to prompt non-premium users to upgrade or buy credits for download."""
    
    user = st.session_state['user_info']
    current_credits = user.get('credits', 0)
    COST_PER_DOWNLOAD = 1
    
    with st.container():
        st.header("🛑 Download Locked! 🛑")
        st.warning("You must pay to download the high-resolution image.")
        
        st.write("---")

        # --- PATH A: User has credits (Use existing credit) ---
        if current_credits >= COST_PER_DOWNLOAD:
            st.subheader("Option 1: Use 1 Existing Credit")
            st.info(f"You have **{current_credits}** credits. Use **1 credit** to unlock this download.")
            
            if st.button(f"Use 1 Credit to Download", key="use_credit_button", use_container_width=True, type="primary"):
                user_id = user['id']
                if database.deduct_credit_from_user(user_id, COST_PER_DOWNLOAD):
                    # Refetch user data to update the whole session state correctly
                    updated_user = database.get_user_by_email(user['email'])
                    st.session_state['user_info'] = updated_user
                    
                    st.session_state['download_cleared'] = True 
                    st.session_state['show_download_gate'] = False 
                    st.toast("Credit used! Download enabled. Click the button below.")
                    st.rerun() 
                else:
                    st.error("Error deducting credit. Please try again.")
            st.write("---")
        
        # --- PATH B: User needs to buy the single credit now (Inline Mock Payment) ---
        else:
            st.subheader("Option 1: Pay $1.00 for this Download")
            st.info("Purchase a single credit now to unlock the image. This payment immediately clears the download.")
            
            # --- NEW: Enhanced Payment Gateway Interface for Single Purchase ---
            card_tab_single, upi_tab_single, netbanking_tab_single = st.tabs(["💳 Card", "📲 UPI", "🏦 Net Banking"])
            
            # Function to handle single payment success logic
            def handle_single_payment_success():
                with st.spinner("Processing payment and unlocking image..."):
                    time.sleep(2) 
                
                st.session_state['download_cleared'] = True 
                st.session_state['show_download_gate'] = False 
                
                processed_bytes = st.session_state.get('processed_image_bytes')
                
                if processed_bytes:
                    st.balloons()
                    st.success("✅ Payment successful! The image is now unlocked. Please click the **Download** button in the main app window.")
                    st.rerun() 
                else:
                    st.error("Payment successful, but processed image data was not found. Please re-process and try again.")
                    st.session_state['download_cleared'] = False
                    st.rerun()

            with card_tab_single:
                st.markdown("##### Credit / Debit Card")
                with st.form("mock_single_credit_card_payment", clear_on_submit=False):
                    card_number = st.text_input(
                        "Card Number", 
                        value="4111 1111 1111 1111", 
                        max_chars=19, 
                        key="single_card_num_new"
                    )
                    
                    col_exp, col_cvc = st.columns(2)
                    with col_exp:
                        st.text_input("Expiry (MM/YY)", value="12/28", max_chars=5, key="single_exp_new")
                    with col_cvc:
                        st.text_input("CVC", type="password", value="123", max_chars=3, key="single_cvc_new")
                    
                    submitted = st.form_submit_button("Pay $1.00 & Download", type="primary", use_container_width=True)

                    if submitted:
                        if card_number.replace(' ', '') == "4111111111111111":
                            handle_single_payment_success()
                        else:
                            st.error("❌ Payment Failed. The card number provided was declined by the demo gateway.")

            with upi_tab_single:
                st.markdown("##### UPI Payment")
                with st.form("mock_single_credit_upi_payment", clear_on_submit=False):
                    upi_id = st.text_input("Enter UPI ID", placeholder="yourname@bank", key="single_upi_new")
                    st.markdown(
                        "<p style='text-align: center; font-style: italic; color: gray;'>OR Scan this Dummy QR Code</p>", 
                        unsafe_allow_html=True
                    )
                    st.code("-----------------", language="text") 
                    
                    submitted = st.form_submit_button("Pay $1.00 & Download", type="primary", use_container_width=True)
                    
                    if submitted:
                        # Mock: UPI payment always succeeds if submitted
                        handle_single_payment_success()

            with netbanking_tab_single:
                st.markdown("##### Net Banking")
                with st.form("mock_single_credit_netbanking_payment", clear_on_submit=False):
                    st.selectbox(
                        "Select Your Bank", 
                        ["HDFC Bank", "ICICI Bank", "Axis Bank", "Others"], 
                        key="single_bank_select"
                    )
                    st.info("You will be redirected to your bank's portal for authentication (Simulated).")
                    
                    submitted = st.form_submit_button("Pay $1.00 & Download", type="primary", use_container_width=True)
                    
                    if submitted:
                        # Mock: Net Banking payment always succeeds if submitted
                        handle_single_payment_success()
            
            st.write("---")


        # --- PATH C: Buy Bulk Credits / Premium (Redirects) ---
        st.subheader("Option 2: Go Premium or Buy Bulk Credits")
        st.success("Go Premium for **Unlimited Downloads** or buy a credit bundle to save money.")
        
        col_prem, col_bulk = st.columns(2)
        with col_prem:
            if st.button("Go Premium ($4.99/mo)", key="go_premium_from_gate", use_container_width=True):
                st.session_state.page = 'Payment_Demo'
                st.session_state['show_download_gate'] = False 
                st.rerun()
        with col_bulk:
            if st.button("Buy Bulk Credits", key="buy_bulk_credits_from_gate", use_container_width=True):
                st.session_state.page = 'Payment_Demo'
                st.session_state['show_download_gate'] = False 
                st.rerun()

        if st.button("Close / Cancel", key="close_gate_button"):
            st.session_state['show_download_gate'] = False
            st.rerun()


def show_main_app():
    """The main application dashboard after a user logs in."""

    # -------------------------------------------------------------------
    # --- Payment Success Card Display (at the very top) ---
    # This card is persistent until the user clicks the button.
    # -------------------------------------------------------------------
    if st.session_state.get('payment_success_card_shown'):
        
        # Use a container with a border for a clear card-like presentation
        success_container = st.container(border=True)
        with success_container:
            st.success(f"**🎉 Payment Confirmed Successfully!**", icon="check")
            unlocked_filename = st.session_state.get('unlocked_filename', 'your high-resolution image')
            st.markdown(f"The file **`{unlocked_filename}`** is now available for download. **Click OK to proceed.**")
            
            # This button is what the user must click for the card to go away
            if st.button("Got It! Close Message", type="primary", key="dismiss_success_card"):
                # Remove the state flag to stop showing the card
                del st.session_state['payment_success_card_shown']
                st.rerun() 
                 
        st.divider() # Visual separator below the card
    # -------------------------------------------------------------------

    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.title("🖼️ Image Transformation Dashboard")
    st.write("Upload your image and select an effect to see the magic happen!")
    
    # Get user info and credit status
    user = st.session_state['user_info']
    user_id = user['id']
    is_premium = user.get('is_premium', False)
    current_credits = user.get('credits', 0)
    
    # ... (rest of your existing show_main_app function)
    
    if is_premium:
        st.success("You are a **PREMIUM** user. Transform and download without limits!")
    elif st.session_state.get('logged_in'):
        st.info(f"You have **{current_credits}** credits. A single download costs **1 credit**.")

    # NOTE: The code block for checking and showing 'show_download_gate_modal' is removed.
    
    # Reset processing state if a new file is uploaded
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="image_uploader")

    
    # 1. Handle new file upload and update session state
    if uploaded_file is not None:
        # Only update state if a *new* file is uploaded
        if uploaded_file.getvalue() != st.session_state.get('last_upload_bytes'):
            st.session_state['original_image_bytes'] = uploaded_file.getvalue()
            st.session_state['original_mime_type'] = uploaded_file.type 
            st.session_state['last_upload_bytes'] = uploaded_file.getvalue()
            st.session_state['processed_image_bytes'] = None 
            st.session_state['download_cleared'] = False # RESET DOWNLOAD STATUS for new image
            st.toast("Image uploaded successfully!")

    # 2. All processing logic now runs if the image data is in session state,
    # regardless of whether the `uploaded_file` object is None (after a rerun).
    if st.session_state.get('original_image_bytes'): 
        
        # Add all styles to the list (kept for consistency)
        styles = [ 
            "Pencil Sketch", 
            "Oil Painting", 
            "Anime",
            "Classic Cartoon",
            "Low poly art",
            "Watercolor",
            "Tiled mosaic"
        ]
        
        st.write("---")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_style = st.selectbox("Select Cartoon Style", styles, key="style_select")
            
            if st.button("Toonify Me!", use_container_width=True, key="toonify_button"):
                if st.session_state.get('original_image_bytes'):
                    with st.spinner(f"Applying '{selected_style}' effect..."):
                        try:
                            if selected_style == "Watercolor":
                                processed_bytes =apply_watercolor_style(
                                    st.session_state['original_image_bytes'],
                                )
                            elif selected_style == "Anime":
                                processed_bytes = anime_filter.apply_anime_style(
                                    st.session_state['original_image_bytes'],
                                    st.session_state['original_mime_type']
                                )
                            elif selected_style == "Low poly art":
                                processed_bytes = apply_low_poly_style(
                                    st.session_state['original_image_bytes'],
                                )
                            elif selected_style == "Tiled mosaic":
                                processed_bytes = apply_tiled_mosaic_style(
                                    st.session_state['original_image_bytes'],
                                )
                            else:
                                processed_bytes = apply_cartoon_filter(
                                    st.session_state['original_image_bytes'], 
                                    selected_style
                                )
                            
                            st.session_state['processed_image_bytes'] = processed_bytes
                            st.toast("Transformation complete! Preview below.")
                            
                        except Exception as e:
                            st.error(f"Error applying style: {e}")
                            st.session_state['processed_image_bytes'] = None
                        
                    st.rerun() 
            
        st.write("---")
        st.subheader("Results")
        
        # --- NEW WRAPPER TO CONSTRICT WIDTH AND CENTER THE SIDE-BY-SIDE VIEW ---
        st.markdown('<div class="transform-comparison-area">', unsafe_allow_html=True) 

        # Display comparison using the two columns (col_orig and col_proc)
        col_orig, col_proc = st.columns(2)

        with col_orig:
            st.markdown("<h4 style='text-align: center;'>Original Image</h4>", unsafe_allow_html=True)
            # Display from session state
            st.image(st.session_state['original_image_bytes'], caption='', use_container_width=True)

        with col_proc:
            st.markdown(f"<h4 style='text-align: center;'>{selected_style} Result</h4>", unsafe_allow_html=True)
            if st.session_state.get('processed_image_bytes'):
                st.image(st.session_state['processed_image_bytes'], caption='', use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True) # CLOSE COMPARISON AREA WRAPPER

        # --- DOWNLOAD GATING LOGIC (Place buttons below the comparison area) ---

        # Use a new set of columns to center the download buttons under the constrained images
        col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])

        with col_btn_center:
            if st.session_state.get('processed_image_bytes'):
                if is_premium or st.session_state['download_cleared']:
                    # PATH 1: Already paid (Premium or credit already deducted/bought) -> Show actual download button
                    st.download_button(
                        label=f"Download Full Image {'(UNLIMITED)' if is_premium else '(PAID & CLEARED)'}",
                        data=st.session_state['processed_image_bytes'],
                        file_name=f"toonify_{selected_style.replace(' ', '_')}.png", 
                        mime="image/png",
                        use_container_width=True,
                        type="primary"
                    )
                
                elif current_credits >= 1:
                    # PATH 2: User has credit -> Deduct credit on this click and then enable download
                    download_label = f"Finalize & Download (Use 1 of your {current_credits} Credit{'s' if current_credits > 1 else ''})"
                    
                    if st.button(download_label, use_container_width=True, type="primary", key="finalize_download_credit"):
                        # Now, the deduction happens *only* on button click
                        if database.deduct_credit_from_user(user_id, 1):
                            st.session_state['user_info']['credits'] -= 1 
                            st.session_state['download_cleared'] = True 
                            st.success("Transformation complete! 1 credit deducted. Please click the download button below.")
                            
                            # --- CRITICAL: SAVE TO HISTORY AFTER SUCCESS ---
                            current_style = st.session_state.get('style_select', 'Unknown Style')
                            original_file_name = uploaded_file.name if uploaded_file else "uploaded_file" 
                            processed_mime = "image/png"

                            if st.session_state.get('processed_image_bytes'):
                                database.save_transformation_history(
                                    user_id, 
                                    current_style, 
                                    st.session_state['processed_image_bytes'], 
                                    original_file_name, 
                                    processed_mime
                                )
                                st.rerun() 
                            else:
                                st.error("Database error or missing processed image data.")
                        else:
                            st.error("Transformation complete, but credit deduction failed. Check logs.")

                else:
                    # PATH 3: User has no credit -> Redirect to Pricing page
                    if st.button("Buy Credits to Download", use_container_width=True, type="primary"):
                        st.session_state['page'] = 'Pricing'
                        st.rerun()

            else:
                # Only show this warning if there's no processed image but an original image exists
                if st.session_state.get('original_image_bytes'):
                    st.warning("Click 'Toonify Me!' to process your image.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- Profile Page ---
def show_profile_page():
    st.markdown('<div style="padding-top: 70px;">', unsafe_allow_html=True)
    st.header("👤 Your Profile & History")
    
    user_info = st.session_state.get('user_info')
    
    if user_info:
        # Fetch fresh user data and ID (Database fetch remains for user_id)
        user_data = database.get_user_by_email(user_info['email'])
        
        # --- CRITICAL FIX START ---
        # 1. Get the credit balance directly from the SESSION STATE (user_info), 
        # which was updated during the successful payment simulation.
        current_credits = user_info.get('credits', 0)
        # --- CRITICAL FIX END ---
        
        if user_data:
            # Continue to get user_id from database if needed for history lookup
            user_id = user_data.get('id') 
        else:
            user_id = None
            
        st.markdown("---")

        # --- Profile Details & Credits Section ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # This metric now displays the correct, updated credit count
            st.metric(label="✨ **Current Credits**", value=f"{current_credits}")
            
            if st.button("Buy More Credits", use_container_width=True, type="primary"):
                st.session_state.page = 'Pricing'
                st.rerun()

        with col2:
            st.subheader("Account Details")
            st.write(f"**Username:** {user_info.get('username')}")
            st.write(f"**Email:** {user_info.get('email')}")
            st.write(f"**First Name:** {user_info.get('first_name', 'N/A')}")
            st.write(f"**Last Name:** {user_info.get('last_name', 'N/A')}")
            st.write(f"**Date of Birth:** {user_info.get('dob', 'N/A')}")
            st.write(f"**Phone:** {user_info.get('phone_number', 'N/A')}")
            st.write(f"**Address:** {user_info.get('address', 'N/A')}")
        
        # --- Transformation History Section ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🖼️ Transformation History")
        st.markdown("---")

        if user_id is not None:
            history_records = database.get_transformation_history(user_id)
            
            if history_records:
                st.info(f"Showing {len(history_records)} recent transformations.")
                
                # Display in a 3-column grid
                num_columns = 3
                cols = st.columns(num_columns)
                
                # NOTE: Ensure Image, BytesIO are imported (from PIL and io)
                try:
                    from PIL import Image
                    from io import BytesIO
                except ImportError:
                    st.error("Missing PIL or io import! Please check your app.py imports.")


                for i, record in enumerate(history_records):
                    with cols[i % num_columns]:
                        with st.container(border=True):
                            
                            image_bytes = record['processed_image_bytes']
                            
                            try:
                                # Convert BLOB (bytes) to PIL Image object for display
                                img_pil = Image.open(BytesIO(image_bytes))
                                
                                st.image(
                                    img_pil, 
                                    caption=f"Style: {record['style']} ({record['timestamp'].strftime('%Y-%m-%d %H:%M')})", 
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error displaying image ID {record['id']}.")
                                
            else:
                st.info("No transformation history found yet! Go to the App page to create your first toon.")
        
    else:
        st.warning("Please log in to view your profile.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- Main Application Router ---
# --- Main Application Router ---
def main():
    """Controls which page is displayed based on the session state."""
    
    # Load CSS first
    load_css()
    
    # Create a placeholder for the fixed navigation bar
    nav_placeholder = st.empty()
    navigation_bar(nav_placeholder) # Call the navigation bar function

    # -------------------------------------------------------------------
    # --- Payment Success Handler for Single Download Purchase ---
    # --- REPLACED st.experimental_get_query_params() with st.query_params ---
    # -------------------------------------------------------------------
    
    # st.query_params returns the query parameters from the URL
    payment_cleared = st.query_params.get('payment_cleared', None)
    unlocked_filename = st.query_params.get('filename', None)
    
    # Check if the payment success flag is present and the user is logged in
    if payment_cleared == 'True' and unlocked_filename and st.session_state.get('logged_in'):
        
        # 1. Set Session State flags 
        # Note: No st.toast or st.balloons, the persistent card will handle the notification.
        st.session_state['download_cleared'] = True           # Enables the final download button
        st.session_state['payment_success_card_shown'] = True # Triggers the display of the persistent card
        st.session_state['unlocked_filename'] = unlocked_filename
        
        # 2. Clean the URL parameters to prevent re-display on every page rerun
        # This is CRITICAL to ensure the success card only shows once after the redirect.
        st.query_params.clear()
        
        # 3. Force navigation to the 'App' page and rerun to process new state.
        st.session_state['page'] = 'App'
        st.rerun() 
    # -------------------------------------------------------------------

    # Page content is rendered based on the state
    page = st.session_state.get('page', 'Home')
    
    if page == 'Home':
        show_home_page()
    elif page == 'Login':
        show_login_page()
    elif page == 'Signup':
        show_signup_page()
    # NEW: Handle payment page
    elif page == 'Gallery':
        show_gallery_page()
    elif page == 'Pricing':
        show_pricing_page()
    elif page == 'Payment_Demo' and st.session_state.get('logged_in'):
        show_upgrade_page()
    elif page == 'App' and st.session_state.get('logged_in'):
        show_main_app()
    elif page == 'Profile' and st.session_state.get('logged_in'):
        show_profile_page()
    else:
        # Default to home page if state is invalid or user is not logged in for protected pages
        if page in ['App', 'Profile', 'Payment_Demo']:
            st.session_state.page = 'Home'
            st.rerun()
        else:
            show_home_page()

if __name__ == "__main__":
    main()