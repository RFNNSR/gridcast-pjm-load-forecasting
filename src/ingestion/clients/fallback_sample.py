from __future__ import annotations
import pandas as pd
from pathlib import Path

from ingestion.clients.base import LoadClient


DEFAULT_SAMPLE_PATH = Path(r"data\raw\pjm\sample\PJME_hourly.csv")
DATETIME_COL="Datetime"

class FallbackSampleClient(LoadClient):
    """Reads the local PJM sample file and returns rows in the window [start,end)"""
    
    def __init__(self, path :Path =DEFAULT_SAMPLE_PATH ):
        self.path = path
        
    def fetch(self, start_datetime_str: str, end_datetime_str:str) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"Sample file not found in {self.path}")
        df = pd.read_csv(self.path)
        if DATETIME_COL not in df.columns :
            raise ValueError(f"{DATETIME_COL} column cant be found")
        
            
        df[DATETIME_COL]= pd.to_datetime( df[DATETIME_COL], errors="coerce" )    
        df =df.sort_values(DATETIME_COL).reset_index(drop=True)
        start_datetime_dt =pd.to_datetime(  start_datetime_str)
        end_datetime_dt =pd.to_datetime(  end_datetime_str)
        mask_rule = (df[DATETIME_COL]>=start_datetime_dt) & (df[DATETIME_COL]<end_datetime_dt)
        return df.loc[mask_rule].copy()

if __name__ == "__main__":
    ...
    