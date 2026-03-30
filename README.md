# Marketplace MVP

Marketplace MVP built with Django + Django REST Framework for the backend and Next.js for the frontend.

## Project Structure

```text
marketplace-mvp/
|-- backend/   Django API
|-- frontend/  Next.js app
|-- .env.example
```

## Backend Setup

1. Create `backend/.env` from `.env.example`.
2. Create and activate a virtual environment.
3. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start Django:

```bash
python manage.py runserver 127.0.0.1:8000
```

## Frontend Setup

1. Create `frontend/.env.local` from `frontend/.env.local.example`.
2. Install dependencies and start Next.js:

```bash
cd frontend
npm install
npm run dev
```

## Key Environment Variables

Backend:
- `DATABASE_URL`
- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CORS_ALLOWED_ORIGINS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `MANUAL_PAYMENT_BANK_NAME`
- `MANUAL_PAYMENT_ACCOUNT_NAME`
- `MANUAL_PAYMENT_ACCOUNT_NUMBER`
- `MANUAL_PAYMENT_NOTE`
- `DJANGO_MEDIA_STORAGE_BACKEND`
- `DJANGO_MEDIA_PUBLIC_BASE_URL`

Frontend:
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_MEDIA_URL`

## Production Notes

- Set `DJANGO_DEBUG=0` in production.
- Set `DJANGO_ALLOWED_HOSTS` to your Render hostnames.
- Set `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to your Vercel frontend origins.
- Configure manual payment instructions through backend env vars. The frontend no longer hardcodes bank details.
- For production media, set `DJANGO_MEDIA_STORAGE_BACKEND=s3` and provide the S3-compatible env vars from `.env.example`.
- Next.js image loading is env-driven through `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_MEDIA_URL`.

## Verification

Backend:

```bash
python manage.py check
python manage.py test orders catalog
```

Frontend:

```bash
npm run lint
npm run build
```
