import streamlit as st
import requests
import docx
from io import BytesIO
import xml.etree.ElementTree as ET
import google.generativeai as genai

# إعدادات واجهة المستخدم الرسومية لـ RESEARCH-MAKER ULTRA
st.set_page_config(page_title="RESEARCH-MAKER ULTRA", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER ULTRA</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>المحرك الأكاديمي الشامل: جلب متعدد المصادر + محاكاة قالب الـ Word المرفوع</h4>", unsafe_allow_html=True)
st.write("---")

# جلب المفاتيح بأمان كامل من خزنة Streamlit (Secrets)
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "").strip()
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "").strip()

# تهيئة خادم جوجل بالمفتاح السري
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
    except Exception as e:
        st.error(f"خطأ في تهيئة خادم جوجل: {e}")

# ==================== قسم قراءة قالب الـ WORD ====================
def extract_structure_from_docx(file_buffer):
    """قراءة مستند الـ Word المرفوع واستخراج الهيكل والترتيب منه تلقائياً"""
    try:
        doc = docx.Document(file_buffer)
        structure_lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                if para.style.name.startswith('Heading') or text.isupper() or any(k in text.lower() for k in ['chapter', 'section', 'المبحث', 'الفصل']):
                    structure_lines.append(f"[Heading] {text}")
                else:
                    structure_lines.append(text)
        return "\n".join(structure_lines)
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحليل ملف القالب: {e}")
        return ""

# ==================== قسم الـ APIs الموسعة لتجهيز البحث ====================
def fetch_semantic_scholar(query):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=8&fields=title,abstract,url"
    try:
        response = requests.get(url, timeout=10)
        data = response.json().get("data", [])
        papers = []
        for item in data:
            if item.get("abstract") or item.get("title"):
                papers.append({
                    "title": item.get("title", "No Title"),
                    "snippet": item.get("abstract", "No abstract available."),
                    "link": item.get("url", "#"),
                    "source": "Semantic Scholar"
                })
        return papers
    except:
        return []

def fetch_arxiv(query):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=8"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.text)
        papers = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary')
            snippet = summary.text if summary is not None else "No summary available."
            link = entry.find('{http://www.w3.org/2005/Atom}id').text
            papers.append({
                "title": title.strip().replace("\n", ""),
                "snippet": snippet.strip().replace("\n", " "),
                "link": link,
                "source": "arXiv Repository"
            })
        return papers
    except:
        return []

def fetch_google_scholar(query):
    if not SERPAPI_KEY: return []
    url = "https://serpapi.com/search"
    params = {"engine": "google_scholar", "q": query, "hl": "en", "api_key": SERPAPI_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        results = response.json().get("organic_results", [])
        return [{
            "title": item.get("title", "No Title"),
            "snippet": item.get("snippet", "No abstract available."),
            "link": item.get("link", "#"),
            "source": "Google Scholar"
        } for item in results[:8]]
    except:
        return []

# ==================== عقل التوليد الذكي وصناعة المحتوى ====================
def generate_advanced_templated_research(title, combined_papers, template_text, lang, style):
    if not GEMINI_KEY:
        return "ERROR_KEY: لم يتم تهيئة مفتاح جيلوجل السري بنجاح في خزنة الموقع."
        
    sources_block = ""
    for idx, p in enumerate(combined_papers):
        sources_block += f"\n[Source {idx+1} from {p['source']}]\nTitle: {p['title']}\nAbstract: {p['snippet']}\nLink: {p['link']}\n"
        
    prompt = f"""
    You are an elite academic professor. Write an extensive, deep, and fully cited scientific research paper about the new topic: '{title}'.
    CRITICAL STRUCTURE MANDATE: Follow and fill the exact section flow from the template.
    Target Language: {lang}
    Citation Style: {style}
    
    [UPLOADED TEMPLATE STRUCT]:
    {template_text}
    
    [ACADEMIC DATABASE]:
    {sources_block}
    """
    
    try:
        # التعديل الحاسم: إجبار استدعاء النموذج المستقر عبر المسار المباشر لتخطي مشاكل الـ 404 للسيرفرات القديمة
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR_API: {e}"

def create_formatted_docx(text, title):
    doc = docx.Document()
    doc.add_heading(title, level=0)
    lines = text.split("\n")
    for line in lines:
        clean_line = line.replace("**", "").replace("###", "").replace("##", "").replace("#", "").strip()
        if not clean_line: continue
        if any(keyword in line for keyword in ["CHAPTER", "Introduction", "Review", "Discussion", "Conclusion", "References", "المبحث", "الفصل"]):
            doc.add_heading(clean_line, level=1)
        else:
            doc.add_paragraph(clean_line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# ==================== بناء واجهة المستخدم ====================
research_title = st.text_input("📝 أولاً: اكتب عنوان البحث العلمي الجديد المُراد صناعته:")
uploaded_file = st.file_uploader("📐 ثانياً: ارفع ملف الـ Word القياسي:", type=["docx"])

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 لغة الكتابة الأكاديمية المطلوبة:", ["English", "العربية"])
with col2:
    citation_style = st.selectbox("📚 نظام توثيق الهوامش والملحقات:", ["APA", "IEEE", "Harvard"])

if st.button("🚀 تشغيل النظام الفائق وإنشاء البحث"):
    if research_title and uploaded_file is not None:
        with st.spinner("📊 جاري تحليل ملف القالب..."):
            extracted_template = extract_structure_from_docx(uploaded_file)
            
        if extracted_template:
            with st.spinner("🌐 جاري جلب الأبحاث العلمية الشاملة..."):
                all_combined_papers = fetch_google_scholar(research_title) + fetch_semantic_scholar(research_title) + fetch_arxiv(research_title)
                
            if not all_combined_papers:
                all_combined_papers = [{"title": f"General Overview on {research_title}", "snippet": "Academic background.", "link": "https://scholar.google.com", "source": "Local System"}]
                
            st.success(f"🔥 تم تأمين {len(all_combined_papers)} مرجعاً علمياً لتوثيق بحثك!")
            
            with st.spinner("🧠 يقوم النظام بصياغة الفصول كاملة الآن..."):
                generated_research = generate_advanced_templated_research(research_title, all_combined_papers, extracted_template, language, citation_style)
                
            st.subheader("📄 معاينة البحث الهيكلي الجديد المولد:")
            st.text_area("المستند الأكاديمي الكامل", generated_research, height=450)
            
            if "ERROR_" not in generated_research:
                st.balloons()
                final_docx = create_formatted_docx(generated_research, research_title)
                st.download_button(
                    label="📥 تحميل مستند البحث العلمي الكامل المنسق تلقائياً (.docx)",
                    data=final_docx,
                    file_name=f"{research_title.replace(' ', '_')}_Final_Research.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error(f"تنبيه: {generated_research}")
    else:
        st.error("الرجاء إدخال عنوان البحث ورفع الملف أولاً.")
