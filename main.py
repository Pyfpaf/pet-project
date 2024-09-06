import os
import dill
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
path = os.environ.get('PROJECT_PATH', '.')

model_path = Path(f'{path}/data/models')
files = [file for file in model_path.iterdir() if file.is_file() and file.suffix == '.pkl']
sorted_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
last_model_path = sorted_files[0]

with open(last_model_path, 'rb') as file:
    object_to_load = dill.load(file)


class Form(BaseModel):
    factory: str
    model: str
    year: float
    city: str
    mileage: float


class Prediction(BaseModel):
    factory: str
    model: str
    year: float
    city: str
    mileage: float
    pred: float


@app.get('/status')
def status():
    return "FastAPI is Running"


@app.get('/version')
def version():
    return object_to_load['metadata']


@app.post('/predict', response_model=Prediction)
def predict(form: Form):
    df = pd.DataFrame.from_dict([form.dict()])
    y = object_to_load['model'].predict(df)

    return {
        'factory': form.factory,
        'model': form.model,
        'year': form.year,
        'city': form.city,
        'mileage': form.mileage,
        'pred': y[0]
    }