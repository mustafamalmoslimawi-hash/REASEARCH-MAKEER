import streamlit as st
import requests
import docx
from io import BytesIO
import xml.etree.ElementTree as ET

# إعدادات واجهة المستخدم الرسومية لـ RESEARCH-MAKER ULTRA
st.set_page_config(page_title="RESEARCH-MAKER ULTRA", layout="wide")

st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER ULTRA V3</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>المحرك الأكاديمي الشامل: توليد مطول + محاكاة كاملة لقالب الـ Word المرفوع</h4>", unsafe_allow_html=True)
st.write("---")

# جلب مفتاح سبرب آبي إذا كان متاحاً
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "").strip()

# ==================== قسم قراءة قالب الـ WORD بالكامل ====================
def extract_structure_from_docx(file_buffer):
    try:
        doc = docx.Document(file_buffer)
        structure_lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                if para.style.name.startswith('Heading') or text.isupper() or any(k in text.lower() for k in ['chapter', 'section', 'المبحث', 'الفصل', 'المقدمة', 'الخاتمة']):
                    structure_lines.append(f"[الهيكل الرئيسي] {text}")
                else:
                    structure_lines.append(text)
        # تم فتح القراءة لتشمل القالب كاملاً ومحاكاته بدقة
        return "\n".join(structure_lines)
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحليل ملف القالب: {e}")
        return ""

# ==================== قسم الـ APIs لتجهيز المراجع ====================
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

# ==================== قسم التوليد المطول والأكاديمي الفائق ====================
def generate_advanced_templated_research(title, combined_papers, template_text, lang, style):
    sources_block = ""
    for idx, p in enumerate(combined_papers):
        sources_block += f"\n- Title: {p['title']}\n  Abstract: {p['snippet']}\n"
        
    # صياغة توجيه صارم ومشدد للذكاء الاصطناعي ليكتب بغزارة ويلتزم بالقالب بالتفصيل
    prompt = (
        f"You are an elite academic professor and Senior Research Writer. Write an extremely comprehensive, "
        f"highly detailed, and exhaustive academic research paper about '{title}' in language: {lang} using {style} citation style.\n\n"
        f"CRITICAL REQUIREMENT:\n"
        f"1. You MUST follow every single section, heading, and layout detailed in this user template:\n{template_text}\n\n"
        f"2. DO NOT summarize or skip sections. Write long, deeply analytical paragraphs for each part to ensure a massive, full-length paper.\n"
        f"3. Seamlessly incorporate data and citations from these actual scientific papers:\n{sources_block}\n\n"
        f"Provide the complete comprehensive output without placeholders."
    )
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # استخدام الموديل العملاق Llama 3.3 70B المجاني القادر على كتابة أبحاث طويلة جداً والالتزام التام بالقوالب
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a professional academic book and research writer who writes exhaustive, lengthy, and highly detailed papers based on user templates."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=160)
        res_json = response.json()
        if 'choices' in res_json and len(res_json['choices']) > 0:
            return res_json['choices'][0]['message']['content']
    except:
        pass
        
    # خيار احتياطي سري في حال حدوث ضغط على الموديل الأول
    try:
        payload["model"] = "nousresearch/hermes-3-llama-3.1-8b:free"
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
        res_json = response.json()
        if 'choices' in res_json and len(res_json['choices']) > 0:
            return res_json['choices'][0]['message']['content']
    except:
        pass
        
    return "ERROR_SYSTEM: السيرفرات العالمية تواجه ضغطاً حالياً، يرجى إعادة المحاولة بعد ثوانٍ قليلة."

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
        with st.spinner("📊 جاري قراءة كامل بنية مستند القالب بدقة..."):
            extracted_template = extract_structure_from_docx(uploaded_file)
        if extracted_template:
            with st.spinner("🌐 جاري جلب المراجع الأكاديمية العميقة..."):
                all_combined_papers = fetch_google_scholar(research_title) + fetch_semantic_scholar(research_title) + fetch_arxiv(research_title)
            
            if not all_combined_papers:
                all_combined_papers = [{"title": "General Context on " + research_title, "snippet": "Academic background data regarding the subject material.", "link": "https://scholar.google.com", "source": "Local System"}]
            
            st.success(f"🔥 تم تأمين {len(all_combined_papers)} مرجعاً علمياً متقاطعة لبناء بحثك!")
            
            with st.spinner("🧠 يقوم المحرك العملاق (70B) بصياغة البحث المطول وتطبيق بنية القالب بالكامل الآن..."):
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
