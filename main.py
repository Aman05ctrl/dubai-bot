# import os
# import json
# import re  # Email validation
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from datetime import datetime
# import requests
# from flask import Flask, request
# import google.generativeai as genai

# # --- CONFIGURATION ---
# app = Flask(__name__)
# # --- Google Sheet Setup ---
# # --- GOOGLE SHEET FUNCTION (Updated) ---
# def save_to_sheet(sender, message, user_name, email, city):
#     try:
#         # 1. Connect
#         scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#         creds = ServiceAccountCredentials.from_json_keyfile_name("google_key.json", scope)
#         client = gspread.authorize(creds)
        
#         # 2. Open Sheet
#         sheet = client.open("Dubai Real Estate Leads").sheet1
        
#         # 3. Time
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
#         # 4. Save Data: [Date, Name, Phone, Message, Email, City]
#         sheet.append_row([current_time, user_name, sender, message, email, city])
#         print(f"✅ Data Saved: {user_name} | {email} | {city}")
#     except Exception as e:
#         print(f"❌ Sheet Error: {e}")
# # ---------------------------------------
# # --------------------------

# # REPLACE WITH YOUR KEYS
# WHATSAPP_TOKEN = "EAAPf2nk4ZAecBQM3kg6FZCsPVPWFQOZBMySzYAhvbjkNHQclZA0hjbTCzV3ixoZBpK4I2a2dhMCrDTpY8lrUckp1uons8axHgtEzZA3JzcWYcp4qim6BHX5ePZCRwKLKNcddMHHc11epUQkO0kvHEwX0wPIdxZATDTnZAiNyBohlNutgqvK0ZA4ZBZAH1EfZCdpypoXtOlAZDZD" 
# PHONE_NUMBER_ID = "904076146124413" 
# GEMINI_API_KEY = "AIzaSyDlCNXnqqKTiDCDUluSpYqrgMGAGuiL2Tg" 

# # Setup Gemini
# genai.configure(api_key=GEMINI_API_KEY)
# # model = genai.GenerativeModel('gemini-2.0-flash')
# model = genai.GenerativeModel('gemini-flash-latest')

# # Load Database
# try:
#     with open('data.json', 'r') as f:
#         PROPERTIES = json.load(f)
# except Exception as e:
#     print(f"Warning: data.json not found or invalid. Error: {e}")
#     PROPERTIES = []

# # --- HELPER FUNCTIONS ---
# def send_whatsapp_text(to_number, text):
#     url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
#     headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
#     data = {
#         "messaging_product": "whatsapp",
#         "to": to_number,
#         "type": "text",
#         "text": {"body": text}
#     }
#     requests.post(url, headers=headers, json=data)

# def send_whatsapp_image(to_number, image_url, caption):
#     url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
#     headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
#     data = {
#         "messaging_product": "whatsapp",
#         "to": to_number,
#         "type": "image",
#         "image": {"link": image_url, "caption": caption}
#     }
#     requests.post(url, headers=headers, json=data)

# # --- SERVER ---
# @app.route('/webhook', methods=['GET'])
# def verify():
#     if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
#         return request.args.get("hub.challenge")
#     return "Verification Failed", 403

# @app.route('/webhook', methods=['POST'])
# def webhook():
#     data = request.json
#     try:
#         if data.get("object"):
#             entry = data["entry"][0]
#             changes = entry["changes"][0]
#             value = changes["value"]
            
#             if "messages" in value:
#                 message = value["messages"][0]
#                 sender_id = message["from"]
#                 text_body = message["text"]["body"]
                
#                 # --- 1. NAME EXTRACTION ---
#                 user_name = "Unknown User"
#                 if "contacts" in value:
#                     try:
#                         user_name = value["contacts"][0]["profile"]["name"]
#                     except:
#                         pass

#                 # --- 2. EMAIL EXTRACTION ---
#                 email_match = re.search(r'[\w\.-]+@[\w\.-]+', text_body)
#                 user_email = email_match.group(0) if email_match else "Not Provided"

