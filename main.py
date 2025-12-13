import os
import json
import re  # Email validation
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
from flask import Flask, request
import google.generativeai as genai

# --- CONFIGURATION ---
app = Flask(__name__)
# --- Google Sheet Setup ---
# --- GOOGLE SHEET FUNCTION (Updated) ---
def save_to_sheet(sender, message, user_name, email, city):
    try:
        # 1. Connect
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("google_key.json", scope)
        client = gspread.authorize(creds)
        
        # 2. Open Sheet
        sheet = client.open("Dubai Real Estate Leads").sheet1
        
        # 3. Time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 4. Save Data: [Date, Name, Phone, Message, Email, City]
        sheet.append_row([current_time, user_name, sender, message, email, city])
        print(f"✅ Data Saved: {user_name} | {email} | {city}")
    except Exception as e:
        print(f"❌ Sheet Error: {e}")
# ---------------------------------------
# --------------------------

# REPLACE WITH YOUR KEYS
WHATSAPP_TOKEN = "EAAPf2nk4ZAecBQM3kg6FZCsPVPWFQOZBMySzYAhvbjkNHQclZA0hjbTCzV3ixoZBpK4I2a2dhMCrDTpY8lrUckp1uons8axHgtEzZA3JzcWYcp4qim6BHX5ePZCRwKLKNcddMHHc11epUQkO0kvHEwX0wPIdxZATDTnZAiNyBohlNutgqvK0ZA4ZBZAH1EfZCdpypoXtOlAZDZD" 
PHONE_NUMBER_ID = "904076146124413" 
GEMINI_API_KEY = "AIzaSyDlCNXnqqKTiDCDUluSpYqrgMGAGuiL2Tg" 

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel('gemini-2.0-flash')
model = genai.GenerativeModel('gemini-flash-latest')

# Load Database
try:
    with open('data.json', 'r') as f:
        PROPERTIES = json.load(f)
except Exception as e:
    print(f"Warning: data.json not found or invalid. Error: {e}")
    PROPERTIES = []

# --- HELPER FUNCTIONS ---
def send_whatsapp_text(to_number, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

def send_whatsapp_image(to_number, image_url, caption):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "image",
        "image": {"link": image_url, "caption": caption}
    }
    requests.post(url, headers=headers, json=data)

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
                
#                 # print(f"User said: {text_body}")
#                 # --- 1. NAME EXTRACTION (WhatsApp Profile Name) ---
#                 user_name = "Unknown User"
#                 if "contacts" in value:
#                     try:
#                         user_name = value["contacts"][0]["profile"]["name"]
#                     except:
#                         pass

#                 # --- 2. EMAIL EXTRACTION (Regex se dhundega) ---
#                 email_match = re.search(r'[\w\.-]+@[\w\.-]+', text_body)
#                 user_email = email_match.group(0) if email_match else "Not Provided"

#                 # --- 3. CITY EXTRACTION (Simple Keyword Search) ---
#                 # Aap aur shehar add kar sakte hain
#                 cities = ["dubai", "marina", "downtown", "meydan", "abudhabi", "sharjah", "india", "delhi", "mumbai"]
#                 user_city = "Not Mentioned"
#                 for city in cities:
#                     if city in text_body.lower():
#                         user_city = city.title() # First letter capital kar dega
#                         break

#                 print(f"User Info: {user_name}, Email: {user_email}, City: {user_city}")

#                 # --- 4. SAVE TO SHEET (Ab saari details jayengi) ---
#                 save_to_sheet(sender_id, text_body, user_name, user_email, user_city)

#                 # save_to_sheet(sender_id, text_body)

#                 # --- GEMINI LOGIC ---
#                 # 1. Ask Gemini to reply
#                 # --- STRICTER GEMINI LOGIC ---
#                 prompt = f"""
#                 You are a Logic Bot, not a chat assistant.
#                 User Input: "{text_body}"
                
#                 RULES:
#                 1. If the user mentions 'Marina', 'Downtown', or 'Meydan', reply with ONLY this code: "SHOW_PHOTO: [Location]". Do not add any other text.
#                 2. If no location is found, ask politely if they want Investment or End-use.
#                 """
                
#                 response = model.generate_content(prompt)
#                 reply_text = response.text.strip()
#                 print(f"AI Reply: {reply_text}")

#                 # 2. Check for "Secret Code" to send photos
#                 if "SHOW_PHOTO" in reply_text:
#                     # Extract location
#                     try:
#                         location_key = reply_text.split(":")[1].strip().lower() # e.g., "marina"
#                     except:
#                         location_key = "unknown"
                    
#                     found = False
#                     for prop in PROPERTIES:
#                         if location_key in prop['location'].lower():
#                             found = True
#                             send_whatsapp_text(sender_id, f"Here are the details for {prop['name']}:")
#                             caption = f"Price: {prop['price_aed']} AED\nROI: {prop['roi']}\n{prop['description']}"
#                             send_whatsapp_image(sender_id, prop['image_url'], caption)
                    
