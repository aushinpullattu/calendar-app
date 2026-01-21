import streamlit as st
import json
from pathlib import Path
from streamlit_calendar import calendar

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Shared Calendar",
    layout="wide"
)

# ------------------ SIMPLE LOGIN ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Incorrect username or password")

if not st.session_state.logged_in:
    login()
    st.stop()

# ------------------ LOGOUT ------------------
st.sidebar.success("✅ Logged in as admin")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ------------------ PATHS ------------------
EVENTS_FILE = Path("events.json")
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# ------------------ LOAD EVENTS ------------------
if EVENTS_FILE.exists():
    with open(EVENTS_FILE, "r") as f:
        events = json.load(f)
else:
    events = []

calendar_events = [
    {
        "title": e["title"],
        "start": e["start"],
        "extendedProps": {
            "image": e.get("image"),
            "instagram": e.get("instagram"),
        },
    }
    for e in events
]

# ------------------ UI ------------------
st.title("📅 Community Calendar")

clicked = calendar(
    events=calendar_events,
    options={
        "initialView": "dayGridMonth",
        "height": 650,
    },
    key="calendar",
)

# ------------------ EVENT DETAILS ------------------
if clicked and "event" in clicked:
    event = clicked["event"]
    props = event.get("extendedProps", {})

    st.subheader(event["title"])

    if props.get("image"):
        st.image(props["image"], use_column_width=True)

    if props.get("instagram"):
        st.markdown(f"📸 [Instagram link]({props['instagram']})")

# ------------------ ADD EVENT ------------------
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add Event")

with st.sidebar.form("add_event"):
    title = st.text_input("Event title")
    date = st.date_input("Event date")
    instagram = st.text_input("Instagram link (optional)")
    image = st.file_uploader("Upload image", type=["jpg", "png"])

    submitted = st.form_submit_button("Add Event")

    if submitted:
        if not title:
            st.sidebar.error("Title is required")
        else:
            image_path = None
            if image:
                image_path = IMAGES_DIR / image.name
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())

            events.append({
                "title": title,
                "start": str(date),
                "image": str(image_path) if image_path else None,
                "instagram": instagram,
            })

            with open(EVENTS_FILE, "w") as f:
                json.dump(events, f, indent=2)

            st.sidebar.success("✅ Event added — refresh if needed")
