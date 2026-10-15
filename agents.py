from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0
)

# 1.采集Agent：收集老人基础信息、用药、病史
def collect_agent(user_input:str):
    prompt = f"""你是信息采集智能体，收集老年人信息：姓名、年龄、基础疾病、正在服用药物。
    硬性规则：
1. 仅提取用户输入文本内明确给出的：姓名、年龄、基础疾病、正在服用的药品。输入框示例文字仅为填写模板，不能当作患者信息。
2. 只评估患者当前正在服用的药物之间的相互作用。用户没有提到的药物，不能作为当前正在使用的药物进行风险分析。
3. 对于用户没有服用的药物，如果需要提及，必须明确标注：【⚠️ 仅作为提醒：如果后续服用XX药，会产生风险，患者目前并未使用该药物】，不能混入当前用药风险列表。
4. 如果用户缺少年龄、疾病或正在服用的药品，则禁止生成完整评估报告，只提示用户补齐信息，严禁编造病史、编造用药清单。
5. 不要复用示例“张大爷”病例作为患者数据。
用户输入：{user_input}
输出整理后的结构化信息。"""
    res = llm.invoke(prompt)
    return res.content

# 2.档案Agent：保存/读取患者档案信息
def record_agent(info:str):
    prompt = f"""你是档案管理智能体，把下面患者信息整理成规范病历档案。
信息：{info}"""
    res = llm.invoke(prompt)
    return res.content

# 3.评估Agent：评估老人身体基础风险
def assess_agent(medical_record:str):
    prompt = f"""你是健康评估智能体，基于病历评估老年患者基础健康风险。
病历：{medical_record}"""
    res = llm.invoke(prompt)
    return res.content

#4.检索Agent：读取知识库，检索药品资料
def retrieve_agent(record:str, knowledge:str):
    prompt = f"""你是知识库检索智能体，根据患者病历，从知识库中查找相关药品、禁忌。
病历：{record}
知识库：{knowledge}"""
    res = llm.invoke(prompt)
    return res.content

#5.校验Agent：检查药物之间的相互作用
def check_agent(retrieval_result:str):
    prompt = f"""你是用药校验智能体，检查多种药物联用有没有冲突、不良反应。
检索内容：{retrieval_result}"""
    res = llm.invoke(prompt)
    return res.content

#6.预警Agent：生成风险警告，标注高危问题
def warning_agent(check_result:str):
    prompt = f"""你是风险预警智能体，识别用药高危风险，给出警告。
校验结果：{check_result}"""
    res = llm.invoke(prompt)
    return res.content

#7.报告Agent：汇总全部信息，生成最终用药安全报告
def report_agent(warning_info:str):
    prompt = f"""你是报告生成智能体，整理所有信息，输出一份通俗易懂的老年人多重用药安全报告。
风险预警内容：{warning_info}"""
    res = llm.invoke(prompt)
    return res.content
