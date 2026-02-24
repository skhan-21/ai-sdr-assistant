import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import json

# Page configuration
st.set_page_config(page_title="AI SDR Assistant", layout="wide")

# Initialize client
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OPENAI_API_KEY not found. Please set it in your environment.")
        st.stop()
    return OpenAI(api_key=api_key)

client = get_openai_client()

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

def validate_inputs(company_name, prospect_name, industry, company_summary):
    """Validate user inputs"""
    if not company_name.strip():
        st.warning("⚠️ Company Name is required")
        return False
    if not prospect_name.strip():
        st.warning("⚠️ Prospect Name is required")
        return False
    if not industry.strip():
        st.warning("⚠️ Industry is required")
        return False
    if not company_summary.strip():
        st.warning("⚠️ Company Description is required")
        return False
    return True

def generate_outreach(company_name, prospect_name, industry, company_summary):
    """Generate outreach content using OpenAI"""
    try:
        prompt = f"""
        You are a high performing SDR.

        Write:
        1. A personalised cold email
        2. A 20 second call opener
        3. A LinkedIn message

        Prospect: {prospect_name}
        Company: {company_name}
        Industry: {industry}
        Description: {company_summary}

        Keep it concise and commercial.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ Error generating content: {str(e)}")
        return None

def save_to_history(company_name, prospect_name, industry, content):
    """Save generated content to history"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "company_name": company_name,
        "prospect_name": prospect_name,
        "industry": industry,
        "content": content
    }
    st.session_state.history.append(entry)

def export_history():
    """Export history as JSON"""
    if not st.session_state.history:
        st.warning("⚠️ No history to export")
        return None
    return json.dumps(st.session_state.history, indent=2)

# Main UI
st.title("🚀 AI SDR Personalisation Assistant")
st.markdown("Generate personalized outreach content in seconds")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Generate", "History", "Settings"])

with tab1:
    st.subheader("📋 Enter Details")
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g., Acme Corp")
        industry = st.text_input("Industry", placeholder="e.g., SaaS, FinTech")
    
    with col2:
        prospect_name = st.text_input("Prospect Name", placeholder="e.g., John Smith")
        company_summary = st.text_area("Company Description", placeholder="Brief description of the company...", height=100)

    if st.button("✨ Generate Outreach", type="primary", use_container_width=True):
        if validate_inputs(company_name, prospect_name, industry, company_summary):
            with st.spinner("🤖 Generating content..."):
                content = generate_outreach(company_name, prospect_name, industry, company_summary)
                
                if content:
                    st.success("✅ Content generated successfully!")
                    st.markdown(content)
                    
                    # Save to history
                    save_to_history(company_name, prospect_name, industry, content)
                    
                    # Export option
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download as Text",
                            data=content,
                            file_name=f"outreach_{prospect_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    with col2:
                        st.info("✅ Saved to history")

with tab2:
    st.subheader("📚 Outreach History")
    
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"📄 {entry['prospect_name']} - {entry['company_name']} ({entry['timestamp'][:10]})"):
                st.markdown(entry['content'])
                st.caption(f"Generated: {entry['timestamp']}")
        
        # Export all history
        if st.button("📊 Export All History as JSON"):
            history_json = export_history()
            if history_json:
                st.download_button(
                    label="📥 Download History",
                    data=history_json,
                    file_name=f"outreach_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    else:
        st.info("📭 No history yet. Generate some outreach content first!")

with tab3:
    st.subheader("⚙️ Settings")
    st.markdown("**API Configuration**")
    if os.getenv("OPENAI_API_KEY"):
        st.success("✅ OpenAI API Key is configured")
    else:
        st.error("❌ OpenAI API Key is not set")
    
    st.markdown("**Statistics**")
    st.metric("Total Generated", len(st.session_state.history))
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.success("✅ History cleared!")
        st.rerun()