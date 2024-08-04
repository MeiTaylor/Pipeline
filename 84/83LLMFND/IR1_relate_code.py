import requests
import json
import difflib
import regex
import textwrap

from concurrent.futures import ThreadPoolExecutor


import requests
from bs4 import BeautifulSoup
import time
import random

import time
import logging
import os
import re

import re
import json
from dateutil.parser import parse
from datetime import datetime


import re
import json
from dateutil.parser import parse
from datetime import datetime
import logging
import requests
from threading import Lock, Semaphore
from concurrent.futures import ThreadPoolExecutor
import time
from collections import deque


# 创建一个全局锁对象和一个时间戳
process_google_search_lock = Lock()
last_call_time = 0


# 你的API密钥
api_key = 'sk-VEA93CzU9Fd892f859C8T3BLBKFJ9d70149fe12640739881'

# # Google搜索函数
# def google_search(question):
#     base_url = "https://cn2us02.opapi.win/api/v1/openapi/search/google-search/v1"
#     url = f"{base_url}?key={api_key}&q={question}"
    
#     headers = {
#         'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Authorization': 'Bearer ' + api_key,
#     }
    
#     response = requests.request("GET", url, headers=headers)
#     return response.text

# Google搜索函数
def google_search(question):
    base_url = "https://cn2us02.opapi.win/api/v1/openapi/search/google-search/v1"
    excluded_sites = (
        "www.snopes.com, www.factcheck.org, www.politifact.com, "
        "www.truthorfiction.com, fullfact.org, www.hoax-slayer.com, leadstories.com, "
        "www.opensecrets.org, www.washingtonpost.com/news/fact-checker, "
        "www.reuters.com/fact-check, apnews.com/APFactCheck, www.bbc.com/news/reality_check, "
        "factcheckni.org, facta.news, checkyourfact.com, africacheck.org, verafiles.org, "
        "maldita.es, correctiv.org, teyit.org"
    )
    
    # 构建请求 URL
    url = f"{base_url}?key={api_key}&q={question}&siteSearch={excluded_sites}&siteSearchFilter=e"
    
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + api_key,
    }
    
    response = requests.request("GET", url, headers=headers)
    return response.text



# gpt4o_mini分析函数
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



# gpt4o_analysis分析函数
def gpt4o_analysis(prompt):
    url = "https://cn2us02.opapi.win/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-4o",
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




# 定义一个函数来找到最相似的URL
def find_best_match(link, evaluation):
    best_match = None
    highest_ratio = 0
    for eval_url in evaluation:
        # SequenceMatcher的基本思想是找到不包含“junk”元素的最长连续匹配子序列（LCS）。
        # 这不会产生最小的编辑序列，但是会产生对人“看起来正确”的匹配
        ratio = difflib.SequenceMatcher(None, link, eval_url).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = eval_url
    return best_match, highest_ratio



def process_item(i, item):
    # 提取链接
    link = item.get('link')
    snippet = item.get('snippet')
    # 获取网页内容和字数
    content, content_tokens = get_content_and_word_count(link, snippet)
    # 添加网页内容和字数到item中
    item['website_content'] = {
        'content': content,
        'content_tokens': content_tokens
    }
    return {f'evidence{i}': item}


def process_google_search(query, output_file_path):
    # 调用谷歌搜索函数获取结果
    data = google_search(query)
    logging.info("Google search over")

    data = json.loads(data)

    # 使用线程池并行处理每个item
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_item, i, item) for i, item in enumerate(data.get('items', []))]
        new_items = [future.result() for future in futures]

    # 使用新的 items 结构更新数据字典
    data['items'] = new_items

    # 将更新后的数据字典写入文件
    with open(output_file_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)







def analyze_string(answer):
    # 去除标点符号，并转换为小写
    answer = re.sub(r'[^\w\s]', '', answer).lower()
    words = answer.split()
    
    # 统计 "yes" 和 "no" 的出现次数
    yes_count = words.count("yes")
    no_count = words.count("no")
    
    # 找到字符串的第一个单词
    first_word = words[0] if words else ""
    
    # 判断第一个单词是否是 "yes" 或 "no"
    first_word_is = "yes" if first_word == "yes" else "no" if first_word == "no" else "neither"
    
    # 计算最终结果
    final_result = "neither"  # 初始化 final_result

    if yes_count > no_count and first_word_is == "yes":
        final_result = "yes"
    elif yes_count < no_count and first_word_is == "no":
        final_result = "no"
    
    return final_result











def check_online_search_needed(claim, Video_information, QA_CONTEXTS, question, output_file_path):
    logging.info("Checking if online search is needed")
    prompt_for_information_retrieving_verifier = f"""
    {{
      "Claim": "{claim}",
      "Video_information": {json.dumps(Video_information)},
      "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
      "New_Question": {{
        "Question": "{question}"
      }},
      "Task": "To answer the question, is searching information online needed? Yes or no? Please provide a precise probability, and if the threshold is greater than 80%, give the result as 'Yes', otherwise give the result as 'No'.",
      "Prediction": ""
    }}
    
    Please note that the first word must be either yes or no
    """

    answer = gpt4o_mini_analysis(prompt_for_information_retrieving_verifier)
    final_result = analyze_string(answer)

    # 如果文件存在，读取文件中的现有数据
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {}

    # 更新数据并添加新的结果
    data["need_online_search"] = final_result

    # 将更新后的数据保存回文件
    with open(output_file_path, 'w') as file:
        json.dump(data, file)
    
    return final_result




def generate_and_format_queries(claim, Video_information, QA_CONTEXTS, question, output_file_path):
    logging.info("Generating and formatting queries")
    # 构建用于生成查询的提示
    prompt_for_queries_generation = f"""
{{
  "Claim": "{claim}",
  "Video_information": {json.dumps(Video_information)},
  "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
  "New_Question": {{
    "Question": "{question}"
  }},
  "Task": "In order to better answer the 'Question': '{question}', please determine what information is required and design two new queries to search for this information on Google. These two queries should be specifically aimed at retrieving relevant information from the web to better answer the 'Question': '{question}'. Please note that the generated queries should not exceed two, and they should focus on different aspects and not be repetitive. The above 'Claim', 'Video_information', and 'QA_CONTEXTS' are just background information and  the queries should focus on answering 'the new question'. Ensure that the queries are in the format suitable for entering into a Google search.",
  "Queries": {{
    "Query1": "",
    "Query2": ""
  }}
}}
"""
    

    # logging.info("Prompts for Queries Generation")
    # logging.info(prompt_for_queries_generation)

    # 生成查询
    # query_answer = gpt4o_mini_analysis(prompt_for_queries_generation)
    query_answer = gpt4o_mini_analysis(prompt_for_queries_generation)

    # 构建用于格式化查询的提示
    prompt_for_query_format = f"""
Please convert the following text content into the specified JSON structure without altering the original query content. Ensure the output is in JSON format.

The desired JSON structure:
{{
  "Queries": {{
    "Query1": "",
    "Query2": ""
  }}
}}

The content to be converted:
{query_answer}
"""


    # 格式化查询答案为 JSON 结构
    # query_json_answer = gpt4o_mini_analysis(prompt_for_query_format)
    query_json_answer = gpt4o_mini_analysis(prompt_for_query_format)
    query_complete_json_answer = extract_complete_json(query_json_answer)

    logging.info("Query Complete JSON Answer")
    logging.info(query_complete_json_answer)

    # 读取现有的 JSON 数据，更新并写回文件
    with open(output_file_path, 'r', encoding='utf-8') as file:
        full_data = json.load(file)
        full_data.update(query_complete_json_answer)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)

    return query_complete_json_answer




