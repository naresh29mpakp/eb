import streamlit as st
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time

# Initialize state variables
if 'meter_data' not in st.session_state:
    st.session_state['meter_data'] = {
        'last_bill_date': datetime.date.today(),
        'meter1_reading': 0,
        'meter2_reading': 0,
        'active_meter': 'meter1',  # Initial active meter
        'history': []
    }

# Function to calculate bill
def calculate_bill(units):
    TNEB_TARIFF = [(100, 0), (200, 2), (500, 3), (float('inf'), 5)]  # (upper_limit, rate_per_unit)
    total_cost = 0
    remaining_units = units

    for limit, rate in TNEB_TARIFF:
        if remaining_units > 0:
            applicable_units = min(remaining_units, limit)
            total_cost += applicable_units * rate
            remaining_units -= applicable_units
        else:
            break

    return total_cost

# Function to simulate WhatsApp notification
def send_notification(message):
    st.sidebar.write(f"WhatsApp Notification Sent: {message}")

# Scheduler for notifications
def schedule_notifications():
    scheduler = BackgroundScheduler()

    def notify_usage():
        st.session_state['meter_data']['last_notification'] = datetime.date.today()
        message = f"Reminder: Check EB meter readings. Current active meter: {st.session_state['meter_data']['active_meter']}"
        send_notification(message)

    def generate_bill():
        generate_bill_action()
        send_notification("New bill has been generated!")

    scheduler.add_job(notify_usage, 'interval', days=15, id='notify_usage')
    scheduler.add_job(generate_bill, 'interval', days=60, id='generate_bill')
    scheduler.start()

# Function to generate bill
def generate_bill_action():
    last_bill_date = st.session_state['meter_data']['last_bill_date']
    meter1_reading = st.session_state['meter_data']['meter1_reading']
    meter2_reading = st.session_state['meter_data']['meter2_reading']

    meter1_usage = meter1_reading - st.session_state['meter_data']['last_meter1_reading']
    meter2_usage = meter2_reading - st.session_state['meter_data']['last_meter2_reading']

    total_usage = meter1_usage + meter2_usage

    meter1_billable = max(0, min(total_usage, 100))
    meter2_billable = max(0, total_usage - meter1_billable)

    bill_amount = calculate_bill(meter1_billable) + calculate_bill(meter2_billable)

    st.session_state['meter_data']['history'].append({
        'date': last_bill_date,
        'meter1_usage': meter1_usage,
        'meter2_usage': meter2_usage,
        'bill_amount': bill_amount
    })

    st.session_state['meter_data']['last_bill_date'] = datetime.date.today()
    st.session_state['meter_data']['last_meter1_reading'] = meter1_reading
    st.session_state['meter_data']['last_meter2_reading'] = meter2_reading

# UI Layout
st.title("TNEB Meter Usage Optimizer")
st.sidebar.header("Controls")
st.sidebar.write("Use the controls to manage the meters.")

# Inputs
current_meter1_reading = st.number_input("Enter current Meter 1 reading", min_value=0, step=1, value=st.session_state['meter_data']['meter1_reading'])
current_meter2_reading = st.number_input("Enter current Meter 2 reading", min_value=0, step=1, value=st.session_state['meter_data']['meter2_reading'])

# Display last bill date and readings
st.write(f"Last Bill Date: {st.session_state['meter_data']['last_bill_date']}")
st.write(f"Meter 1 Last Reading: {st.session_state['meter_data']['meter1_reading']} units")
st.write(f"Meter 2 Last Reading: {st.session_state['meter_data']['meter2_reading']} units")

# Display usage since last bill
meter1_usage = max(0, current_meter1_reading - st.session_state['meter_data']['meter1_reading'])
meter2_usage = max(0, current_meter2_reading - st.session_state['meter_data']['meter2_reading'])
st.write(f"Usage since last bill: Meter 1: {meter1_usage} units, Meter 2: {meter2_usage} units")

# Toggle meter switch
active_meter = st.radio("Select active meter", options=['meter1', 'meter2'], index=0 if st.session_state['meter_data']['active_meter'] == 'meter1' else 1)
st.session_state['meter_data']['active_meter'] = active_meter
st.write(f"Active Meter: {active_meter}")

# Button to generate bill
if st.button("Generate Bill"):
    st.session_state['meter_data']['meter1_reading'] = current_meter1_reading
    st.session_state['meter_data']['meter2_reading'] = current_meter2_reading
    generate_bill_action()
    st.success("Bill generated and saved!")

# Display Billing History
if st.checkbox("Show Billing History"):
    if st.session_state['meter_data']['history']:
        for bill in st.session_state['meter_data']['history']:
            st.write(f"Date: {bill['date']}, Meter 1 Usage: {bill['meter1_usage']} units, Meter 2 Usage: {bill['meter2_usage']} units, Bill Amount: ₹{bill['bill_amount']}")
    else:
        st.write("No billing history available.")

# Start notifications in a background thread
if 'scheduler_thread' not in st.session_state:
    st.session_state['scheduler_thread'] = threading.Thread(target=schedule_notifications, daemon=True)
    st.session_state['scheduler_thread'].start()

st.sidebar.write("Notifications are scheduled.")
