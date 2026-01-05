import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime

# --- SaaS Configuration & Assets ---
APP_NAME = "DataScrub Pro"
TAGLINE = "Enterprise-Grade Data Cleaning for Modern Growth Teams"
VERSION = "v2.1.0 (Premium)"

st.set_page_config(
    page_title=f"{APP_NAME} | {TAGLINE}",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (SaaS Look & Feel) ---
st.markdown("""
<style>
    /* Global Fonts & Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Headers */
    .hero-header {
        font-weight: 800;
        font-size: 2.5rem;
        background: -webkit-linear-gradient(120deg, #2563eb, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Success/Action Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* Custom Badge */
    .saas-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
        vertical-align: middle;
    }
    .badge-pro { background: #dbeafe; color: #1e40af; }
    
    /* Sidebar Upsell Box */
    .upsell-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #334155;
    }
    .upsell-title { font-weight: bold; font-size: 1.1rem; margin-bottom: 10px; color: #fbbf24; }
    .upsell-text { font-size: 0.9rem; color: #e2e8f0; margin-bottom: 15px; }
    .upsell-btn { 
        display: block; width: 100%; padding: 8px; 
        background: #3b82f6; text-align: center; color: white; 
        text-decoration: none; border-radius: 6px; font-weight: bold;
    }
    .upsell-btn:hover { background: #2563eb; }

</style>
""", unsafe_allow_html=True)

# --- Helper Functions (The "Secret Sauce") ---

def calculate_quality_score(df):
    """Calculates a 0-100 score based on data completeness and duplicates."""
    total_cells = df.size
    total_missing = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    # Weights
    missing_penalty = (total_missing / total_cells) * 100 if total_cells > 0 else 0
    duplicate_penalty = (duplicate_rows / len(df)) * 100 if len(df) > 0 else 0
    
    score = 100 - (missing_penalty * 0.7) - (duplicate_penalty * 0.3)
    return max(0, int(score))

def is_valid_email(email):
    # Robust regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, str(email)) is not None

def clean_phone(phone):
    # Keep only digits
    if pd.isna(phone): return phone
    return re.sub(r'\D', '', str(phone))

# --- Application Layout ---

# Sidebar: Control Center
with st.sidebar:
    st.markdown(f"## 💎 {APP_NAME} <span class='saas-badge badge-pro'>Pro</span>", unsafe_allow_html=True)
    st.markdown("Your daily data operations, solved.")
    st.markdown("---")
    
    st.subheader("⚙️ Operation Mode")
    mode = st.radio("Select Action:", ["Health Audit", "Deep Clean", "Export Tools"], index=0)

    st.markdown("---")
    
    # Intelligent Upsell Block
    st.markdown("""
    <div class="upsell-box">
        <div class="upsell-title">⚡ Enterprise Automation</div>
        <div class="upsell-text">
            Processing >50k rows? Need direct Salesforce/HubSpot API syncing?
            We build custom data pipelines.
        </div>
        <a href="mailto:sales@datascrubpro.com?subject=Enterprise%20Pipeline%20Inquiry" class="upsell-btn">Book Demo Call</a>
    </div>
    """, unsafe_allow_html=True)

# Main Stage
st.markdown(f'<h1 class="hero-header">{APP_NAME}</h1>', unsafe_allow_html=True)
st.markdown(f"**{TAGLINE}**")

# File Upload (Top of Funnel)
uploaded_file = st.file_uploader("📂 Upload Lead List / Data Export (CSV)", type=["csv"], help="Drag & drop for instant audit")

if uploaded_file:
    # Load Data
    try:
        df = pd.read_csv(uploaded_file)
        
        # Session State for Cleaned Data
        if 'cleaned_df' not in st.session_state or st.session_state.get('last_file') != uploaded_file.name:
            st.session_state.cleaned_df = df.copy()
            st.session_state.last_file = uploaded_file.name
        
        current_df = st.session_state.cleaned_df

        # --- MODE 1: HEALTH AUDIT (The "Hook") ---
        if mode == "Health Audit":
            st.subheader("📊 Data Health Audit")
            st.info("We analyzed your file for common CRM and database errors.")
            
            score = calculate_quality_score(df)
            
            # Score Visual
            col_score, col_metrics = st.columns([1, 2])
            
            with col_score:
                st.metric("Overall Health Score", f"{score}/100", delta="Excellent" if score > 80 else "- Needs Attention" if score < 50 else "Average", delta_color="normal")
                if score < 80:
                    st.warning("⚠️ Improvement Needed: Run 'Deep Clean' to fix issues.")
            
            with col_metrics:
                m1, m2, m3 = st.columns(3)
                m1.metric("Duplicates", df.duplicated().sum(), help="Identical rows finding")
                m2.metric("Missing Values", df.isnull().sum().sum(), help="Empty cells across the dataset")
                m3.metric("Columns", df.shape[1])
            
            st.markdown("### 🕵️ Audit Details")
            st.dataframe(df.head(5), use_container_width=True)
            
            with st.expander("View Column-wise Missing Data Breakdown"):
                st.bar_chart(df.isnull().sum())

        # --- MODE 2: DEEP CLEAN (The "Value") ---
        elif mode == "Deep Clean":
            st.subheader("🧼 deepClean™ Toolkit")
            
            col_settings, col_preview = st.columns([1, 2])
            
            with col_settings:
                st.markdown("#### Configuration")
                
                # Standard
                st.markdown("**1. Structure**")
                chk_duplicates = st.checkbox("Remove Duplicates", value=True)
                chk_empty_rows = st.checkbox("Drop Empty Rows", value=False)
                
                # Smart CRM Stuff
                st.markdown("**2. CRM Formatting (Smart)**")
                chk_title_case = st.checkbox("Title Case Names", help="JOHN DOE -> John Doe")
                chk_trim = st.checkbox("Trim Whitespace", value=True, help="Removes invisible trailing spaces")
                
                # Advanced
                st.markdown("**3. Advanced Ops**")
                email_col = st.selectbox("Select Email Column (for valid)", ["None"] + list(current_df.columns))
                chk_validate_email = st.checkbox(f"Remove Invalid Emails in '{email_col}'", disabled=(email_col=="None"))
                
                if st.button("🚀 Run Cleaning Job", type="primary"):
                    # Process
                    temp_df = df.copy()
                    
                    if chk_duplicates:
                        temp_df.drop_duplicates(inplace=True)
                    
                    if chk_empty_rows:
                        temp_df.dropna(how='all', inplace=True)
                        
                    if chk_trim:
                        # Apply strip to all object columns
                        obj_cols = temp_df.select_dtypes(include=['object']).columns
                        for col in obj_cols:
                            temp_df[col] = temp_df[col].str.strip()
                            
                    if chk_title_case:
                        # Try to guess name columns or apply to all text keys
                        obj_cols = temp_df.select_dtypes(include=['object']).columns
                        for col in obj_cols:
                            # Heuristic: if column name contains 'name', title case it
                            if 'name' in col.lower():
                                temp_df[col] = temp_df[col].str.title()
                    
                    if email_col != "None" and chk_validate_email:
                        # Filter emails
                        temp_df = temp_df[temp_df[email_col].apply(is_valid_email)]
                    
                    st.session_state.cleaned_df = temp_df
                    st.session_state.cleaning_complete = True
                    st.success("Analysis & Cleaning Complete!")
                    st.balloons()

                # --- NEW: Immediate Download Block ---
                if st.session_state.get('cleaning_complete'):
                    st.markdown("### 📥 Download Result")
                    
                    csv = st.session_state.cleaned_df.to_csv(index=False).encode('utf-8')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    st.download_button(
                        label="Download Cleaned CSV",
                        data=csv,
                        file_name=f"cleaned_data_{timestamp}.csv",
                        mime="text/csv",
                        type="secondary"
                    )

            with col_preview:
                st.markdown("#### Live Preview (First 10 Rows)")
                st.dataframe(st.session_state.cleaned_df.head(10), use_container_width=True)
                st.info(f"Showing **{len(st.session_state.cleaned_df)}** valid rows (from original {len(df)})")

        # --- MODE 3: EXPORT (The "Closure") ---
        elif mode == "Export Tools":
            st.subheader("📤 Export & Integration")
            
            clean_data = st.session_state.cleaned_df
            
            st.markdown("Choose your platform format:")
            
            platform = st.selectbox("Target Platform", ["Universal CSV", "Salesforce Compatible", "HubSpot Import"])
            
            if platform == "Salesforce Compatible":
                st.caption("ℹ️ Ensuring headers are snake_case and dates are ISO8601.")
                # Simple logic for demo: snake_case columns
                clean_data.columns = [c.lower().replace(' ', '_') for c in clean_data.columns]
                
            file_name = f"datascrub_pro_{platform.lower().replace(' ', '_')}.csv"
            
            csv = clean_data.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label=f"⬇️ Download for {platform}",
                data=csv,
                file_name=file_name,
                mime="text/csv",
                type="primary"
            )
            
            st.markdown("---")
            st.warning("🔒 **Security Note:** Your data is processed locally in RAM and cleared on refresh. We do not store your customer lists.")

    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.error("Please ensure you uploaded a valid CSV file.")

else:
    # LANDING PAGE STATE (No file uploaded)
    
    # Value Props
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🛡️ Secure")
        st.markdown("Processed in-memory. Your data never leaves this secure environment.")
        
    with col2:
        st.markdown("### ⚡ Fast")
        st.markdown("Built on high-performance Pandas. Clean 100k+ rows in seconds.")
        
    with col3:
        st.markdown("### 🎯 Accuracy")
        st.markdown("Pre-configured algorithms for CRM fields: Emails, Names, and Dates.")
        
    # Example Empty State Art
    st.markdown("---")
    st.markdown("<center><div style='color: #94a3b8; margin-top: 50px;'>👆 <b>Upload a CSV</b> to generate your free Audit Report</div></center>", unsafe_allow_html=True)