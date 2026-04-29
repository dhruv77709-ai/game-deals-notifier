import requests
import time
import os
import resend

# ================== CONFIG ==================
resend.api_key = os.getenv("RESEND_API_KEY")

CHECK_INTERVAL = 3600  # 1 hour

# Optional: keep list (used for reference/logging only)
STEAM_GAMES = {
    "Resident Evil 2": 883710,
    "Resident Evil 3": 952060,
    "Resident Evil 7": 418370
}
# ============================================


def send_email(subject, message):
    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": ["dhruv77709@gmail.com"],
            "subject": subject,
            "html": f"<p>{message}</p>"
        })
    except Exception as e:
        print("Email error:", e)


# -------- EPIC FREE GAMES --------
def check_epic():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    data = requests.get(url).json()

    free_games = []

    for game in data['data']['Catalog']['searchStore']['elements']:
        title = game.get('title')
        promos = game.get('promotions')

        if promos and promos.get('promotionalOffers'):
            free_games.append(title)

    return free_games


# -------- STEAM FIXED VERSION (WORKING) --------
def check_steam():
    deals = []

    try:
        url = "https://store.steampowered.com/api/featuredcategories/?l=english"
        data = requests.get(url, timeout=10).json()

        specials = data.get("specials", {}).get("items", [])

        for game in specials:
            name = game.get("name")
            discount = game.get("discount_percent", 0)
            final_price = game.get("final_price", 0) / 100

            if discount > 0:
                deals.append(f"{name} is {discount}% OFF - ₹{final_price}")

    except Exception as e:
        print("Steam fetch error:", e)

    return deals


# -------- MAIN LOOP --------
def main():
    print("App started...")

    seen_epic = set()
    seen_steam = set()

    while True:
        try:
            # EPIC
            epic_games = check_epic()
            for game in epic_games:
                if game not in seen_epic:
                    send_email("Free Game Alert (Epic)", f"Free on Epic: {game}")
                    seen_epic.add(game)

            # STEAM
            steam_deals = check_steam()
            for deal in steam_deals:
                if deal not in seen_steam:
                    send_email("Steam Deal Alert", deal)
                    seen_steam.add(deal)

        except Exception as e:
            print("Main loop error:", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
