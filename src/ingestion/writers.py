
import pandas as pd
from pathlib import Path

import shutil
def write_partitioned_parquet(df: pd.DataFrame ,output_dir : Path, overwrite:bool = False) -> int:
    
    if df.shape[0]==0:
        return 0
    
    columns = ["timestamp_utc", "zone","load_mw"]
    missing_columns= [c for c in columns if c not in df.columns]
    if missing_columns :
        raise ValueError(f"need these columns {missing_columns}")
    out = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(out["timestamp_utc"]):
        raise ValueError(f"timestamp column is not datetime type")
    out["year"] = out["timestamp_utc"].dt.year
    out["month"] = out["timestamp_utc"].dt.month.astype(str).str.zfill(2)
    if overwrite:
        try:
            shutil.rmtree(path=str(output_dir))
        except FileNotFoundError:
            pass
    output_dir.mkdir(parents=True, exist_ok=True)
    
    out.to_parquet(output_dir,
                  partition_cols=["year","month"],
                  index=False

    )
    num_written_files= len(list(output_dir.rglob("*.parquet")))
    # num_written_files = out.drop_duplicates(["year","month"],keep="first",inplace=False).shape[0]
    return num_written_files