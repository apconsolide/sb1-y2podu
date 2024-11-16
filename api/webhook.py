from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import random
import string
from datetime import datetime
from .database import Database
from .models import User, Question, CVRequest
from .email_sender import EmailSender

load_dotenv()

# Environment variables
TOKEN = os.getenv('TELEGRAM_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY')
LINKEDIN_POST_URL = os.getenv('LINKEDIN_POST_URL')

# Initialize services
db = Database(MONGODB_URI)
email_sender = EmailSender()

WELCOME_MESSAGE = """Welcome to CV_UP! 🌟
Here you can:
1. Get your CV corrected ✍️
2. Get a ready CV model (junior/senior) 📄
3. Access general resources 📚
4. Ask questions (Q&A) ❓
5. Find job offers 💼
6. Prepare for interviews 🎯

Use /help to see available commands."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome new users and save their info"""
    user = update.effective_user
    db.upsert_user(User(
        telegram_id=user.id,
        username=user.username,
        joined_date=datetime.utcnow()
    ))
    await update.message.reply_text(WELCOME_MESSAGE)

def generate_verification_code():
    """Generate random verification code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def send_cv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CV request command"""
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "Please use the format: /sendcv email_address cv_type(junior/senior)"
            )
            return

        email = args[0]
        cv_type = args[-1].lower()
        user_id = update.effective_user.id

        if cv_type not in ['junior', 'senior']:
            await update.message.reply_text("CV type must be either 'junior' or 'senior'")
            return

        # Update user's email
        db.upsert_user(User(
            telegram_id=user_id,
            username=update.effective_user.username,
            email=email,
            joined_date=datetime.utcnow()
        ))

        # Check existing requests
        existing_requests = db.get_user_cv_requests(user_id)
        if any(r.cv_type == cv_type and r.status == "completed" for r in existing_requests):
            await update.message.reply_text(
                "You have already received this CV type. Each user can only get one copy of each CV type."
            )
            return

        verification_code = generate_verification_code()
        
        # Create new CV request
        cv_request = CVRequest(
            telegram_id=user_id,
            email=email,
            cv_type=cv_type,
            verification_code=verification_code,
            status="pending",
            request_date=datetime.utcnow()
        )
        db.add_cv_request(cv_request)

        keyboard = [[
            InlineKeyboardButton(
                "Verify on LinkedIn", 
                url=f"{LINKEDIN_POST_URL}"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Please follow these steps to receive your CV:\n\n"
            f"1. Click the button below to open our LinkedIn post\n"
            f"2. Like the post\n"
            f"3. Comment with this code: {verification_code}\n"
            f"4. Return here and click /verify_{verification_code}\n\n"
            f"Once verified, your CV will be sent to {email}",
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(
            "An error occurred. Please try again or contact support."
        )
        print(f"Error in send_cv: {e}")

async def verify_linkedin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify LinkedIn interaction and send CV"""
    try:
        command = update.message.text
        verification_code = command.split('_')[1]

        cv_request = db.get_cv_request(verification_code)
        if not cv_request or cv_request.status != "pending":
            await update.message.reply_text(
                "Invalid or expired verification code. Please try again."
            )
            return

        # TODO: Implement LinkedIn API verification
        verified = True

        if verified:
            # Send CV via email
            email_sent = email_sender.send_cv(cv_request.email, cv_request.cv_type)
            
            if email_sent:
                db.update_cv_request_status(
                    verification_code,
                    "completed",
                    linkedin_verified=True
                )
                await update.message.reply_text(
                    f"Verification successful! Your CV has been sent to {cv_request.email}. "
                    "Please check your inbox (and spam folder)."
                )
            else:
                await update.message.reply_text(
                    "Verification successful but there was an error sending the CV. "
                    "Please try again or contact support."
                )
        else:
            await update.message.reply_text(
                "Verification failed. Please ensure you've liked and commented on the LinkedIn post."
            )

    except Exception as e:
        await update.message.reply_text(
            "An error occurred during verification. Please try again."
        )
        print(f"Error in verify_linkedin: {e}")

async def my_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's questions and their status"""
    questions = db.get_user_questions(update.effective_user.id)
    
    if not questions:
        await update.message.reply_text("You haven't asked any questions yet.")
        return
    
    response = "Your questions:\n\n"
    for i, q in enumerate(questions, 1):
        response += f"{i}. Status: {q.status}\n"
        response += f"Q: {q.question_text}\n"
        if q.answer_text:
            response += f"A: {q.answer_text}\n"
        response += "\n"
    
    await update.message.reply_text(response)

def main():
    """Set up and run the bot"""
    app = Application.builder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sendcv", send_cv))
    app.add_handler(CommandHandler("verify", verify_linkedin))
    app.add_handler(CommandHandler("ask", ask_question))
    app.add_handler(CommandHandler("myquestions", my_questions))

    # Start webhook
    return app

app = main()