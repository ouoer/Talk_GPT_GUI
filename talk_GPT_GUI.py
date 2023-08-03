import tkinter as tk
from tkinter.font import Font
import openai
from datetime import datetime
import json
import os
# -*- coding: utf-8 -*-

# Set your OpenAI API key here
openai.api_key = ''

class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT")
        self.create_widgets()
        self.conversation_list = []
        self.talk = Chat(conversation_list=self.conversation_list)

    def create_widgets(self):
        # Frame to hold conversation and input widgets
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        # Conversation Text Widget
        self.conversation_text = tk.Text(self.frame, wrap="word", font=Font(family="SimSun", size=12))
        self.conversation_text.pack(padx=10, pady=10)
        self.conversation_text.config(borderwidth=1, relief="solid")

        # Input Text Widget
        self.input_text = tk.Text(self.frame, wrap="word", font=Font(family="SimSun", size=12), height=3)
        self.input_text.pack(padx=10, pady=5, fill=tk.X)
        self.input_text.config(borderwidth=1, relief="solid")

        # Submit Button
        self.submit_button = tk.Button(self.frame, text="提交", font=Font(family="Arial", size=12),
                                       command=self.on_submit)
        self.submit_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Clear Button
        self.clear_button = tk.Button(self.frame, text="Clear", font=Font(family="Arial", size=12),
                                      command=self.clear_text)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Select All Button
        self.select_all_button = tk.Button(self.frame, text="Select All", font=Font(family="Arial", size=12),
                                           command=self.select_all_text)
        self.select_all_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Bind events to the conversation text widget
        self.conversation_text.bind("<FocusIn>", self.on_conversation_text_focus_in)
        self.conversation_text.bind("<FocusOut>", self.on_conversation_text_focus_out)
        # Bind events to the input text widget
        self.input_text.bind("<FocusIn>", self.on_input_text_focus_in)
        self.input_text.bind("<FocusOut>", self.on_input_text_focus_out)

    def on_submit(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        self.input_text.delete("1.0", tk.END)
        self.conversation_text.insert(tk.END, f"\nMe: {user_input}\n", 'user')

        # Call the ChatGPT API and get AI response
        ai_response = self.talk.ask(user_input)
        self.conversation_text.insert(tk.END, f"\nGPT3.5: {ai_response}\n", 'ai')

        # Save conversation to JSON file
        current_datetime = datetime.now().strftime("%Y-%m-%d")
        file_name = f"conversation_log_{current_datetime}.json"
        self.talk.get_conversation_data()
        self.talk.save_conversation_to_json(file_name)

    def clear_text(self):
        self.conversation_text.delete("1.0", tk.END)

    def select_all_text(self):
        self.conversation_text.tag_add(tk.SEL, "1.0", tk.END)
        self.conversation_text.mark_set(tk.INSERT, "1.0")
        self.conversation_text.see(tk.INSERT)

    def on_conversation_text_focus_in(self, event):
        self.conversation_text.configure(wrap="none", autoseparators=False)
        self.conversation_text.bind("<Control-a>", self.select_all_text)
        self.conversation_text.bind("<Control-A>", self.select_all_text)
        self.conversation_text.bind("<Control-x>", lambda event: self.conversation_text.event_generate("<<Cut>>"))
        self.conversation_text.bind("<Control-c>", lambda event: self.conversation_text.event_generate("<<Copy>>"))
        self.conversation_text.bind("<Control-v>", lambda event: self.conversation_text.event_generate("<<Paste>>"))

    def on_conversation_text_focus_out(self, event):
        self.conversation_text.configure(wrap="word", autoseparators=True)
        self.conversation_text.unbind("<Control-a>")
        self.conversation_text.unbind("<Control-A>")
        self.conversation_text.unbind("<Control-x>")
        self.conversation_text.unbind("<Control-c>")
        self.conversation_text.unbind("<Control-v>")

    def on_input_text_focus_in(self, event):
        self.input_text.configure(wrap="none", autoseparators=False)

    def on_input_text_focus_out(self, event):
        self.input_text.configure(wrap="word", autoseparators=True)

class Chat:
    def __init__(self, conversation_list=[], conversation_data={}) -> None:
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
    root = tk.Tk()
    root.tk.call('encoding', 'system', 'utf-8')
    chat_gui = ChatGUI(root)
    root.mainloop()
