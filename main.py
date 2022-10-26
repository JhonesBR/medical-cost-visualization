# ------------------------------------ Import Libraries -----------------------------------
from msilib import text
from bokeh.models import Button, ColumnDataSource, CheckboxGroup, Div, Label, Text, Select, Slider, Tabs, Panel
from bokeh.transform import linear_cmap
from bokeh.layouts import column, gridplot, row
from bokeh.palettes import RdBu
from bokeh.plotting import figure
from bokeh.io import curdoc
from os.path import dirname, join
from colour import Color
import dask.dataframe as dd
import pandas as pd
import pickle
from prediction import get_prediction
# -----------------------------------------------------------------------------------------


# --------------------------------------- Load Data ---------------------------------------
filepath = join(dirname(__file__), 'data/insurance_clean.csv')
ddf = dd.read_csv(filepath)
model = pickle.load(open(join(dirname(__file__), 'models/gradient_boosting.pkl'), 'rb'))
# -----------------------------------------------------------------------------------------


# ------------------------------------ Input Controls ------------------------------------
axis_map = {
    'Age': 'age',
    'BMI': 'bmi',
    'Number of dependent children': 'children',
}
x_axis = Select(title='X Axis', options=sorted(axis_map.keys()), value='Age')

highlight_map = {
    'None': 'none',
    'Smoker': 'smoker',
    'Sex': 'sex',
}
highlight = Select(title='Highlight', options=['None', 'Smoker', 'Sex'], value='None')

age_input = Slider(start=3, end=100, value=18, step=1, title='Age')
height_input = Slider(start=130, end=240, value=170, step=1, title='Height (cm)')
weight_input = Slider(start=30, end=240, value=65, step=1, title='Weight (kg)')
children_input = Slider(start=0, end=7, value=0, step=0, title='Number of dependent children')
sex_input = Select(title='Sex', options=['Male', 'Female'], value='Male')
smoker_input = CheckboxGroup(labels=['Smoker'], active=[])
calculate_button = Button(label='Calculate', button_type='success')
# -----------------------------------------------------------------------------------------


# ------------------------------------- Create Figure -------------------------------------
source = ColumnDataSource(data=dict(x=[], y=[]))
predict_source = ColumnDataSource(data=dict(x=[], y=[]))
TOOLTIPS = [
    ('Mean charges', '@y'),
    ('Mean age', '@mean_age'),
    ('Mean bmi', '@mean_bmi'),
    ('Mean number of dependent children', '@mean_children'),
    ('Highlight', '@highlight')
]
p = figure(height=450, width=620, title='', toolbar_location=None, tooltips=TOOLTIPS)
p.toolbar.active_drag = None

pred = figure(height=450, width=620, title='', toolbar_location=None, x_range=['Prediction'])
pred.axis.visible = False
pred.xgrid.grid_line_color = None
pred.ygrid.grid_line_color = None
pred.toolbar.active_drag = None
ghost_white = '#F8F8FF'
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
        custom_pallete = [c.hex for c in list(Color('green').range_to(Color('red'), 128))]
    elif highlight_map[highlight.value] == 'sex':
        custom_pallete = [c.hex for c in list(Color('pink').range_to(Color('blue'), 128))]
    else:
        custom_pallete = [c.hex for c in list(Color('blue').range_to(Color('red'), 128))]
    return linear_cmap(field_name='alpha', palette=custom_pallete, low=0, high=1)

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
        p.vbar(x='x', top='y', color=color_mapper, source=source, width=1, line_color=ghost_white)
    else:
        p.circle(x='x', y='y', color=color_mapper, source=source, size=7, line_color=ghost_white)

def predict():
    age = age_input.value
    sex = 1 if sex_input.value == 'Male' else 0
    bmi = weight_input.value / ((height_input.value/100)**2)
    children = children_input.value
    smoker = 1 if smoker_input.active else 0
    df = get_prediction(model, age, sex, bmi, children, smoker)
    predict_source.data = dict(
        x=df['x'],
        y=df['charges'],
    )

    pred.renderers = []

    pred.text(x=0, y=int(df['charges'][0]/2),
        text=[f"Predicted Charges: ${df['charges'][0]:.2f}"],
        text_color=ghost_white,
        text_font_size='20pt'
    )

# -----------------------------------------------------------------------------------------


# ----------------------------------------- Front -----------------------------------------
visualization_controls = [x_axis, highlight]
for control in visualization_controls:
    control.on_change('value', lambda attr, old, new: update())
inputs = column(*visualization_controls)
visualization = column(inputs, p, sizing_mode='scale_both')

calculate_button.on_click(lambda: predict())
prediction = gridplot([
        [age_input, height_input, weight_input],
        [children_input, sex_input, smoker_input],
        [Div(), calculate_button, Div()],
        [Div(), pred, Div()]
    ], sizing_mode='scale_width'
    , toolbar_location=None
)

tab1 = Panel(child=visualization, title='Data Visualization')
tab2 = Panel(child=prediction, title='Charges prediction')
root = Tabs(tabs=[tab1, tab2])

update()
curdoc().theme = 'dark_minimal'
curdoc().add_root(root)
curdoc().title = 'Medical Cost'
# -----------------------------------------------------------------------------------------