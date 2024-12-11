import streamlit as st
import datetime

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
st.sidebar.header("Navigation")
options = ["Enter Current Readings", "Refresh Data", "Show Billing History"]
choice = st.sidebar.radio("Choose an action:", options)

if choice == "Enter Current Readings":
    st.subheader("Enter Current Readings")
    
    if meter_data['last_reading_date'] is None:
        st.write("First-time setup: Enter initial readings.")
    else:
        st.write("Update with new readings.")

    last_reading_date = st.date_input("Enter last reading date:", datetime.date.today())
    meter1_current = st.number_input("Enter Meter 1 current reading:", min_value=0, step=1)
    meter2_current = st.number_input("Enter Meter 2 current reading:", min_value=0, step=1)

    if st.button("Generate Bill"):
        if meter_data['last_reading_date'] is not None:
            meter1_usage = max(0, meter1_current - meter_data['meter1_reading'])
            meter2_usage = max(0, meter2_current - meter_data['meter2_reading'])

            total_usage = meter1_usage + meter2_usage
            meter1_final = min(total_usage, 100)
            meter2_final = max(0, total_usage - meter1_final)

            meter1_billable = max(0, meter1_final - 100)
            meter2_billable = max(0, meter2_final - 100)

            bill_amount = calculate_bill(meter1_billable) + calculate_bill(meter2_billable)

            bill_details = {
                'date': last_reading_date.strftime("%Y-%m-%d"),
                'meter1_usage': meter1_usage,
                'meter2_usage': meter2_usage,
                'bill_amount': bill_amount
            }
            meter_data['history'].append(bill_details)

            st.success(f"Bill Generated:")
            st.write(f"**Meter 1 Usage:** {meter1_usage} units")
            st.write(f"**Meter 2 Usage:** {meter2_usage} units")
            st.write(f"**Total Bill Amount:** ₹{bill_amount}")

        meter_data['last_reading_date'] = last_reading_date
        meter_data['meter1_reading'] = meter1_current
        meter_data['meter2_reading'] = meter2_current

elif choice == "Refresh Data":
    if st.button("Refresh Data"):
        st.session_state.meter_data = {
            'last_reading_date': None,
            'meter1_reading': 0,
            'meter2_reading': 0,
            'history': []
        }
        st.success("Data has been refreshed.")

elif choice == "Show Billing History":
    st.subheader("Billing History")
    if meter_data['history']:
        for idx, bill in enumerate(meter_data['history'], start=1):
            st.write(f"### Bill {idx}")
            st.write(f"**Date:** {bill['date']}")
            st.write(f"**Meter 1 Usage:** {bill['meter1_usage']} units")
            st.write(f"**Meter 2 Usage:** {bill['meter2_usage']} units")
            st.write(f"**Bill Amount:** ₹{bill['bill_amount']}")
            st.write("---")
    else:
        st.info("No billing history available.")