def check_online_search_and_generate_queries(claim, Video_information, QA_CONTEXTS, question, output_file_path):



    logging.warning("---------------------------------------------------------")
    logging.warning("--------- Does the question need online search? ---------")
    logging.warning("---------- Generating search terms in English -----------")
    logging.warning("---------------------------------------------------------")


#     prompt_for_information_retrieving_verifier_and_queries_generation = f"""
# {{
#   "Claim": "{claim}",
#   "Video_information": {json.dumps(Video_information)},
#   "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
#   "New_Question": {{
#     "Question": "{question}"
#   }},
#   "Task": "To answer the question, is searching information online needed? Yes or no? If you believe the probability that online search is needed is greater than 80%, give the result as 'Yes' and generate two new queries to search for this information on Google. If the probability is 80% or less, give the result as 'No' and do not provide any queries. The queries should focus on different aspects and not be repetitive. The above 'Claim', 'Video_information', and 'QA_CONTEXTS' are just background information, and the queries should focus on answering the new question. Ensure that the queries are in the format suitable for entering into a Google search.",
#   "Prediction": {{
#     "need_online_search": "",
#     "Queries": {{
#       "Query1": "",
#       "Query2": ""
#     }}
#   }}
# }}
# """
    

#     prompt_for_information_retrieving_verifier_and_queries_generation = f"""
# {{
#   "Claim": "{claim}",
#   "Video_information": {json.dumps(Video_information)},
#   "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
#   "New_Question": {{
#     "Question": "{question}"
#   }},
#   "Task": "Determine if online information searching is needed to answer the new question. Consider the following criteria:

# 1. Online search is generally recommended for most questions to provide comprehensive and up-to-date information.
# 2. If the question can be fully and confidently answered using only the given 'Claim', 'Video_information', and 'QA_CONTEXTS', online search may not be necessary.
# 3. If the question specifically asks about details or content exclusively present in the video, online search may not be needed.
# 4. For any question that could benefit from additional context, background, or current information, online search is recommended.

# Based on these criteria, determine if online search is needed (Yes or No). If online search could potentially provide any useful information or context, even if not strictly necessary, choose 'Yes'. Only choose 'No' if the question is entirely about specific video content that cannot be found online.

# If the result is 'Yes', generate two new queries for Google Custom Search API. If 'No', do not provide any queries.

# If generating queries:
# - Ensure Query 1 and Query 2 focus on different aspects of the question and are not repetitive.
# - Each query should be concise (not exceeding 10 words) and suitable for Google Custom Search API.
# - Provide key terms that represent the core focus of each specific query. Key terms must be a single word.

# Note: The generated queries should be phrases suitable for Google Search.

# Output Format:
# "Prediction": {{
#     "need_online_search": "",
#     "reasoning": "Briefly explain the rationale behind the decision to search or not search online",
#     "Queries": {{
#       "Query1": {{
#         "query": "Concise search query (max 10 words) for one aspect, suitable for Google Search",
#         "key_terms": "Core word representing the main focus of this query. Key terms must be a single word."
#       }},
#       "Query2": {{
#         "query": "Different concise search query (max 10 words) for another aspect, suitable for Google Search",
#         "key_terms": "Core word representing the main focus, distinct from Query 1. Key terms must be a single word."
#       }}
#     }}
#   }}

# Example:
#   "Prediction": {{
#     "need_online_search": "Yes",
#     "reasoning": "To find the latest information on blockchain technology, an online search is necessary.",
#     "Queries": {{
#       "Query1": {{
#         "query": "Find the latest blog posts about 'blockchain technology.'",
#         "key_terms": "blockchain"
#       }},
#       "Query2": {{
#         "query": "Recent developments in blockchain technology",
#         "key_terms": "developments"
#       }}
#     }}
#   }}

#   "Prediction": {{
#     "need_online_search": "No",
#     "reasoning": "The question pertains specifically to the content shown in the video and requires video content analysis.",
#   }}
# }}
# """







    prompt_for_information_retrieving_verifier_and_queries_generation = f"""
{{
  "Claim": "{claim}",
  "Video_information": {json.dumps(Video_information)},
  "QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
  "New_Question": {{
    "Question": "{question}"
  }},
  "Task": "Determine if online information searching is needed to answer the new question. Consider the following criteria:

1. Online search is generally recommended for most questions to provide comprehensive and up-to-date information.
2. If the question can be fully and confidently answered using only the given 'Claim', 'Video_information', and 'QA_CONTEXTS', online search may not be necessary.
3. If the question specifically asks about details or content exclusively present in the video, online search may not be needed.
4. For any question that could benefit from additional context, background, or current information, online search is recommended.

Based on these criteria, determine if online search is needed (Yes or No).

If online search could potentially provide any useful information or context, even if not strictly necessary, choose 'Yes'. Only choose 'No' if the question is entirely about specific video content that cannot be found online.

If the result is 'Yes', generate two new queries for Google Custom Search API. If 'No', do not provide any queries.

Output Format:
**Analysis Process:**
If generating queries:
Generate the queries by following these steps, and output the result of each step. This will ensure that the output is well-considered:
Step 1: Generate the 'searching goals' to answer this question.
Step 2: Please generate 1 professional searching query for each goal used to perform a search using the Google Custom Search API. Based on the above 'searching goals'.
Generate output results for each step. This will ensure that the output is fully considered and well-structured.


"Prediction": {{
    "need_online_search": "",
    "reasoning": "Briefly explain the rationale behind the decision to search or not search online",
    "Queries": {{
      "Query1": {{
        "query": "Concise search query (max 10 words) for one aspect, suitable for Google Search",
        "searching_goal": "Provide detailed and specific explanations to clearly define the objectives that this query aims to achieve"
      }},
      "Query2": {{
        "query": "Different concise search query (max 10 words) for another aspect, suitable for Google Search",
        "searching_goal": "Provide detailed and specific explanations to clearly define the objectives that this query aims to achieve"
      }}
    }}
  }}
}}
Note: Both the two-step analysis process and the final JSON answer need to be outputted. The two-step analysis includes:
Step 1: Generate the 'searching goals' to answer this question.
Step 2: Please generate 1 professional searching query for each goal used to perform a search using the Google Custom Search API. Based on the above 'searching goals'.
"""






    logging.info("################## Online Search and Query Generation Input ##################")
    logging.info(prompt_for_information_retrieving_verifier_and_queries_generation)

    query_answer = gpt4o_mini_analysis(prompt_for_information_retrieving_verifier_and_queries_generation)

    logging.info("################## Online Search and Query Generation Raw Output ##################")
    logging.info(query_answer)

