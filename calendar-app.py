import streamlit as st
import json
from streamlit_calendar import calendar
import streamlit_authenticator as stauth
import yaml
from PIL import Image
from yaml.loader import SafeLoader

st.set_page_config(page_title="Shared Calendar", layout="wide")

# ---------- AUTH ----------
with open("users.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

name, authentication_status, username = authenticator.login("Login", "main")

if not authentication_status:
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"Welcome {name}")

# ---------- LOAD EVENTS ----------
with open("events.json", "r") as f:
    events = json.load(f)

calendar_events = [
    {
        "title": e["title"],
        "start": e["start"],
        "extendedProps": {
            "image": e["image"],
            "instagram": e["instagram"]
        }
    }
    for e in events
]

# ---------- CALENDAR ----------
st.header("📅 Community Calendar")

calendar_options = {
    "initialView": "dayGridMonth",
    "eventClick": True
}

clicked = calendar(
    events=calendar_events,
    options=calendar_options,
    key="calendar",
)

# ---------- EVENT DETAILS ----------
if clicked and "event" in clicked:
    event = clicked["event"]
    props = event["extendedProps"]

    st.subheader(event["title"])

    if props.get("image"):
        img = Image.open(props["image"])
        st.image(img, use_column_width=True)

    if props.get("instagram"):
        st.markdown(f"📸 [View on Instagram]({props['instagram']})")

# ---------- ADD EVENT (ADMIN / ALL USERS) ----------
st.sidebar.subheader("➕ Add Event")

with st.sidebar.form("add_event"):
    title = st.text_input("Title")
    date = st.date_input("Date")
    instagram = st.text_input("Instagram Link")
    image = st.file_uploader("Image", type=["jpg", "png"])

    submitted = st.form_submit_button("Add")

    if submitted:
        img_path = None
        if image:
            img_path = f"images/{image.name}"
            with open(img_path, "wb") as f:
                f.write(image.getbuffer())

        events.append({
            "title": title,
            "start": str(date),
            "image": img_path,
            "instagram": instagram
        })

        with open("events.json", "w") as f:
            json.dump(events, f, indent=2)

        st.success("Event added! Refresh the page.")
