import json
import requests
import re

import logging
import os
import sys
import regex


# logging.basicConfig(filename='claim_verifer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')






api_key = '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'

def gpt4o_mini_analysis(prompt):
    url = "https://cn2us02.opapi.win/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        "Authorization": 'Bearer ' + api_key,
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    res = response.json()
    res_content = res['choices'][0]['message']['content']
    return res_content






# 提取完整的JSON数据
def extract_complete_json(response_text):
    json_pattern = r'(\{(?:[^{}]|(?1))*\})'
    matches = regex.findall(json_pattern, response_text)
    if matches:
        try:
            for match in matches:
                json_data = json.loads(match)
                return json_data
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
    return None
























# output_file_path = "/workspaces/llmfnd/CV_result.json"



# Claim = "A video showing a shark swimming on a flooded highway during Hurricane Ian in Florida."
# Video_information = {
#     "Video_headline": "a shark swimming on a flooded highway",
#     "Video_transcript": "",
#     "Video_description_on_platform": "This video analyzes and debunks the photo of a shark allegedly swimming on a flooded highway.",
#     "Video_platform": "youtube",
#     "Video_date": "2023_08_07",
#     "Video_description_from_descriptor": "A video, including the shark on a flooded highway."
# }
# QA_CONTEXTS = {}


# # 定义要保存的数据
# data = {
#     "Claim": Claim,
#     "Video_information": Video_information,
#     "QA_CONTEXTS": QA_CONTEXTS
# }



# # 检查文件是否存在
# if not os.path.exists(output_file_path):
#     # 如果文件不存在，创建文件并写入一个空的JSON对象
#     with open(output_file_path, 'w') as file:
#         json.dump({}, file)

# print(f"文件已创建或已存在: {output_file_path}")













# ------------------------------------------ #
# Prompts for Claim Verifier 
# ------------------------------------------ #

