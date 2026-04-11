# Bachata Club - Milestone 4 (Code Institute)

Bachata Club is a full-stack Django membership platform for Bachata dancers. Visitors can explore the homepage and subscription plans, create an account, activate a free 30-day membership when logged in, and access members-only Bachata lesson videos and practice logs.

The project is built around a clean, responsive interface, protected member content, and a membership model that can be extended to Stripe-powered paid subscriptions.

---

# 1. UX

## Project Overview

Bachata Club is designed for dancers who want structured learning, consistent practice, and a simple way to access premium Bachata content. The site presents the studio brand clearly on the homepage, explains the membership value on the pricing page, and gives logged-in users immediate access to a free 30-day trial.

Members can browse released video lessons, filter by level, and track their practice logs. The experience is intentionally lightweight and practical so the main actions are easy to understand.

### Features Overview

- **Homepage**: A clean landing page that introduces the Bachata Club brand, highlights the learning path, and links users to membership actions.
- **Membership Plans**: A pricing page that shows the available plan cards and lets logged-in users start a free 30-day membership immediately.
- **Authentication**: Standard sign up, log in, and log out pages for account access.
- **Member Library**: A protected video lesson area for active members.
- **Practice Logs**: A simple log system for recording practice sessions and tracking progress.
- **Subscription Status**: A page that shows the member's current status and time remaining in the free trial.
- **Responsive Design**: The layout adapts to desktop, tablet, and mobile screen sizes.
- **Filtering and Search**: The member video library includes level filtering and title search.

### User Experience Highlights

- The homepage gives a strong visual identity while keeping the main actions easy to find.
- Logged-in users can activate a free 30-day membership with one button click.
- Member-only pages are protected so access is controlled by membership status.
- The member library is structured to make lessons easy to browse by level.
- Practice logging keeps the site useful beyond passive video watching.
- Forms and buttons are kept simple so the flow is easy to follow on mobile devices.
- Status messages and redirects guide users through sign up, login, and membership activation.

### Website Preview

**Homepage**
- Introduces the brand and learning offer.
- Links to membership plans, login, sign up, and the member library when available.

**Membership Plans**
- Shows the available membership card layout.
- Lets logged-in users start the free 30-day membership straight away.

**Subscription Status**
- Displays the current membership state.
- Shows remaining free-trial days when access is active.

**Member Library**
- Shows released Bachata lessons for active members.
- Includes filtering by level and search by title.

**Practice Logs**
- Lets members create, review, and edit practice entries.

---

# 2. HTML Structure Overview

The project is split into reusable templates that work together to provide a consistent experience:

- **base.html**: The shared layout containing the navigation bar, main content wrapper, flash messages, and script loading.
- **home/index.html**: The homepage with the hero section, brand block, calls to action, and feature cards.
- **accounts/signup.html**: Account creation page.
- **registration/login.html**: Login page used by Django's auth system.
- **registration/logged_out.html**: Logout confirmation page.
- **subscriptions/pricing.html**: Membership plan display and activation entry point.
- **subscriptions/status.html**: Membership status and free-trial progress page.
- **subscriptions/checkout_success.html**: Checkout success page for future paid flow support.
- **subscriptions/checkout_cancel.html**: Checkout cancel page for future paid flow support.
- **videos/member_library.html**: Protected lesson library for members.
- **practice/log_list.html**: Practice log overview page.
- **practice/log_form.html**: Create/edit practice log form.

The templates use semantic HTML, Bootstrap layout helpers, and custom styling classes to keep the structure readable and maintainable.

---

# 3. CSS Class Reference

The project uses a custom stylesheet to create a clear visual identity and a responsive layout.

## Layout and Structure

- **.page-shell**: Shared width and spacing wrapper.
- **.page-header**: Card-like header block used across pages.
- **.panel-grid**: Grid layout for cards and content blocks.
- **.panel-card**: Generic content card.
- **.status-panel**: Subscription status container.
- **.message-panel**: Empty state and message container.

## Homepage Styles

- **.home-main**: Removes default container constraints on the homepage.
- **.home-hero**: Main homepage hero section.
- **.home-hero__overlay**: Background overlay element for the hero area.
- **.home-hero__inner**: Main hero layout grid.
- **.home-hero__content**: Text content block on the homepage.
- **.home-brand**: Brand row containing the logo mark and text.
- **.home-title**: Main homepage heading.
- **.home-lead**: Homepage introductory paragraph.
- **.home-actions**: Call-to-action button row.
- **.home-btn**: Shared homepage button styling.
- **.home-features**: Grid for the three feature cards.
- **.home-card**: Individual feature card.

## Subscription and Member Pages

- **.subscriptions-page**: Page-level subscription theme hook.
- **.subscription-hero**: Main subscriptions hero section.
- **.subscription-shell**: Wrapper for subscription content.
- **.subscription-header**: Header block on subscription pages.
- **.subscription-grid**: Membership plan card layout.
- **.status-pill**: Membership status badge.
- **.modern-actions**: Action button container.

