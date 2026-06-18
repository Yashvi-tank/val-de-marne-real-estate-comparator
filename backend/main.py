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


@app.get("/cadastre-info")
def cadastre_info():
    with gzip.open(CADASTRE_FILE, "rt", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "type": data["type"],
        "features_count": len(data["features"])
    }