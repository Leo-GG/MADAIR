import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
#import pymysql # st.connection doesn't work because it can't install mysqlclient 
#import toml

# Use wide layout
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Reading data
#toml_data = toml.load("secrets.toml")
# saving each credential into a variable
#HOST_NAME = toml_data['mysql']['host']
#DATABASE = toml_data['mysql']['database']
#PASSWORD = toml_data['mysql']['password']
#USER = toml_data['mysql']['user']
#PORT = toml_data['mysql']['port']


# Perform query.
## use pymysql instead of streamlit.connect
#connection_string = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST_NAME}:{PORT}/{DATABASE}'
#engine = create_engine(connection_string)

df = conn.query('SELECT * from AirData;', ttl=600)
#df=pd.read_sql(f"SELECT * FROM AirData", con=engine)
df_anomalies = conn.query('SELECT * from Outliers;', ttl=600)
#df_anomalies=pd.read_sql(f"SELECT * FROM Outliers", con=engine)

# Load Data
@st.cache_data
def load_data(file_path):
    return pd.read_parquet(file_path)

# Load data from the local file
#df = load_data(DATA_FILE_PATH)
#df_anomalies = load_data(ANOMALIES_FILE_PATH)

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])



# Sidebar for contaminant selection
st.sidebar.header('Select Contaminant')
contaminants = list(set(df.Contaminant.values))
selected_contaminant = st.sidebar.selectbox('Contaminant', contaminants,index=1)

# Calculate default date range
max_date = df['Date'].max()
min_date = df['Date'].min()
default_start_date = max_date - pd.DateOffset(years=1)

# Sidebar for date selection
st.sidebar.header('Select Date Range')
start_date = st.sidebar.date_input('Start Date', default_start_date,min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input('End Date', max_date,min_value=min_date, max_value=max_date)

# Sidebar for outlier display
st.sidebar.header('Display Outliers')
show_outliers = st.sidebar.radio('Show Outliers', ('No', 'Yes'))


## Display data quality stats
st.write(f"## Distribution of {selected_contaminant} outlier values (2001-2024)")
sel_anomalies=df_anomalies[df_anomalies.Contaminant==selected_contaminant].copy()

col_stats1, col_stats2 = st.columns([2,1])
with col_stats1:
    fig_outliers=px.bar(sel_anomalies,x='Year',y='Anomalies', color='Location')
    st.write(f"### Total outliers for {selected_contaminant} (2001-2024): {sel_anomalies.Anomalies.sum()}")
    fig_outliers.update_layout(yaxis_title=f'{selected_contaminant} outliers')
    st.plotly_chart(fig_outliers)

with col_stats2:
    # Pie chart of total anomalies per location
    outliers_per_location = sel_anomalies[['Location','Anomalies']].groupby('Location').sum().reset_index()
    outliers_pie = px.pie(outliers_per_location, names='Location', values='Anomalies', title='')
    st.write(f"### {selected_contaminant} outliers per Location (2001-2024)")
    #outliers_pie.update_traces(showlegend=False)
    st.plotly_chart(outliers_pie)

##    
# Display timeline of monitoring stations
st.write(f"## Monitoring stations activity period (2001-2024)")
timelines=df[['Location','Date']].groupby('Location').max().merge(df[['Location','Date']].groupby('Location').min(),left_index=True, right_index=True).reset_index().melt(id_vars='Location').drop(columns='variable').sort_values('value')
timeline_plot=px.line(timelines, x='value', y='Location',color='Location', height=600,color_discrete_sequence=px.colors.sequential.Reds)
timeline_plot.update(layout_showlegend=False)
timeline_plot.update_layout(xaxis_title=f'Year')
timeline_plot.update_traces(line=dict( width=6))
st.plotly_chart(timeline_plot)
  
    
# Filter data based on selected date range
filtered_df = df[(df.Contaminant==selected_contaminant) & (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
filtered_df = filtered_df.sort_values('Date')


# Remove outliers or keep them, based on the button status
if show_outliers=='Yes':
    st.write(f"## Raw {selected_contaminant} data from {start_date} to {end_date}")
else:
    st.write(f"## Filtered {selected_contaminant} data from {start_date} to {end_date}")
    filtered_df=filtered_df[filtered_df.Outlier==False].copy()
    
# Display the selected data
# Display summary statistics for the selected contaminant
st.write(f"### Summary Statistics")

if not filtered_df.empty:  
    # Compute summary statistics
    max_values = filtered_df[['Location','Value']].groupby('Location').max()#.reset_index()
    min_values = filtered_df[['Location','Value']].groupby('Location').min()#.reset_index()
    mean_values = filtered_df[['Location','Value']].groupby('Location').mean()#.reset_index()

    # Create columns for side-by-side display
    col1, col2, col3 = st.columns([1,1,1])
    
    with col1:
        st.write("**Maximum Values**")
        st.dataframe(max_values)

    with col2:
        st.write("**Minimum Values**")
        st.dataframe(min_values)
    
    with col3:
        st.write("**Average Values**")
        st.dataframe(mean_values)
        
    col_stats1,col_stats2=st.columns([1,2])
    with col_stats1:
        # Pie chart of total contaminant per location
        total_per_location = filtered_df[['Location','Value']].groupby('Location').sum().reset_index()
        pie_chart = px.pie(total_per_location, names='Location', values='Value', title='Total detected per location')
        #st.write(f"### Total {selected_contaminant} per Location")
        st.plotly_chart(pie_chart)
    with col_stats2:
        # Create boxplot using Plotly Express
        fig_box = px.box(filtered_df, x='Location', y='Value', points=None, color='Location', title='Distribution per location')
        fig_box.update_layout(yaxis_title=f'{selected_contaminant}')
        st.plotly_chart(fig_box)
        
else:
    st.write("No data available for the selected date range.")
    
    
    

# Exploratory Data Analysis (EDA) for the selected contaminant
st.write(f"### {selected_contaminant} charts")

if not filtered_df.empty:

    # Plot time series of the selected contaminant
    fig_ts = px.line(filtered_df, x='Date', y='Value', color='Location', title=f'{selected_contaminant} over Time')
    fig_ts.update_layout(xaxis_title='Date', yaxis_title=selected_contaminant)
    fig_ts.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig_ts.update_yaxes(showline=True, linewidth=1, linecolor='black')
    st.plotly_chart(fig_ts)

    # Histogram of the selected contaminant
    fig_hist = px.histogram(filtered_df, x='Value', nbins=30, title=f'Distribution of {selected_contaminant}')
    fig_hist.update_layout(xaxis_title=selected_contaminant, yaxis_title='Frequency')
    fig_hist.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig_hist.update_yaxes(showline=True, linewidth=1, linecolor='black')
    st.plotly_chart(fig_hist)
    
else:
    st.write("No data available for the selected date range.")
