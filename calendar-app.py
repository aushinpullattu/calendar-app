import streamlit as st
import json
from streamlit_calendar import calendar
import streamlit_authenticator as stauth
import yaml
from PIL import Image
from yaml.loader import SafeLoader
from pathlib import Path

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Shared Calendar",
    layout="wide"
)

# ------------------ LOAD AUTH CONFIG ------------------
with open("users.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ------------------ LOGIN (SIDEBAR) ------------------
name, authentication_status, username = authenticator.login(
    location="sidebar"
)

if authentication_status is False:
    st.error("❌ Username/password is incorrect")
    st.stop()

if authentication_status is None:
    st.warning("🔐 Please enter your username and password")
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"Welcome {name}")

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

# Convert to calendar format
calendar_events = [
    {
        "title": e["title"],
        "start": e["start"],
        "extendedProps": {
            "image": e.get("image"),
            "instagram": e.get("instagram")
        }
    }
    for e in events
]

# ------------------ MAIN UI ------------------
st.title("📅 Community Calendar")

clicked = calendar(
    events=calendar_events,
    options={
        "initialView": "dayGridMonth",
        "height": 650
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
        st.markdown(
            f"📸 [View Instagram Post]({props['instagram']})",
            unsafe_allow_html=True
        )

# ------------------ ADD EVENT FORM ------------------
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add New Event")

with st.sidebar.form("add_event"):
    title = st.text_input("Event title")
    date = st.date_input("Event date")
    instagram = st.text_input("Instagram link (optional)")
    image = st.file_uploader("Upload image", type=["jpg", "png"])

    submitted = st.form_submit_button("Add Event")

    if submitted and title:
        image_path = None

        if image:
            image_path = IMAGES_DIR / image.name
            with open(image_path, "wb") as f:
                f.write(image.getbuffer())

        events.append({
            "title": title,
            "start": str(date),
            "image": str(image_path) if image_path else None,
            "instagram": instagram
        })

        with open(EVENTS_FILE, "w") as f:
            json.dump(events, f, indent=2)

        st.sidebar.success("✅ Event added! Refresh the page.")
