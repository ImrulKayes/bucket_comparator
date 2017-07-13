# Import necessary packages
from bokeh.layouts import row, column
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Dropdown, DataTable, TableColumn, Div, PreText, Button
import pandas as pd
import numpy as np
import scipy.stats as stats
from os.path import dirname, join

# Set constants
apps_home = dirname(__file__)
apps_data_folder_name = 'data'
apps_data = apps_home + '/' + apps_data_folder_name
data_path = apps_data + '/' + 'data.csv'

# Read data as a dataframe
def read_data(data_path):
    df = pd.read_csv(data_path, sep=',', )
    return df

# Filter dataframe based on a section and return the dataframe
def get_selected_df(section):
    return df[df['section'] == section]

# Perform kruskal-wallis test and return test results
def get_test_result(df):
    test_result = stats.mstats.kruskalwallis(df['group_A'], df['group_B'])
    test_val = test_result.statistic
    p_val = test_result.pvalue
    conclusion = 'Buckets are statistically different' if p_val <= 0.05 else 'Buckets statistically same'
    return test_val, p_val, conclusion

# Update data of the count_source 
def update_count_plot(df_selected):
    count_source.data = dict(section_col=df_selected.section, bucket=df_selected.bucket, group_A=df_selected.group_A, group_B=df_selected.group_B)

# Stuffs we want to do if dropdown value changes
def selector_change(attrname, old, new):
 
    section = selector.value
    df_selected = get_selected_df(section)

    update_count_plot(df_selected)

    test_val, p_val, conclusion = get_test_result(df_selected)
    div.text = div_text.format(section, test_val, p_val, conclusion)
    table_pre_text.text = pre_text_text.format(section)

    percentile, group_A_percentiles, group_B_percentiles = get_percentiles(df_selected)

    data = dict(percentile=percentile, group_A_percentiles=group_A_percentiles, group_B_percentiles=group_B_percentiles)
    percentile_source.data = data


def get_percentiles(df):
    percentiles = ['Low (25%)', 'Medium (50%)', 'High (75%)']
    group_A_percentiles = [
        np.percentile(df['group_A'], 25),
        np.percentile(df['group_A'], 50),
        np.percentile(df['group_A'], 75)
    ]

    group_B_percentiles = [
        np.percentile(df['group_B'], 25),
        np.percentile(df['group_B'], 50),
        np.percentile(df['group_B'], 75)
    ]

    return percentiles, group_A_percentiles, group_B_percentiles

"""
""""""""""""""""""""""""""""""
Entry of main functionalities
""""""""""""""""""""""""""""""
"""

# Read data in a pandas dataframe
df = read_data(data_path)

# Get unique sections from the pandas dataframe
section_list = list(df.section.unique())

# Select a seed section
section = section_list[1]

# Filter the dataframe based on the section
df_selected = get_selected_df(section)

# Get percentiles of the dataframe
percentile, group_A_percentiles, group_B_percentiles = get_percentiles(df_selected)

# ColumnDataSource to be used in Table
percentile_source = ColumnDataSource(
    data=dict(percentile=percentile, group_A_percentiles=group_A_percentiles, group_B_percentiles=group_B_percentiles))

# Columns to be used in Table
columns = [
    TableColumn(field="percentile", title="Percentile"),
    TableColumn(field="group_A_percentiles", title="Group A"),
    TableColumn(field="group_B_percentiles", title="Group B")
]

# Create a data table
data_table = DataTable(source=percentile_source, columns=columns, width=400, height=280)

# Pre text for the data table
pre_text_text = """Percentiles of buckets for section: {0}"""
table_pre_text = PreText(text=pre_text_text.format(section), width=400, height=20)

# ColumnDataSource for the plot
count_source = ColumnDataSource(
    data=dict(section_col=df_selected.section, bucket=df_selected.bucket, group_A=df_selected.group_A, group_B=df_selected.group_B))

# Create the figure plot
count_Plot = figure(title="Count plot", tools="",
                    toolbar_location=None, plot_height=400, plot_width=800)

count_Plot.xaxis.axis_label = "Bucket number"
count_Plot.yaxis.axis_label = "Total count"

line_group_A = count_Plot.line('bucket', 'group_A', color='#A6CEE3', legend='Group A', source=count_source)
line_group_B = count_Plot.line('bucket', 'group_B', color='#B2DF8A', legend='Group B', source=count_source)

# Custom java script code will be exected to when Download data buttion will be clicked
code = open(join(dirname(__file__), "download_data.js")).read()
download_button = Button(label="Download data", button_type="success")
download_button.callback = CustomJS(args = dict(source=count_source),
                                    code = code)

# Create the selector for choosing sections
menu = [(x, x) for x in section_list]
selector = Dropdown(label="Select section", button_type="primary", menu=menu, width=350)

# On change in dropdown call selector_change function
selector.on_change('value', selector_change)

# Create div for stats on selected section
div_text = """
    <blockquote>
        <h4>Stats of the selected section</h4>
    </blockquote>

    <ul>
        <li>Selected section: {0}</li>
        <li>Kruskal Wallis test statistic: {1}</li>
        <li>Kruskal Wallis test p-value: {2}</li>
        <li>
            <b>Conclusion: {3}</b>
        </li>
    </ur>
"""

test_val, p_val, conclusion = get_test_result(df_selected)
div = Div(text=div_text.format(section, test_val, p_val, conclusion), width=400, height=100)

# Create the layout
slector_div_text_table = column(selector, div, table_pre_text, data_table)
plot_button = column(count_Plot, download_button)
layout = row(slector_div_text_table, plot_button)

# Add the layout to the doc
curdoc().add_root(layout)
curdoc().title = "Section count analysis"
