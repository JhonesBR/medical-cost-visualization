import pandas as pd

def get_prediction(model, age, sex, bmi, children, smoker):
    df = pd.DataFrame({
        'age': [age],
        'sex': [sex],
        'bmi': [bmi],
        'children': [children],
        'smoker': [smoker]
    })

    return pd.DataFrame({
        'charges': [model.predict(df)[0]],
        'x': ['Prediction']
    })