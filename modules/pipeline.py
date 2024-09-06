import logging
import os
from datetime import datetime

import dill
import pandas as pd
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_absolute_error

# Укажем путь к файлам проекта:
# -> $PROJECT_PATH при запуске в Airflow
# -> иначе - текущая директория при локальном запуске
path = os.environ.get('PROJECT_PATH', '..')


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    def calculate_outliers(data):
        q25 = data.quantile(0.25)
        q75 = data.quantile(0.75)
        iqr = q75 - q25
        bounds = (q25 - 1.5 * iqr, q75 + 1.5 * iqr)
        return bounds

    df = df.copy()
    boundaries = calculate_outliers(df['mileage'])
    df.loc[df['mileage'] > boundaries[1], 'mileage'] = round(boundaries[1])
    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.model = df.model.apply(lambda x: x[:4])
    df['age'] = 2024 - df['year'] + 1
    df.drop('year', axis=1, inplace=True)
    return df


def pipeline() -> None:
    df_1 = pd.read_csv(f'{path}/parsers/data/alpha_data.csv')
    df_2 = pd.read_csv(f'{path}/parsers/data/europlan_data.csv')
    df_3 = pd.read_csv(f'{path}/parsers/data/gpbl_data.csv')
    df = pd.concat([df_1, df_2, df_3], ignore_index=True)

    X = df.drop('price', axis=1)
    y = df.price

    numerical_features = make_column_selector(dtype_include=['int64', 'float64'])
    categorical_features = make_column_selector(dtype_include=object)

    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', drop='first'))
    ])

    column_transformer = ColumnTransformer(transformers=[
        ('numerical', numerical_transformer, numerical_features),
        ('categorical', categorical_transformer, categorical_features)
    ])

    preprocessor = Pipeline(steps=[
        ('outlier_remover', FunctionTransformer(remove_outliers)),
        ('feature_creator', FunctionTransformer(create_features)),
        ('column_transformer', column_transformer)
    ])

    models = [
        Lasso(alpha=100),
        Ridge(alpha=10),
        RandomForestRegressor(n_estimators=150),
    ]

    best_score = 100000000.0
    best_pipe = None
    for model in models:

        pipe = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])

        score = cross_val_score(pipe, X, y, cv=5, scoring=make_scorer(mean_absolute_error), n_jobs=-1)
        logging.info(f'model: {type(model).__name__}, MAE_mean: {score.mean():.4f}, MAE_std: {score.std():.4f}')
        # print(f'model: {type(model).__name__}, MAE_mean: {score.mean():.4f}, MAE_std: {score.std():.4f}')
        if score.mean() < best_score:
            best_score = score.mean()
            best_pipe = pipe

    logging.info(f'best model: {type(best_pipe.named_steps["regressor"]).__name__}, MAE: {best_score:.4f}')
    # print(f'best model: {type(best_pipe.named_steps["classifier"]).__name__}, MAE: {best_score:.4f}')

    best_pipe.fit(X, y)
    model_filename = f'{path}/data/models/cars_pipe_{datetime.now().strftime("%Y%m%d%H%M")}.pkl'

    best_pipe.fit(X, y)
    with open(model_filename, 'wb') as file:
        dill.dump({
            'model': best_pipe,
            'metadata': {
                'name': 'Car price prediction model',
                'author': 'Alex Polyakov',
                'version': 1,
                'date': datetime.now(),
                'type': type(best_pipe.named_steps["regressor"]).__name__,
                'MAE': best_score
            }
        }, file)

    logging.info(f'Model is saved as {model_filename}')


def main() -> None:
    pipeline()


if __name__ == '__main__':
    main()