#     prompt_for_query_format = f"""
# Please convert the following text content into the specified JSON structure without altering the original query content. Ensure the output is in JSON format.

# The desired JSON structure for online search needed:
# {{
#   "Prediction": {{
#     "need_online_search": "Yes",
#     "Queries": {{
#       "Query1": "",
#       "Query2": ""
#     }}
#   }}
# }}

# The desired JSON structure for no online search needed:
# {{
#   "Prediction": {{
#     "need_online_search": "No"
#   }}
# }}

# The content to be converted:
# {query_answer}
# """



#     prompt_for_query_format = f"""
# Please convert the following text content into the specified JSON structure, preserving the original content as much as possible while ensuring the output conforms to the required format. The output must be valid JSON.

# The desired JSON structure for when online search is needed:
# {{
#   "Prediction": {{
#     "need_online_search": "Yes",
#     "reasoning": "",
#     "Queries": {{
#       "Query1": {{
#         "query": "",
#         "key_terms": ""
#       }},
#       "Query2": {{
#         "query": "",
#         "key_terms": ""
#       }}
#     }}
#   }}
# }}

# The desired JSON structure for when no online search is needed:
# {{
#   "Prediction": {{
#     "need_online_search": "No",
#     "reasoning": ""
#   }}
# }}

# Please ensure that:
# 1. The "need_online_search" value is either "Yes" or "No".
# 2. The "reasoning" field contains a brief explanation for the decision.
# 3. If "need_online_search" is "Yes", include both Query 1 and Query 2 with their respective "query" and "key_terms".
# 4. The generated queries should be phrases suitable for Google Search.
# 5. The key_terms should represent the core focus of each query. Key terms must be either a single word or a very short phrase.
# 6. Query 1 and Query 2 should focus on different aspects of the question.

# The content to be converted:
# {query_answer}
# """


    prompt_for_query_format = f"""
Please convert the following text content into the specified JSON structure, preserving the original content as much as possible while ensuring the output conforms to the required format. The output must be valid JSON.

The desired JSON structure for when online search is needed:
{{
  "Prediction": {{
    "need_online_search": "Yes",
    "reasoning": "",
    "Queries": {{
      "Query1": {{
        "query": "Concise search query (max 10 words) for one aspect, suitable for Google Search",
        "searching_goal": "Provide detailed and specific explanations to clearly define the objectives that this query aims to achieve"
      }},
      "Query2": {{
        "query": "Different concise search query (max 10 words) for another aspect, suitable for Google Search",
        "searching_goal": "Provide detailed and specific explanations to clearly define the objectives that this query aims to achieve"
      }}
    }}
  }}
}}

The desired JSON structure for when no online search is needed:
{{
  "Prediction": {{
    "need_online_search": "No",
    "reasoning": ""
  }}
}}

Please ensure that:
1. The "need_online_search" value is either "Yes" or "No".
2. The "reasoning" field contains a brief explanation for the decision.
3. If "need_online_search" is "Yes", include both Query 1 and Query 2 with their respective "query" and "searching_goal".
4. The generated queries should be phrases suitable for Google Search.
5. The searching_goal should specify the objective the query aims to achieve.

The content to be converted:
{query_answer}
"""


    query_json_answer = gpt4o_mini_analysis(prompt_for_query_format)

    # logging.info("prompt_for_information_retrieving_verifier_and_queries_generation JSON ANSWER")
    # logging.info(query_json_answer)


    query_complete_json_answer = extract_complete_json(query_json_answer)


    # 读取现有的 JSON 数据，更新并写回文件
    with open(output_file_path, 'r', encoding='utf-8') as file:
        full_data = json.load(file)
        full_data.update(query_complete_json_answer)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)

    return query_complete_json_answer