def process_claim_verifier(Claim, Video_information, QA_CONTEXTS, output_file_path):

    logging.warning("\n" * 5)

    logging.warning("----------------------------------")
    logging.warning("--------- Claim Verifier ---------")
    logging.warning("----------------------------------")

    # 构建用于验证声明的提示
    # prompt_for_claim_verifier = f"""
    # {{
    #   "Claim": "{Claim}",
    #   "Video_information": {Video_information},
    #   "QA_CONTEXTS": {QA_CONTEXTS},
    #   "Task": "Based on the content of the Video_information and the QA_CONTEXTS, accurately and rigorously determine whether the claim is true or false. Can we determine the truthfulness of the claim based on the existing information? Please provide a reliability probability, and clearly answer 'Yes' (the existing information can determine the truthfulness) or 'No' (the existing information cannot determine the truthfulness). Answer 'Yes' only if the reliability probability is sufficiently high.",
    #   "Prediction": ""
    # }}

    # The final output should include only a reliability probability (0%~100%), and a 'Yes' or 'No' to indicate whether the existing information supports making a judgment on the claim's truthfulness. There should be only one 'Yes' or 'No', along with a reliability probability ranging from 0% to 100%.
    # """

    prompt_for_claim_verifier = f"""
{{
  "Claim": "{Claim}",
  "Video_information": {Video_information},
  "QA_CONTEXTS": {QA_CONTEXTS},
  "Task": "Based on the content of the Video_information and the QA_CONTEXTS, accurately and rigorously determine whether the existing information is sufficient to judge the truthfulness of the claim. Can we determine the truthfulness of the claim based on the existing information? Please provide a reliability probability, clearly answer 'Yes' (the existing information is sufficient to determine the truthfulness) or 'No' (the existing information is insufficient to determine the truthfulness), and provide a detailed reason for your judgment. Include specific evidence from the provided information to support your conclusion. Answer 'Yes' only if the reliability probability is sufficiently high.",
  "Output_Format": {{
    "CVResult": {{
      "Judgment": "Yes or No",
      "Confidence": "0%~100%",
      "Reason": "Detailed explanation for the judgment, including specific evidence from the provided information that explains why the information is sufficient or insufficient to determine the truthfulness of the claim"
    }}
  }}
}}
The final output must be in valid JSON format, strictly adhering to the structure specified in the 'Output_Format' field. Provide a 'Yes' or 'No' judgment, a reliability probability ranging from 0% to 100%, and a detailed reason explaining your judgment with specific evidence. Ensure that the entire response is a properly formatted JSON object.
"""


    # 获取声明验证的答案
    claim_verifier_answer = gpt4o_mini_analysis(prompt_for_claim_verifier)

    logging.info("################## Claim Verifier Input ##################")
    # logging.info("prompt_for_claim_verifier")
    logging.info(prompt_for_claim_verifier)

    logging.info("################## Claim Verifier Raw Output ##################")
    # logging.info("claim_verifier_answer")
    logging.info(claim_verifier_answer)

    # # 格式化声明验证的提示
    # format_prompt_for_claim_verifier = f"""
    # Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format.

    # The desired JSON structure:
    # {{
    #   "CVResult": {{
    #     "Judgment": "Yes or No",
    #     "Confidence": "0%~100%"
    #   }}
    # }}

    # The content to be converted:
    # {claim_verifier_answer}
    # """
    # 格式化声明验证的提示
    format_prompt_for_claim_verifier = f"""
Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format.

The desired JSON structure:
{{
  "CVResult": {{
    "Judgment": "Yes or No",
    "Confidence": "0%~100%",
    "Reason": "Concise explanation for the judgment"
  }}
}}

The content to be converted:
{claim_verifier_answer}
"""

    # logging.info("----------------------------------------------")
    # logging.info("format_prompt_for_claim_verifier")
    # logging.info(format_prompt_for_claim_verifier)

    # 获取格式化后的JSON答案
    json_claim_verifier_answer = gpt4o_mini_analysis(format_prompt_for_claim_verifier)

    # logging.info("----------------------------------------------")
    # logging.info("json_claim_verifier_answer")
    # logging.info(json_claim_verifier_answer)

    # 提取完整的JSON声明验证答案
    complete_json_claim_verifier_answer = extract_complete_json(json_claim_verifier_answer)



    # 确保文件是字典结构而不是列表
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r+') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # 确保现有数据是一个字典
    if not isinstance(existing_data, dict):
        existing_data = {}

    # 删除已有的 CVResult
    if "CVResult" in existing_data:
        del existing_data["CVResult"]

    # 追加新生成的声明验证答案
    existing_data.update(complete_json_claim_verifier_answer)

    # 保存更新后的内容到文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

    # logging.info("complete_json_claim_verifier_answer successfully appended to %s", output_file_path)

    # 提取 Judgement 和 Confidence 并进行转换
    judgment_str = complete_json_claim_verifier_answer["CVResult"]["Judgment"]
    confidence_str = complete_json_claim_verifier_answer["CVResult"]["Confidence"]

    judgment_bool = True if judgment_str.lower() == "yes" else False
    confidence_float = float(confidence_str.strip('%')) / 100.0

    return judgment_bool, confidence_float


















def check_usefulness(Claim, Video_information, question):


    logging.warning("------------------------------------------------------")
    logging.warning("--------- Check Generate Question Usefulness ---------")
    logging.warning("------------------------------------------------------")

    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        logging.info(f"################## Attempt {attempts + 1} ##################")
        
        prompt_for_usefulness_confirmation = f"""
{{
    "Claim": "{Claim}",
    "Video_information": {json.dumps(Video_information)},
    "Generated_Question": "{question}",
    "Task": "Evaluate if the generated question is useful for determining the authenticity of the Claim and Video_information to assess if they constitute misinformation. If the question addresses any aspect that helps in judging the truthfulness of the Claim and Video_information, it is considered useful. Provide your answer as 'yes' if the question is useful, and 'no' if it is not. Additionally, provide a reason explaining your assessment.",
    "Usefulness_Assessment": {{
        "Useful": "yes / no",
        "Reason": ""
    }}
}}
"""

        logging.info("################## Check Generate Question Usefulness Input ##################")
        logging.info(prompt_for_usefulness_confirmation)

        # 调用分析函数
        question_usefulness_confirmation = gpt4o_mini_analysis(prompt_for_usefulness_confirmation)

        logging.info("################## Check Generate Question Usefulness Output ##################")
        logging.info(question_usefulness_confirmation)

        prompt_for_format = f"""
Please convert the following text content into the specified JSON structure. 

The desired JSON structure:
{{
    "Usefulness_Assessment": {{
        "Useful": "yes / no",
        "Reason": ""
    }}
}}

The content to be converted:
{question_usefulness_confirmation}
"""

        # logging.info("################## JSON Format Conversion Input ##################")
        # logging.info(prompt_for_format)

        answer_format = gpt4o_mini_analysis(prompt_for_format)

        # logging.info("################## JSON Format Conversion Output ##################")
        # logging.info(answer_format)

        # 提取 JSON 数据
        json_useful = extract_complete_json(answer_format)

        if json_useful and 'Usefulness_Assessment' in json_useful:
            useful_value = json_useful['Usefulness_Assessment'].get('Useful', '').strip().lower()
            reason_value = json_useful['Usefulness_Assessment'].get('Reason', '').strip()
            # logging.info(f"Usefulness: {useful_value}, Reason: {reason_value}")

            if useful_value in ['yes', 'no']:
                return useful_value == 'yes'
        
        attempts += 1
    
    # 超过最大尝试次数，返回 False
    return False



