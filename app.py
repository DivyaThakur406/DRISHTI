import streamlit as st
import pandas as pd
import re
import math

from datetime import datetime


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
# ============================================================

LOCATION_COORDINATES = {

    "srinagar": (34.0837, 74.7973),

    "pahalgam": (34.0160, 75.3150),

    "anantnag": (33.7310, 75.1480),

    "baramulla": (34.2090, 74.3420),

    "jammu": (32.7266, 74.8570),

    "kathua": (32.3867, 75.5182)

}


# ============================================================
# EMERGENCY RESOURCE DATABASE
# ============================================================

RESOURCES = [

    {
        "name": "NDRF Rescue Team A",
        "type": "Rescue Team",
        "location": "Srinagar",
        "lat": 34.0700,
        "lon": 74.7850,
        "capacity": 10,
        "status": "AVAILABLE"
    },

    {
        "name": "Rescue Team B",
        "type": "Rescue Team",
        "location": "Pahalgam",
        "lat": 34.0250,
        "lon": 75.3000,
        "capacity": 6,
        "status": "AVAILABLE"
    },

    {
        "name": "District Hospital Srinagar",
        "type": "Hospital",
        "location": "Srinagar",
        "lat": 34.0850,
        "lon": 74.8000,
        "capacity": 150,
        "status": "AVAILABLE"
    },

    {
        "name": "Emergency Shelter 01",
        "type": "Shelter",
        "location": "Srinagar",
        "lat": 34.0900,
        "lon": 74.7800,
        "capacity": 250,
        "status": "AVAILABLE"
    },

    {
        "name": "Emergency Shelter 02",
        "type": "Shelter",
        "location": "Pahalgam",
        "lat": 34.0200,
        "lon": 75.2900,
        "capacity": 150,
        "status": "AVAILABLE"
    },

    {
        "name": "Fire & Emergency Unit",
        "type": "Fire & Rescue",
        "location": "Anantnag",
        "lat": 33.7400,
        "lon": 75.1600,
        "capacity": 8,
        "status": "BUSY"
    }
]


# ============================================================
# INCIDENT DATABASE
# ============================================================

