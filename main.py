import streamlit as st
import psycopg2
from dotenv import load_dotenv
import os
import re
import bcrypt
import pandas as pd


def get_connection():
    try:
        if "postgres" in st.secrets: 
            db = st.secrets["postgres"]
            return psycopg2.connect(
                user=db["user"],
                password=db["password"],
                host=db["host"],
                port=db["port"],
                dbname=db.get("dbname", "postgres")
            )
        else:
            load_dotenv("database.env")
            return psycopg2.connect(
                user=os.getenv("user"),
                password=os.getenv("password"),
                host=os.getenv("host"),
                port=os.getenv("port"),
                dbname=os.getenv("dbname", "postgres")
            )
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode(), salt).decode()

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_current_user():
    if "user_id" not in st.session_state:
        return None
    return st.session_state.user_id, st.session_state.username, st.session_state.role

def is_teacher():
    return st.session_state.get("role") in ("teacher", "admin")

def is_admin():
    return st.session_state.get("role") == "admin"

# Load environment variables from .env
load_dotenv("database.env")

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connect to the database
try:
    with psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW();")
            print("Current Time:", cursor.fetchone())

    print("Connection successful and closed properly!")

except Exception as e:
    print(f"Failed to connect: {e}")

# --- Streamlit ---
st.title("💡WeSTEM – Innovate💡")

#
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login/Registration part

if not st.session_state.logged_in:
    page = st.radio("Choose action:", ["Registration", "Login"])

    if page == "Registration":
        with st.form("register_form"):
            st.subheader("Registration for new users 📝")

            email = st.text_input("Email 📬", placeholder="blablabla@yourmail.com")
            password = st.text_input("Password 🔐", type="password")

            col1, col2 = st.columns([1, 2])
            with col1:
                first_name = st.text_input("First name", placeholder="Arsen")
            with col2:
                last_name = st.text_input("Last name", placeholder="Kenjakayev")

            country_codes = {
                "🇺🇿 Uzbekistan(+998)": "+998",
                "🇰🇷 South Korea(+82)": "+82",
                "🇷🇺 Russia(+7)": "+7",
                "🇺🇸 USA(+1)": "+1"
            }
            col1, col2 = st.columns([1, 2])
            with col1:
                country = st.selectbox("Country 🌍", list(country_codes.keys()))
                code = country_codes[country]
            with col2:
                phone_number = st.text_input("Phone number 📱", placeholder="901234567")

            submit = st.form_submit_button("Register ✅")

        if submit:
            full_number = code + phone_number.strip()

            if all([email, password, first_name, last_name, phone_number]):
                try:
                    errors = []
                    if not re.fullmatch(r"^[\w.-]+@[\w.-]+\.\w{2,}$", email):
                        errors.append("Incorrect email. Follow example: blablabla@yourmail.com 😡"
                                      "Can't fix the error? DM me @arcsenus")

                    if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
                        errors.append("Password must be at least 8 chars and contain 1 letter + 1 number 😡"
                                      "Can't fix the error? DM me @arcsenus")

                    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-]{2,30}", first_name):
                        errors.append("First name must be 2–30 letters 😡"
                                      "Can't fix the error? DM me @arcsenus")

                    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-]{2,30}", last_name):
                        errors.append("Last name must be 2–30 letters 😡"
                                      "Can't fix the error? DM me @arcsenus")

                    if not re.fullmatch(r"\d{9,12}", phone_number):
                        errors.append("Phone must be 9–12 digits 😡"
                                      "Can't fix the error? DM me @arcsenus")

                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM users WHERE email = %s;", (email,))

                    if errors:
                        for i in errors:
                            st.error(i)
                    elif cur.fetchone():
                        st.error("❌ User already exists"
                                 "Can't fix the error? DM me @arcsenus")
                    else:
                        password_hashed = hash_password(password)
                        cur.execute(
                            "INSERT INTO users (email, password, first_name, last_name, phone) VALUES (%s, %s, %s, %s, %s);",
                            (email, password_hashed, first_name, last_name, full_number),
                        )
                        conn.commit()
                        st.success("✅ Registration successful! Please login.")
                    cur.close()
                    conn.close()
                except Exception as e:
                    st.error(f"Error: {e}"
                             f"Can't fix the error? DM me @arcsenus")
            else:
                st.warning("Fill all the blanks!")

    elif page == "Login":
        with st.form("login_form"):
            st.subheader("Enter the system 🔑")
            email = st.text_input("Email 📬", key="login_user", placeholder="blablabla@yourmail.com")
            password = st.text_input("Password 🔐", type="password", key="login_pass")
            submit = st.form_submit_button("Login ✅")

        if submit:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT id, password, role FROM users WHERE email = %s;", (email,))
                user = cur.fetchone()
                if user and check_password(password, user[1]):  # user[1] = password
                    st.session_state.logged_in = True
                    st.session_state.username = email
                    st.session_state.user_id = user[0]  # id
                    st.session_state.role = user[2] or "student"
                    st.rerun()
                else:
                    st.error("❌ Incorrect login or password!"
                             "Can't the fix error? DM me @arcsenus")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Error: {e}"
                         f"Can't fix the error? DM me @arcsenus")