# ------------------------------------------ #
# Prompts for the initial question generation
# ------------------------------------------ #




def generate_initial_question(Claim, Video_information, output_file_path):



    logging.warning("\n" * 5)

    logging.warning("------------------------------------------------")
    logging.warning("--------- Initial Question Generator ---------")
    logging.warning("------------------------------------------------")

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        # 初始问题生成的提示
        # prompt_for_initial_question = f"""
        # {{
        #   "Claim": "{Claim}",
        #   "Video_information": {json.dumps(Video_information)},
        #   "Task": "Based on the relevant information from the Video_information and Claim, generate a professional and detailed question that can help determine the authenticity of the video content and the Claim. The goal is to assess whether the Claim is a true statement or misinformation. The final output should be a single question, in one sentence, not exceeding 20 words.",
        #   "Initial_Question_Generation": {{
        #     "Question": ""
        #   }}
        # }}
        # """
        prompt_for_initial_questions = f"""
{{
    "Claim": "{Claim}",
    "Video_information": {json.dumps(Video_information)},
    "Task": "Based on the provided Video_information and Claim, generate a series of professional, detailed questions to comprehensively assess the authenticity of the video content and verify the accuracy of the Claim.",
    "Requirements": {{
        "1. Primary Question": {{
            "Description": "Generate 1 crucial question addressing the most significant or potentially dubious aspect of the Claim.",
            "Rule": "This question should target the core issue, most effectively validating the Claim and video content authenticity."
        }},
        "2. Secondary Questions": {{
            "Description": "Generate 2 to 4 secondary questions, each targeting a different potential point of contention in the Claim.",
            "Rules": [
                "Each secondary question should focus on Claim content not addressed by the primary question.",
                "Ensure secondary questions cover all potentially problematic aspects of the Claim.",
                "Secondary questions should be distinct, each addressing a different point of contention.",
                "The number of secondary questions should flexibly range from 2 to 4, based on the Claim's complexity and number of contentious points."
            ]
        }},
        "General Rules": [
            "Each question should be a complete sentence, not exceeding 20 words.",
            "Questions should be clear, specific, and directly aimed at verifying authenticity.",
            "Questions should consider the relevant context provided in the Video_information."
        ]
    }},
    "Analysis Steps": [
        "1. Carefully analyze the Claim, identifying all potential points of contention.",
        "2. Focus the primary question on the most critical or likely contentious point.",
        "3. Allocate remaining contentious points to secondary questions, ensuring comprehensive coverage.",
        "4. Determine the appropriate number of secondary questions (2-4) based on the quantity and significance of contentious points.",
        "5. Reference the Video_information to ensure questions are relevant to the video content.",
        "6. Review and refine each question according to the general rules."
    ],
    "Output Format": {{
        "Initial_Question_Generation": {{
            "Primary_Question": "",
            "Secondary_Questions": {{
                "Secondary_Question_1": "",
                "Secondary_Question_2": "",
                "Secondary_Question_3": "",
                "Secondary_Question_4": ""
            }}
        }}
    }},
    "Note": "When outputting, if fewer than 4 secondary questions are generated, please remove the excess 'Secondary_Question' fields."
}}
"""






        logging.info(f"################## Initial Questions Generator Input (Attempt {attempts + 1}) ##################")
        logging.info(prompt_for_initial_questions)

        # 使用 gpt4o_mini_analysis 生成初始问题
        initial_questions_answer = gpt4o_mini_analysis(prompt_for_initial_questions)

        logging.info(f"################## Initial Question Generator Raw Output (Attempt {attempts + 1}) ##################")
        logging.info(initial_questions_answer)


        # 格式化初始问题生成的提示
        prompt_for_initial_question_json = f"""
{{
    "Task": "Convert the provided question generation results into a structured JSON format.",
    "Input": {{
        "Content": "{initial_questions_answer}"
    }},
    "Output_Requirements": {{
        "Format": "Valid JSON",
        "Structure": {{
            "Initial_Question_Generation": {{
                "Primary_Question": "string",
                "Secondary_Questions": {{
                    "Secondary_Question_1": "string",
                    "Secondary_Question_2": "string",
                    "Secondary_Question_3": "string (if present)",
                    "Secondary_Question_4": "string (if present)"
                }}
            }}
        }}
    }},
    "Rules": [
        "1. Extract the primary question and all secondary questions from the input content.",
        "2. Ensure each question is a complete sentence and does not exceed 20 words.",
        "3. Include all secondary questions present in the input, up to a maximum of 4.",
        "4. If fewer than 4 secondary questions are present, omit the unused fields.",
        "5. Maintain the original wording of the questions as much as possible.",
        "6. Ensure the output is in valid JSON format with proper escaping of special characters."
    ],
    "Note": "The output should match the actual number of questions in the input, with a minimum of one primary question and two secondary questions, and a maximum of four secondary questions."
}}

Please process the input content and provide the output in the specified JSON structure without any additional explanations or examples.
"""

        # 使用gpt4o_mini_analysis转换为JSON格式
        json_initial_question_answer = gpt4o_mini_analysis(prompt_for_initial_question_json)

        # 提取完整的JSON结构
        complete_json_initial_question_answer = extract_complete_json(json_initial_question_answer)


        


        # 从字典中提取primary_question_answer
        primary_question_answer = complete_json_initial_question_answer.get('Initial_Question_Generation', {}).get('Primary_Question', '')

        # 从字典中提取secondary_questions
        secondary_questions = complete_json_initial_question_answer.get('Initial_Question_Generation', {}).get('Secondary_Questions', {})


        # 检查问题的有效性
        result = check_usefulness(Claim, Video_information, primary_question_answer)

        # logging.info(f"################## Usefulness Check Result (Attempt {attempts + 1}): {result}, Reason: {reason} ##################")

        if result:
            # 如果结果有效，退出循环
            logging.info("Generated question is useful.")
            break
        else:
            # 如果结果无效，增加尝试次数并重新生成
            logging.info("Generated question is not useful. Regenerating...")
            attempts += 1

    if attempts == max_attempts:
        logging.info("Maximum attempts reached. Returning the last generated question.")
    

    # logging.info(f"################## Complete JSON (Attempt {attempts + 1}) ##################")
    # logging.info(complete_json_initial_question_answer)

    # 确保文件是字典结构而不是列表
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r+') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # 确保现有数据是一个字典
    if not isinstance(existing_data, dict):
        existing_data = {}
    
    # 删除已有的Initial_Question_Generation键
    existing_data.pop("Initial_Question_Generation", None)

    # 追加新生成的问题
    existing_data.update(complete_json_initial_question_answer)

    # 保存更新后的内容到文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

    logging.info("Initial question has been generated and saved successfully.")

    # 返回生成的问题
    # return "Initial_Question_Generation", complete_json_initial_question_answer["Initial_Question_Generation"]["Question"]
    return "Initial_Question_Generation", primary_question_answer, secondary_questions

