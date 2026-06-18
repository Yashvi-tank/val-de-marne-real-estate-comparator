import pandas as pd
from pathlib import Path
import sys

def main():
    # Resolve paths
    backend_dir = Path(__file__).parent
    data_dir = backend_dir / "data"
    dvf_file = data_dir / "dvf.csv"
    output_file = data_dir / "commune_stats.csv"

    print(f"Reading DVF data from {dvf_file}...")
    if not dvf_file.exists():
        print(f"Error: {dvf_file} not found.")
        sys.exit(1)

    df = pd.read_csv(dvf_file, sep="|", low_memory=False)
    print(f"Loaded {len(df)} total rows.")

    # Keep only department 94
    print("Filtering for department 94...")
    df = df[df["Code departement"].astype(str) == "94"].copy()
    print(f"Found {len(df)} rows for department 94.")

    # Clean numeric columns
    df["Valeur fonciere"] = (
        df["Valeur fonciere"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    df["Valeur fonciere"] = pd.to_numeric(df["Valeur fonciere"], errors="coerce")
    df["Surface reelle bati"] = pd.to_numeric(df["Surface reelle bati"], errors="coerce")

    # Filter mutation Vente and non-null values
    df = df[
        (df["Nature mutation"] == "Vente")
        & (df["Valeur fonciere"].notna())
        & (df["Surface reelle bati"].notna())
    ]
    print(f"Filtered to actual sales with valid fields: {len(df)} rows.")

    # Apply outlier limits
    print("Applying outlier filters...")
    df = df[(df["Surface reelle bati"] >= 10) & (df["Surface reelle bati"] <= 500)]
    df = df[(df["Valeur fonciere"] >= 20000) & (df["Valeur fonciere"] <= 5000000)]
    
    # Calculate price per sqm to filter on it
    df["price_per_sqm_temp"] = df["Valeur fonciere"] / df["Surface reelle bati"]
    df = df[(df["price_per_sqm_temp"] >= 1000) & (df["price_per_sqm_temp"] <= 20000)]
    df = df.drop(columns=["price_per_sqm_temp"])
    
    print(f"Rows remaining after outlier filtering: {len(df)}.")

    # Group by Code commune
    print("Computing statistics grouped by commune...")
    stats_rows = []
    
    for code, group in df.groupby("Code commune"):
        dvf_commune_code = int(code)
        cadastre_code = int(f"94{dvf_commune_code:03d}")
        
        # Determine the most frequent commune name
        commune_name = str(group["Commune"].mode().iloc[0]).strip().upper() if not group.empty else ""
        
        transaction_count = len(group)
        avg_price = float(group["Valeur fonciere"].mean())
        median_price = float(group["Valeur fonciere"].median())
        avg_surface = float(group["Surface reelle bati"].mean())
        
        # Calculate price per sqm (avg_price / avg_surface)
        avg_price_per_sqm = avg_price / avg_surface if avg_surface > 0 else 0.0
        
        stats_rows.append({
            "cadastre_code": cadastre_code,
            "dvf_commune_code": dvf_commune_code,
            "commune_name": commune_name,
            "transaction_count": transaction_count,
            "average_price": round(avg_price, 2),
            "median_price": round(median_price, 2),
            "average_surface": round(avg_surface, 2),
            "average_price_per_sqm": round(avg_price_per_sqm, 2)
        })

    # Save to CSV
    stats_df = pd.DataFrame(stats_rows)
    # Sort by commune_name
    stats_df = stats_df.sort_values(by="commune_name")
    stats_df.to_csv(output_file, index=False, sep=",")
    print(f"Successfully generated precomputed statistics for {len(stats_df)} communes at {output_file}.")

if __name__ == "__main__":
    main()
