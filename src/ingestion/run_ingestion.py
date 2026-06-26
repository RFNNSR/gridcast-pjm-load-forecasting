
import argparse
from pathlib import Path


import pandas as pd
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine import Engine

from ingestion.clients.fallback_sample import FallbackSampleClient
from ingestion.writers import write_partitioned_parquet
from ingestion.normalize import normalize_load

from enum import Enum

INPUT_PATH = Path(r"data/raw/pjm/sample/PJME_hourly.csv")
OUTPUT_PATH = Path("data/raw/pjm/dev_fallback")

class ColumnNames(Enum):
    DT_COL="Datetime"
    LOAD_COL="PJME_MW"
    ZONE_VALUE="PJME"
    SOURCE_TZ="America/New_York"
    
def make_engine(env_path: Path) -> Engine:
    postgres_config = dotenv_values(env_path)
    
    variables = ["POSTGRES_DB",
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_HOST",
                "POSTGRES_PORT"]
    missing_variables = [variable for variable in variables if not postgres_config.get(variable)]
    if missing_variables:
        raise ValueError(f"missing variables which required for .env are:{missing_variables}")
    db_url = (
        f"postgresql+psycopg2://{postgres_config['POSTGRES_USER']}:"
        f"{postgres_config['POSTGRES_PASSWORD']}@{postgres_config['POSTGRES_HOST']}:"
        f"{postgres_config['POSTGRES_PORT']}/{postgres_config['POSTGRES_DB']}"
    )
    engine= create_engine(db_url)
    
    return engine


def sql_executor(engine: Engine, sql_text:str,parameters:dict |None =None):
    """execute the query and returns a list [the error in exist, query output]"""
    with engine.begin() as conn:
        truncate_text = text(sql_text)
        query_return=conn.execute(truncate_text,parameters or {})
        
        return query_return

        
def main():
    #parse the arguments        
    parser=argparse.ArgumentParser()
    parser.add_argument("--start",required=True, type=pd.Timestamp)
    parser.add_argument("--end",required=True, type=pd.Timestamp)
    parser.add_argument("--overwrite",action="store_true")
    args = parser.parse_args()
    start = args.start
    end = args.end
    if start >= end:
        raise ValueError("--start must be earlier than --end")
    overwrite = args.overwrite
    env_path = Path(".env")
    engine = make_engine(env_path)



    #insert the first part of the log record
    insert_text="""
    --begin-sql
    insert into ops.ingestion_runs (
        source,
        feed,
        range_start,
        range_end,
        result_status)
        values(
            'dev_fallback',
            'PJME_hourly_sample',
            :start,
            :end,
            'running')
            
        
    returning run_id;
    
    
    """
    # insert_text ="insert into ops.ingestion_runs (source,feed, range_start, range_end, result_status) values('dev_fallback', 'PJME_hourly_sample', :start,:end,'running') returning run_id;"
    insert_text_parameters={"start":start,"end":end}
    run_uid= sql_executor(engine= engine , sql_text=insert_text,parameters=insert_text_parameters)
    run_uid = run_uid.scalar_one()

    #fetch the raw data
    
    fallbackSampleClient= FallbackSampleClient(INPUT_PATH)
    try:
        raw_df=fallbackSampleClient.fetch(str(start),str(end))
        num_row_fetched = raw_df.shape[0]

    #normalize the fetched data
        normalized_df = normalize_load(raw_df,
                                    dt_col=ColumnNames.DT_COL.value,
                                    load_col=ColumnNames.LOAD_COL.value,
                                    zone_value=ColumnNames.ZONE_VALUE.value,
                                    source_tz=ColumnNames.SOURCE_TZ.value)

    #write the normalized data
        

        num_written_file=write_partitioned_parquet(normalized_df,output_dir=OUTPUT_PATH,overwrite=overwrite)
        
        success_update_text = """
        --sql
         Update ops.ingestion_runs 
         set 
            finished_at = now(),
            rows_fetched = :num_row_fetched,
            files_written = :num_written_file,
            output_path=:output_path,
            result_status='success' 
        where run_id = :run_uid
        ;
        """ 
        update_parameters={"num_row_fetched":num_row_fetched,
                           "num_written_file":num_written_file,
                           "output_path":str(OUTPUT_PATH),
                           "run_uid":run_uid}
        query_output=sql_executor(engine=engine, sql_text=success_update_text,parameters=update_parameters)
        
    except Exception as e:
        failed_update_text = """
        --sql
        Update ops.ingestion_runs 
        set 
            finished_at = now(),
            result_status='failed', 
            error_message= :e 
        where run_id=:run_uid
        ;
        """
        update_parameters={"e":str(e),
                           "run_uid":run_uid}
        query_output=sql_executor(engine=engine , sql_text = failed_update_text,parameters=update_parameters)
        raise 
    print("Ingestion completed successfully.")
    print(f"run_id: {run_uid}")
    print(f"rows_fetched: {num_row_fetched}")
    print(f"files_written: {num_written_file}")
    print(f"output_path: {OUTPUT_PATH}")
if __name__ == "__main__":
    main()
    