# Helper functions like gpt4o_mini_analysis, check_usefulness, and extract_complete_json would be defined here as well.





# ---------------------------------------------- #
# Prompts for the follow-up question generation
# ---------------------------------------------- #



def generate_follow_up_question(Claim, Video_information, QA_CONTEXTS, secondary_questions, output_file_path):


    logging.warning("\n" * 5)

    logging.warning("------------------------------------------------")
    logging.warning("--------- Follow Up Question Generator ---------")
    logging.warning("------------------------------------------------")

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:


#         prompt_for_the_follow_up_question = f"""
# {{
#   "Claim": "{Claim}",
#   "Video_information": {json.dumps(Video_information)},
#   "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
#   "Task": "To verify the Claim, generate a professional and detailed follow-up question based on the relevant information from the Claim and Video_information, which are our fundamental sources for identifying misinformation. QA_CONTEXTS are previous QA pairs that can serve as a reference. The goal is to determine the next step in assessing the authenticity of the Claim and Video_information. The final output should be a single question, in one sentence, not exceeding 20 words.",
#   "Important Note": "Ensure that the new question is distinct from previous ones in QA_CONTEXTS. Focus on generating a novel question that explores a new aspect or angle of the Claim that has not been addressed in previous questions.",
#   "Final Task": "Generate a unique, non-repetitive question based on Claim, Video_information, and QA_CONTEXTS to help determine the authenticity of this 'Claim'. The question should provide a fresh perspective on the investigation, avoiding any duplication of previously asked questions."
# }}
# """