def process_query_and_quality_score_value(query, key_terms, claim, Video_information, QA_CONTEXTS, question, output_file_path):
    logging.warning("-----------------------------------------------------")
    logging.warning("---------------- Google Search Terms ----------------")
    logging.warning("------------- Evaluating Website Quality ------------")
    logging.warning("-----------------------------------------------------")



    process_google_search(query, output_file_path)

    with open(output_file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    # 提取所有的 'displayLink' 值
    display_links = []
    for evidence in data.get('items', []):
        for key, item in evidence.items():
            if isinstance(item, dict):
                display_link = item.get('displayLink')
                if display_link:
                    display_links.append(display_link)

    # logging.info("display_links")
    # logging.info(display_links)


    prompt = f"""
{{
"Claim": "{claim}",
"Video_information": {Video_information},
"QA_CONTEXTS": {QA_CONTEXTS},
"Relate_Website": {display_links},
"Task": "Based on the provided Claim, Video_information, and QA_CONTEXTS, evaluate the listed websites to determine which ones have high credibility in terms of truthfulness and accuracy, and can aid in detecting fake news. Please provide a quality score (website_quality) out of 10 for each website and explain the reasoning for the score. The evaluation criteria include the website's overall reliability, historical accuracy, and capability to detect and expose fake news.

Please combine the evaluations for these aspects to give an overall quality score (website_quality) for each website, and provide detailed explanations for each score."
}}
In your response, when referring to related websites, be sure to provide the original name of the specific and detailed website in Relate_Website, and do not modify this name.
It is required to rate and explain the reasons for all websites. Each website should be rated an overall quality score (website_quality) out of 10, with detailed explanations for each score.
"""





    max_iterations = 3
    iterations = 0

    while iterations < max_iterations:
        logging.info(f"################## Google Search Terms Input (Attempt {iterations}) ##################")
        logging.info(prompt)

        # 获取gpt4o_mini的分析结果
        answer = gpt4o_mini_analysis(prompt)


        logging.info(f"################## Google Search Terms Output (Attempt {iterations}) ##################")
        logging.info(answer)

        # 构建gpt4o_mini的格式转换提示
        prompt_for_format = f"""
    Please convert the following text content into JSON format. For each website, use the following format:
    {{
        "website": {{
        "website_qualityScore": "quality_score_value",
        "justification": "justification_text"
        }}
    }}

    Note: 
    - "quality_score_value" should be an integer between 0 and 10.
    - "justification" should be a string.

    Website represents the current website URL for rating and evaluation, rather than the word "website", preferably with a complete link via HTTP or HTTPS. For each website, quality_score_value, relevances_score_value, and newness_score_value are integers that represent the website's ratings in terms of quality, relevance, and novelty, ranging from 1 to 10. Justification_text is a string that provides reasons and explanations for the rating.
    The following is the text content that needs to be converted:
    {answer}
    """

        # 获取格式化的JSON结果
        answer_format = gpt4o_mini_analysis(prompt_for_format)

        # 提取评价信息
        evaluation = extract_complete_json(answer_format)
        # logging.info("rating and evaluation")
        # logging.info(evaluation)

        if not evaluation:
            logging.error("未能提取有效的JSON格式评价信息，重新获取GPT-3.5的分析结果。")
            iterations += 1
            continue  # 重新开始while循环

        # 初始化 match_count 和 total_items
        match_count = 0
        total_items = 0

        # 遍历所有的 items 并处理每个 evidence
        for evidence in data.get('items', []):
            total_items += 1  # 每遍历一个 item，total_items 加 1
            for key, item in evidence.items():
                if isinstance(item, dict):
                    display_link = item.get('displayLink')
                    if display_link:
                        best_match, ratio = find_best_match(display_link, evaluation)
                        # logging.info(f"Display Link: {display_link}, Best Match: {best_match}, Ratio: {ratio}")
                        if ratio > 0.6:  # 设定一个相似度阈值，可以根据需要调整
                            item['website_quality_evaluation'] = evaluation[best_match]
                            match_count += 1

        if match_count == total_items:
            break  # 如果所有的items都匹配到了评价信息，则跳出while循环

        iterations += 1

    if iterations == max_iterations:
        logging.error("在最大尝试次数内未能成功匹配所有评价信息。")


    # 将更新后的数据写回output_file_pathjson文件
    updated_single_query_path = output_file_path.replace(".json", "_updated.json")
    with open(updated_single_query_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)











    

def process_newness(file_path):

    def extract_date_from_snippet(snippet):
        match = re.search(r'(\b\w+\b \d{1,2}, \d{4})', snippet)
        if match:
            try:
                date = parse(match.group(1), fuzzy=True).date()
                return date
            except ValueError:
                return None
        return None

    def extract_date_from_metatags(metatags):
        date_keys = ['article:published_time', 'sort_date']
        for tag in metatags:
            for key in date_keys:
                if key in tag:
                    date_str = tag[key]
                    try:
                        date = parse(date_str, fuzzy=True).date()
                        return date
                    except ValueError:
                        pass
        return None

    def extract_dates_from_items(items):
        evidence_dates = {}
        for item in items:
            for evidence_key, evidence in item.items():
                # 提取 snippet 中的时间信息
                snippet = evidence.get('snippet', '')
                date_from_snippet = extract_date_from_snippet(snippet)
                if date_from_snippet:
                    evidence_dates[evidence_key] = date_from_snippet
                    continue

                # 提取 metatags 中的时间信息
                pagemap = evidence.get('pagemap', {})
                metatags = pagemap.get('metatags', [])
                date_from_metatags = extract_date_from_metatags(metatags)
                if date_from_metatags:
                    evidence_dates[evidence_key] = date_from_metatags
                    continue

                # 默认日期为None
                evidence_dates[evidence_key] = None

        return evidence_dates

    def score_by_time_gradient(dates):
        now = datetime.now().date()
        gradients = [7, 15, 30, 90, 180, 365, 730]  # 以天为单位的梯度：一星期、半个月、30天、90天、半年、1年、两年
        scores = {}
        for evidence_key, date in dates.items():
            if date is None:
                scores[evidence_key] = 0
            else:
                diff_days = (now - date).days
                score = 1  # 默认为1分
                for i, gradient in enumerate(gradients):
                    if diff_days <= gradient:
                        score = 10 - i
                        break
                scores[evidence_key] = score
        return scores

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        items = data.get('items', [])
        evidence_dates = extract_dates_from_items(items)
        scores = score_by_time_gradient(evidence_dates)

        # 将日期和分数添加到 evidence 中
        for item in items:
            for evidence_key, evidence in item.items():
                date = evidence_dates.get(evidence_key, None)
                evidence['Newness'] = {
                    'NewnessScore': scores.get(evidence_key, 0),
                    'Date': date.isoformat() if date else 'No date found'
                }

        # 将修改后的数据写回到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Processed {file_path} successfully.")
        return True

    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"Failed to process {file_path}: {e}")
        return False