#                 # --- 3. CITY EXTRACTION (Updated for Demo) ---
#                 # Added UK and specific Dubai areas as per your request
#                 demo_cities = [
#                     "dubai", "marina", "downtown", "meydan", "abudhabi", "yas", "saadiyat", 
#                     "sharjah", "india", "delhi", "mumbai", 
#                     "uk", "london", "manchester", "birmingham"
#                 ]
                
#                 user_city = "Not Mentioned"
#                 # Check against the list
#                 for city in demo_cities:
#                     if city in text_body.lower():
#                         user_city = city.title()
#                         break
                
#                 # If not in list, but user provided a location, we mark it as "Custom"
#                 if user_city == "Not Mentioned" and len(text_body) < 20:
#                      # Heuristic: If message is short, it might be a city name not in our list
#                      pass 

#                 print(f"User Info: {user_name}, Email: {user_email}, City: {user_city}")

#                 # --- 4. SAVE TO SHEET ---
#                 save_to_sheet(sender_id, text_body, user_name, user_email, user_city)

                
#                 # 1. THE BRAIN (Sarah's Personality & Rules)
#                 prompt = f"""
#                 You are Sarah, a Senior Property Consultant. You are chatting with a client on WhatsApp.
#                 TONE: Professional but warm, casual, and direct. Use emojis naturally (👋, 🏡, ✨).
#                 GOAL: Guide them from City -> Budget -> Closing.
                
#                 Current User Input: "{text_body}"
#                 User's Extracted City: "{user_city}"

#                 YOUR DATA:
#                 - Locations: Dubai (Marina, Downtown), Abu Dhabi (Yas, Saadiyat), UK (London, Manchester).
#                 - Luxury Tier: "The Royal Penthouse Collection" (15M AED / £3M).
#                 - Standard Tier: "Sunrise Family Apartments" (2.5M AED / £500k).

#                 INSTRUCTIONS:
#                 1. GREETING: If user says Hi/Hello, reply: 
#                    "Hi there! 👋 I'm Sarah. It's a pleasure to assist you. Which city or area are you looking into today? (e.g., Dubai Marina, London)"

#                 2. LOCATION RECEIVED: If user mentions a valid location (like "{user_city}"), reply:
#                    "Excellent choice! 🏙️ '{user_city}' is a fantastic market. To tailor the best options, do you prefer Luxury, Standard, or Affordable?"

#                 3. BUDGET RECEIVED (THE MAGIC STEP): 
#                    If the user mentions 'Luxury', 'Standard', or 'Budget':
#                    - First, describe the property nicely based on the 'YOUR DATA' section.
#                    - THEN, strictly append this code at the end: "SHOW_PHOTO: {user_city}"
#                    (This will automatically send them the image while you talk).

#                 4. DIRECT IMAGE REQUEST: 
#                    If the user asks "Show me photos" or "Images", reply:
#                    "Here is a glimpse of what we have available. SHOW_PHOTO: {user_city}"

#                 5. OUT OF SCOPE: If they ask for a city not in the list (e.g. Tokyo), redirect them politely to Dubai or UK.
#                 """
                
#                 # 2. GENERATE RESPONSE
#                 response = model.generate_content(prompt)
#                 full_reply = response.text.strip()
                
#                 # 3. CLEANUP (Fix Bold Formatting for WhatsApp)
#                 # Convert **Bold** to *Bold*
#                 full_reply = full_reply.replace("**", "*")
                
#                 # 4. SMART SEPARATION (Talk + Show Photo)
#                 # Sarah might send text AND a photo command. We need to split them.
                
#                 if "SHOW_PHOTO" in full_reply:
#                     # Logic: Split the text from the command
#                     try:
#                         # 1. Extract the text part (Sarah's speech)
#                         text_part = full_reply.split("SHOW_PHOTO")[0].strip()
#                         if text_part:
#                             send_whatsapp_text(sender_id, text_part)
                        
