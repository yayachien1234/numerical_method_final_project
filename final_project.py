#!/usr/bin/env python
# coding: utf-8

# In[5]:


import flet as ft
import openai
import pandas as pd

# ----------這邊要輸入API KEY----------#
openai.api_key=""

#----------初始化，並且指示接下來他要蒐集使用者什麼資訊----------#
messages = []
messages.append({"role":"system","content":"你現在是一個幫忙挑選筆電的助理，接下來請你依序詢問我的gender(boy/girl), character(student/engineer), game or not(yes/no) , need 3D ability or not(yes/no),不需要為我推薦筆電,最後問完時要告訴我已經問完了，請不要擅自修改我的問題也不要新增其他問題，並請你直接開始問問題"})



def main(page: ft.Page):
    chat = ft.Column()
    new_message = ft.TextField()
    
    def GPT(message):
        """
        將輸入的字句丟給ChatGPT去做回應
        """
        messages.append({"role":"user","content": new_message.value})
        response=openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages)
        reply = response["choices"][0]["message"]["content"]
        new_message.value = reply
        chat.controls.append(ft.Text(new_message.value))
        new_message.value = ""
        page.update()
    
    def organize(message):
        """
        1.將蒐集的資料依照指定格式輸出給變數gender, character, game, three_D
        2.讀取csv並且進行資料修整
        3.列出根據變數篩選的方法
        4.篩選出來後丟給ChatGPT叫他跟使用者介紹
        """
        messages.append({"role":"user","content": "請你幫我整理剛剛我提出的我的需求特徵，依照gender, character, game, 3D排序,並回傳陣列給我，範例為:[ boy, student, yes, yes ],並且請你回傳時只回傳矩陣的部分,不要有其他文字"})
        response=openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages)
        reply = response["choices"][0]["message"]["content"]
        
        #----------將reply整理成可以指定給變數的格式----------#
        
        s = reply
        s = s.replace("[", "").replace("]", "")  # 去除前後的中括號
        s_list = s.split(",")  # 根據逗號分割字符串
        s_list = [item.strip() for item in s_list]  # 去除前後的空格
        gender, character, game, three_D = s_list
        
        #----------输出结果為: ['boy', 'engineer', 'yes', 'yes']----------#


        #----------讀取有筆電各項資訊的csv + 進行資料修整----------#
        df = pd.read_csv('laptop_dataset.csv')
        df['Storage'] = df['Storage'].str.replace('SSD', '')
        df['Storage'] = df['Storage'].str.replace('1TB', '1000GB')
        df['Storage'] = df['Storage'].str.replace('GB', '')
        df['RAM'] = df['RAM'].str.replace('GB', '')
        df['Screen Size'] = df['Screen Size'].str.replace('inches', '')
        df['RAM'] = df['RAM'].astype(int)
        df['Storage'] = df['Storage'].astype(int)
        df['Screen Size'] = df['Screen Size'].astype(float)
        
        #----------針對變數的值(使用者的特徵)去對資料進行篩選----------#

        if game == "yes":
            filtered_data = df[(df['CPU Score'] >= 9) & (df['GPU Score'] >= 8.7)]
        if three_D == "yes":
            filtered_data = df[(df['GPU Score'] >= 8.0)]
        if character =="student":
            filtered_data = df[(df['CPU Score'] >= 7) &(df['GPU Score'] >= 6) & (df['GPU Score'] <= 8)& (df['RAM'] >= 8)& (df['Storage'] >= 256)& (df['Screen Size'] >= 13)]
        elif character =="engineer":
            filtered_data = df[(df['CPU Score'] >= 8.5) & (df['CPU Score'] <= 9.5) &(df['GPU Score'] >= 6.5) & (df['GPU Score'] <= 8)& (df['RAM'] >= 16)& (df['Storage'] >= 512)& (df['Screen Size'] >= 14)]
        
        #----------將篩選出來的資料manufacture、model_name指定給manu_list、model_name_list ,後面才能做使用----------#
        
        manu_list = filtered_data['Manufacturer'].values
        model_name_list = filtered_data['Model Name'].values
        
        new_message.value = f"總共會推薦給你{len(manu_list)}台筆電作參考"
        chat.controls.append(ft.Text(new_message.value))
        new_message.value = ""
        #----------將manu_list、model_name_list依序代入給ChatGPT,讓他介紹我們篩選出的筆電特點----------#
        for i in range(0, len(manu_list)):
            new_message.value = f"第{i+1}台電腦是{manu_list[i]}的{model_name_list[i]}"
            chat.controls.append(ft.Text(new_message.value))
            new_message.value = ""
            messages.append({"role":"user","content": f"請為我介紹{manu_list[i]}的{model_name_list[i]}這台電腦"})
            response=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages)
            reply = response["choices"][0]["message"]["content"]
            new_message.value = reply
            chat.controls.append(ft.Text(new_message.value))
            new_message.value = ""
            page.update()

        
    page.add(
        chat, ft.Row(controls=[new_message, ft.ElevatedButton("GPT", on_click=GPT), ft.ElevatedButton("整理需求", on_click=organize)])
    )

ft.app(target=main)


# In[ ]:




