import os
import pandas as pd
from src.etl.ingest import load_csv
from src.etl.clean import clean_data
from src.etl.segment import segment_by_province_product
from src.persistence.file_store import save_parquet

def build_base_parquets(folder_path="src/data/raw"):
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    all_dfs = []

    for file in sorted(all_files):
        df = load_csv(os.path.join(folder_path, file))
        all_dfs.append(df)

    df_total = pd.concat(all_dfs, ignore_index=True)
    df_clean = clean_data(df_total)

    segments = segment_by_province_product(df_clean)

    for (provincia, producto), data in segments.items():
        base_path = f"src/data/segmented/{provincia}/{producto}/"
        save_parquet(data, base_path + "original.parquet")

    return True