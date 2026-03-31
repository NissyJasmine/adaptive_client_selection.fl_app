import streamlit as st
import pandas as pd
import numpy as np
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="FL Device Selector", layout="wide")

st.title("📱 Federated Learning Device Selection Engine")
st.markdown("""
This dashboard selects the best hardware clients for Federated Learning training 
based on your specific hardware requirements.
""")


# --- DATA FETCHING (DIRECT READ FOR GLOBAL DEPLOYMENT) ---
@st.cache_data
def load_data():
    file_path = "devices_dataset.csv.xlsx"
    try:
        # Check if file exists to provide a clear error message
        if os.path.exists(file_path):
            # Read directly from the Excel file
            df = pd.read_excel(file_path)
            # Ensure all data is treated as strings to prevent ArrowTypeError
            return df.astype(str)
        else:
            st.error(f"File '{file_path}' not found in the repository.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


df = load_data()

if not df.empty:
    # --- DATA PRE-PROCESSING ---
    # Extracting numeric values from strings like '8 GB' for filtering logic
    df['RAM_num'] = df['RAM'].str.extract('(\d+)').astype(float)
    df['Bat_num'] = df['Battery Capacity'].str.extract('(\d+)').astype(float)

    # --- SIDEBAR: USER REQUIREMENTS ---
    st.sidebar.header("⌨️ Set Hardware Requirements")

    # Manual Number Inputs for precise filtering
    req_ram = st.sidebar.number_input("Minimum RAM (GB)", min_value=1, max_value=64, value=8)
    req_battery = st.sidebar.number_input("Minimum Battery (mAh)", min_value=1000, max_value=10000, value=4500)

    # Dynamic Processor Dropdown populated from the Excel data
    processor_options = ["All"] + sorted(df['Processor'].unique().tolist())
    selected_cpu = st.sidebar.selectbox("Select Processor Type", options=processor_options)

    # --- FILTERING LOGIC ---
    mask = (df['RAM_num'] >= req_ram) & (df['Bat_num'] >= req_battery)

    if selected_cpu != "All":
        mask = mask & (df['Processor'] == selected_cpu)

    filtered_df = df[mask].copy()

    # --- OUTPUT DISPLAY ---
    if not filtered_df.empty:
        # Calculate Simulated Accuracy Score for FL suitability
        filtered_df['Accuracy_Score'] = (
                (filtered_df['RAM_num'] * 1.8) +
                (filtered_df['Bat_num'] / 130) +
                35
        ).clip(70.0, 99.2)

        st.subheader(f"✅ Found {len(filtered_df)} Matching Devices")

        # Dropdown to select a specific device from filtered results
        selected_model = st.selectbox("Select a device for full feature output:", filtered_df['Model Name'])
        device_data = filtered_df[filtered_df['Model Name'] == selected_model].iloc[0]

        # Final Feature Output Cards
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.header(f"✨ {device_data['Model Name']}")
            st.metric(label="Predicted FL Accuracy", value=f"{float(device_data['Accuracy_Score']):.2f}%")
            st.write(f"**Manufacturer:** {device_data['Company Name']}")
            st.write(f"**Processor:** {device_data['Processor']}")

        with col2:
            st.info("📋 Technical Specifications")
            specs = {
                "RAM": device_data['RAM'],
                "Battery": device_data['Battery Capacity'],
                "Weight": device_data.get('Mobile Weight', 'N/A'),
                "Internal Storage": device_data.get('Internal Storage', 'N/A')
            }
            st.table(pd.DataFrame(specs.items(), columns=["Feature", "Value"]))

        st.success("Analysis complete. This device is eligible for the Federated Learning cluster.")

    else:
        st.warning("No devices match your current requirements. Try lowering your RAM or Battery minimums.")

else:
    st.info("Please ensure 'devices_dataset.csv.xlsx' is uploaded to your GitHub repository.")