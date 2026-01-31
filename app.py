"""
Streamlit Frontend for CV-LinkedIn Comparator
Provides user interface for uploading CV and comparing with LinkedIn profile.
"""

import streamlit as st
import requests
import json
from typing import Dict, Optional

# Configuration
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="CV-LinkedIn Comparator",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #0066cc;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-excellent {
        color: #28a745;
        font-weight: bold;
    }
    .score-good {
        color: #ffc107;
        font-weight: bold;
    }
    .score-poor {
        color: #dc3545;
        font-weight: bold;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
    .skill-common {
        background-color: #28a745;
        color: white;
    }
    .skill-cv {
        background-color: #007bff;
        color: white;
    }
    .skill-linkedin {
        background-color: #0077b5;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def display_score(score: float, label: str):
    """Display a score with appropriate color coding."""
    if score >= 80:
        color_class = "score-excellent"
        emoji = "✅"
    elif score >= 60:
        color_class = "score-good"
        emoji = "⚠️"
    else:
        color_class = "score-poor"
        emoji = "❌"
    
    st.markdown(
        f"**{label}:** <span class='{color_class}'>{emoji} {score:.1f}%</span>",
        unsafe_allow_html=True
    )


def display_skills(skills_data: Dict):
    """Display skills comparison with badges."""
    st.subheader("🎯 Skills Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**✅ Common Skills**")
        common = skills_data.get('common', [])
        if common:
            for skill in common:
                st.markdown(
                    f"<span class='skill-badge skill-common'>{skill}</span>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No common skills found")
    
    with col2:
        st.markdown("**📄 CV Only**")
        cv_only = skills_data.get('cv_only', [])
        if cv_only:
            for skill in cv_only:
                st.markdown(
                    f"<span class='skill-badge skill-cv'>{skill}</span>",
                    unsafe_allow_html=True
                )
        else:
            st.success("All CV skills are on LinkedIn!")
    
    with col3:
        st.markdown("**💼 LinkedIn Only**")
        linkedin_only = skills_data.get('linkedin_only', [])
        if linkedin_only:
            for skill in linkedin_only:
                st.markdown(
                    f"<span class='skill-badge skill-linkedin'>{skill}</span>",
                    unsafe_allow_html=True
                )
        else:
            st.success("All LinkedIn skills are on CV!")
    
    # Skills match rate
    match_rate = skills_data.get('match_rate', 0)
    st.progress(match_rate / 100)
    st.caption(f"Skills Match Rate: {match_rate:.1f}%")


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("<h1 class='main-header'>📄 CV vs LinkedIn Comparator</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-header'>Compare your CV with your LinkedIn profile to ensure consistency</p>",
        unsafe_allow_html=True
    )
    
    # Check API status
    with st.spinner("Checking API connection..."):
        api_healthy = check_api_health()
    
    if not api_healthy:
        st.error("⚠️ Backend API is not running. Please start the backend server first.")
        st.code("python -m uvicorn backend.main:app --reload", language="bash")
        return
    
    st.success("✅ Connected to backend API")
    st.divider()
    
    # Input section
    st.header("📝 Upload Your Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ Upload CV")
        cv_file = st.file_uploader(
            "Upload your CV (PDF or DOCX)",
            type=['pdf', 'docx'],
            help="Upload your CV in PDF or DOCX format"
        )
        
        if cv_file:
            st.success(f"✅ File uploaded: {cv_file.name}")
            st.caption(f"Size: {cv_file.size / 1024:.1f} KB")
    
    with col2:
        st.subheader("2️⃣ LinkedIn Profile")
        linkedin_text = st.text_area(
            "Paste your LinkedIn profile text",
            height=200,
            help="Copy and paste the text from your LinkedIn profile, including experience, skills, and education sections",
            placeholder="Example:\n\nEXPERIENCE\nSenior Developer at Tech Corp (2020-2023)\n- Led team of 5 developers\n- Built Python applications\n\nSKILLS\nPython, JavaScript, React, AWS, Docker\n\nEDUCATION\nBS Computer Science, University XYZ (2016-2020)"
        )
    
    # Compare button
    st.divider()
    
    if st.button("🔍 Compare CV and LinkedIn", type="primary", use_container_width=True):
        
        # Validation
        if not cv_file:
            st.error("❌ Please upload a CV file")
            return
        
        if not linkedin_text or len(linkedin_text.strip()) < 50:
            st.error("❌ Please provide LinkedIn profile text (minimum 50 characters)")
            return
        
        # Make API request
        with st.spinner("🔄 Analyzing and comparing... This may take a moment..."):
            try:
                # Prepare form data
                files = {
                    'cv_file': (cv_file.name, cv_file.getvalue(), cv_file.type)
                }
                data = {
                    'linkedin_text': linkedin_text
                }
                
                # Send request
                response = requests.post(
                    f"{API_URL}/compare",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    st.success("✅ Analysis Complete!")
                    st.divider()
                    
                    # Overall Score
                    st.header("📊 Overall Match Score")
                    overall_score = result['overall_score']
                    
                    # Create a large metric display
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.metric(
                            label="Match Score",
                            value=f"{overall_score:.1f}%",
                            delta="Excellent!" if overall_score >= 80 else "Needs improvement" if overall_score < 60 else "Good"
                        )
                        st.progress(overall_score / 100)
                    
                    st.divider()
                    
                    # Section Scores
                    st.header("📋 Section Breakdown")
                    section_cols = st.columns(3)
                    
                    sections = result['section_scores']
                    section_names = ['experience', 'skills', 'education']
                    section_emojis = ['💼', '🎯', '🎓']
                    
                    for idx, (section, emoji) in enumerate(zip(section_names, section_emojis)):
                        with section_cols[idx]:
                            score = sections.get(section, 0)
                            st.metric(
                                label=f"{emoji} {section.title()}",
                                value=f"{score:.1f}%"
                            )
                            st.progress(score / 100)
                    
                    st.divider()
                    
                    # Skills Analysis
                    display_skills(result['skills_comparison'])
                    
                    st.divider()
                    
                    # Recommendations
                    st.header("💡 Recommendations")
                    recommendations = result.get('recommendations', [])
                    
                    if recommendations:
                        for rec in recommendations:
                            if '✅' in rec:
                                st.success(rec)
                            elif '❌' in rec:
                                st.error(rec)
                            else:
                                st.warning(rec)
                    else:
                        st.info("No specific recommendations at this time.")
                    
                    # Discrepancies
                    if result.get('discrepancies'):
                        st.divider()
                        st.header("⚠️ Discrepancies Detected")
                        
                        for disc in result['discrepancies']:
                            severity = disc['severity']
                            section = disc['section']
                            score = disc['score']
                            
                            if severity == 'high':
                                st.error(f"**{section.title()}**: Low match ({score*100:.1f}%) - Significant differences detected")
                            else:
                                st.warning(f"**{section.title()}**: Moderate match ({score*100:.1f}%) - Some differences found")
                    
                    # Raw JSON (expandable)
                    with st.expander("🔍 View Raw JSON Response"):
                        st.json(result)
                
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.json(response.json())
            
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. The backend might be processing a large file. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API. Please ensure it's running.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.exception(e)
    
    # Footer
    st.divider()
    st.caption("💡 **Tip**: Make sure your LinkedIn profile text includes clear section headers like 'EXPERIENCE', 'SKILLS', and 'EDUCATION' for best results.")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📖 How to Use")
        st.markdown("""
        1. **Upload your CV** in PDF or DOCX format
        2. **Copy your LinkedIn profile**:
           - Go to your LinkedIn profile
           - Select and copy the text
           - Include Experience, Skills, and Education sections
        3. **Click Compare** to analyze
        4. **Review results** and recommendations
        
        ### Tips for Best Results
        - Ensure your LinkedIn text has clear section headers
        - Include complete information in both CV and LinkedIn
        - Use consistent terminology across platforms
        
        ### Score Interpretation
        - **80-100%**: Excellent match ✅
        - **60-79%**: Good match ⚠️
        - **0-59%**: Needs improvement ❌
        """)
        
        st.divider()
        
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses AI to compare your CV with your LinkedIn profile,
        helping you maintain consistency across platforms.
        
        **Technology:**
        - Local sentence transformers
        - Privacy-focused (no data sent externally)
        - Fast and accurate semantic comparison
        """)


if __name__ == "__main__":
    main()
