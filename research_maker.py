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

# إعدادات واجهة المستخدم الرسومية لـ RESEARCH-MAKER المطوّر
st.set_page_config(page_title="RESEARCH-MAKER PRO", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER PRO</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>النظام الأكاديمي المتقدم لتوليد البحوث المطولة (20 صفحة) وأكثر من 30 مصدراً علمياً</h4>", unsafe_allow_html=True)
st.write("---")

def fetch_extensive_google_scholar(query):
    """جلب مكثف لأكثر من 30 مرجعاً أكاديمياً عبر SerpApi باستخدام الترقيم التلقائي (Pagination)"""
    if not SERPAPI_KEY:
        return []
    
    all_filtered_papers = []
    # سنقوم بعمل 4 جولات سحب متتالية لجمع ما يقارب 35 إلى 40 مرجعاً علمياً
    for start_page in [0, 10, 20, 30]:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_scholar",
            "q": query,
            "hl": "en",
            "start": start_page,
            "api_key": SERPAPI_KEY
        }
        try:
            response = requests.get(url, params=params)
            results = response.json().get("organic_results", [])
            for item in results:
                all_filtered_papers.append({
                    "title": item.get("title", "No Title"),
                    "snippet": item.get("snippet", "No abstract available."),
                    "link": item.get("link", "#"),
                    "authors": item.get("publication_info", {}).get("summary", "Unknown Authors")
                })
        except:
            break # التوقف في حال حدوث أي انقطاع بالاتصال
            
    return all_filtered_papers[:35]  # الاحتفاظ بأفضل 35 مصدراً علمياً متميزاً

def generate_deep_academic_paper(title, context_papers, lang, style):
    """استدعاء عقل Gemini المتطور لصياغة كتابة أكاديمية ممتدة وشديدة التفصيل (تحاكي 20 صفحة)"""
    if not GEMINI_KEY:
        return "خطأ: لم يتم إضافة مفتاح Gemini API بشكل صحيح في ملف البيئة لتوليد البحث الطويل."
        
    # دمج الـ 35 مصدراً وبناء قاعدة بيانات ضخمة للذكاء الاصطناعي ليقتبس منها
    papers_text = ""
    for idx, p in enumerate(context_papers):
        papers_text += f"\n[Source {idx+1}] Title: {p['title']} | Authors: {p['authors']} | Data: {p['snippet']}\n"
        
    prompt = f"""
    You are a distinguished senior academic researcher and professor. Write an exhaustive, comprehensive, and deeply analyzed scientific research paper about the topic: '{title}'.
    The target output must simulate a massive 20-page monograph (approximately 6,000 to 8,000 words).
    
    Target Language: {lang}
    Citation Style: {style}
    
    You MUST strictly review, incorporate, and cite ALL the 35 academic sources provided below. Use exhaustive in-text citations throughout every paragraph (e.g., [1], [2], [3]... up to [35] depending on the text).
    
    Sources Database:
    {papers_text}
    
    Strict Structural Requirements to hit the 20-page depth:
    1. ABSTRACT & KEYWORDS: Detailed synthesis.
    2. CHAPTER 1: INTRODUCTION & BACKGROUND: Elaborate deeply on historical context, global significance, and problem statements (minimum 1,500 words).
    3. CHAPTER 2: EXTENSIVE LITERATURE REVIEW: Systematically compare, contrast, and synthesize all ideas from the 35 sources provided. Dive deep into conflicting perspectives.
    4. CHAPTER 3: METHODOLOGICAL FRAMEWORK & ANALYSIS: Expand heavily on mathematical, clinical, or social methodologies applicable to '{title}'.
    5. CHAPTER 4: RESULTS, DEEP DISCUSSION & IMPLICATIONS: Deduce comprehensive analytical insights, global impacts, and future trends.
    6. CHAPTER 5: CONCLUSION & RECOMMENDATIONS.
    7. COMPREHENSIVE REFERENCES: List all the 35 sources used sequentially according to the {style} guidelines.
    
    Make the style extremely scholarly, formal, sophisticated, and highly descriptive to fulfill the maximum word capacity. Do not summarize; expand every point to its absolute limit.
    """
    
    # استخدام نموذج Pro المتطور لمعالجة النصوص الضخمة والبحوث الطويلة جداً
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,  # رفع حد التوليد الأقصى للنصوص الضخمة والبحوث المطولة
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in result:
            return f"خطأ من خوادم جوجل (API Error): {result['error'].get('message', 'تفاصيل غير معروفة')}"
        else:
            return "حدث استجابة غير متوقعة من خوادم جوجل، تأكد من سلامة المفتاح وحسابك."
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بنظام Gemini المطور: {e}"

