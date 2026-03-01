# Bachata Club - Milestone 4 (Code Institute)

Bachata Club is a full-stack Django subscription platform where users can register, subscribe monthly via Stripe, and access members-only Bachata lesson videos. New videos are intended to be released weekly and are visible only to active subscribers.

## Project Description

Bachata Club is a subscription-based learning platform where users pay monthly to access exclusive Bachata dance video lessons, with new members-only content released weekly.

## Quick Start (Clone + Run)

```bash
git clone https://github.com/Juanakas/code_institute_milestone_4.git
cd code_institute_milestone_4
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then:

```bash
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Business Model

- Public users can view the homepage and pricing details.
- Registered users can subscribe using Stripe Checkout.
- Only users with an active subscription status can access the members library and practice tracking features.

## Main Features

- Django multi-app architecture (`home`, `accounts`, `videos`, `subscriptions`, `practice`)
- User registration/login/logout
- Stripe subscription checkout flow
- Stripe webhook handling to sync subscription status
- Protected members area for video lessons
- Weekly release-ready lesson model (`release_date`, `is_published`)
- Practice log CRUD for authenticated subscribed members
- Bootstrap responsive navigation and pages
- JavaScript lesson filtering (level + search)

## Data Model Summary

### `videos.VideoLesson`
- `title`, `slug`, `description`, `level`, `video_url`, `release_date`, `is_published`

### `subscriptions.SubscriptionPlan`
- `name`, `stripe_price_id`, `monthly_price`, `is_active`

### `subscriptions.Membership`
- One-to-one with user, stores Stripe IDs and active period/status

### `practice.PracticeLog`
- Linked to user and optional lesson, includes date, minutes, and notes

## Mandatory Requirements Mapping

1. **Django Full Stack Project**: Implemented with Django and relational DB support.
2. **Multiple Apps**: Five reusable apps created.
3. **Data Modeling**: Multiple custom models with relationships.
4. **User Authentication**: Registration, login, logout configured.
5. **User Interaction**: Practice log form with validation for create/edit.
6. **Use of Stripe**: Subscription checkout + webhook processing included.
7. **Structure and Navigation**: Main nav + Bootstrap layout.
8. **Use of JavaScript**: Member library filter/search script.
9. **Documentation**: This README included.
10. **Version Control**: Project is ready for Git/GitHub workflow.
11. **Attribution**: No external tutorial code copied into source.
12. **Deployment**: `Procfile`, production settings, and dependency list added.
13. **Security**: Secrets moved to environment variables, debug controlled by env.

## Setup Instructions

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in values.
4. Run migrations:
   - `python manage.py migrate`
5. Create admin user:
   - `python manage.py createsuperuser`
6. Run server:
   - `python manage.py runserver`

## Stripe Configuration Notes

- Create a monthly recurring Price in Stripe and copy the `price_...` ID.
- In Django admin, create a `SubscriptionPlan` and paste that Price ID.
- Configure Stripe webhook endpoint to:
  - `/subscriptions/webhook/`
- Add webhook secret to `STRIPE_WEBHOOK_SECRET`.

## Deployment Notes

- Set `DEBUG=0` in production.
- Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` appropriately.
- Provide production `DATABASE_URL` (PostgreSQL recommended).

## Content Population (Next Step)

- Upload/add weekly Bachata videos by creating `VideoLesson` entries in admin.
- Publish each lesson by setting `is_published=True` and `release_date`.