#                         # 2. Extract the location for the photo
#                         command_part = full_reply.split("SHOW_PHOTO")[1] # Gets ": Dubai Marina"
#                         location_part = command_part.replace(":", "").strip().lower()
#                         # Clean up any accidental symbols
#                         location_key = location_part.replace("*", "").replace(".", "")
                        
#                         # 3. Find and Send Image
#                         found = False
#                         for prop in PROPERTIES:
#                             if location_key in prop['location'].lower():
#                                 found = True
#                                 # Send the image
#                                 caption = f"📸 *View:* {prop['name']}\n*Price:* {prop['price_aed']} AED\n*ROI:* {prop['roi']}"
#                                 send_whatsapp_image(sender_id, prop['image_url'], caption)
#                                 break # Stop after finding the first match
                        
#                         if not found:
#                             # Fallback if Sarah tried to show a photo we don't have
#                             pass # Do nothing, just the text sent above is enough
                            
#                     except Exception as e:
#                         print(f"Error parsing hybrid response: {e}")
#                         send_whatsapp_text(sender_id, full_reply.replace("SHOW_PHOTO", "")) # Just send text if error
                
#                 else:
#                     # No photo command, just normal chat
#                     print(f"AI Reply: {full_reply}")
#                     send_whatsapp_text(sender_id, full_reply)

#     except Exception as e:
#         print(f"Error: {e}")

#     return "OK", 200

# if __name__ == '__main__':
#     print("🚀 Bot is running on Port 5000...")
#     app.run(port=5000)


# import os
# import json
# import re
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from datetime import datetime
# import pytz  # DUBAI TIME ke liye zaroori
# import requests
# from flask import Flask, request
# import google.generativeai as genai

# # --- CONFIGURATION ---
# app = Flask(__name__)

# # REPLACE WITH YOUR KEYS
# WHATSAPP_TOKEN = "EAAPf2nk4ZAecBQM3kg6FZCsPVPWFQOZBMySzYAhvbjkNHQclZA0hjbTCzV3ixoZBpK4I2a2dhMCrDTpY8lrUckp1uons8axHgtEzZA3JzcWYcp4qim6BHX5ePZCRwKLKNcddMHHc11epUQkO0kvHEwX0wPIdxZATDTnZAiNyBohlNutgqvK0ZA4ZBZAH1EfZCdpypoXtOlAZDZD" 
# PHONE_NUMBER_ID = "904076146124413" 
# GEMINI_API_KEY = "AIzaSyDlCNXnqqKTiDCDUluSpYqrgMGAGuiL2Tg" 

# # Setup Gemini
# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel('gemini-flash-latest')

# # Load Database
# try:
#     with open('data.json', 'r') as f:
#         PROPERTIES = json.load(f)
# except Exception as e:
#     print(f"Warning: data.json not found. Error: {e}")
#     PROPERTIES = []

# # --- HELPER: TIMEZONE & PHONE FORMAT ---
# def get_dubai_time():
#     # Server time ko Dubai Time mein convert karna
#     try:
#         dubai_tz = pytz.timezone('Asia/Dubai')
#         return datetime.now(dubai_tz).strftime("%Y-%m-%d %H:%M:%S")
#     except Exception:
#         # Fallback agar pytz fail ho (rare case)
#         return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# def format_phone_number(phone_id):
#     # Country code alag karna
#     if phone_id.startswith("91"):
#         return "+91", phone_id[2:]
#     elif phone_id.startswith("971"):
#         return "+971", phone_id[3:]
#     elif phone_id.startswith("1"):
#         return "+1", phone_id[1:]
#     elif phone_id.startswith("44"):
#         return "+44", phone_id[2:]
#     else:
#         return "", phone_id # Default