## Typography and Colors

- **.page-title**: Shared page heading style.
- **.page-lead**: Shared descriptive text style.
- **.panel-title**: Card title styling.
- **.panel-text**: Card body text styling.
- **.home-card__kicker**: Small uppercase label above each feature card.
- **.home-brand__eyebrow**: Upper label in the homepage brand block.
- **.home-brand__label**: Supporting brand description text.

## Forms and Buttons

- **.btn-primary**: Main action button style.
- **.btn-success**: Confirmation and success actions.
- **.btn-outline-primary**: Secondary action button.
- **.form-panel**: Form wrapper card.
- **.form-control**: Bootstrap form field styling, refined through the custom stylesheet.

## Responsive Design

Media queries adjust the layout on smaller screens so the homepage, subscription cards, and member content remain usable on phones and tablets.

---

# 4. Credits

This project was completed using Django, Bootstrap, vanilla JavaScript, and custom CSS.

**Technologies and libraries used:**
- Django
- Stripe integration
- Bootstrap 5
- WhiteNoise
- dj-database-url
- python-dotenv
- psycopg2-binary
- gunicorn
- Google Fonts: Cinzel and Manrope

The overall structure was built using Code Institute Full Stack learning principles and adapted into a membership-based Bachata platform.

---

# 5. Testing

## Django Checks

The project was checked with Django's built-in system checks during development.

Run the check command with:

```powershell
python manage.py check
```

## Manual Testing

The main user flows were checked during development:

| Test Case | Expected Outcome |
|-----------|------------------|
| Homepage loads | Hero section and feature cards display correctly |
| Pricing page loads | Membership plans display correctly |
| Logged-in activation | Free 30-day membership is created immediately |
| Logged-out activation | User is sent to login/sign up flow |
| Member library access | Only active members can open the lesson library |
| Subscription status | Free-trial days remaining are shown |
| Practice logs | Members can create and manage practice entries |
| Responsive layout | Layout works on desktop, tablet, and mobile |

## Accessibility Checks

The interface was designed with readability in mind:

- Semantic HTML elements are used throughout.
- Navigation and forms are easy to follow with keyboard focus.
- Text contrast has been tuned for readability on both light and dark sections.
- The layout scales well on smaller screens.

---

# 6. Deployment

### Version Control with Git

The project is managed with Git so changes can be tracked and prepared for GitHub.

Typical workflow:

```powershell
git status
git add .
git commit -m "Update Bachata Club README and styling"
```

## Production Deployment

This project is ready to be deployed to a Python hosting platform such as Heroku, Render, Railway, or PythonAnywhere.

**Required environment variables:**

