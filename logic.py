import random
import re
import anthropic

# Minimax Configuration
# Using the Domestic Version Endpoint (Anthropic Compatible)
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic" 
MINIMAX_MODEL = "MiniMax-M2.1" 

PATTERNS = {
    "P1": "日期函数转换 (TO_DATE -> TO_TIMESTAMP_NTZ)",
    "P2": "全角符号清洗 (Full-width -> Half-width)",
    "P3": "Null 处理 (Empty String -> SetNull)",
    "P4": "综合实战 (Mixed)"
}

QUESTIONS = {
    "P1": [
        "SELECT TO_DATE('2023-01-01', 'YYYY-MM-DD') FROM T_SALES;",
        "INSERT INTO T_LOGS VALUES (TO_DATE('2023/05/20', 'YYYY/MM/DD'));",
        "UPDATE T_CUST SET BIRTH_DATE = TO_DATE('19900101', 'YYYYMMDD');"
    ],
    "P2": [
        "SELECT * FROM T_A WHERE ID ＝ '123';",
        "SELECT * FROM T_B WHERE PRICE ＞ 1000;",
        "SELECT NAME FROM T_C WHERE (ID ＝ 1 OR ID ＝ 2);"
    ],
    "P3": [
        "If Link.Col1 = \"\" Then ...",
        "If Trim(Link.Name) = \"\" Then ...",
        "StageVar = If Link.Date = \"\" Then ... Else ..."
    ],
    "P4": [
        "SELECT TO_DATE('2023-01-01') FROM T_A WHERE ID ＝ '999';",
        "If Link.Date = \"\" Then Result = TO_DATE('20220101') ...",
        "UPDATE T_X SET VAL = 'A' WHERE CODE ＞ 50 AND DATE_COL = TO_DATE('2023-12-31');"
    ]
}

def get_client(api_key):
    """Returns an Anthropic client configured for Minimax (Domestic)."""
    # Note: The Anthropic SDK might auto-append /messages, but we set base_url to include /v1 
    # based on standard conventions. If Minimax expects /anthropic/messages, we might need adjustment.
    # The user provided "https://api.minimaxi.com/anthropic" as baseUrl.
    # Standard Anthropic base is "https://api.anthropic.com/v1".
    # So we try "https://api.minimaxi.com/anthropic/v1" first.
    return anthropic.Anthropic(
        api_key=api_key, 
        base_url=MINIMAX_BASE_URL
    )

def extract_text_content(message):
    """Helper to extract text from Anthropic response blocks."""
    content = ""
    for block in message.content:
        if block.type == 'text':
            content += block.text
    return content

def generate_question(pattern_type):
    """Generates a random question based on the selected pattern (Mock/Legacy)."""
    if pattern_type in QUESTIONS:
        return random.choice(QUESTIONS[pattern_type])
    return "Invalid Pattern Selected"

def generate_question_with_ai(api_key, pattern_type):
    """Generates a question using Minimax AI via Anthropic SDK."""
    client = get_client(api_key)
    
    prompt = f"""
    你是一个高级 ETL 工程师。请根据用户选择的模式 '{pattern_type} - {PATTERNS.get(pattern_type, "Unknown")}'，生成一段 有问题的 Oracle SQL 或 DataStage 伪代码。
    
    要求：
    1. 代码必须包含需要迁移的旧语法。
    2. 不要直接给出答案，只给出题目代码本身，不要包含 "```sql" 等 markdown 格式标记，只返回纯文本代码。
    3. 场景要贴近真实金融/零售业务（使用 T_SALES, T_CUST 等表名）。
    4. 只需要生成 1-3 行代码。
    """

    try:
        response = client.messages.create(
            model=MINIMAX_MODEL,
            max_tokens=1000,
            system="你是一个专业的代码出题助手。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return extract_text_content(response).strip()
    except Exception as e:
        return f"AI Generation Error: {str(e)}"

def check_answer(pattern_type, user_code):
    """
    Validates the user's code based on the pattern rules using Regex (Mock/Legacy).
    Returns (is_correct, feedback_message)
    """
    is_correct = True
    feedback = []

    # Check P1: TO_DATE should be replaced by TO_TIMESTAMP_NTZ
    if pattern_type in ["P1", "P4"]:
        if "TO_DATE" in user_code.upper():
            is_correct = False
            feedback.append("❌ found 'TO_DATE'. Please use 'TO_TIMESTAMP_NTZ' for Snowflake.")
        elif "TO_TIMESTAMP_NTZ" not in user_code.upper():
             pass

    # Check P2: Full-width characters
    if pattern_type in ["P2", "P4"]:
        full_width_chars = ['＝', '＞', '＜', '（', '）', '，', '；']
        found_chars = [char for char in full_width_chars if char in user_code]
        if found_chars:
            is_correct = False
            feedback.append(f"❌ Found full-width characters: {', '.join(found_chars)}. Please convert to half-width.")

    # Check P3: Empty string logic for DataStage
    if pattern_type in ["P3", "P4"]:
        if re.search(r'=\s*""', user_code) or re.search(r"=\s*''", user_code):
             is_correct = False
             feedback.append("❌ Found explicit empty string comparison. Use 'IsNull()' or 'SetNull()' logic.")

    if is_correct:
        return True, "✅ PASS: Code looks good!"
    else:
        return False, "\n".join(feedback)

def check_answer_with_ai(api_key, pattern_type, question_code, user_code):
    """Validates the user's code using Minimax AI via Anthropic SDK."""
    client = get_client(api_key)
    
    prompt = f"""
    任务：检查用户是否将代码正确迁移到了 Snowflake/DataStage 新规范。
    
    当前题目模式：{pattern_type} - {PATTERNS.get(pattern_type, "Unknown")}
    原始题目代码：
    {question_code}
    
    用户提交的代码：
    {user_code}
    
    规范列表：
    - Oracle TO_DATE -> Snowflake TO_TIMESTAMP_NTZ
    - 全角符号 ＝＞（） -> 半角 ASCII
    - 空字符串 "" -> 必须显式转为 SetNull() 或 IsNull() 判断
    
    请判断：
    1. 如果符合所有规范，返回 'PASS'。
    2. 如果有遗漏，返回 'FAIL' 并用中文解释原因。
    
    请只返回状态和原因，格式如下：
    PASS
    (或)
    FAIL: 原因说明...
    """

    try:
        response = client.messages.create(
            model=MINIMAX_MODEL,
            max_tokens=1000,
            system="你是一个严格的代码审核员 (Code Reviewer)。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result = extract_text_content(response).strip()
        
        if result.startswith("PASS"):
            return True, "✅ " + result
        else:
            return False, "❌ " + result
            
    except Exception as e:
        return False, f"AI Review Error: {str(e)}"
