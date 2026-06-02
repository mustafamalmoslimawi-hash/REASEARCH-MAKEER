import streamlit as st
import requests
import docx
from io import BytesIO

# إعدادات واجهة المستخدم الرسومية للموقع
st.set_page_config(page_title="RESEARCH-MAKER", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>النظام الأكاديمي الذكي للبحث التلقائي وصياغة البحوث بـ Gemini المجاني</h4>", unsafe_allow_html=True)
st.write("---")

# 🔑 ضع مفاتيحك الخاصة هنا بين علامات التنصيص
SERPAPI_KEY = "3333539fe58445aebe1e4c9ae5d105d12e12160121f8beb93d8ff6bbd657c515"
GEMINI_KEY = "AQ.Ab8RN6K2P_mXtgZ34-iJR8z3TARBk6mAcvwe51IIz9280y9DlA"

def fetch_google_scholar(query):
    """جلب الأبحاث والمراجع من جوجل سكالر"""
    if not SERPAPI_KEY or "ضع_مفتاح" in SERPAPI_KEY: return []
    url = "https://serpapi.com/search"
    params = {"engine": "google_scholar", "q": query, "hl": "en", "api_key": SERPAPI_KEY}
    try:
        response = requests.get(url, params=params)
        return [{
            "title": item.get("title", "No Title"),
            "snippet": item.get("snippet", "No abstract available."),
            "link": item.get("link", "#")
        } for item in response.json().get("organic_results", [])[:5]] # جلب أفضل 5 أبحاث
    except: return []

def generate_research_with_gemini(title, context_papers, lang, style):
    """صياغة البحث باستخدام Google Gemini API بناءً على نتائج مراجع جوجل"""
    if not GEMINI_KEY or "ضع_مفتاح" in GEMINI_KEY:
        return "خطأ: لم يتم إضافة مفتاح Gemini API بشكل صحيح."
        
    papers_text = ""
    for idx, p in enumerate(context_papers):
        papers_text += f"\n[Paper {idx+1}] Title: {p['title']}\nSummary: {p['snippet']}\n"
        
    prompt = f"""
    You are an expert academic researcher. Write a professional scientific research paper based on the following topic and background papers.
    Topic: {title}
    Target Language: {lang}
    Citation Style: {style}
    
    Literature Background:
    {papers_text}
    
    Requirements:
    1. Write a comprehensive 'Introduction' section with in-text citations like [1], [2] to cite the background papers.
    2. Write a detailed 'Results and Discussion' section.
    3. Include a formal 'References' section matching {style} style.
    """
    
    # رابط استدعاء نموذج Gemini 1.5 Flash السريع والمجاني لإنتاج النصوص
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/vnd.google.protobuf"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"حدث خطأ أثناء الصياغة بذكاء Gemini: {e}"

def create_word_document(text, title):
    """تحويل النص المولد إلى ملف Word قابل للتعديل والطباعة"""
    doc = docx.Document()
    doc.add_heading(title, level=0)
    lines = text.split("\n")
    for line in lines:
        clean_line = line.replace("**", "").replace("###", "").replace("##", "").strip()
        if line.strip().startswith("1.") or "Introduction" in line or "Results" in line or "References" in line:
            doc.add_heading(clean_line, level=1)
        elif line.strip(): 
            doc.add_paragraph(clean_line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# بناء الواجهة
research_title = st.text_input("📝 أدخل عنوان البحث العلمي المطلوب صياغته:")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 لغة الصياغة الأكاديمية:", ["English", "العربية"])
with col2:
    citation_style = st.selectbox("📚 نظام توثيق المراجع الدولي:", ["APA", "IEEE", "Harvard"])

if st.button("🚀 ابدأ البحث التلقائي وصياغة البحث"):
    if research_title:
        if "ضع_مفتاح" in SERPAPI_KEY or "ضع_مفتاح" in GEMINI_KEY:
            st.error("🛑 يرجى تزويد الكود بمفاتيحك (SerpApi و Gemini) لكي يعمل النظام.")
        else:
            with st.spinner("🔄 jari فحص Google Scholar وسحب المراجع العلمية الموثقة..."):
                all_papers = fetch_google_scholar(research_title)
                
            if all_papers:
                st.success(f"✅ تم جمع {len(all_papers)} مراجع علمية بنجاح! جاري الصياغة الآن عبر سيرفرات Gemini...")
                with st.spinner("🧠 يقوم عقل Gemini الاصطناعي بكتابة الأقسام وتنسيق الهوامش الأكاديمية..."):
                    generated_text = generate_research_with_gemini(research_title, all_papers, language, citation_style)
                    
                st.balloons()
                st.subheader("📄 معاينة البحث العلمي المولد:")
                st.text_area("نص البحث الكامل", generated_text, height=400)
                
                word_file = create_word_document(generated_text, research_title)
                st.download_button(
                    label="📥 تحميل البحث العلمي الجاهز بصيغة ملف Word (.docx)",
                    data=word_file,
                    file_name=f"{research_title.replace(' ', '_')}_Research.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.warning("تعذر العثور على أبحاث، حاول تغيير الكلمات المفتاحية.")
    else:
        st.error("الرجاء كتابة عنوان البحث أولاً.")
