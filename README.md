# DATA698
 
## Insurance Policy Change Detection Tool (Capstone Project)

### Overview

This project presents an NLP-based tool that is designed to detect changes between expiring and renewal insurance policy documents. Currently, underwriters compare these documents manually, which is a time-consuming and error-prone process. This tool enhances the review process by using semantic similarity analysis and visual difference reporting. The tool allows underwriters to quickly identify changes in coverages, clauses, etc. 

### Project Structure

- **main.py** core logic for comparing policies
- **test.py** paragraph-level evaluation using annotated JSONs
- **generate_policies.py** synthetic policy generation
- **visuals.py** visuals 
- **web_app.py** web interface for uploading and comparing PDFs
- **ANNOTATED-POLICIES/** contains expiring, renewal, and manually annotated JSONs
- **requirements.txt** contains required Python packages
- **README.md** this file

### Dependencies

See **requirements.txt** file for full list

## Disclaimer

Real-world policy templates used in this project have been anonymized. No confidential data is shared.

## Author

Kristin Lussi
M.S. in Data Science, CUNY School of Professional Studies