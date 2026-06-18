import pandas as pd
from fastapi import FastAPI, HTTPException, Query
import gzip
import json
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Val-de-Marne Real Estate Comparator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"
CADASTRE_FILE = DATA_DIR / "cadastre_94_val_de_marne.geojson.gz"
DVF_FILE = DATA_DIR / "dvf.csv"


# Global caches to avoid reading files repeatedly
_cadastre_data = None
_dvf_df = None


def load_cadastre():
    """Load and return the cadastre GeoJSON data (cached)."""
    global _cadastre_data
    if _cadastre_data is not None:
        return _cadastre_data
    with gzip.open(CADASTRE_FILE, "rt", encoding="utf-8") as f:
        _cadastre_data = json.load(f)
    return _cadastre_data


def load_dvf() -> pd.DataFrame:
    """Load DVF data, filter for department 94, and clean numeric columns (cached).

    Returns a DataFrame with only valid sales (Nature mutation == 'Vente',
    Valeur fonciere > 0, Surface reelle bati > 0).
    """
    global _dvf_df
    if _dvf_df is not None:
        return _dvf_df

    if not DVF_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail=f"DVF data file not found at {DVF_FILE.name}. "
                   "Please download it and place it in backend/data/."
        )

    df = pd.read_csv(DVF_FILE, sep="|", low_memory=False)

    # Keep only department 94
    df = df[df["Code departement"].astype(str) == "94"].copy()

    # Clean "Valeur fonciere": French decimal format uses comma
    df["Valeur fonciere"] = (
        df["Valeur fonciere"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    df["Valeur fonciere"] = pd.to_numeric(df["Valeur fonciere"], errors="coerce")

    # Clean "Surface reelle bati"
    df["Surface reelle bati"] = pd.to_numeric(df["Surface reelle bati"], errors="coerce")

    # Filter: only actual sales with valid price and surface
    df = df[
        (df["Nature mutation"] == "Vente")
        & (df["Valeur fonciere"].notna())
        & (df["Valeur fonciere"] > 0)
        & (df["Surface reelle bati"].notna())
        & (df["Surface reelle bati"] > 0)
    ]

    _dvf_df = df
    return _dvf_df


def normalize_commune_code(raw_code: int) -> int:
    """Accept both cadastre-style (94046) and DVF-style (46) commune codes.

    If the code has 5 digits and starts with 94, strip the department prefix.
    Otherwise, return as-is.
    """
    code_str = str(raw_code)
    if len(code_str) == 5 and code_str.startswith("94"):
        return int(code_str[2:])  # 94046 -> 46
    return raw_code


def compute_commune_stats(df: pd.DataFrame, raw_code: int) -> dict:
    """Compute statistics for a single commune from an already-cleaned DataFrame.

    Accepts both cadastre codes (94046) and DVF codes (46).
    """
    dvf_code = normalize_commune_code(raw_code)
    commune_df = df[df["Code commune"] == dvf_code]

    if commune_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No valid transactions found for commune code {raw_code} "
                   "in department 94."
        )

    commune_name = commune_df["Commune"].mode().iloc[0]  # most frequent name
    cadastre_code = int(f"94{dvf_code:03d}")  # 46 -> 94046

    avg_price = commune_df["Valeur fonciere"].mean()
    median_price = commune_df["Valeur fonciere"].median()
    avg_surface = commune_df["Surface reelle bati"].mean()
    avg_price_per_sqm = avg_price / avg_surface if avg_surface > 0 else None

    return {
        "cadastre_code": cadastre_code,
        "dvf_commune_code": dvf_code,
        "commune_name": commune_name,
        "transaction_count": int(len(commune_df)),
        "average_price": round(float(avg_price), 2),
        "median_price": round(float(median_price), 2),
        "average_surface": round(float(avg_surface), 2),
        "average_price_per_sqm": round(float(avg_price_per_sqm), 2) if avg_price_per_sqm else None,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {"message": "API is running"}


@app.get("/cadastre-info")
def cadastre_info():
    data = load_cadastre()
    return {
        "type": data["type"],
        "features_count": len(data["features"]),
    }


@app.get("/communes")
def get_communes():
    # Load DVF to extract names mapping
    df = load_dvf()
    
    # Filter unique (Code commune -> Commune name)
    df_clean = df[df["Commune"].notna() & (df["Commune"] != "")]
    # Create code to name map (taking mode name per code)
    name_map = {}
    for code, group in df_clean.groupby("Code commune"):
        if not group.empty:
            name_map[int(code)] = str(group["Commune"].mode().iloc[0])

    # Load cadastre codes
    data = load_cadastre()
    cadastre_codes = set(feature["properties"]["commune"] for feature in data["features"])

    result = []
    for code_str in cadastre_codes:
        try:
            code_int = int(code_str)
            dvf_code = normalize_commune_code(code_int)
            name = name_map.get(dvf_code, f"Commune {code_str}")
            result.append({
                "code": code_str,
                "name": name.strip().upper()
            })
        except ValueError:
            continue

    # Sort by name alphabetically
    result.sort(key=lambda x: x["name"])

    return {
        "count": len(result),
        "communes": result,
    }


@app.get("/dvf-info")
def dvf_info():
    if not DVF_FILE.exists():
        raise HTTPException(status_code=503, detail="DVF file not found.")
    df = pd.read_csv(DVF_FILE, sep="|", nrows=5)
    return {
        "columns": list(df.columns),
        "sample_rows": len(df),
    }


@app.get("/dvf-stats")
def dvf_stats():
    df = load_dvf()
    return {
        "val_de_marne_rows": len(df),
        "communes_count": int(df["Code commune"].nunique()),
    }


@app.get("/stats/{commune_code}")
def commune_stats(commune_code: int):
    """Return price / surface statistics for a single commune in department 94.

    Accepts both formats: cadastre code (94046) or DVF code (46).
    """
    df = load_dvf()
    return compute_commune_stats(df, commune_code)


@app.get("/compare")
def compare_communes(
    left: int = Query(..., description="Commune code, either 94046 or 46"),
    right: int = Query(..., description="Commune code, either 94046 or 46"),
):
    """Compare two communes on price / surface statistics.

    Returns stats for both communes plus a `winner` object indicating which
    commune has the lower average price per square meter.
    """
    df = load_dvf()

    left_stats = compute_commune_stats(df, left)
    right_stats = compute_commune_stats(df, right)

    # Determine winner (lower avg price/m²)
    left_ppsm = left_stats["average_price_per_sqm"]
    right_ppsm = right_stats["average_price_per_sqm"]

    if left_ppsm is not None and right_ppsm is not None:
        if left_ppsm < right_ppsm:
            winner = {
                "cadastre_code": left_stats["cadastre_code"],
                "dvf_commune_code": left_stats["dvf_commune_code"],
                "commune_name": left_stats["commune_name"],
                "average_price_per_sqm": left_ppsm,
            }
        else:
            winner = {
                "cadastre_code": right_stats["cadastre_code"],
                "dvf_commune_code": right_stats["dvf_commune_code"],
                "commune_name": right_stats["commune_name"],
                "average_price_per_sqm": right_ppsm,
            }
    else:
        winner = None

    return {
        "left": left_stats,
        "right": right_stats,
        "winner": winner,
    }