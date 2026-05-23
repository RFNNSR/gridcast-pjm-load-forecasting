"""Ingestion client interface for hourly load data.

Clients fetch source data for a requested time window and return a DataFrame.
Time window semantics: [start, end) -> start inclusive, end exclusive."""

from typing import Protocol,runtime_checkable

import pandas as pd


class LoadClient ( Protocol):
   
    def fetch(self, start: str, end: str) -> pd.DataFrame:
        """Fetch records in time window [start,end) and returns at DataFrame format"""
        
        ...
