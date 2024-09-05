import os
import dill
import json
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

path = os.environ.get('PROJECT_PATH', '.')


def predict() -> None:

    model_path = Path(f'{path}/data/models')
    files = [file for file in model_path.iterdir() if file.is_file() and file.suffix == '.pkl']
    sorted_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    last_model_path = sorted_files[0]

    with open(last_model_path, 'rb') as file_model:
        model = dill.load(file_model)

    logging.info(f'model file have read {last_model_path}')

    cars_id = []
    predictions = []
    for file_test in os.listdir(f'{path}/data/test'):
        with open(f'{path}/data/test/' + file_test, 'r') as test_file:
            predict_data = pd.json_normalize(json.load(test_file))
            prediction = model.predict(predict_data)
            cars_id.append(predict_data['id'].values[0])
            predictions.append(prediction[0])

    df_data = {'cars_id': cars_id, 'pred': predictions, 'model_file': last_model_path.name}
    df_predict = pd.DataFrame(df_data)
    predict_filename = f'{path}/data/predictions/preds_{datetime.now().strftime("%Y%m%d%H%M")}.csv'
    df_predict.to_csv(predict_filename, index=False)

    logging.info(f'Predicts is saved as {predict_filename}')

if __name__ == '__main__':
    predict()