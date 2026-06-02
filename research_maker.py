import streamlit as st
import requests

# إعدادات الصفحة الأساسية للموقع لتكون متناسقة واحترافية
st.set_page_config(page_title="RESEARCH-MAKER", layout="wide")

# التصميم العلوي للموقع (العنوان والترحيب)
st.markdown("<h1 style='text-align: center; color: #008080;'>🔬 RESEARCH-MAKER</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555;'>النظام الذكي للبحث الأكاديمي وصياغة الأبحاث تلقائياً</h4>", unsafe_allow_html=True)
st.write("---")

# ضع مفتاح SerpApi الذي نسخته هنا بين القوسين لتشغيل السيرفر مؤقتاً 
# (أو يفضل مستقبلاً قراءته من ملف .env)
SERPAPI_KEY = "3333539fe58445aebe1e4c9ae5d105d12e12160121f8beb93d8ff6bbd657c515"

def fetch_google_scholar_papers(query):
    """دالة للاتصال بجوجل سكالر وسحب أهم الأبحاث والمراجع"""
    if not SERPAPI_KEY or "اكتب_مفتاح" in SERPAPI_KEY:
        st.error("⚠️ الرجاء إضافة مفتاح الـ API الخاص بـ SerpApi داخل الكود أولاً لتفعيل البحث.")
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
        results = response.json()
        
        # تجميع الأبحاث المستخرجة وترتيبها
        articles = []
        for item in results.get("organic_results", [])[:5]:  # جلب أهم 5 أبحاث فقط للسرعة
            articles.append({
                "title": item.get("title", "No Title"),
                "link": item.get("link", "#"),
                "snippet": item.get("snippet", "No abstract available."),
                "citations": item.get("inline_links", {}).get("cited_by", {}).get("total", 0)
            })
        return articles
    except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال بالخادم: {e}")
        return []

# بناء عناصر واجهة المستخدم المدخلة
research_title = st.text_input("📝 أدخل الكلمات المفتاحية أو عنوان البحث العلمي المطلوب:")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 لغة الصياغة المطلوبة:", ["English", "العربية"])
with col2:
    citation_style = st.selectbox("📚 نظام توثيق المراجع:", ["APA", "IEEE", "Harvard"])

# زر بدء عمليات البحث التلقائي
if st.button("🚀 ابدأ البحث الأكاديمي والتوليد"):
    if research_title:
        with st.spinner("🔄 جاري الاتصال بقاعدة بيانات Google Scholar وسحب الأوراق العلمية والمراجع..."):
            papers = fetch_google_scholar_papers(research_title)
            
            if papers:
                st.success(f"✅ تم العثور على {len(papers)} أبحاث أكاديمية موثقة ومطابقة لعناوينك!")
                st.write("---")
                
                # عرض نتائج البحث للمستخدم في الواجهة
                st.subheader("📋 الأوراق العلمية والمراجع المعتمدة المستخرجة:")
                for index, paper in enumerate(papers):
                    with st.expander(f"📄 مرجع [{index+1}]: {paper['title']}"):
                        st.markdown(f"**الملخص المستخلص (Snippet):** {paper['snippet']}")
                        st.markdown(f"**عدد الاقتباسات العالمي (Citations):** {paper['citations']}")
                        st.markdown(f"[🔗 رابط الورقة العلمية الأصلية]({paper['link']})")
                
                st.write("---")
                st.info("💡 الخطوة القادمة: سيتم إرسال هذه البيانات المستخرجة إلى نموذج الذكاء الاصطناعي (العقل المفكر) لبناء المقدمة، التحليل، والمراجع تلقائياً لتنزيلها كملف جاهز.")
            else:
                st.warning("لم يتم العثور على نتائج، يرجى التحقق من المفتاح أو العنوان وحاول مجدداً.")
    else:
        st.error("الرجاء كتابة اسم أو عنوان البحث أولاً قبل الضغط على الزر.")
