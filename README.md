# CV_UP Telegram Bot

A production-ready Telegram bot for CV management and distribution.

## Features

- CV model distribution (Junior/Senior)
- LinkedIn verification system
- User tracking
- Email-based CV delivery
- MongoDB integration
- Vercel deployment ready

## Setup

1. Create a `.env` file with required credentials:
   - TELEGRAM_TOKEN
   - MONGODB_URI
   - LINKEDIN_API_KEY
   - LINKEDIN_POST_URL
   - GMAIL_EMAIL
   - GMAIL_APP_PASSWORD (Generate from Google Account settings)

2. Place CV templates in the `cv_templates` directory:
   - `junior_template.docx`
   - `senior_template.docx`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Deploy to Vercel:
   ```bash
   vercel
   ```

## Commands

- `/start` - Welcome message and bot introduction
- `/sendcv [email] [cv_type]` - Request a CV model (junior/senior)
- `/verify_[code]` - Verify LinkedIn interaction
- `/ask [question]` - Ask a question
- `/myquestions` - View your questions history

## Security

- One CV per type per user
- Email verification
- LinkedIn interaction verification
- Secure MongoDB integration
- Gmail App Password for secure email sending

## CV Templates

Place your CV templates in the `cv_templates` directory:
- `junior_template.docx` - Template for junior positions
- `senior_template.docx` - Template for senior positions