import pandas as pd
def normalize_load(df: pd.DataFrame, 
                   *,
                   dt_col:str,
                   load_col:str,
                   zone_value:str ,
                   source_tz:str | None,
                   ) -> pd.DataFrame:
    """
     This method normalize the data
     
     Out put schema:
     timestamp_utc: timezone aware timestamp in UTC time
     zone: region identifier
     load_mw: load data in mega watt (electricity)
     
     
     if the timestamp column already has the time zone the source_tz will be ignored.
    """ 
    
    if not dt_col in df.columns:
        raise ValueError(f" {dt_col} column can't be found ")
    if not load_col in df.columns :
        raise ValueError(f" {load_col} column can't be found ")
    out = df[[dt_col,load_col]].copy()
    out[dt_col] = pd.to_datetime(out[dt_col], errors="coerce")
    

    if out[dt_col].dt.tz is None and source_tz is None:
        raise ValueError(f" The TimeStamp column has no time zone so a time zone should be stated at source_tz parameter")
    if out[dt_col].dt.tz is None:
        out[dt_col]=out[dt_col].dt.tz_localize(source_tz, ambiguous="NaT", nonexistent="shift_forward")
    out=out.dropna(axis=0,subset=[dt_col])    
    out["timestamp_utc"] = out[dt_col].dt.tz_convert("UTC")
    out["load_mw"]= pd.to_numeric(out[load_col], errors="coerce")
    out= out.dropna(axis=0, subset= ["load_mw"])
    

    out["zone"]=zone_value

    
    out =out.sort_values("timestamp_utc").reset_index(drop=True)
    
    return out[["timestamp_utc","zone","load_mw"]]
    
if __name__== "__main__":
    ...
