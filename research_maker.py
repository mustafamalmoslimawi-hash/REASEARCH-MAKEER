import streamlit as st
import requests
from openai import OpenAI
import docx
from io import BytesIO

# إعدادات واجهة المستخدم الرسومية للموقع
st.set_page_config(page_title="RESEARCH-MAKER", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>النظام الأكاديمي الذكي للبحث التلقائي وصياغة البحوث الجاهزة</h4>", unsafe_allow_html=True)
st.write("---")

# 🔑 ضع مفاتيحك هنا (مفتاح SerpApi ومفتاح OpenAI فقط)
SERPAPI_KEY = "ضع_مفتاح_serpapi_هنا"
OPENAI_KEY = "ضع_مفتاح_openai_هنا"

# تفعيل اتصال OpenAI
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY and "ضع_مفتاح" not in OPENAI_KEY else None

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

def generate_research_with_ai(title, context_papers, lang, style):
    """صياغة البحث بالذكاء الاصطناعي بناءً على نتائج مراجع جوجل"""
    if not client: return "خطأ: لم يتم إضافة مفتاح OpenAI API بشكل صحيح."
        
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
    1. Write an 'Introduction' section with in-text citations like [1], [2].
    2. Write a 'Results and Discussion' section.
    3. Include a formal 'References' section matching {style} style.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"حدث خطأ أثناء الصياغة بالذكاء الاصطناعي: {e}"

def create_word_document(text, title):
    """تحويل النص إلى ملف Word"""
    doc = docx.Document()
    doc.add_heading(title, level=0)
    lines = text.split("\n")
    for line in lines:
        if line.strip().startswith("1.") or line.strip().startswith("Introduction") or line.strip().startswith("Results") or line.strip().startswith("References"):
            doc.add_heading(line, level=1)
        elif line.strip(): doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# الواجهة
research_title = st.text_input("📝 أدخل عنوان البحث العلمي المطلوب صياغته:")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 لغة الصياغة الأكاديمية:", ["English", "العربية"])
with col2:
    citation_style = st.selectbox("📚 نظام توثيق المراجع الدولي:", ["APA", "IEEE", "Harvard"])

if st.button("🚀 ابدأ البحث التلقائي وصياغة البحث"):
    if research_title:
        if "ضع_مفتاح" in SERPAPI_KEY or "ضع_مفتاح" in OPENAI_KEY:
            st.error("🛑 يرجى تزويد الكود بمفاتيح (SerpApi و OpenAI) لكي يعمل النظام.")
        else:
            with st.spinner("🔄 جاري فحص Google Scholar وسحب المراجع العلمية..."):
                all_papers = fetch_google_scholar(research_title)
                
            if all_papers:
                st.success(f"✅ تم جمع {len(all_papers)} مراجع علمية موثقة! جاري الصياغة الآن...")
                with st.spinner("🧠 يقوم العقل الاصطناعي بكتابة الأقسام وتنسيق المراجع..."):
                    generated_text = generate_research_with_ai(research_title, all_papers, language, citation_style)
                    
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
