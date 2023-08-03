import sys
import openai
from datetime import datetime
import json
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont

# Set your OpenAI API key here
openai.api_key = ''

class ChatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.create_widgets()
        self.conversation_list = []
        self.talk = Chat(conversation_list=self.conversation_list)

    def create_widgets(self):
        # Conversation Text Widget
        self.conversation_text = QTextEdit(self)
        self.conversation_text.setReadOnly(True)
        self.conversation_text.setFontFamily("SimSun")
        self.conversation_text.setFontPointSize(12)

        # Input Text Widget
        self.input_text = QTextEdit(self)
        self.input_text.setFontFamily("SimSun")
        self.input_text.setFontPointSize(12)

        # Submit Button
        self.submit_button = QPushButton("提交", self)
        font = QFont()
        font.setPointSize(12)
        self.submit_button.setFont(font)
        self.submit_button.clicked.connect(self.on_submit)

        # Clear Button
        self.clear_button = QPushButton("Clear", self)
        font = QFont()
        font.setPointSize(12)
        self.clear_button.setFont(font)
        self.clear_button.clicked.connect(self.clear_text)

        # Select All Button
        self.select_all_button = QPushButton("Select All", self)
        font = QFont()
        font.setPointSize(12)
        self.select_all_button.setFont(font)
        self.select_all_button.clicked.connect(self.select_all_text)

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.conversation_text)
        layout.addWidget(self.input_text)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.select_all_button)

    def on_submit(self):
        user_input = self.input_text.toPlainText().strip()
        self.input_text.clear()
        self.conversation_text.append(f"\nMe: {user_input}\n")

        # Call the ChatGPT API and get AI response
        ai_response = self.talk.ask(user_input)
        self.conversation_text.append(f"\nGPT3.5: {ai_response}\n")

        # Save conversation to JSON file
        current_datetime = datetime.now().strftime("%Y-%m-%d")
        file_name = f"conversation_log_{current_datetime}.json"
        self.talk.get_conversation_data()
        self.talk.save_conversation_to_json(file_name)

    def clear_text(self):
        self.conversation_text.clear()

    def select_all_text(self):
        self.conversation_text.selectAll()

class Chat:
    def __init__(self, conversation_list=[], conversation_data={}):
        self.conversation_list = conversation_list
        self.costs_list = []
        self.conversation_data = conversation_data

    def ask(self, prompt):
        self.conversation_list.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.conversation_list)
        answer = response.choices[0].message['content']
        self.conversation_list.append({"role": "assistant", "content": answer})
        a = self.total_counts(response)
        self.costs_list.append(a)
        return answer

    def total_counts(self, response):
        tokens_nums = int(response['usage']['total_tokens'])
        price = 0.002 / 1000
        us = '{:.5f}'.format(price * tokens_nums)
        return float(us)

    def save_conversation_to_json(self, file_name):
        save_path = "/ChatGPT_API/logs"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_data, f, ensure_ascii=False)

    def get_conversation_data(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if current_datetime not in self.conversation_data:
            self.conversation_data[current_datetime] = []
        self.conversation_data[current_datetime].append(self.conversation_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_gui = ChatGUI()
    chat_gui.show()
    sys.exit(app.exec_())
