import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QFont, QTextCursor  # Add the QTextCursor import
import openai
import html

# Set your OpenAI API key here
openai.api_key = ''

class ChatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT")
        self.setGeometry(100, 100, 1000, 800)  
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.create_widgets()
        self.conversation_list = []
        self.input_text.textChanged.connect(self.update_character_count)
        self.talk = Chat(conversation_list=self.conversation_list)
        # Initialize character count label
        self.update_character_count()

        # Initialize total cost
        self.total_cost = 0.0

    def update_character_count(self):
        text = self.input_text.toPlainText()
        character_count = len(text)
        self.character_count_label.setText(f"当前输入框中的字符数：{character_count}")

    def create_widgets(self):
        self.character_count_label = QLabel(self)
        self.character_count_label.setFont(QFont("Arial", 12))
        self.character_count_label.setText("当前输入框中的字符数：0")

        self.conversation_text = QTextEdit(self)
        self.conversation_text.setReadOnly(True)
        self.conversation_text.setFontFamily("Arial")  # Use Arial font family
        self.conversation_text.setFontPointSize(24)

        # Input Text Widget
        self.input_text = QTextEdit(self)
        self.input_text.setFontFamily("Arial")  # Use Arial font family
        self.input_text.setFontPointSize(18)

        # Submit Button
        self.submit_button = QPushButton("提交", self)
        self.submit_button.setFont(QFont("Arial", 12))
        self.submit_button.clicked.connect(self.on_submit)

        # Cost Label
        self.cost_label = QLabel(self)
        self.cost_label.setFont(QFont("Arial", 12))
        self.cost_label.setText("本次对话共消耗：")

        self.total_cost_label = QLabel(self)
        self.total_cost_label.setFont(QFont("Arial", 12))
        self.total_cost_label.setText("总共消费：0.00000美元")

        # Initialize character count label
        self.update_character_count()

        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.conversation_text)
        layout.addWidget(self.input_text)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.cost_label)
        layout.addWidget(self.total_cost_label)
        layout.addWidget(self.character_count_label)  # Add character count label to the layout

    def on_submit(self):
        user_input = self.input_text.toPlainText().strip()
        self.input_text.clear()

        # Append user input to the conversation with proper formatting
        self.append_to_conversation(f"{user_input}\n", role="Me")

        # Call the ChatGPT API and get AI response
        
        ai_response = self.talk.ask(user_input)
        role = "GPT3.5-16k"

        # Append AI's response to the conversation with proper formatting
        self.append_to_conversation(f"{ai_response}\n", role=role)

        # Save conversation to JSON file
        current_datetime = datetime.now().strftime("%Y-%m-%d")
        file_name = f"conversation_log_{current_datetime}.json"
        self.talk.get_conversation_data()
        self.talk.save_conversation_to_json(file_name)

        # Update cost label
        cost = self.talk.total_counts()
        self.cost_label.setText(f"本次对话共消耗：{cost:.5f}美元")

        # Update total cost label
        self.total_cost += cost
        self.total_cost_label.setText(f"总共消费：{self.total_cost:.5f}美元")

    def append_to_conversation(self, text, role):
        # Move cursor to the end
        self.conversation_text.moveCursor(QTextCursor.End)

        # Append text with proper formatting
        role_html = f"<font color='red'><b>{role}:</b></font>" if role == "Me" else f"<font color='green'><b>{role}:</b></font>"
        content_html = html.escape(text).replace("\n", "<br>")

        if "    " in text:  # Check if the text contains indentation (code block)
            code_html = f"<pre style='font-family: monospace; color: red;'>{content_html}</pre>"
            self.conversation_text.textCursor().insertHtml(f"{role_html}<br>{code_html}<br>")
        elif "Me" in role:
            self.conversation_text.textCursor().insertHtml(f"{role_html}<br><font color='red'>{content_html}</font><br>")
        elif "GPT3.5-16k" in role:  # GPT3.5-16k
            self.conversation_text.textCursor().insertHtml(f"{role_html}<br><font color='blue'>{content_html}</font><br>")

        # Move cursor to the new end
        self.conversation_text.moveCursor(QTextCursor.End)

class Chat:
    def __init__(self, conversation_list=[], conversation_data={}):
        self.conversation_list = conversation_list
        self.costs_list = []
        self.conversation_data = conversation_data

    def ask_large_model(self, prompt):
        self.conversation_list.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=self.conversation_list)
        answer = response.choices[0].message['content']
        self.conversation_list.append({"role": "assistant", "content": answer})
        a = self.total_counts(response)
        self.costs_list.append(a)
        return answer

    def total_counts(self, response=None):
        if response:
            tokens_nums = int(response['usage']['total_tokens'])
            price = 0.002 / 1000
            us = '{:.5f}'.format(price * tokens_nums)
            return float(us)
        else:
            return sum(self.costs_list)

    def save_conversation_to_json(self, file_name):
        save_path = "/ChatGPT_API/logs"  # Update the save path if necessary
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, file_name)
        with open(file_path, 'a', encoding='utf-8') as f:
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
