import pandas as pd
import streamlit as st

BranchData_URL = 'https://raw.githubusercontent.com/hazeyblu/Essmart/main/BranchDetails.csv'
CovidData_URL = 'https://api.covid19india.org/csv/latest/districts.csv'

st.title("Essmart Covid Response Hub")


@st.cache(show_spinner=False)
def load_data(branch_data=False, districts_list=None):
    if districts_list is None:
        districts_list = ['']
    if branch_data:
        br_details = pd.read_csv(BranchData_URL)
        in_districts = br_details.District.unique()
        return br_details, in_districts
    else:
        data = pd.read_csv(CovidData_URL)
        needed_data = data[data['District'].isin(districts_list)]
        print(needed_data.columns)
        return needed_data


@st.cache(show_spinner=False)
def data_wrangle(dataset, districts_list=None):
    if districts_list is None:
        districts_list = ['']
    print("hi")


branch_details, interested_districts = load_data(branch_data=True)

truncated_data = load_data(districts_list=interested_districts)


st.sidebar.subheader('State-Level Information')
selectedState = st.sidebar.selectbox("State level information:", ('Karnataka', 'Andhra Pradesh', 'Tamil Nadu'))
state_short_data = truncated_data[truncated_data['State'] == selectedState]
district_short_list = state_short_data.District.unique()
st.header('Districts in State with Essmart presence:')
district_list = []
for district in district_short_list:
    if st.checkbox(district, value=True):
        district_list.append(district)


st.subheader('\nRaw Data')
if st.checkbox('Show branch & district information'):
    st.subheader('Branch Info')
    st.dataframe(data=branch_details, height=600)
