from app.main import app

# Vercel Serverless environment expects an 'app' variable that is a WSGI/ASGI app.
# Our FastAPI app is naturally ASGI, and Vercel's Python runtime natively supports it.