```text
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:5432/dbname
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

**Deployment steps:**

1. Install production dependencies.
2. Configure environment variables.
3. Run migrations.
4. Collect static files.
5. Push the project to GitHub.
6. Deploy the repository to your hosting platform.
7. Verify the site after deployment.

The repository includes a `Procfile` and WhiteNoise support for static file serving.

---

# 7. User Stories

### User Story 1: New Visitor

**As a** new visitor interested in Bachata
**I want to** understand the membership offer quickly
**So that** I can decide whether to join

**Implemented by:** homepage hero, feature cards, and pricing page.

### User Story 2: Logged-In Dancer

**As a** logged-in dancer
**I want to** start a free membership right away
**So that** I can access the member library immediately

**Implemented by:** the free 30-day activation button and membership status page.

### User Story 3: Returning Member

**As a** returning member
**I want to** find lessons and log practice easily
**So that** I can continue improving my dancing

**Implemented by:** member library filters, search, and practice logs.

### User Story 4: Studio Admin

**As a** studio admin
**I want to** manage plans, lessons, and membership records
**So that** the content stays organised and current

**Implemented by:** Django admin and the project data models.

---

# 8. Purpose and Value

Bachata Club provides a focused membership experience for dancers who want a structured path into Bachata learning.

**For students:**
- Simple sign up and login flow
- Immediate access to a free 30-day membership when logged in
- Clear lesson library with level-based filtering
- Practice logs for tracking progress

**For the studio:**
- Membership status tracking
- Admin management through Django
- A structured way to introduce premium content
- A platform that can be expanded into a paid subscription model

---

# 9. Features

- Public homepage with a strong brand identity
- Membership pricing page
- Free 30-day membership activation for logged-in users
- Protected member-only lesson library
- Lesson filtering by level and search by title
- Practice log create, read, update, and edit functionality
- Django authentication integration
- Subscription status page with access details
- Responsive layout and button system

---

# 10. Tech Stack

- **Backend:** Python, Django
- **Database:** SQLite in development, PostgreSQL ready for production
- **Frontend:** HTML5, CSS3, Bootstrap 5, vanilla JavaScript
- **Payments:** Stripe integration is included for subscription support
- **Static file serving:** WhiteNoise
- **Environment handling:** python-dotenv
- **Deployment support:** gunicorn and Procfile

---

# 11. Setup

### 1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the project root and add the required values.

### 4) Apply database migrations

```powershell
python manage.py migrate
```

### 5) Create a superuser

```powershell
python manage.py createsuperuser
```

### 6) Run the development server

```powershell
python manage.py runserver
```

Then open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/admin/

---

# 12. Database Schema

## `videos.VideoLesson`

- `title`
- `slug`
- `description`
- `level`
- `video_url`
- `release_date`
- `is_published`
- `created_at`
- `updated_at`

## `subscriptions.SubscriptionPlan`

- `name`
- `stripe_price_id`
- `monthly_price`
- `is_active`

## `subscriptions.Membership`

- One-to-one relation with `User`
- `stripe_customer_id`
- `stripe_subscription_id`
- `status`
- `current_period_end`
- `updated_at`

## `practice.PracticeLog`

- Foreign key to `User`
- Optional foreign key to `VideoLesson`
- `practiced_on`
- `minutes`
- `notes`
- `created_at`
- `updated_at`

---

# 13. URLs

## Main Routes

- `/` - Root redirect to the homepage
- `/home/` - Homepage
- `/accounts/signup/` - Sign up
- `/accounts/login/` - Log in
- `/accounts/logout/` - Log out
- `/subscriptions/` - Membership pricing page
- `/subscriptions/status/` - Membership status page
- `/subscriptions/activate-free/` - Free 30-day activation
- `/subscriptions/checkout/<plan_id>/` - Stripe checkout route
- `/subscriptions/success/` - Checkout success page
- `/subscriptions/cancel/` - Checkout cancel page
- `/members/` - Member lesson library
- `/practice/` - Practice log list
- `/practice/new/` - Create practice log
- `/practice/<pk>/edit/` - Edit practice log
- `/admin/` - Django admin

---

# 14. CRUD Coverage

- **Create**: sign up, free membership activation, create practice logs, create lesson and plan records in admin
- **Read**: homepage, pricing, status, member library, practice log list
- **Update**: edit practice logs, update membership records in admin, update lesson records in admin
- **Delete**: practice log management can be extended through admin or future user actions

---

# 15. Code Quality and Standards

**Python:**
- Clear function and model names
- Django conventions followed for views, models, and URLs
- Environment variables used for secrets and deployment settings

**HTML/CSS:**
- Semantic markup
- Reusable template blocks
- Custom styling layered on top of Bootstrap
- Responsive layout helpers

**Project Organisation:**
- Separate apps for different concerns
- Reusable templates and shared base layout
- Static assets separated from templates

---

# 16. Stripe Configuration Notes

Stripe support is included for future paid subscription plans.

To use Stripe for paid plans:

1. Create a recurring monthly Price in Stripe.
2. Add the `price_...` value to `SubscriptionPlan.stripe_price_id` in Django admin.
3. Configure your Stripe webhook endpoint to point to `/subscriptions/webhook/`.
4. Add the webhook secret to `STRIPE_WEBHOOK_SECRET`.

The current user-facing flow gives logged-in users a free 30-day membership immediately, while the Stripe checkout route remains available for future expansion.

---

# 17. Project Structure

```text
14_milestione4/
├── accounts/
├── bachata_club/
├── home/
├── practice/
├── subscriptions/
├── videos/
├── static/
│   ├── css/
│   ├── images/
│   └── js/
├── templates/
│   ├── accounts/
│   ├── home/
│   ├── practice/
│   ├── registration/
│   ├── subscriptions/
│   └── videos/
├── manage.py
├── Procfile
├── requirements.txt
└── README.md
```

---

# 18. Future Enhancements

Possible improvements for later versions:

- Email confirmations for membership activation
- Real paid subscription checkout for monthly billing
- Lesson progress tracking
- Instructor dashboard for content planning
- Better analytics for practice logs
- Member profile pages
- Waitlist or event booking features
- Multi-location support

---

# 19. Credits and Attribution

- **Framework:** Django
- **Styling:** Bootstrap 5 and custom CSS
- **Payments:** Stripe integration
- **Fonts:** Google Fonts
- **Static serving:** WhiteNoise
- **Deployment support:** gunicorn and PostgreSQL-ready configuration

All project code in this repository is original work built for the Code Institute milestone project, with standard framework and library usage where required.

---

# 20. License

This project was created for educational purposes as part of Code Institute training.

---

# 21. Contact

For questions about the project, use the GitHub repository once it has been pushed and published.

---

# 22. Commit and Push

After reviewing the README and any other staged changes, use the standard Git workflow:

```powershell
git status
git add README.md
git commit -m "Rewrite README for Bachata Club"
git push origin main
```

If the remote is not configured yet, add it first with `git remote add origin <your-repo-url>`.
