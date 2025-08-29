# EVE Echoes Planetary Mining Optimizer

A comprehensive web application for optimizing planetary mining operations in EVE Echoes.

## Features

- 🪐 **Planetary Resource Analysis** - Analyze resources across all systems, constellations, and regions
- 💰 **Price Management** - Import and manage custom price lists
- 📊 **Mining Units Optimization** - Calculate optimal mining unit placement
- 🚀 **Logistics Planning** - Plan cargo runs based on ship capacity
- 📈 **Analytics & Reports** - Detailed profitability analysis and reports
- 👥 **Multi-user Support** - Secure user authentication and personal data storage

## Live Demo

[Access the application here](https://your-app-name.streamlit.app) *(Update after deployment)*

## Support the Developer

If you find this tool helpful, please consider supporting the development by sending ISK donations to:

**lawrokhPL** in EVE Echoes

Your support helps maintain and improve this calculator! o7

## Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/eve-echoes-optimizer.git
cd eve-echoes-optimizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run web_app.py
```

### Environment configuration (.env)

Create a `.env` file in the project root (or use the provided `.env.example`):

```ini
# Backend: file | sql
DATA_BACKEND=sql

# Local dev fallback (SQLite)
SQLITE_PATH=data/local.db

# Cloud SQL (Postgres)
DB_USER=your_user
DB_PASS=your_password
DB_NAME=EveCalcDB
# Choose one connection method:
# 1) TCP for local/dev
DB_HOST=127.0.0.1:5432
# 2) Cloud SQL unix socket on GCP
CLOUD_SQL_CONNECTION_NAME=your-project:region:instance

# Auth backend: local | google
AUTH_BACKEND=local
# Google OAuth (only if AUTH_BACKEND=google)
OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
OAUTH_REDIRECT_URI=

# Streamlit
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8080
```

When `DATA_BACKEND=sql`:
- The app stores users, preferences, prices, price history and mining units in Postgres (Cloud SQL on GCP).
- For local development without Postgres, leave DB variables empty – the app falls back to SQLite at `data/local.db`.

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Data Processing**: Pandas, NumPy
- **Data Storage**: JSON, Parquet

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Contact

For questions or suggestions, please contact the developer in-game: **lawrokhPL**

---
Made with ❤️ for the EVE Echoes community