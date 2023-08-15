import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import streamlit as st



def target_file(uploaded_file):
    """Функция принимает загруженный КСГ и делает с ним минимальную манипуляцию для того, чтобы потом передадть в работу по аномалиям"""
        
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

    df['фильтр'] = df['obj_key'] + ' ' + df['obj_shortName']

    return df


def upload_ksg_1(df: pd.DataFrame):
    """Данная функция считвает загруженный файл и преобрабатывает данные для вявление аномалий 1-группы
    Когда срок задачи давно прошел, а процент выполнения задачи 0
    """

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

    ticks = range(min(for_plot.index.astype(int)), max(for_plot.index.astype(int)), 10)
    ax.set_xticks(ticks)
    ax.set_xticklabels(ticks, rotation=45, ha='right')

    # Add grid lines
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return fig



def upload_ksg_2(df: pd.DataFrame):
    """Функция для подсчета аномалий 2-й группы, когда срок прошел > 2 недель, а задача не выполнена на 100%"""
    df_delay = df[(df['date_diff']<-14) & (df['ПроцентЗавершенияЗадачи'] != 0) & (df['ПроцентЗавершенияЗадачи'] != 100)]

    return df_delay

#функция для расчета планового значения выполнения работ
def plan(row):
    days_diff = (row['date_report'] - row['ДатаНачалаЗадачи']).days
    if days_diff < 0:
        return 0
    else:
        total_days = (row['ДатаОкончанияЗадачи'] - row['ДатаНачалаЗадачи']).days
        if total_days == 0:  # Проверяем деление на ноль
            return 0
        else:
            return round(days_diff * 100 / total_days,2)


def upload_ksg_3(df: pd.DataFrame):
    """
    Данная функция принимает уже загруженный до этого файл КСГ и считает данные для отображения 2-й группы аномалий
    """

    df_leak = df[df['date_diff'] >= 0]
    df_leak = df_leak[df_leak['ПроцентЗавершенияЗадачи'] != 100]
    df_leak['План'] = np.where((df_leak['date_report'] - df_leak['ДатаНачалаЗадачи']).dt.days < 0, 0, df_leak.apply(plan, axis=1))
    df_leak['Недельный темп %'] = 100 * 7  / (df_leak['ДатаОкончанияЗадачи'] - df_leak['ДатаНачалаЗадачи']).dt.days
    df_leak['Срок в днях'] = (df_leak['ДатаОкончанияЗадачи'] - df_leak['ДатаНачалаЗадачи']).dt.days
    df_temps = df_leak[~df_leak['Недельный темп %'].isna()]
    df_temps = df_temps[df_temps['Недельный темп %'] < 100]
    df_anomaly_3 = df_temps[(df_temps['План'] - df_temps['ПроцентЗавершенияЗадачи']) > 2 * df_temps['Недельный темп %']]

    return df_anomaly_3