# # --- GOOGLE SHEET FUNCTION (STRICTLY SAFE UPDATE) ---
# def update_sheet_smartly(sender_id, user_name, email, city, interest):
#     try:
#         # 1. Connect
#         scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#         creds = ServiceAccountCredentials.from_json_keyfile_name("google_key.json", scope)
#         client = gspread.authorize(creds)
#         sheet = client.open("Dubai Real Estate Leads").sheet1
        
#         # 2. Prepare Data
#         current_time = get_dubai_time()
#         country_code, clean_phone = format_phone_number(sender_id)
        
#         # 3. Check if User Exists (Search by Raw Phone ID in Column H)
#         # Note: Column H index is 8
#         cell = None
#         try:
#             cell = sheet.find(sender_id) 
#         except gspread.exceptions.CellNotFound:
#             cell = None
#         except Exception as e:
#             print(f"Search Error: {e}")
#             cell = None

#         if cell:
#             # --- EXISTING USER (SAFE UPDATE ONLY) ---
#             # Rule: Date (Col 1), Code (Col 3), Phone (Col 4) ko touch nahi karna.
#             # Rule: Sirf wahi cell update karo jo user ne naya diya hai.
            
#             row_num = cell.row
#             print(f"🔄 User found at Row {row_num}. Checking for new info...")
            
#             # Name Update: Sirf tab jab wo "Unknown" na ho
#             if user_name != "Unknown User":
#                 sheet.update_cell(row_num, 2, user_name)
                
#             # Interest Update (Column E = 5)
#             if interest != "Not Specified":
#                 sheet.update_cell(row_num, 5, interest) 
#                 print(f"   -> Updated Interest to {interest}")
                
#             # Email Update (Column F = 6)
#             if email != "Not Provided":
#                 sheet.update_cell(row_num, 6, email)    
#                 print(f"   -> Updated Email to {email}")
                
#             # City Update (Column G = 7)
#             if city != "Not Mentioned":
#                 sheet.update_cell(row_num, 7, city)     
#                 print(f"   -> Updated City to {city}")

#         else:
#             # --- NEW USER (CREATE ROW) ---
#             print(f"🆕 Creating new user: {user_name}")
            
#             # Column Structure:
#             # A: Date | B: Name | C: Code | D: Phone | E: Interest | F: Email | G: City | H: RAW_ID
            
#             sheet.append_row([
#                 current_time,   # A: Join Date
#                 user_name,      # B: Name
#                 country_code,   # C: Country Code (+91)
#                 clean_phone,    # D: Clean Phone
#                 interest,       # E: Interest
#                 email,          # F: Email
#                 city,           # G: City
#                 sender_id       # H: Raw ID (Hidden/System)
#             ])
            
#     except Exception as e:
#         print(f"❌ Sheet Error: {e}")

# # --- WHATSAPP SENDERS ---
# def send_whatsapp_text(to_number, text):
#     try:
#         url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
#         headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
#         data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text}}
#         requests.post(url, headers=headers, json=data)
#     except Exception as e:
#         print(f"WhatsApp Send Error: {e}")

# def send_whatsapp_image(to_number, image_url, caption):
#     try:
#         url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
#         headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
#         data = {"messaging_product": "whatsapp", "to": to_number, "type": "image", "image": {"link": image_url, "caption": caption}}
#         requests.post(url, headers=headers, json=data)
#     except Exception as e:
#         print(f"WhatsApp Image Error: {e}")

# # --- SERVER ---
# @app.route('/webhook', methods=['GET'])
# def verify():
#     if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
#         return request.args.get("hub.challenge")
#     return "Verification Failed", 403

# @app.route('/webhook', methods=['POST'])
# def webhook():
#     data = request.json
#     try:
#         if data.get("object"):
#             entry = data["entry"][0]
#             changes = entry["changes"][0]
#             value = changes["value"]
            
#             if "messages" in value:
#                 message = value["messages"][0]
#                 sender_id = message["from"]
#                 text_body = message["text"]["body"]
                
