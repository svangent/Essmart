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


def extract_detailed_info(dataset, district):
    shortened_dataset = pd.DataFrame()
    for districts in dataset.District.unique():
        sub_set = dataset[dataset['District'] == districts]
        sub_set = sub_set.iloc[-30::]
        shortened_dataset = pd.concat([shortened_dataset, sub_set])
    shortened_dataset.reset_index(drop=True, inplace=True)

    district_metrics = shortened_dataset[shortened_dataset['District'] == district]
    d7 = district_metrics['7D'].iloc[-1]
    d14 = district_metrics['14D'].iloc[-1]
    d21 = district_metrics['21D'].iloc[-1]
    d28 = district_metrics['28D'].iloc[-1]
    return d7, d14, d21, d28, district_metrics


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
    district_list = sorted(list(set(district_list)))
    district_shorter_data = state_short_data[state_short_data.District.isin(district_list)]
    c, r, d, t = extract_info(district_shorter_data)
    analysis_layout(district_shorter_data, district_list)

    # """
    # -----------------------
    # Main Layout Column 3
    # -----------------------
    # """
    c3.empty()
    if len(branch_list):
        c3.markdown("<h3 style='text-align: center; color: #39A275;'>Districts covered</h3>",
                    unsafe_allow_html=True)
        c3_data = branch_short_list[branch_short_list.Branch.isin(branch_list)]
        c3.table(c3_data)

    # """
    # -----------------------
    # Main Layout Column 4
    # -----------------------
    # """
    c4.empty()
    if len(branch_list):
        c4.markdown("<h3 style='text-align: center; color: #39A275;'>Combined Statistics</h3>",
                    unsafe_allow_html=True)
        table_data = pd.DataFrame([["Confirmed", c], ["Recovered", r], ["Deceased", d], ["Tested", t]])
        table_data.columns = [['Item', 'Total']]
        c4.table(table_data)
        c4.caption("*Reported Numbers since March 2020")


def analysis_layout(district_shorter_data, district_list):
    st.markdown("---")
    if district_list:
        st.markdown("<h2 style='text-align: center; color: #39A275;'><Strong>Analysis</Strong></h2>",
                    unsafe_allow_html=True)
        c1, c2, c3 = st.beta_columns((1, 3, 1))
        # """
        # -----------------------
        # Analysis Layout Column 1
        # -----------------------
        # """
        c1.markdown("<h3 style='text-align: center; color: #39A275;'>District Selection</h3>",
                    unsafe_allow_html=True)
        district_detailed = c1.radio(label="Deep Dive", options=district_list, index=0,
                                     help="Select district (refer to branch details above) to see historical details")
        windows = [7, 14, 21, 28]
        columns = []
        c1.markdown("<h4 style='text-align: center; color: #39A275;'>Average New Cases for Graph</h4>",
                    unsafe_allow_html=True)
        for window in windows:
            if c1.checkbox(f'{window} days', True):
                columns.append(f'{window}D')
        d7, d14, d21, d28, metrics = extract_detailed_info(district_shorter_data, district_detailed)
        # """
        # -----------------------
        # Analysis Layout Column 2
        # -----------------------
        # """
        c2.markdown("<h3 style='text-align: center; color: #39A275;'>Historical Graph</h3>",
                    unsafe_allow_html=True)
        days = 20
        metrics = metrics.iloc[-days::]
        metrics = metrics[columns]
        c2.line_chart(metrics, use_container_width=True)
        days = c2.slider(label="Days", min_value=1, max_value=30, value=20)
        crossovers_truth = ['🔴', '🔴', '🔴', '🔴', '🔴', '🔴']

        labels = ['7 Day', '14 Day', '21 Day', '28 Day']
        values = [d7, d14, d21, d28]

        significance_count = 0
        if d7 < d14:
            crossovers_truth[0] = '🟢'
            significance_count += 0.2
        if d7 < d21:
            crossovers_truth[1] = '🟢'
            significance_count += 0.2
        if d7 < d28:
            crossovers_truth[2] = '🟢'
            significance_count += 0.3
        if d14 < d21:
            crossovers_truth[3] = '🟢'
            significance_count += 0.3
        if d14 < d28:
            crossovers_truth[4] = '🟢'
            significance_count += 0.5
        if d21 < d28:
            crossovers_truth[5] = '🟢'
            significance_count += 1

        expander = c2.beta_expander(label="Crossover Event Checks")
        explanation = ["7 Day Average Crosses 14 Day Average, signalling short term improvement",
                       "7 Day Average Crosses 21 Day Average, signalling short term improvement",
                       "7 Day Average Crosses 28 Day Average, signalling short term improvement",
                       "14 Day Average Crosses 21 Day Average, signalling medium term improvement",
                       "14 Day Average Crosses 28 Day Average, signalling medium term improvement",
                       "21 Day Average Crosses 28 Day Average, signalling long term improvement"]
        explanation_data = pd.DataFrame(columns=['Description', 'Status'])
        explanation_data['Description'] = explanation
        explanation_data['Status'] = crossovers_truth
        expander.table(explanation_data)
        # """
        # -----------------------
        # Analysis Layout Column 3
        # -----------------------
        # """
        c3.markdown("<h3 style='text-align: center; color: #39A275;'>Current Condition</h3>",
                    unsafe_allow_html=True)

        if significance_count < 1.5:
            c3.markdown("<h1 style='text-align: center;'>🔴</h1>",
                        unsafe_allow_html=True)
        elif significance_count <= 2.1:
            c3.markdown("<h1 style='text-align: center;'>🌕</h1>",
                        unsafe_allow_html=True)
        elif significance_count > 2.1:
            c3.markdown("<h1 style='text-align: center;'>🟢</h1>",
                        unsafe_allow_html=True)

        display_data = pd.DataFrame(values, index=labels, columns=['Average Cases'])
        display_data = round(display_data)
        c3.table(display_data)


main_layout()
