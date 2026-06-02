import requests
import os
from dotenv import load_dotenv

# تحميل مفاتيح الأمان من ملف .env
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
SPRINGER_KEY = os.getenv("SPRINGER_API_KEY")

def search_google_scholar(query):
    """البحث في جوجل سكالر وجلب المراجع والعناوين الروابط"""
    if not SERPAPI_KEY:
        return {"error": "مفتاح SerpApi غير متاح"}
        
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        results = response.json()
        
        # استخراج الأبحاث المستهدفة
        articles = []
        for item in results.get("organic_results", [])[:5]: # جلب أهم 5 أبحاث
            articles.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"), # الملخص البسيط
                "citations": item.get("inline_links", {}).get("cited_by", {}).get("total", 0)
            })
        return articles
    except Exception as e:
        return {"error": str(e)}

def search_springer(query):
    """البحث في قاعدة بيانات Springer & Nature الأكاديمية"""
    if not SPRINGER_KEY:
        return {"error": "مفتاح Springer API غير متاح"}
        
    # رابط البحث في قاعدة بيانات Springer المفتوحة
    url = f"http://api.springernature.com/meta/v1/json"
    params = {
        "q": query,
        "api_key": SPRINGER_KEY,
        "p": 5 # جلب أول 5 أبحاث
    }
    
    try:
        response = requests.get(url, params=params)
        results = response.json()
        
        articles = []
        for item in results.get("records", []):
            articles.append({
                "title": item.get("title"),
                "link": item.get("url", [{}])[0].get("value") if item.get("url") else "",
                "abstract": item.get("abstract", "No abstract available"),
                "publisher": item.get("publisherName")
            })
        return articles
    except Exception as e:
        return {"error": str(e)}
