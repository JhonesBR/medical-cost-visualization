from os.path import dirname, join

import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure

import dask.dataframe as dd

filepath = join(dirname(__file__), 'insurance_clean.csv')
ddf = dd.read_csv(filepath)

# ---------- Input Controls ----------
axis_map = {
    "Age": "age",
    "BMI": "bmi",
    "Number of dependent children": "children",
    "Region": "region",
}
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Age")

highlight_map = {
    "Smoker": "smoker",
    "Sex": "sex",
}
highlight = Select(title="Highlight", options=[
                   'Smoker', 'Sex'], value="Smoker")
# ------------------------------------

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[]))

TOOLTIPS = [
    ("Title", "@title"),
    ("Year", "@year"),
    ("$", "@revenue")
]

p = figure(height=600, width=700, title="",
           toolbar_location=None, sizing_mode="scale_both")


def select_figure():
    computed = ddf.groupby(
        axis_map[x_axis.value]).mean().compute().reset_index()
    df = pd.DataFrame()
    df[axis_map[x_axis.value]] = computed[axis_map[x_axis.value]]
    df['charges'] = computed['charges']
    df['alpha'] = computed[highlight_map[highlight.value]]

    if highlight_map[highlight.value] == 'smoker':
        df['color'] = 'red'
    else:
        df['color'] = 'blue'
    return df


def update():
    df = select_figure()
    y_name = 'charges'
    x_name = axis_map[x_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = 'Charges'
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df['color'],
        alpha=df['alpha']
    )

    p.renderers = []
    if x_name == 'age' or x_name == 'children':
        p.vbar(x="x", top="y", fill_color='color',
               fill_alpha='alpha', source=source, width=1)
    else:
        p.circle(x="x", y="y", fill_alpha='alpha', fill_color='color',
                 source=source, size=7, line_color=None)


controls = [x_axis, highlight]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320)

root = row(inputs, p)

update()  # initial load of the data

curdoc().add_root(root)
curdoc().title = "Medical Cost"
