import streamlit as st

st.header("Home")
st.write(f"You are logged in as {st.session_state.role}")