import requests
import json
import httpx
import uuid
import cloudscraper
import time
import winsound

ACCESS_TOKEN = "EAAPtaG2c554BPIZBpzJ04h3AenkMs754SFugSU1tmQqdQdwuhHXDYF1VWPWOPZBs9kqXrWa8YVGHtsTqK36iYKTofwZAjZBmekcMhYIWkqLAbKjzX6XIPP9ME11OQFX1mBwIMAKwxGKzaRDWfSWpGfyOmoSl0flj9j7ORjrMdEARD4SlbFqBZB0XTs3ZC9DZCYwmQZDZD"
PHONE_NUMBER_ID = "731071996758445"
TO_NUMBER = "916383438324"
whatsappUrl = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "messaging_product": "whatsapp",
    "to": TO_NUMBER,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        }
    }
}

def get_json_from_text(url, start_text, end_text):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    data = response.text

    start_index = data.find(start_text)
    if start_index == -1:
        print("ERROR: Starting index not found!")
        return None
    start_index += len(start_text)

    end_index = data.find(end_text, start_index)
    if end_index == -1:
        print("ERROR: Ending index not found!")
        return None

    json_str = data[start_index:end_index].strip()
    json_str = json_str + "}}}"

    try:
        json_obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}")

    return json_obj

def getShowTimesForTheatreCode(theatreCode, jsonObj):
    #print(jsonObj["showtimesByEvent"]["showDates"])
    if jsonObj is None or jsonObj["showtimesByEvent"]["showDates"] is None or jsonObj["showtimesByEvent"]["showDates"].get("20250814") is None:
        return []
    showTimeWidgets = jsonObj["showtimesByEvent"]["showDates"]["20250814"]["dynamic"]["data"]["showtimeWidgets"]
    result = next((item for item in showTimeWidgets if item.get('type') == 'groupList'), None)
    data = result['data'][0]['data']
    theatre = next((item for item in data if item['additionalData']['venueCode'] == theatreCode), None)
    if theatre is None:
        return []
    showTimes = [item.get('title') for item in theatre['showtimes']]
    return showTimes

if __name__ == "__main__":
    loop = 1
    while True:
        print("Loop count: "+str(loop))
        url = "https://in.bookmyshow.com/movies/chennai/coolie/buytickets/ET00395817/20250814"
        start_marker = "window.__INITIAL_STATE__ = "
        end_marker = """}}}</script><script>"""
        theatreCodeList = ["TVHP"]
        json_obj = get_json_from_text(url, start_marker, end_marker)
        if json_obj is None:
            continue
        for theatreCode in theatreCodeList:
            timingList = getShowTimesForTheatreCode(theatreCode, json_obj)
            print(f"Found {timingList} for {theatreCode}")
            for timing in timingList:
                if 8 < int(timing[:2]) < 12 and timing[-2:] == "AM":
                    print("Found "+timing+" in "+theatreCode)
                    response = requests.post(whatsappUrl, headers=headers, json=payload)
                    print("Status code:", response.status_code)
                    winsound.Beep(1000, 50000)
                break
        loop += 1
        time.sleep(1)



# INPR - INOX Luxe Phoenix
# MAYJ - Mayajaal
# CBMC - Cinepolis
# TVHP - Vijay Park
# INTO - Marina Mall
# ACON - AGS Navalur
