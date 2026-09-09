import streamlit as st
import pandas as pd
import re
import math
import requests

from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# FIX HTML RENDERING
# ============================================================
#
# BUG FIX EXPLANATION:
# The original code used textwrap.dedent(), which only strips the
# COMMON leading whitespace shared by every line in a string. Because
# the HTML strings in this file are written inline inside deeply
# nested functions / with-blocks, their indentation varies a lot from
# line to line. dedent() could not fully remove it, so many lines
# stayed indented by 4+ spaces. Streamlit's Markdown parser treats any
# line indented by 4+ spaces as a fenced code block, so instead of
# rendering as HTML, it was displayed as literal escaped text.
#
# THE FIX: strip leading whitespace from EVERY individual line (not
# just the shared prefix). HTML doesn't care about whitespace between
# tags, so this is safe and guarantees no line is ever left indented
# enough to be mistaken for a code block.

def _delined(body):
    """Strip leading whitespace from every line of an HTML string."""
    if isinstance(body, str):
        return "\n".join(line.lstrip() for line in body.split("\n"))
    return body


_original_markdown = st.markdown

def fixed_markdown(body, *args, **kwargs):

    if kwargs.get("unsafe_allow_html", False):
        body = _delined(body)

    return _original_markdown(
        body,
        *args,
        **kwargs
    )

st.markdown = fixed_markdown


# st.sidebar is a SEPARATE DeltaGenerator object with its own bound
# `markdown` method — patching st.markdown above does NOT affect
# st.sidebar.markdown. Every st.sidebar.markdown(..., unsafe_allow_html=True)
# call (logo, "logged in as" box, system status pill, etc.) needs its
# own patch, or it keeps using the original, un-fixed method.

_original_sidebar_markdown = st.sidebar.markdown

def fixed_sidebar_markdown(body, *args, **kwargs):

    if kwargs.get("unsafe_allow_html", False):
        body = _delined(body)

    return _original_sidebar_markdown(
        body,
        *args,
        **kwargs
    )

st.sidebar.markdown = fixed_sidebar_markdown


# ============================================================
# DRISHTI
# ============================================================

st.set_page_config(
    page_title="DRISHTI | Disaster Intelligence",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# UI / UX DESIGN
# ============================================================

st.markdown("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #07111f;
    color: #e5e7eb;
}

[data-testid="stSidebar"] {
    background: #0b1728;
    border-right: 1px solid #1e334d;
}

[data-testid="stSidebar"] * {
    color: #dbeafe;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
}

/* HERO */

.hero {
    background: linear-gradient(
        135deg,
        #0b1f38 0%,
        #102e4d 55%,
        #123d5a 100%
    );

    border: 1px solid #24496b;
    border-radius: 22px;
    padding: 24px 28px;
    margin-bottom: 20px;
}

.hero h1 {
    margin: 0;
    font-size: 2.2rem;
    color: #f8fafc;
}

.hero p {
    margin: 7px 0 0;
    color: #a9c3dd;
    font-size: .95rem;
}

/* SECTION */

.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 8px 0 12px;
}

/* CARDS */

.card {
    background: #0d1b2d;
    border: 1px solid #1d344d;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
}

/* METRICS */

.metric {
    background: #0d1b2d;
    border: 1px solid #1d344d;
    border-radius: 16px;
    padding: 17px 18px;
}

.metric-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #f8fafc;
}

.metric-label {
    color: #89a4bf;
    font-size: .76rem;
    font-weight: 600;
    margin-top: 3px;
}

/* INCIDENT */

.critical {
    border-left: 5px solid #ef4444;
}

.high {
    border-left: 5px solid #f59e0b;
}

.medium {
    border-left: 5px solid #38bdf8;
}

/* PILLS */

.pill {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    font-size: .72rem;
    font-weight: 800;
    margin-right: 6px;
}

.pill-red {
    background: #3a151b;
    color: #fca5a5;
}

.pill-orange {
    background: #3b2910;
    color: #fcd34d;
}

.pill-blue {
    background: #102b43;
    color: #7dd3fc;
}

.pill-green {
    background: #102e24;
    color: #86efac;
}

/* AI */

.ai-result {
    background: linear-gradient(
        135deg,
        #0c2439,
        #0c1a2c
    );

    border: 1px solid #245477;
    border-radius: 20px;
    padding: 22px;
    margin-top: 16px;
}

.ai-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #e0f2fe;
}

.muted {
    color: #8fa9c2;
    font-size: .82rem;
}

/* LOGIN */

.login-card {
    max-width: 520px;
    margin: 45px auto;

    background: #f8fafc;
    color: #111827;

    border-radius: 24px;
    padding: 34px;

    box-shadow: 0 20px 60px rgba(0,0,0,.35);
}

.login-logo {
    text-align: center;
    font-size: 54px;
}

.login-title {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 800;
    color: #0f172a;
}

.login-sub {
    text-align: center;
    color: #64748b;
    font-size: .82rem;
    margin-bottom: 20px;
}

/* BUTTONS */

.stButton > button {
    border-radius: 11px;
    font-weight: 700;
    min-height: 42px;
}

/* STREAMLIT METRIC */

div[data-testid="stMetric"] {
    background: #0d1b2d;
    border: 1px solid #1d344d;
    border-radius: 15px;
    padding: 12px;
}

