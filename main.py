import os
import uuid
import base64
import random
import requests
import httpx
from os import system as sm
from sys import platform as pf
from time import sleep as sp
from urllib.parse import urlparse, parse_qs
from rich import print as rp
from rich.panel import Panel as pan
from dotenv import load_dotenv
load_dotenv()

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")


# ─── Color Definitions ───────────────────────────────────────────────────────
R = "[bold red]"
G = "[bold green]"
Y = "[bold yellow]"
B = "[bold blue]"
M = "[bold magenta]"
C = "[bold cyan]"
W = "[bold white]"

TOKEN_FILE = os.path.join(os.getcwd(), "accesstoken.txt")

# ─── UI Functions ────────────────────────────────────────────────────────────
def randc():
    return random.choice([R, G, Y, B, M, C])

def logo():
    rp(pan(f"""{randc()}
  ______________________________
 /  _____/\\_   _____/\\__    ___/
/   \\  ___ |    __)_   |    |   
\\    \\_\\  \\|        \\  |    |   
 \\______  /_______  /  |____|   
        \\/        \\/""",
        title=f"{Y}FB TOKEN + REACT TOOL",
        subtitle=f"{R}BY GABO",
        border_style="bold purple"))

def clear():
    sm('cls' if pf in ['win32', 'win64'] else 'clear')
    logo()

# ─── Token Getter ────────────────────────────────────────────────────────────
def get_fb_token(email, password):
    base_access_token = '350685531728|62f8ce9f74b12f84c123cc23437a4a32'
    data = {
        'adid': str(uuid.uuid4()),
        'format': 'json',
        'device_id': str(uuid.uuid4()),
        'credentials_type': 'device_based_login_password',
        'email': email,
        'password': password,
        'access_token': base_access_token,
        'generate_session_cookies': '1',
        'method': 'auth.login'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        resp = httpx.post("https://b-graph.facebook.com/auth/login",
                          headers=headers, data=data, timeout=30)
        if resp.status_code == 200:
            res = resp.json()
            if 'access_token' in res:
                return res['access_token']
            elif 'error' in res:
                rp(f"{R}Error: {res['error']['message']}")
        else:
            rp(f"{R}Failed: HTTP code {resp.status_code}")
    except Exception as e:
        rp(f"{R}Connection Error: {e}")
    return None

def save_access_token(token):
    try:
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
    except Exception as e:
        rp(f"{R}Error saving token: {e}")

def read_access_token():
    try:
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except:
        return None

def token_getter_flow():
    clear()
    email = input(f"{C}Email/UID: {Y}")
    password = input(f"{C}Password: {Y}")
    token = get_fb_token(email, password)
    clear()
    if token:
        save_access_token(token)
        rp(pan(f"{G}Token obtained!", border_style="bold green"))
        rp(f"{C}{token}")
    else:
        rp(pan(f"{R}Failed to obtain token!", border_style="bold red"))
    input(f"{C}Press Enter to return...")

# ─── URL / ID Helpers ────────────────────────────────────────────────────────
def convert_post_link(url):
    try:
        p = urlparse(url)
        parts = p.path.split('/')
        if 'posts' in parts:
            i = parts.index('posts')
            return f"{parts[i-1]}_{parts[i+1]}"
        if 'story.php' in p.path:
            fbid = parse_qs(p.query).get('story_fbid', [None])[0]
            return f"{parts[1]}_{fbid}"
        return parts[-1]
    except:
        return None

def extract_comment_id_from_url(url):
    try:
        p = urlparse(url)
        eid = parse_qs(p.query).get('comment_id', [None])[0]
        dec = base64.b64decode(eid).decode()
        return dec.split("_")[-1]
    except:
        return None

# ─── Graph API Actions ──────────────────────────────────────────────────────
def react_to_post(token, post_id, reaction_type="LIKE"):
    try:
        url = f"https://graph.facebook.com/v19.0/{post_id}/reactions"
        res = requests.post(url, params={"type": reaction_type, "access_token": token})
        return res.json()
    except:
        return None

def react_to_comment(token, comment_id, reaction_type="LIKE"):
    try:
        url = f"https://graph.facebook.com/v19.0/{comment_id}/reactions"
        res = requests.post(url, params={"type": reaction_type, "access_token": token})
        return res.json()
    except:
        return None

# ─── Automation Flows ────────────────────────────────────────────────────────
def auto_post_reaction_flow():
    clear()
    token = read_access_token()
    if not token:
        rp(f"{R}No token found. Please get one first.")
        input("Press Enter...")
        return

    url = input(f"{C}Post URL: {Y}")
    rtype = input(f"{C}Reaction (LIKE/LOVE/HAHA/WOW/SAD/ANGRY): {Y}").upper()
    count = int(input(f"{C}How many times? {Y}"))

    pid = convert_post_link(url)
    if not pid:
        rp(f"{R}Invalid URL.")
        input("Enter to return...")
        return

    for _ in range(count):
        res = react_to_post(token, pid, rtype)
        if res and 'success' in res:
            rp(f"{G}Reacted!")
        else:
            rp(f"{R}Failed.")
        sp(1)
    input("Done. Enter to return...")

def auto_comment_reaction_flow():
    clear()
    token = read_access_token()
    if not token:
        rp(f"{R}No token found. Please get one first.")
        input("Press Enter...")
        return

    url = input(f"{C}Comment URL: {Y}")
    rtype = input(f"{C}Reaction (LIKE/LOVE/HAHA/WOW/SAD/ANGRY): {Y}").upper()
    count = int(input(f"{C}How many times? {Y}"))

    cid = extract_comment_id_from_url(url)
    if not cid:
        rp(f"{R}Invalid URL.")
        input("Enter to return...")
        return

    for _ in range(count):
        res = react_to_comment(token, cid, rtype)
        if res and 'success' in res:
            rp(f"{G}Reacted!")
        else:
            rp(f"{R}Failed.")
        sp(1)
    input("Done. Enter to return...")

# ─── Main Menu ───────────────────────────────────────────────────────────────
def main_menu():
    clear()
    rp(pan(f"""
{Y}[1]{G} Get Facebook Token
{Y}[2]{G} Auto Post Reaction
{Y}[3]{G} Auto Comment Reaction
{Y}[4]{R} Exit""", border_style="bold purple"))
    return input(f"{C}Choose option: {Y}")

if __name__ == "__main__":
    while True:
        opt = main_menu().strip()
        if opt == '1': token_getter_flow()
        elif opt == '2': auto_post_reaction_flow()
        elif opt == '3': auto_comment_reaction_flow()
        elif opt == '4':
            rp(f"{G}Exiting. Goodbye!")
            break
        else:
            rp(f"{R}Invalid option!")
            sp(1)
