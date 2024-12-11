import streamlit as st
import pandas as pd
import datetime
import os

# File to store data
DATA_FILE = "meter_data.csv"

# Load existing data from CSV
if os.path.exists(DATA_FILE):
    meter_data = pd.read_csv(DATA_FILE, parse_dates=["Date"])
else:
    meter_data = pd.DataFrame(columns=["Date", "Meter 1 Reading", "Meter 2 Reading"])

# Initialize session state for readings
if "meter_data" not in st.session_state:
    st.session_state["meter_data"] = meter_data

# Title and app description
st.title("Persistent Meter Reading Tracker")
st.write("Track and update your meter readings. Data is saved locally and persists between sessions.")

# Input fields
st.header("Add New Reading")
reading_date = st.date_input("Reading Date", datetime.date.today())
meter1_reading = st.number_input("Meter 1 Reading", min_value=0, step=1)
meter2_reading = st.number_input("Meter 2 Reading", min_value=0, step=1)

# Add new reading button
if st.button("Add Reading"):
    if not st.session_state["meter_data"].empty and pd.to_datetime(reading_date) <= st.session_state["meter_data"]["Date"].iloc[-1]:
        st.warning("New reading date must be after the last recorded date.")
    else:
        new_data = {
            "Date": reading_date,
            "Meter 1 Reading": meter1_reading,
            "Meter 2 Reading": meter2_reading,
        }
        st.session_state["meter_data"] = pd.concat([st.session_state["meter_data"], pd.DataFrame([new_data])], ignore_index=True)
        st.session_state["meter_data"].to_csv(DATA_FILE, index=False)  # Save to file
        st.success("Reading added successfully!")

# Display readings in a table
if not st.session_state["meter_data"].empty:
    st.header("Reading History")
    
    # Calculate differences and prepare data for display
    data = []
    for i in range(len(st.session_state["meter_data"])):
        current = st.session_state["meter_data"].iloc[i]
        if i == 0:
            diff1 = diff2 = 0
        else:
            previous = st.session_state["meter_data"].iloc[i - 1]
            diff1 = current["Meter 1 Reading"] - previous["Meter 1 Reading"]
            diff2 = current["Meter 2 Reading"] - previous["Meter 2 Reading"]
        
        data.append({
            "Date": current["Date"],
            "Meter 1 Reading": current["Meter 1 Reading"],
            "Meter 2 Reading": current["Meter 2 Reading"],
            "Meter 1 Usage": diff1,
            "Meter 2 Usage": diff2
        })

    df = pd.DataFrame(data)
    st.table(df)
else:
    st.write("No readings recorded yet.")

# Refresh button to clear all data
if st.button("Refresh Data"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)  # Delete the file to clear data
    st.session_state["meter_data"] = pd.DataFrame(columns=["Date", "Meter 1 Reading", "Meter 2 Reading"])
    st.success("All data cleared!")

# Footer
st.sidebar.write("Persistent Meter Reading Tracker")
