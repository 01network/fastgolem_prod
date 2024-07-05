import streamlit as st

# Check if there is selected data in session state
if 'selected_data' in st.session_state:
    selected_data = st.session_state.selected_data

    st.sidebar.header('Download Selected Data')

    # Display the selected data
    st.write('Selected Data:')
    st.dataframe(selected_data)

    # Download button in the sidebar
    csv = selected_data.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='selected_data.csv',
        mime='text/csv',
    )
else:
    st.write('No data selected. Please go back and select data to download.')
