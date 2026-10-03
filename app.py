import json

import streamlit as st
import smtplib

from google import genai
from google.genai import types
from email.mime.text import MIMEText

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

MODEL_NAME = "gemini-3.5-flash-lite"
st.set_page_config(page_title="LabelLens", page_icon="🏷️")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])

        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content,})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text

    except Exception as error:
        return f"Sorry, something went wrong: {error}"


def send_email(to_address, subject, body):
    try:
        message = MIMEText(body)

        message["Subject"] = subject
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_address

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(message)

        return True, "Email sent successfully."

    except Exception as error:
        return False, str(error)

if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False


if not st.session_state.onboarded:
    st.title("🏷️ LabelLens")
    st.caption("Understand what's inside.")
    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        email_address = st.text_input(
            "Your email address",
            placeholder="you@example.com",
            help="Your LabelLens analysis will be sent here.",
        )
        submitted = st.form_submit_button("Let's go 🚀")
    if submitted:
        missing_fields = []

        if not name.strip():
            missing_fields.append("name")

        if not email_address.strip():
            missing_fields.append("email address")

        if missing_fields:
            if len(missing_fields) == 2:
                st.warning("Please enter your name and email address.")
            else:
                st.warning(f"Please enter your {missing_fields[0]}.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email_address = (email_address.strip())

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            st.session_state.messages = []
            st.session_state.analysis_ready = False
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("🏷️ LabelLens")

with button_col:
    send_disabled = not st.session_state.analysis_ready

    send_mail = st.button(
        "Send to 📧 Mail",
        disabled=send_disabled,
        use_container_width=True,
    )

if send_mail:
    with st.spinner("Preparing your LabelLens analysis..."):
        summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

    success, info = send_email(
        st.session_state.email_address,
        "Your LabelLens Product Analysis",
        summary,
    )

    if success:
        st.success("Analysis sent to your email 📧")
    else:
        st.error(f"Couldn't send the email: {info}")

st.caption(
    f"Logged in as {st.session_state.name} · "
    f"Analysis will be sent to "f"{st.session_state.email_address}"
)

if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Ask about a product, or attach a photo of its label",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Analyze this product label and explain the "
            "product name, brand, ingredients, nutrition "
            "information, allergens, additives, preservatives, "
            "and important label information. Only use information "
            "that is visible and readable in the provided image."
        )

    with st.spinner("Analyzing the product label..."):
        answer = ask_gemini(parts)
    add_message("assistant", "text", answer)

    st.session_state.analysis_ready = True
    st.rerun()