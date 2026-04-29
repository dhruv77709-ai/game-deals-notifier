import requests
import time
import os
import resend

# ================== CONFIG ==================
resend.api_key = os.getenv("RESEND_API_KEY")

CHECK_INTERVAL = 3600  # 1 hour

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


# -------- STEAM DISCOUNTS (FIXED) --------
def check_steam():
    deals = []

    for name, app_id in STEAM_GAMES.items():
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            data = requests.get(url, timeout=10).json()

            game = data.get(str(app_id), {})
            if not game.get("success"):
                continue

            info = game.get("data", {})
            price = info.get("price_overview")

            if price:
                discount = price.get("discount_percent", 0)
                final_price = price.get("final", 0) / 100

                if discount > 0:
                    deals.append(f"{name} is {discount}% OFF - ₹{final_price}")

            # optional: free check
            if info.get("is_free"):
                deals.append(f"{name} is FREE on Steam!")

        except Exception as e:
            print(f"Steam error for {name}:", e)

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
