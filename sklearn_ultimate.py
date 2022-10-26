# Models and splitting
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

# Metrics
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import median_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import max_error
from sklearn.metrics import mean_absolute_percentage_error

import pandas as pd

def sklearn_models_ultimate(x, y):
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Create dataframe
    df = pd.DataFrame(columns=[
        'Model',
        'Mean Squared Error',
        'R2 Score',
        'Mean Absolute Error',
        'Mean Absolute Percentage ErrorE',
        'Median Absolute Error',
        'Explained Variance Score',
        'Max error'
    ])

    model_names = [
        'Linear Regression',
        'Decision Tree',
        'Random Forest',
        'Gradient Boosting',
        'Support Vector Machine',
        'K Neighbors'
    ]

    models = [
        LinearRegression(),
        DecisionTreeRegressor(),
        RandomForestRegressor(),
        GradientBoostingRegressor(),
        SVR(),
        KNeighborsRegressor()
    ]

    for model in models:
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        df.loc[len(df)] = get_metrics(model_names[models.index(model)], y_test, y_pred)

    print(f'Best Mean Squared Error: {df.loc[df["Mean Squared Error"].idxmin()]["Model"]}')
    print(f'Best R2 Score: {df.loc[df["R2 Score"].idxmax()]["Model"]}')
    print(f'Best Mean Absolute Error: {df.loc[df["Mean Absolute Error"].idxmin()]["Model"]}')
    print(f'Best Mean Absolute Percentage Error: {df.loc[df["Mean Absolute Percentage ErrorE"].idxmin()]["Model"]}')
    print(f'Best Median Absolute Error: {df.loc[df["Median Absolute Error"].idxmin()]["Model"]}')
    print(f'Best Explained Variance Score: {df.loc[df["Explained Variance Score"].idxmax()]["Model"]}')
    print(f'Best Max error: {df.loc[df["Max error"].idxmin()]["Model"]}')

    return {model_names[i]:models[i] for i in range(len(models))}, df



def get_metrics(model, y_test, y_pred):
    model_mse = mean_squared_error(y_test, y_pred)
    model_r2 = r2_score(y_test, y_pred)
    model_mae = mean_absolute_error(y_test, y_pred)
    model_mape = mean_absolute_percentage_error(y_test, y_pred)
    model_mde = median_absolute_error(y_test, y_pred)
    model_ev = explained_variance_score(y_test, y_pred)
    model_me = max_error(y_test, y_pred)
    return [model, model_mse, model_r2, model_mae, model_mape, model_mde, model_ev, model_me]

    