#                 # --- 1. DATA EXTRACTION ---
#                 user_name = "Unknown User"
#                 if "contacts" in value:
#                     try:
#                         user_name = value["contacts"][0]["profile"]["name"]
#                     except:
#                         pass

#                 # Email Extraction
#                 email_match = re.search(r'[\w\.-]+@[\w\.-]+', text_body)
#                 user_email = email_match.group(0) if email_match else "Not Provided"

#                 # City Extraction
#                 demo_cities = ["dubai", "marina", "downtown", "meydan", "abudhabi", "yas", "uk", "london", "manchester"]
#                 user_city = "Not Mentioned"
#                 for city in demo_cities:
#                     if city in text_body.lower():
#                         user_city = city.title()
#                         break
                
#                 # Interest Extraction
#                 user_interest = "Not Specified"
#                 if "luxury" in text_body.lower(): user_interest = "Luxury"
#                 elif "standard" in text_body.lower(): user_interest = "Standard"
#                 elif "budget" in text_body.lower() or "affordable" in text_body.lower(): user_interest = "Affordable"

#                 print(f"Extracted: {user_name} | {user_email} | {user_city} | {user_interest}")

#                 # --- 2. UPDATE SHEET (SMARTLY) ---
#                 # Naya logic yahan call hoga with fixed columns
#                 update_sheet_smartly(sender_id, user_name, user_email, user_city, user_interest)

#                 # --- 3. SARAH PERSONA LOGIC ---
#                 prompt = f"""
#                 You are Sarah, a Senior Property Consultant. You are chatting with a client on WhatsApp.
#                 TONE: Professional but warm, casual, and direct. Use emojis naturally (👋, 🏡, ✨).
#                 GOAL: Guide them from City -> Budget -> Closing.
                
#                 Current User Input: "{text_body}"
#                 User's Extracted City: "{user_city}"

#                 YOUR DATA:
#                 - Locations: Dubai (Marina, Downtown), Abu Dhabi (Yas, Saadiyat), UK (London, Manchester).
#                 - Luxury Tier: "The Royal Penthouse Collection" (15M AED / £3M).
#                 - Standard Tier: "Sunrise Family Apartments" (2.5M AED / £500k).

#                 INSTRUCTIONS:
#                 1. GREETING: If user says Hi/Hello, reply: 
#                    "Hi there! 👋 I'm Sarah. It's a pleasure to assist you. Which city or area are you looking into today? (e.g., Dubai Marina, London)"

#                 2. LOCATION RECEIVED: If user mentions a valid location (like "{user_city}"), reply:
#                    "Excellent choice! 🏙️ '{user_city}' is a fantastic market. To tailor the best options, do you prefer Luxury, Standard, or Affordable?"

#                 3. BUDGET RECEIVED (THE MAGIC STEP): 
#                    If the user mentions 'Luxury', 'Standard', or 'Budget':
#                    - First, describe the property nicely based on the 'YOUR DATA' section.
#                    - THEN, strictly append this code at the end: "SHOW_PHOTO: {user_city}"
#                    (This will automatically send them the image while you talk).

#                 4. DIRECT IMAGE REQUEST: 
#                    If the user asks "Show me photos" or "Images", reply:
#                    "Here is a glimpse of what we have available. SHOW_PHOTO: {user_city}"

#                 5. OUT OF SCOPE: If they ask for a city not in the list (e.g. Tokyo), redirect them politely to Dubai or UK.

#                 6. EMAIL COLLECTION:
#                    If the conversation is progressing and they show interest, gently ask:
#                    "To share the full brochure and floor plans, may I have your email address? 📧"
#                 """
                
#                 # Generate AI Response
#                 try:
#                     response = model.generate_content(prompt)
#                     full_reply = response.text.strip()
#                     full_reply = full_reply.replace("**", "*") # Fix Bold
#                 except Exception as e:
#                     print(f"Gemini Error: {e}")
#                     full_reply = "I'm having a little trouble connecting to my database. Could you please say that again?"

