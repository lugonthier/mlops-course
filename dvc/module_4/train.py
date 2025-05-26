import yaml
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--train_data_path', type=str, required=True)
parser.add_argument('--model_output_path', type=str, required=True)

args = parser.parse_args()

with open('params.yaml', 'r') as f:
    params = yaml.safe_load(f)

os.makedirs(os.path.dirname(args.model_output_path), exist_ok=True)

train_df = pd.read_csv(args.train_data_path)

X_train = train_df.iloc[:, :-1]
y_train = train_df.iloc[:, -1]

model = RandomForestClassifier(
    n_estimators=params['train']['n_est'], 
    random_state=params['train']['seed']
)
model.fit(X_train, y_train)

with open(args.model_output_path, 'wb') as f:
    pickle.dump(model, f)