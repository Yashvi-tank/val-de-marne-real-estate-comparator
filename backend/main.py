import pandas as pd
from fastapi import FastAPI
import gzip
import json
from pathlib import Path

app = FastAPI()

DATA_DIR = Path(__file__).parent / "data"
CADASTRE_FILE = DATA_DIR / "cadastre_94_val_de_marne.geojson.gz"


@app.get("/")
def home():
    return {"message": "API is running"}


def load_cadastre():
    with gzip.open(CADASTRE_FILE, "rt", encoding="utf-8") as f:
        return json.load(f)


@app.get("/cadastre-info")
def cadastre_info():
    data = load_cadastre()

    return {
        "type": data["type"],
        "features_count": len(data["features"])
    }


@app.get("/communes")
def get_communes():
    data = load_cadastre()

    communes = sorted(
        set(feature["properties"]["commune"] for feature in data["features"])
    )

    return {
        "count": len(communes),
        "communes": communes
    }

DVF_FILE = DATA_DIR / "dvf.csv"


@app.get("/dvf-info")
def dvf_info():
    df = pd.read_csv(DVF_FILE, sep="|", nrows=5)

    return {
        "columns": list(df.columns),
        "sample_rows": len(df)
    }