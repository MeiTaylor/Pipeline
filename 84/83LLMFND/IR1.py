# 定义输出为utf8
# -*- coding: utf-8 -*-

import json
import requests
import re
import regex
from IR1_relate_code import *

import logging
import os
from concurrent.futures import ThreadPoolExecutor
import threading


# logging.basicConfig(filename='test_IR1.log', level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')




def information_retriever_complete(claim, Video_information, QA_CONTEXTS, question, output_file_path):
    
    
    logging.warning("\n" * 5)
    logging.warning("-----------------------------------------")
    logging.warning("--------- Information Retriever ---------")
    logging.warning("-----------------------------------------")
    
    




    def process_query(query_key, query, searching_goal, claim, Video_information, QA_CONTEXTS, question, output_file_path):
        logging.info(f"Processing query key: {query_key}, query: {query}, searching_goal: {searching_goal}")

        # 获取输出文件路径的目录部分
        prefix = os.path.dirname(output_file_path)

        # 构建单个查询的文件路径
        single_query_path = os.path.join(prefix, f"{query_key}.json")

        # 处理查询并计算网站的质量得分，将结果保存到output_file_path
        process_query_and_quality_score_value(query, searching_goal, claim, Video_information, QA_CONTEXTS, question, single_query_path)
        
        # 更新后的查询文件路径
        updated_single_query_path = single_query_path.replace(".json", "_updated.json")

        process_evidence_and_Newness_Relevance(query_key, query, claim, Video_information, QA_CONTEXTS, question, updated_single_query_path)





    attempt_count = 0  # 初始化尝试计数器

    while attempt_count < 3:

        # 尝试读取 JSON 文件
        try:
            with open(output_file_path, 'r', encoding='utf-8') as file:
                try:
                    full_data = json.load(file)
                except json.JSONDecodeError:
                    full_data = {}  # 如果文件为空或无效，则初始化为空的 JSON 结构
        except FileNotFoundError:
            full_data = {}  # 如果文件不存在，则初始化为空的 JSON 结构

        # 更新数据
        full_data["Question"] = question

        # 写入更新后的数据到文件
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=4, ensure_ascii=False)


        attempt_count += 1
        search_and_queries = check_online_search_and_generate_queries(claim, Video_information, QA_CONTEXTS, question, output_file_path)

        # 检查是否需要在线搜索
        if search_and_queries['Prediction']['need_online_search'] == "No":
            logging.info("No online search needed.")
            process_claim_and_generate_answer_without_gs(claim, Video_information, question, output_file_path)

            return  # 直接跳出函数
        
        else:


            logging.info("Online search needed.")
            queries = search_and_queries['Prediction']['Queries']
            # 使用 ThreadPoolExecutor 并发处理查询
            with ThreadPoolExecutor(max_workers=1) as executor:
                futures = []
                for query_key, query_details in queries.items():
                    query = query_details['query']
                    searching_goal = query_details['searching_goal']
                    futures.append(executor.submit(
                        process_query, 
                        query_key, 
                        query, 
                        searching_goal, 
                        claim, 
                        Video_information, 
                        QA_CONTEXTS, 
                        question, 
                        output_file_path
                    ))
            
                # 等待所有线程完成
                for future in futures:
                    future.result()
            logging.info("两个查询处理均执行完毕")




            # 获取当前输出文件路径的目录部分
            now_folder_path = os.path.dirname(output_file_path)

            # 处理JSON文件，将结果合并并保存到输出文件路径
            process_json_files(now_folder_path, output_file_path)


            now_evidences_useful = select_useful_evidence(claim, Video_information, QA_CONTEXTS, question, output_file_path)

            if now_evidences_useful:
                break  # 如果所有查询都成功处理，则退出循环
            else:
                logging.info("Some queries failed, retrying...")

                # 删除指定文件
                for key in queries.keys():
                    prefix = os.path.dirname(output_file_path)
                    single_query_path = os.path.join(prefix, f"{key}.json")
                    updated_single_query_path = single_query_path.replace(".json", "_updated.json")

                    if os.path.exists(single_query_path):
                        os.remove(single_query_path)
                        logging.info(f"Deleted file: {single_query_path}")
                        
                    if os.path.exists(updated_single_query_path):
                        os.remove(updated_single_query_path)
                        logging.info(f"Deleted file: {updated_single_query_path}")

                # 清空 output_file_path 文件内容
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.truncate(0)
                logging.info(f"Cleared file contents: {output_file_path}")




    # Prompts for Question Answer based on the Evidence
    # 处理声明并生成回答，将结果保存到输出文件路径
    process_claim_and_generate_answer(claim, Video_information, QA_CONTEXTS, question, output_file_path)











