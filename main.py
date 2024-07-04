import streamlit as st
import pandas as pd
import json
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(
    layout="wide"
)

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Admin", "User", "Visitor"]

def login():
    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if st.button("Log In"):
        st.session_state.role = role
        st.rerun()

def logout():
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

logout_page =  st.Page(logout, title="log out", icon=":material/logout:")
settings =  st.Page("settings.py", title="Settings", icon=":material/settings:")

resources_account = st.Page(
    "resources/account.py",
    title="Account",
    icon=":material/help:",
)

resources_download = st.Page(
    "resources/download.py",
    title="Downloads",
    icon=":material/download:",
)

resources_fastgolem = st.Page(
    "resources/fastgolem.py",
    title="FastGolem",
    icon=":material/person_search:",
    default=(role == "User"),
)

website_home =  st.Page(
    "website/home.py",
    title="Doctory Network",
    icon=":material/home:",
    default=(role == "Visitor"),
)
website_wwa = st.Page(
    "website/wwa.py",
    title="Who We Are",
    icon=":material/home:",
)

account_pages = [logout_page, settings]
resources_pages = [resources_account, resources_fastgolem, resources_download]
website_pages = [website_home, website_wwa]

st.title("FastGolem Demo 2024")
st.logo("images/doctory-purple_350x100.png", icon_image="images/doctory-purple_Favicon.png")

page_dictionary =  {}
if st.session_state.role in ["User", "Admin"]:
    page_dictionary["Resources"] = resources_pages
if st.session_state.role in ["Visitor", "Admin"]:
    page_dictionary["Website"] = website_pages

if len(page_dictionary) > 0:
    pg = st.navigation({"Account": account_pages} | page_dictionary)
else:
    pg = st.navigation([st.Page(login)])

st.markdown(
"""
<style>
.dataframe { width: 100% !important; }
[data-testid="stElementToolbar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True
)

pg.run()