#                 # --- 4. HANDLE RESPONSE (Photo vs Text) ---
#                 if "SHOW_PHOTO" in full_reply:
#                     try:
#                         # Logic to split text and command safely
#                         parts = full_reply.split("SHOW_PHOTO")
#                         text_part = parts[0].strip()
                        
#                         if len(parts) > 1:
#                             command_part = parts[1]
#                         else:
#                             command_part = ": unknown" # Fallback

#                         if text_part:
#                             send_whatsapp_text(sender_id, text_part)
                        
#                         location_part = command_part.replace(":", "").strip().lower()
#                         location_key = location_part.replace("*", "").replace(".", "")
                        
#                         found = False
#                         for prop in PROPERTIES:
#                             if location_key in prop['location'].lower():
#                                 found = True
#                                 caption = f"📸 *View:* {prop['name']}\n*Price:* {prop['price_aed']} AED\n*ROI:* {prop['roi']}"
#                                 send_whatsapp_image(sender_id, prop['image_url'], caption)
#                                 break
                        
#                         if not found:
#                              pass # Image nahi mili toh sirf text kaafi hai
                            
#                     except Exception as e:
#                         print(f"Error parsing hybrid response: {e}")
#                         # Fallback: Agar parsing fail ho toh poora text bhej do (bina command ke)
#                         send_whatsapp_text(sender_id, full_reply.replace("SHOW_PHOTO", ""))
#                 else:
#                     send_whatsapp_text(sender_id, full_reply)

#     except Exception as e:
#         print(f"Webhook Error: {e}")

#     return "OK", 200

# if __name__ == '__main__':
#     # Render uses Gunicorn, but this is fine for local testing
#     print("🚀 Bot is running on Port 5000...")
#     app.run(port=5000)

import os
import json
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import requests
from flask import Flask, request
import google.generativeai as genai

# --- CONFIGURATION ---
app = Flask(__name__)

# REPLACE WITH YOUR KEYS
WHATSAPP_TOKEN = "EAAPf2nk4ZAecBQM3kg6FZCsPVPWFQOZBMySzYAhvbjkNHQclZA0hjbTCzV3ixoZBpK4I2a2dhMCrDTpY8lrUckp1uons8axHgtEzZA3JzcWYcp4qim6BHX5ePZCRwKLKNcddMHHc11epUQkO0kvHEwX0wPIdxZATDTnZAiNyBohlNutgqvK0ZA4ZBZAH1EfZCdpypoXtOlAZDZD" 
PHONE_NUMBER_ID = "904076146124413" 
GEMINI_API_KEY = "AIzaSyDlCNXnqqKTiDCDUluSpYqrgMGAGuiL2Tg" 

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# --- LOAD DATABASE (SECURE WAY) ---
# Ye ensure karega ki Render par file sahi se mile
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
KEY_FILE = os.path.join(BASE_DIR, 'google_key.json')

try:
    with open(DATA_FILE, 'r') as f:
        PROPERTIES = json.load(f)
        print(f"✅ Database Loaded: {len(PROPERTIES)} properties found.")
except Exception as e:
    print(f"❌ Critical Error: data.json not found or invalid. {e}")
    PROPERTIES = []

# --- HELPER FUNCTIONS ---
def get_dubai_time():
    try:
        dubai_tz = pytz.timezone('Asia/Dubai')
        return datetime.now(dubai_tz).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_phone_number(phone_id):
    """
    Splits Country Code (+91) and Number strictly.
    Input: 918470911526 -> Output: +91, 8470911526
    """
    phone_id = str(phone_id)
    if phone_id.startswith("91") and len(phone_id) > 10:
        return "+91", phone_id[2:]
    elif phone_id.startswith("971"):
        return "+971", phone_id[3:]
    elif phone_id.startswith("1") and len(phone_id) > 10:
        return "+1", phone_id[1:]
    elif phone_id.startswith("44"):
        return "+44", phone_id[2:]
    else:
        return "", phone_id 

