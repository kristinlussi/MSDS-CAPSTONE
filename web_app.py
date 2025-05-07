import base64
import streamlit as st
import tempfile
from main import *

st.title("Expiring vs. Renewal Comparison Tool")

custom_css = """
<style>
  body {
    background-color: #f0f0f0;
    color: #333;
  }
  .report-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 10px;
    color: #f0f0f0;
  }
  table.diff {
    width: 100%;
    border: 2px solid #000;
  }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Upload Expiring and Renewal PDF files
expiring_file = st.file_uploader("Upload Expiring Policy", type="pdf", key="expiring")
renewal_file = st.file_uploader("Upload Renewal Policy", type="pdf", key="renewal")

if expiring_file is not None and renewal_file is not None:
    # Save uploaded files to temporary files so they can be processed by difference code
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_exp:
        tmp_exp.write(expiring_file.read())
        expiring_path = tmp_exp.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_ren:
        tmp_ren.write(renewal_file.read())
        renewal_path = tmp_ren.name

    st.write("Processing documents...")
    
    # Run the main function from main.py which produces the diff html report
    main(expiring_path, renewal_path)
    
    # Read the generated HTML diff report
    with open("diff_output.html", "r", encoding="utf-8") as f:
        diff_html = f.read()
    
    # Encode the HTML content into base64
    b64_html = base64.b64encode(diff_html.encode()).decode()
    
    # Create a data URL and hyperlink that opens the HTML in a new tab
    new_tab_link = f'<a href="data:text/html;base64,{b64_html}" target="_blank">Report is Ready</a>'
    
    st.markdown(new_tab_link, unsafe_allow_html=True)