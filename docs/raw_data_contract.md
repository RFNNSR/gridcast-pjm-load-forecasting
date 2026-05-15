# Raw data contract - PJM Hourly load (Draft)

## Status
Draft (created before sampling)

## Purpose
Define minimal expectation for the raw dataset so ingestion and downstream modeling remain

## Source 
- Provider: PJM
- Intended Feed: Hourly load (metered/actual)
- Access: PJM Data Miner API (API key not yet obtained)
- Temporary dev source: ( downloaded from kaggle)

## Expected grain (assumption)
- One record per hour (mostly!).  
  

## Timestamp policy (decision)
- Store timestamps/datetime[s] (timezone-aware?).

## Minimum required fields (assumptions)
- timestamp (datetime) 
- load_mw (numeric)    

## Raw data rules (project standard)
- Raw files are immutable once written.
- Any cleaning happens in processed/staging layers.