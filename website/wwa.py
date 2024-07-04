import streamlit as st

st.header("Who we are")
st.write(f"You are logged in as {st.session_state.role}")