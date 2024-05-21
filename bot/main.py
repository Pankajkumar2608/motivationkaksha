from lib2to3.pgen2 import driver
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter , landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph
from reportlab.lib import colors
import pandas as pd
import html
import requests
from bs4 import BeautifulSoup
import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from googleapiclient.discovery import build
from telegram import ParseMode

# Replace these with your actual data
API_KEY = 'AIzaSyD8wT7rh4xYFpCVj__nCp_sNrPBRYpoGaw'
CHANNEL_ID = 'UCI5x5XHZnKLO4DTTMqUb0ng'
USER_FILE = 'registered_users.txt'

JOSAA_URL = 'https://josaa.admissions.nic.in/applicant/SeatAllotmentResult/CurrentORCR.aspx'

# Enable logging
IIT_LIST = ["IIT Bombay",
    "IIT Delhi",
    "IIT Madras",
    "IIT Kanpur",
    "IIT Kharagpur",
    "IIT Roorkee",
    "IIT Guwahati",
    "IIT Hyderabad",
    "IIT Ropar",
    "IIT Bhubaneswar",
    "IIT Gandhinagar",
    "IIT Jodhpur",
    "IIT Patna",
    "IIT Indore",
    "IIT Mandi",
    "IIT (BHU) Varanasi",
    "IIT Palakkad",
    "IIT Tirupati",
    "IIT Dhanbad",
    "IIT Bhilai",
    "IIT Goa",
    "IIT Jammu",
    "IIT Dharwad",
    "IIT Bhagalpur",
    "IIT Gandhinagar (Gandhinagar Campus)",
    "IIT Jodhpur (Jodhpur Campus)",
    "IIT Hyderabad (Kandi Campus)",
    "IIT Ropar (Rupnagar Campus)",
    "IIT Bhubaneswar (Bhubaneswar Campus)",
    "IIT Patna (Patna Campus)",
    "IIT Indore (Indore Campus)",
    "IIT Mandi (Mandi Campus)",
    "IIT (BHU) Varanasi (Varanasi Campus)",
    "IIT Palakkad (Palakkad Campus)",
    "IIT Tirupati (Tirupati Campus)",
    "IIT Dhanbad (Dhanbad Campus)"]
NIT_LIST =  ["NIT Trichy",
    "NIT Warangal",
    "NIT Surathkal",
    "NIT Calicut",
    "NIT Rourkela",
    "NIT Kurukshetra",
    "NIT Durgapur",
    "NIT Allahabad",
    "NIT Jamshedpur",
    "NIT Bhopal",
    "NIT Nagpur",
    "NIT Jaipur",
    "NIT Surat",
    "NIT Patna",
    "NIT Hamirpur",
    "NIT Jalandhar",
    "NIT Silchar",
    "NIT Agartala",
    "NIT Raipur",
    "NIT Srinagar",
    "NIT Meghalaya",
    "NIT Manipur",
    "NIT Mizoram",
    "NIT Arunachal Pradesh",
    "NIT Delhi",
    "NIT Goa",
    "NIT Puducherry",
    "NIT Sikkim",
    "NIT Uttarakhand",
    "NIT Andhra Pradesh",
    "NIT Nagaland",
    "NIT Tripura"]
IIIT_LIST = [
    "IIIT Allahabad", "IIIT Chittoor", "IIIT Guwahati", "IIIT Vadodara", 
    "IIIT Sri City", "IIIT Kota", "IIIT Kalyani", "IIIT Lucknow", 
    "IIIT Dharwad", "IIIT Kottayam", "IIIT Pune", "IIIT Una", "IIIT Ranchi", 
    "IIIT Nagpur", "IIIT Bhagalpur", "IIIT Bhopal", "IIIT Surat", "IIIT Manipur", 
    "IIIT Sonepat", "IIIT Kurnool", "IIIT Tiruchirappalli", "IIIT Raichur", 
    "IIIT Agartala", "IIIT Bhagalpur", "IIIT Bhopal", "IIIT Bhubaneswar", 
    "IIIT Dharwad", "IIIT Jabalpur", "IIIT Kakinada", "IIIT Kalyani", 
    "IIIT Kanchipuram", "IIIT Kottayam", "IIIT Kota", "IIIT Lucknow", 
    "IIIT Manipur", "IIIT Nagpur", "IIIT Pune", "IIIT Ranchi", "IIIT Raichur", 
    "IIIT Sricity", "IIIT Surat", "IIIT Una", "IIIT Vadodara"
]
GFTI_LIST = [
    "Assam University, Silchar", "Birla Institute of Technology, Mesra", 
    "Gurukula Kangri Vishwavidyalaya, Haridwar", "Indian Institute of Carpet Technology, Bhadohi", 
    "Institute of Infrastructure, Technology, Research and Management, Ahmedabad", 
    "Shri Mata Vaishno Devi University, Katra", "Institute of Technology, Guru Ghasidas Vishwavidyalaya, Bilaspur", 
    "University Institute of Technology, HPU, Shimla", "University Institute of Engineering and Technology, Panjab University, Chandigarh", 
    "National Institute of Electronics and Information Technology, Aurangabad", "Sant Longowal Institute of Engineering and Technology, Longowal", 
    "School of Engineering and Technology, Mizoram University, Aizawl", "School of Engineering and Technology, Nagaland University, Dimapur", 
    "Central Institute of Technology, Kokrajhar", "School of Engineering, Jadavpur University, Kolkata", 
    "Institute of Chemical Technology, Mumbai", "National Institute of Foundry and Forge Technology, Ranchi", 
    "Indian Institute of Food Processing Technology, Thanjavur", "National Institute of Advanced Manufacturing Technology, Ranchi", 
    "Punjab Engineering College (PEC), Chandigarh"
]

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

