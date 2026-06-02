import streamlit as st
import requests
import docx
from io import BytesIO
import os
from dotenv import load_dotenv

# تفريغ الذاكرة المؤقتة وجلب المفاتيح البيئية
load_dotenv()

# جلب المفاتيح الصافية وتنظيفها من علامات التنصيص
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip().replace('"', '').replace("'", "")
GEMINI_KEY = os.getenv("GEMINI_KEY", "").strip().replace('"', '').replace("'", "")

# إعدادات واجهة المستخدم الرسومية لـ RESEARCH-MAKER
st.set_page_config(page_title="RESEARCH-MAKER", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>النظام الأكاديمي الذكي للبحث التلقائي وصياغة البحوث بـ Gemini و SerpApi</h4>", unsafe_allow_html=True)
st.write("---")

def fetch_google_scholar(query):
    """جلب وتصفية الأبحاث والمراجع الأكاديمية عبر SerpApi"""
    if not SERPAPI_KEY:
        return []
    
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        results = response.json().get("organic_results", [])
        
        filtered_papers = []
        for item in results[:5]:  # سحب أفضل 5 مراجع علمية
            filtered_papers.append({
                "title": item.get("title", "No Title"),
                "snippet": item.get("snippet", "No abstract available."),
                "link": item.get("link", "#"),
                "authors": item.get("publication_info", {}).get("summary", "Unknown Authors")
            })
        return filtered_papers
    except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال بمحرك SerpApi: {e}")
        return []

def generate_research_with_gemini(title, context_papers, lang, style):
    """صياغة البحث العلمي الأكاديمي الموثق باستخدام نموذج Gemini 1.5 Flash"""
    if not GEMINI_KEY:
        return "خطأ: لم يتم إضافة مفتاح Gemini API بشكل صحيح في ملف البيئة."
        
    # تنظيم الأبحاث المجلوبة كخلفية علمية للـ Prompt
    papers_text = ""
    for idx, p in enumerate(context_papers):
        papers_text += f"\n[Paper {idx+1}] Title: {p['title']}\nAuthors/Source: {p['authors']}\nSummary: {p['snippet']}\n"
        
    prompt = f"""
    You are an expert academic researcher. Write a comprehensive, high-quality, and professional scientific research paper based on the following topic and background literature.
    
    Topic: {title}
    Target Language: {lang}
    Citation Style: {style}
    
    Literature Background (Source Material):
    {papers_text}
    
    Requirements & Structure:
    1. Introduction: Write a highly detailed introduction providing global context, significance, and in-text citations matching the papers provided (e.g., [1] or (Author, Year) depending on {style}).
    2. Literature Review & Methodology Discussion: Synthesize the background information professionally.
    3. Results and Discussion: Expand on the surface points with academic arguments.
    4. Conclusion: Summarize the final insights.
    5. References: Create a formal references list structured according to {style} formatting guidelines using the source material provided.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in result:
            return f"خطأ من سيرفر جوجل (API Error): {result['error'].get('message', 'تفاصيل غير معروفة')}"
        else:
            return f"استجابة غير متوقعة من السيرفر. تفاصيل: {result}"
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بذكاء Gemini: {e}"

def create_word_document(text, title):
    """تحويل النص الأكاديمي المولد إلى ملف Word (.docx) منسق تلقائياً"""
    doc = docx.Document()
    doc.add_heading(title, level=0)
    
    lines = text.split("\n")
    for line in lines:
        # تنظيف علامات العناوين والنصوص العريضة في ماركداون
        clean_line = line.replace("**", "").replace("###", "").replace("##", "").strip()
        
        if line.strip().startswith("1.") or "Introduction" in line or "Results" in line or "References" in line or "Conclusion" in line:
            doc.add_heading(clean_line, level=1)
        elif line.strip(): 
            doc.add_paragraph(clean_line)
            
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# بناء عناصر واجهة المستخدم المستقرة
research_title = st.text_input("📝 أدخل عنوان البحث العلمي المطلوب صياغته:")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 لغة الصياغة الأكاديمية:", ["English", "العربية"])
with col2:
    citation_style = st.selectbox("📚 نظام توثيق المراجع الدولي:", ["APA", "IEEE", "Harvard"])

if st.button("🚀 ابدأ البحث التلقائي وصياغة البحث"):
    if research_title:
        if not SERPAPI_KEY or not GEMINI_KEY:
            st.error("🛑 يرجى التحقق من وجود مفاتيح (SerpApi و Gemini) داخل ملف الـ .env وحفظ الملف أولاً.")
        else:
            with st.spinner("🔄 جاري فحص Google Scholar وسحب المصادر الأكاديمية عبر محرك البحث المدمج..."):
                all_papers = fetch_google_scholar(research_title)
                
            if all_papers:
                st.success(f"✅ تم العثور على {len(all_papers)} مراجع علمية وتصفيتها بنجاح! جاري الصياغة الآن...")
                
                # عرض المراجع المجلوبة في الواجهة للشفافية والأمان
                with st.expander("🔗 استعراض المراجع العلمية المعتمدة في الصياغة"):
                    for i, paper in enumerate(all_papers):
                        st.markdown(f"**[{i+1}] {paper['title']}**")
                        st.caption(f"المؤلفون والمصدر: {paper['authors']}")
                        st.write(paper['snippet'])
                        st.markdown(f"[رابط المصدر]({paper['link']})")
                        st.write("---")
                
                with st.spinner("🧠 يقوم نظام Gemini الآن بتحليل البيانات وكتابة أقسام البحث وتوثيق الهوامش..."):
                    generated_text = generate_research_with_gemini(research_title, all_papers, language, citation_style)
                    
                st.subheader("📄 معاينة مسودة البحث العلمي المولد:")
                st.text_area("النص الكامل للبحث", generated_text, height=400)
                
                # فحص نجاح توليد النص قبل توفير زر التحميل
                if "خطأ" not in generated_text and "Error" not in generated_text:
                    st.balloons()
                    word_file = create_word_document(generated_text, research_title)
                    st.download_button(
                        label="📥 تحميل البحث العلمي الأكاديمي المنسق كاملاً بصيغة ملف Word (.docx)",
                        data=word_file,
                        file_name=f"{research_title.replace(' ', '_')}_Research.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            else:
                st.warning("تعذر العثور على مراجع كافية في Google Scholar لهذه الكلمات المفتاحية، يرجى تجربة صياغة أخرى للعنوان.")
    else:
        st.error("الرجاء كتابة عنوان البحث العلمي أولاً.")
