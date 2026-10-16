# ==========新增【只加在文件最开头，原有代码保留不动】==========
from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
def call_deepseek(system_prompt, user_text):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_text}],
        temperature=0.4
    )
    return resp.choices[0].message.content
# =========================================================
import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text
import pytesseract
from PIL import Image
# ===================== 【11】药品知识库 全局定义 =====================
drug_kb = {
    "阿司匹林": "【阿司匹林】抗血小板药物，用于预防血栓。风险：和布洛芬联用会显著增加消化道出血风险；肾病患者慎用。",
    "布洛芬": "【布洛芬】解热镇痛抗炎药。风险：长期服用损伤肾脏；与阿司匹林合用出血风险升高。",
    "氨氯地平": "【氨氯地平】降压药，高血压常用。不良反应：脚踝水肿、头晕。",
    "二甲双胍": "【二甲双胍】降糖药，2型糖尿病首选。注意：肾功能不全需要调整剂量。",
    "辛伐他汀": "【辛伐他汀】降脂药，用于高血脂。注意：少数人会肌肉酸痛，定期查肌酶。"
}
# ===================== 【12】中英文语言包 =====================
lang_dict = {
    "zh": {
        "system_title": "多场景健康智能评估系统",
        "select_mode": "请选择评估模式",
        "mode_med": "👴 老年多重用药安全评估",
        "mode_eye": "👧 青少年眼部健康评估",
        "mode_about": "📖 使用说明与免责声明",
        "history_title": "📜 历史报告记录",
        "clear_all": "🗑️ 清空所有记录",
        "med_title": "💊 老年人多重用药安全评估系统",
        "med_sub": "七个智能体协同用药风险检测",
        "med_desc": "输入老人基础疾病、正在服用的药品，系统自动分析药物冲突、副作用与用药风险等级",
        "template_title": "📋 快速病例模板",
        "template_select": "选择模板一键填充",
        "fill_btn": "✅ 填充病例",
        "voice_tip_med": "🎤 语音录入：点击麦克风，口述老人病情与用药信息",
        "input_label_med": "📝 手动输入老人健康与用药信息",
        "placeholder_med": "例：张大爷，72岁，慢性肾病，服用阿司匹林、布洛芬",
        "clear_input": "🗑️ 清空输入框",
        "run_med": "🚀 开始智能评估并生成报告",
        "empty_warn": "⚠️ 输入内容不能为空！",
        "info_warn_med": "⚠️ 信息不足！请补充老人年龄、基础疾病、正在服用的药物，再进行评估。",
        "eval_success_med": "✅ 用药风险评估完成！",
        "report_title_med": "📄 老年人多重用药安全报告",
        "drug_detail_title": "🔍 查看识别到的药品知识库详情",
        "eye_title": "👁️ 青少年眼部健康评估系统",
        "eye_sub": "近视风险智能分析",
        "eye_desc": "输入青少年年龄、每日用眼时长、眼部不适症状，评估近视风险并给出护眼建议",
        "template_title_eye": "📋 快速病例模板",
        "template_select_eye": "选择模板一键填充",
        "fill_btn_eye": "✅ 填充用眼场景",
        "voice_tip_eye": "🎤 语音录入：口述学生年龄、用眼情况、眼睛症状",
        "input_label_eye": "📝 输入青少年用眼情况、症状、年龄",
        "placeholder_eye": "例：14岁，每天玩手机6小时，眼睛干涩、酸胀，很少户外运动",
        "clear_input_eye": "🧹 清空",
        "ocr_tip": "📷 上传视力检查单图片，自动识别文字填充",
        "upload_label": "上传图片",
        "ocr_result": "识别结果：",
        "ocr_fill_btn": "✅ 将识别文字填入输入框",
        "run_eye": "🔍 智能分析眼部健康状态",
        "info_warn_eye": "⚠️ 信息不足！请补充年龄、每日用眼时长、眼部不适症状等信息，再进行评估。",
        "eval_success_eye": "✅ 青少年眼部智能分析完成！",
        "report_title_eye": "📄 眼部健康智能评估报告",
        "about_title": "📖 使用说明与免责声明",
        "about_text": """
### 使用说明
1. 老年用药模块：填写老人年龄、基础疾病、服用药物，评估用药风险。
2. 青少年眼部模块：填写年龄、用眼时长、眼部症状；支持图片上传OCR识别视力单。
3. 支持语音输入、模板一键填充、报告下载、历史报告查看。
### ⚠️免责声明
本系统仅为科普风险筛查工具，**不能替代执业医师或临床药师的专业诊断**，评估结果仅供参考，不可作为诊疗依据。如有身体不适，请前往正规医疗机构就诊。
"""
    },
    "en": {
        "system_title": "Multi-scenario Health Intelligent Assessment System",
        "select_mode": "Select assessment mode",
        "mode_med": "👴 Elderly Multi-Medication Safety Assessment",
        "mode_eye": "👧 Teen Eye Health Assessment",
        "mode_about": "📖 Guide & Disclaimer",
        "history_title": "📜 History Reports",
        "clear_all": "🗑️ Clear All Records",
        "med_title": "💊 Elderly Multi-Medication Safety Assessment System",
        "med_sub": "Seven-agent Medication Risk Detection",
        "med_desc": "Input elderly disease and medicines to analyze drug interaction and risk",
        "template_title": "📋 Quick Template",
        "template_select": "Select template to fill",
        "fill_btn": "✅ Fill Template",
        "voice_tip_med": "🎤 Voice input: Click mic to describe patient info",
        "input_label_med": "📝 Manual input of health and medication info",
        "placeholder_med": "e.g. Grandpa Zhang,72,chronic kidney disease, taking aspirin and ibuprofen",
        "clear_input": "🗑️ Clear Input",
        "run_med": "🚀 Start Assessment",
        "empty_warn": "⚠️ Input cannot be empty!",
        "info_warn_med": "⚠️ Insufficient info! Please fill age, disease and medicines.",
        "eval_success_med": "✅ Medication risk assessment completed!",
        "report_title_med": "📄 Elderly Medication Safety Report",
        "drug_detail_title": "🔍 View drug knowledge details",
        "eye_title": "👁️ Teen Eye Health Assessment System",
        "eye_sub": "Myopia Risk Analysis",
        "eye_desc": "Input age, daily screen time and eye symptoms to evaluate myopia risk",
        "template_title_eye": "📋 Quick Template",
        "template_select_eye": "Select template to fill",
        "fill_btn_eye": "✅ Fill Template",
        "voice_tip_eye": "🎤 Voice input: Describe age and eye condition",
        "input_label_eye": "📝 Input teen eye & usage info",
        "placeholder_eye": "e.g. 14 years old, 6h mobile daily, dry eyes, little outdoor activity",
        "clear_input_eye": "🧹 Clear",
        "ocr_tip": "📷 Upload vision report image for OCR",
        "upload_label": "Upload image",
        "ocr_result": "OCR Result: ",
        "ocr_fill_btn": "✅ Fill text into input box",
        "run_eye": "🔍 Analyze eye health",
        "info_warn_eye": "⚠️ Insufficient info! Please add age, eye symptoms and usage time.",
        "eval_success_eye": "✅ Teen eye analysis completed!",
        "report_title_eye": "📄 Eye Health Assessment Report",
        "about_title": "📖 Guide & Disclaimer",
        "about_text": """
### Instructions
1. Medication module: Fill age, disease and drugs for risk evaluation.
2. Eye module: Fill age, screen time and eye symptoms. Support OCR for vision report.
3. Support voice input, template fill, report download and history view.
### ⚠️ Disclaimer
This system is only for risk screening, **NOT a substitute for professional doctor or pharmacist diagnosis**. Results are for reference only. Seek medical help from hospital if unwell.
"""
    }
}
# ==========【13】OCR 配置（Windows请修改为你本地tesseract路径！如果不装OCR，可以注释这两行 ==========
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# =========================================================================================
# ====================== 页面基础配置与美化CSS ======================
st.set_page_config(
    page_title="多场景健康智能评估系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .card{
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .sidebar .stRadio label {
        font-size:16px;
    }
    .stButton>button {
        border-radius:8px;
    }
</style>
""", unsafe_allow_html=True)
# ====================== 状态初始化 ======================
if "history_reports" not in st.session_state:
    st.session_state.history_reports = []
if "current_input" not in st.session_state:
    st.session_state.current_input = ""
# ====================== 侧边栏 ======================
with st.sidebar:
    st.markdown("## 🧠 " + lang_dict["zh"]["system_title"])
    st.divider()
    # 语言切换
    lang = st.selectbox("🌐 Language / 语言",["zh","en"],format_func=lambda x:"中文" if x=="zh" else "English")
    L = lang_dict[lang]
    mode = st.radio(
        L["select_mode"],
        [L["mode_med"], L["mode_eye"], L["mode_about"]]
    )
    st.divider()
    st.markdown("### " + L["history_title"])
    if st.session_state.history_reports:
        idx = st.selectbox("选择历史报告查看", range(len(st.session_state.history_reports)), format_func=lambda x: f"报告{x+1}")
        st.markdown(st.session_state.history_reports[idx])
    else:
        st.write("暂无报告记录")
    if st.button(L["clear_all"]):
        st.session_state.history_reports = []
        st.session_state.current_input = ""
        st.rerun()
# ====================== 【页面：使用说明与免责】 ======================
if mode == L["mode_about"]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title(L["about_title"])
    st.markdown(L["about_text"])
    st.markdown("</div>", unsafe_allow_html=True)
# ====================== 场景一：老年多重用药安全评估 ======================
elif mode == L["mode_med"]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title(L["med_title"])
    st.subheader(L["med_sub"])
    st.markdown(L["med_desc"])
    st.divider()
    # 病例模板
    case_templates = {
        "【示例1：高危药物冲突】": "张大爷，72岁，慢性肾病，服用阿司匹林、布洛芬",
        "【示例2：信息不全示例】": "李大爷",
        "【示例3：单一药物低风险】": "王阿姨，66岁，高血压，正在服用氨氯地平",
        "【示例4：多病多药】": "刘爷爷，78岁，高血压、糖尿病，服用氨氯地平、二甲双胍、辛伐他汀"
    }
    st.subheader(L["template_title"])
    case_name = st.selectbox(L["template_select"], list(case_templates.keys()))
    if st.button(L["fill_btn"]):
        st.session_state.current_input = case_templates[case_name]
        st.rerun()
    st.divider()
    # 语音录入
    st.markdown(L["voice_tip_med"])
    text_out = speech_to_text(language='zh', just_once=True, key='mic_med')
    if text_out:
        st.session_state.current_input = text_out
        st.rerun()
    user_text = st.text_input(L["input_label_med"],
                            placeholder=L["placeholder_med"],
                            value=st.session_state.current_input)
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(L["clear_input"]):
            st.session_state.current_input = ""
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    run_btn = st.button(L["run_med"], type="primary")
    if run_btn and user_text.strip():
        content = user_text.strip()
        # 用药信息校验：需要包含年龄、疾病、药品关键词
        need_words = ["岁", "药", "服用", "吃", "高血压", "糖尿病", "肾病", "冠心病", "阿司匹林", "氨氯地平"]
        has_valid_info = any(w in content for w in need_words)
        if not has_valid_info:
            st.warning(L["info_warn_med"])
        else:
            st.success(L["eval_success_med"])
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("## " + L["report_title_med"])

            # =========【这里已经替换成LLM调用】=========
            if lang == "zh":
                sys_prompt = """你是老年多重用药安全评估专家。根据用户输入老人信息，生成用药评估报告。
输出格式严格遵守：
### 💊 老年人用药评估结果
**评估对象信息：**{用户信息}
**风险等级：高危 ⚠️ / 中风险 ⚠️ / 低风险 ✅**
风险分析内容
### ✅ 安全建议
安全建议内容
⚠️ 提醒：评估仅供科普参考，不能替代药师/医生诊断。"""
            else:
                sys_prompt = """You are elderly medication safety expert. Generate assessment report.
Format:
### 💊 Elderly Medication Assessment
**Patient Info:**{user info}
**Risk Level: High ⚠️ / Medium ⚠️ / Low ✅**
risk analysis
### ✅ Advice
advice
⚠️ This report is for reference only, not substitute for doctor or pharmacist."""

            report = call_deepseek(sys_prompt, content)
            # 自动识别风险等级展示对应颜色提示
            if "高危" in report or "High ⚠️" in report:
                st.error("🔴 【高用药风险】")
            elif "中风险" in report or "Medium ⚠️" in report:
                st.warning("🟠 【中等用药风险】")
            else:
                st.info("🟢 【低用药风险】")
            # ========================================

            st.markdown(report)
            st.session_state.history_reports.append(report)
            st.download_button("📥 下载报告", report, file_name="老年用药安全报告.txt")
            # ==========【11】药品知识库面板 ==========
            found_drugs = [name for name in drug_kb if name in content]
            if found_drugs:
                with st.expander(L["drug_detail_title"]):
                    for dname in found_drugs:
                        st.markdown(drug_kb[dname])
            # =======================================
            st.markdown("</div>", unsafe_allow_html=True)
    elif run_btn and not user_text.strip():
        st.warning(L["empty_warn"])
# ====================== 场景二：青少年眼部健康评估 ======================
elif mode == L["mode_eye"]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title(L["eye_title"])
    st.subheader(L["eye_sub"])
    st.markdown(L["eye_desc"])
    st.divider()
    eye_templates = {
        "【示例1：高风险用眼】": "14岁初中生，每天网课加写作业用眼12小时，经常眼干、视物模糊，经常熬夜玩手机",
        "【示例2：中风险用眼】": "16岁高中生，长时间近距离看书，眼睛酸胀，坐姿不好",
        "【示例3：低风险用眼】": "13岁学生，每天户外2小时，无眼睛不适"
    }
    st.subheader(L["template_title_eye"])
    eye_case = st.selectbox(L["template_select_eye"], list(eye_templates.keys()))
    if st.button(L["fill_btn_eye"]):
        st.session_state.current_input = eye_templates[eye_case]
        st.rerun()
    st.divider()
   # # 【13】OCR视力单图片上传识别
   #st.markdown(L["ocr_tip"])
    #upload_img = st.file_uploader(L["upload_label"], type=["jpg","png","jpeg"])
    #if upload_img is not None:
        #img = Image.open(upload_img)
        #st.image(img, width=400)
        ## 如果没有装Tesseract，注释下面一行
       # text_from_img = pytesseract.image_to_string(img, lang='chi_sim')
       # st.write(L["ocr_result"], text_from_img)
        #if st.button(L["ocr_fill_btn"]):
            #st.session_state.current_input = text_from_img
            #st.rerun()
    #st.divider()
    # 语音录入
    st.markdown(L["voice_tip_eye"])
    eye_text_out = speech_to_text(language='zh', just_once=True, key='mic_eye')
    if eye_text_out:
        st.session_state.current_input = eye_text_out
        st.rerun()
    eye_input = st.text_input(L["input_label_eye"],
                            placeholder=L["placeholder_eye"],
                            value=st.session_state.current_input)
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(L["clear_input_eye"]):
            st.session_state.current_input = ""
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    eye_run = st.button(L["run_eye"], type="primary")
    if eye_run and eye_input.strip():
        content = eye_input.strip()
        # 眼部信息校验
        need_words = ["岁", "小时", "眼", "眼睛", "干涩", "酸胀", "视力", "看手机", "看书", "网课"]
        has_valid_info = any(w in content for w in need_words)
        if not has_valid_info:
            st.warning(L["info_warn_eye"])
        else:
            st.success(L["eval_success_eye"])
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("## " + L["report_title_eye"])

            # =========【眼部模块替换为LLM调用】=========
            if lang == "zh":
                sys_prompt = """你是青少年眼部健康评估专家。根据用户输入信息生成眼部评估报告。
严格输出格式：
### 👁️ 青少年眼部健康评估结果
**评估对象信息：**{用户信息}
**风险等级：高危 ⚠️ / 中风险 ⚠️ / 低风险 ✅**
风险分析
### ✅ 专业改善建议
护眼建议内容
⚠️提醒：仅健康科普，不能替代眼科医生检查。"""
            else:
                sys_prompt = """You are teen eye health assessment expert. Generate eye report.
Format:
### 👁️ Teen Eye Assessment Result
**Info:**{user info}
**Risk: High ⚠️ / Medium ⚠️ / Low ✅**
analysis
### ✅ Advice
eye protection advice
⚠️ For reference only, not substitute for ophthalmologist examination."""

            report = call_deepseek(sys_prompt, content)
            # 根据返回结果自动展示风险色块
            if "高危" in report or "High ⚠️" in report:
                st.error("🔴 【高近视风险】")
            elif "中风险" in report or "Medium ⚠️" in report:
                st.warning("🟠 【中度视疲劳风险】")
            else:
                st.info("🟢 【低风险】")
            # ========================================

            st.markdown(report)
            st.session_state.history_reports.append(report)
            st.download_button("📥 下载报告", report, file_name="青少年眼部健康报告.txt")
            st.markdown("</div>", unsafe_allow_html=True)
    elif eye_run and not eye_input.strip():
        st.warning(L["empty_warn"])