def create_rich_word_document(text, title):
    """تحويل البحث الطويل والمصادر إلى ملف Word مخصص ومصمم بطريقة أكاديمية منسقة للطباعة"""
    doc = docx.Document()
    doc.add_heading(title, level=0)
    
    lines = text.split("\n")
    for line in lines:
        clean_line = line.replace("**", "").replace("###", "").replace("##", "").replace("#", "").strip()
        if not clean_line:
            continue
        if "CHAPTER" in line or "Introduction" in line or "Review" in line or "Discussion" in line or "References" in line or "Conclusion" in line:
            doc.add_heading(clean_line, level=1)
        else:
            doc.add_paragraph(clean_line)
            
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# بناء الواجهة الرسومية المتطورة للمستخدم
research_title = st.text_input("📝 أدخل عنوان البحث العلمي المطول المطلوب إنشاؤه (سيتم سحب +30 مرجعاً صريحاً):")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 لغة الصياغة الأكاديمية المطولة:", ["English", "العربية"])
with col2:
    citation_style = st.selectbox("📚 نظام توثيق المراجع الدولي (لأكثر من 30 مصدراً):", ["APA", "IEEE", "Harvard"])

if st.button("🚀 ابدأ التوليد العميق وصياغة الـ 20 صفحة"):
    if research_title:
        if not SERPAPI_KEY or not GEMINI_KEY:
            st.error("🛑 خطأ في الإعدادات: هذا النظام يتطلب وجود SERPAPI_KEY و GEMINI_KEY معاً في ملف الـ .env ليعمل بنجاح.")
        else:
            with st.spinner("🔄 جاري تفعيل البحث العميق المتتالي لجمع أكثر من 30 مرجعاً علمياً من Google Scholar..."):
                all_papers = fetch_extensive_google_scholar(research_title)
                
            if len(all_papers) >= 20:
                st.success(f"✅ مذهل! تم جلب وتصفية {len(all_papers)} مصدراً أكاديمياً جاهزاً للتضمين صراحة!")
                
                with st.expander("🔗 استعراض قاعدة بيانات الـ +30 مصدراً العلمي المستخرجة"):
                    for i, paper in enumerate(all_papers):
                        st.markdown(f"**[{i+1}] {paper['title']}**")
                        st.caption(f"المصدر والمؤلفون: {paper['authors']}")
                        st.write(paper['snippet'])
                        st.markdown(f"[رابط المصدر الأكاديمي]({paper['link']})")
                        st.write("---")
                
                with st.spinner("🧠 يقوم نموذج Gemini 1.5 Pro الآن بتحليل البيانات وصياغة الـ 20 صفحة بالتفصيل الشديد... قد يستغرق دقيقة نظراً لضخامة البحث:"):
                    generated_text = generate_deep_academic_paper(research_title, all_papers, language, citation_style)
                    
                st.subheader("📄 معاينة مسودة البحث العلمي الضخم:")
                st.text_area("نص البحث الممتد بالكامل", generated_text, height=500)
                
                if "خطأ" not in generated_text and "Error" not in generated_text:
                    st.balloons()
                    word_file = create_rich_word_document(generated_text, research_title)
                    st.download_button(
                        label="📥 تحميل البحث الأكاديمي الضخم والمستقر كاملاً بصيغة ملف Word (.docx)",
                        data=word_file,
                        file_name=f"{research_title.replace(' ', '_')}_Extended_Research_Paper.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            else:
                st.warning(f"تم العثور على {len(all_papers)} مصادر فقط. يرجى تجربة عنوان بحثي عام أو معروف عالمياً لضمان سحب أكثر من 30 مصدراً بنجاح.")
    else:
        st.error("الرجاء كتابة عنوان البحث الأكاديمي أولاً.")
