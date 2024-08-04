import json
import requests
import re

import logging
import os
import sys
import regex
import traceback

from CV_relate_code import *
# from InformationRetriever import information_retriever_complete
from IR1 import *

# from IR2 import *

import os
import json
import shutil
import logging
from datetime import datetime
import pytz
import os
import json
import shutil
import logging
import threading
import traceback
import time


# 定义一个自定义的北京时间格式化器
class BeijingFormatter(logging.Formatter):
    def converter(self, timestamp):
        # 将时间戳转换为UTC时间
        dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        # 将UTC时间转换为北京时间
        return dt.astimezone(pytz.timezone('Asia/Shanghai'))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        # 使用自定义的日期格式
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def format(self, record):
        record.asctime = self.formatTime(record)
        return super().format(record)

# 创建一个自定义的日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)













def update_cv_result_with_ir_data(key, cv_output_file_path, ir_output_file_path):
    # 从IR_output_file_path中提取内容
    with open(ir_output_file_path, 'r') as ir_file:
        ir_data = json.load(ir_file)

    qa_data = ir_data.get('QA', {})
    qa_question = qa_data.get('Question', '')
    qa_answer = qa_data.get('Answer', '')
    qa_confidence = qa_data.get('Confidence', '')

    # 更新CV_output_file_path中的json文件
    cv_json_file_path = os.path.join(cv_output_file_path)

    # 读取CV_result.json内容
    with open(cv_json_file_path, 'r') as cv_file:
        cv_data = json.load(cv_file)

    # 更新Initial_Question_Generation部分
    initial_question_generation = cv_data.get(key, {})
    initial_question_generation['Question'] = qa_question
    initial_question_generation['Answer'] = qa_answer
    initial_question_generation['Confidence'] = qa_confidence

    cv_data[key] = initial_question_generation

    # 将更新后的数据写回CV_result.json
    with open(cv_json_file_path, 'w') as cv_file:
        json.dump(cv_data, cv_file, indent=4)

    logging.info("Updated CV_result.json with QA data from IR_result.json")




