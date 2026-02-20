import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
import io   # REQUIRED for compression

# -------------------------
# PAGE CONFIG + LOGO
# -------------------------
logo = Image.open("logo.jpeg")

st.set_page_config(
    page_title="Lekha Yatra",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=logo
)
st.markdown("""
    <style>
        :root {
            color-scheme: light;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# CUSTOM CSS (MATCH HTML THEME)
# -------------------------
st.markdown("""
<style>
body { background-color: #f5f7fb; }

.top-header {
    background: #283593;
    padding: 14px 24px;
    border-radius: 8px;
    color: white;
    font-size: 20px;
    font-weight: bold;
}

.card {
    background: white;
    padding: 18px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

section[data-testid="stSidebar"] { background-color: #283593; }
section[data-testid="stSidebar"] * { color: white; }

.stButton>button {
    background: #283593;
    color: white;
    border-radius: 6px;
}

header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------
if "documents" not in st.session_state:
    st.session_state.documents = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:

    st.image(logo, width=120)
    st.markdown('<div class="top-header">Lekha Yatra – Family Login</div>', unsafe_allow_html=True)

    family = st.text_input("User Name")
    pin = st.text_input("PIN (4–6 digits)", type="password")

    if st.button("Login"):
        if family and pin:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Enter family name and PIN")

# -------------------------
# MAIN APP
# -------------------------
else:

    col1, col2 = st.columns([1, 8])
    with col1:
        st.image(logo, width=70)
    with col2:
        st.markdown('<div class="top-header">Lekha Yatra – From Paper Trails To Digital Ease</div>',
                    unsafe_allow_html=True)

    st.sidebar.image(logo, width=120)

    menu = st.sidebar.radio("Navigation", [
        "🏠 Home",
        "📂 Upload Document",
        "📊 Document Overview",
        "🔍 Search Documents",
        "📝 Readiness Checker",
        "👨‍👩‍👧 Family Vault",
        "❓ Help"   
    ])

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # -------------------------
    # HOME
    # -------------------------
    if menu == "🏠 Home":

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.header("Welcome to Lekha Yatra")

        st.write("""
    Lekha Yatra is a smart digital document management platform designed to help individuals and families organize, store, and access their important documents in one secure place.

    In daily life, documents are often scattered across emails, cloud drives, messaging apps, and physical files, making them difficult to find when urgently needed. Lekha Yatra solves this problem by bringing everything together into a single, organized system.

    The platform automatically categorizes documents into sections such as Government, Education, Finance, and Career, making them easy to manage and retrieve anytime.

    Users can also track issue and expiry dates, receive alerts before documents expire, and check whether they are ready for applications like scholarships, jobs, admissions, or government services.

    With features like quick search, document overview, readiness checking, and a family vault for multiple members, Lekha Yatra transforms scattered paperwork into a structured and reliable digital system.

    Our goal is simple — to help users stay organized, prepared, and stress-free when important opportunities arise.
        """)

        st.subheader("Key Takeaways")

        st.write("""
    ✔ Centralized storage for all important documents  
    ✔ Automatic organization into categories  
    ✔ Expiry tracking and alerts  
    ✔ Quick search and easy retrieval  
    ✔ Application readiness checker  
    ✔ Support for multiple family members  
        """)

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # UPLOAD DOCUMENT
    # -------------------------
    elif menu == "📂 Upload Document":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Add / Update Document")

        # -------- CATEGORY MAPPING FUNCTION --------
        def auto_category_from_type(doc_type):
            mapping = {
                "Aadhaar Card": "Government",
                "PAN Card": "Government",
                "Passport": "Government",
                "Income Certificate": "Government",

                "10th Marksheet": "Education",
                "12th Marksheet": "Education",
                "Degree Certificate": "Education",
                "Bonafide Certificate": "Education",

                "Bank Passbook": "Finance",

                "Resume": "Career",
                "Experience Letter": "Career"
            }
            return mapping.get(doc_type, "Other")

        # -------- SECTION 1: DOCUMENT INFO --------
        title = st.text_input("Document Title")

        doc_type = st.selectbox(
            "Document Type",
            [
                "Aadhaar Card", "PAN Card", "Passport",
                "Income Certificate", "Bank Passbook",
                "10th Marksheet", "12th Marksheet",
                "Degree Certificate", "Bonafide Certificate",
                "Resume", "Experience Letter", "Other"
            ]
        )

        # -------- AUTO CATEGORY --------
        category = auto_category_from_type(doc_type)
        st.write(f"Auto Category: **{category}**")

        # -------- SECTION 3: OWNER --------
        owner = st.selectbox(
            "Family Member",
            ["Self", "Father", "Mother", "Sibling", "Other"]
        )

        # -------- SECTION 4: VALIDITY --------
        issue_date = st.date_input("Issue Date")
        no_expiry = st.checkbox("No Expiry (NA)")  # ⭐ NEW OPTION

        if no_expiry:
            expiry = None
        else:
            expiry = st.date_input("Expiry Date")

        # -------- SECTION 5: FILE UPLOAD --------
        uploaded_file = st.file_uploader(
            "Upload Document (PDF/JPG/PNG)",
            type=["pdf", "jpg", "jpeg", "png"]
        )

        if st.button("Save Document"):

            if title and uploaded_file:
                original_filename = uploaded_file.name   

                # -------- FILE COMPRESSION --------
                MAX_SIZE_MB = 1
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)

                compressed_note = ""

                if file_size > MAX_SIZE_MB:
                    compressed_note = " (Compressed)"

                    # Compress only images
                    if uploaded_file.type.startswith("image"):
                        img = Image.open(uploaded_file)
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=50)
                        uploaded_file = buffer

                st.session_state.documents.append({
                    "title": title,
                    "doc_type": doc_type,
                    "category": category,
                    "owner": owner,
                    "issue_date": issue_date,
                    "expiry": expiry,
                    "filename": uploaded_file.name,
                    "compressed": compressed_note
                })

                st.success(f"Document saved successfully!{compressed_note}")

            else:
                st.error("Please fill required fields and upload file.")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # Document Overview
    # -------------------------
    elif menu == "📊 Document Overview":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Document Overview")

        today = date.today()
        total = len(st.session_state.documents)
        expired = sum(
            1 for d in st.session_state.documents
            if d["expiry"] is not None and d["expiry"] < today
        )

        expiring_soon = sum(
            1 for d in st.session_state.documents
            if d["expiry"] is not None and 0 <= (d["expiry"] - today).days <= 60
        )

        alerts = []   
        for d in st.session_state.documents:
            if d["expiry"] is None:
                continue

            days_left = (d["expiry"] - today).days

            if days_left < 0:
                expired += 1
            elif days_left <= 30:
                expiring_soon += 1

                if days_left <= 1:
                    alerts.append(f"⚠ {d['title']} expires in 1 day")
                elif days_left <= 2:
                    alerts.append(f"⚠ {d['title']} expires in 2 days")
                elif days_left <= 14:
                    alerts.append(f"⚠ {d['title']} expires in 2 weeks")
                else:
                    alerts.append(f"⚠ {d['title']} expires within 1 month")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total", total)
        c2.metric("Expired", expired)
        c3.metric("Expiring Soon", expiring_soon)
        if alerts:
            st.warning("Expiry Alerts")
            for a in alerts:
                st.write(a)

        if total:
            st.dataframe(pd.DataFrame(st.session_state.documents), use_container_width=True)
        else:
            st.info("No documents yet.")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # SEARCH
    # -------------------------
    elif menu == "🔍 Search Documents":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Browse Documents")
        
        docs = st.session_state.documents

        # -------- SEARCH --------
        search_query = st.text_input("Search by document name")

        # -------- CATEGORY FILE VIEW --------
        st.subheader("Categories")

        # ✅ SHOW ALL CATEGORIES ALWAYS
        categories = ["ID", "Education", "Finance", "Government", "Other"]

        # CSS for file-style cards
        st.markdown("""
        <style>
        .file-card {
            background: #eef2ff;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            font-weight: bold;
            cursor: pointer;
            border: 2px solid #283593;
            transition: 0.2s;
        }
        .file-card:hover {
            background: #dbe4ff;
            transform: scale(1.05);
        }
        </style>
        """, unsafe_allow_html=True)

        if "selected_category" not in st.session_state:
            st.session_state.selected_category = None

        cols = st.columns(len(categories))

        for i, cat in enumerate(categories):
            count = sum(1 for d in docs if d["category"] == cat)

            with cols[i]:
                if st.button(f"📁 {cat}\n({count})"):
                    st.session_state.selected_category = cat

        # -------- FILTER DOCUMENTS --------
        filtered_docs = docs

        if st.session_state.selected_category:
            filtered_docs = [
                d for d in filtered_docs
                if d["category"] == st.session_state.selected_category
            ]

        if search_query:
            filtered_docs = [
                d for d in filtered_docs
                if search_query.lower() in d["title"].lower()
            ]

        st.markdown("---")

        if filtered_docs:
            st.dataframe(pd.DataFrame(filtered_docs), use_container_width=True)
        else:
            st.info("No documents found.")

        st.markdown('</div>', unsafe_allow_html=True)
    # -------------------------
    # READINESS CHECKER
    # -------------------------
    elif menu == "📝 Readiness Checker":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Application Readiness")

        purpose = st.selectbox("Purpose", ["Scholarship","Internship" ,"Job (Freshers)","Job (Experienced)", "Admission", "Loan (Personal)","Loan (Education)","Passport Application","Government Scheme Application"])

        # -------- REQUIRED DOCUMENTS TEMPLATE --------
        required_docs = {
            "Scholarship": [
                "Aadhaar Card",
                "Income Certificate",
                "Bank Passbook",
                "10th Marksheet",
                "12th Marksheet",
                "Bonafide Certificate"
            ],
            "Internship": [
                "Resume",
                "College ID Card",
                "Bonafide Certificate",
                "Latest Marksheet",
                "Project Portfolio",
                "Certificates"
            ],
            "Job (Freshers)": [
                "Aadhaar Card",
                "10th Marksheet",
                "12th Marksheet",
                "Degree Certificate",
                "Resume",
                "Internship Certificate"
            ],
            "Job (Experienced)": [
                "Aadhaar Card",
                "Degree Certificate",
                "Resume",
                "Experience Letter",
                "Relieving Letter",
                "Salary Slips",
                "Bank Statement"
            ],
            "Admission": [
                "Aadhaar Card",
                "10th Marksheet",
                "12th Marksheet",
                "Transfer Certificate"
            ],
            "Loan (Personal)": [
                "Aadhaar Card",
                "Income Proof",
                "Bank Statement",
                "PAN Card"
            ],
            "Loan (Education)": [
                "Aadhaar Card",
                "Income Proof",
                "Bank Statement",
                "PAN Card",
                "Admission Letter",
                "Fee Structure"
            ],
            "Passport Application": [
                "Aadhaar Card",
                "Address Proof",
                "Birth Certificate",
                "Educational Certificate"
            ],
            "Government Scheme Application": [
                "Aadhaar Card",
                "Income Certificate",
                "Caste Certificate",
                "Bank Details"
            ]
        }

        if st.button("Check Readiness"):

            # Normalize titles from saved documents
            def normalize(text):
                return text.lower().replace("aadhar", "aadhaar")

            existing_titles = [normalize(d["title"]) for d in st.session_state.documents]
            needed = required_docs[purpose]

            missing = []

            for req in required_docs[purpose]:
                req_norm = normalize(req)

                if not any(req_norm in title for title in existing_titles):
                    missing.append(req)

            available = [doc for doc in needed if doc in existing_titles]

            st.subheader("Required Documents")

            for doc in needed:
                if doc in available:
                    st.success(f"✔ {doc}")
                else:
                    st.error(f"✖ {doc} (Missing)")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # FAMILY VAULT
    # -------------------------
    elif menu == "👨‍👩‍👧 Family Vault":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Family Vault")

        if st.session_state.documents:
            owners = set(d["owner"] for d in st.session_state.documents)
            for person in owners:
                st.subheader(person)
                docs = [d for d in st.session_state.documents if d["owner"] == person]
                st.dataframe(pd.DataFrame(docs), use_container_width=True)
        else:
            st.info("No documents uploaded yet.")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # HELP PAGE
    # -------------------------
    elif menu == "❓ Help":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Help & Support")

        st.subheader("Common Issues & Solutions")

        st.write("""
    **📂 Document Upload Problems**
    - Ensure file size is within limit
    - Use supported formats (PDF/JPG/PNG)
    - Refresh page if upload fails

    **🔍 Unable to Find Documents**
    - Check correct category
    - Use search option
    - Ensure document was saved successfully

    **✏️ Updating Documents**
    - Re-upload with updated details
    - Old versions remain in vault

    **🔒 Access Issues**
    - Ensure login session active
    - Do not refresh repeatedly during upload

    **👤 Profile Problems**
    - Logout and login again
    - Clear browser cache if needed
        """)

        st.subheader("Contact Support")

        st.write("""
    For assistance, contact our experts:

    📞 Support Number: +91 XXXXX XXXXX  
    📧 Email: support@lekhayatra.com  

    Our team will guide you through any issue.
        """)

        st.markdown('</div>', unsafe_allow_html=True)