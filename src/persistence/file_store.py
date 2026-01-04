import pandas as pd
import os

def save_parquet(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_parquet(path, index=False)

def save_metadata(metadata, path):
    import json
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(metadata, f, indent=4)