# Account system

else:
    st.success(f"Welcome, {st.session_state.username}! 🎉")
    st.write("👉 Here is your schedule")
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE events
            SET is_active = FALSE
            WHERE event_date < CURRENT_DATE
            OR (
                event_date = CURRENT_DATE 
                AND (event_time + INTERVAL '1 hour') < CURRENT_TIME);
        """)
        conn.commit()
        cur.execute("SELECT * FROM events "
                    "WHERE is_active = True;")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index(columns[0])
        st.dataframe(df)
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error: {e}"
                 f"Can't fix the error? DM me @arcsenus")

    if is_teacher():
        st.markdown("### Create event ➕")
        with st.form("create_event_form"):
            title = st.text_input("Title")
            description = st.text_area("Description")
            date = st.date_input("Date")
            time = st.time_input("Time")
            location = st.text_input("Location")
            submit = st.form_submit_button("Create event")

        if submit:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO events (title, description, event_date, event_time, location, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (title, description, date, time, location, st.session_state.user_id))
                conn.commit()
                st.success("Event created ✅")
                cur.close()
                conn.close()
                st.rerun()
            except Exception as e:
                st.error(f"Error creating event: {e}"
                         f"Can't fix the error? DM me @arcsenus")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, event_date, event_time, location, created_by "
        "FROM events "
        "WHERE is_active = True "
        "ORDER BY event_date, event_time;")
    events = cur.fetchall()
    columns = [d[0] for d in cur.description]
    cur.close()
    conn.close()

    # Отрисовка
    for ev in events:
        ev_id, title, desc, ev_date, ev_time, location, created_by = ev
        st.subheader(f"**{title}**")
        st.write(f"Date: {ev_date}")
        st.write(f"Time: {ev_time}")
        st.write(f"Location: {location}")
        st.write(desc)

        user_id = st.session_state.get("user_id")
        if user_id:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM registrations WHERE event_id=%s AND user_id=%s;", (ev_id, user_id))
            joined = cur.fetchone() is not None
            cur.execute("SELECT COUNT(*) FROM registrations WHERE event_id=%s;", (ev_id,))
            count = cur.fetchone()[0]
            cur.close()
            conn.close()

            if joined:
                if st.button("Leave", key=f"leave_{ev_id}_{user_id}"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM registrations WHERE event_id=%s AND user_id=%s;", (ev_id, user_id))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("You left the event")
                    st.rerun()
            else:
                if st.button(f"Join ({count})", key=f"join_{ev_id}_{user_id}"):
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO registrations (user_id, event_id) VALUES (%s, %s)
                            ON CONFLICT (user_id, event_id) DO NOTHING;
                        """, (user_id, ev_id))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("You joined ✅")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}"
                                 f"Can't fix the error? DM me @arcsenus")
        else:
            st.info("Log in to join events")

    if not events:
        st.write("No events planned, come back later 💔")

    if is_teacher():
        st.markdown("### 📋 Your events:")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, event_date, event_time "
                    "FROM events "
                    "WHERE created_by = %s AND is_active = True " 
                    "ORDER BY event_date;",
                    (st.session_state.user_id,))
        my_events = cur.fetchall()
        for ev in my_events:
            ev_id, title, ev_date, ev_time = ev
            st.subheader(f"**{title}**")
            st.write(f"Date: {ev_date}")
            st.write(f"Time: {ev_time}")
            cur.execute("""
                SELECT u.id, u.first_name, u.last_name, u.email, u.phone
                FROM registrations r JOIN users u ON r.user_id = u.id
                WHERE r.event_id = %s;
            """, (ev_id,))
            participants = cur.fetchall()
            if participants:
                for p in participants:
                    st.write(f"- {p[1]} {p[2]} ({p[3]}) [{p[4]}]")
            else:
                st.write("No participants yet")
            if st.button("Delete event", key=f"del_{ev_id}"):
                cur.execute("DELETE FROM events WHERE id=%s;", (ev_id,))
                conn.commit()
                st.success("Event deleted")
                st.rerun()
        cur.close()
        conn.close()
    st.markdown("---")
    if st.button("Leave from account"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