def process_evidence_and_Newness_Relevance(key, query, claim, Video_information, QA_CONTEXTS, question, updated_single_query_path):


    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        process_newness(updated_single_query_path)
        
        # 选择10个证据的部分信息进行下一步的证据选择
        evidence_json = process_evidence(updated_single_query_path)
    

        logging.warning("----------------------------------------------")
        logging.warning("--------- Evaluating Relevance Score ---------")
        logging.warning("----------------------------------------------")



        prompt_for_evidence_scores = f"""
{{
"Claim": "{claim}",
"Video_information": {json.dumps(Video_information)},
"QA_CONTEXTS": {json.dumps(QA_CONTEXTS)},
"New_Question": {{
    "Question": "{question}"
}},
"Current Evidence Searching queries on google": {{
    "{key}": "{query}"
}},
"Evidences": {json.dumps(evidence_json)},
"Task": "Based on the information of each evidence in 'Evidences', especially the content of website_content, evaluate the relevance of this evidence to the current question (RelevanceScore, 0~10 points, provide a score). Consider how closely the evidence addresses the specifics of the question '{question}', with a strong emphasis on how the evidence helps in determining whether the Claim and Video_information constitute false news. Evidence that significantly aids in judging the veracity of the Claim and Video_information should receive higher scores, while less relevant evidence should receive lower scores. The more the evidence helps in determining the truthfulness of the Claim and Video_information, the higher the RelevanceScore should be.

For each evidence (evidence0, evidence1, evidence2, evidence3, evidence4, evidence5, evidence6, evidence7, evidence8, evidence9), provide the following:
1. 'RelevanceScore': score, justification
Each evidence should include these details, specified as 'evidenceN' where N is the evidence number."
}}
"""



        complete_json_evidence_answer = {}
        expected_evidences = {f"evidence{i}" for i in range(10)}


        logging.info(f"################## Process RelevanceScore Input (Attempt {attempt}) ##################")
        logging.info(prompt_for_evidence_scores)

        evidence_scores = gpt4o_mini_analysis(prompt_for_evidence_scores)

        logging.info(f"################## Process RelevanceScore Output (Attempt {attempt}) ##################")
        logging.info(evidence_scores)



        format_prompt = f"""
Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format.

The desired JSON structure:
"evidenceN": {{
  "RelevanceScore": "score",
  "Relevance Justification": "justification"
}}

Note: 
- "score" should be an integer between 0 and 10.
- "justification" should be a string.

The content to be converted:
{evidence_scores}
"""

        json_evidence_answer = gpt4o_mini_analysis(format_prompt)
        # logging.info("evidence_scores JSON ANSWER")
        # logging.info(json_evidence_answer)


        new_evidence = extract_complete_json(json_evidence_answer)

        complete_json_evidence_answer.update(new_evidence)
        
        if expected_evidences.issubset(complete_json_evidence_answer.keys()):
            break

    with open(updated_single_query_path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    for evidence_key, scores in complete_json_evidence_answer.items():
        for item in data['items']:
            if evidence_key in item:
                item[evidence_key]['Relevance'] = scores

    with open(updated_single_query_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    logging.info("success updated_new_evidence")







def select_useful_evidence(claim, Video_information, QA_CONTEXTS, question, output_file_path):



    logging.warning("--------------------------------------------")
    logging.warning("------------ Evidence Selection ------------")
    logging.warning("----- Evaluating Usefulness of Evidence -----")
    logging.warning("--------------------------------------------")

    # 读取输出文件
    with open(output_file_path, 'r', encoding='utf-8') as file:
        new_data = json.load(file)

    # 用于存储所有转换后的证据的字典
    all_transformed_evidence = {}

    # 用于存储所有证据及其得分的列表
    all_evidences_with_scores = []

    # 遍历数据中的每个查询
    for query_key in new_data:
        if query_key.startswith("Query"):  # 检查键是否以“Query”开头
            evidence_list = new_data[query_key]
            
            # 计算每个evidence的total_score
            for i, evidence_dict in enumerate(evidence_list):
                quality_score = evidence_dict.get('website_quality_evaluation', {}).get('website_qualityScore', 0)
                newness_score = evidence_dict.get('Newness', {}).get('NewnessScore', 0)
                relevance_score = evidence_dict.get('Relevance', {}).get('RelevanceScore', 0)
                total_score = quality_score + newness_score + relevance_score * 2
                
                evidence_dict['total_score'] = total_score
                
                # 将每个evidence及其得分添加到列表中
                all_evidences_with_scores.append((query_key, i, evidence_dict, total_score))

    # 根据total_score对所有evidences进行排序
    sorted_all_evidences = sorted(all_evidences_with_scores, key=lambda x: x[3], reverse=True)

    # 取出total_score最高的三个evidence
    top_three_evidences = sorted_all_evidences[:3]

    # 提取top三个evidence的信息
    for query_key, i, evidence_dict, total_score in top_three_evidences:
        # 构造新键
        new_key = f"{query_key}_evidence_{i + 1}"
        
        # 提取所需的字段
        extracted_info = {
            "title": evidence_dict.get("title", ""),
            "link": evidence_dict.get("link", ""),
            "snippet": evidence_dict.get("snippet", ""),
            "content": evidence_dict.get("content", {}).get("content", "")
        }
        
        # 将提取的信息添加到转换后的证据字典中
        all_transformed_evidence[new_key] = extracted_info

    

    # 将提取的证据添加到原始数据的 "RelevantEvidence" 键下
    new_data["RelevantEvidence"] = all_transformed_evidence


    # 验证json格式，并循环3次直到正确
    true_json_answer = None
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        attempt += 1


#         validation_evidence_prompt = f"""
# {{
# "Claim": "{claim}",
# "Video_information": {json.dumps(Video_information, indent=2)},
# "QA_CONTEXTS": {json.dumps(QA_CONTEXTS, indent=2)},
# "New_Question": {{
#     "Question": "{question}"
# }},
# "Evidences": {json.dumps(all_transformed_evidence, indent=2)},
# "Task": "Evaluate the provided evidence to determine if it is useful for answering the New_Question. The task is to assess whether the evidence contains relevant information that can help address the question. If the evidence can contribute to answering the question, output 'yes' or 'no'. Additionally, provide a reason explaining your assessment.",
# "EvidenceIsUseful": {{
#     "Useful": "yes / no",
#     "Reason": ""
# }}
# }}
# """

        validation_evidence_prompt = f"""
{{
"Claim": "{claim}",
"Video_information": {json.dumps(Video_information, indent=2)},
"QA_CONTEXTS": {json.dumps(QA_CONTEXTS, indent=2)},
"New_Question": {{
    "Question": "{question}"
}},
"Evidences": {json.dumps(all_transformed_evidence, indent=2)},
"Task": "Evaluate the provided evidence to determine its relevance and usefulness in addressing the New_Question and ultimately assessing the truthfulness of the Claim within the context of the Video_information. Consider the following:

1. Relevance: Does the evidence directly relate to the New_Question or the Claim?
2. Support or Refutation: Does the evidence support or refute the New_Question or Claim? Both supporting and refuting evidence can be useful.
3. Context: Does the evidence provide important context or background information?
4. Factual Content: Does the evidence contain factual information that can be used to evaluate the New_Question or Claim?
5. Source Credibility: If the source of the evidence is mentioned, is it from a reputable or relevant source?

Based on these criteria, determine if the evidence is useful. Even if the evidence contradicts the New_Question or Claim, it can still be considered useful if it's relevant to the overall assessment.

Output 'yes' if the evidence is useful (relevant and informative) or 'no' if it's not. Provide a detailed reason explaining your assessment, referencing specific aspects of the evidence that led to your conclusion.",
"EvidenceIsUseful": {{
    "Useful": "yes / no",
    "Reason": "Provide a detailed explanation here, referencing specific content from the evidence and how it relates to the New_Question and Claim."
}}
}}
"""



        logging.info(f"################## Validation Evidence Prompt (Attempt {attempt}) ##################")
        logging.info(validation_evidence_prompt)

        validation_evidence_answer = gpt4o_mini_analysis(validation_evidence_prompt)

        logging.info(f"################## Validation Evidence Answer (Attempt {attempt}) ##################")
        logging.info(validation_evidence_answer)

        prompt_for_format = f"""
Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format.

The desired JSON structure:
{{
    "EvidenceIsUseful": {{
        "Useful": "yes / no",
        "Reason": ""
    }}
}}

The content to be converted:
{validation_evidence_answer}
"""


        
        json_answer = gpt4o_mini_analysis(prompt_for_format)

        true_json_answer = extract_complete_json(json_answer)


        if true_json_answer and "EvidenceIsUseful" in true_json_answer and true_json_answer["EvidenceIsUseful"]["Useful"] in ["yes", "no"]:
            break
    

    if true_json_answer and true_json_answer.get("EvidenceIsUseful", {}).get("Useful") == "yes":
        # 将更新后的数据写回文件
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(new_data, file, indent=4, ensure_ascii=False)
        return True
    else:
        return False


    

















def process_claim_and_generate_answer(claim, Video_information, QA_CONTEXTS, question, output_file_path):

    
    logging.warning("----------------------------------------------------------")
    logging.warning("--------- Question Anser Model With GoogleSearch ---------")
    logging.warning("----------------------------------------------------------")



    # 加载 JSON 数据
    with open(output_file_path, 'r', encoding='utf-8') as file:
        new_data = json.load(file)


    # 提取 RelevantEvidence 并存储在 all_transformed_evidence
    all_transformed_evidence = new_data.get("RelevantEvidence", {})


    # 提取 Queries 内容
    queries_content = new_data.get("Queries", {})

    # 构建 prompt
    prompt_for_question_answer_based_on_evidence = f"""
    {{
      "Claim": "{claim}",
      "Video_information": {json.dumps(Video_information, ensure_ascii=False, indent=4)},
      "QA_CONTEXTS": {json.dumps(QA_CONTEXTS, ensure_ascii=False, indent=4)},
      "New_Question": {{
        "Question": "{question}"
      }},
      "Queries": {json.dumps(queries_content, ensure_ascii=False, indent=4)},
      "Good evidence information": {json.dumps(all_transformed_evidence, ensure_ascii=False, indent=4)},
      "Task": "Based on the evidence extracted, generate an explanatory answer to the question: '{question}' that references the evidence. Note to add the referenced evidence number after the argument for each reason, e.g., [Query 1_evidence1····]. And evaluate the confidence (XX%) of your answer based on the analysis of the above evaluation of the evidence and the logic of the reasoning process."
    }}
    """





    attempt = 0
    max_attempts = 5
    final_json_answer = None

    while attempt < max_attempts:
        attempt += 1
        logging.info(f"################## Question Answer Input (Attempt {attempt}) ##################")
        logging.info(prompt_for_question_answer_based_on_evidence)

        answer = gpt4o_mini_analysis(prompt_for_question_answer_based_on_evidence)

        

        logging.info(f"################## Question Answer Output (Attempt {attempt}) ##################")
        logging.info(answer)

        format_final_prompt = f"""
        Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format.

        Desired JSON structure:
        {{
          "QA": {{
            "Question": "{question}",
            "Answer": "",
            "Confidence": ""
          }}
        }}

        Please note: Only modify the structure of the given following content, keeping the content as intact as possible and preserving the original language and descriptions.

        Text content to be converted:
        "{answer}"
        The final output should be in JSON format, which includes the extracted content of the 'Answer' and the 'Confidence' of the non empty percentage.
        """

        # logging.info("format_final_prompt")
        # logging.info(format_final_prompt)

        final_answer = gpt4o_mini_analysis(format_final_prompt)

        final_json_answer = extract_complete_json(final_answer)


        # 检查 Answer 和 Confidence 字段是否为空
        if final_json_answer and final_json_answer.get("QA", {}).get("Answer") and final_json_answer.get("QA", {}).get("Confidence"):
            break  # 如果不为空，则跳出循环

    with open(output_file_path, 'r', encoding='utf-8') as file:
        full_data = json.load(file)
    full_data.update(final_json_answer)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)














def process_claim_and_generate_answer_without_gs(claim, Video_information, question, output_file_path):
    
    logging.warning("-------------------------------------------------------------")
    logging.warning("--------- Question Anser Model Without GoogleSearch ---------")
    logging.warning("-------------------------------------------------------------")



    # 构建 prompt
    prompt_for_question_answer = f"""
{{
    "Claim": "{claim}",
    "Video_information": {json.dumps(Video_information, ensure_ascii=False, indent=4)},
    "New_Question": {{
    "Question": "{question}"
    }},
    "Task": "Based on the Claim and the Video_information, generate an explanatory answer to the question: '{question}' that references the evidence.  And evaluate the confidence (XX%) of your answer based on the analysis of the logic of the reasoning process."
}}
"""


    # token_count = count_tokens(prompt_for_question_answer)
    # print(f"Token count: {token_count}")
    # logging.info(f"Token count: {token_count}")

    attempt = 0
    max_attempts = 5
    final_json_answer = None

    while attempt < max_attempts:
        attempt += 1
        
        logging.info("prompt_for_question_answer")
        logging.info(prompt_for_question_answer)

        answer = gpt4o_mini_analysis(prompt_for_question_answer)        

        logging.info("prompt_for_question_answer ANSWER")
        logging.info(answer)

        format_final_prompt = f"""
Please convert the following text content into the specified JSON structure. Ensure the output is in JSON format and maintain the original content as much as possible, changing only the structure to the specified JSON format.

Desired JSON structure:
{{
    "QA": {{
    "Question": "{question}",
    "Answer": "",
    "Confidence": ""
    }}
}}

Please note: Only modify the structure of the given following content, keeping the content as intact as possible and preserving the original language and descriptions.

Text content to be converted:
"{answer}"
The final output should be in JSON format, which includes the extracted content of the 'Answer' and the 'Confidence' of the non empty percentage.
"""

        # logging.info("format_final_prompt")
        # logging.info(format_final_prompt)

        final_answer = gpt4o_mini_analysis(format_final_prompt)

        final_json_answer = extract_complete_json(final_answer)

        logging.info("QA Model final_json_answer")
        logging.info(final_json_answer)

        # 检查 Answer 和 Confidence 字段是否为空
        if final_json_answer and final_json_answer.get("QA", {}).get("Answer") and final_json_answer.get("QA", {}).get("Confidence"):
            break  # 如果不为空，则跳出循环

    with open(output_file_path, 'r', encoding='utf-8') as file:
        full_data = json.load(file)
    full_data.update(final_json_answer)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)









