#         prompt_for_the_follow_up_question = f"""
# {{
#   "Claim": "{Claim}",
#   "Video_information": {json.dumps(Video_information)},
#   "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
#   "Secondary_Questions": {json.dumps(secondary_questions)},
#   "Task": "To verify the Claim, generate a professional and detailed follow-up question based on the relevant information from the Claim, Video_information, and QA_CONTEXTS, which are our fundamental sources for identifying misinformation. QA_CONTEXTS are previous QA pairs that can serve as a reference. The goal is to determine the next step in assessing the authenticity of the Claim and Video_information.",
#   "Important Note": "Ensure that the new question is distinct from previous ones in QA_CONTEXTS. QA_CONTEXTS can be used as a reference, but the new question must not duplicate any of the previous questions. You can choose a question from Secondary_Questions or generate a new question as long as it does not repeat any existing questions in QA_CONTEXTS.",
#   "Final Task": "Select a unique question from Secondary_Questions or generate a new, non-repetitive question based on Claim, Video_information, and QA_CONTEXTS to help determine the authenticity of this 'Claim'. The question should provide a fresh perspective on the investigation, avoiding any duplication of previously asked questions. Ensure the question is specific, relevant, and concise, not exceeding 20 words."
# }}
# """


        prompt_for_the_follow_up_question = f"""
{{
  "Claim": "{Claim}",
  "Video_information": {json.dumps(Video_information)},
  "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
  "Secondary_Questions": {json.dumps(secondary_questions)},
  "Task": "Generate a professional and detailed follow-up question to verify the Claim, utilizing the provided information sources.",
  "Information Sources": [
    "1. Claim: The statement being investigated",
    "2. Video_information: Details about the video related to the claim",
    "3. QA_CONTEXTS: Previous question-answer pairs serving as reference"
  ],
  "Question Generation Methods": [
    {{"Method 1: Select from Secondary_Questions": [
      "- Review the provided Secondary_Questions list",
      "- Choose the most relevant question that addresses current information gaps",
      "- Ensure the selected question is not a duplicate of any in QA_CONTEXTS",
      "- The chosen question should provide a fresh perspective on the investigation"
    ]}},
    {{"Method 2: Generate a New Question": [
      "- Analyze Claim, Video_information, and QA_CONTEXTS thoroughly",
      "- Identify aspects of the Claim that haven't been addressed or need further clarification",
      "- Formulate a new, targeted question that explores these unexplored angles",
      "- Ensure the new question is unique and not present in QA_CONTEXTS"
    ]}}
  ],
  "Guidelines for Both Methods": [
    "- The question must help assess the authenticity of the Claim and Video_information",
    "- Avoid any duplication with questions in QA_CONTEXTS",
    "- Provide a fresh perspective that advances the investigation",
    "- Keep the question specific, relevant, and concise (max 20 words)",
    "- Focus on aspects that are crucial for identifying potential misinformation"
  ],
  "Output Requirements": [
    "A single, well-formulated question that meets all the above criteria. The question should provide a fresh perspective on the investigation, avoiding any duplication of previously asked questions. Ensure the question is specific, relevant, and concise, not exceeding 20 words."
  ]
}}
"""



        logging.info(f"################## Follow Up Question Input (Attempt {attempts + 1}) ##################")
        logging.info(prompt_for_the_follow_up_question)

        # 使用gpt4o_mini_analysis生成跟进问题
        follow_up_question_answer = gpt4o_mini_analysis(prompt_for_the_follow_up_question)

        logging.info(f"################## Follow Up Question Output (Attempt {attempts + 1}) ##################")
        logging.info(follow_up_question_answer)

        # 检查问题的有效性
        result = check_usefulness(Claim, Video_information, follow_up_question_answer)

        if result:
            # 如果结果有效，退出循环
            logging.info("Generated follow-up question is useful.")
            break
        else:
            # 如果结果无效，增加尝试次数并重新生成
            logging.info("Generated follow-up question is not useful. Regenerating...")
            attempts += 1

    if attempts == max_attempts:
        logging.info("Maximum attempts reached. Returning the last generated follow-up question.")

    # 格式化跟进问题生成的提示
    prompt_for_follow_up_question_formatting = f"""
    Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format. The final output should be a single question, in one sentence, not exceeding 30 words.

    The desired JSON structure:
    {{
      "Follow_Up_Question_Generation": {{
        "Question": ""
      }}
    }}

    The content to be converted:
    {follow_up_question_answer}
    """


    # 使用gpt4o_mini_analysis转换为JSON格式
    json_follow_up_question_answer = gpt4o_mini_analysis(prompt_for_follow_up_question_formatting)


    # 提取完整的JSON结构
    complete_json_follow_up_question_answer = extract_complete_json(json_follow_up_question_answer)



    # 检查文件是否存在，如果存在则读取现有内容
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r+', encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # 确保现有数据是一个字典
    if not isinstance(existing_data, dict):
        existing_data = {}

    # 确定新的键名
    counter = 1
    new_key = f"Follow_Up_Question_{counter}"
    while new_key in existing_data:
        if all(k in existing_data[new_key] for k in ['Question', 'Answer', 'Confidence']):
            counter += 1
            new_key = f"Follow_Up_Question_{counter}"
        else:
            break

    # 删除已有的Follow_Up_Question_{counter}键
    existing_data.pop(f"Follow_Up_Question_{counter}", None)

    # 修改键名
    complete_json_follow_up_question_answer = {
        new_key: complete_json_follow_up_question_answer["Follow_Up_Question_Generation"]
    }

    # 追加新生成的问题
    existing_data.update(complete_json_follow_up_question_answer)

    # 保存更新后的内容到文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

    logging.info("Follow-up question has been generated and saved successfully.")

    return new_key, complete_json_follow_up_question_answer[new_key]["Question"]




















