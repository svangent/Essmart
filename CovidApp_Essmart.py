import pandas as pd
import streamlit as st
from PIL import Image

BranchData_URL = 'https://raw.githubusercontent.com/hazeyblu/Essmart/main/BranchDetails.csv'
CovidData_URL = 'https://api.covid19india.org/csv/latest/districts.csv'

logo = Image.open('3Circles.png').resize((90, 30))
st.set_page_config(page_title='ESSMART vs Covid', initial_sidebar_state='collapsed',
                   page_icon=logo,
                   layout='wide')
col1, col2, col3 = st.beta_columns((1, 3, 1))
col1.image(logo)
col2.markdown("<h1 style='text-align: center; color: #39A275;'>Essmart Covid Tracker</h1>",
              unsafe_allow_html=True)
col3.empty()


@st.cache(show_spinner=False, persist=True)
def data_wrangle(dataset):
    """

    Main part of analysis where trends are studied

    :param dataset: mutated dataset consisting of data only for interested districts
    :return: modified dataset with rolling average calculation
    """
    rolling_windows = [7, 14, 21, 28]
    output_dataframe = pd.DataFrame()
    for districts in dataset.District.unique():
        sub_set = dataset[dataset['District'] == districts]
        sub_set["NewCases"] = sub_set.Confirmed - sub_set.Confirmed.shift(1)
        for window in rolling_windows:
            sub_set[f"{window}D"] = sub_set.NewCases.rolling(window).mean()
        output_dataframe = pd.concat([output_dataframe, sub_set])
    output_dataframe.reset_index(drop=True, inplace=True)
    return output_dataframe


@st.cache(show_spinner=False, persist=True)
def load_data(branch_data=False, districts_list=None):
    """

    Fetching and loading required data, serves dual purpose to utilize caching

    :param branch_data: list of Essmart branches and respective districts
    :param districts_list: list of districts to serve as filter from main dataset
    :return: varies based on function call
    """
    if districts_list is None:
        districts_list = ['']
    if branch_data:
        br_details = pd.read_csv(BranchData_URL)
        in_districts = br_details.District.unique()
        return br_details, in_districts
    else:
        data = pd.read_csv(CovidData_URL)
        needed_data = data[data['District'].isin(districts_list)]
        needed_data = data_wrangle(needed_data)
        print(needed_data.columns)
        return needed_data


def extract_info(dataset):
    c, r, d, t = 0, 0, 0, 0
    for districts in dataset.District.unique():
        sub_set = dataset[dataset['District'] == districts]
        c += sub_set.Confirmed.iloc[-1]
        r += sub_set.Recovered.iloc[-1]
        d += sub_set.Deceased.iloc[-1]
        t += sub_set.Tested.iloc[-1]
    return c, r, d, t


def main_layout():
    branch_details, interested_districts = load_data(branch_data=True)

    truncated_data = load_data(districts_list=interested_districts)

    c1, c2, c3, c4 = st.beta_columns((1, 1, 1, 1))

    # """
    # -----------------------
    # Main Layout Column 1
    # -----------------------
    # """
    c1.markdown("<h3 style='text-align: center; color: #39A275;'>State Level Information</h3>",
                unsafe_allow_html=True)
    selected_state = c1.selectbox("State level information:", ('Karnataka', 'Andhra Pradesh', 'Tamil Nadu'))
    radio_input = c1.radio(label='Branch Select Default:',
                           options=('All', 'None'),
                           index=1,
                           help="Choose if you would like all branches to be selected by default or not")
    if radio_input == 'All':
        pre_select = True
    else:
        pre_select = False
    state_short_data = truncated_data[truncated_data.State == selected_state]
    district_short_list = state_short_data.District.unique()
    branch_short_list = branch_details[branch_details.District.isin(district_short_list)]

    # """
    # -----------------------
    # Main Layout Column 2
    # -----------------------
    # """
    c2.markdown("<h3 style='text-align: center; color: #39A275;'>Essmart branches:</h3>",
                unsafe_allow_html=True)
    district_list = []
    branch_list = []
    for branch, district in zip(branch_short_list.Branch, branch_short_list.District):
        if c2.checkbox(branch, value=pre_select):
            district_list.append(district)
            branch_list.append(branch)
    district_list = list(set(district_list))
    district_shorter_list = state_short_data[state_short_data.District.isin(district_list)]
    c, r, d, t = extract_info(district_shorter_list)

    # """
    # -----------------------
    # Main Layout Column 3
    # -----------------------
    # """
    c3.markdown("<h3 style='text-align: center; color: #39A275;'>Districts covered</h3>",
                unsafe_allow_html=True)
    c3_data = branch_short_list[branch_short_list.Branch.isin(branch_list)]
    if len(c3_data):
        c3.table(c3_data)

    # """
    # -----------------------
    # Main Layout Column 4
    # -----------------------
    # """
    c4.markdown("<h3 style='text-align: center; color: #39A275;'>Combined Statistics</h3>",
                unsafe_allow_html=True)
    table_data = pd.DataFrame([["Confirmed", c], ["Recovered", r], ["Deceased", d], ["Tested", t]])
    table_data.columns = [['Item', 'Total']]
    if len(c3_data):
        c4.table(table_data)
        c4.markdown("<h6 style='text-align: right; color: #39A275;"
                    "'><strong>Note:</strong> total reported numbers since first case</h6>",
                    unsafe_allow_html=True)


def analysis_layout():
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #39A275;'>Analysis</h2>",
                unsafe_allow_html=True)


main_layout()
# analysis_layout()
