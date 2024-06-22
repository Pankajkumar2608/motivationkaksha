import asyncio
import os
import logging
import random
import time
import csv
from io import StringIO
from telegram import ChatMember
from telegram.ext import ChatMemberHandler
from telegram.ext import  CommandHandler, CallbackQueryHandler, Application, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from googleapiclient.discovery import build
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.firefox.service import Service as FirefoxService

# Replace these with your actual data
API_KEY = 'AIzaSyD8wT7rh4xYFpCVj__nCp_sNrPBRYpoGaw'

USER_FILE = 'registered_users.txt'
CHANNEL_ID = '-1002244117290'
JOSAA_URL = 'https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx'
MOTIVATIONKAKSHA_URL = 'https://motivationkaksha-website-2216612a3de0.herokuapp.com'

# Create a cache dictionary
cache = {}

# College name lists
IIT_LIST = ["IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", "IIT Kharagpur", "IIT Roorkee", "IIT Guwahati", "IIT Hyderabad", "IIT Ropar", "IIT Bhubaneswar", "IIT Gandhinagar", "IIT Jodhpur", "IIT Patna", "IIT Indore", "IIT Mandi", "IIT (BHU) Varanasi", "IIT Palakkad", "IIT Tirupati", "IIT Dhanbad", "IIT Bhilai", "IIT Goa", "IIT Jammu", "IIT Dharwad", "IIT Bhagalpur", "IIT Gandhinagar (Gandhinagar Campus)", "IIT Jodhpur (Jodhpur Campus)", "IIT Hyderabad (Kandi Campus)", "IIT Ropar (Rupnagar Campus)", "IIT Bhubaneswar (Bhubaneswar Campus)", "IIT Patna (Patna Campus)", "IIT Indore (Indore Campus)", "IIT Mandi (Mandi Campus)", "IIT (BHU) Varanasi (Varanasi Campus)", "IIT Palakkad (Palakkad Campus)", "IIT Tirupati (Tirupati Campus)", "IIT Dhanbad (Dhanbad Campus)"]
NIT_LIST = ["NIT Trichy", "NIT Warangal", "NIT Surathkal", "NIT Calicut", "NIT Rourkela", "NIT Kurukshetra", "NIT Durgapur", "NIT Allahabad", "NIT Jamshedpur", "NIT Bhopal", "NIT Nagpur", "NIT Jaipur", "NIT Surat", "NIT Patna", "NIT Hamirpur", "NIT Jalandhar", "NIT Silchar", "NIT Agartala", "NIT Raipur", "NIT Srinagar", "NIT Meghalaya", "NIT Manipur", "NIT Mizoram", "NIT Arunachal Pradesh", "NIT Delhi", "NIT Goa", "NIT Puducherry", "NIT Sikkim", "NIT Uttarakhand", "NIT Andhra Pradesh", "NIT Nagaland", "NIT Tripura"]
IIIT_LIST = ["IIIT Allahabad", "IIIT Chittoor", "IIIT Guwahati", "IIIT Vadodara", "IIIT Sri City", "IIIT Kota", "IIIT Kalyani", "IIIT Lucknow", "IIIT Dharwad", "IIIT Kottayam", "IIIT Pune", "IIIT Una", "IIIT Ranchi", "IIIT Nagpur", "IIIT Bhagalpur", "IIIT Bhopal", "IIIT Surat", "IIIT Manipur", "IIIT Sonepat", "IIIT Kurnool", "IIIT Tiruchirappalli", "IIIT Raichur", "IIIT Agartala", "IIIT Bhagalpur", "IIIT Bhopal", "IIIT Bhubaneswar", "IIIT Dharwad", "IIIT Jabalpur", "IIIT Kakinada", "IIIT Kalyani", "IIIT Kanchipuram", "IIIT Kottayam", "IIIT Kota", "IIIT Lucknow", "IIIT Manipur", "IIIT Nagpur", "IIIT Pune", "IIIT Ranchi", "IIIT Raichur", "IIIT Sricity", "IIIT Surat", "IIIT Una", "IIIT Vadodara"]
GFTI_LIST = ["Assam University, Silchar", "Birla Institute of Technology, Mesra", "Gurukula Kangri Vishwavidyalaya, Haridwar", "Indian Institute of Carpet Technology, Bhadohi", "Institute of Infrastructure, Technology, Research and Management, Ahmedabad", "Shri Mata Vaishno Devi University, Katra", "Institute of Technology, Guru Ghasidas Vishwavidyalaya, Bilaspur", "University Institute of Technology, HPU, Shimla", "University Institute of Engineering and Technology, Panjab University, Chandigarh", "National Institute of Electronics and Information Technology, Aurangabad", "Sant Longowal Institute of Engineering and Technology, Longowal", "School of Engineering and Technology, Mizoram University, Aizawl", "School of Engineering and Technology, Nagaland University, Dimapur", "Central Institute of Technology, Kokrajhar", "School of Engineering and Technology, Jadavpur University, Kolkata", "Institute of Chemical Technology, Mumbai", "National Institute of Foundry and Forge Technology, Ranchi", "Indian Institute of Food Processing Technology, Thanjavur", "National Institute of Advanced Manufacturing Technology, Ranchi", "Punjab Engineering College (PEC), Chandigarh"]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Load registered users from file
def load_registered_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as file:
            return set(line.strip() for line in file)
    return set()