# output_file_path = r"/workspaces/com_pipe/test/IR_result.json"








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

# Question = "Is there verifiable documentation or eyewitness testimony corroborating the presence of a shark on the flooded highway during Hurricane Ian in Florida?"



# Claim = "A video that went viral in August 2023 showed a beach party in Kyiv, proving that the war in Ukraine is a hoax."
# Video_information = {
#     "Video_description_from_descriptor": "The video captures scenes from a beach club setting, presumably in Kyiv during a time of war, juxtaposing the leisurely atmosphere of the pool party with the underlying tensions of the conflict. The video begins with a man walking on a serene beach, followed by a scene featuring a group of people relaxing on the beach in a beach club setting. The camera then focuses on a man preparing a drink before shifting to a couple enjoying the beach ambiance. Subsequently, the frame transitions to another man engaging in drink preparation. The key frame highlights consist of several snapshots showcasing a beach club in Kyiv during a war. These frames capture a bustling atmosphere with people sunbathing, lounging, and socializing amidst the backdrop of conflict. Scenes include individuals in swimwear, lounging by a pool and under white umbrellas, enjoying a leisurely time despite the mention of war in the captions."
# }
# QA_CONTEXTS = {}

# Question = "Does the video accurately represent the current situation in Kyiv or mislead about the war in Ukraine?"




# Claim = "Online video showed U.S. President Donald Trump visiting Maui in the aftermath of the August 2023 wildfires."
# Video_information = {
#     "Video_description_from_descriptor": "The video captures scenes of volunteers engaging in post-hurricane cleanup efforts, emphasizing community resilience and support. President Trump is featured delivering a speech, instilling a sense of unity and encouragement among the volunteers. Key frames display social media posts with messages like 'A Real President Truly cares' and '#TRUMP2024', as well as images of individuals surrounded by supportive crowds, reinforcing themes of care, patriotism, and collective action. The visuals highlight the spirit of volunteerism and public service, intertwining with political messaging promoting a specific candidacy for the presidency. The juxtaposition of disaster response, political discourse, and online engagement underscores a multifaceted narrative of civic duty, leadership, and social media advocacy within the context of post-disaster recovery efforts."
# }
# QA_CONTEXTS = {}
# Question = "Does the video accurately depict Trump visiting Maui after the August 2023 wildfires, or is it manipulated?"





# Claim = "A video shows North Korean leader Kim Jong Un and Russian President Vladimir Putin toasting each other then placing their drinks on the table without consuming them."
# Video_information = {
#     "Video_description_from_descriptor": "The video opens with a man in a black suit standing at a podium, holding a glass of wine, and appearing to deliver a speech or presentation in a formal setting with blue curtains in the background. The focus then shifts to another man in a suit standing at a table, also holding a glass of wine and giving a speech at the same event. Throughout the video, the man in the black suit with the wine glass remains the central figure, although both men are speaking. The scenes depict interactions between the individuals, highlighting moments of toasting and gestures with the glasses of wine. The setting suggests a formal event or ceremony, with microphone setups on the tables indicating a structured gathering. The key frames capture various interactions between the two men, showcasing subtle moments of trust issues or skepticism humorously referenced in the captions. These moments include both men holding glasses of what is presumed to be champagne, engaging in dialogue or gestures, and maintaining a serious demeanor. The occurrences culminate with the man in the black suit finishing his speech, implying a conclusion to the event or presentation. Overall, the video portrays a sequence of formal interactions and speeches at an organized function, emphasizing the dynamic between the two suited men through moments of raising glasses and engaging in speech delivery."
# }
# QA_CONTEXTS = {
#     "Question": "Is there verified evidence of Kim Jong Un and Vladimir Putin toasting together in this video?",
#     "Answer": "Yes, there is verified evidence that Kim Jong Un and Vladimir Putin did toast together, but the claims about them placing their drinks down without consuming them are misleading due to manipulated video footage. The original video clip that circulated implied an awkward moment in which both leaders toasted but then placed their full drinks on the table, suggesting a lack of trust. However, fact-checking indicates that this segment was altered to appear that way; the actual video was played in reverse. In reality, the complete footage shows both leaders toasting and then drinking from their glasses after the toast. Furthermore, their meeting was noted to be a full-scale diplomatic exchange, and there were numerous reports and videos from the event showcasing their interactions, including them toasting with champagne. Therefore, while there is evidence of a toast, the portrayal that they refrained from consuming their drinks is inaccurate.",
#     "Confidence": "85%"
# }
# Question = "What were the specific interactions and toasts between Kim Jong Un and Vladimir Putin reported in other footage from the event?"












# information_retriever_complete(Claim, Video_information, QA_CONTEXTS, Question, output_file_path)