</style>
""", unsafe_allow_html=True)
# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None


# ============================================================
# DISASTER LOCATION DATABASE
# Prototype data note: No government incident records are used in this prototype.
# ============================================================

LOCATION_COORDINATES = {

    "sikkim": (27.5330, 88.5122),
    "arunachal pradesh": (28.2180, 94.7278),
    "assam": (26.2006, 92.9376),
    "meghalaya": (25.4670, 91.3662),
    "nagaland": (26.1584, 94.5624),
    "manipur": (24.6637, 93.9063),
    "mizoram": (23.1645, 92.9376),
    "tripura": (23.9408, 91.9882),
    "jammu & kashmir": (33.7782, 76.5762)

}


# ============================================================
# EMERGENCY RESOURCE DATABASE
# ============================================================

RESOURCES = [

    {
        "name": "NER Rescue Team A",
        "type": "Rescue Team",
        "location": "Sikkim",
        "lat": 27.5330,
        "lon": 88.5122,
        "capacity": 10,
        "status": "AVAILABLE"
    },

    {
        "name": "Mountain Rescue Team B",
        "type": "Rescue Team",
        "location": "Arunachal Pradesh",
        "lat": 28.2180,
        "lon": 94.7278,
        "capacity": 8,
        "status": "AVAILABLE"
    },

    {
        "name": "Emergency Medical Unit",
        "type": "Medical Unit",
        "location": "Meghalaya",
        "lat": 25.4670,
        "lon": 91.3662,
        "capacity": 40,
        "status": "AVAILABLE"
    },

    {
        "name": "Emergency Shelter 01",
        "type": "Shelter",
        "location": "Mizoram",
        "lat": 23.1645,
        "lon": 92.9376,
        "capacity": 200,
        "status": "AVAILABLE"
    },

    {
        "name": "Rapid Response Unit",
        "type": "Rescue Team",
        "location": "Manipur",
        "lat": 24.6637,
        "lon": 93.9063,
        "capacity": 7,
        "status": "BUSY"
    },

    {
        "name": "Mountain Response Unit",
        "type": "Rescue Team",
        "location": "Jammu & Kashmir",
        "lat": 33.7782,
        "lon": 76.5762,
        "capacity": 8,
        "status": "AVAILABLE"
    }

]


# ============================================================
# INCIDENT DATABASE
# ============================================================

if "incidents" not in st.session_state:

    st.session_state.incidents = [

        {
            "id": "INC-2042",
            "type": "Landslide",
            "location": "Sikkim",
            "lat": 27.5330,
            "lon": 88.5122,
            "severity": "CRITICAL",
            "confidence": 92,
            "affected": 65,
            "status": "ACTIVE",
            "description":
                "Synthetic prototype report: slope movement indicators "
                "suggest a possible road blockage.",
            "source":
                "Synthetic Sensor Simulation",
            "time":
                "12 min ago"
        },

        {
            "id": "INC-2041",
            "type": "Landslide",
            "location": "Arunachal Pradesh",
            "lat": 28.2180,
            "lon": 94.7278,
            "severity": "HIGH",
            "confidence": 87,
            "affected": 42,
            "status": "ACTIVE",
            "description":
                "Synthetic prototype report: elevated rainfall and "
                "slope instability detected.",
            "source":
                "Synthetic Environmental Simulation",
            "time":
                "28 min ago"
        },

        {
            "id": "INC-2040",
            "type": "Landslide",
            "location": "Meghalaya",
            "lat": 25.4670,
            "lon": 91.3662,
            "severity": "HIGH",
            "confidence": 89,
            "affected": 38,
            "status": "ACTIVE",
            "description":
                "Synthetic prototype report: high soil moisture combined "
                "with unstable terrain conditions.",
            "source":
                "Synthetic Environmental Simulation",
            "time":
                "41 min ago"
        },

        {
            "id": "INC-2039",
            "type": "Landslide",
            "location": "Jammu & Kashmir",
            "lat": 33.7782,
            "lon": 76.5762,
            "severity": "HIGH",
            "confidence": 85,
            "affected": 25,
            "status": "MONITORING",
            "description":
                "Synthetic prototype report: elevated slope and terrain "
                "instability conditions.",
            "source":
                "Synthetic Sensor Simulation",
            "time":
                "1 hr ago"
        }

    ]


# ============================================================
# AI INCIDENT ANALYSIS ENGINE
# ============================================================

def extract_location(text):

    text = text.lower()

    for location in LOCATION_COORDINATES:

        if location in text:

            return location.title()

    return "Location Pending Verification"


# ------------------------------------------------------------


def detect_disaster_type(text):

    text = text.lower()

    disaster_keywords = {

        "Flood": [
            "flood",
            "flooding",
            "waterlogging",
            "water entered",
            "overflow",
            "inundation"
        ],

        "Landslide": [
            "landslide",
            "mudslide",
            "rockfall",
            "slope failure"
        ],

        "Earthquake": [
            "earthquake",
            "tremor",
            "shaking",
            "magnitude"
        ],

        "Fire": [
            "fire",
            "flames",
            "smoke",
            "burning"
        ],

        "Cyclone": [
            "cyclone",
            "storm",
            "strong winds"
        ]

    }


    scores = {}

    for disaster, keywords in disaster_keywords.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1

        scores[disaster] = score


    detected = max(
        scores,
        key=scores.get
    )


    if scores[detected] == 0:

        return "Other"

    return detected


# ------------------------------------------------------------


def calculate_severity(text):

    text = text.lower()


    critical_keywords = [

        "trapped",
        "missing",
        "collapsed",
        "deaths",
        "dead",
        "fatal",
        "injured",
        "urgent",
        "rescue",
        "stranded",
        "life threatening"

    ]


    high_keywords = [

        "severe",
        "blocked",
        "danger",
        "families",
        "houses",
        "rapid",
        "evacuate",
        "evacuation",
        "major damage"

    ]


    critical_score = 0

    high_score = 0


    for word in critical_keywords:

        if word in text:

            critical_score += 1


    for word in high_keywords:

        if word in text:

            high_score += 1


    # -------------------------

    if critical_score >= 2:

        return "CRITICAL", 95


    elif critical_score >= 1:

        return "HIGH", 89


    elif high_score >= 2:

        return "HIGH", 87


    elif high_score >= 1:

        return "MEDIUM", 82


    else:

        return "LOW", 75


# ------------------------------------------------------------


def estimate_affected_people(text):

    numbers = re.findall(
        r'\b\d{1,6}\b',
        text
    )


    for number in numbers:

        value = int(number)

        if 1 <= value <= 100000:

            return value


    return 50


# ------------------------------------------------------------


def generate_response(severity):

    if severity == "CRITICAL":

        return [

            "🚑 Dispatch nearest rescue team immediately",

            "🏥 Prioritize hospital capacity",

            "🏠 Activate nearest emergency shelter",

            "📢 Issue targeted emergency alert",

            "🚧 Restrict access to affected zone"

        ]


    elif severity == "HIGH":

        return [

            "🚑 Deploy response resources",

            "🏥 Check nearby medical capacity",

            "🏠 Prepare evacuation shelter",

            "📡 Request additional field reports"

        ]


    elif severity == "MEDIUM":

        return [

            "👁️ Continue monitoring",

            "📡 Collect additional reports",

            "🚨 Keep response team on standby"

        ]


    else:

        return [

            "👁️ Monitor incident",

            "📡 Request additional evidence"

        ]


# ------------------------------------------------------------


def analyze_incident(report):

    text = report.lower()


    disaster_type = detect_disaster_type(
        text
    )


    location = extract_location(
        text
    )


    severity, confidence = calculate_severity(
        text
    )


    affected = estimate_affected_people(
        text
    )


    # Coordinates

    if location.lower() in LOCATION_COORDINATES:

        lat, lon = LOCATION_COORDINATES[
            location.lower()
        ]

    else:

        lat, lon = (
            34.0837,
            74.7973
        )


    # Verification signals

    verification_signals = [

        (
            "Emergency keywords",
            "Strong"
            if severity in ["CRITICAL", "HIGH"]
            else "Moderate"
        ),

        (
            "Disaster classification",
            "Detected"
            if disaster_type != "Other"
            else "Uncertain"
        ),

        (
            "Location extraction",
            "Detected"
            if location != "Location Pending Verification"
            else "Pending"
        ),

        (
            "Independent corroboration",
            "Pending"
        )

    ]


    response = generate_response(
        severity
    )


    return {

        "type":
            disaster_type,

        "location":
            location,

        "lat":
            lat,

        "lon":
            lon,

        "severity":
            severity,

        "confidence":
            confidence,

        "affected":
            affected,

        "signals":
            verification_signals,

        "response":
            response

    }


# ============================================================
# ADD INCIDENT TO COMMAND CENTER
# ============================================================

def add_incident_to_command_center(
    analysis,
    original_report
):

    next_number = (
        1043
        + len(
            st.session_state.incidents
        )
    )


    incident_id = (
        f"INC-{next_number}"
    )


    new_incident = {

        "id":
            incident_id,

        "type":
            analysis["type"],

        "location":
            analysis["location"],

        "lat":
            analysis["lat"],

        "lon":
            analysis["lon"],

        "severity":
            analysis["severity"],

        "confidence":
            analysis["confidence"],

        "affected":
            analysis["affected"],

        "status":
            "ACTIVE",

        "description":
            original_report[:250],

        "source":
            "AI Analyzer",

        "time":
            "Just now"

    }


    # Add newest incident first

    st.session_state.incidents.insert(
        0,
        new_incident
    )


    return incident_id

# ============================================================
# AI RESOURCE MATCHING
# ============================================================

def calculate_distance_km(lat1, lon1, lat2, lon2):

    radius = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        +
        math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    return 2 * radius * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )


def recommend_resources(incident):

    incident_lat = incident["lat"]
    incident_lon = incident["lon"]
    incident_location = incident["location"].lower()

    available_rescue = [
        resource
        for resource in RESOURCES
        if resource["type"] == "Rescue Team"
        and resource["status"] == "AVAILABLE"
    ]

    scored_rescue = []

    for resource in available_rescue:

        distance = calculate_distance_km(
            incident_lat,
            incident_lon,
            resource["lat"],
            resource["lon"]
        )

        location_bonus = (
            2
            if resource["location"].lower() == incident_location
            else 0
        )

        score = location_bonus + (1 / (distance + 0.5))

        scored_rescue.append(
            (score, distance, resource)
        )

    scored_rescue.sort(
        key=lambda item: item[0],
        reverse=True
    )

    rescue_team = (
        scored_rescue[0][2]
        if scored_rescue
        else None
    )

    rescue_distance = (
        scored_rescue[0][1]
        if scored_rescue
        else None
    )

    hospitals = [
        resource
        for resource in RESOURCES
        if resource["type"] == "Hospital"
        and resource["status"] == "AVAILABLE"
    ]

    scored_hospitals = []

    for resource in hospitals:

        distance = calculate_distance_km(
            incident_lat,
            incident_lon,
            resource["lat"],
            resource["lon"]
        )

        scored_hospitals.append(
            (distance, resource)
        )

    scored_hospitals.sort(
        key=lambda item: item[0]
    )

    hospital = (
        scored_hospitals[0][1]
        if scored_hospitals
        else None
    )

    hospital_distance = (
        scored_hospitals[0][0]
        if scored_hospitals
        else None
    )

    shelters = [
        resource
        for resource in RESOURCES
        if resource["type"] == "Shelter"
        and resource["status"] == "AVAILABLE"
    ]

    scored_shelters = []

    for resource in shelters:

        distance = calculate_distance_km(
            incident_lat,
            incident_lon,
            resource["lat"],
            resource["lon"]
        )

        scored_shelters.append(
            (distance, resource)
        )

    scored_shelters.sort(
        key=lambda item: item[0]
    )

    shelter = (
        scored_shelters[0][1]
        if scored_shelters
        else None
    )

    shelter_distance = (
        scored_shelters[0][0]
        if scored_shelters
        else None
    )

    eta_minutes = None

    if rescue_distance is not None:
        eta_minutes = max(
            5,
            round(rescue_distance / 0.45)
        )

    return {
        "rescue_team": rescue_team,
        "rescue_distance": rescue_distance,
        "eta_minutes": eta_minutes,
        "hospital": hospital,
        "hospital_distance": hospital_distance,
        "shelter": shelter,
        "shelter_distance": shelter_distance
    }

# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    # Logo

    st.markdown(
        '<div class="login-logo">🚨</div>',
        unsafe_allow_html=True
    )

    # Title

    st.markdown(
        '<div class="login-title">DRISHTI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="login-sub">
            Disaster Response Intelligence & Situational Tracking Interface
            <br>
            <b>From scattered information to actionable response.</b>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Username

    username = st.text_input(
        "Username",
        placeholder="Enter your username"
    )

    # Password

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    # Role

    role = st.selectbox(
        "Access as",
        [
            "Emergency Responder",
            "Administrator",
            "Citizen"
        ]
    )

    st.write("")

    # Login button

    login = st.button(
        "🔐  ENTER DRISHTI",
        use_container_width=True,
        type="primary"
    )

    if login:

        users = {

            "admin": {
                "password": "1234",
                "role": "Administrator"
            },

            "responder": {
                "password": "1234",
                "role": "Emergency Responder"
            },

            "citizen": {
                "password": "1234",
                "role": "Citizen"
            }

        }

        # Check credentials

        if (
            username in users
            and
            password == users[username]["password"]
            and
            role == users[username]["role"]
        ):

            st.session_state.logged_in = True

            st.session_state.username = username

            st.session_state.role = role

            st.rerun()

        else:

            st.error(
                "Invalid username, password or selected role."
            )

    st.markdown(
        '''
        <div style="
            text-align:center;
            margin-top:20px;
            color:#16a34a;
            font-weight:700;
        ">
            🟢 Emergency Network Online
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # Demo credentials

    with st.expander("🔑 Demo Credentials"):

        st.write("**Emergency Responder**")

        st.code(
            "Username: responder\nPassword: 1234"
        )

        st.write("**Administrator**")

        st.code(
            "Username: admin\nPassword: 1234"
        )

        st.write("**Citizen**")

        st.code(
            "Username: citizen\nPassword: 1234"
        )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def sidebar_navigation():

    # Logo

    st.sidebar.markdown(
        """
        <div style="
            text-align:center;
            padding:10px 0 5px 0;
        ">

            <div style="
                font-size:38px;
            ">
                🚨
            </div>

            <div style="
                font-size:24px;
                font-weight:800;
                color:#f8fafc;
            ">
                DRISHTI
            </div>

            <div style="
                font-size:11px;
                color:#89a4bf;
            ">
                DISASTER INTELLIGENCE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.divider()

    # Logged-in user

    st.sidebar.markdown(
        f"""
        <div style="
            background:#102238;
            border:1px solid #1d344d;
            border-radius:12px;
            padding:12px;
            margin-bottom:10px;
        ">

            <div style="
                color:#8fa9c2;
                font-size:11px;
            ">
                LOGGED IN AS
            </div>

            <div style="
                color:#f8fafc;
                font-weight:700;
                margin-top:3px;
            ">
                👤 {st.session_state.username}
            </div>

            <div style="
                color:#7dd3fc;
                font-size:12px;
                margin-top:3px;
            ">
                {st.session_state.role}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation

    st.sidebar.markdown(
        "### NAVIGATION"
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "Command Center",
            "Landslide Risk Monitoring",
            "NER Risk Map",
            "AI Incident Analyzer",
            "Incident Verification",
            "Resource Allocation",
            "Citizen Reports",
            "Analytics"
        ],
        label_visibility="collapsed"
    )

    st.sidebar.divider()

    # System status

    st.sidebar.markdown(
        """
        <div style="
            background:#102e24;
            border:1px solid #1c5a40;
            border-radius:10px;
            padding:9px;
            text-align:center;
            color:#86efac;
            font-size:12px;
            font-weight:700;
        ">
            🟢 SYSTEM ONLINE
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.write("")

    # Logout

    if st.sidebar.button(
        "↪ Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.username = None

        st.session_state.role = None

        st.session_state.last_analysis = None

        st.rerun()

    return page
# ============================================================
# COMMAND CENTER
# ============================================================

def command_center():

    # --------------------------------------------------------
    # CALCULATE LIVE INCIDENT STATISTICS
    # --------------------------------------------------------

    active_incidents = [
        incident
        for incident in st.session_state.incidents
        if incident["status"] == "ACTIVE"
    ]

    critical_incidents = [
        incident
        for incident in active_incidents
        if incident["severity"] == "CRITICAL"
    ]

    high_incidents = [
        incident
        for incident in active_incidents
        if incident["severity"] == "HIGH"
    ]

    total_affected = sum(
        incident["affected"]
        for incident in active_incidents
    )


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="hero">

            <h1>
                🚨 Emergency Command Center
            </h1>

            <p>
                Real-time situational awareness •
                AI prioritization •
                emergency response coordination
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # TOP STATUS BAR
    # --------------------------------------------------------

    status_col1, status_col2 = st.columns([3, 1])

    with status_col1:

        st.caption(
            f"Last synchronized: "
            f"{datetime.now().strftime('%d %b %Y • %H:%M:%S')}"
        )

    with status_col2:

        st.success(
            "LIVE SYSTEM"
        )


    # --------------------------------------------------------
    # KEY METRICS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📊 Situation Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)


    # Active incidents

    with c1:

        st.markdown(
            f"""
            <div class="metric">

                <div class="metric-value">
                    {len(active_incidents)}
                </div>

                <div class="metric-label">
                    ACTIVE INCIDENTS
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # Critical incidents

    with c2:

        st.markdown(
            f"""
            <div class="metric">

                <div class="metric-value">
                    {len(critical_incidents)}
                </div>

                <div class="metric-label">
                    CRITICAL INCIDENTS
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # Affected people

    with c3:

        st.markdown(
            f"""
            <div class="metric">

                <div class="metric-value">
                    {total_affected:,}
                </div>

                <div class="metric-label">
                    PEOPLE AFFECTED
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # Available resources

    with c4:

        st.markdown(
            """
            <div class="metric">

                <div class="metric-value">
                    18
                </div>

                <div class="metric-label">
                    RESOURCES AVAILABLE
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")


    # --------------------------------------------------------
    # INCIDENT MAP
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🗺️ Live Incident Map</div>',
        unsafe_allow_html=True
    )


    if active_incidents:

        map_data = pd.DataFrame(

            [
                {
                    "lat":
                        incident["lat"],

                    "lon":
                        incident["lon"]
                }

                for incident
                in active_incidents
            ]

        )


        st.map(
            map_data,

            latitude="lat",

            longitude="lon",

            zoom=7,

            height=390
        )

    else:

        st.info(
            "No active incidents currently reported."
        )



    # --------------------------------------------------------
    # OPERATIONAL RESOURCE LAYER
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🚑 Operational Resources Near Incidents'
        '</div>',
        unsafe_allow_html=True
    )

    resource_df = pd.DataFrame(
        [
            {
                "Resource": resource["name"],
                "Type": resource["type"],
                "Location": resource["location"],
                "Status": resource["status"],
                "Capacity": resource["capacity"]
            }
            for resource in RESOURCES
        ]
    )

    st.dataframe(
        resource_df,
        hide_index=True,
        use_container_width=True
    )

    st.write("")


    # --------------------------------------------------------
    # INCIDENT + AI PANEL
    # --------------------------------------------------------

    incident_col, ai_col = st.columns(
        [1.6, 1]
    )


    # ========================================================
    # PRIORITY INCIDENTS
    # ========================================================

    with incident_col:

        st.markdown(
            '<div class="section-title">'
            '🚨 Priority Incident Queue'
            '</div>',
            unsafe_allow_html=True
        )


        # Sort by severity

        severity_order = {

            "CRITICAL": 0,

            "HIGH": 1,

            "MEDIUM": 2,

            "LOW": 3

        }


        sorted_incidents = sorted(

            active_incidents,

            key=lambda x:
                severity_order.get(
                    x["severity"],
                    4
                )

        )


        if not sorted_incidents:

            st.success(
                "No active incidents."
            )


        for incident in sorted_incidents:


            # Determine styling

            if incident["severity"] == "CRITICAL":

                card_class = "critical"

                severity_pill = "pill-red"

                icon = "🔴"


            elif incident["severity"] == "HIGH":

                card_class = "high"

                severity_pill = "pill-orange"

                icon = "🟠"


            else:

                card_class = "medium"

                severity_pill = "pill-blue"

                icon = "🔵"


            st.markdown(

                f"""
                <div class="card {card_class}">

                    <div>

                        <span class="pill {severity_pill}">
                            {incident["severity"]}
                        </span>

                        <span class="pill pill-green">
                            {incident["status"]}
                        </span>

                    </div>


                    <h3>
                        {icon}
                        {incident["type"]}
                        —
                        {incident["location"]}
                    </h3>


                    <div class="muted">

                        {incident["id"]}
                        &nbsp; • &nbsp;
                        {incident["time"]}
                        &nbsp; • &nbsp;
                        Source:
                        {incident["source"]}

                    </div>


                    <p>
                        {incident["description"]}
                    </p>


                    <div>

                        <b>
                            AI Confidence:
                        </b>

                        {incident["confidence"]}%


                        &nbsp;&nbsp;&nbsp;


                        <b>
                            Affected:
                        </b>

                        {incident["affected"]}

                    </div>

                </div>
                """,

                unsafe_allow_html=True

            )


    # ========================================================
    # AI RESPONSE RECOMMENDATION
    # ========================================================

    with ai_col:

        st.markdown(
            '<div class="section-title">'
            '⚡ AI Response Recommendation'
            '</div>',
            unsafe_allow_html=True
        )


        if critical_incidents:

            critical = critical_incidents[0]


            st.markdown(

                f"""
                <div class="ai-result">

                    <div class="ai-title">
                        🔴 CRITICAL RESPONSE REQUIRED
                    </div>


                    <h2>
                        {critical["type"]}
                    </h2>


                    <p>
                        📍
                        <b>
                            {critical["location"]}
                        </b>
                    </p>


                    <p class="muted">

                        Confidence:
                        {critical["confidence"]}%

                        <br>

                        Estimated affected:
                        {critical["affected"]}

                    </p>


                    <hr>


                    <b>
                        Recommended actions
                    </b>


                    <p>
                        🚑 Dispatch nearest rescue team
                    </p>

                    <p>
                        🏥 Prioritize hospital capacity
                    </p>

                    <p>
                        🏠 Identify nearby shelter
                    </p>

                    <p>
                        📢 Issue targeted emergency alert
                    </p>

                    <p>
                        🚧 Restrict access to affected zone
                    </p>

                </div>
                """,

                unsafe_allow_html=True

            )


        elif high_incidents:

            high = high_incidents[0]


            st.warning(
                f"""
                HIGH PRIORITY INCIDENT

                {high["type"]}
                reported at {high["location"]}.

                Response resources should be prepared.
                """
            )


        else:

            st.success(
                "🟢 No critical incidents "
                "requiring immediate escalation."
            )


    # --------------------------------------------------------
    # RESPONSE SUMMARY
    # --------------------------------------------------------

    st.write("")

    st.markdown(
        '<div class="section-title">'
        '📡 Operational Summary'
        '</div>',
        unsafe_allow_html=True
    )


    summary_col1, summary_col2, summary_col3 = st.columns(3)


    with summary_col1:

        st.markdown(
            """
            <div class="card">

                <h3>
                    📥 Incoming Reports
                </h3>

                <div class="metric-value">
                    27
                </div>

                <div class="muted">
                    Reports received today
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with summary_col2:

        st.markdown(
            """
            <div class="card">

                <h3>
                    🔎 Verified Incidents
                </h3>

                <div class="metric-value">
                    14
                </div>

                <div class="muted">
                    Cross-source validated
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with summary_col3:

        st.markdown(
            """
            <div class="card">

                <h3>
                    ⚡ Response Teams
                </h3>

                <div class="metric-value">
                    12 / 18
                </div>

                <div class="muted">
                    Teams currently available
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )
        # ============================================================
# LANDSLIDE RISK MONITORING
# ============================================================

def landslide_risk_monitoring():
    # Keep the latest analyses for a simple risk trend.
    if "landslide_risk_history" not in st.session_state:
        st.session_state.landslide_risk_history = []


    st.markdown(
        """
        <div class="hero">
            <h1>⛰️ Landslide Risk Monitoring</h1>
            <p>
                AI-based environmental risk assessment and
                early warning for landslide-prone regions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # NER LOCATION
    st.markdown(
        '<div class="section-title">📍 Northeast Region</div>',
        unsafe_allow_html=True
    )

    ner_locations = [
        "Sikkim",
        "Arunachal Pradesh",
        "Assam",
        "Meghalaya",
        "Nagaland",
        "Manipur",
        "Mizoram",
        "Tripura",
        "Jammu & Kashmir"
    ]

    selected_region = st.selectbox(
        "Select monitoring region",
        ner_locations
    )

    st.info(
        f"📡 Monitoring landslide risk for **{selected_region}**"
    )

    st.markdown(
        '<div class="section-title">🌦️ Environmental Conditions</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        rainfall = st.slider("🌧️ Rainfall Risk", 0, 100, 70)
        soil_moisture = st.slider("💧 Soil Moisture", 0, 100, 65)

    with col2:
        slope = st.slider("⛰️ Slope Risk", 0, 100, 60)
        elevation = st.slider("🏔️ Elevation Exposure", 0, 100, 50)

    with col3:
        vegetation_loss = st.slider("🌱 Vegetation Loss", 0, 100, 40)
        terrain_instability = st.slider("⚠️ Terrain Instability", 0, 100, 60)

    st.write("")

    if st.button(
        "🔍 ANALYZE LANDSLIDE RISK",
        use_container_width=True,
        type="primary"
    ):
        try:
            response = requests.post(
                f"{BACKEND_URL}/risk/predict",
                json={
                    "rainfall": rainfall,
                    "soil_moisture": soil_moisture,
                    "slope": slope,
                    "elevation": elevation,
                    "vegetation_loss": vegetation_loss,
                    "terrain_instability": terrain_instability
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                risk_score = result["risk_score"]
                risk_level = result["risk_level"]
                warning = result["early_warning"]
                confidence = float(result.get("confidence", 0))

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("LANDSLIDE RISK", f"{risk_score} / 100")

                with c2:
                    st.metric("RISK LEVEL", risk_level)

                with c3:
                    st.metric(
                        "EARLY WARNING",
                        "ACTIVE" if warning else "NORMAL"
                    )

                st.caption(f"🤖 Random Forest confidence: {confidence:.1f}%")

                if risk_level == "CRITICAL":
                    st.error(
                        "🚨 CRITICAL LANDSLIDE RISK — "
                        "EARLY WARNING ACTIVE"
                    )
                elif risk_level == "HIGH":
                    st.warning(
                        "⚠️ HIGH LANDSLIDE RISK — "
                        "PRECAUTIONARY ACTION ADVISED"
                    )
                elif risk_level == "MODERATE":
                    st.info(
                        "🟡 MODERATE LANDSLIDE RISK — "
                        "CONTINUE MONITORING"
                    )
                else:
                    st.success("🟢 LOW LANDSLIDE RISK")

                # AI DECISION SUPPORT — RECOMMENDED ACTIONS
                st.markdown(
                    '<div class="section-title">🚨 AI Recommended Actions</div>',
                    unsafe_allow_html=True
                )

                if risk_level == "CRITICAL":
                    st.error(
                        """
                        **🔴 IMMEDIATE ACTION REQUIRED**

                        • Issue an early warning for vulnerable areas.  
                        • Restrict access to high-risk slopes and exposed routes.  
                        • Deploy nearby response resources and keep evacuation support ready.  
                        • Increase monitoring frequency and reassess environmental conditions.
                        """
                    )
                elif risk_level == "HIGH":
                    st.warning(
                        """
                        **🟠 PREPARE RESPONSE**

                        • Increase monitoring of vulnerable slopes.  
                        • Inspect roads, settlements and other exposed locations.  
                        • Keep response teams and essential resources on standby.  
                        • Reassess the risk if rainfall or soil moisture increases.
                        """
                    )
                elif risk_level == "MODERATE":
                    st.info(
                        """
                        **🟡 ENHANCED MONITORING**

                        • Continue monitoring rainfall and soil moisture.  
                        • Watch for rapid changes in slope or terrain conditions.  
                        • Review vulnerable locations and maintain response readiness.
                        """
                    )
                else:
                    st.success(
                        """
                        **🟢 ROUTINE MONITORING**

                        • Continue routine environmental monitoring.  
                        • Maintain normal response readiness.  
                        • Recalculate risk if environmental conditions change.
                        """
                    )

                st.caption(
                    "Decision-support recommendations are generated from the calculated "
                    "prototype risk level. Final operational decisions remain with authorized responders."
                )

                # RISK TREND
                st.session_state.landslide_risk_history.append({
                    "Analysis": len(st.session_state.landslide_risk_history) + 1,
                    "Risk Score": float(risk_score)
                })

                # Keep only the latest 10 analyses.
                st.session_state.landslide_risk_history = (
                    st.session_state.landslide_risk_history[-10:]
                )

                st.markdown(
                    '<div class="section-title">📈 Risk Trend</div>',
                    unsafe_allow_html=True
                )

                trend_df = pd.DataFrame(
                    st.session_state.landslide_risk_history
                )

                st.line_chart(
                    trend_df.set_index("Analysis")["Risk Score"],
                    y_label="Risk Score (0–100)",
                    x_label="Analysis"
                )

                if len(trend_df) >= 2:
                    previous_score = float(trend_df.iloc[-2]["Risk Score"])
                    current_score = float(trend_df.iloc[-1]["Risk Score"])

                    if current_score > previous_score:
                        st.warning(
                            f"📈 Risk is increasing: "
                            f"{previous_score:.1f} → {current_score:.1f}"
                        )
                    elif current_score < previous_score:
                        st.success(
                            f"📉 Risk is decreasing: "
                            f"{previous_score:.1f} → {current_score:.1f}"
                        )
                    else:
                        st.info(
                            f"➡️ Risk is stable at {current_score:.1f}/100"
                        )


            else:
                st.error(
                    f"Risk prediction service returned "
                    f"status {response.status_code}."
                )

        except requests.RequestException:
            st.error(
                "Unable to connect to DRISHTI backend. "
                "Make sure FastAPI is running."
            )


# ============================================================
# AI INCIDENT ANALYZER
# ============================================================

def ner_landslide_risk_map():
    """NER + J&K risk overview using synthetic environmental conditions."""
    st.markdown(
        '<div class="hero"><h1>🗺️ NER + J&K Landslide Risk Map</h1>'
        '<p>Environmental-condition based landslide risk assessment</p></div>',
        unsafe_allow_html=True
    )

    # Synthetic environmental inputs for prototype demonstration.
    # These are NOT government incident records and are not presented as live risk.
    synthetic_environment = {
        "Sikkim": {
            "latitude": 27.5330, "longitude": 88.5122,
            "rainfall": 85, "soil_moisture": 78, "slope": 90,
            "elevation": 82, "vegetation_loss": 45, "terrain_instability": 80
        },
        "Arunachal Pradesh": {
            "latitude": 28.2180, "longitude": 94.7278,
            "rainfall": 78, "soil_moisture": 74, "slope": 86,
            "elevation": 88, "vegetation_loss": 40, "terrain_instability": 75
        },
        "Assam": {
            "latitude": 26.2006, "longitude": 92.9376,
            "rainfall": 62, "soil_moisture": 65, "slope": 35,
            "elevation": 25, "vegetation_loss": 30, "terrain_instability": 40
        },
        "Meghalaya": {
            "latitude": 25.4670, "longitude": 91.3662,
            "rainfall": 82, "soil_moisture": 76, "slope": 72,
            "elevation": 65, "vegetation_loss": 38, "terrain_instability": 68
        },
        "Nagaland": {
            "latitude": 26.1584, "longitude": 94.5624,
            "rainfall": 68, "soil_moisture": 66, "slope": 64,
            "elevation": 62, "vegetation_loss": 35, "terrain_instability": 58
        },
        "Manipur": {
            "latitude": 24.6637, "longitude": 93.9063,
            "rainfall": 75, "soil_moisture": 72, "slope": 70,
            "elevation": 60, "vegetation_loss": 42, "terrain_instability": 70
        },
        "Mizoram": {
            "latitude": 23.1645, "longitude": 92.9376,
            "rainfall": 80, "soil_moisture": 75, "slope": 82,
            "elevation": 58, "vegetation_loss": 48, "terrain_instability": 78
        },
        "Tripura": {
            "latitude": 23.9408, "longitude": 91.9882,
            "rainfall": 58, "soil_moisture": 60, "slope": 42,
            "elevation": 30, "vegetation_loss": 28, "terrain_instability": 38
        },
        "Jammu & Kashmir": {
            "latitude": 33.7782, "longitude": 76.5762,
            "rainfall": 65, "soil_moisture": 58, "slope": 80,
            "elevation": 90, "vegetation_loss": 35, "terrain_instability": 72
        },
    }

    def calculate_region_risk(values):
        """Send synthetic environmental conditions through the same FastAPI risk engine."""
        try:
            response = requests.post(
                f"{BACKEND_URL}/risk/predict",
                json={
                    "rainfall": values["rainfall"],
                    "soil_moisture": values["soil_moisture"],
                    "slope": values["slope"],
                    "elevation": values["elevation"],
                    "vegetation_loss": values["vegetation_loss"],
                    "terrain_instability": values["terrain_instability"],
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            # Fallback keeps the map usable if FastAPI is temporarily unavailable.
            risk = (
                values["rainfall"] * 0.30
                + values["soil_moisture"] * 0.20
                + values["slope"] * 0.20
                + values["elevation"] * 0.10
                + values["vegetation_loss"] * 0.10
                + values["terrain_instability"] * 0.10
            )
            risk = round(min(max(risk, 0), 100), 2)
            if risk >= 80:
                level, warning = "CRITICAL", True
            elif risk >= 60:
                level, warning = "HIGH", True
            elif risk >= 40:
                level, warning = "MODERATE", False
            else:
                level, warning = "LOW", False
            return {
                "risk_score": risk,
                "risk_level": level,
                "early_warning": warning
            }

    rows = []
    for region, values in synthetic_environment.items():
        result = calculate_region_risk(values)
        rows.append({
            "Region": region,
            "Latitude": values["latitude"],
            "Longitude": values["longitude"],
            "Risk Score": result["risk_score"],
            "Risk Level": result["risk_level"],
            "Early Warning": "ACTIVE" if result["early_warning"] else "MONITOR"
        })

    risk_data = pd.DataFrame(rows)

    st.info(
        "🧪 Prototype mode: risk values are calculated from synthetic environmental "
        "conditions. No government incident records are used."
    )

    st.markdown(
        '<div class="section-title">📍 Regional Risk Overview</div>',
        unsafe_allow_html=True
    )

    selected_map_region = st.selectbox(
        "Select a region to inspect",
        risk_data["Region"].tolist(),
        key="ner_map_region"
    )

    selected = risk_data[risk_data["Region"] == selected_map_region].iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("RISK SCORE", f'{float(selected["Risk Score"]):.1f}/100')
    with c2:
        st.metric("RISK LEVEL", selected["Risk Level"])
    with c3:
        st.metric("EARLY WARNING", selected["Early Warning"])

    map_points = risk_data.rename(
        columns={"Latitude": "lat", "Longitude": "lon"}
    )[["lat", "lon"]]

    st.map(map_points, zoom=5)

    st.caption(
        "Map locations are representative coordinates. Environmental values are "
        "synthetic demo inputs; a deployed system can replace them with validated "
        "sensor, weather, satellite, or other authorized environmental feeds."
    )

    st.markdown(
        '<div class="section-title">🌦️ Environmental Conditions Used</div>',
        unsafe_allow_html=True
    )

    env = synthetic_environment[selected_map_region]
    e1, e2, e3 = st.columns(3)
    with e1:
        st.metric("RAINFALL RISK", env["rainfall"])
        st.metric("SOIL MOISTURE", env["soil_moisture"])
    with e2:
        st.metric("SLOPE RISK", env["slope"])
        st.metric("ELEVATION EXPOSURE", env["elevation"])
    with e3:
        st.metric("VEGETATION LOSS", env["vegetation_loss"])
        st.metric("TERRAIN INSTABILITY", env["terrain_instability"])

    st.markdown(
        '<div class="section-title">📊 Regional Risk Table</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        risk_data[["Region", "Risk Score", "Risk Level", "Early Warning"]],
        use_container_width=True,
        hide_index=True
    )

    score = float(selected["Risk Score"])
    if score >= 80:
        st.error(
            f"🚨 {selected_map_region}: CRITICAL risk. "
            "Immediate response review and intensified monitoring recommended."
        )
    elif score >= 60:
        st.warning(
            f"⚠️ {selected_map_region}: HIGH risk. "
            "Increase monitoring and prepare response resources."
        )
    elif score >= 40:
        st.info(
            f"🟡 {selected_map_region}: MODERATE risk. "
            "Continue monitoring environmental conditions."
        )
    else:
        st.success(
            f"🟢 {selected_map_region}: LOW risk. "
            "Continue routine monitoring."
        )


def ai_incident_analyzer():

    st.markdown(
        """
        <div class="hero">

            <h1>
                🤖 AI Incident Analyzer
            </h1>

            <p>
                Transform unstructured emergency reports
                into prioritized, actionable disaster intelligence.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # INFORMATION BANNER
    # --------------------------------------------------------

    st.info(
        "💡 Try: "
        "Severe flooding in Srinagar. "
        "50 people are trapped, roads are blocked "
        "and urgent rescue is required."
    )


    # --------------------------------------------------------
    # REPORT INPUT
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📥 Incoming Emergency Report'
        '</div>',
        unsafe_allow_html=True
    )


    report = st.text_area(

        "Emergency report",

        height=170,

        placeholder=(
            "Paste a citizen report, field report, "
            "emergency alert or incident description here..."
        ),

        label_visibility="collapsed"

    )


    # --------------------------------------------------------
    # ACTION BUTTONS
    # --------------------------------------------------------

    button_col1, button_col2 = st.columns(2)


    with button_col1:

        analyze_button = st.button(

            "🤖 ANALYZE INCIDENT",

            use_container_width=True,

            type="primary"

        )


    with button_col2:

        clear_button = st.button(

            "🧹 CLEAR ANALYSIS",

            use_container_width=True

        )


    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    if clear_button:

        st.session_state.last_analysis = None

        st.rerun()


    # --------------------------------------------------------
    # ANALYZE
    # --------------------------------------------------------

    if analyze_button:

        if not report.strip():

            st.warning(
                "⚠️ Please enter an emergency report first."
            )

        else:

            with st.spinner(
                "🤖 DRISHTI AI is analyzing the incident..."
            ):

                analysis = analyze_incident(
                    report
                )

                st.session_state.last_analysis = analysis


            st.success(
                "✓ Incident analysis completed."
            )


    # --------------------------------------------------------
    # GET LAST ANALYSIS
    # --------------------------------------------------------

    analysis = (
        st.session_state.last_analysis
    )


    if analysis is None:

        st.markdown(
            """
            <div class="card">

                <h3>
                    🧠 Waiting for incident data
                </h3>

                <p class="muted">

                    DRISHTI will identify the disaster type,
                    location, severity, confidence and
                    recommended response actions.

                </p>

            </div>
            """,

            unsafe_allow_html=True

        )

        return


    # ========================================================
    # ANALYSIS RESULT
    # ========================================================

    st.markdown(
        """
        <div class="ai-result">

            <div class="ai-title">
                ✓ AI ANALYSIS COMPLETE
            </div>

            <p class="muted">
                Structured intelligence extracted from
                the incoming emergency report.
            </p>

        </div>
        """,

        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CORE RESULTS
    # --------------------------------------------------------

    st.write("")

    result_col1, result_col2, result_col3, result_col4 = (
        st.columns(4)
    )


    with result_col1:

        st.metric(
            "🚨 Disaster Type",
            analysis["type"]
        )


    with result_col2:

        st.metric(
            "📍 Location",
            analysis["location"]
        )


    with result_col3:

        st.metric(
            "⚠️ Severity",
            analysis["severity"]
        )


    with result_col4:

        st.metric(
            "🎯 Confidence",
            f'{analysis["confidence"]}%'
        )


    st.write("")


    # ========================================================
    # DETAILS
    # ========================================================

    details_col1, details_col2 = st.columns(
        [1, 1]
    )


    # --------------------------------------------------------
    # VERIFICATION SIGNALS
    # --------------------------------------------------------

    with details_col1:

        st.markdown(
            '<div class="section-title">'
            '🔎 Verification Signals'
            '</div>',
            unsafe_allow_html=True
        )


        signal_data = pd.DataFrame(

            analysis["signals"],

            columns=[
                "Signal",
                "Assessment"
            ]

        )


        st.dataframe(

            signal_data,

            hide_index=True,

            use_container_width=True

        )


    # --------------------------------------------------------
    # RESPONSE RECOMMENDATION
    # --------------------------------------------------------

    with details_col2:

        st.markdown(
            '<div class="section-title">'
            '⚡ Recommended Response'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )


        for action in analysis["response"]:

            st.write(
                action
            )


        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # ========================================================
    # IMPACT ASSESSMENT
    # ========================================================

    st.write("")

    st.markdown(
        '<div class="section-title">'
        '📊 Preliminary Impact Assessment'
        '</div>',
        unsafe_allow_html=True
    )


    impact_col1, impact_col2, impact_col3 = (
        st.columns(3)
    )


    with impact_col1:

        st.metric(
            "Estimated People Affected",
            analysis["affected"]
        )


    with impact_col2:

        st.metric(
            "Response Priority",
            analysis["severity"]
        )


    with impact_col3:

        if analysis["confidence"] >= 90:

            confidence_status = "HIGH"

        elif analysis["confidence"] >= 80:

            confidence_status = "MODERATE"

        else:

            confidence_status = "LOW"


        st.metric(
            "Evidence Confidence",
            confidence_status
        )


    # ========================================================
    # COMMAND CENTER CONNECTION
    # ========================================================

    st.write("")

    st.markdown(
        """
        <div class="ai-result">

            <div class="ai-title">
                🚨 Operational Handoff
            </div>

            <p>
                The AI has converted this report into
                a structured incident. Add it to the
                Command Center to make it visible to
                emergency responders.
            </p>

        </div>
        """,

        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # ADD TO COMMAND CENTER
    # --------------------------------------------------------

    if st.button(

        "🚨 ADD INCIDENT TO COMMAND CENTER",

        use_container_width=True,

        type="primary"

    ):

        # Make sure we have the original report

        original_report = report.strip()


        if not original_report:

            original_report = (
                "Incident analyzed by DRISHTI AI."
            )


        # Add incident

        incident_id = add_incident_to_command_center(

            analysis,

            original_report

        )


        # Clear previous analysis

        st.session_state.last_analysis = None


        st.success(
            f"✓ {incident_id} has been added "
            f"to the Command Center."
        )


        st.info(
            "Open **Command Center** from the sidebar "
            "to see the new incident on the live map "
            "and priority queue."
        )
        # ============================================================
# INCIDENT VERIFICATION
# ============================================================

def incident_verification():

    st.markdown(
        """
        <div class="hero">
            <h1>🔎 Incident Verification Center</h1>
            <p>
                DRISHTI validates synthetic environmental and citizen-report
                signals to prioritize potential landslide incidents.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Prototype-only incident set.
    # This page intentionally does not use government incident records.
    verification_incidents = [
        {
            "id": "INC-2042", "type": "Landslide", "location": "Sikkim",
            "lat": 27.5330, "lon": 88.5122, "severity": "CRITICAL",
            "confidence": 92, "affected": 65, "status": "ACTIVE",
            "description": "Synthetic report: elevated rainfall, soil moisture and slope instability indicate a potential landslide zone.",
            "source": "Synthetic Environmental Simulation", "time": "12 min ago"
        },
        {
            "id": "INC-2041", "type": "Landslide", "location": "Arunachal Pradesh",
            "lat": 28.2180, "lon": 94.7278, "severity": "HIGH",
            "confidence": 87, "affected": 42, "status": "ACTIVE",
            "description": "Synthetic report: heavy rainfall conditions combined with steep terrain require increased monitoring.",
            "source": "Synthetic Environmental Simulation", "time": "28 min ago"
        },
        {
            "id": "INC-2040", "type": "Landslide", "location": "Meghalaya",
            "lat": 25.4670, "lon": 91.3662, "severity": "HIGH",
            "confidence": 89, "affected": 38, "status": "ACTIVE",
            "description": "Synthetic report: high soil moisture and terrain instability detected in a vulnerable zone.",
            "source": "Synthetic Environmental Simulation", "time": "41 min ago"
        },
        {
            "id": "INC-2039", "type": "Landslide", "location": "Mizoram",
            "lat": 23.1645, "lon": 92.9376, "severity": "HIGH",
            "confidence": 86, "affected": 31, "status": "ACTIVE",
            "description": "Synthetic report: steep slope conditions and vegetation loss increase landslide susceptibility.",
            "source": "Synthetic Environmental Simulation", "time": "55 min ago"
        },
        {
            "id": "INC-2038", "type": "Landslide", "location": "Manipur",
            "lat": 24.6637, "lon": 93.9063, "severity": "HIGH",
            "confidence": 84, "affected": 27, "status": "ACTIVE",
            "description": "Synthetic report: elevated terrain instability combined with wet soil conditions.",
            "source": "Synthetic Environmental Simulation", "time": "1 hr ago"
        },
        {
            "id": "INC-2037", "type": "Landslide", "location": "Jammu & Kashmir",
            "lat": 33.7782, "lon": 76.5762, "severity": "HIGH",
            "confidence": 85, "affected": 25, "status": "ACTIVE",
            "description": "Synthetic report: steep slopes, high elevation exposure and terrain instability require monitoring.",
            "source": "Synthetic Environmental Simulation", "time": "1 hr ago"
        },
        {
            "id": "INC-2036", "type": "Landslide", "location": "Nagaland",
            "lat": 26.1584, "lon": 94.5624, "severity": "MODERATE",
            "confidence": 78, "affected": 18, "status": "ACTIVE",
            "description": "Synthetic report: moderate rainfall and slope conditions indicate continued monitoring.",
            "source": "Synthetic Environmental Simulation", "time": "1 hr ago"
        },
        {
            "id": "INC-2035", "type": "Landslide", "location": "Tripura",
            "lat": 23.9408, "lon": 91.9882, "severity": "MODERATE",
            "confidence": 74, "affected": 12, "status": "ACTIVE",
            "description": "Synthetic report: moderate environmental risk indicators detected.",
            "source": "Synthetic Environmental Simulation", "time": "2 hrs ago"
        },
    ]

    st.markdown(
        '<div class="section-title">📡 Prototype Information Signals</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("👤 Synthetic Reports", "14")
    with c2:
        st.metric("🌦️ Environmental Signals", "6")
    with c3:
        st.metric("🛰️ Terrain Signals", "4")
    with c4:
        st.metric("🤖 AI Confidence", "91%")

    st.caption(
        "Prototype mode: these verification records are synthetic examples "
        "for demonstration and are not government incident records."
    )

    st.markdown(
        '<div class="section-title">🚨 Select Incident for Verification</div>',
        unsafe_allow_html=True
    )

    incident_options = {
        f'{incident["id"]} — {incident["type"]} — {incident["location"]}': incident
        for incident in verification_incidents
    }

    selected_label = st.selectbox(
        "Choose an incident",
        list(incident_options.keys()),
        key="verification_incident_selector"
    )

    selected_incident = incident_options[selected_label]

    st.write("")

    overview_col1, overview_col2 = st.columns([1.4, 1])

    with overview_col1:
        severity = selected_incident["severity"]

        if severity == "CRITICAL":
            st.error(f'🚨 {severity} — Immediate verification required')
        elif severity == "HIGH":
            st.warning(f'⚠️ {severity} — Priority verification required')
        else:
            st.info(f'🟡 {severity} — Continue monitoring')

        st.markdown(
            f"""
            **Location:** {selected_incident["location"]}

            **Incident:** {selected_incident["type"]}

            **Description:** {selected_incident["description"]}

            **Signal source:** {selected_incident["source"]}

            **Reported:** {selected_incident["time"]}
            """
        )

    with overview_col2:
        st.metric("AI CONFIDENCE", f'{selected_incident["confidence"]}%')
        st.metric("EST. AFFECTED", selected_incident["affected"])
        st.metric("STATUS", selected_incident["status"])

        st.progress(
            min(selected_incident["confidence"] / 100, 1.0),
            text=f'{selected_incident["confidence"]}% confidence'
        )

    st.markdown(
        '<div class="section-title">🧠 Verification Signals</div>',
        unsafe_allow_html=True
    )

    signal_col1, signal_col2, signal_col3 = st.columns(3)

    with signal_col1:
        st.metric("Rainfall Signal", "ELEVATED")
    with signal_col2:
        st.metric("Slope Signal", "ELEVATED")
    with signal_col3:
        st.metric("Terrain Signal", "ELEVATED")

    st.markdown(
        '<div class="section-title">📍 Incident Location</div>',
        unsafe_allow_html=True
    )

    location_df = pd.DataFrame([{
        "lat": selected_incident["lat"],
        "lon": selected_incident["lon"]
    }])

    st.map(location_df, zoom=6)


def resource_allocation():

    st.markdown(
        """
        <div class="hero">

            <h1>
                🚑 Smart Resource Allocation
            </h1>

            <p>
                Match critical incidents with the
                nearest suitable emergency resources.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # RESOURCE SUMMARY
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📊 Resource Availability'
        '</div>',
        unsafe_allow_html=True
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:
        st.metric(
            "🚑 Rescue Teams",
            "8 / 10"
        )

    with c2:
        st.metric(
            "🏥 Hospitals",
            "6 / 7"
        )

    with c3:
        st.metric(
            "🏠 Shelters",
            "12 / 15"
        )

    with c4:
        st.metric(
            "🚒 Emergency Units",
            "7 / 9"
        )


    st.write("")


    # --------------------------------------------------------
    # SELECT INCIDENT
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🎯 Select Incident'
        '</div>',
        unsafe_allow_html=True
    )


    active_incidents = [

        incident

        for incident
        in st.session_state.incidents

        if incident["status"] == "ACTIVE"

    ]


    if not active_incidents:

        st.success(
            "No active incidents requiring resources."
        )

        return


    incident_options = {

        f'{incident["id"]} — '
        f'{incident["type"]} — '
        f'{incident["location"]}':
            incident

        for incident
        in active_incidents

    }


    selected = st.selectbox(

        "Incident",

        list(
            incident_options.keys()
        )

    )


    incident = incident_options[selected]


    st.write("")


    # --------------------------------------------------------
    # INCIDENT SUMMARY
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="card">

            <span class="pill pill-red">
                {incident["severity"]}
            </span>

            <span class="pill pill-green">
                ACTIVE
            </span>

            <h2>
                {incident["type"]}
                —
                {incident["location"]}
            </h2>

            <p>
                {incident["description"]}
            </p>

            <b>
                Estimated affected:
            </b>

            {incident["affected"]}

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # AI MATCHING
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🤖 AI Resource Recommendation'
        '</div>',
        unsafe_allow_html=True
    )


    recommendations = recommend_resources(
        incident
    )

    rescue_team = recommendations["rescue_team"]
    rescue_distance = recommendations["rescue_distance"]
    eta_minutes = recommendations["eta_minutes"]
    hospital = recommendations["hospital"]
    hospital_distance = recommendations["hospital_distance"]
    shelter = recommendations["shelter"]
    shelter_distance = recommendations["shelter_distance"]

    if rescue_team:
        recommended_resource = rescue_team["name"]
    else:
        recommended_resource = "No rescue team available"

    if incident["severity"] == "CRITICAL":
        reason = (
            "Critical incident detected. DRISHTI prioritizes "
            "the nearest suitable available rescue team and "
            "supporting medical and shelter resources."
        )
    elif incident["severity"] == "HIGH":
        reason = (
            "High-priority incident detected. Available "
            "response resources are matched using location, "
            "availability and proximity."
        )
    else:
        reason = (
            "Incident requires monitoring and appropriate "
            "first-response support."
        )


    st.markdown(
        f"""
        <div class="ai-result">

            <div class="ai-title">
                ⚡ AI RESPONSE RECOMMENDATION
            </div>

            <h2>
                🚑 {recommended_resource}
            </h2>

            <p>
                {reason}
            </p>

            <hr>

            <h3>🚑 Rescue Team</h3>

            <p>
                {
                    rescue_team["name"]
                    if rescue_team
                    else "No available rescue team"
                }
            </p>

            <p class="muted">
                Status: {
                    rescue_team["status"]
                    if rescue_team
                    else "UNAVAILABLE"
                }
                <br>
                Distance: {
                    f"{rescue_distance:.1f} km"
                    if rescue_distance is not None
                    else "N/A"
                }
                <br>
                Estimated ETA: {
                    f"{eta_minutes} minutes"
                    if eta_minutes is not None
                    else "N/A"
                }
                <br>
                Capacity: {
                    rescue_team["capacity"]
                    if rescue_team
                    else "N/A"
                } responders
            </p>

            <h3>🏥 Medical Support</h3>

            <p>
                {
                    hospital["name"]
                    if hospital
                    else "No nearby hospital available"
                }
            </p>

            <p class="muted">
                Distance: {
                    f"{hospital_distance:.1f} km"
                    if hospital_distance is not None
                    else "N/A"
                }
                <br>
                Capacity: {
                    hospital["capacity"]
                    if hospital
                    else "N/A"
                }
            </p>

            <h3>🏠 Emergency Shelter</h3>

            <p>
                {
                    shelter["name"]
                    if shelter
                    else "No nearby shelter available"
                }
            </p>

            <p class="muted">
                Distance: {
                    f"{shelter_distance:.1f} km"
                    if shelter_distance is not None
                    else "N/A"
                }
                <br>
                Capacity: {
                    shelter["capacity"]
                    if shelter
                    else "N/A"
                }
            </p>

            <hr>

            <b>Selection factors</b>

            <p>
                ✓ Resource availability
                <br>
                ✓ Incident severity
                <br>
                ✓ Geographic proximity
                <br>
                ✓ Resource suitability
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.write("")


    # --------------------------------------------------------
    # AVAILABLE RESOURCES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🚨 Available Emergency Resources'
        '</div>',
        unsafe_allow_html=True
    )


    resources = pd.DataFrame({

        "Resource": [

            "NDRF Rescue Team A",

            "Rescue Team B",

            "District Hospital",

            "Emergency Shelter 01",

            "Fire & Emergency Unit",

            "Emergency Shelter 02"

        ],

        "Type": [

            "Rescue Team",

            "Rescue Team",

            "Hospital",

            "Shelter",

            "Fire & Rescue",

            "Shelter"

        ],

        "Location": [

            "Srinagar",

            "Pahalgam",

            "Srinagar",

            "Srinagar",

            "Anantnag",

            "Anantnag"

        ],

        "Status": [

            "AVAILABLE",

            "AVAILABLE",

            "AVAILABLE",

            "AVAILABLE",

            "BUSY",

            "AVAILABLE"

        ]

    })


    st.dataframe(

        resources,

        hide_index=True,

        use_container_width=True

    )


    # --------------------------------------------------------
    # DISPATCH BUTTON
    # --------------------------------------------------------

    if st.button(

        "🚑 DISPATCH RECOMMENDED RESOURCE",

        use_container_width=True,

        type="primary"

    ):

        if rescue_team:

            st.success(
                f"✓ {rescue_team['name']} "
                f"has been assigned to "
                f"{incident['id']}."
            )

            st.info(
                f"📍 Deployment location: "
                f"{incident['location']}"
            )

            st.info(
                f"⏱️ Estimated arrival: "
                f"{eta_minutes} minutes"
            )

            st.info(
                "⚡ Status: RESPONSE TEAM DISPATCHED"
            )

        else:

            st.error(
                "No available rescue team can currently "
                "be assigned."
            )

def citizen_reports():

    st.markdown(
        """
        <div class="hero">

            <h1>
                📱 Citizen Emergency Reporting
            </h1>

            <p>
                Report disasters directly to the
                DRISHTI emergency intelligence network.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.info(
        "🚨 In an actual deployment, this module can "
        "capture GPS coordinates, photos, videos and "
        "timestamped field evidence."
    )


    # --------------------------------------------------------
    # REPORT FORM
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📥 Submit Emergency Report'
        '</div>',
        unsafe_allow_html=True
    )


    with st.form(
        "citizen_emergency_report"
    ):

        disaster_type = st.selectbox(

            "Disaster Type",

            [
                "Flood",
                "Landslide",
                "Earthquake",
                "Fire",
                "Cyclone",
                "Other"
            ]

        )


        location = st.text_input(

            "Location",

            placeholder="Example: Srinagar"

        )


        description = st.text_area(

            "Describe the emergency",

            height=150,

            placeholder=(
                "Example: Severe flooding has entered "
                "houses. Several families are trapped "
                "and roads are blocked."
            )

        )


        affected = st.number_input(

            "Estimated people affected",

            min_value=1,

            max_value=100000,

            value=50

        )


        evidence = st.file_uploader(

            "Upload photo evidence (optional)",

            type=[
                "jpg",
                "jpeg",
                "png"
            ]

        )


        submit = st.form_submit_button(

            "🚨 SUBMIT EMERGENCY REPORT",

            use_container_width=True,

            type="primary"

        )


    # --------------------------------------------------------
    # PROCESS REPORT
    # --------------------------------------------------------

    if submit:

        if not location.strip():

            st.warning(
                "Please enter the incident location."
            )

            return


        if not description.strip():

            st.warning(
                "Please describe the emergency."
            )

            return


        # Combine information for AI

        report_text = (

            disaster_type
            + " "
            + location
            + " "
            + description

        )


        # Analyze using our AI engine

        analysis = analyze_incident(

            report_text

        )


        # Override affected estimate

        analysis["affected"] = int(
            affected
        )


        # Add incident

        incident_id = (
            add_incident_to_command_center(

                analysis,

                description

            )
        )


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        st.success(

            f"✓ Emergency report submitted successfully."

        )


        st.info(

            f"Incident ID: {incident_id}"

        )


        # ----------------------------------------------------
        # AI RESULT
        # ----------------------------------------------------

        result_col1, result_col2, result_col3 = (
            st.columns(3)
        )


        with result_col1:

            st.metric(

                "Disaster",

                analysis["type"]

            )


        with result_col2:

            st.metric(

                "AI Priority",

                analysis["severity"]

            )


        with result_col3:

            st.metric(

                "Confidence",

                f'{analysis["confidence"]}%'

            )


        st.success(

            "✓ The incident has been added to "
            "the Emergency Command Center."

        )


        st.info(

            "Open **Command Center** from the sidebar "
            "to view the incident on the map."

        )


        # Evidence status

        if evidence:

            st.success(
                "📷 Evidence uploaded successfully."
            )

        else:

            st.caption(
                "No photo evidence attached."
            )
            # ============================================================
# ANALYTICS
# ============================================================

def analytics():

    st.markdown(
        """
        <div class="hero">

            <h1>
                📊 Disaster Analytics
            </h1>

            <p>
                Monitor incident trends, severity,
                impact and response workload.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(
        st.session_state.incidents
    )


    # --------------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------------

    total_incidents = len(df)


    critical_count = len(

        df[
            df["severity"]
            == "CRITICAL"
        ]

    )


    high_count = len(

        df[
            df["severity"]
            == "HIGH"
        ]

    )


    total_affected = int(

        df["affected"].sum()

    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(

            "Total Incidents",

            total_incidents

        )


    with c2:

        st.metric(

            "Critical",

            critical_count

        )


    with c3:

        st.metric(

            "High Priority",

            high_count

        )


    with c4:

        st.metric(

            "People Affected",

            total_affected

        )


    st.write("")


    # --------------------------------------------------------
    # SEVERITY CHART
    # --------------------------------------------------------

    chart_col1, chart_col2 = st.columns(
        [1, 1]
    )


    with chart_col1:

        st.markdown(
            '<div class="section-title">'
            '⚠️ Incidents by Severity'
            '</div>',
            unsafe_allow_html=True
        )


        severity_data = (

            df[
                "severity"
            ]

            .value_counts()

        )


        st.bar_chart(
            severity_data
        )


    # --------------------------------------------------------
    # DISASTER TYPE CHART
    # --------------------------------------------------------

    with chart_col2:

        st.markdown(
            '<div class="section-title">'
            '🌪️ Incidents by Disaster Type'
            '</div>',
            unsafe_allow_html=True
        )


        disaster_data = (

            df[
                "type"
            ]

            .value_counts()

        )


        st.bar_chart(
            disaster_data
        )


    st.write("")


    # --------------------------------------------------------
    # INCIDENT TABLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📋 Incident Records'
        '</div>',
        unsafe_allow_html=True
    )


    display_columns = [

        "id",

        "type",

        "location",

        "severity",

        "confidence",

        "affected",

        "status",

        "source"

    ]


    st.dataframe(

        df[
            display_columns
        ],

        hide_index=True,

        use_container_width=True

    )


    # --------------------------------------------------------
    # IMPACT SUMMARY
    # --------------------------------------------------------

    st.write("")

    st.markdown(
        """
        <div class="ai-result">

            <div class="ai-title">
                📈 Operational Insight
            </div>

            <p>
                DRISHTI continuously aggregates
                incoming incidents and provides
                decision-makers with a consolidated
                view of disaster impact.
            </p>

            <p>
                <b>
                    Current system priority:
                </b>
                Focus response resources on
                critical incidents first.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )
    # ============================================================
# MAIN APPLICATION ROUTER
# ============================================================

if not st.session_state.logged_in:

    # Show login page

    login_page()


else:

    # Show sidebar

    selected_page = sidebar_navigation()


    # --------------------------------------------------------
    # COMMAND CENTER
    # --------------------------------------------------------

    if selected_page == "Command Center":

        command_center()


    # --------------------------------------------------------
    # LANDSLIDE RISK MONITORING
    # --------------------------------------------------------

    elif selected_page == "Landslide Risk Monitoring":

        landslide_risk_monitoring()


    # --------------------------------------------------------
    # AI INCIDENT ANALYZER
    # --------------------------------------------------------

    elif selected_page == "NER Risk Map":
        ner_landslide_risk_map()
    elif selected_page == "AI Incident Analyzer":

        ai_incident_analyzer()


    # --------------------------------------------------------
    # INCIDENT VERIFICATION
    # --------------------------------------------------------

    elif selected_page == "Incident Verification":

        incident_verification()


    # --------------------------------------------------------
    # RESOURCE ALLOCATION
    # --------------------------------------------------------

    elif selected_page == "Resource Allocation":

        resource_allocation()


    # --------------------------------------------------------
    # CITIZEN REPORTS
    # --------------------------------------------------------

    elif selected_page == "Citizen Reports":

        citizen_reports()


    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    elif selected_page == "Analytics":

        analytics()