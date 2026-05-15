import os
import pandas as pd
from playwright.sync_api import sync_playwright
from groq import Groq

def scrape_data():
    """Mengekstrak data dari laman web secara langsung"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Laman Web Sasaran
        page.goto("http://books.toscrape.com/")
        
        titles = page.locator("h3 a").all_inner_texts()
        prices = page.locator(".price_color").all_inner_texts()
        
        data = []
        # Ambil 10 item teratas
        for i in range(min(10, len(titles))):
            data.append({
                "Nama Produk": titles[i],
                "Harga": prices[i].replace("Â", ""),
            })
            
        df = pd.DataFrame(data)
        df.to_csv("data_buku_besar.csv", index=False)
        browser.close()
        return data

def analyze_with_ai(data):
    """Menghantar data yang diekstrak ke Llama 3.1 untuk analisis perniagaan"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Ralat: Sila masukkan Kunci API dalam Streamlit Secrets."

    client = Groq(api_key=api_key)
    
    # Prompt dalam Bahasa Melayu untuk hasil profesional
    prompt = f"""
    Anda adalah Pakar Analisis Data Pasaran profesional. 
    Analisis data harga produk ini: {str(data)}
    
    Sila berikan:
    1. Kenal pasti produk paling mahal dan paling murah.
    2. Analisis ringkas trend harga (Wawasan Perniagaan).
    3. Cadangan strategi untuk peruncit.
    
    Gunakan format Markdown dengan emoji untuk paparan yang kemas dan profesional.
    Tulis sepenuhnya dalam Bahasa Melayu.
    """
    
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-70b-versatile",
    )
    
    result = chat.choices[0].message.content
    with open("laporan_ai.txt", "w", encoding="utf-8") as f:
        f.write(result)
    return result

def run_all():
    """Aliran pelaksanaan utama"""
    scraped_data = scrape_data()
    analyze_with_ai(scraped_data)