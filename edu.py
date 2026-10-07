import streamlit as st
import hashlib
from datetime import date, datetime
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )
)

if connection.is_connected():
    print("EduFix MySQL database connected successfully!")
else:
    print("Database connection failed.")
# Create cursor
cursor = connection.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    school_name VARCHAR(150) NOT NULL,
    role VARCHAR(30) NOT NULL,
    class_section VARCHAR(30),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
)
""")

# Create reports table
cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    people_affected INT NOT NULL,
    report_date DATE NOT NULL,
    description TEXT,
    priority_score INT,
    status VARCHAR(20) DEFAULT 'Pending',

    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
)
""")

connection.commit()

print("Users table created successfully.")
print("Reports table created successfully.")

cursor.close()
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


# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""


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
    SELECT user_id, name
    FROM users
    WHERE username = %s AND password_hash = %s
    """

    cursor.execute(query, (username, password_hash))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user
# ---------------- MAIN APPLICATION ----------------

st.sidebar.title("EduFix")

st.sidebar.write(f"Welcome, {st.session_state.user_name}")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Report a Problem",
        "Check Status",
        "Dashboard & Analytics"
    ]
)
st.sidebar.divider()

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.rerun()


# ---------------- HOME ----------------

if page == "Home":

    st.title("🏫 EduFix")

    st.subheader(
        "Smart School Problem Reporting & Decision Support System"
    )

    st.write(
        "EduFix provides a digital platform for reporting, "
        "tracking, analyzing and prioritizing school-related problems."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Digital Reporting", "✓")
        st.caption("Report school problems digitally.")

    with col2:
        st.metric("Priority Analysis", "✓")
        st.caption("Identify problems requiring greater attention.")

    with col3:
        st.metric("Data Analytics", "✓")
        st.caption("Analyze recurring problems and trends.")

    st.divider()

    st.subheader("How EduFix Works")

    st.markdown("""
    **1. Report**
    Submit details about a school problem.

    **2. Analyze**
    EduFix calculates a transparent priority score.

    **3. Track**
    Check whether a reported problem is Pending,
    In Progress or Resolved.

    **4. Improve**
    Use dashboards and analytics to identify
    recurring problem areas.
    """)

    st.info(
        "EduFix is designed as an academic prototype for "
        "school problem reporting and data-driven decision support."
    )

# ---------------- REPORT A PROBLEM ----------------

if page == "Report a Problem":

    st.title("📝 Report a Problem")

    st.write(
        "Submit details about a school problem. "
        "EduFix will calculate its priority automatically."
    )

    st.divider()

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

    location = st.selectbox(
        "Location",
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

    severity = st.selectbox(
        "Severity",
        [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]
    )

    people_affected = st.number_input(
        "Number of People Affected",
        min_value=1,
        max_value=1000,
        value=1,
        step=1
    )

    report_date = st.date_input(
        "Date of Report",
        value=date.today()
    )

    description = st.text_area(
        "Problem Description",
        placeholder="Describe the problem clearly..."
    )

    # ---------------- PRIORITY CALCULATION ----------------

    severity_score = {
        "Low": 10,
        "Medium": 25,
        "High": 40,
        "Critical": 50
    }

    score = severity_score[severity]

    # Effect of number of people affected
    if people_affected <= 5:
        people_score = 5
    elif people_affected <= 20:
        people_score = 15
    elif people_affected <= 50:
        people_score = 25
    else:
        people_score = 30

    priority_score = min(score + people_score, 100)

    if priority_score >= 70:
        priority_level = "High"
    elif priority_score >= 40:
        priority_level = "Medium"
    else:
        priority_level = "Low"

    st.divider()

    st.subheader("Priority Assessment")

    col1, col2 = st.columns(2)

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

    # ---------------- SUBMIT REPORT ----------------

    if st.button(
        "Submit Problem Report",
        use_container_width=True
    ):

        if not description.strip():

            st.warning(
                "Please provide a description of the problem."
            )

        else:

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

            cursor.close()
            connection.close()

            st.success(
                f"Problem reported successfully! "
                f"Priority: {priority_level} ({priority_score}/100)"
            )

# ---------------- CHECK STATUS ----------------

if page == "Check Status":

    st.title("🔎 Check Status")

    st.write(
        "View the problems you have reported and their current status."
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

        st.subheader(f"Your Reports: {len(reports)}")

        for report in reports:

            with st.expander(
                f"Report #{report['report_id']} — "
                f"{report['category']} — "
                f"{report['status']}"
            ):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write("**Location**")
                    st.write(report["location"])

                with col2:
                    st.write("**Severity**")
                    st.write(report["severity"])

                with col3:
                    st.write("**Priority**")
                    st.write(
                        f"{report['priority_score']}/100"
                    )

                st.write(
                    f"**People affected:** "
                    f"{report['people_affected']}"
                )

                st.write(
                    f"**Date:** "
                    f"{report['report_date']}"
                )

                st.write(
                    f"**Description:** "
                    f"{report['description']}"
                )

                if report["status"] == "Pending":
                    st.warning("Status: Pending")

                elif report["status"] == "In Progress":
                    st.info("Status: In Progress")

                elif report["status"] == "Resolved":
                    st.success("Status: Resolved")

    else:

        st.info(
            "You have not submitted any problem reports yet."
        )

  # ==============================
# DASHBOARD & ANALYTICS
# ==============================

if page == "Dashboard & Analytics":

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