# --- DUAL SHEET MANAGER (PROFILES + LOGS) ---
def handle_dual_sheets(sender_id, user_name, message_content, email, city, interest, reply_type):
    try:
        # 1. Connect
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scope)
        client = gspread.authorize(creds)
        
        # Open Spreadsheet
        spreadsheet = client.open("Dubai Real Estate Leads")
        
        current_time = get_dubai_time()
        country_code, clean_phone = format_phone_number(sender_id)

        # ----------------------------------------
        # TASK 1: UPDATE "Logs" (Conversation History)
        # ----------------------------------------
        try:
            sheet_logs = spreadsheet.worksheet("Logs")
            # Headers: Timestamp | Name | Country Code | Phone | Message | Reply Type
            sheet_logs.append_row([
                current_time, 
                user_name, 
                country_code, 
                clean_phone, 
                message_content, 
                reply_type
            ])
            print(f"📝 Logged to History: {message_content}")
        except Exception as e:
            print(f"❌ Error logging history (Check 'Logs' tab name): {e}")

        # ----------------------------------------
        # TASK 2: UPDATE "Profiles" (One Row Per User)
        # ----------------------------------------
        try:
            sheet_profiles = spreadsheet.worksheet("Profiles")
            
            # Search by Raw ID (Column H -> Index 8)
            cell = None
            try:
                cell = sheet_profiles.find(sender_id)
            except:
                cell = None
            
            if cell:
                # --- UPDATE EXISTING USER ---
                row_num = cell.row
                # Sirf naya data update karein, overwrite na karein agar khali ho
                if user_name != "Unknown User": 
                    sheet_profiles.update_cell(row_num, 2, user_name)
                if interest != "Not Specified": 
                    sheet_profiles.update_cell(row_num, 5, interest)
                if email != "Not Provided": 
                    sheet_profiles.update_cell(row_num, 6, email)
                if city != "Not Mentioned": 
                    sheet_profiles.update_cell(row_num, 7, city)
                print(f"🔄 Profile Updated for Row {row_num}")
            else:
                # --- CREATE NEW PROFILE ---
                print(f"🆕 Creating New Profile for {user_name}")
                # Headers: Date | Name | Code | Phone | Interest | Email | City | RawID
                sheet_profiles.append_row([
                    current_time, 
                    user_name, 
                    country_code, 
                    clean_phone, 
                    interest, 
                    email, 
                    city, 
                    sender_id
                ])
        except Exception as e:
            print(f"❌ Error updating profile (Check 'Profiles' tab name): {e}")
            
    except Exception as e:
        print(f"❌ Gspread Connection Error: {e}")

# --- WHATSAPP SENDERS ---
def send_whatsapp_text(to_number, text):
    try:
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text}}
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Send Error: {e}")

def send_whatsapp_image(to_number, image_url, caption):
    try:
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        data = {"messaging_product": "whatsapp", "to": to_number, "type": "image", "image": {"link": image_url, "caption": caption}}
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Image Error: {e}")