def register(update: Update, context: CallbackContext) -> None:
    """Register the user."""
    user_id = update.message.from_user.id
    if user_id not in registered_users:
        user_first_name = update.message.from_user.first_name
        user_username = update.message.from_user.username
        registered_users.add(user_id)
        save_registered_user(user_id)
        update.message.reply_text(f"Registered successfully!\nName: {user_first_name}\nTelegram ID: {user_id}\nUsername: @{user_username}")
        show_main_menu(update.message)
    else:
        update.message.reply_text("You are already registered!")

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.message.from_user.id
    if user_id in registered_users:
        show_main_menu(update.message)
    else:
        keyboard = [
            [InlineKeyboardButton("Register", callback_data='register')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            '*Hey! Welcome to Motivation Kaksha Bot!* Before we proceed, let\'s register first.',
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
def user_count(update: Update, context: CallbackContext) -> None:
    """Show the number of registered users."""
    update.message.reply_text(f"There are {len(registered_users)} users registered on this bot.")
    

def show_main_menu(message):
    keyboard = [
        [InlineKeyboardButton("Motivation", callback_data='motivation')],
        [InlineKeyboardButton("IIT OCR", callback_data='iit')],
        [InlineKeyboardButton("NIT OCR", callback_data='nit')],
        [InlineKeyboardButton("IIIT OCR", callback_data='iiit')],
        [InlineKeyboardButton("GFTI OCR", callback_data='gfti')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply_text('Choose an option:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_first_name = query.from_user.first_name
    user_username = query.from_user.username

    if query.data == 'register':
        registered_users.add(user_id)
        save_registered_user(user_id)
        query.edit_message_text(text=f"Name: {user_first_name}\nTelegram ID: {user_id}\nUsername: @{user_username}\n There are {len(registered_users)} users registered on this bot.")
        query.message.reply_text(f"Welcome to the Motivation Kaksha Bot, {user_first_name}!")
        show_main_menu(query.message)
    elif query.data == 'motivation':
        query.edit_message_text(text="Processing your request, please wait...")
        video_link = get_random_youtube_video()
        query.edit_message_text(
            text=f"Here is a motivational video for you: {video_link}",
            parse_mode=ParseMode.MARKDOWN
        )
        show_main_menu(query.message)
    elif query.data == 'iit':
        send_college_buttons(query, IIT_LIST, 'IIT')
    elif query.data == 'nit':
        send_college_buttons(query, NIT_LIST, 'NIT')
    elif query.data == 'iiit':
        send_college_buttons(query, IIIT_LIST, 'IIIT')
    elif query.data == 'gfti':
        send_college_buttons(query, GFTI_LIST, 'GFTI')
    elif query.data == 'back':
        show_main_menu(query.message)
    else:
        institute_name = query.data.split('_')[1]
        if query.data.startswith('IIT_'):
            institute_type = 'Indian Institute of Technology'
        elif query.data.startswith('NIT_'):
            institute_type = 'National Institute of Technology'
        elif query.data.startswith('IIIT_'):
            institute_type = 'Indian Institute of Information Technology'
        elif query.data.startswith('GFTI_'):
            institute_type = 'Government Funded Technical Institutions '
        # Display a message to the user while the data is being scraped
        query.edit_message_text(text="Processing your request, please wait... Till subcribe our yt channel https://youtube.com/@motivationkaksha?si=LXVF0hgRihCFdJcW")
        pdf_file = scrape_josaa_cutoff(institute_type, institute_name)
        with open(pdf_file, "rb") as file:
            document = InputFile(file)
            query.message.reply_document(document)
        show_main_menu(query.message)

def send_college_buttons(query, college_list, prefix):
    keyboard = []
    for college in college_list:
        college_parts = college.split(' ')
        if len(college_parts) >= 2:
            callback_data = f"{prefix}_{college_parts[1]}"
            keyboard.append([InlineKeyboardButton(college, callback_data=callback_data)])
        else:
            keyboard.append([InlineKeyboardButton(college, callback_data=f"{prefix}_{college}")])
    keyboard.append([InlineKeyboardButton("Back", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Select a {prefix}:", reply_markup=reply_markup)


def get_random_youtube_video():
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.search().list(
        part='snippet',
        channelId=CHANNEL_ID,
        maxResults=50,
        order='date'
    )
    response = request.execute()
    videos = [item['id']['videoId'] for item in response['items'] if item['id']['kind'] == 'youtube#video']
    video_id = random.choice(videos)
    return f"https://www.youtube.com/watch?v={video_id}"

def scrape_josaa_cutoff(institute_type, institute_name):
    """Scrape the cutoff data from JoSAA website for a specific institute."""
    driver = webdriver.Firefox()
    driver.get('https://josaa.admissions.nic.in/applicant/SeatAllotmentResult/CurrentORCR.aspx')

    try:
        wait = WebDriverWait(driver, 10)

        select_round = driver.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_ddlroundno_chosen"]/a')
        select_round.click()
        select_round.send_keys('6' + Keys.ENTER )
        
        time.sleep(2)

        select_inst_type = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_ddlInstype_chosen"]/a')
        select_inst_type.click()
        inputText = institute_type;
        select_inst_type.send_keys(inputText + Keys.ENTER)
        

        # Wait for the next dropdown to load
        time.sleep(2)

        # Locate Institute Name dropdown by its ID and select the option
        select_inst_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_ddlInstitute_chosen"]/a')))
        select_inst_name.click()
        select_inst_name.send_keys(institute_name + Keys.ENTER)
        
        time.sleep(2)


        # Locate Academic Program dropdown by its ID and select the option
        select_program = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_ddlBranch_chosen"]/a')))
        driver.execute_script("arguments[0].click();", select_program)
        select_program.send_keys("A" + Keys.ENTER)

        time.sleep(2)

        # Locate Seat Type / Category dropdown by its ID and select the option
        select_seat_type = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_ddlSeattype_chosen"]/a')))
        select_seat_type.click()
        select_seat_type.send_keys("A" + Keys.ENTER)

        time.sleep(2)

        # Locate the Submit button by its ID and click it
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]')))
        submit_button.click()

        # Wait for the results to load
        time.sleep(5)
    finally:
        # Wait for the table to be present on the page
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div[2]")))

        # Scroll down to the table
        driver.execute_script("arguments[0].scrollIntoView(true);", table)

        # Extract the table data
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            data.append(row_data)

        # Create a pandas DataFrame from the extracted data
        df = pd.DataFrame(data, columns=["Institute", "Academic Program Name", "Quota", "Seat Type", "Gender", "Opening Rank", "Closing Rank"])
    custom_width = 1.5 * letter[1]  # Width in landscape orientation
    custom_height = 1.5 * letter[0]  # Height in landscape orientation
    custom_pagesize = (custom_width, custom_height)

    doc = SimpleDocTemplate("josaa_cutoff.pdf", pagesize= custom_pagesize )
    elements = []

    header_style = ParagraphStyle(name='Header', parent=None, fontSize=14, leading=16, textColor=colors.white, backColor=colors.grey, alignment=1, spaceAfter=12)
    header = Paragraph("JOSAA Cutoff", header_style)
    elements.append(header)

    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data)
    table_style = TableStyle([
       ('BACKGROUND', (0,0), (-1,0), colors.grey),
       ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
       ('ALIGN', (0,0), (-1,-1), 'CENTER'),
       ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
       ('FONTSIZE', (0,0), (-1,0), 14),
       ('BOTTOMPADDING', (0,0), (-1,0), 12),
       ('BACKGROUND', (0,1), (-1,-1), colors.beige),
       ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    table.setStyle(table_style)
    elements.append(table)
    styles = getSampleStyleSheet()
    watermark_style = ParagraphStyle(name='Watermark', parent=styles['BodyText'], fontSize=50, leading=50, textColor=colors.grey, alignment=1)
    watermark = Paragraph("Motivation Kaksha", watermark_style)
    elements.append(watermark)

    doc.build(elements)


    # Close the browser
    driver.quit()
    return "josaa_cutoff.pdf"

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('This bot helps you get the JOSAA cutoff data. Use the buttons to navigate through the options.')

def main() -> None:
    """Start the bot."""
    # Use Updater with context to support newer versions of the library
    updater = Updater(token="6831597916:AAF-1Ayowl6_3KZIvxpDAM22RGsfeAIRoTM", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("usercount", user_count))

    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()