import streamlit as st
import pandas as pd
import datetime

# Initialize session state for readings
if 'meter_data' not in st.session_state:
    st.session_state['meter_data'] = []

# Title and app description
st.title("Meter Reading Tracker")
st.write("Track and update your meter readings. Readings are recorded every 15 days.")

# Input fields
st.header("Add New Reading")
reading_date = st.date_input("Reading Date", datetime.date.today())
meter1_reading = st.number_input("Meter 1 Reading", min_value=0, step=1)
meter2_reading = st.number_input("Meter 2 Reading", min_value=0, step=1)

# Add new reading button
if st.button("Add Reading"):
    if st.session_state['meter_data'] and reading_date <= st.session_state['meter_data'][-1]['date']:
        st.warning("New reading date must be after the last recorded date.")
    else:
        st.session_state['meter_data'].append({
            'date': reading_date,
            'meter1_reading': meter1_reading,
            'meter2_reading': meter2_reading
        })
        st.success("Reading added successfully!")

# Display readings in a table
if st.session_state['meter_data']:
    st.header("Reading History")
    
    # Calculate differences and prepare data for display
    data = []
    for i in range(len(st.session_state['meter_data'])):
        current = st.session_state['meter_data'][i]
        if i == 0:
            diff1 = diff2 = 0
        else:
            previous = st.session_state['meter_data'][i - 1]
            diff1 = current['meter1_reading'] - previous['meter1_reading']
            diff2 = current['meter2_reading'] - previous['meter2_reading']
        
        data.append({
            'Date': current['date'],
            'Meter 1 Reading': current['meter1_reading'],
            'Meter 2 Reading': current['meter2_reading'],
            'Meter 1 Usage': diff1,
            'Meter 2 Usage': diff2
        })

    df = pd.DataFrame(data)
    st.table(df)
else:
    st.write("No readings recorded yet.")

# Refresh button to clear all data
if st.button("Refresh Data"):
    st.session_state['meter_data'] = []
    st.success("All data cleared!")

# Footer
st.sidebar.write("Mobile-friendly Meter Reading Tracker")
