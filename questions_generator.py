"""
This module contains classes for generating questions for mock interview.

The QuestionsGenerator class uses Generative AI to generate questions for mock interview. It takes the student ID and search for the midterm performance json file and conversation with My-GPTs as an input and starts the process of generating questions and store it in new json file.


## Example:
    ```python
    >>> from questions_generator import QuestionsGenerator
    >>> generator = QuestionsGenerator('111403538')
    >>> generator.start_process(user_content)
    ```
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

class QuestionsGenerator:
    """
    Generates questions for mock interview using Generative AI.

    ## Attributes:
        student_id (str): The ID of the student.

    ## Methods:
        start_process: Starts the process of generating questions and create new json file.

    ## Example:
    ```python
    >>> generator = QuestionsGenerator('111403538')
    >>> generator.start_process(user_content)
    ```
    """

    def __init__(self, student_id: str) -> None:
        """
        Initializes the QuestionsGenerator object.
        """
        self.student_id = student_id
        self.user_prompt_template = self._initialize_user_prompt_template()
        self.system_prompt_template = self._initialize_system_prompt_template()
        self.conversation_history = ["# 使用者與AI的對話內容"]

        load_dotenv()

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def _initialize_system_prompt_template(self) -> str:
        """
        Initializes the system prompt template.

        Returns:
            SystemTemplate: The initialized system prompt template.
        """
        system_template = f"""
# 背景設定

1. 你是一位大學教師，為人客氣和善，不會使用命令語氣，進行口頭面試測驗，就像語音對話的習慣一樣，一次問一個問題。

2. 你講授「Python - 程式設計」課程，你會接收到學生詢問的很多問題，你要根據這些問題歷史去評估學生的知識遷移的程度。

3. 現在請與學生以對話方式進行口頭面試測驗，目標為評估學生「根據問題將Python或其他程式語言或其他知識技能，進行知識轉化的過程以及知識遷移之程度與能力」。整個口頭面試測驗過程將分為兩個階段，一次問一個問題。

    3.1. 第一階段：說明本問卷的目的，解釋「什麼是遷移學習」。接著一次問一個題目，分別詢問學生的資本資訊：姓名、學號、科系、年級等基本資料。
    
    3.2. 第二階段：一次問一個問題，問題具有接續性，請以大約10個開放式申論問答題，藉由學生的回答，評估學生的知識遷移程度與能力，你將發揮好奇心，透過學生的回答，進一步詢問更詳細的內容。
    
學生可以隨時停止口頭面試測驗，口頭面試測驗結束後，請明確告知口試結束，並根據之前學生回覆內容給予正面的講評與鼓勵，以鼓勵學生繼續追求知識。

4. 你會收到使用者與AI的對話內容，請根據對話內容，進行下一個問題的提問，一次問一個問題。

{self.user_prompt_template}
"""

        return system_template

    def _initialize_user_prompt_template(self) -> str:
        """
        Initializes the user prompt template.

        Returns:
            UserTemplate: The initialized user prompt template.
        """
        midterm = self._get_midterm()
        mygpt = self._get_mygpt()

        user_template = f"""
        # 期中考弱項
        {midterm}

        # 問題
        {mygpt}
        """

        return user_template

    def _add_conversation_history(self, content: str) -> str:
        """
        add the conversation history.
        """

        self.conversation_history.append(content)

    def _get_midterm(self) -> str:
        """
        Get the midterm performance of the student.

        Returns:
            str: The midterm performance of the student.
        """
        result = ""

        with open(f"midterm/{self.student_id}.json", "r", encoding='utf-8') as file:
            midterm = json.load(file)

            for key, value in midterm.items():
                result += f"{key}: {value}\n"

        return result

    def _get_mygpt(self) -> str:
        """
        Get the conversation with My-GPTs.

        Returns:
            str: The conversation with My-GPTs.
        """
        result = ""

        with open(f"mygpt/{self.student_id}.json", "r", encoding='utf-8') as file:
            mygpt = json.load(file)

            for key, value in mygpt.items():
                result += f"{key}:\n\n"

                for idx, question in enumerate(value, start=1):
                    result += f"{idx}. {question}\n"

                result += "\n"

        return result

    def _get_questions(self, model: str) -> str:
        """
        Get the questions generated by Generative AI.
        
        Args:
            model (str): The model to use for generating questions.

        Returns:
            str: The generated questions.
        """
        conversation_history = ("\n").join(self.conversation_history)

        messages = [
            {"role": "system", "content": self.system_prompt_template},
            {"role": "user", "content": conversation_history}
        ]

        chat_completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
        )
        self._add_conversation_history(chat_completion.choices[0].message.content)

        return chat_completion.choices[0].message.content

    def start_process(self, user_content: str) -> str:
        """
        Starts the process of generating questions and store it in new json file.

        Args:
            user_content (str): The user response with the question.

        Returns:
            str: The generated questions.
        """
        model = "gpt-4o"
        self._add_conversation_history(user_content)
        result = self._get_questions(model)

        return result
