# Digital Detective AI - Streamlit Edition

This version is designed to run as a single Streamlit web application.

## Features
- CSV and Excel upload
- Automatic common-column detection
- Dashboard metrics and charts
- Investigation Stack visualization
- Push/pop/peek/search concepts
- Gemini AI analysis
- Rule-based fallback when Gemini is unavailable
- Related grouping and pattern detection
- Downloadable analysis report
- Separate C++ academic core

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Gemini API

Create a Gemini API key in Google AI Studio and configure it as:

```text
GEMINI_API_KEY
```

For Streamlit Community Cloud, add it under App Settings -> Secrets:

```toml
GEMINI_API_KEY = "your-key"
```

Never commit your real API key to a public repository.

## Sample dataset

Use the provided `digital_detective_sample_dataset.csv` or `.xlsx` from the earlier project.

## Deployment

The easiest public deployment is Streamlit Community Cloud. The app can be connected to a GitHub repository and deployed as a `streamlit.app` URL.

Docker deployment is also supported using the included Dockerfile.

## Academic explanation

The C++ core demonstrates:
- Abstract class
- Inheritance
- Encapsulation
- Polymorphism
- Stack
- Search
- Deletion by index

The Streamlit layer provides the usable data-analysis interface.
