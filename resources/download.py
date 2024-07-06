import streamlit as st
import pandas as pd

# Set up the page
st.header("Downloads", divider='orange')
st.sidebar.title('Manage')

# Ensure user session is correctly set up
if 'user' not in st.session_state or 'username' not in st.session_state.user:
    st.error("User not logged in. Please log in to continue.")
    st.stop()

# Load the main dataframe from session state
if 'df' not in st.session_state:
    st.error("Main dataframe not found in session state. Please load the data.")
    st.stop()

# Check if there is selected data in session state
if 'selected_data' not in st.session_state:
    st.session_state.selected_data = pd.DataFrame()

if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

user_id = st.session_state.user['username']


# Save the selected data to the user-specific dataframe
if not st.session_state.selected_data.empty:
    selected_data = st.session_state.selected_data

    # Save the data to the user-specific dataframe tagged with username
    if user_id not in st.session_state.user_data:
        st.session_state.user_data[user_id] = pd.DataFrame()

    st.session_state.user_data[user_id] = pd.concat([st.session_state.user_data[user_id], selected_data]).drop_duplicates().reset_index(drop=True)

    # Clear the selected data after saving
    st.session_state.selected_data = pd.DataFrame()
    
    # Display the user-specific saved data
    st.write(f"Data saved for user {user_id}:")
    selected_downloads = st.dataframe(
        st.session_state.user_data[user_id],
        key='download_editor',
        selection_mode="multi-row",
        hide_index=False)

    # Correctly handle selected downloads
    selected_indices = selected_downloads.selection.rows
    selected_data_for_download = st.session_state.user_data[user_id].iloc[selected_indices]
    
    # Download button in the sidebar
    csv = selected_data_for_download.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='selected_data.csv',
        mime='text/csv',
    )

else:
    if user_id in st.session_state.user_data and not st.session_state.user_data[user_id].empty:
        # Display user-specific saved data
        st.write(f"Data saved for user {user_id}:")
        st.dataframe(st.session_state.user_data[user_id])
    else:
        st.write('No data selected. Please go back and select data to download.')
