import streamlit as st
import requests
import docx
from io import BytesIO
import xml.etree.ElementTree as ET

# إعدادات واجهة المستخدم الرسومية لـ RESEARCH-MAKER ULTRA
st.set_page_config(page_title="RESEARCH-MAKER ULTRA", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER ULTRA</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>المحرك الأكاديمي الشامل: جلب متعدد المصادر + محاكاة قالب الـ Word المرفوع</h4>", unsafe_allow_html=True)
st.write("---")

# جلب المفاتيح بأمان من خزنة Streamlit (Secrets)
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "").strip()
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "").strip()

# ==================== قسم قراءة قالب الـ WORD ====================
def extract_structure_from_docx(file_buffer):
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

# ==================== قسم الـ APIs لتجهيز المراجع ====================
def fetch_semantic_scholar(query):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,abstract,url"
    try:
        response = requests.get(url, timeout=10)
        data = response.json().get("data", [])
        return [{"title": item.get("title", "No Title"), "snippet": item.get("abstract", "No abstract available."), "link": item.get("url", "#"), "source": "Semantic Scholar"} for item in data if item.get("abstract")]
    except: return []

def fetch_arxiv(query):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=5"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.text)
        papers = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary')
            papers.append({"title": title.strip().replace("\n", ""), "snippet": summary.text.strip().replace("\n", " ") if summary is not None else "", "link": entry.find('{http://www.w3.org/2005/Atom}id').text, "source": "arXiv Repository"})
        return papers
    except: return []

def fetch_google_scholar(query):
    if not SERPAPI_KEY: return []
    url = "https://serpapi.com/search"
    params = {"engine": "google_scholar", "q": query, "hl": "en", "api_key": SERPAPI_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        results = response.json().get("organic_results", [])
        return [{"title": item.get("title", "No Title"), "snippet": item.get("snippet", "No abstract available."), "link": item.get("link", "#"), "source": "Google Scholar"} for item in results[:5]]
    except: return []

# ==================== الدالة المعدلة لدعم مفاتيح Vertex AI (التي تبدأ بـ AQ) ====================
def generate_advanced_templated_research(title, combined_papers, template_text, lang, style):
    if not GEMINI_KEY:
        return "ERROR_KEY: لم يتم العثور على مفتاح GEMINI_KEY في إعدادات الخزنة."
        
    sources_block = ""
    for idx, p in enumerate(combined_papers):
        sources_block += f"\n- Title: {p['title']}\n  Abstract: {p['snippet']}\n"
        
    prompt = (
        f"You are an elite academic professor. Write a comprehensive, deep academic research paper about '{title}' "
        f"in language: {lang} using {style} citation style.\n\n"
        f"Strictly align your writing with this structural layout extracted from the user template:\n{template_text}\n\n"
        f"Integrate context and data from these academic sources:\n{sources_block}\n\n"
        f"Provide a long, well-structured scientific output."
    )
    
    # إعداد الـ Headers لتتوافق مع معايير مفاتيح الخدمة والمصادقة المباشرة لروابط التطور والإنتاج السحابي
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': GEMINI_KEY
    }
    
    # استخدام المسار الأساسي الموحد والمستقر للإصدار الأول للـ API لضمان التوافق المطلق
    api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    
    # إذا تم رصد مفتاح AI Studio تقليدي مستقبلاً، يتم إلحاقه بالرابط تلقائياً كخيار احتياطي ثانٍ
    if GEMINI_KEY.startswith('AIza'):
        api_url += f"?key={GEMINI_KEY}"
        
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        res_json = response.json()
        
        if 'candidates' in res_json and res_json['candidates']:
            return res_json['candidates'][0]['content']['parts'][0]['text']
            
        if 'error' in res_json:
            # محاولة مع إصدار v1beta كخيار بديل في حالة تعثر المسار الأساسي
            fallback_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            if GEMINI_KEY.startswith('AIza'): fallback_url += f"?key={GEMINI_KEY}"
            
            fallback_res = requests.post(fallback_url, json=payload, headers=headers, timeout=120).json()
            if 'candidates' in fallback_res and fallback_res['candidates']:
                return fallback_res['candidates'][0]['content']['parts'][0]['text']
                
            return f"ERROR_API_SERVER: {res_json['error'].get('message', 'خطأ في معالجة الهوية السحابية للمفتاح الحالي.')}"
            
        return "ERROR_RESPONSE: استجابة خادم جوجل غير مطابقة للمواصفات البرمجية الحالية."
        
    except Exception as e:
        return f"ERROR_SYSTEM: حدث خطأ أثناء الاتصال بالشبكة الخارجية: {e}"

def create_formatted_docx(text, title):
    doc = docx.Document()
    doc.add_heading(title, level=0)
    for line in text.split("\n"):
        clean = line.replace("**", "").replace("###", "").replace("##", "").strip()
        if clean: doc.add_paragraph(clean)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# ==================== واجهة المستخدم الرسومية ====================
research_title = st.text_input("📝 أولاً: اكتب عنوان البحث العلمي الجديد المُراد صناعته:")
uploaded_file = st.file_uploader("📐 ثانياً: ارفع ملف الـ Word القياسي تلقائياً:", type=["docx"])

col1, col2 = st.columns(2)
with col1: language = st.selectbox("🌐 لغة الكتابة الأكاديمية المطلوبة:", ["English", "العربية"])
with col2: citation_style = st.selectbox("📚 نظام توثيق الهوامش والملحقات:", ["APA", "IEEE", "Harvard"])

if st.button("🚀 تشغيل النظام الفائق وإنشاء البحث"):
    if research_title and uploaded_file is not None:
        with st.spinner("📊 jاري قراءة بنية المستند..."):
            extracted_template = extract_structure_from_docx(uploaded_file)
        if extracted_template:
            with st.spinner("🌐 جاري سحب الأبحاث العلمية الشاملة..."):
                all_combined_papers = fetch_google_scholar(research_title) + fetch_semantic_scholar(research_title) + fetch_arxiv(research_title)
            
            if not all_combined_papers:
                all_combined_papers = [{"title": "General Context on " + research_title, "snippet": "Academic background data regarding the subject material.", "link": "https://scholar.google.com", "source": "Local System"}]
            
            st.success(f"🔥 تم تأمين {len(all_combined_papers)} مرجعاً علمياً متقاطعة لبناء بحثك!")
            
            with st.spinner("🧠 يقوم النظام الفائق بصياغة البحث كاملاً الآن..."):
                generated_research = generate_advanced_templated_research(research_title, all_combined_papers, extracted_template, language, citation_style)
            
            st.subheader("📄 معاينة البحث الهيكلي الجديد المولد:")
            
            if "ERROR_" in generated_research:
                st.error(generated_research)
            else:
                st.text_area("المستند الأكاديمي الكامل", generated_research, height=450)
                st.balloons()
                st.download_button(label="📥 تحميل مستند البحث العلمي الكامل (.docx)", data=create_formatted_docx(generated_research, research_title), file_name=f"{research_title.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.error("الرجاء إدخال عنوان البحث ورفع الملف أولاً.")
