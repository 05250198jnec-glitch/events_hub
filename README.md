# Smart Hall Booking System — JNEC

**Student:** Tashi  
**Student ID:** 05250198

A full-stack hall booking application based on the supplied Smart Hall Booking System screens. Built with Flask, SQLite, HTML, CSS and JavaScript.

## Features
- Student registration/login with hashed passwords and session authentication
- Hall catalogue, category filtering, capacity and indicative prices
- Booking with date/time validation, capacity checks and conflict prevention
- Booking history and cancellation
- Admin dashboard with approval/rejection and summary counts
- Feedback form
- SQLite database and sample halls/admin account created automatically

## Run locally
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Demo admin
- Email: `admin@college.edu`
- Password: `Admin123!`

Change the demo password and set a strong `SECRET_KEY` before deployment. The SQLite database is created as `smart_hall.db` on first run.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/register | Register |
| POST | /api/login | Login |
| POST | /api/logout | Logout |
| GET | /api/me | Current user |
| GET | /api/halls | List halls |
| GET | /api/bookings | User bookings |
| POST | /api/bookings | Create booking |
| POST | /api/bookings/{id}/cancel | Cancel booking |
| POST | /api/feedback | Submit feedback |
| GET | /api/admin/dashboard | Admin dashboard |
| PATCH | /api/admin/bookings/{id} | Approve/reject |
