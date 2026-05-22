import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_csv(filename: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / filename, **kwargs)


@st.cache_data
def load_excel(filename: str, sheet_name=0, **kwargs) -> pd.DataFrame:
    return pd.read_excel(DATA_DIR / filename, sheet_name=sheet_name, **kwargs)