# ------------------------------- #
# Prompts for Validator
# 我能理解这个的作用是判断当前的
# ------------------------------- #



# 分析结果并提取yes或no

def analyze_string_yes_no(answer):
    # 去除标点符号，并转换为小写
    answer = re.sub(r'[^\w\s]', '', answer).lower()
    words = answer.split()
    
    # 如果只有一个单词，并且是 "yes" 或 "no"
    if len(words) == 1 and (words[0] == "yes" or words[0] == "no"):
        return words[0]
    else:
        return "neither"




def get_validator_result(Claim, Video_information, QA_CONTEXTS):


    logging.warning("\n" * 5)

    logging.warning("--------------------------------")
    logging.warning("--------- QA Validator ---------")
    logging.warning("--------------------------------")

    # 生成prompt
    prompt_for_validator = f"""
{{
    "Claim": "{Claim}",
    "Video_information": {json.dumps(Video_information)},
    "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
    "Task": "Based on the QA_CONTEXTS, determine if there is enough information to establish whether the Claim is true or false. Provide your answer in the 'QApairIsUseful' section. Answer 'yes' if the Question_Answer pair is valuable for verifying the Claim's accuracy, or 'no' if it is not valuable. Additionally, provide a detailed and specific reason for your answer."
    "QApairIsUseful": {{
        "Useful": "yes / no",
        "Reason": ""
    }}
}}
"""


 # 初始化循环次数
    max_attempts = 5
    attempts = 0
    true_json_answer = None

    while attempts < max_attempts:
        attempts += 1

        logging.info(f"################## QA Validator Input (Attempt {attempts}) ##################")
        logging.info(prompt_for_validator)

        # 调用模型分析并获取答案
        answer = gpt4o_mini_analysis(prompt_for_validator)

        logging.info(f"################## QA Validator Output (Attempt {attempts}) ##################")
        logging.info(answer)

        prompt_for_format = f"""
Please convert the following text content into the specified JSON structure. 

The desired JSON structure:
{{
    "QApairIsUseful": {{
        "Useful": "yes / no",
        "Reason": ""
    }}
}}

The content to be converted:
{answer}
"""

        # logging.info(f"################## Formatting Input (Attempt {attempts}) ##################")
        # logging.info(prompt_for_format)

        # 获取最终的yes或no结果
        json_answer = gpt4o_mini_analysis(prompt_for_format)

        true_json_answer = extract_complete_json(json_answer)

        # logging.info(f"################## Formatted Output (Attempt {attempts}) ##################")
        # logging.info(json_answer)


        if true_json_answer and true_json_answer.get("QApairIsUseful", {}).get("Useful") == "yes":
            return True
        elif true_json_answer and true_json_answer.get("QApairIsUseful", {}).get("Useful") == "no":
            return False
        else:
            continue

    # 如果循环达到最大次数，返回False
    return False















