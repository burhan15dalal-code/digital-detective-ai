import json
import os
from io import BytesIO

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Digital Detective AI",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px;}
.hero {
    padding: 1.4rem 1.6rem;
    border-radius: 18px;
    background: linear-gradient(135deg,#0d2038,#142b4d);
    border: 1px solid #244666;
    margin-bottom: 1.2rem;
}
.hero h1 {margin:0; font-size:2.2rem;}
.hero p {color:#9eb4cc; margin:.4rem 0 0;}
.metric-card {
    background:#0e1b2d;
    border:1px solid #1e3853;
    border-radius:14px;
    padding:16px;
}
.small {color:#91a7bd; font-size:.85rem;}
.insight {
    background:#0d1d30;
    border-left:4px solid #55d7ff;
    padding:14px 16px;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "records" not in st.session_state:
    st.session_state.records = []
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# ---------- Helpers ----------
def normalize_records(df):
    df = df.fillna("")
    records = []
    for i, row in df.iterrows():
        raw = {str(k).strip(): str(v).strip() for k, v in row.to_dict().items()}
        lower = {k.lower(): v for k, v in raw.items()}
        def pick(names, default=""):
            for n in names:
                if n.lower() in lower and lower[n.lower()]:
                    return lower[n.lower()]
            return default
        records.append({
            "index": int(i),
            "id": pick(["id", "record_id", "record id"], str(i + 1)),
            "name": pick(["name", "suspect", "person", "title"], f"Record {i+1}"),
            "type": pick(["type", "category", "record_type", "record type"], "Other"),
            "location": pick(["location", "foundat", "found at", "place"], ""),
            "date": pick(["date", "incident_date", "incident date"], ""),
            "priority": pick(["priority", "importance", "suspicion", "suspicion level"], ""),
            "description": pick(["description", "details", "detail", "notes"], " | ".join(f"{k}: {v}" for k,v in raw.items() if v)),
            "raw": raw,
        })
    return records

def category(value):
    t = str(value).lower()
    if "suspect" in t: return "Suspect"
    if "evidence" in t: return "Evidence"
    if "clue" in t: return "Clue"
    if "witness" in t: return "Witness"
    return "Other"

def local_analysis(records):
    cats = {}
    for r in records:
        c = category(r["type"])
        cats.setdefault(c, []).append(r["name"])
    locations = {}
    for r in records:
        if r["location"]:
            locations.setdefault(r["location"], []).append(r["name"])
    repeated = [f"{k}: {len(v)} records" for k,v in locations.items() if len(v) > 1]
    return {
        "summary": f"{len(records)} records processed. "
                   f"{sum(1 for r in records if category(r['type'])=='Suspect')} suspects, "
                   f"{sum(1 for r in records if category(r['type'])=='Evidence')} evidence items, "
                   f"{sum(1 for r in records if category(r['type'])=='Clue')} clues and "
                   f"{sum(1 for r in records if category(r['type'])=='Witness')} witnesses identified.",
        "categories": cats,
        "patterns": repeated or ["No repeated locations were detected."],
        "limitations": ["Rule-based fallback only. Configure Gemini for AI-assisted analysis."]
    }

def gemini_analysis(records, api_key):
    from google import genai
    sample = records[:150]
    prompt = f"""
You are an investigation-data analysis assistant for a student project named Digital Detective AI.
Analyze only the supplied records. Do not claim anyone is guilty. Treat all results as investigative
leads, not proof. Do not invent facts.

Return ONLY valid JSON with:
{{
 "summary": "neutral short summary",
 "categories": {{"Suspect":[],"Evidence":[],"Clue":[],"Witness":[],"Other":[]}},
 "priority": [{{"record":"","level":"High|Medium|Low","reason":""}}],
 "groups": [{{"group":"","records":[],"reason":""}}],
 "patterns": [],
 "limitations": []
}}

Tasks:
- classify records
- group related records by location/type/topic
- identify high-priority records from supplied information
- identify repeated patterns
- provide a concise neutral summary

Records:
{json.dumps(sample, ensure_ascii=False)}
"""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)

def make_report(df, analysis):
    lines = [
        "DIGITAL DETECTIVE AI - INVESTIGATION ANALYSIS",
        "=" * 55,
        "",
        "SUMMARY",
        analysis.get("summary", ""),
        "",
        "CATEGORIES",
    ]
    for k, vals in analysis.get("categories", {}).items():
        lines.append(f"{k}: {', '.join(map(str, vals)) or 'None'}")
    lines += ["", "PRIORITY"]
    for p in analysis.get("priority", []):
        lines.append(f"- {p.get('level','')}: {p.get('record','')} - {p.get('reason','')}")
    lines += ["", "GROUPS"]
    for g in analysis.get("groups", []):
        lines.append(f"- {g.get('group','')}: {', '.join(map(str,g.get('records',[])))}")
        lines.append(f"  {g.get('reason','')}")
    lines += ["", "PATTERNS"]
    lines += [f"- {x}" for x in analysis.get("patterns", [])]
    lines += ["", "LIMITATIONS"]
    lines += [f"- {x}" for x in analysis.get("limitations", [])]
    lines += ["", "Note: AI results are investigative leads and must not be treated as proof."]
    return "\n".join(lines)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🕵️ DIGITAL DETECTIVE")
    st.caption("Crime Investigation Simulator")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Import Data", "Investigation Stack", "AI Analysis", "Reports"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("Academic core")
    st.write("Abstract class")
    st.write("Inheritance")
    st.write("Encapsulation")
    st.write("Polymorphism")
    st.write("Stack operations")

# ---------- Hero ----------
st.markdown("""
<div class="hero">
<h1>Investigation Command Center</h1>
<p>OOP + Stack + CSV/Excel + AI-assisted investigation analysis</p>
</div>
""", unsafe_allow_html=True)

# ---------- Import ----------
if page == "Import Data":
    st.header("📁 Import Investigation Data")
    uploaded = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
        help="The app automatically detects common columns such as name, type, location, date, priority and description."
    )
    if uploaded:
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            st.session_state.df = df
            st.session_state.records = normalize_records(df)
            st.session_state.analysis = None
            st.success(f"Imported {len(df)} records from {uploaded.name}")
            st.write("Detected columns:", ", ".join(map(str, df.columns)))
            st.dataframe(df, use_container_width=True, height=450)
        except Exception as e:
            st.error(f"Could not read the file: {e}")

# ---------- Dashboard ----------
elif page == "Dashboard":
    records = st.session_state.records
    if not records:
        st.info("Import a CSV or Excel file from the sidebar to begin.")
    else:
        counts = {}
        for r in records:
            counts[category(r["type"])] = counts.get(category(r["type"]), 0) + 1
        cols = st.columns(5)
        for col, label in zip(cols, ["Total","Suspects","Evidence","Clues","Witnesses"]):
            key = {"Total":len(records),"Suspects":counts.get("Suspect",0),"Evidence":counts.get("Evidence",0),
                   "Clues":counts.get("Clue",0),"Witnesses":counts.get("Witness",0)}[label]
            col.metric(label, key)

        st.subheader("📊 Record Distribution")
        chart = pd.DataFrame({"Category": list(counts.keys()), "Records": list(counts.values())}).set_index("Category")
        st.bar_chart(chart)

        st.subheader("Recent Investigation Records")
        st.dataframe(pd.DataFrame(records)[["id","name","type","location","date","priority","description"]], use_container_width=True)

# ---------- Stack ----------
elif page == "Investigation Stack":
    st.header("📚 Investigation Stack")
    records = st.session_state.records
    if not records:
        st.info("No records loaded.")
    else:
        st.caption("TOP → newest imported record first. This visualizes the LIFO stack concept.")
        for i, r in enumerate(reversed(records)):
            with st.container(border=True):
                if i == 0:
                    st.markdown("**🔝 TOP**")
                st.write(f"**{r['name']}**  ·  `{category(r['type'])}`")
                st.caption(f"Location: {r['location']} | Priority: {r['priority']}")
                st.write(r["description"])

        st.divider()
        st.subheader("Stack Operations")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Peek", use_container_width=True):
                st.write(records[-1] if records else "Stack empty")
        with c2:
            if st.button("Pop", use_container_width=True):
                if records:
                    st.session_state.records.pop()
                    st.success("Latest record removed.")
                    st.rerun()
        with c3:
            search = st.text_input("Search name")
        if search:
            found = [r for r in records if search.lower() in r["name"].lower()]
            st.write(f"Found {len(found)} record(s).")
            st.dataframe(pd.DataFrame(found), use_container_width=True)

# ---------- AI ----------
elif page == "AI Analysis":
    st.header("🤖 AI Investigation Analysis")
    records = st.session_state.records
    if not records:
        st.info("Import data first.")
    else:
        st.write(f"Ready to analyze **{len(records)} records**.")
        api_key = None
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        else:
            api_key = os.getenv("GEMINI_API_KEY")

        use_ai = st.toggle("Use Gemini AI", value=bool(api_key), disabled=not bool(api_key))
        if not api_key:
            st.warning("Gemini key not configured. Rule-based analysis is available as a fallback.")

        if st.button("🔎 Analyze Investigation", type="primary", use_container_width=True):
            with st.spinner("Analyzing investigation records..."):
                try:
                    if use_ai and api_key:
                        st.session_state.analysis = gemini_analysis(records, api_key)
                    else:
                        st.session_state.analysis = local_analysis(records)
                    st.success("Analysis complete.")
                except Exception as e:
                    st.error(f"AI analysis failed. Using local fallback. Details: {e}")
                    st.session_state.analysis = local_analysis(records)

        a = st.session_state.analysis
        if a:
            st.subheader("Summary")
            st.markdown(f'<div class="insight">{a.get("summary","")}</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Segregation")
                st.json(a.get("categories", {}))
            with c2:
                st.subheader("Patterns")
                for p in a.get("patterns", []):
                    st.write("•", p)

            st.subheader("Priority Analysis")
            st.dataframe(pd.DataFrame(a.get("priority", [])), use_container_width=True)

            st.subheader("Related Groups")
            st.dataframe(pd.DataFrame(a.get("groups", [])), use_container_width=True)

            st.subheader("Limitations")
            for x in a.get("limitations", []):
                st.write("•", x)

# ---------- Reports ----------
elif page == "Reports":
    st.header("📄 Investigation Report")
    if not st.session_state.analysis:
        st.info("Run an analysis first.")
    else:
        report = make_report(st.session_state.df, st.session_state.analysis)
        st.text_area("Report Preview", report, height=500)
        st.download_button(
            "⬇️ Download Analysis Report",
            report,
            file_name="digital_detective_analysis.txt",
            mime="text/plain",
            use_container_width=True,
        )
        if not st.session_state.df.empty:
            csv = st.session_state.df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Imported Data",
                csv,
                file_name="digital_detective_imported_data.csv",
                mime="text/csv",
                use_container_width=True,
            )