#                     if not found:
#                         send_whatsapp_text(sender_id, "I have properties there, but I need to check the latest availability.")
                
#                 else:
#                     # Normal Reply
#                     send_whatsapp_text(sender_id, reply_text)

#     except Exception as e:
#         print(f"Error: {e}")

#     return "OK", 200

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
                
                # --- 1. NAME EXTRACTION ---
                user_name = "Unknown User"
                if "contacts" in value:
                    try:
                        user_name = value["contacts"][0]["profile"]["name"]
                    except:
                        pass

                # --- 2. EMAIL EXTRACTION ---
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', text_body)
                user_email = email_match.group(0) if email_match else "Not Provided"

                # --- 3. CITY EXTRACTION (Updated for Demo) ---
                # Added UK and specific Dubai areas as per your request
                demo_cities = [
                    "dubai", "marina", "downtown", "meydan", "abudhabi", "yas", "saadiyat", 
                    "sharjah", "india", "delhi", "mumbai", 
                    "uk", "london", "manchester", "birmingham"
                ]
                
                user_city = "Not Mentioned"
                # Check against the list
                for city in demo_cities:
                    if city in text_body.lower():
                        user_city = city.title()
                        break
                
                # If not in list, but user provided a location, we mark it as "Custom"
                if user_city == "Not Mentioned" and len(text_body) < 20:
                     # Heuristic: If message is short, it might be a city name not in our list
                     pass 

                print(f"User Info: {user_name}, Email: {user_email}, City: {user_city}")

                # --- 4. SAVE TO SHEET ---
                save_to_sheet(sender_id, text_body, user_name, user_email, user_city)

                # --- 5. GEMINI LOGIC (THE BRAIN) ---
                # We inject the "Polite Demo Persona" here.
                
                prompt = f"""
                You are a sophisticated, polite Real Estate AI Agent for a Client Demo.
                Current User Input: "{text_body}"
                User's Extracted City: "{user_city}"

                YOUR KNOWLEDGE BASE (DEMO DATA):
                - Locations: Dubai (Marina, Downtown, Business Bay), Abu Dhabi (Yas, Saadiyat), UK (London, Manchester).
                - Budget Tiers: 
                  1. Luxury: "The Royal Penthouse Collection" (15M AED / £3M).
                  2. Standard: "Sunrise Family Apartments" (2.5M AED / £500k).
                  3. Budget: "Smart Studios" (650k AED / £150k).

                INSTRUCTIONS:
                1. If the user greets (Hi/Hello), reply warmly: "Hello! It is a pleasure to assist you. Which specific city or area would you like to explore today? (e.g., Dubai Marina, London)"
                
                2. If the user mentions a city inside our 'Locations' list:
                   Reply: "Excellent choice! '{user_city}' is a fantastic market. To tailor the results, do you prefer Luxury, Standard, or Affordable options?"
                
                3. If the user mentions a city NOT in our list (e.g., Tokyo, New York):
                   Reply: "That is a wonderful location. However, for this specific demonstration, our data is optimized for UAE and UK prime markets. Would you like to try a search in Dubai or London instead?"

                4. If the user mentions 'Luxury', 'Standard', or 'Budget':
                   Reply with the details from the 'Budget Tiers' section above politely. Ask if they want to schedule a viewing.

                5. IMAGE TRIGGER RULE: 
                   If the user explicitly asks to SEE photos or asks "Show me [Location]", 
                   ONLY output this exact code: "SHOW_PHOTO: [Location]"
                   (Do not write any other text if you use this code).
                """
                
                response = model.generate_content(prompt)
                reply_text = response.text.strip()
                print(f"AI Reply: {reply_text}")

                # --- 6. REPLY HANDLING ---
                # Check for "Secret Code" to send photos
                if "SHOW_PHOTO" in reply_text:
                    try:
                        location_key = reply_text.split(":")[1].strip().lower()
                    except:
                        location_key = "unknown"
                    
                    found = False
                    # Search in your JSON database
                    for prop in PROPERTIES:
                        if location_key in prop['location'].lower():
                            found = True
                            send_whatsapp_text(sender_id, f"Here are the details for {prop['name']}:")
                            caption = f"Price: {prop['price_aed']} AED\nROI: {prop['roi']}\n{prop['description']}"
                            send_whatsapp_image(sender_id, prop['image_url'], caption)
                    
                    if not found:
                        send_whatsapp_text(sender_id, f"I am searching for the best photos in {location_key}...")
                
                else:
                    # Normal Polite Text Reply
                    send_whatsapp_text(sender_id, reply_text)

    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

if __name__ == '__main__':
    print("🚀 Bot is running on Port 5000...")
    app.run(port=5000)