def validate_json_structure(json_data):
    # 验证JSON结构是否符合预期格式
    if not isinstance(json_data, dict):
        return False

    final_judgement = json_data.get("Final_Judgement")
    if not final_judgement:
        return False

    answer = final_judgement.get("Answer")
    reasons = final_judgement.get("Reasons")
    claim_authenticity = final_judgement.get("Therefore, the Claim authenticity is")
    info_type = final_judgement.get("The information type is")

    if answer == "True":
        return reasons and claim_authenticity == "True" and info_type == "Real" and "The specific type of False Information is" not in final_judgement

    if answer == "False":
        false_info_type = final_judgement.get("The specific type of False Information is")
        return reasons and claim_authenticity == "False" and info_type == "False" and false_info_type

    return False

# ------------------------------- #
# Prompts for Reasoner
# ------------------------------- #


def process_claim_final(Claim, Video_information, QA_CONTEXTS, output_file_path):
    # Prompts for Reasoner


    logging.warning("\n" * 5)

    logging.warning("----------------------------------")
    logging.warning("--------- Final Reasoner ---------")
    logging.warning("----------------------------------")


#     prompt_for_reasoner = f"""
# {{
#   "Claim": "{Claim}",
#   "Video_information": {Video_information},
#   "QA_CONTEXTS": {QA_CONTEXTS},
#   "Task": "Is this Claim true or false considering the provided Video information? And which information type does it belong to: Real, Unverified, Outdated, or False? If 'False,' specify the type: False video description, Video Clip Edit, Computer-generated Imagery, False speech, Staged Video, Text-Video Contradictory, Text unsupported by the video. Please provide your reasoning process. Ensure the final answer addresses all the following aspects: Answer, Reasons, Therefore, the Claim authenticity is, The information type is, If it is false, the specific type of False Information is.",
#   "Output_Answer_Format": {{
#     "Answer": "",
#     "Reasons": "",
#     "Therefore, the Claim authenticity is": "",
#     "The information type is": "",
#     "If it is false, the specific type of False Information is": ""
#   }},
# "Please Note": "Make sure to address Answer, Reasons, Therefore, the Claim authenticity is, The information type is, If it is false, the specific type of False Information is, specifically based on the provided Video information."
# }}
# """


    prompt_for_reasoner = f"""
{{
  "Claim": "{Claim}",
  "Video_information": {Video_information},
  "QA_CONTEXTS": {QA_CONTEXTS},
  "Task": "Is this Claim true or false considering the provided Video information? And which information type does it belong to: Real, Unverified, Outdated, or False? If 'False,' specify the type: False video description, Video Clip Edit, Computer-generated Imagery, False speech, Staged Video, Text-Video Contradictory, Text unsupported by the video. Please provide your reasoning process. Ensure the final answer addresses all the following aspects: Answer, Reasons, Therefore, the Claim authenticity is, The information type is, If it is false, the specific type of False Information is.",
  "Output_Answer_Format": {{
    "Answer": "",
    "Reasons": "",
    "Therefore, the Claim authenticity is": "",
    "The information type is": "",
    "If it is false, the specific type of False Information is": ""
  }},
  "Please Note": "Make sure to address Answer, Reasons, Therefore, the Claim authenticity is, The information type is, If it is false, the specific type of False Information is, specifically based on the provided Video information.",
  "Evidence Citation Guidelines": {{
    "1. Reference Format": "For each argument or piece of information used, add the referenced evidence number after it.",
    "2. Citation Format": "Use the format [Question_type Question_number_Query number_evidence number] for your references. For example:",
      "- Initial Question Generation": "[Initial_Question_Generation_Query X_evidenceY]",
      "- Follow Up Questions": "[Follow_Up_Question_Z_Query X_evidenceY]",
      "Where X is the query number, Y is the evidence number, and Z is the follow-up question number.",
    "3. Comprehensive Referencing": "Ensure that every piece of information drawn from the provided evidence is properly referenced.",
    "4. Answer Quality": "Strive for a comprehensive yet concise answer that directly addresses the question while incorporating relevant evidence.",
    "5. Output Inclusion": "When citing evidence in the final output, include the full reference tag (e.g., [Follow_Up_Question_1_Query 1_evidence_2]) in the 'Reasons' section of the Output_Answer_Format."
  }}
}}
"""


    attempt = 0
    max_attempts = 3
    true_json_answer = {}

    while attempt < max_attempts:
        attempt += 1
        answer = gpt4o_mini_analysis(prompt_for_reasoner)

        logging.info(f"################## Final Reasoner Input (Attempt {attempt}) ##################")
        logging.info(prompt_for_reasoner)

        answer = gpt4o_mini_analysis(prompt_for_reasoner)

        logging.info(f"################## Final Reasoner Raw Output (Attempt {attempt}) ##################")
        logging.info(answer)


        

        # 格式化初始问题生成的提示
        prompt_for_format = f"""
        Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format.

        First, determine whether the claim is True or False.

        For True claims, use the following JSON structure:
        {{
        "Final_Judgement": {{
        "Answer": "True",
        "Reasons": "{{{{reasons}}}}",
        "Therefore, the Claim authenticity is": "True",
        "The information type is": "Real"
        }}
        }}

        For False claims, use the following JSON structure:
        {{
        "Final_Judgement": {{
        "Answer": "False",
        "Reasons": "{{{{reasons}}}}",
        "Therefore, the Claim authenticity is": "False",
        "The information type is": "False",
        "The specific type of False Information is": "{{{{false_info_type}}}}"
        }}
        }}

        If the claim is False, please choose the specific type of False Information from the following options:
        False video description, Video Clip Edit, Computer-generated Imagery, False speech, Staged Video, Text-Video Contradictory, Text unsupported by the video, Other.

        Content to be converted:
        {answer}

        Please Note: The final task is to first determine the authenticity of the claim. If it is True, only the "Reasons" field needs to be filled. If it is False, the "Reasons" field should be filled, and the "The specific type of False Information" field should be selected.
        """

        # 使用 gpt4o_mini_analysis 将结果转换为 JSON 格式
        json_answer = gpt4o_mini_analysis(prompt_for_format)
        true_json_answer = extract_complete_json(json_answer)

        # 检查提取和验证是否成功
        if validate_json_structure(true_json_answer):
            break



    # 确保文件是字典结构而不是列表
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r+') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # 确保现有数据是一个字典
    if not isinstance(existing_data, dict):
        existing_data = {}

    # 追加新生成的数据
    existing_data.update(true_json_answer)

    # 保存更新后的内容到文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

    logging.info("The claim processing result has been generated and successfully saved.")


    # 返回处理结果
    return true_json_answer



