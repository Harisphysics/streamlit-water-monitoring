import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
r_layout = "wide"

#set up bassic
st.set_page_config(
    page_title="Water Monitoring",
    layout=r_layout, 
    initial_sidebar_state="expanded" 
)
page_width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH',  want_output = True,)


creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets.connections)
client = gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_data(sheet):
    sheet = client.open("Data_Air").worksheet(sheet)
    data = sheet.get_all_records()[-100:]
    return data

sheet_1 = load_data("Sheet1")

# header
html_header = """
    <div class="jumbotron" style="display: flex; justify-content: space-around; flex-direction: row; align-items: center;">
    <img class="logo" src="https://upload.wikimedia.org/wikipedia/commons/9/9a/Kementerian_Agama_new_logo.png" alt="logo UNJ" style="width: 100px; height: 100px;margin-right: 20px;"></img>
        <h1 style=' color: green; width: auto;'>Monitoring Air Realtime</h1>
    </div>
"""
st.markdown(html_header, unsafe_allow_html=True)

data_list_1 = sheet_1

dates = [row['Date'] for row in data_list_1]
times = [row['Time'] for row in data_list_1]
turbidity = [(-111.25*(row['Turbidity']*5/1024) + 506.67) for row in data_list_1]
ph = [row['pH'] for row in data_list_1]
tds = [(row['TDS']+1.3333)/4.8 for row in data_list_1]

# Combine Date and Time into DateTime
datetimes = [datetime.strptime(f"{date} {time}", "%m/%d/%Y %H.%M.%S") for date, time in zip(dates, times)]

#urrent_values = data_list_1[0]  # Assuming the most recent data is at the top
st.write("----")
st.write("### Nilai pengukuran saat ini")
columns = st.columns(3, gap='large')

# Function to create styled markdown for parameters and values
def create_styled_markdown(label, value):
    return f"""
    <div class="parameter-label">{label}</div>
    <div class="current-value">{value}</div>
    """

columns[0].markdown(create_styled_markdown("NTU", turbidity[-1]), unsafe_allow_html=True)
columns[1].markdown(create_styled_markdown("pH", ph[-1]), unsafe_allow_html=True)
columns[2].markdown(create_styled_markdown("mg/mL", tds[-1]), unsafe_allow_html=True)

if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()

# Create a subplot for Turbidity, pH, and TDS
fig = make_subplots(
    rows=3, cols=1, 
    subplot_titles=('Turbidity', 'pH', 'TDS'),
    shared_xaxes=True
)

# Add Turbidity plot
fig.add_trace(go.Scatter(x=datetimes, y=turbidity, mode='lines+markers', name='Turbidity'), row=1, col=1)

# Add pH plot
fig.add_trace(go.Scatter(x=datetimes, y=ph, mode='lines+markers', name='pH', line=dict(color='green')), row=2, col=1)

# Add TDS plot
fig.add_trace(go.Scatter(x=datetimes, y=tds, mode='lines+markers', name='TDS', line=dict(color='blue')), row=3, col=1)

# Update layout for responsiveness
fig.update_layout(
    height=600 if page_width > 500 else 1000,  # Adjust height based on screen size
    showlegend=False,
    title_text="Water Quality Parameters Over Time",
    xaxis_title="DateTime",
)

# Display the plot
st.plotly_chart(fig, use_container_width=True)

# CSS
style = """
    <style>
    .current-value {
        font-size: 24px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .parameter-label {
        font-size: 18px;
        color: #4b4bff;
    }
    @media screen and (max-width: 500px) {
        .logo {
            display: none;
        }
    }
    </style>
"""
st.markdown(style, unsafe_allow_html=True)
