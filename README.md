# UK Population Dashboard

An interactive web dashboard visualising UK population data, built with Python and served via Flask.

## Project Structure

```
uk-population-dashboard/
├── app.py
├── uk_population_dashboard.py
├── mye24tablesuk.xlsx
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/uk-population-dashboard.git
cd uk-population-dashboard
```

### 2. Create and activate a virtual environment
```bash
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```

### 5. Run the app
```bash
python app.py
```

Open your browser at **http://localhost:5000**

## Deploying to Render

1. Push this repository to GitHub
2. Go to [https://render.com](https://render.com) and sign in with GitHub
3. Click **New +** → **Web Service**
4. Connect this repository
5. Use these settings:

| Field | Value |
|-------|-------|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| Plan | Free |

6. Add environment variables:
   - `PORT` = `5000`
   - `PYTHON_VERSION` = `3.11.0`

7. Click **Create Web Service** — your app will be live in a few minutes.

## Data Source

Population data sourced from the ONS Mid-Year Estimates (`mye24tablesuk.xlsx`).

## Tech Stack

- **Python** — data processing
- **Pandas** — data manipulation
- **Flask** — web server
- **Gunicorn** — production WSGI server
- **Render** — cloud hosting
