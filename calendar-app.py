import streamlit as st
import json
from pathlib import Path
from streamlit_calendar import calendar
from datetime import date

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Shared Calendar",
    layout="wide"
)

# ------------------ MULTI-USER LOGIN ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# Hardcoded users
USERS = {
    "admin": "admin123",
    "aushin": "password123"
}

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_pressed = st.button("Login")
    if login_pressed:
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"✅ Logged in as {username}")
        else:
            st.error("❌ Incorrect username or password")

# Show login if not logged in
if not st.session_state.logged_in:
    login()
    st.stop()

# ------------------ LOGOUT ------------------
st.sidebar.success(f"✅ Logged in as {st.session_state.user}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.experimental_rerun()

# ------------------ FILE PATHS ------------------
EVENTS_FILE = Path("events.json")
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# ------------------ LOAD EVENTS ------------------
if EVENTS_FILE.exists():
    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)
else:
    events = []

# Convert events for calendar
calendar_events = [
    {
        "title": e["title"],
        "start": e["start"],
        "end": e.get("end", e["start"]),
        "extendedProps": {
            "image": e.get("image"),
            "instagram": e.get("instagram"),
        },
    }
    for e in events
]

# ------------------ CALENDAR ------------------
st.title("📅 Community Calendar")

clicked = calendar(
    events=calendar_events,
    options={
        "initialView": "dayGridMonth",
        "height": 650,
        "eventClick": "function(info){return info.event.id}"  # enable click detection
    },
    key="calendar"
)

# ------------------ SHOW EVENT DETAILS ------------------
if clicked and "event" in clicked:
    # Match clicked event by title
    clicked_title = clicked["event"]["title"]
    matching_events = [e for e in events if e["title"] == clicked_title]
    if matching_events:
        event = matching_events[0]  # pick first match
        st.subheader(event["title"])
        st.markdown(f"**Start Date:** {event['start']}")
        st.markdown(f"**End Date:** {event.get('end', event['start'])}")
        if event.get("image"):
            st.image(event["image"], use_column_width=True)
        if event.get("instagram"):
            st.markdown(f"📸 [Instagram link]({event['instagram']})")

# ------------------ ADD EVENT ------------------
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add Event")

with st.sidebar.form("add_event"):
    title = st.text_input("Event title")
    start_date = st.date_input("Start date", value=date.today())
    end_date = st.date_input("End date", value=date.today())
    instagram = st.text_input("Instagram link (optional)")
    image = st.file_uploader("Upload image", type=["jpg", "png"])
    submitted = st.form_submit_button("Add Event")

    if submitted:
        if not title:
            st.sidebar.error("Title is required")
        elif end_date < start_date:
            st.sidebar.error("End date cannot be before start date")
        else:
            image_path = None
            if image:
                image_path = IMAGES_DIR / image.name
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            new_event = {
                "title": title,
                "start": str(start_date),
                "end": str(end_date),
                "image": str(image_path) if image_path else None,
                "instagram": instagram,
            }

            events.append(new_event)

            with open(EVENTS_FILE, "w") as f:
                json.dump(events, f, indent=2)

            st.sidebar.success("✅ Event added — it will appear in the calendar immediately")
            st.experimental_rerun()
