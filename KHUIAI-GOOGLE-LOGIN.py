from playwright.sync_api import sync_playwright
from datetime import datetime
import os

SITE_URL = "https://www.khuiai.com/"
CHECKIN_URL = "https://www.khuiai.com/th/daily-check-in"
PROFILE = "profile-google"

def log(msg):
    print(msg, flush=True)

def is_logged_in(page):
    return page.locator("text=เข้าสู่ระบบ").count() == 0 and page.locator("text=Login").count() == 0

def wait_until_logged_in(page):
    log("⏳ กำลังรอให้ Google login เสร็จ...")
    for _ in range(120):
        if is_logged_in(page):
            log("✅ ตรวจพบว่า login สำเร็จแล้ว")
            return True
        page.wait_for_timeout(1000)
    return False

def auto_checkin_google():
    print("="*70)
    print("🤖 [Google-Login] KHUI AI AUTO CHECK-IN | Vibe Coded by flukkieboyy x chatgpt")
    print("🕒", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("="*70)

    os.makedirs(PROFILE, exist_ok=True)

    with sync_playwright() as p:
        while True:
            context = p.chromium.launch_persistent_context(
                PROFILE,
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )

            page = context.new_page()
            log("🌐 เปิดเว็บไซต์ KhuiAI...")
            page.goto(SITE_URL, wait_until="load")
            page.wait_for_timeout(4000)

            # 🌍 เลือกประเทศ
            try:
                if page.locator("text=Thailand").count() > 0:
                    page.locator("text=Thailand").first.click()
                    page.wait_for_timeout(2000)
            except:
                pass

            # 🔐 ยังไม่ login → เปิด Google Login
            if not is_logged_in(page):
                log("🔐 ยังไม่ได้ login – เปิดหน้าล็อกอิน")

                if page.locator("text=เข้าสู่ระบบ").count() > 0:
                    page.locator("text=เข้าสู่ระบบ").first.click()
                else:
                    page.locator("text=Login").first.click()

                page.wait_for_timeout(3000)

                if page.locator("text=Login with Google").count() > 0 or page.locator("text=เข้าสู่ระบบด้วย Google").count() > 0:
                    log("🔑 กดปุ่ม Login with Google")

                    if page.locator("text=Login with Google").count() > 0:
                        page.locator("text=Login with Google").first.click()
                    else:
                        page.locator("text=เข้าสู่ระบบด้วย Google").first.click()

                    if wait_until_logged_in(page):
                        log("🔄 รีสตาร์ทเบราว์เซอร์เพื่อใช้ session")
                        context.close()
                        continue
                    else:
                        log("❌ Login ไม่สำเร็จ")
                        context.close()
                        return
                else:
                    log("❌ ไม่พบปุ่ม Login with Google")
                    context.close()
                    return

            # ======================
            # LOGIN แล้ว → เช็คอิน
            # ======================
            log("✅ ล็อกอินด้วย Google สำเร็จ")

            # ปิด popup
            try:
                if page.locator("text=ไว้ทีหลัง").count() > 0:
                    page.locator("text=ไว้ทีหลัง").first.click()
                elif page.locator("button:has-text('×')").count() > 0:
                    page.locator("button:has-text('×')").first.click()
            except:
                pass

            log("➡️ เปิดหน้าเช็คอิน...")
            page.goto(CHECKIN_URL, wait_until="load")
            page.wait_for_timeout(4000)

            if page.locator("text=รับรางวัลไปแล้ว").count() > 0:
                log("🎁 คุณกดรับรางวัลไปแล้ว")
                log("👉 กรุณารอใหม่วันพรุ่งนี้")
            elif page.locator("text=รับรางวัล").count() > 0:
                log("🎁 กำลังกดรับรางวัล...")
                page.locator("text=รับรางวัล").first.click()
                page.wait_for_timeout(3000)
                log("🎉 เช็คอินสำเร็จ!")
            else:
                log("❌ ไม่พบปุ่มรับรางวัล")

            print("="*70)
            input("กด Enter เพื่อปิดโปรแกรม...")
            context.close()
            break

if __name__ == "__main__":
    auto_checkin_google()
