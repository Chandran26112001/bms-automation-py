import requests
import json
import cloudscraper
import time
import winsound
import asyncio

from telethon import TelegramClient, errors

tele_api_id = 10048584
tele_api_hash = "57155257e08449b92f3e9372021e4399"

RECIPIENTS = [
    '+916380998663',
    '+919688911442',
    '+919080597620',
    '+919361330948'
]

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
    if jsonObj is None or jsonObj["showtimesByEvent"]["showDates"] is None or jsonObj["showtimesByEvent"]["showDates"].get("20260106") is None:
        return []
    showTimeWidgets = jsonObj["showtimesByEvent"]["showDates"]["20260106"]["dynamic"]["data"]["showtimeWidgets"]
    result = next((item for item in showTimeWidgets if item.get('type') == 'groupList'), None)
    data = result['data'][0]['data']
    theatre = next((item for item in data if item['additionalData']['venueCode'] == theatreCode), None)
    if theatre is None:
        return []
    showTimes = [item.get('title') for item in theatre['showtimes']]
    return showTimes

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": "ad8cfuv7v5v3ivekv99aooizirezbv",
            "user": "uh7hzgek2n6yyt3v6a79pi9t5mgvay",
            "message": text,
        }
    )

async def sendTeleMessage(url):
    # Create the client and connect
    client = TelegramClient("SESSION_NAME", tele_api_id, tele_api_hash)
    await client.start()
    print(f"Logged in as: {(await client.get_me()).first_name}")
    for user in RECIPIENTS:
        try:
            print(f"Sending to {user}...")
            await client.send_message(user, "BOSS KESARI READY!!! Link: "+url)
            print(f"✅ Sent to {user}")
            await asyncio.sleep(2)

        except errors.FloodWaitError as e:
            print(f"⚠️ Rate limited. Must wait {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
        except ValueError:
            print(f"❌ Could not find user: {user}")
        except Exception as e:
            print(f"❌ Error sending to {user}: {e}")

    await client.disconnect()

async def main():
    client = TelegramClient("SESSION_NAME", tele_api_id, tele_api_hash)
    await client.start()
    print(f"Logged in as: {(await client.get_me()).first_name}")
    loop = 1
    try:
        while True:
            print("Loop count: " + str(loop))
            url = "https://in.bookmyshow.com/movies/chennai/45/buytickets/ET00440377/20260106"
            start_marker = "window.__INITIAL_STATE__ = "
            end_marker = "}}}</script><script>"
            theatreCodeList = ["TVHP", "INPR", "MAYJ", "CBMC", "TVHP", "INTO", "ACON", "MCSK"]
            json_obj = get_json_from_text(url, start_marker, end_marker)
            print(json_obj)
            if json_obj is None:
                continue
            for theatreCode in theatreCodeList:
                timingList = getShowTimesForTheatreCode(theatreCode, json_obj)
                print(f"Found {timingList} for {theatreCode}")
                for timing in timingList:
                    print(timing)
                    if 8 < int(timing[:2]) < 12 and timing[-2:] == "AM":
                        print("Found " + timing + " in " + theatreCode)
                        push("Project Kesari Initiated. Link: " + url)
                        for user in RECIPIENTS:
                            try:
                                print(f"Sending to {user}...")
                                await client.send_message(user, "BOSS KESARI READY!!! Link: " + url)
                                print(f"✅ Sent to {user}")
                            except Exception as e:
                                print(f"❌ Error sending to {user}: {e}")
                        winsound.Beep(1000, 50000)
                    break
            loop += 1
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())



# INPR - INOX Luxe Phoenix
# MAYJ - Mayajaal
# CBMC - Cinepolis
# TVHP - Vijay Park
# INTO - Marina Mall
# ACON - AGS Navalur
# MCSK - Miraj