def extract_qa_contexts(cv_output_file_path):
    # 检查文件是否存在，如果存在则读取现有内容
    if os.path.exists(cv_output_file_path):
        with open(cv_output_file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                logging.error("Error reading JSON file.")
                return {}
    else:
        logging.error(f"File {cv_output_file_path} does not exist.")
        return {}

    # 提取Initial_Question_Generation和Follow_Up_Question_{counter}的内容
    new_QA_CONTEXTS = {}
    for key, value in data.items():
        if key == "Initial_Question_Generation":
            initial_question_generation = {
                "Question": value.get("Question", ""),
                "Answer": value.get("Answer", ""),
                "Confidence": value.get("Confidence", "")
            }
            new_QA_CONTEXTS[key] = initial_question_generation
        elif key.startswith("Follow_Up_Question_"):
            new_QA_CONTEXTS[key] = value

    return new_QA_CONTEXTS





































# CV_output_file_path = "/workspaces/com_pipe/zero_shot_llmfnd_new/result/1915109/CV_result.json"


# # # # # # 46506212
# Claim = "A video that went viral in August 2023 showed a beach party in Kyiv, proving that the war in Ukraine is a hoax."
# Video_information = {
#     "Video_description_from_descriptor": "The video captures scenes from a beach club setting, presumably in Kyiv during a time of war, juxtaposing the leisurely atmosphere of the pool party with the underlying tensions of the conflict. The video begins with a man walking on a serene beach, followed by a scene featuring a group of people relaxing on the beach in a beach club setting. The camera then focuses on a man preparing a drink before shifting to a couple enjoying the beach ambiance. Subsequently, the frame transitions to another man engaging in drink preparation. The key frame highlights consist of several snapshots showcasing a beach club in Kyiv during a war. These frames capture a bustling atmosphere with people sunbathing, lounging, and socializing amidst the backdrop of conflict. Scenes include individuals in swimwear, lounging by a pool and under white umbrellas, enjoying a leisurely time despite the mention of war in the captions."
# }
# QA_CONTEXTS = {}



# # # # # # # 46591501
# Claim = "A video shows North Korean leader Kim Jong Un and Russian President Vladimir Putin toasting each other then placing their drinks on the table without consuming them."
# Video_information = {
#     "Video_description_from_descriptor": "The video opens with a man in a black suit standing at a podium, holding a glass of wine, and appearing to deliver a speech or presentation in a formal setting with blue curtains in the background. The focus then shifts to another man in a suit standing at a table, also holding a glass of wine and giving a speech at the same event. Throughout the video, the man in the black suit with the wine glass remains the central figure, although both men are speaking. The scenes depict interactions between the individuals, highlighting moments of toasting and gestures with the glasses of wine. The setting suggests a formal event or ceremony, with microphone setups on the tables indicating a structured gathering. The key frames capture various interactions between the two men, showcasing subtle moments of trust issues or skepticism humorously referenced in the captions. These moments include both men holding glasses of what is presumed to be champagne, engaging in dialogue or gestures, and maintaining a serious demeanor. The occurrences culminate with the man in the black suit finishing his speech, implying a conclusion to the event or presentation. Overall, the video portrays a sequence of formal interactions and speeches at an organized function, emphasizing the dynamic between the two suited men through moments of raising glasses and engaging in speech delivery."
# }
# QA_CONTEXTS = {}


# # # # # 46512203
# Claim = "Online video showed U.S. President Donald Trump visiting Maui in the aftermath of the August 2023 wildfires."
# Video_information = {
#     "Video_description_from_descriptor": "The video captures scenes of volunteers engaging in post-hurricane cleanup efforts, emphasizing community resilience and support. President Trump is featured delivering a speech, instilling a sense of unity and encouragement among the volunteers. Key frames display social media posts with messages like 'A Real President Truly cares' and '#TRUMP2024', as well as images of individuals surrounded by supportive crowds, reinforcing themes of care, patriotism, and collective action. The visuals highlight the spirit of volunteerism and public service, intertwining with political messaging promoting a specific candidacy for the presidency. The juxtaposition of disaster response, political discourse, and online engagement underscores a multifaceted narrative of civic duty, leadership, and social media advocacy within the context of post-disaster recovery efforts."
# }
# QA_CONTEXTS = {}



# # # # # 46592810
# Claim = "A viral video shared in January 2023 authentically shows young girls in a house on Jeffrey Epstein's island."
# Video_information = {
#     "Video_description_from_descriptor": "The video primarily centers around a little girl playing with a dog in a bathtub. The key frame highlights provide glimpses into various indoor settings, potentially a spa or bathhouse, featuring large pillars, checkered floors, and different individuals in the background. One key frame captures the young child interacting near a sink, another shows the girl in a bikini holding a teddy bear amidst other children and a unique circular platform, and yet another displays luxurious indoor surroundings with two women engaged in pouring liquid into a bowl. The images consistently depict intricate architectural details, including pillars and distinct floor patterns, hinting at a high-end or exotic location where the playful interactions unfold between the girl and her surroundings."
# }
# QA_CONTEXTS = {}


# Claim =  "Marine vet Christopher Marquez was assaulted at a Washington, D.C., McDonald's retaurant by Black Lives Matter activists."
# Video_information = {
#     "video_date": 20160217.0,
#     "platform": "foxnews",
#     "video_headline": "Decorated Marine vet attacked at a McDonald's",
#     "video_transcript": "A decorated marine bullied, attacked, and robbed at a Washington DC McDonald's. Christopher Marquez who won a bronze star for a service in Iraq, claims he was attacked by 5 people who harassed him about the Black Lives Matter movement. He says the gang approached him aggressively, asked him if he thought, quote, black lives mattered. Marquez was then knocked unconscious in his wallet, including 100 of dollars in cash stolen. Kinda brought back memories of the war and stuff. My head really hurts. I get to get this sharp pain just goes straight down my my face, and it I I haven't really slept too well at all since it happened. Authorities are still searching for the attackers. Marquez, seen on the left in this iconic photo from the battle in Fallujah, Iraq, which became the basis for 2 famous no man left behind statutes.",
#     "Video_descriptor": "The video opens with a news anchor, dressed in a yellow attire, reporting on a story with headlines indicating a veteran and decorated marine being attacked at a D.C. McDonald's. The subsequent scene shifts to a man in a yellow shirt speaking to the camera, potentially related to the reported incident. Soldiers in fatigues are then portrayed in a camaraderie-filled moment, engaged in activities such as eating together and playing rock-paper-scissors. One of the soldiers appears to be injured, receiving assistance from another soldier, while a large bronze statue depicting soldiers in action poses alludes to themes of support and unity. The narrative progresses with soldiers walking away from the camera, emphasizing a sense of departure or transition. Throughout the video, key frames depict various scenes relating to the reported incident, including images from a news broadcast showing the news anchor, a blurred night scene, and the interior of a McDonald's restaurant. The presence of logos such as 'FOX NEWS' and overlays of text underscore the news reporting context, as seen in the timestamps indicating different moments of reporting. The video encapsulates a blend of news reporting, personal narratives, military camaraderie, and symbolic representations, all revolving around the central event of the attack on a veteran and decorated marine at a D.C. McDonald's, ultimately culminating in a visual story of interconnected events and responses."
# }
# QA_CONTEXTS = {}














def process_claim_verification(CV_output_file_path, Claim, Video_information, QA_CONTEXTS):
    # 检查文件是否存在
    if not os.path.exists(CV_output_file_path):
        # 如果文件不存在，创建文件并写入一个空的JSON对象
        with open(CV_output_file_path, 'w') as file:
            json.dump({}, file)

    with open(CV_output_file_path, 'r+') as file:
        data = json.load(file)
        data["Claim"] = Claim
        data["Video_information"] = Video_information
        file.seek(0)
        json.dump(data, file, indent=4)

    try:
        # 调用 process_claim_verifier 函数
        judgment, confidence = process_claim_verifier(Claim, Video_information, QA_CONTEXTS, CV_output_file_path)
        logging.info("process_claim_verifier result - Judgment: %s, Confidence: %s", judgment, confidence)

        # 判断是否需要生成问题
        if_generate_question = not (judgment and confidence >= 0.9)

        logging.warning("\n" * 5)
        logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logging.info("!!!!!!!!!! Processing Initial Question !!!!!!!!!!")
        logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logging.warning("\n" * 5)

        if if_generate_question:
            max_attempts = 3
            attempts = 0
            is_now_QA_useful = False

            while not is_now_QA_useful and attempts < max_attempts:
                try:
                    # key, question = generate_initial_question(Claim, Video_information, CV_output_file_path)
                    key, primary_question_answer, secondary_questions = generate_initial_question(Claim, Video_information, CV_output_file_path)


                    logging.info("Generated Initial Question: %s", primary_question_answer)

                    key_folder_path = os.path.join(os.path.dirname(CV_output_file_path), key)
                    os.makedirs(key_folder_path, exist_ok=True)

                    IR_output_file_path = os.path.join(key_folder_path, "IR_result.json")

                    information_retriever_complete(Claim, Video_information, QA_CONTEXTS, primary_question_answer, IR_output_file_path)
                    logging.info("IR results saved to: %s", IR_output_file_path)


                    with open(IR_output_file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        newest_QA_Context = data['QA']
                    
                    is_now_QA_useful = get_validator_result(Claim, Video_information, newest_QA_Context)
                    
                    attempts += 1
                except Exception as e:
                    logging.error("Error in initial question generation attempt %d: %s", attempts, str(e))
                    logging.error(traceback.format_exc())

            if is_now_QA_useful:
                update_cv_result_with_ir_data(key, CV_output_file_path, IR_output_file_path)
            else:
                logging.warning("Max generate_initial_question attempts reached and QA context is still not useful.")

        new_question_count = 1
        while if_generate_question:
            new_QA_CONTEXTS = extract_qa_contexts(CV_output_file_path)

            new_judgment, new_confidence = process_claim_verifier(Claim, Video_information, new_QA_CONTEXTS, CV_output_file_path)
            logging.info("New process_claim_verifier result - Judgment: %s, Confidence: %s", new_judgment, new_confidence)

            if new_judgment and new_confidence >= 0.9:
                break

            if new_question_count >= 3:
                break

            logging.warning("\n" * 5)
            logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            logging.info("!!!!!!!!!! Processing question #%d !!!!!!!!!!", new_question_count)
            logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            logging.warning("\n" * 5)

            new_question_count += 1

            max_attempts = 3
            attempts = 0
            is_now_QA_useful = False

            while not is_now_QA_useful and attempts < max_attempts:
                try:
                    new_key, follow_up_question = generate_follow_up_question(Claim, Video_information, new_QA_CONTEXTS, secondary_questions, CV_output_file_path)
                    logging.info("%s Generated Question: %s", new_key, follow_up_question)

                    new_key_folder_path = os.path.join(os.path.dirname(CV_output_file_path), new_key)
                    os.makedirs(new_key_folder_path, exist_ok=True)

                    IR_output_file_path = os.path.join(new_key_folder_path, "IR_result.json")

                    information_retriever_complete(Claim, Video_information, new_QA_CONTEXTS, follow_up_question, IR_output_file_path)
                    logging.info("IR results saved to: %s", IR_output_file_path)

                    with open(IR_output_file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        newest_QA_Context = data['QA']
                    
                    is_now_QA_useful = get_validator_result(Claim, Video_information, newest_QA_Context)
                    
                    attempts += 1
                except Exception as e:
                    logging.error("Error in follow-up question generation attempt %d: %s", attempts, str(e))
                    logging.error(traceback.format_exc())

            if is_now_QA_useful:
                update_cv_result_with_ir_data(new_key, CV_output_file_path, IR_output_file_path)
            else:
                logging.warning("Max generate_follow_up_question attempts reached and QA context is still not useful.")

        new_QA_CONTEXTS = extract_qa_contexts(CV_output_file_path)
        final_json_answer = process_claim_final(Claim, Video_information, new_QA_CONTEXTS, CV_output_file_path)
        logging.info("final_json_answer \n%s", final_json_answer)

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        logging.error(traceback.format_exc())






# process_claim_verification(CV_output_file_path, Claim, Video_information, QA_CONTEXTS)







# 定义一个包装函数来处理超时
def process_with_timeout(CV_output_file_path, Claim, Video_information, QA_CONTEXTS, timeout, event):
    thread = threading.Thread(target=process_claim_verification, args=(CV_output_file_path, Claim, Video_information, QA_CONTEXTS))
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        logging.error("Timeout reached for %s", CV_output_file_path)
        event.set()  # 设置事件，通知超时










def main():
    target_folder = r"E:\aim\LLM_FND\pipeline\84\83_new_examples"
    json_files = sorted([f for f in os.listdir(target_folder) if f.endswith('.json')])

    for file_name in json_files:
        try:
            print(f"---------- Processing {file_name}... ----------")
            json_file_path = os.path.join(target_folder, file_name)
            file_base_name = os.path.splitext(file_name)[0]
            output_folder = os.path.join(target_folder, file_base_name)
            CV_output_file_path = os.path.join(output_folder, f"{file_base_name}_CV_result.json")

            if os.path.exists(CV_output_file_path):
                with open(CV_output_file_path, 'r', encoding='utf-8') as f:
                    cv_data = json.load(f)
                    if "Final_Judgement" in cv_data:
                        print(f"Skipping {file_name} as it has already been processed.")
                        continue

            if os.path.exists(output_folder):
                shutil.rmtree(output_folder)
            os.makedirs(output_folder, exist_ok=True)

            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            Claim = data["claim"]
            Video_information = data["Video_information"]

            log_file_name = f'{file_base_name}_claim_verifer.log'
            log_file_path = os.path.join(output_folder, log_file_name)

            if os.path.exists(log_file_path):
                os.remove(log_file_path)

            file_handler = logging.FileHandler(log_file_path)
            formatter = BeijingFormatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            timeout_event = threading.Event()
            timeout_minutes = 20

            process_with_timeout(CV_output_file_path, Claim, Video_information, {}, timeout_minutes * 60, timeout_event)

            if timeout_event.is_set():
                print(f"Timeout reached for {file_name}. Skipping to the next file.")
                logger.removeHandler(file_handler)
                continue

            shutil.move(log_file_path, os.path.join(output_folder, log_file_name))
            logger.removeHandler(file_handler)
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            logging.error(f"Error processing file {file_name}: {e}")
            logging.error(traceback.format_exc())
        finally:
            if 'file_handler' in locals():
                logger.removeHandler(file_handler)

if __name__ == "__main__":
    for attempt in range(3):
        try:
            main()
            break
        except Exception as e:
            print("Terminated")
            logging.error("Terminated")
            logging.error(traceback.format_exc())
            print("Error occurred during execution. Pausing for 10 seconds...")
            time.sleep(10)
        else:
            print("Processed successfully.")