# Save registered user to file
def save_registered_user(user_id):
    with open(USER_FILE, 'a') as file:
        file.write(f"{user_id}\n")

registered_users = load_registered_users()

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register the user."""
    user_id = update.effective_user.id
    if user_id not in registered_users:
        user_first_name = update.effective_user.first_name
        user_username = update.effective_user.username
        registered_users.add(user_id)
        save_registered_user(user_id)

        # Create the registration message using HTML formatting
        register_msg = f"""
<b>✅ Registered successfully!</b>

Name: {user_first_name}
Telegram ID: <code>{user_id}</code>
Username: @{user_username}

There are <b>{len(registered_users)}</b> users registered on this bot.
"""
        keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(register_msg, parse_mode='HTML', reply_markup=reply_markup)
        await show_main_menu(update.message)
    else:
        await update.message.reply_text("❗️ <b>You are already registered!</b>", parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    if user_id in registered_users:
        await show_main_menu(update.message)
    else:
        keyboard = [
            [InlineKeyboardButton("🔑 Register", callback_data='register')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            '👋 *Hey Welcome to Motivation Kaksha Bot!* Before we proceed, let\'s register first.',
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def user_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the number of registered users."""
    await update.message.reply_text(f"🙋‍♂️ There are {len(registered_users)} users registered on this bot.")

