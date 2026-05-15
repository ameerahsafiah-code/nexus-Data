import os
import subprocess
import pandas as pd
from playwright.sync_api import sync_playwright
from groq import Groq

def install_dependencies():
    """Memaksa pemasangan semua dependencies Linux dan browser di server"""
    try:
        # 1. Pasang browser Chromium
        subprocess.run(["playwright", "install", "chromium"], check=True)
        # 2. Pasang sistem dependencies (libglib, dll) secara paksa
        subprocess.run(["playwright", "install-deps", "chromium"], check=True)
    except Exception as e:
        print(f"Nota Pemasangan: {e}")

def scrape_data():
    # Panggil fungsi install setiap kali untuk pastikan ia wujud
    install_dependencies()
    
    with sync_playwright() as p:
        # Gunakan argumen tambahan untuk mengelakkan ralat sandbox di Linux
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
        
        try:
            page.goto("http://books.toscrape.com/", timeout=60000)
            titles = page.locator("h3 a").all_inner_texts()
            prices = page.locator(".price_color").all_inner_texts()
            
            data = []
            for i in range(min(10, len(titles))):
                data.append({
                    "Nama Produk": titles[i],
                    "Harga": prices[i].replace("Â", ""),
                })
                
            df = pd.DataFrame(data)
            df.to_csv("data_buku_besar.csv", index=False)
            return data
        except Exception as e:
            print(f"Ralat Scraping: {e}")
            return []
        finally:
            browser.close()

def analyze_with_ai(data):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "API Key tidak dijumpai."

    client = Groq(api_key=api_key)
    prompt = f"Analisis data harga produk ini dalam Bahasa Melayu: {str(data)}. Berikan produk termahal, termurah dan cadangan perniagaan."
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-70b-versatile",
        )
        result = chat.choices[0].message.content
        with open("laporan_ai.txt", "w", encoding="utf-8") as f:
            f.write(result)
        return result
    except Exception as e:
        return f"Ralat AI: {e}"

def run_all():
    data = scrape_data()
    if data:
        analyze_with_ai(data)