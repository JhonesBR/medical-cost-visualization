# ------------------------------------ Import Libraries -----------------------------------
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.transform import linear_cmap
from bokeh.layouts import column, row
from bokeh.palettes import RdBu
from bokeh.plotting import figure
from bokeh.io import curdoc
from os.path import dirname, join
from colour import Color
import dask.dataframe as dd
import pandas as pd
# -----------------------------------------------------------------------------------------


# --------------------------------------- Load Data ---------------------------------------
filepath = join(dirname(__file__), 'insurance_clean.csv')
ddf = dd.read_csv(filepath)
# -----------------------------------------------------------------------------------------


# ------------------------------------ Input Controls ------------------------------------
axis_map = {
    "Age": "age",
    "BMI": "bmi",
    "Number of dependent children": "children",
}
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Age")

highlight_map = {
    "None": "none",
    "Smoker": "smoker",
    "Sex": "sex",
}
highlight = Select(title="Highlight", options=['None', 'Smoker', 'Sex'], value="None")
# -----------------------------------------------------------------------------------------


# ------------------------------------- Create Figure -------------------------------------
source = ColumnDataSource(data=dict(x=[], y=[]))
TOOLTIPS = [
    ("Mean charges", "@y"),
    ("Mean age", "@mean_age"),
    ("Mean bmi", "@mean_bmi"),
    ("Mean number of dependent children", "@mean_children"),
    ("Highlight", "@highlight")
]
p = figure(height=450, width=620, title="", toolbar_location=None, tooltips=TOOLTIPS)
# -----------------------------------------------------------------------------------------


# --------------------------------------- Functions ---------------------------------------
def select_figure():
    # Group data
    computed = ddf.groupby(
        axis_map[x_axis.value]).mean().compute().reset_index()
    df = pd.DataFrame()
    df[axis_map[x_axis.value]] = computed[axis_map[x_axis.value]]
    df['charges'] = computed['charges']
    df['mean_age'] = computed['age']
    df['mean_bmi'] = computed['bmi']
    df['mean_children'] = computed['children']

    if highlight.value == 'None':
        length = len(df)
        df['alpha'] = [i/length for i in range(length)]
    else:
        df['alpha'] = computed[highlight_map[highlight.value]]

    if highlight_map[highlight.value] == 'smoker':
        df['highlight'] = df['alpha'].apply(
            lambda x: f'{(1-x)*100:.2f}% Non-Smoker' if x <= 0.5 else f'{x*100:.2f}% Smoker'
        )
    elif highlight_map[highlight.value] == 'sex':
        df['highlight'] = df['alpha'].apply(
            lambda x: f'{(1-x)*100:.2f}% Female' if x <= 0.5 else f'{x*100:.2f}% Male'
        )
    else:
        df['highlight'] = 'None'

    return df

def select_mapper():
    custom_pallete = []
    if highlight_map[highlight.value] == 'smoker':
        custom_pallete = [c.hex for c in list(Color("green").range_to(Color("red"), 128))]
    elif highlight_map[highlight.value] == 'sex':
        custom_pallete = [c.hex for c in list(Color("pink").range_to(Color("blue"), 128))]
    else:
        custom_pallete = [c.hex for c in list(Color("blue").range_to(Color("red"), 128))]
    return linear_cmap(field_name="alpha", palette=custom_pallete, low=0, high=1)

def update():
    df = select_figure()
    color_mapper = select_mapper()
    y_name = 'charges'
    x_name = axis_map[x_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = 'Charges'
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        alpha=df['alpha'],
        mean_bmi=df['mean_bmi'],
        mean_age=df['mean_age'],
        mean_children=df['mean_children'],
        highlight=df['highlight']
    )

    p.renderers = []
    if x_name == 'age' or x_name == 'children':
        p.vbar(x="x", top="y", color=color_mapper, source=source, width=1)
    else:
        p.circle(x="x", y="y", color=color_mapper, source=source, size=7, line_color=None)
# -----------------------------------------------------------------------------------------


# ----------------------------------------- Front -----------------------------------------
controls = [x_axis, highlight]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320)
root = column(inputs, p)

update() 
curdoc().add_root(root)
curdoc().title = "Medical Cost"
# -----------------------------------------------------------------------------------------