if "incidents" not in st.session_state:

    st.session_state.incidents = [

        {
            "id": "INC-1042",
            "type": "Flood",
            "location": "Srinagar",
            "lat": 34.0837,
            "lon": 74.7973,
            "severity": "CRITICAL",
            "confidence": 94,
            "affected": 120,
            "status": "ACTIVE",
            "description":
                "Water has entered residential areas. "
                "Several families reported trapped.",
            "source":
                "Citizen + Official",
            "time":
                "12 min ago"
        },

        {
            "id": "INC-1041",
            "type": "Landslide",
            "location": "Pahalgam",
            "lat": 34.0160,
            "lon": 75.3150,
            "severity": "HIGH",
            "confidence": 88,
            "affected": 42,
            "status": "ACTIVE",
            "description":
                "Road blocked after slope failure. "
                "Vehicles stranded.",
            "source":
                "Citizen Report",
            "time":
                "28 min ago"
        },

        {
            "id": "INC-1040",
            "type": "Flash Flood",
            "location": "Anantnag",
            "lat": 33.7310,
            "lon": 75.1480,
            "severity": "HIGH",
            "confidence": 91,
            "affected": 76,
            "status": "ACTIVE",
            "description":
                "Rapid water rise near low-lying settlements.",
            "source":
                "Weather + Citizen",
            "time":
                "41 min ago"
        },

        {
            "id": "INC-1039",
            "type": "Earthquake",
            "location": "Baramulla",
            "lat": 34.2090,
            "lon": 74.3420,
            "severity": "MEDIUM",
            "confidence": 81,
            "affected": 18,
            "status": "MONITORING",
            "description":
                "Tremors reported. No major structural "
                "damage confirmed.",
            "source":
                "Citizen Report",
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
# AI INCIDENT ANALYZER
# ============================================================

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

            <h1>
                🔎 Incident Verification Center
            </h1>

            <p>
                Cross-source intelligence helps DRISHTI
                identify credible incidents, reduce duplicates,
                and prioritize verified emergencies.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # TOP SUMMARY
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📡 Information Sources'
        '</div>',
        unsafe_allow_html=True
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "👤 Citizen Reports",
            "14"
        )


    with c2:

        st.metric(
            "🏛️ Official Alerts",
            "2"
        )


    with c3:

        st.metric(
            "🌦️ Weather Signals",
            "6"
        )


    with c4:

        st.metric(
            "📰 News Signals",
            "9"
        )


    st.write("")


    # ========================================================
    # SELECT INCIDENT
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🚨 Select Incident for Verification'
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

        st.info(
            "No active incidents available for verification."
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


    selected_label = st.selectbox(

        "Choose an incident",

        list(
            incident_options.keys()
        )

    )


    selected_incident = incident_options[
        selected_label
    ]


    st.write("")


    # ========================================================
    # INCIDENT OVERVIEW
    # ========================================================

    overview_col1, overview_col2 = st.columns(
        [1.4, 1]
    )


    with overview_col1:

        severity = selected_incident[
            "severity"
        ]


        if severity == "CRITICAL":

            severity_text = "🔴 CRITICAL"

        elif severity == "HIGH":

            severity_text = "🟠 HIGH"

        else:

            severity_text = "🔵 MEDIUM"


        st.markdown(
            f"""
            <div class="card">

                <div class="muted">
                    INCIDENT OVERVIEW
                </div>

                <h2>
                    {selected_incident["type"]}
                    —
                    {selected_incident["location"]}
                </h2>

                <p>
                    {selected_incident["description"]}
                </p>

                <hr>

                <b>Incident ID:</b>
                {selected_incident["id"]}

                <br><br>

                <b>Severity:</b>
                {severity_text}

                <br><br>

                <b>People affected:</b>
                {selected_incident["affected"]}

                <br><br>

                <b>Initial AI confidence:</b>
                {selected_incident["confidence"]}%

            </div>
            """,
            unsafe_allow_html=True
        )


    with overview_col2:

        st.markdown(
            """
            <div class="card">

                <div class="muted">
                    VERIFICATION STATUS
                </div>

                <h2>
                    🟢 HIGH CONFIDENCE
                </h2>

                <p>
                    Multiple information signals
                    support the reported incident.
                </p>

                <div style="
                    background:#16344b;
                    border-radius:10px;
                    height:12px;
                    margin-top:18px;
                ">

                    <div style="
                        background:#22c55e;
                        width:94%;
                        height:12px;
                        border-radius:10px;
                    ">
                    </div>

                </div>

                <p style="
                    text-align:right;
                    margin-top:8px;
                    color:#86efac;
                    font-weight:700;
                ">
                    94% confidence
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # SOURCE CORRELATION
    # ========================================================

    st.write("")

    st.markdown(
        '<div class="section-title">'
        '🔗 Multi-Source Correlation'
        '</div>',
        unsafe_allow_html=True
    )


    source_data = pd.DataFrame({

        "Information Source": [

            "👤 Citizen Reports",

            "🏛️ Official Emergency Alert",

            "🌦️ Weather / Sensor Signal",

            "📰 News / Media Reports",

            "📍 Location Consistency",

            "🔁 Duplicate Detection"

        ],

        "Evidence": [

            "7 reports",

            "1 matching alert",

            "Rainfall warning detected",

            "3 matching reports",

            "Same affected region",

            "4 duplicate reports linked"

        ],

        "Confidence Contribution": [

            "HIGH",

            "VERY HIGH",

            "MEDIUM",

            "MEDIUM",

            "HIGH",

            "HIGH"

        ],

        "Status": [

            "✓ CONFIRMED",

            "✓ CONFIRMED",

            "✓ CORROBORATED",

            "✓ CORROBORATED",

            "✓ MATCHED",

            "✓ CLUSTERED"

        ]

    })


    st.dataframe(

        source_data,

        hide_index=True,

        use_container_width=True

    )


    # ========================================================
    # DUPLICATE DETECTION
    # ========================================================

    st.write("")

    duplicate_col1, duplicate_col2 = st.columns(
        [1, 1]
    )


    with duplicate_col1:

        st.markdown(
            """
            <div class="card">

                <h3>
                    🔁 Duplicate Detection
                </h3>

                <p>
                    DRISHTI identified multiple reports
                    describing the same incident.
                </p>

                <h2>
                    4 reports → 1 incident
                </h2>

                <div class="muted">
                    Duplicate reports are clustered
                    to prevent inflated incident counts.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with duplicate_col2:

        st.markdown(
            """
            <div class="card">

                <h3>
                    📍 Location Correlation
                </h3>

                <p>
                    Reports from nearby locations
                    are compared to identify
                    the same disaster event.
                </p>

                <h2>
                    ✓ Location Match
                </h2>

                <div class="muted">
                    Spatial consistency increases
                    confidence in the incident.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # FINAL VERDICT
    # ========================================================

    st.write("")

    st.markdown(
        '<div class="section-title">'
        '🎯 Verification Verdict'
        '</div>',
        unsafe_allow_html=True
    )


    st.success(
        "✓ VERIFIED INCIDENT — "
        "Multiple independent information signals "
        "support this event."
    )


    verdict_col1, verdict_col2, verdict_col3 = (
        st.columns(3)
    )


    with verdict_col1:

        st.metric(
            "Verification Score",
            "94%"
        )


    with verdict_col2:

        st.metric(
            "Independent Sources",
            "4"
        )


    with verdict_col3:

        st.metric(
            "Duplicate Reports",
            "4 → 1"
        )


    # ========================================================
    # OPERATIONAL DECISION
    # ========================================================

    st.write("")

    st.markdown(
        """
        <div class="ai-result">

            <div class="ai-title">
                ⚡ OPERATIONAL DECISION
            </div>

            <p>
                The incident has sufficient evidence
                to enter the emergency response queue.
            </p>

            <p>
                🚑 Recommended:
                <b>
                    Dispatch response resources
                </b>
            </p>

            <p>
                🏥 Recommended:
                <b>
                    Check nearby medical capacity
                </b>
            </p>

            <p>
                📢 Recommended:
                <b>
                    Issue targeted emergency notification
                </b>
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )
    # ============================================================
# SMART RESOURCE ALLOCATION
# ============================================================

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
    # AI INCIDENT ANALYZER
    # --------------------------------------------------------

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