import streamlit as st
import hashlib
from datetime import date, datetime
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

def get_connection():

    ca_path = "/tmp/aiven_ca.pem"

    with open(ca_path, "w") as file:
        file.write(st.secrets["CA_CERT"])

    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        ssl_ca=ca_path,
        ssl_verify_cert=True
    )


connection = None

try:
    connection = get_connection()

    # database work here

finally:
    if connection is not None and connection.is_connected():
        connection.close()

# ---------------- DATABASE CONNECTION ----------------

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="EduFix",
    page_icon="🏫",
    layout="wide"
)
# ---------------- EDUFIX UI STYLE ----------------

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background-color: #f7f9fc;
    }

    /* Main headings */
    h1, h2, h3 {
        color: #12355b;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #12355b;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Buttons */
    .stButton > button {
        background-color: #1f6feb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #1558b0;
        color: white;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 600;
    }

    /* Info boxes */
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""   


# ---------------- PASSWORD HASHING ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
# ---------------- USER REGISTRATION ----------------

def register_user(name, school_name, role, class_section, username, password):

    connection = get_connection()
    cursor = connection.cursor()

    password_hash = hash_password(password)

    query = """
    INSERT INTO users
    (name, school_name, role, class_section, username, password_hash)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        school_name,
        role,
        class_section,
        username,
        password_hash
    )

    try:
        cursor.execute(query, values)
        connection.commit()
        return True, "Registration successful."

    except mysql.connector.IntegrityError:
        return False, "Username already exists."

    finally:
        cursor.close()
        connection.close()


# ---------------- USER LOGIN ----------------

def login_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    password_hash = hash_password(password)

    query = """
    SELECT user_id, name, role
    FROM users
    WHERE username = %s AND password_hash = %s
    """

    cursor.execute(query, (username, password_hash))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user
    # ---------------- LOGIN / REGISTER ----------------

if not st.session_state.logged_in:

    st.title("🏫 EduFix")

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    # ---------------- LOGIN ----------------

    with login_tab:

        st.subheader("Login")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            user = login_user(
                username,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_name = user[1]
                st.session_state.user_role = user[2]

                st.success("Login successful!")
                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    # ---------------- REGISTER ----------------

    with register_tab:

        st.subheader("Create Account")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        school_name = st.text_input(
            "School Name",
            key="register_school"
        )

        role = st.selectbox(
    "Role",
    [
        "Student",
        "Teacher", 
        "Admin"
    ],
    key="register_role"
        )
    

        class_section = st.text_input(
            "Class / Section",
            key="register_class"
        )

        username = st.text_input(
            "Username",
            key="register_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm"
        )

        if st.button(
            "Register",
            use_container_width=True
        ):

            if not all([
                name,
                school_name,
                class_section,
                username,
                password,
                confirm_password
            ]):

                st.warning(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    name,
                    school_name,
                    role,
                    class_section,
                    username,
                    password
                )

                if success:
                    st.success(message)
                    st.info(
                        "You can now log in using your username and password."
                    )
                else:
                    st.error(message)

    # IMPORTANT
    st.stop()
# ---------------- MAIN APPLICATION ----------------

st.sidebar.markdown(
    """
    <div style="text-align:center; padding:10px 0 20px 0;">
        <div style="font-size:42px;">🏫</div>
        <h2 style="margin:0; color:white;">EduFix</h2>
        <p style="margin:4px 0; color:#dbeafe; font-size:13px;">
            School Problem Management
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    f"""
    <div style="
        background-color: rgba(255,255,255,0.10);
        padding:12px;
        border-radius:10px;
        margin-bottom:15px;
    ">
        <div style="font-size:12px; color:#dbeafe;">
            LOGGED IN AS
        </div>
        <div style="font-size:17px; font-weight:600; color:white;">
            {st.session_state.user_name}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    "**Navigation**",
    unsafe_allow_html=True
)

pages = [
    "🏠 Home",
    "📝 Report a Problem",
    "🔎 Check Status",
    "📊 Dashboard & Analytics"
]

if st.session_state.user_role == "Admin":
    pages.append("🛡️ Admin Management")

page = st.sidebar.radio(
    "",
    pages
)

st.sidebar.markdown("---")

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.session_state.user_role = ""
    st.rerun()
# ---------------- HOME ----------------

if page == "🏠 Home":
    st.markdown(
    """
    <div style="background: linear-gradient(135deg, #12355b, #1f6feb); padding: 35px 40px; border-radius: 16px; margin-bottom: 25px;">
        <div style="color: white; font-size: 42px; font-weight: 700; margin-bottom: 8px;">🏫 EduFix</div>
        <div style="color: #e8f1ff; font-size: 20px; margin-bottom: 8px;">Smart School Problem Reporting & Decision Support System</div>
        <div style="color: #dbeafe; font-size: 15px;">Report problems, prioritize their urgency, track progress, and use data to support better school management.</div>
    </div>
    """,
    unsafe_allow_html=True
    )
            
    st.subheader("What EduFix Does")

    st.write(
        "EduFix provides a centralized platform for reporting and "
        "managing school-related problems. Each report is evaluated "
        "using a transparent priority scoring system."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📝 Digital Reporting")
        st.write(
            "Submit school problems with category, location, "
            "severity and affected people."
        )

    with col2:
        st.markdown("### 🎯 Priority Analysis")
        st.write(
            "A transparent score helps identify problems "
            "requiring greater attention."
        )

    with col3:
        st.markdown("### 📊 Data Analytics")
        st.write(
            "Analyze reports, status, severity and problem "
            "patterns through the dashboard."
        )

    st.divider()

    st.subheader("How EduFix Works")

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        st.markdown("### 1️⃣ Report")
        st.caption("Submit details about a school problem.")

    with step2:
        st.markdown("### 2️⃣ Prioritize")
        st.caption(
            "EduFix calculates a transparent priority score."
        )

    with step3:
        st.markdown("### 3️⃣ Track")
        st.caption(
            "Monitor whether the problem is Pending, "
            "In Progress or Resolved."
        )

    with step4:
        st.markdown("### 4️⃣ Improve")
        st.caption(
            "Use collected data to identify recurring issues."
        )

    st.divider()

    st.info(
        "💡 EduFix converts school problem reporting into a "
        "structured digital process that can support "
        "data-driven decision making."
    )

    st.caption(
        "EduFix • Academic Prototype for School Problem Reporting "
        "& Data-Driven Decision Support"
    )

# ==============================
# REPORT A PROBLEM
# ==============================

if page == "📝 Report a Problem":

    st.title("📝 Report a Problem")

    st.write(
        "Provide details about the problem. EduFix will calculate "
        "a priority score based on its severity, impact, category "
        "and location."
    )

    st.divider()

    # ---------------- PROBLEM DETAILS ----------------

    st.subheader("📋 Problem Details")

    col1, col2 = st.columns(2)

    with col1:

        category = st.selectbox(
            "Problem Category",
            [
                "Electrical",
                "Furniture",
                "Water / Plumbing",
                "Cleanliness",
                "Laboratory",
                "Library",
                "Computer Lab",
                "Washroom",
                "Other"
            ]
        )

        severity = st.selectbox(
            "Severity",
            [
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        )

    with col2:

        location = st.selectbox(
            "Problem Location",
            [
                "Classroom",
                "Science Block",
                "Computer Lab",
                "Library",
                "Laboratory",
                "Washroom",
                "Playground",
                "Corridor",
                "Other"
            ]
        )

        people_affected = st.number_input(
            "Number of People Affected",
            min_value=1,
            max_value=1000,
            value=1,
            step=1
        )

    description = st.text_area(
        "Describe the Problem",
        placeholder=(
            "Briefly describe what happened, where it occurred "
            "and any important details..."
        ),
        height=120
    )

    report_date = date.today()

    st.divider()

    # ---------------- PRIORITY INFORMATION ----------------

    st.subheader("🎯 Priority Analysis")

    st.info(
        "EduFix calculates priority using five factors: "
        "severity, people affected, category, location and "
        "the time a problem remains unresolved."
    )

    st.caption(
        "A higher score indicates a greater need for attention. "
        "The scoring system is transparent and rule-based."
    )

    st.divider()

    # ---------------- SUBMIT ----------------

    if st.button(
        "🚀 Submit Report",
        use_container_width=True
    ):

        severity_score = {
            "Low": 8,
            "Medium": 17,
            "High": 26,
            "Critical": 35
        }

        category_score = {
            "Electrical": 15,
            "Water / Plumbing": 14,
            "Laboratory": 12,
            "Computer Lab": 10,
            "Washroom": 10,
            "Cleanliness": 8,
            "Furniture": 7,
            "Library": 5,
            "Other": 5
        }

        location_score = {
            "Classroom": 15,
            "Science Block": 20,
            "Computer Lab": 18,
            "Library": 10,
            "Laboratory": 18,
            "Washroom": 15,
            "Playground": 10,
            "Corridor": 12,
            "Other": 5
        }

        severity_points = severity_score[severity]
        category_points = category_score[category]
        location_points = location_score[location]

        if people_affected <= 5:
            people_points = 4
        elif people_affected <= 20:
            people_points = 8
        elif people_affected <= 50:
            people_points = 14
        else:
            people_points = 20

        time_points = 0

        priority_score = (
            severity_points
            + people_points
            + category_points
            + location_points
            + time_points
        )

        if priority_score >= 70:
            priority_level = "High"
        elif priority_score >= 40:
            priority_level = "Medium"
        else:
            priority_level = "Low"

        connection = None
        cursor = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO reports
            (
                user_id,
                category,
                location,
                severity,
                people_affected,
                report_date,
                description,
                priority_score,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                st.session_state.user_id,
                category,
                location,
                severity,
                people_affected,
                report_date,
                description,
                priority_score,
                "Pending"
            )

            cursor.execute(query, values)
            connection.commit()

            st.success(
                "✅ Problem reported successfully!"
            )

            st.divider()

            st.subheader("📊 Report Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Priority Score",
                    f"{priority_score}/100"
                )

            with col2:
                st.metric(
                    "Priority Level",
                    priority_level
                )

            with col3:
                st.metric(
                    "Status",
                    "Pending"
                )

            st.info(
                "Your report has been saved successfully. "
                "You can monitor its progress from Check Status."
            )

        except mysql.connector.Error as error:

            st.error(
                f"Database error: {error}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.close()
   # ---------------- CHECK STATUS ----------------

if page == "🔎 Check Status":

    st.title("🔎 Check Status")

    st.write(
        "Track the problems you have reported and monitor their current status."
    )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        report_id,
        category,
        location,
        severity,
        people_affected,
        report_date,
        priority_score,
        status,
        description
    FROM reports
    WHERE user_id = %s
    ORDER BY report_date DESC, report_id DESC
    """

    cursor.execute(
        query,
        (st.session_state.user_id,)
    )

    reports = cursor.fetchall()

    cursor.close()
    connection.close()

    if reports:

        # ---------------- SUMMARY ----------------

        total_reports = len(reports)
        pending_reports = sum(
            1 for r in reports if r["status"] == "Pending"
        )
        in_progress_reports = sum(
            1 for r in reports if r["status"] == "In Progress"
        )
        resolved_reports = sum(
            1 for r in reports if r["status"] == "Resolved"
        )

        st.subheader("📌 Report Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Reports", total_reports)

        with col2:
            st.metric("Pending", pending_reports)

        with col3:
            st.metric("In Progress", in_progress_reports)

        with col4:
            st.metric("Resolved", resolved_reports)

        st.divider()

        # ---------------- REPORT LIST ----------------

        st.subheader(f"📋 Your Reports ({total_reports})")

        for report in reports:

            status_icon = {
                "Pending": "🟡",
                "In Progress": "🔵",
                "Resolved": "🟢"
            }.get(report["status"], "⚪")

            with st.expander(
                f"{status_icon} Report #{report['report_id']} — "
                f"{report['category']} — "
                f"{report['status']}"
            ):

                # Report identification
                st.markdown(
                    f"**Report #{report['report_id']}**"
                )

                st.caption(
                    f"Submitted on {report['report_date']}"
                )

                st.divider()

                # Main information
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**📍 Location**")
                    st.write(report["location"])

                with col2:
                    st.markdown("**⚠️ Severity**")
                    st.write(report["severity"])

                with col3:
                    st.markdown("**🎯 Priority Score**")
                    st.write(
                        f"{report['priority_score']}/100"
                    )

                st.divider()

                # Impact
                st.markdown("**👥 People Affected**")
                st.write(report["people_affected"])

                # Description
                st.markdown("**📝 Description**")

                if report["description"]:
                    st.write(report["description"])
                else:
                    st.caption("No description provided.")

                st.divider()

                # Status
                if report["status"] == "Pending":

                    st.warning(
                        "🟡 **Pending** — Your report has been submitted "
                        "and is awaiting action."
                    )

                elif report["status"] == "In Progress":

                    st.info(
                        "🔵 **In Progress** — Action is currently being "
                        "taken on this problem."
                    )

                elif report["status"] == "Resolved":

                    st.success(
                        "🟢 **Resolved** — This problem has been marked "
                        "as resolved."
                    )

    else:

        st.info(
            "📭 You have not submitted any problem reports yet."
        )

        st.write(
            "Use **Report a Problem** to submit your first report."
        )               
# ==============================
# DASHBOARD & ANALYTICS
# ==============================

if page == "📊 Dashboard & Analytics":

    st.title("📊 Dashboard & Analytics")
    st.write(
        "Analyze reported school problems and monitor their "
        "priority, status and impact."
    )

    # ------------------------------
    # LOAD REPORTS FROM MYSQL
    # ------------------------------

    connection = None

    try:
        connection = get_connection()

        query = """
        SELECT
            report_id,
            user_id,
            category,
            location,
            severity,
            people_affected,
            report_date,
            description,
            priority_score,
            status
        FROM reports
        ORDER BY report_date DESC, report_id DESC
        """

        df = pd.read_sql(query, connection)

    except mysql.connector.Error as error:
        st.error(f"Database error: {error}")
        st.stop()

    finally:
        if connection is not None and connection.is_connected():
            connection.close()

    # ------------------------------
    # CHECK IF REPORTS EXIST
    # ------------------------------

    if df.empty:

        st.info(
            "No reports have been submitted yet."
        )

        st.stop()

    # ------------------------------
    # PREPARE DATE DATA
    # ------------------------------

    df["report_date"] = pd.to_datetime(
        df["report_date"]
    )

    today = pd.Timestamp(date.today())

    df["days_unresolved"] = (
        today - df["report_date"]
    ).dt.days

    # Resolved reports do not accumulate
    # unresolved duration
    df.loc[
        df["status"] == "Resolved",
        "days_unresolved"
    ] = 0

    # ------------------------------
    # TIME-BASED PRIORITY
    # ------------------------------

    def calculate_time_points(days):

        if days <= 0:
            return 0

        elif days <= 2:
            return 2

        elif days <= 6:
            return 5

        elif days <= 13:
            return 8

        else:
            return 10

    df["time_points"] = (
        df["days_unresolved"]
        .apply(calculate_time_points)
    )

    # ------------------------------
    # CURRENT PRIORITY
    # ------------------------------

    df["current_priority"] = (
        df["priority_score"]
        + df["time_points"]
    )

    df["current_priority"] = (
        df["current_priority"]
        .clip(upper=100)
    )

    # ------------------------------
    # CURRENT PRIORITY LEVEL
    # ------------------------------

    def get_priority_level(score):

        if score >= 70:
            return "High"

        elif score >= 40:
            return "Medium"

        else:
            return "Low"

    df["current_priority_level"] = (
        df["current_priority"]
        .apply(get_priority_level)
    )

    # ==============================
    # KPI CARDS
    # ==============================

    st.subheader("📌 Overview")

    total_reports = len(df)

    pending_reports = (
        df["status"] == "Pending"
    ).sum()

    in_progress_reports = (
        df["status"] == "In Progress"
    ).sum()

    resolved_reports = (
        df["status"] == "Resolved"
    ).sum()

    high_priority_reports = (
        df["current_priority_level"] == "High"
    ).sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Reports",
            total_reports
        )

    with col2:
        st.metric(
            "Pending",
            pending_reports
        )

    with col3:
        st.metric(
            "In Progress",
            in_progress_reports
        )

    with col4:
        st.metric(
            "Resolved",
            resolved_reports
        )

    with col5:
        st.metric(
            "High Priority",
            high_priority_reports
        )

    # ==============================
    # FILTERS
    # ==============================

    st.subheader("🔎 Filter Reports")

    col1, col2 = st.columns(2)

    with col1:

        category_filter = st.multiselect(
            "Category",
            sorted(
                df["category"]
                .dropna()
                .unique()
            ),
            default=sorted(
                df["category"]
                .dropna()
                .unique()
            )
        )

    with col2:

        location_filter = st.multiselect(
            "Location",
            sorted(
                df["location"]
                .dropna()
                .unique()
            ),
            default=sorted(
                df["location"]
                .dropna()
                .unique()
            )
        )

    col3, col4 = st.columns(2)

    with col3:

        severity_filter = st.multiselect(
            "Severity",
            [
                "Low",
                "Medium",
                "High",
                "Critical"
            ],
            default=[
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        )

    with col4:

        status_filter = st.multiselect(
            "Status",
            [
                "Pending",
                "In Progress",
                "Resolved"
            ],
            default=[
                "Pending",
                "In Progress",
                "Resolved"
            ]
        )

    # ------------------------------
    # APPLY FILTERS
    # ------------------------------

    filtered_df = df[
        df["category"].isin(category_filter)
        &
        df["location"].isin(location_filter)
        &
        df["severity"].isin(severity_filter)
        &
        df["status"].isin(status_filter)
    ].copy()

    st.info(
        f"{len(filtered_df)} reports match the selected filters."
    )

    # ==============================
    # CURRENT REPORT DATA
    # ==============================

    st.subheader("📋 Report Data")

    display_columns = [
        "report_id",
        "category",
        "location",
        "severity",
        "people_affected",
        "report_date",
        "days_unresolved",
        "current_priority",
        "current_priority_level",
        "status"
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True
    )

# ---------------- ADMIN MANAGEMENT ----------------

if page == "🛡️ Admin Management" and st.session_state.user_role == "Admin":

    st.title("🛡️ Admin Management")

    st.write(
        "Manage registered users, monitor school problems, "
        "and control report status from the administrative panel."
    )

    st.divider()

    # ---------------- DATABASE CONNECTION ----------------

    connection = None

    try:

        connection = get_connection()

        # USER DATA
        users_query = """
        SELECT
            user_id,
            name,
            school_name,
            role,
            class_section,
            username
        FROM users
        ORDER BY user_id DESC
        """

        users_df = pd.read_sql(
            users_query,
            connection
        )

        # REPORT DATA
        reports_query = """
        SELECT
            report_id,
            category,
            location,
            severity,
            people_affected,
            report_date,
            priority_score,
            status
        FROM reports
        ORDER BY report_date DESC, report_id DESC
        """

        reports_df = pd.read_sql(
            reports_query,
            connection
        )

    except mysql.connector.Error as error:

        st.error(
            f"Database error: {error}"
        )

        st.stop()

    finally:

        if connection is not None and connection.is_connected():
            connection.close()

    # ---------------- ADMIN KPIs ----------------

    total_users = len(users_df)
    total_reports = len(reports_df)

    pending_reports = (
        (reports_df["status"] == "Pending").sum()
        if not reports_df.empty else 0
    )

    resolved_reports = (
        (reports_df["status"] == "Resolved").sum()
        if not reports_df.empty else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Registered Users",
            total_users
        )

    with col2:
        st.metric(
            "Total Reports",
            total_reports
        )

    with col3:
        st.metric(
            "Pending Reports",
            pending_reports
        )

    with col4:
        st.metric(
            "Resolved Reports",
            resolved_reports
        )

    st.divider()

    # ---------------- USER MANAGEMENT ----------------

    st.subheader("👥 Registered Users")

    if users_df.empty:

        st.info("No registered users found.")

    else:

        st.dataframe(
            users_df[
                [
                    "user_id",
                    "name",
                    "school_name",
                    "role",
                    "class_section",
                    "username"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ---------------- REPORT MANAGEMENT ----------------

    st.subheader("📋 Report Management")

    if reports_df.empty:

        st.info("No reports have been submitted yet.")

    else:

        st.dataframe(
            reports_df,
            use_container_width=True,
            hide_index=True
        )

