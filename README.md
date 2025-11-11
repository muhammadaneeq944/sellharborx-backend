# SellHarborX Backend

A FastAPI backend for SellHarborX, deployed on Render and connected to MongoDB Atlas.

## 🚀 Deployment on Render

1. Push this folder to GitHub.
2. Go to [Render.com](https://render.com/) → New Web Service → Connect your repo.
3. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
4. Add Environment Variables (from `.env.example`).
5. Deploy 🎉

## ⚙️ Environment Variables

| Variable | Description |
|-----------|--------------|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `ADMIN_USERNAME` | Admin username |
| `ADMIN_PASSWORD` | Admin password |
| `MAIL_USERNAME` | SMTP username |
| `MAIL_PASSWORD` | SMTP password |
| `MAIL_FROM` | Email sender |
| `MAIL_PORT` | SMTP port |
| `MAIL_SERVER` | SMTP server host |

## 🧩 Stack
- FastAPI
- Gunicorn + Uvicorn
- MongoDB (Atlas)
- Render (Free Tier)