def process_evidence(file_path):


    logging.warning("\n" * 5)
    logging.warning("--------------------------------------")
    logging.warning("--------- Processing evidence ---------")
    logging.warning("--------- Extracting necessary content from Google search results ---------")
    logging.warning("--------------------------------------")



    # 加载 JSON 数据
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 提取 items
    items = data.get("items", [])

    # 选择前 10 项
    top_items = items[:10]

    # 从每个 top item 提取所需的字段，并重命名
    evidence_found_and_judgments = []
    for i, item_dict in enumerate(top_items):
        for key, item in item_dict.items():
            evidence = {
                "title": item.get("title"),
                "link": item.get("link"),
                "displayLink": item.get("displayLink"),
                "snippet": item.get("snippet"),
                "htmlSnippet": item.get("htmlSnippet"),
                "website_content": item.get("website_content", {}).get("content")
            }
            evidence_found_and_judgments.append({f'evidence{i}': evidence})

    # 以 JSON 格式输出结果
    output_json = json.dumps(evidence_found_and_judgments, indent=4, ensure_ascii=False)

    return output_json










import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import logging
import threading

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

def fetch_webpage_content_bs4(link, retries=1):
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1'
    }
    
    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(retries):
        try:
            response = session.get(link)
            response.raise_for_status()
            response.encoding = 'utf-8'  # 明确指定响应的编码
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            content = '\n'.join([para.get_text() for para in paragraphs])

            # 确保内容是UTF-8编码
            content = content.encode('utf-8', errors='replace').decode('utf-8')

            return {"success": True, "content": content}
        except requests.exceptions.RequestException as e:
            # logging.error(f"BS4 Error fetching {link}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(3)  # 等待3秒后重试
            else:
                return {"success": False, "error": f"Error fetching {link}: {str(e)}"}

