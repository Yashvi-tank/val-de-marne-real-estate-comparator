# Val-de-Marne Real Estate Comparator

Full-stack application to compare territories in Val-de-Marne using public French real estate transaction data.

## Stack

- Backend: Python, FastAPI, Pandas
- Frontend: React / Next.js
- Data:
  - Cadastre department 94
  - DVF real estate transactions

## Local setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload