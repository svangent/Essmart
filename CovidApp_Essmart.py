import pandas as pd
import streamlit as st

BranchData_URL = 'https://raw.githubusercontent.com/hazeyblu/Essmart/main/BranchDetails.csv'
CovidData_URL = 'https://api.covid19india.org/csv/latest/districts.csv'

st.set_page_config(page_title='ESSMART vs Covid', page_icon="ESS", layout='wide', initial_sidebar_state='collapsed')
st.markdown("<h1 style='text-align: center; color: #39A275;'>Essmart Covid Response Hub</h1>",
            unsafe_allow_html=True)


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
    rolling_windows = [7, 14, 21, 28]
    print("hi")


branch_details, interested_districts = load_data(branch_data=True)

truncated_data = load_data(districts_list=interested_districts)

pre_select = st.sidebar.checkbox(label="Select all branches", value=False,
                                 help='Check if you want to select all branches in State')
c1, c2, c3, c4 = st.beta_columns((1, 1, 2, 2))
c1.header('State-Level Information')
selectedState = c1.selectbox("State level information:", ('Karnataka', 'Andhra Pradesh', 'Tamil Nadu'))
state_short_data = truncated_data[truncated_data.State == selectedState]
district_short_list = state_short_data.District.unique()
branch_short_list = branch_details[branch_details.District.isin(district_short_list)]
c2.header('Essmart branches:')
district_list = []
branch_list = []
for branch, district in zip(branch_short_list.Branch, branch_short_list.District):
    if c2.checkbox(branch, value=pre_select):
        district_list.append(district)
        branch_list.append(branch)
district_list = list(set(district_list))
district_shorter_list = state_short_data[state_short_data.District.isin(district_list)]
c3.header("Districts covered")
c3_data = branch_short_list[branch_short_list.Branch.isin(branch_list)]
if len(c3_data):
    c3.write(c3_data)
st.markdown("---")
st.markdown("<h2 style='text-align: center; color: #39A275;'>Analysis</h2>",
            unsafe_allow_html=True)
