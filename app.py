import requests
import time
import smtplib
from email.mime.text import MIMEText

# ================== CONFIG ==================
EMAIL_ADDRESS = "dhruv77709@gmail.com"
EMAIL_PASSWORD = "oypu lnxa hrfc jhwn"
RECEIVER_EMAIL = "dhruv77709@gmail.com"

CHECK_INTERVAL = 3600  # 1 hour

STEAM_GAMES = {
    "Resident Evil 2": 883710,
    "Resident Evil 3": 952060,
    "Resident Evil 7": 418370
}
# ============================================


def send_email(subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("Email error:", e)


def check_epic():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    data = requests.get(url).json()

    free_games = []

    for game in data['data']['Catalog']['searchStore']['elements']:
        title = game['title']
        promos = game.get('promotions')

        if promos and promos.get('promotionalOffers'):
            free_games.append(title)

    return free_games


def check_steam():
    deals = []

    for name, app_id in STEAM_GAMES.items():
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        data = requests.get(url).json()

        if data[str(app_id)]['success']:
            info = data[str(app_id)]['data']

            if info.get('is_free'):
                deals.append(f"{name} is FREE on Steam!")
            elif 'price_overview' in info:
                price = info['price_overview']
                discount = price.get('discount_percent', 0)

                if discount > 0:
                    deals.append(f"{name} is {discount}% OFF!")

    return deals


def main():
    print("App started...")
    send_email("TEST", "It works!")
    seen_epic = set()
    seen_steam = set()

    while True:
        try:
            epic_games = check_epic()
            for game in epic_games:
                if game not in seen_epic:
                    send_email("Free Game Alert!", f"Free on Epic: {game}")
                    seen_epic.add(game)

            steam_deals = check_steam()
            for deal in steam_deals:
                if deal not in seen_steam:
                    send_email("Steam Deal Alert!", deal)
                    seen_steam.add(deal)

        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
