# Import-LLM-to-apply-sentimental-analysis-for-prediction-on-stock-
This is a project learning about LLM's application in sentimental analysis and hence conduct prediction on stock market. All resources are strickly protected and all rights reserved.

1. Dataset: EquAnnoInfo (沪深股票公告基本信息）
Time：2018.12.1~2023.12.1
Market: China Market
Nature: Announcement or statement

2. Methodology:
In this project, we mainly uitilize Large Language Model(LLM) to conduct sentimental analysis on the concerned dataset of basic information on stock announcements for the Shanghai and Shenzhen stock markets(or China market). The objective is hence predict the stock market involving the sentimental analysis result. Firstly, we proceed the raw data by obtain them from the links in the .pkl files and do basic processing, like removal of illegel characters or problem of prolonged text(exceed maximum of tokens). Secondly, the processed announcement will be analysis by cetain LLM. Due to technical problems, we use Qwen-72B for the first 4 months'processing and Yi-34B-Chat for the left 21 months, and the whole period of dataset used is from 2018.12.1 to 2020.12.31, all 25 months. In the sentimental analysis, we use appropriate prompt to enable the Chinese-base LLM to classify whether the announment is positive or negetive, and to what extent. The neutral announment will be graded as 3, while the most postive is 5 and the most negative be grade as 1. Lastly, we store the statistic with regrad to its date, company name, URL link and sentimental text in the form as EXCEL. The results shows that most of the announcements are graded as 3(about an average of 60%). The relatively positive entries take more share compare to whose regarded as relatively negative.

3. Implementation Details:
The follows are feature of the program **import LLM to apply sentimental analysis on EquAnnofo dataset**:

(1). **Configuration and Library Imports**: The script starts by importing necessary libraries such as `openai`, `pandas`, `re` (for regular expressions), `requests` (for handling HTTP requests), `PyPDF2` (for PDF processing), among others. It also sets up the OpenAI API key and base URL for making requests to an AI model.

(2). **Function Definitions**:
   - `extract_score_from_text(text)`: Extracts the last number found in a string using regular expressions and ensures the number is within the range 1 to 5, defaulting to 3 if no number is found.
   - `download_and_convert_pdf_to_text(pdf_url, max_pages=2)`: Downloads a PDF from a given URL, extracts text from the first few pages (default is up to 2 pages), and returns the combined text.
   - `remove_illegal_chars(value)`: Cleans a string by removing characters that are not printable, which is useful for preparing text for Excel output.
   - `analyze_sentiment(text, company)`: Sends a request to the OpenAI API with a prompt asking to analyze the sentiment of a company announcement and return a sentiment score based on the text.
   - `get_next_file_to_process(output_folder, pkl_files)`: Determines which `.pkl` file should be processed next based on existing output files.

(3). **Main Process (`run` function)**:
   - The script reads a list of `.pkl` files from a specified folder. These files are expected to contain data frames with information about company announcements.
   - It determines the next `.pkl` file to process based on previously processed files.
   - For each `.pkl` file to be processed, it reads the data frame, extracts company names, publication times, and PDF URLs.
   - It then downloads and extracts text from each PDF URL for sentiment analysis.
   - The sentiment analysis is performed by sending the extracted text to the OpenAI API with a specific prompt designed to evaluate the sentiment towards the company based on the announcement.
   - The script extracts a sentiment score from the API's response and appends it to the data frame.
   - Finally, it cleans the data frame of any illegal characters and saves the results as an Excel file in a specified output folder.

(4). **Execution**: The script concludes by specifying the folder paths for the source `.pkl` files and the output directory. It then calls the `run` function to start processing the files.



