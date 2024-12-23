import streamlit as st
import pandas as pd
import datetime
from github import Github

# GitHub credentials
GITHUB_TOKEN = "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"  # Your token
REPO_NAME = "naresh29mpakp/eb"  # Your repository name
FILE_PATH = "meter_data.csv"  # Path to the file in the repo

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Load existing data
try:
    contents = repo.get_contents(FILE_PATH)
    csv_data = contents.decoded_content.decode()
    meter_data = pd.read_csv(pd.compat.StringIO(csv_data), parse_dates=["Date"])
except Exception as e:
    meter_data = pd.DataFrame(columns=["Date", "Meter 1 Reading", "Meter 2 Reading"])

# Initialize session state for readings
if "meter_data" not in st.session_state:
    st.session_state["meter_data"] = meter_data

# Title and app description
st.title("Persistent Meter Reading Tracker")
st.write("Track and update your meter readings. Data is saved to GitHub and persists between sessions.")

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
        # Save data to GitHub
        csv_content = st.session_state["meter_data"].to_csv(index=False)
        if contents:
            repo.update_file(FILE_PATH, "Update meter data", csv_content, contents.sha)
        else:
            repo.create_file(FILE_PATH, "Create meter data file", csv_content)
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
    if contents:
        repo.delete_file(FILE_PATH, "Clear all meter data", contents.sha)
    st.session_state["meter_data"] = pd.DataFrame(columns=["Date", "Meter 1 Reading", "Meter 2 Reading"])
    st.success("All data cleared!")

# Footer
st.sidebar.write("Persistent Meter Reading Tracker")
