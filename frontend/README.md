# Frontend - Val-de-Marne Real Estate Comparator

This is the React/Vite frontend for the Val-de-Marne Real Estate Comparator.

It provides a modern interface for comparing real estate indicators between two communes in Val-de-Marne using data served by the FastAPI backend.

---

## Features

* Select two communes from Val-de-Marne
* Compare real estate indicators
* Display transaction count, average price, median price, average surface, and price per square meter
* Highlight the more affordable commune
* Responsive design for desktop and mobile
* Smooth, minimal UI with subtle animations

---

## Tech Stack

* React
* Vite
* JavaScript
* CSS
* Fetch API

---

## Environment Variable

Create a `.env` file inside the `frontend/` folder:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

For production, use the deployed backend URL:

```env
VITE_API_BASE_URL=https://val-de-marne-real-estate-api.onrender.com
```

---

## Local Development

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

---

## Build for Production

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

---

## Backend API Used

The frontend consumes these backend endpoints:

```http
GET /communes
GET /compare?left={communeCode}&right={communeCode}
```

Example:

```http
GET /compare?left=94046&right=94076
```

---

## Deployment

The frontend is deployed on Vercel.

During deployment, add this environment variable in Vercel:

```env
VITE_API_BASE_URL=https://val-de-marne-real-estate-api.onrender.com
```

Build settings:

```text
Framework: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

---

## Author

Yashvi TANK
