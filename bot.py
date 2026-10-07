import random, time, requests, os
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

# YOUR LINK
TARGET_URL = "https://www.profitableratecpmnetwork.com/u6up40pk?key=2eb554d5d05ea1898b5d0421198ef398"
MAX_VIEWS = 100000

PROFILES = [
    {"e": "webkit", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "vp": {"width": 390, "height": 844}},
    {"e": "webkit", "ua": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "vp": {"width": 820, "height": 1180}},
    {"e": "chromium", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "vp": {"width": 412, "height": 915}},
    {"e": "chromium", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "vp": {"width": 1920, "height": 1080}},
    {"e": "firefox", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Gecko/20100101 Firefox/125.0", "vp": {"width": 1680, "height": 1050}}
]

def get_proxies():
    try:
        res = requests.get('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=json', timeout=10)
        return [p['proxy'] for p in res.json()['proxies'] if p['protocol'] in ['http', 'https']]
    except: return []

def run_view(proxy, profile, num):
    try:
        with sync_playwright() as p:
            browser = getattr(p, profile['e']).launch(headless=True)
            ctx = browser.new_context(user_agent=profile['ua'], viewport=profile['vp'], proxy={"server": f"http://{proxy}"})
            page = ctx.new_page()
            page.goto(TARGET_URL, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            page.mouse.wheel(0, random.randint(100, 800))
            page.wait_for_timeout(1000)
            browser.close()
            print(f"SUCCESS: View {num} completed using {profile['e']}.")
            return 1
    except Exception as e:
        print(f"Proxy {proxy} failed. Skipping.")
        return 0

def main():
    start_time = time.time()
    total = 0
    if os.path.exists("views.txt"):
        with open("views.txt", "r") as f:
            try: total = int(f.read().strip())
            except: total = 0
    print(f"Starting from {total} views...")

    while total < MAX_VIEWS:
        if time.time() - start_time > 21000:
            print("Time limit reached. Exiting for auto-restart...")
            break

        proxies = get_proxies()
        if len(proxies) < 10:
            time.sleep(10)
            continue

        shuffled = random.sample(PROFILES, len(PROFILES))
        used, tasks = set(), []
        for i in range(5):
            proxy = random.choice(proxies)
            while proxy in used:
                proxy = random.choice(proxies)
            used.add(proxy)
            tasks.append((proxy, shuffled[i % len(shuffled)], total + i + 1))

        with ThreadPoolExecutor(max_workers=5) as ex:
            total += sum(ex.map(lambda a: run_view(*a), tasks))

        with open("views.txt", "w") as f:
            f.write(str(total))
        print(f"Total Views So Far: {total}/{MAX_VIEWS}")

if __name__ == "__main__":
    main()
