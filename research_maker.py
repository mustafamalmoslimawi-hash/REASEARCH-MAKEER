import streamlit as st
import requests
import docx
from io import BytesIO
import xml.etree.ElementTree as ET

# إعدادات واجهة المستخدم الرسومية لـ RESEARCH-MAKER ULTRA
st.set_page_config(page_title="RESEARCH-MAKER ULTRA", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER ULTRA</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>المحرك الأكاديمي الشامل: توليد مطول وعميق يحاكي كامل قالب الـ Word المرفوع</h4>", unsafe_allow_html=True)
st.write("---")

# جلب مفاتيح الربط من السيكرتس بشكل آمن
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "").strip()
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "").strip()

# ==================== قسم قراءة قالب الـ WORD بالكامل ====================
def extract_structure_from_docx(file_buffer):
    try:
        doc = docx.Document(file_buffer)
        structure_lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                if para.style.name.startswith('Heading') or text.isupper() or any(k in text.lower() for k in ['chapter', 'section', 'المبحث', 'الفصل', 'المقدمة', 'الخاتمة', 'المطلب']):
                    structure_lines.append(f"[الهيكل والترتيب الرئيسي] {text}")
                else:
                    structure_lines.append(text)
        return "\n".join(structure_lines) # قراءة شاملة وكاملة للقالب لمحاكاته بدقة
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحليل ملف القالب: {e}")
        return ""

# ==================== قسم الـ APIs لتجهيز المراجع العلمية ====================
def fetch_semantic_scholar(query):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=4&fields=title,abstract,url"
    try:
        response = requests.get(url, timeout=10)
        data = response.json().get("data", [])
        return [{"title": item.get("title", "No Title"), "snippet": item.get("abstract", "No abstract available."), "link": item.get("url", "#"), "source": "Semantic Scholar"} for item in data if item.get("abstract")]
    except: return []

def fetch_arxiv(query):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=4"
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
        return [{"title": item.get("title", "No Title"), "snippet": item.get("snippet", "No abstract available."), "link": item.get("link", "#"), "source": "Google Scholar"} for item in results[:4]]
    except: return []

# ==================== محرك الإنتاج العملاق والمطول المستقر المباشر ====================
def generate_advanced_templated_research(title, combined_papers, template_text, lang, style):
    sources_block = ""
    for idx, p in enumerate(combined_papers):
        sources_block += f"\n- Title: {p['title']}\n  Abstract: {p['snippet']}\n"
        
    prompt = (
        f"You are an elite academic professor and expert research builder. Write a comprehensive, multi-page, extremely deep "
        f"academic research paper about '{title}' in language: {lang} using {style} citation style.\n\n"
        f"STRICT REQUIREMENTS FOR LENGTH & STRUCTURE:\n"
        f"1. Your text output must be very long, rich, highly detailed, and elaborate. Expand heavily on every point to ensure a substantial multi-page document.\n"
        f"2. You MUST perfectly mimic, align with, and replicate the full structure, sections, and headings of the user's template below:\n{template_text}\n\n"
        f"3. Integrate context and citations from these papers into the sections:\n{sources_block}\n\n"
        f"Generate the full-length comprehensive scientific output now."
    )
    
    # استخدام الرابط المباشر لـ Gemini والموديل الاحترافي 1.5 Pro لمعالجة الأبحاث الطويلة جداً وضمان الاستقرار الكامل
    if GEMINI_KEY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 8192, # الحد الأقصى للتوليد المطول لإعطاء صفحات كثيرة
                "temperature": 0.4
            }
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=180)
            res_json = response.json()
            if 'candidates' in res_json and len(res_json['candidates']) > 0:
                return res_json['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            pass

    # خط دفاع احتياطي تلقائي (Fallback) عبر السيرفرات البديلة المفتوحة في حال حدوث ضغط مفاجئ
    try:
        openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        payload_or = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post(openrouter_url, json=payload_or, headers={"Content-Type": "application/json"}, timeout=120)
        res_json = res.json()
        if 'choices' in res_json and len(res_json['choices']) > 0:
            return res_json['choices'][0]['message']['content']
    except:
        pass
        
    return "ERROR_SYSTEM: الخادم مستغرق في التوليد، يرجى إعادة الضغط على زر التشغيل فوراً لاستلام بحثك كاملاً."

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
        with st.spinner("📊 جاري تحليل وقراءة قالب الـ Word كاملاً لمحاكاته..."):
            extracted_template = extract_structure_from_docx(uploaded_file)
        if extracted_template:
            with st.spinner("🌐 جاري جلب وتجميع المراجع الأكاديمية الشاملة..."):
                all_combined_papers = fetch_google_scholar(research_title) + fetch_semantic_scholar(research_title) + fetch_arxiv(research_title)
            
            if not all_combined_papers:
                all_combined_papers = [{"title": "General Context on " + research_title, "snippet": "Academic background data regarding the subject material.", "link": "https://scholar.google.com", "source": "Local System"}]
            
            st.success(f"🔥 تم تأمين {len(all_combined_papers)} مرجعاً علمياً متقاطعة لبناء بحثك!")
            
            with st.spinner("🧠 يقوم المحرك الاحترافي بصياغة بحث طويل ومطول ومطابق للقالب تماماً..."):
                generated_research = generate_advanced_templated_research(research_title, all_combined_papers, extracted_template, language, citation_style)
            
            st.subheader("📄 معاينة البحث الهيكلي الجديد المولد:")
            st.text_area("المستند الأكاديمي الكامل", generated_research, height=450)
            if "ERROR_" not in generated_research:
                st.balloons()
                st.download_button(label="📥 تحميل مستند البحث العلمي الكامل (.docx)", data=create_formatted_docx(generated_research, research_title), file_name=f"{research_title.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            else:
                st.error(generated_research)
    else:
        st.error("الرجاء إدخال عنوان البحث ورفع الملف أولاً.")
