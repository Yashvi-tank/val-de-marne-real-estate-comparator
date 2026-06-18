# Val-de-Marne Real Estate Comparator

A full-stack web application that compares real estate market indicators across communes in the Val-de-Marne department (94), using official French property transaction data (DVF).

## Live Demo

Frontend:
https://val-de-marne-real-estate-api.vercel.app/

Backend API:
https://val-de-marne-real-estate-api.onrender.com/

---

## Project Overview

This application allows users to compare two communes from Val-de-Marne and visualize key real estate indicators derived from official transaction records.

Users can:

* Select two communes
* Compare real estate market performance
* View transaction statistics
* Compare average and median property prices
* Compare average property surface areas
* Compare average price per square meter
* Identify the more affordable territory

---

## Data Sources

### DVF (Demandes de Valeurs Foncières)

Official French property transaction database published by the French government.

Used to extract:

* Property sale transactions
* Sale prices
* Property surfaces
* Commune information

### Cadastre 94

Official cadastral data for the Val-de-Marne department.

Used to:

* Identify and validate communes
* Map commune codes between datasets

---

## Architecture

### Frontend

* React
* Vite
* Modern responsive UI
* Fetch API

### Backend

* Python
* FastAPI
* Pandas

### Deployment

Frontend:

* Vercel

Backend:

* Render

---

## Design Decisions

### Why precomputed statistics?

The original DVF dataset contains millions of records and is too large to efficiently process on every API request.

Instead:

1. Raw DVF data is processed once locally.
2. Cleaning and outlier filtering are applied.
3. Commune-level statistics are generated.
4. A lightweight `commune_stats.csv` file is produced.
5. The deployed API serves data directly from this precomputed dataset.

Benefits:

* Faster response times
* Simpler deployment
* Lower memory usage
* Better scalability
* Cleaner architecture

---

## Data Cleaning

To improve indicator quality, the following filters were applied:

### Property Surface

Only transactions with:

* Surface ≥ 10 m²
* Surface ≤ 500 m²

### Property Value

Only transactions with:

* Value ≥ €20,000
* Value ≤ €5,000,000

### Price per Square Meter

Only transactions with:

* Price/m² ≥ €1,000
* Price/m² ≤ €20,000

### Transaction Type

Only:

* Vente (Sale)

transactions were included.

---

## API Endpoints

### Get Communes

GET

```http
/communes
```

Returns the list of available communes.

---

### Get Statistics

GET

```http
/stats/{commune_code}
```

Example:

```http
/stats/94046
```

Returns:

* Transaction count
* Average price
* Median price
* Average surface
* Average price per square meter

---

### Compare Two Communes

GET

```http
/compare?left=94046&right=94076
```

Returns:

* Statistics for both communes
* Most affordable commune based on average price per square meter

---

## Local Setup

### Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Project Structure

```text
real-estate-comparator-94/
│
├── backend/
│   ├── main.py
│   ├── generate_stats.py
│   ├── requirements.txt
│   └── data/
│       └── commune_stats.csv
│
├── frontend/
│
└── README.md
```

---

## Future Improvements

* Interactive map visualization
* Historical trend analysis
* Additional departments
* Advanced filtering
* Data export functionality
* Price evolution charts

---

## Author

Yashvi TANK

Created as part of a full-stack technical assessment focused on data processing, API design, deployment, and user experience.
