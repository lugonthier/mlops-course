import yaml
import pandas as pd
from sklearn.model_selection import train_test_split
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--raw_data_path', type=str, required=True)
parser.add_argument('--output_path', type=str, required=True)

args = parser.parse_args()

with open('params.yaml', 'r') as f:
    params = yaml.safe_load(f)

os.makedirs(args.output_path, exist_ok=True)

df = pd.read_csv(args.raw_data_path)

train_df, test_df = train_test_split(
    df, 
    test_size=params['prepare']['split'], 
    random_state=params['prepare']['seed']
)

train_df.to_csv(os.path.join(args.output_path, 'train.csv'), index=False)
test_df.to_csv(os.path.join(args.output_path, 'test.csv'), index=False)