async def show_main_menu(message):
    keyboard = [
        [InlineKeyboardButton("💪 Motivation", callback_data='motivation')],
        [InlineKeyboardButton("🎓 IIT OCR", callback_data='iit')],
        [InlineKeyboardButton("🏫 NIT OCR", callback_data='nit')],
        [InlineKeyboardButton("🏢 IIIT OCR", callback_data='iiit')],
        [InlineKeyboardButton("🏭 GFTI OCR", callback_data='gfti')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text('*Choose an option:*', reply_markup=reply_markup, parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_first_name = query.from_user.first_name
    user_username = query.from_user.username

    if query.data == 'register':
        if user_id not in registered_users:
            registered_users.add(user_id)
            save_registered_user(user_id)

            # Create the registration message using HTML formatting
            register_msg = f"""
<b>✅ Registered successfully!</b>

Name: {user_first_name}
Telegram ID: <code>{user_id}</code>
Username: @{user_username}

There are <b>{len(registered_users)}</b> users registered on this bot.
"""
            keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text(register_msg, parse_mode='HTML', reply_markup=reply_markup)
            await show_main_menu(query.message)
        else:
            await query.message.reply_text("❗️ <b>You are already registered!</b>", parse_mode='HTML')

    elif query.data == 'motivation':
        await query.edit_message_text(text="🔍 Processing your request, please wait...")
        video_link = get_random_youtube_video()
        await query.edit_message_text(
            text=f"🎥 Here is a motivational video for you: {video_link}",
            parse_mode='Markdown'
        )
        await show_main_menu(query.message)
    elif query.data in ['iit', 'nit', 'iiit', 'gfti']:
        if query.data == 'iit':
            url = MOTIVATIONKAKSHA_URL + '/iit'
        elif query.data == 'nit':
            url = MOTIVATIONKAKSHA_URL + '/nit'
        elif query.data == 'iiit':
            url = MOTIVATIONKAKSHA_URL + '/iiit'
        elif query.data == 'gfti':
            url = MOTIVATIONKAKSHA_URL + '/gfti'
        await query.edit_message_text(text=f"Checkout cutoff on this website: {url}")
        await show_main_menu(query.message)
    elif query.data == 'back':
        await show_main_menu(query.message)
    else:
        await query.message.reply_text("Invalid option. Please choose again.")

async def get_josaa_cutoff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the JOSAA cutoff data and send the CSV to the user."""
    institute_type = update.message.text.split(' ').lower()
    if institute_type == '/iitocr':
        url = MOTIVATIONKAKSHA_URL
    elif institute_type == '/nitocr':
        url = MOTIVATIONKAKSHA_URL
    elif institute_type == '/iiitocr':
        url = MOTIVATIONKAKSHA_URL
    elif institute_type == '/gftiocr':
        url = MOTIVATIONKAKSHA_URL
    else:
        await update.message.reply_text(text="Invalid command. Please use /iitocr, /nitocr, /iiitocr, or /gftiocr.")
        return
    await update.message.reply_text(text=f"Checkout cutoff on this website: {url}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 *Motivation Kaksha Bot*

This bot helps you get the JOSAA cutoff data. Here's how you can use it:

1. Use the /start command to get started.
2. Click on the buttons to navigate through the options:
   - 💪 *Motivation*: Get motivational content.
   - 🎓 *IIT OCR*: Get the JOSAA cutoff data for IITs.
   - 🏫 *NIT OCR*: Get the JOSAA cutoff data for NITs.
   - 🏢 *IIIT OCR*: Get the JOSAA cutoff data for IIITs.
   - 🏭 *GFTI OCR*: Get the JOSAA cutoff data for GFTIs.
3. The bot will provide the cutoff data in a CSV format.

4. Hey, I'd love to hear your thoughts about the bot.\n Do you have any feedback or suggestions on how I can improve?\n Please let me know, and I'll do my best to make the necessary changes.\n use command  /feedback (Your valueble feedback)

*Credits: This bot was developed by [Pankaj](https://t.me/unofficial_g_o_d).*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def send_notification_to_users(context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    """Send a notification message to all registered users."""
    for user_id in registered_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {e}")

async def send_notification_to_groups(context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    """Send a notification message to all groups where the bot is added."""
    for chat_id in context.bot_data.get('groups', []):
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"Error sending notification to group {chat_id}: {e}")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a notification message to all registered users and groups."""
    user_id = update.effective_user.id
    if user_id == 1268179255:
        message = update.message.text.split(' ', 1)
        await send_notification_to_users(context, message)
        await send_notification_to_groups(context, message)
    else:
        await update.message.reply_text("❌ You are not authorized to use this command.")

async def handle_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle chat member updates."""
    chat_id = update.effective_chat.id
    if update.my_chat_member.new_chat_member.status == ChatMember.ADMINISTRATOR:
        context.bot_data.setdefault('groups', []).append(chat_id)
    elif update.my_chat_member.old_chat_member.status == ChatMember.ADMINISTRATOR:
        context.bot_data.get('groups', []).remove(chat_id)

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    user_username = update.effective_user.username
    feedback_text = update.message.text.split(' ', 1)
    feedback_message = f"📝 Feedback from {user_first_name} (@{user_username}, ID: {user_id}):\n\n{feedback_text}"
    await context.bot.send_message(chat_id="1268179255", text=feedback_message)
    await update.message.reply_text("📨 Your feedback has been sent to the bot owner. Thank you!")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token("6831597916:AAF-1Ayowl6_3KZIvxpDAM22RGsfeAIRoTM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("usercount", user_count))
    application.add_handler(CommandHandler("josaa_cutoff", get_josaa_cutoff))
    application.add_handler(CommandHandler("notify", notify))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(ChatMemberHandler(handle_chat_member_update))
    application.add_handler(CommandHandler("feedback", feedback))
    application.run_polling()

if __name__ == '__main__':
    main()
