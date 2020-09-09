import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pypistats
import seaborn as sns

now_datetime = datetime.today()
min_starttime = now_datetime + relativedelta(months=-4)
start_date = st.sidebar.date_input('Select start date:', value=min_starttime, min_value=min_starttime, max_value=now_datetime)
end_date = st.sidebar.date_input('Select end date:', value=now_datetime, min_value=min_starttime, max_value=now_datetime)

#@st.cache
def get_weekly_downloads(package):
    try:
        data = pypistats.overall(package, total=False, format="pandas")
        results = data[data.category != 'Total']
        results['Date'] = pd.to_datetime(results['date'])
        results = pd.DataFrame(results.groupby(pd.Grouper(key='Date', freq='W-SUN'))['downloads'].sum().reset_index())
        results['Package'] = package
        return results
    except Exception as foo:
        st.write("Invalid package", package, foo)
        return pd.DataFrame()

st.header("PyPi - Package Download Comparison")
st.markdown('''
    This app uses the [PyPiStats Library](https://pypi.org/project/pypistats/) to get daily downloads for each package specified, sum the counts by week (starting on Sunday), and plot the results side by side.  

    Use the start and end dates in the sidebar to narrow the timeframe for results. Note that the library returns a maximum of 4 months (despite claiming 180 days), thus the date selectors are limited to that range.
''')


# get package list
package_list = st.text_input("Enter packages, comma separated", value="streamlit,dash,panel,gradio")

# Initialize download data
final_data = pd.DataFrame()

# Loop over package list and grab stats from PyPi
for package in (package_list.split(',')):
    package = package.strip()
    if package == "":
        continue
    results = get_weekly_downloads(package)
    if results.empty == False:
        final_data = pd.concat([final_data, results])

# Filter on user date range
mask = (final_data['Date'] >= pd.to_datetime(start_date)) & (final_data['Date'] <= pd.to_datetime(end_date))
final_data = final_data.loc[mask]

# Plot combined results
chart = sns.barplot(x='Date', y='downloads', hue='Package', data=final_data)
x_dates = final_data['Date'].dt.strftime('%Y-%m-%d')
chart.set_xticklabels(labels=final_data['Date'].dt.strftime('%Y-%m-%d'), rotation=90)
st.pyplot()

if (st.checkbox("Show Data", key='downloads')):
        st.write(final_data.sort_values('Date', ascending=False))