def fetch_webpage_content_selenium(link):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')  # 无头模式，不打开浏览器窗口
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.set_preference("general.useragent.override", random.choice(user_agents))
    
    driver = None
    try:
        driver_path = '/usr/local/bin/geckodriver'  # GeckoDriver的路径
        service = FirefoxService(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=options)
        
        driver.get(link)
        
        # 模拟滚动页面以触发动态加载
        SCROLL_PAUSE_TIME = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # 使用WebDriverWait等待页面特定元素加载
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'p')))
        
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        content = '\n'.join([para.text for para in paragraphs])
        
        return {"success": True, "content": content}
    except Exception as e:
        # logging.error(f"Selenium Error fetching {link}: {str(e)}")
        return {"success": False, "error": f"Error fetching {link}: {str(e)}"}
    finally:
        if driver:
            driver.quit()






def readAPI_fetch_content(url):
    api_key = None

    def fetch(url, headers):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type'):
            return response.json()
        else:
            raise requests.exceptions.ContentTypeError(
                f"Unexpected content type: {response.headers.get('Content-Type')}"
            )

    def remove_unwanted_text(text):
        url_pattern = re.compile(r'\(https?://[^\)]+\)')
        mailto_pattern = re.compile(r'\(mailto:[^\)]+\)')
        brackets_pattern = re.compile(r'\[.*?\]')
        text = url_pattern.sub('', text)
        text = mailto_pattern.sub('', text)
        text = brackets_pattern.sub('', text)
        text = '\n'.join([line for line in text.split('\n') if line.strip()])
        return text

    headers_common = {
        "Accept": "application/json",
    }

    if api_key:
        headers_common["Authorization"] = f"Bearer {api_key}"

    url1 = f"https://r.jina.ai/{url}"
    retries = 3
    delay = 60  # seconds

    result = {
        'success': False,
        'error': f"Failed to fetch {url} after {retries} attempts"
    }

    for attempt in range(retries):
        logging.info(f"readerAPI Process {url}, attempt {attempt + 1}")
        try:
            response_default = fetch(url1, headers_common)
            default_content = response_default.get('data').get('content')
            clean_default_content = remove_unwanted_text(default_content)

            result = {
                'success': True,
                'content': clean_default_content,
            }
            break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logging.warning(f"429 Too Many Requests for url: {url}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                result = {
                    'success': False,
                    'error': f"Error fetching {url}: {str(e)}"
                }
                break
        except Exception as e:
            result = {
                'success': False,
                'error': f"Error fetching {url}: {str(e)}"
            }
            break

    return result