# --- SERVER ---
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        return request.args.get("hub.challenge")
    return "Verification Failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        if data.get("object"):
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            
            if "messages" in value:
                message = value["messages"][0]
                sender_id = message["from"]
                text_body = message["text"]["body"]
                
                # --- DATA EXTRACTION ---
                user_name = "Unknown User"
                if "contacts" in value:
                    try:
                        user_name = value["contacts"][0]["profile"]["name"]
                    except:
                        pass

                email_match = re.search(r'[\w\.-]+@[\w\.-]+', text_body)
                user_email = email_match.group(0) if email_match else "Not Provided"

                # Expanded Cities List
                demo_cities = ["dubai", "marina", "downtown", "meydan", "abudhabi", "yas", "uk", "london", "manchester"]
                user_city = "Not Mentioned"
                for city in demo_cities:
                    if city in text_body.lower():
                        user_city = city.title()
                        break
                
                user_interest = "Not Specified"
                if "luxury" in text_body.lower(): user_interest = "Luxury"
                elif "standard" in text_body.lower(): user_interest = "Standard"
                elif "budget" in text_body.lower() or "affordable" in text_body.lower(): user_interest = "Affordable"

                print(f"📩 Msg from {user_name}: {text_body}")

                # --- SARAH LOGIC ---
                prompt = f"""
                You are Sarah, a Senior Property Consultant. 
                TONE: Professional but warm, casual, and direct. Use emojis (👋, 🏡).
                GOAL: Guide them from City -> Budget -> Closing.
                
                Current User Input: "{text_body}"
                User's Extracted City (from this message): "{user_city}"

                YOUR DATA:
                - Locations: Dubai (Marina, Downtown), Abu Dhabi (Yas), UK (London).
                - Luxury Tier: "The Royal Penthouse Collection" (15M AED).
                - Standard Tier: "Sunrise Family Apartments" (2.5M AED).

                INSTRUCTIONS:
                1. GREETING: If user says Hi/Hello: "Hi there! 👋 I'm Sarah. Which city or area are you looking into today?"
                
                2. LOCATION: If location mentioned (like "{user_city}"): 
                   "Excellent choice! 🏙️ '{user_city}' is fantastic. Do you prefer Luxury, Standard, or Affordable?"

                3. BUDGET (MAGIC STEP): If budget/tier mentioned AND you know the City:
                   - Describe property.
                   - THEN append: "SHOW_PHOTO: {user_city}"

                4. IMAGE REQUEST (CRITICAL): 
                   - If user asks for photos AND "{user_city}" is VALID:
                     Reply: "Here is a glimpse. SHOW_PHOTO: {user_city}"
                   - If user asks for photos BUT City is Unknown:
                     Reply: "I'd love to show you photos! 📸 Could you remind me which area you are interested in? (e.g. Dubai Marina, Downtown)"

                5. EMAIL: If interested, ask for email politely.
                """
                
                reply_type = "Text Reply" 
                try:
                    response = model.generate_content(prompt)
                    full_reply = response.text.strip().replace("**", "*")
                except:
                    full_reply = "I'm checking the database, please wait a moment."

                # --- HANDLE RESPONSE ---
                if "SHOW_PHOTO" in full_reply:
                    reply_type = "Image Sent"
                    try:
                        # Extract Command
                        parts = full_reply.split("SHOW_PHOTO")
                        text_part = parts[0].strip()
                        command_part = parts[1] if len(parts) > 1 else ": unknown"

                        if text_part: send_whatsapp_text(sender_id, text_part)
                        
                        # Clean Location Key
                        location_key = command_part.replace(":", "").replace("*", "").replace(".", "").strip().lower()
                        print(f"🔍 Searching Image for: {location_key}")

                        found = False
                        # Check in Loaded Properties
                        for prop in PROPERTIES:
                            if location_key in prop['location'].lower():
                                found = True
                                caption = f"📸 *View:* {prop['name']}\n*Price:* {prop['price_aed']} AED\n*ROI:* {prop['roi']}"
                                send_whatsapp_image(sender_id, prop['image_url'], caption)
                                break
                        
                        if not found:
                             print("❌ Image not found in data.json")
                             send_whatsapp_text(sender_id, "I have the details, but I'm just fetching the latest photos for that area. One moment please!")
                             
                    except Exception as e:
                        print(f"Hybrid Error: {e}")
                        send_whatsapp_text(sender_id, full_reply.replace("SHOW_PHOTO", ""))
                else:
                    send_whatsapp_text(sender_id, full_reply)

                # --- UPDATE SHEETS ---
                handle_dual_sheets(sender_id, user_name, text_body, user_email, user_city, user_interest, reply_type)

    except Exception as e:
        print(f"Webhook Error: {e}")

    return "OK", 200

if __name__ == '__main__':
    # Render uses Gunicorn, but this is fine for local testing
    print("🚀 Bot is running on Port 5000...")
    app.run(port=5000)