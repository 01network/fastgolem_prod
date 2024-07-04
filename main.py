import streamlit as st
import logging
import os

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROLES = [None, "Admin", "User", "Visitor"]

secrets = st.secrets

# Ensure .data folder exists
data_folder = '.data'
os.makedirs(data_folder, exist_ok=True)
logger.info(f"/.data folder created")

# Check if the file .data/hcp_data.csv exists
if os.path.exists(os.path.join(data_folder, 'hcp_data.csv')):
    st.session_state.file_uploaded = True
    logger.info("Existing hcp_data.csv found, setting file_uploaded to True")
else:
    st.session_state.file_uploaded = False
    logger.info(f"No hcp_data.csv file found")

st.set_page_config(
    layout="wide"
)

# Session state for role
if "role" not in st.session_state:
    st.session_state.role = None

# # Session state for file upload
# if "file_uploaded" not in st.session_state:
#     st.session_state.file_uploaded = False

# Function to save uploaded file
def save_uploaded_file(uploaded_file):
    if uploaded_file.name != 'hcp_data.csv':
        st.error(f"{uploaded_file.name} is the wrong type!")
        logger.info(f"Upload of {uploaded_file.name} failed.")
        return
    with open(os.path.join(data_folder, uploaded_file.name), 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.file_uploaded = True
    st.success(f"Saved file: {uploaded_file.name}")
    logger.info(f"File {uploaded_file.name} saved successfully")

# # File upload section
# st.title("CSV File Upload")

if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)
else:
    logger.info(f"Data ingestion is successfull")

def login():
    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if role == "Admin":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            #Check admin credentials
            if username in secrets.admin and secrets.admin[username] == password:
                st.session_state.role = role
                st.session_state.username = username
                st.sidebar.success(f"Logged in as {role}")
                logger.info(f"Admin {username} logged in")
                st.rerun()
            else:
                st.error("Invalid admin username or password")
                logger.info(f"Admin login attempt failed")
    
    elif role == "User":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            if username in secrets.user and secrets.user[username] == password:
                st.session_state.role = role
                st.session_state.username = username
                st.sidebar.success(f"Logged in as {role}")
                logger.info(f"User {username} logged in")
                st.rerun()
            else:
                st.error("Invalid username or password")
                logger.info(f"User login attempt failed")
    else:
        if st.button("Log In"):
            st.session_state.role = role
            logger.info(f"Visitor User log in successful")
            st.sidebar.success(f"Logged in as {role}")
            st.rerun()

def logout():
    st.session_state.role = None
    st.session_state.file_uploaded = False
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


if st.session_state.file_uploaded:
    st.title("FastGolem Demo 2024")
    st.logo("images/doctory-purple_350x100.png", icon_image="images/doctory-purple_Favicon.png")

    page_dictionary =  {}
    if st.session_state.role in ["User"]:
        page_dictionary["Resources"] = resources_pages
        logger.info(f"NAV - Resources")
    if st.session_state.role in ["Visitor"]:
        page_dictionary["Website"] = website_pages
        logger.info(f"NAV -  Website")
    if st.session_state.role in ["Admin"]:
        page_dictionary["Resources"] = resources_pages
        logger.info(f"NAV - Resources")
    if len(page_dictionary) > 0:
        pg = st.navigation({"Account": account_pages} | page_dictionary)
        logger.info(f"NAV - Account")
    else:
        pg = st.navigation([st.Page(login)])
        logger.info(f"NAV - Login")

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
    logger.info(f"Page navigation initiated successfully")
    pg.run()
else:
    st.info("Please upload the source CSV file to proceed to role selection.")