def fetch_webpage_content(link, retries=2):
    results = [None, None, None]

    def run_bs4():
        results[0] = fetch_webpage_content_bs4(link, retries)
        # logging.info(f"BS4 result: {results[0]}")
        # logging.info(f"BS4 result: {results[0].get('success')}")

    def run_selenium():
        results[1] = fetch_webpage_content_selenium(link)
        # logging.info(f"Selenium result: {results[1]}")
        # logging.info(f"Selenium result: {results[1].get('success')}")

    def run_readapi():
        results[2] = readAPI_fetch_content(link)
        # logging.info(f"ReadAPI result: {results[2]}")
        # logging.info(f"ReadAPI result: {results[2].get('success')}")

    threads = [
        threading.Thread(target=run_bs4),
        threading.Thread(target=run_selenium),
        threading.Thread(target=run_readapi),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


    # 返回内容最长的结果
    valid_results = [result for result in results if result and result.get("content")]
    if valid_results:
        valid_results.sort(key=lambda x: len(x.get("content", "")), reverse=True)
        return valid_results[0]

    # 如果都失败，返回最后一个结果
    return results[-1] if results[-1] else {"success": False, "content": ""}











import tiktoken

def count_tokens(text, model_name='gpt-3.5-turbo'):
    # 加载与模型对应的编码器
    encoding = tiktoken.encoding_for_model(model_name)
    
    # 将文本编码为tokens
    tokens = encoding.encode(text)
    
    # 返回token的数量
    return len(tokens)







def modified_final_evidence(evidence):
    # 解析JSON数据
    json_evidence = evidence

    # 处理每一个evidence
    for query_key, evidences in json_evidence.items():
        if query_key.startswith("Query") and isinstance(evidences, dict):  # 确保只处理以Query开头的键
            for evidence_key, value in evidences.items():
                # 去除evaluation
                if 'website_quality_evaluation' in value:
                    del value['website_quality_evaluation']

                # 获取网页内容并添加到JSON数据中
                link = value['link']
                content_result = fetch_webpage_content(link)
                if content_result["success"]:
                    content = content_result["content"]
                    if count_tokens(content) > 4000:
                        content = ' '.join(content.split()[:4000]) + " ... [Content truncated]"
                    value['complete_content'] = content
                else:
                    value['complete_content'] = content_result["error"]

    return json_evidence





def get_content_and_word_count(link, snippet):

    # 获取网页内容
    content_result = fetch_webpage_content(link)
    if content_result["success"]:
        content = content_result["content"]
        content_tokens = count_tokens(content)

        
        if content_tokens > 500:
            content = extract_surrounding_text(content, snippet)
            logging.info(f"Link: {link} \t Content tokens: {content_tokens}")
            content_tokens = 500
    else:
        content = content_result["error"]
        content_tokens = 0
    
    return content, content_tokens












import os
import spacy
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken
import time
import concurrent.futures

def extract_surrounding_text(content, snippet, num_tokens=250):
    start_time = time.time()

    # 定义函数来计算token数量
    def count_tokens(text, model_name='gpt-3.5-turbo'):
        # 加载与模型对应的编码器
        encoding = tiktoken.encoding_for_model(model_name)
        # 将文本编码为tokens
        tokens = encoding.encode(text)
        # 返回token的数量
        return len(tokens)

    # 定义函数来编码文本为tokens
    def encode_text(text, model_name='gpt-3.5-turbo'):
        # 加载与模型对应的编码器
        encoding = tiktoken.encoding_for_model(model_name)
        # 将文本编码为tokens
        tokens = encoding.encode(text)
        return tokens, encoding

    # 提取最佳句子的前后各num_tokens个tokens
    def get_surrounding_tokens(content, snippet, num_tokens=250):
        # 获取当前 Python 文件所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建模型路径
        en_core_web_sm_path = os.path.join(current_dir, 'model', 'en_core_web_sm-3.7.1')
        
        # 加载spaCy的英语模型
        nlp = spacy.load(en_core_web_sm_path)

        # 检查文本长度，如果超过限制，则截取前10万字符
        max_length = 10000
        if len(content) > max_length:
            content = content[:max_length]

        # 将content转换为spaCy Doc对象
        content_doc = nlp(content)

        # 将content转换为句子列表
        sentences = [sent.text for sent in content_doc.sents]

        # 将snippet转换为spacy Doc对象
        snippet_doc = nlp(snippet)

        # 定义一个函数来计算相似度
        def calculate_similarity(snippet_doc, sentences):
            vectorizer = CountVectorizer().fit_transform([snippet_doc.text] + sentences)
            vectors = vectorizer.toarray()
            cosine_matrix = cosine_similarity(vectors)
            similarities = cosine_matrix[0][1:]  # 跳过第一个，因为那是snippet和自己的相似度
            return similarities

        # 计算每个句子与snippet的相似度
        similarities = calculate_similarity(snippet_doc, sentences)

        # 找到相似度最高的句子索引
        best_sentence_index = np.argmax(similarities)

        # 找到相似度最高的句子
        best_sentence = sentences[best_sentence_index]

        # 找到目标句子的开始和结束索引
        target_start_index = content_doc.text.find(best_sentence)
        target_end_index = target_start_index + len(best_sentence)
        
        # 提取目标句子的Token索引
        target_start_token_index = None
        target_end_token_index = None
        
        for token in content_doc:
            if token.idx == target_start_index:
                target_start_token_index = token.i
            if token.idx + len(token.text) - 1 == target_end_index - 1:
                target_end_token_index = token.i

        if target_start_token_index is None or target_end_token_index is None:
            return ""
        
        # 将全文转为tokens
        all_tokens, encoding = encode_text(content_doc.text)

        # 计算前后num_tokens个Token的范围
        start_token_index = max(0, target_start_token_index - num_tokens)
        end_token_index = min(len(all_tokens), target_end_token_index + num_tokens + 1)

        # 检查是否到达文本的开头或结尾，并添加提示
        prefix = "" if start_token_index == 0 else "[Content truncated]..."
        suffix = "" if end_token_index == len(all_tokens) else "...[Content truncated]"

        # 提取前后num_tokens个Token并拼接成字符串
        surrounding_tokens = all_tokens[start_token_index:end_token_index]
        surrounding_text = prefix + encoding.decode(surrounding_tokens) + suffix
        return surrounding_text

    # 使用线程池执行get_surrounding_tokens函数
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_surrounding_tokens, content, snippet, num_tokens)
        try:
            surrounding_text = future.result(timeout=60)
        except concurrent.futures.TimeoutError:
            # 如果超时，则获取前500个tokens
            surrounding_text = encode_text(content[:500])[1].decode(encode_text(content[:500])[0])

    return surrounding_text




















def contains_fact_check(link):
    """
    检查链接中是否包含 'fact' 和 'check' 两个连续的单词。
    """
    pattern = re.compile(r'fact[\W_]*check', re.IGNORECASE)
    return bool(pattern.search(link))


def process_json_files(folder_path, output_file_path):
    logging.info(f"Processing JSON files in folder: {folder_path}")
    # 初始化一个字典来保存所有符合条件的证据
    output_data = {}

    # 遍历文件夹中的所有文件
    files = [f for f in os.listdir(folder_path) if f.startswith("Query") and f.endswith("_updated.json")]

    # 按照文件名中的数字排序
    files.sort(key=lambda f: int(re.search(r'Query(\d+)', f).group(1)))

    # 处理每个文件
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            evidences = []
            # 遍历文件中的所有证据
            for item in data.get("items", []):
                for key, evidence in item.items():
                    if evidence.get("website_content", {}).get("content_tokens", 0) != 0:
                        try:
                            quality_score = int(evidence["website_quality_evaluation"].get("website_qualityScore", 0))
                            newness_score = int(evidence["Newness"].get("NewnessScore", 0))
                            relevance_score = int(evidence["Relevance"].get("RelevanceScore", 0))
                            total_score = quality_score + newness_score + relevance_score*2

                            # 过滤掉包含 "fact" 和 "check" 单词的链接
                            if not contains_fact_check(evidence["link"]):
                                evidences.append({
                                    "title": evidence["title"],
                                    "link": evidence["link"],
                                    "snippet": evidence["snippet"],
                                    "content": evidence["website_content"],
                                    "website_quality_evaluation": evidence["website_quality_evaluation"],
                                    "Newness": evidence["Newness"],
                                    "Relevance": evidence["Relevance"],
                                    "total_score": total_score  # 临时存储用于排序
                                })
                        except KeyError as e:
                            logging.info(f"Error processing evidence: {evidence}")
                            logging.info(f"KeyError: {e}")

            # 根据总得分对证据进行排序，并选择得分最高的3个证据
            top_evidences = sorted(evidences, key=lambda x: x["total_score"], reverse=True)[:3]
            # 去除total_score字段
            for evidence in top_evidences:
                del evidence["total_score"]

            # 获取文件前缀作为key
            query_key = filename.replace('_updated.json', '')
            output_data[query_key] = top_evidences

    # 如果输出文件存在，读取其内容
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as output_file:
            existing_data = json.load(output_file)
    else:
        existing_data = {}

    # 将新的数据合并到现有数据中
    existing_data.update(output_data)

    # 将合并后的结果写入输出文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(existing_data, output_file, ensure_ascii=False, indent=4)

    print(f"结果已追加写入 {output_file_path}")

# 使用示例
# process_json_files('path/to/json/folder', 'path/to/output.json')
