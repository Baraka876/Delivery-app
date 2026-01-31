import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Pro Delivery Log", layout="wide")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(worksheet="Sheet1")

st.title("🚚 Professional Delivery & Expense Tracker")

# 2. Input Section
with st.expander("➕ Log New Delivery & Expenses", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date = st.date_input("Delivery Date", datetime.now())
            client = st.text_input("Company / Recipient")
            lpo = st.text_input("LPO Number")
            delivered_by = st.text_input("Delivered By (Name)")
        
        with col2:
            product = st.text_input("Product Name")
            qty = st.number_input("Quantity", min_value=0.0)
            status = st.selectbox("Payment Status", ["Paid", "Credit", "Partial"])
            invoice_img = st.file_uploader("Upload Signed Invoice (Photo)", type=['jpg', 'png', 'jpeg'])
            
        with col3:
            st.markdown("**Expenses**")
            trans_exp = st.number_input("Transport Cost", min_value=0.0)
            bites_exp = st.number_input("Small Bites", min_value=0.0)
            notes = st.text_area("Additional Notes")
            
        total_exp = trans_exp + bites_exp
        st.markdown(f"### Total Expense: **{total_exp}**")
        
        submit = st.form_submit_button("Save Delivery to Database")

# 3. Saving Logic
if submit:
    new_entry = pd.DataFrame([{
        "Date": date.strftime("%Y-%m-%d"),
        "Client": client,
        "LPO": lpo,
        "Product": product,
        "Qty": qty,
        "Transport": trans_exp,
        "Bites": bites_exp,
        "Total_Exp": total_exp,
        "Status": status,
        "Staff": delivered_by,
        "Notes": notes
    }])
    updated_df = pd.concat([data, new_entry], ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_df)
    st.success("✅ Logged successfully!")
    st.rerun()

# 4. Reports & Bookkeeping Section
st.divider()
st.header("📊 Bookkeeping & Monthly Reports")

if not data.empty:
    # Filter for the current month
    data['Date'] = pd.to_datetime(data['Date'])
    current_month = datetime.now().strftime("%m")
    month_data = data[data['Date'].dt.strftime('%m') == current_month]
    
    # Totals First (As requested)
    t1, t2, t3 = st.columns(3)
    t1.metric("Month Total Expenses", f"{month_data['Total_Exp'].sum()}")
    t2.metric("Total Qty Delivered", f"{month_data['Qty'].sum()}")
    t3.metric("Pending Credits", len(month_data[month_data['Status'] == "Credit"]))

    st.subheader("Monthly Detailed View")
    st.dataframe(month_data, use_container_width=True)

    # Export for WhatsApp/Sharing
    csv = month_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📩 Download Report for WhatsApp",
        data=csv,
        file_name=f"Delivery_Report_{datetime.now().strftime('%Y-%m')}.csv",
        mime='text/csv',
    )
else:
    st.info("No data available yet.")
