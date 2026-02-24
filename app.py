'''import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("volunteer.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS volunteers (
    volunteer_id TEXT PRIMARY KEY,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_id TEXT,
    task TEXT,
    start_time TEXT,
    end_time TEXT,
    hours REAL,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id)
)
""")

conn.commit()


# ---------------- HELPER FUNCTION ----------------
def calculate_hours(start_time, end_time):
    fmt = "%Y-%m-%d %H:%M"
    start = datetime.strptime(start_time, fmt)
    end = datetime.strptime(end_time, fmt)
    duration = end - start
    return round(duration.total_seconds() / 3600, 2)


# ---------------- STREAMLIT UI ----------------
st.title("🧑‍🤝‍🧑 Volunteer Management System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Log Volunteer Shift", "View Total Volunteer Hours"]
)

# ---------------- LOG SHIFT ----------------
if menu == "Log Volunteer Shift":
    st.header("Log Volunteer Shift")

    vid = st.text_input("Volunteer ID")
    name = st.text_input("Volunteer Name")
    task = st.text_input("Task Assigned")
    start_time = st.text_input("Start Time (YYYY-MM-DD HH:MM)")
    end_time = st.text_input("End Time (YYYY-MM-DD HH:MM)")

    if st.button("Log Shift"):
        try:
            hours = calculate_hours(start_time, end_time)

            # Insert volunteer (ignore if exists)
            cursor.execute(
                "INSERT OR IGNORE INTO volunteers VALUES (?, ?)",
                (vid, name)
            )

            # Insert shift
            cursor.execute("""
                INSERT INTO shifts (volunteer_id, task, start_time, end_time, hours)
                VALUES (?, ?, ?, ?, ?)
            """, (vid, task, start_time, end_time, hours))

            conn.commit()
            st.success(f"Shift logged successfully! ⏱️ Hours: {hours}")

        except Exception as e:
            st.error(f"Error: {e}")


# ---------------- VIEW TOTAL HOURS ----------------
elif menu == "View Total Volunteer Hours":
    st.header("View Total Hours")

    vid = st.text_input("Enter Volunteer ID")

    if st.button("View Hours"):
        cursor.execute("""
            SELECT SUM(hours) FROM shifts WHERE volunteer_id = ?
        """, (vid,))
        result = cursor.fetchone()[0]

        if result:
            st.success(f"Total hours worked by Volunteer {vid}: {result} hours")
        else:
            st.warning("No records found for this volunteer.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("**Created By:** Lalzarliani Khiangte and Soumita Das")
st.markdown("**Copyright:** AIPA (2025), NSTI(W) Kolkata")'''


import streamlit as st
import mysql.connector
from datetime import datetime, timedelta


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="volunteer_db"
    )


def calculate_hours(start_dt, end_dt):

    # Same day work
    if start_dt.date() == end_dt.date():
        if start_dt.weekday() == 6:   # Sunday
            return 0
        duration = end_dt - start_dt
        return round(duration.total_seconds() / 3600, 2)

    # Multiple days (8 hours per day, excluding Sundays)
    total_hours = 0
    current_date = start_dt.date()

    while current_date <= end_dt.date():
        if current_date.weekday() != 6:  # Not Sunday
            total_hours += 8
        current_date += timedelta(days=1)

    return total_hours


st.title("Volunteer Management System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Log Volunteer Shift", "View Total Volunteer Hours"]
)


if menu == "Log Volunteer Shift":
    st.header("Log Volunteer Shift")

    vid = st.text_input("Volunteer ID")
    name = st.text_input("Volunteer Name")
    task = st.text_input("Task Assigned")
    start_date = st.date_input("Start Date")
    start_time = st.time_input("Start Time")
    end_date = st.date_input("End Date")
    end_time = st.time_input("End Time")

    if st.button("Log Shift"):
        try:
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)

            # Invalid date check
            if end_dt.date() < start_dt.date():
                st.error("End date cannot be before start date")
                st.stop()

            hours = calculate_hours(start_dt, end_dt)

            conn = get_connection()
            cursor = conn.cursor()

            # Insert volunteer if not exists
            cursor.execute(
                "INSERT IGNORE INTO volunteers (volunteer_id, name) VALUES (%s, %s)",
                (vid, name)
            )
            conn.commit()

            cursor.execute("""
                INSERT INTO shifts (volunteer_id, task, start_time, end_time, hours)
                VALUES (%s, %s, %s, %s, %s)
            """, (vid, task, start_dt, end_dt, hours))

            conn.commit()
            conn.close()

            st.success(f"Shift logged successfully! ⏱️ Hours: {hours}")

        except Exception as e:
            st.error(f"Database Error: {e}")


elif menu == "View Total Volunteer Hours":
    st.header("View Total Volunteer Hours")

    vid = st.text_input("Volunteer ID")

    if st.button("View Hours"):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT SUM(hours) FROM shifts WHERE volunteer_id = %s",
                (vid,)
            )
            result = cursor.fetchone()[0]

            conn.close()

            if result:
                st.success(f"Total hours worked by Volunteer {vid}: {round(result,2)} hours")
            else:
                st.warning("No records found.")

        except Exception as e:
            st.error(f"Database Error: {e}")


st.markdown("---")
st.markdown("**Created By:** Lalzarliani Khiangte and Soumita Das")
st.markdown("**Copyright:** AIPA (2025), NSTI(W) Kolkata")
