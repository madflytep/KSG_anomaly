import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import streamlit as st

def upload_ksg_1(uploaded_file):
    """Данная функция считвает загруженный файл и преобрабатывает данные для вявление аномалий 1-группы
    Когда срок задачи давно прошел, а процент выполнения задачи 0
    """
    
    df = pd.read_excel(uploaded_file)
    df['date_report'] = uploaded_file.name.replace('.xlsx', '')
    df['date_report'] = df['date_report'].apply(pd.to_datetime)
    df['date_diff'] = (df['ДатаОкончанияЗадачи'] -  df['date_report']).dt.days

    #загрузка списка объектов и получение объектов, по которым не ведется работа
    directory = pd.read_excel('directory/directory.xlsx', sheet_name='objects_spr')
    status_list = ['Приостановлен', 'Проектирование приостановлено', 'Строительство приостановлено']
    black_objects = directory[directory['status'].isin(status_list)]['obj_key']

    df = df[~df['obj_key'].isin(black_objects)]

    #убираем бинарные задачи
    code_task = list(df['Кодзадачи'].unique())

    # уберем бинарные задачи из анализа, то есть, где код задачи всегда 0 или 100

    binary_task = {}

    for task in code_task:
        
        values = df[df['Кодзадачи'] == task]['ПроцентЗавершенияЗадачи'].unique()
        
        binary_task[task] = values

    tasks_2 = []

    for task in code_task:
        if len(binary_task[task]) == 2:
            tasks_2.append(task)
    
    df = df[~df['Кодзадачи'].isin(tasks_2)]

    df_past = df[(df['ПроцентЗавершенияЗадачи'] == 0) & (df['date_diff'] < 0)]

    return df_past




def show_plot_1(df: pd.DataFrame):
    
    """Данная функция принимает датафрейм и отображает распределение задач на графике"""
    
    for_plot = df['date_diff'].value_counts()

    fig, ax = plt.subplots(figsize=(20, 15))

    # Plotting the bar chart with a different color and without edgecolor
    bars = ax.bar(for_plot.index, for_plot.values, color='lightsteelblue')

    # Customize plot appearance
    ax.set_xlabel('Отклонение от даты выгрузки до даты завершения задачи', fontsize=18)
    ax.set_ylabel('Количество записей в КСГ', fontsize=18)
    ax.set_title('Распределение количества задач по отклонениям от дней выгрузки, где процент завершения задачи 0', fontsize=16)

    # Set x-axis ticks and labels
    ticks = range(min(for_plot.index.astype(int)), max(for_plot.index.astype(int)), 50)
    ax.set_xticks(ticks)
    ax.set_xticklabels(ticks, rotation=45, ha='right')

    # Add grid lines
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return fig


def download_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data