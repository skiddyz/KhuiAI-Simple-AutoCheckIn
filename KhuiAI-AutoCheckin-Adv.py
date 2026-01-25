from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os
import sys

# ==============================
# LOAD CONFIG
# ==============================
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

SITE_URL = config.get("site_url")
CHECKIN_API = config.get("checkin_api")
EMAIL = config.get("email", "").strip()
PASSWORD = config.get("password", "").strip()

PROFILE_DIR = "profile"

# ==============================
def log(msg):
    print(msg, flush=True)

# ==============================
def check_email_verification_block(page):
    keywords = [
        "กรุณายืนยันอีเมล",
        "ส่งอีเมลยืนยันอีกครั้ง",
        "ยืนยันอีเมล"
    ]

    for text in keywords:
        if page.locator(f"text={text}").count() > 0:
            log("❌ แอคเคาน์นี้ยังไม่ได้ยืนยันตัวตน")
            log("👉 กรุณายืนยันอีเมลก่อนใช้งานระบบอัตโนมัติ")
            return True
    return False

# ==============================
def auto_checkin():
    print("=" * 70)
    print("🤖 KHUI AI AUTO CHECK-IN | Vibe Coded by flukkieboyy x chatgpt")
    print("🕒", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 70)

    if not EMAIL or not PASSWORD:
        log("❌ กรุณาใส่ email และ password ใน config.json")
        sys.exit(1)

    os.makedirs(PROFILE_DIR, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False
        )

        page = context.new_page()

        # ==============================
        # OPEN WEBSITE
        # ==============================
        log("🌐 Opening website...")
        page.goto(SITE_URL, wait_until="load")
        page.wait_for_timeout(3000)

        # ==============================
        # HANDLE COUNTRY / LANGUAGE
        # ==============================
        log("🌍 Checking country selector...")
        try:
            if page.locator("text=Thailand").count() > 0:
                page.click("text=Thailand")
                page.wait_for_timeout(2000)
                log("✅ Country selected automatically")
            else:
                log("✅ Country already selected")
        except:
            log("⚠️ Country selector skipped")

        # ==============================
        # OPEN LOGIN POPUP
        # ==============================
        if page.locator("text=เข้าสู่ระบบ").count() > 0:
            log("🔐 Opening login popup...")
            page.locator("text=เข้าสู่ระบบ").first.click()
            page.wait_for_timeout(3000)
        else:
            log("✅ Already logged in (session exists)")

        # ==============================
        # AUTO LOGIN
        # ==============================
        if page.locator("input[type='email']").count() > 0:
            log("✍️ Filling login form automatically...")
            page.fill("input[type='email']", EMAIL)
            page.fill("input[type='password']", PASSWORD)
            page.click("button[type='submit']")
            page.wait_for_timeout(6000)

            # CHECK EMAIL VERIFICATION
            if check_email_verification_block(page):
                context.close()
                log("🛑 Process stopped")
                return

            log("✅ Login submitted successfully")
        else:
            log("✅ Already logged in (session exists)")

        # ==============================
        # CLOSE PROMO POPUP IF EXISTS
        # ==============================
        log("🎁 Checking promo popup...")
        log("🎁 Checking promo popup...")

        try:
            # ปุ่ม X
            if page.locator("button[aria-label='Close']").count() > 0:
                page.locator("button[aria-label='Close']").click()
                page.wait_for_timeout(1000)
                log("✅ Promo popup closed (X)")

            # ปุ่ม "ไว้ทีหลัง"
            elif page.get_by_role("button", name="ไว้ทีหลัง").count() > 0:
                page.get_by_role("button", name="ไว้ทีหลัง").click()
                page.wait_for_timeout(1000)
                log("✅ Promo popup closed (Later)")

            else:
                log("✅ No promo popup")

        except Exception as e:
            log(f"⚠️ Popup handling failed: {e}")


        # ==============================
        # GO TO CHECK-IN PAGE
        # ==============================
        log("➡️ Opening check-in page...")
        page.goto("https://www.khuiai.com/th/daily-check-in", wait_until="load")
        page.wait_for_timeout(4000)

        # ==============================
        # CLAIM REWARD
        # ==============================
        if page.locator("text=รับรางวัลไปแล้ว").count() > 0:
            log("🎁 คุณได้เช็คอินไปแล้ววันนี้")
            log("👉 กรุณารอวันพรุ่งนี้")
        elif page.locator("text=รับรางวัล").count() > 0:
            log("🎁 Claiming daily reward...")
            page.locator("text=รับรางวัล").first.click()
            page.wait_for_timeout(3000)
            log("🎉 CHECK-IN SUCCESSFUL!")
        else:
            log("❌ ไม่พบปุ่มรับรางวัล (อาจหน้าเปลี่ยนหรือยังไม่ login)")


        page.wait_for_timeout(3000)
        context.close()

    print("=" * 70)
    log("🛑 Finished")

# ==============================
if __name__ == "__main__":
    auto_checkin()

print("-" * 70)
input("กด Enter เพื่อปิดโปรแกรม...")
