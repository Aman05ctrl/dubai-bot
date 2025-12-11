import os
import json
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
                
                print(f"User said: {text_body}")

                # --- GEMINI LOGIC ---
                # 1. Ask Gemini to reply
                # --- STRICTER GEMINI LOGIC ---
                prompt = f"""
                You are a Logic Bot, not a chat assistant.
                User Input: "{text_body}"
                
                RULES:
                1. If the user mentions 'Marina', 'Downtown', or 'Meydan', reply with ONLY this code: "SHOW_PHOTO: [Location]". Do not add any other text.
                2. If no location is found, ask politely if they want Investment or End-use.
                """
                
                response = model.generate_content(prompt)
                reply_text = response.text.strip()
                print(f"AI Reply: {reply_text}")

                # 2. Check for "Secret Code" to send photos
                if "SHOW_PHOTO" in reply_text:
                    # Extract location
                    try:
                        location_key = reply_text.split(":")[1].strip().lower() # e.g., "marina"
                    except:
                        location_key = "unknown"
                    
                    found = False
                    for prop in PROPERTIES:
                        if location_key in prop['location'].lower():
                            found = True
                            send_whatsapp_text(sender_id, f"Here are the details for {prop['name']}:")
                            caption = f"Price: {prop['price_aed']} AED\nROI: {prop['roi']}\n{prop['description']}"
                            send_whatsapp_image(sender_id, prop['image_url'], caption)
                    
                    if not found:
                        send_whatsapp_text(sender_id, "I have properties there, but I need to check the latest availability.")
                
                else:
                    # Normal Reply
                    send_whatsapp_text(sender_id, reply_text)

    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

if __name__ == '__main__':
    print("🚀 Bot is running on Port 5000...")
    app.run(port=5000)