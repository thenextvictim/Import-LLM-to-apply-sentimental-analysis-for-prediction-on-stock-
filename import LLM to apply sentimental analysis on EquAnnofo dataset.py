import openai
import pandas as pd
import re
import os
import requests
from PyPDF2 import PdfReader
from io import BytesIO
import time
import openpyxl


def extract_score_from_text(text):
    # 使用正则表达式匹配文本中的所有数字
    matches = re.findall(r'\b(\d+)\b', text)
    if matches:
        # 如果找到数字，将最后一个匹配项转换成整数
        score = int(matches[-1])
        # 如果数字在1到5之间，则返回该数字，否则返回3
        return min(max(score, 1), 5)
    else:
        # 如果没有找到数字，返回3作为默认值
        return 3

def download_and_convert_pdf_to_text(pdf_url, max_pages=2):
    try:
        # Set a timeout for the request to prevent it from hanging indefinitely
        response = requests.get(pdf_url, timeout=10)  # timeout value can be adjusted as needed
        with BytesIO(response.content) as open_pdf_file:
            pdf_reader = PdfReader(open_pdf_file)
            text = ""
            # You can adjust the number of pages to process
            for page_number in range(min(len(pdf_reader.pages), max_pages)):
                try:
                    # Attempt to extract text from a page
                    page_text = pdf_reader.pages[page_number].extract_text()
                    if page_text:
                        text += page_text
                except Exception as e:
                    # Handle issues with reading specific pages of the PDF
                    # You can decide whether to continue or to stop processing further pages
                    continue
        print(text)
        return text
    except Exception as e:
        # Handle other exceptions that may occur
            return "请评分3"

        
def remove_illegal_chars(value):
    # 移除 Excel 非法字符
    if value is not None and isinstance(value, str):
        return ''.join(c for c in value if c.isprintable())
    return value



# to get proper authentication, make sure to use a valid key that's listed in
# the --api-keys flag. if no flag value is provided, the `api_key` will be ignored.
openai.api_key = "EMPTY"
openai.api_base = "http://147.8.210.247:8510/v1"

# 指定模型名称
model = "Yi-34B-Chat"

def analyze_sentiment(text, company):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": f"请分析以下公告，并确定它对“{company}”公司未来的影响是积极的还是消极的。如果公告对该公司表现出明确的积极或消极情感，请在1到5之间打分，以表示积极性或消极性的程度，1代表最消极，5代表最积极。为了确定公告对公司未来的影响，请考虑以下标准：公告是否预示着公司的积极或消极结果？ 公告是否表示公司的绩效或声誉有积极或消极的变化？ 公告是否显示出公司所在行业或市场的积极或消极趋势？ 如果文章没有表现出对公司明确的积极或消极情感，或者描述处于中立态度，请返回3分。 无论如何都请只返回一个数字，不要解释任何其他推理或评价，也不要给出除了阿拉伯数字之外的任何符号。 公告是：“{text}”。"}]
        )
        # 获取LLM返回的文本响应
        sentiment_text = response.choices[0].message.content
        print(sentiment_text)
        # 使用额外的逻辑来提取评分
        sentiment_score = extract_score_from_text(sentiment_text)
        return sentiment_score
    except Exception as e:
        print(f"An error occurred: {e}")
        return 3
    
def get_next_file_to_process(output_folder, pkl_files):
    # 获取所有现有Excel文件
    existing_files = [f for f in os.listdir(output_folder) if f.endswith('_result.xlsx')]
    print(existing_files)
    # 如果没有现有文件，返回第一个pkl文件
    if not existing_files:
        return pkl_files[0] if pkl_files else None
    # 获取最新的Excel文件名（不包括后缀）
    latest_excel_file = max(existing_files).replace('_result.xlsx', '')
    print(latest_excel_file)
    # 找到对应的pkl文件，如果存在，则返回下一个pkl文件
    if latest_excel_file + '.pkl' in pkl_files:
        latest_index = pkl_files.index(latest_excel_file + '.pkl')
        return pkl_files[latest_index + 1] if latest_index + 1 < len(pkl_files) else None
    else:
        return pkl_files[0]
    

def run(folder_path, output_folder):

    # 获取pkl文件列表并按名称排序
    pkl_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.pkl')])
    # 确定下一个要处理的pkl文件
    next_pkl_file = get_next_file_to_process(output_folder, pkl_files)
    print(next_pkl_file)
    
    if not next_pkl_file:
        print("没有新的pkl文件需要处理。")
        return

    # 从下一个pkl文件开始处理
    start_processing_from = pkl_files.index(next_pkl_file)

    for pkl_file in pkl_files[start_processing_from:]:
        #time cost
        start_time = time.time()

        file_path = os.path.join(folder_path, pkl_file)
        # 使用read_pickle方法读取Pickle文件
        df = pd.read_pickle(file_path)
        print(df)
        # 创建一个新的DataFrame来存储结果
        result_df = pd.DataFrame()

        # 从原始DataFrame中提取所需的列
        result_df['Company Name'] = df['secShortName']
        result_df['Publication Time'] = df['publishDate']
        result_df['PDF URL'] = df['s3Address']

        # 进行文本预处理之后再情感分析
        result_df['Text for Sentiment Analysis'] = result_df['PDF URL'].apply(download_and_convert_pdf_to_text)
        result_df['Sentiment Score'] = result_df.apply(lambda x: analyze_sentiment(x['Text for Sentiment Analysis'], x['Company Name']) if x['Text for Sentiment Analysis'] else None, axis=1)

        # 输出结果
        output_file_path = os.path.join(output_folder, pkl_file.replace('.pkl', '_result.xlsx'))

        # 将结果输出为Excel文件
        # 然后在写入 Excel 之前对值进行清洗
        result_df = result_df.applymap(remove_illegal_chars)
        result_df.to_excel(output_file_path, index=False)
    

        # 记录结束时间
        end_time = time.time()
        # 计算时间消耗
        time_taken = end_time - start_time
        print("代码执行时间：", time_taken, "秒")

#done 1.prompt中文 2.本地预处理pdf 3.token 过长问题 4. 1-5分 5.弄成一个class
# 指定文件夹路径
folder_path = "/Users/邓梦毫/Desktop/LLM调用--Qwen72b/EquAnnoInfo/EquAnnoInfo/"

# 获取文件夹中所有文件的列表
file_list = os.listdir(folder_path)
output_folder = "C:/Users/邓梦毫/Desktop/LLM调用--Qwen72b/EquAnnoInfo/Results"

run(folder_path, output_folder)







#12.28 done 1.prompt中文 2.本地预处理pdf 3.token 过长问题 4. 1-5分 5.弄成一个class
#1.3 done 6.提速 7.空白问题 8.some statistics 9.改进 prompt，examples
#1.12 Qwen-72B-Chat模型无法调用，报错为An error occurred: Request timed out: HTTPConnectionPool(host='147.8.210.247', port=8510): Read timed out. (read timeout=600) 
# 原因：是因为另一个项目组占了一部分显卡，导致qwen经常内存不够爆掉
#1.17 更换Qwen-72B-Chat-int4后模型无法调用， 报错为An error occurred: Invalid response object from API: '{"object":"error","message":"Only  allowed now, your model Qwen-72B-Chat-Int4","code":40301}' (HTTP response code was 400)
#原因：现在模型启动不了 但是也没报错，试试看是否通过重启一下服务器可能清理下各种任务缓存什么的是最有效的办法了，其他的方面我都排查过了 解决不了这个问题
