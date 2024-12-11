import streamlit as st
import datetime

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

# Initialize state
if 'meter_data' not in st.session_state:
    st.session_state.meter_data = {
        'last_reading_date': None,
        'meter1_reading': 0,
        'meter2_reading': 0,
        'history': []
    }

meter_data = st.session_state.meter_data

st.title("TNEB Domestic Meter Usage Optimizer")

# Show last billing details if available
if meter_data['last_reading_date']:
    st.subheader("Last Billing Details")
    st.write(f"**Date:** {meter_data['last_reading_date']}")
    st.write(f"**Meter 1 Last Reading:** {meter_data['meter1_reading']} units")
    st.write(f"**Meter 2 Last Reading:** {meter_data['meter2_reading']} units")

    # Calculate usage since last reading
    meter1_current = st.number_input("Enter current reading for Meter 1:", min_value=0, value=meter_data['meter1_reading'])
    meter2_current = st.number_input("Enter current reading for Meter 2:", min_value=0, value=meter_data['meter2_reading'])

    meter1_usage = max(0, meter1_current - meter_data['meter1_reading'])
    meter2_usage = max(0, meter2_current - meter_data['meter2_reading'])
    total_usage = meter1_usage + meter2_usage

    st.subheader("Usage Details")
    st.write(f"**Meter 1 Usage:** {meter1_usage} units")
    st.write(f"**Meter 2 Usage:** {meter2_usage} units")
    st.write(f"**Total Usage:** {total_usage} units")

    # Determine meter optimization
    meter1_final = min(total_usage, 100)
    meter2_final = max(0, total_usage - meter1_final)

    meter1_billable = max(0, meter1_final - 100)
    meter2_billable = max(0, meter2_final - 100)

    bill_amount = calculate_bill(meter1_billable) + calculate_bill(meter2_billable)

    st.subheader("Billing Details")
    st.write(f"**Meter 1 Billable Units:** {meter1_billable} units")
    st.write(f"**Meter 2 Billable Units:** {meter2_billable} units")
    st.write(f"**Total Bill Amount:** ₹{bill_amount}")

    # Notification about meter change
    if total_usage > 100:
        st.warning("**Meter change recommended:** Switch to Meter 2 for further usage.")

    # Save billing details on button click
    if st.button("Save Billing Details"):
        meter_data['history'].append({
            'date': datetime.date.today().strftime("%Y-%m-%d"),
            'meter1_usage': meter1_usage,
            'meter2_usage': meter2_usage,
            'bill_amount': bill_amount
        })
        meter_data['last_reading_date'] = datetime.date.today().strftime("%Y-%m-%d")
        meter_data['meter1_reading'] = meter1_current
        meter_data['meter2_reading'] = meter2_current
        st.success("Billing details saved.")

    # WhatsApp notification (simulation)
    st.write("### WhatsApp Notification")
    st.text_area("Notification Preview", value=f"Last Billing Date: {meter_data['last_reading_date']}\n"
                                        f"Meter 1 Usage: {meter1_usage} units\n"
                                        f"Meter 2 Usage: {meter2_usage} units\n"
                                        f"Total Bill Amount: ₹{bill_amount}\n"
                                        f"Meter change recommended: Switch to Meter 2 for further usage.")
else:
    # First-time setup
    st.subheader("Enter Initial Readings")
    last_reading_date = st.date_input("Last Reading Date")
    meter1_initial = st.number_input("Enter initial reading for Meter 1:", min_value=0, value=0)
    meter2_initial = st.number_input("Enter initial reading for Meter 2:", min_value=0, value=0)

    if st.button("Save Initial Readings"):
        meter_data['last_reading_date'] = last_reading_date.strftime("%Y-%m-%d")
        meter_data['meter1_reading'] = meter1_initial
        meter_data['meter2_reading'] = meter2_initial
        st.success("Initial readings saved.")

# Refresh data
if st.button("Refresh Data"):
    st.session_state.meter_data = {
        'last_reading_date': None,
        'meter1_reading': 0,
        'meter2_reading': 0,
        'history': []
    }
    st.success("Data has been refreshed.")

# Show billing history
if meter_data['history']:
    st.subheader("Billing History")
    for idx, bill in enumerate(meter_data['history'], start=1):
        st.write(f"**Bill {idx}:**")
        st.write(f"Date: {bill['date']}")
        st.write(f"Meter 1 Usage: {bill['meter1_usage']} units")
        st.write(f"Meter 2 Usage: {bill['meter2_usage']} units")
        st.write(f"Bill Amount: ₹{bill['bill_amount']}")
