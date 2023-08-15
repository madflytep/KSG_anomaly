import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from PIL import Image
import base64

from modules import upload_ksg_1 as original_upload_ksg_1
from modules import upload_ksg_2 as original_upload_ksg_2
from modules import upload_ksg_3 as original_upload_ksg_3
from modules import show_plot_1 as original_show_plot_1
from modules import target_file as original_target_file

@st.cache_data
def target_file(uploaded_file):
    return original_target_file(uploaded_file)

@st.cache_data
def upload_ksg_1(df):
    return original_upload_ksg_1(df)

@st.cache_data
def upload_ksg_2(df):
    return original_upload_ksg_2(df)

@st.cache_data
def upload_ksg_3(df):
    return original_upload_ksg_3(df)

@st.cache_data
def show_plot_1(df):
    return original_show_plot_1(df)

@st.cache_data
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


# Код для стилизации кнопки
button_style = '''
    display: inline-block;
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    border-radius: 4px;
    cursor: pointer;
'''

#переопределим функции, чтобы хрантиь все в кеше и страница не перезагружалась


# заголовки и подзаголовки
image = Image.open('logo.png')
st.image(image)
st.title("Сервис по поиску аномалий данных в КСГ")
st.header("Пожалуйста, загрузите текущий файл КСГ")

#загрузка списка объектов и получение объектов, по которым не ведется работа
directory = pd.read_excel('directory/directory.xlsx', sheet_name='objects_spr')
status_list = ['Приостановлен', 'Проектирование приостановлено', 'Строительство приостановлено']
black_objects = directory[directory['status'].isin(status_list)]['obj_key']

#загрузка файла
uploaded_file = st.file_uploader("Загрузите файл с КСГ")


# tab1, tab2, tab3 = st.tabs(['Аномалии 1-й группы', 'Аномалии 2-й группы', 'Аномалии 3-й группы'])

if uploaded_file is not None:
    with st.spinner("Идет загрузка КСГ..."):
        df = target_file(uploaded_file)
        df_1 = upload_ksg_1(df)
        df_2 = upload_ksg_2(df)
        df_3 = upload_ksg_3(df) 
    st.success('КСГ загрузилось успешно')

    filter = list((df['obj_key'] + ' ' + df['obj_shortName']).unique())


    # отображение фильтра по объектам
    
    selected = st.multiselect('Выберите нужный объект',
                            options=filter,
                            default=None,
                            label_visibility='hidden'
                            )
    tab1, tab2, tab3 = st.tabs(['Аномалии 1-й группы', 'Аномалии 2-й группы', 'Аномалии 3-й группы'])

    with tab1:  
        if not selected:
            st.metric("Кол-во аномалий, когда срок задачи прошел, а процент завершения 0%", value = f'{df_1.shape[0]}')
            st.write(show_plot_1(df_1))
            st.dataframe(df_1.astype(str), width=1200)
            
            df_xlsx_1 = download_excel(df_1)
            # Код для ссылки на скачивание с применением стилей кнопки
            download_link = f'''
                <a href="data:application/octet-stream;base64,{base64.b64encode(df_xlsx_1).decode()}"
                download="Аномалии_1-й_группы.xlsx" style="{button_style}">
                Скачать данные в Excel
                </a>
            '''

            st.markdown(download_link, unsafe_allow_html=True)
        else:
            filtered_df_1 = df_1[df_1['фильтр'].isin(selected)]
            if filtered_df_1.shape[0] == 0:
                st.success('Аномалий не обнаружено')

            else:
                st.metric("Кол-во аномалий, когда срок задачи прошел, а процент завершения 0%", value = f'{filtered_df_1.shape[0]}')
                st.write(show_plot_1(filtered_df_1))
                st.dataframe(filtered_df_1.astype(str), width=1200)
                df_xlsx_1 = download_excel(filtered_df_1)
                # Код для ссылки на скачивание с применением стилей кнопки
                download_link = f'''
                    <a href="data:application/octet-stream;base64,{base64.b64encode(df_xlsx_1).decode()}"
                    download="Аномалии_1-й_группы.xlsx" style="{button_style}">
                    Скачать данные в Excel
                    </a>
                '''
                st.markdown(download_link, unsafe_allow_html=True)

        

    with tab2:
        if not selected:
            st.metric("Кол-во аномалий, когда срок задачи прошел, а процент завершения не 100%", value = f'{df_2.shape[0]}')
            df_delay_2 = df_2.groupby('фильтр', as_index=False)['obj_key'].count().sort_values('obj_key',ascending=False)
            df_delay_2.columns = ['Объект', 'Кол-во аномалий']
            df_delay_2 = df_delay_2.astype(str)
            st.data_editor(
                df_delay_2,
                column_config={
                    "Кол-во аномалий":st.column_config.ProgressColumn(
                        "Кол-во аномалий",
                        format="%u",
                        min_value=df_delay_2['Кол-во аномалий'].min(),
                        max_value=df_delay_2['Кол-во аномалий'].max()
                    ),
                },
                hide_index=False
            )
            st.dataframe(df_2.astype(str), height=600, width=1200)
            df_xlsx_2 = download_excel(df_2)
            # Код для ссылки на скачивание с применением стилей кнопки
            download_link = f'''
                <a href="data:application/octet-stream;base64,{base64.b64encode(df_xlsx_2).decode()}"
                download="Аномалии_2-й_группы.xlsx" style="{button_style}">
                Скачать данные в Excel
                </a>
            '''
            st.markdown(download_link, unsafe_allow_html=True)
        else:
            filtered_df_2 = df_2[df_2['фильтр'].isin(selected)]
            if filtered_df_2.shape[0] == 0:
                st.success('аномалий не обнаружено')
            else:
                df_delay_2 = filtered_df_2.groupby('фильтр', as_index=False)['obj_key'].count().sort_values('obj_key',ascending=False)
                df_delay_2.columns = ['Объект', 'Кол-во аномалий']
                df_delay_2 = df_delay_2.astype(str)
                st.metric("Кол-во аномалий, когда срок задачи прошел, а процент завершения 0%", value = f'{filtered_df_2.shape[0]}')
                st.data_editor(
                    df_delay_2,
                    column_config={
                        "Кол-во аномалий":st.column_config.ProgressColumn(
                            "Кол-во аномалий",
                            format="%f",
                            min_value=df_delay_2['Кол-во аномалий'].min(),
                            max_value=df_delay_2['Кол-во аномалий'].max()
                        ),
                    },
                    hide_index=False
                )
                st.dataframe(filtered_df_2.reset_index().astype(str), height=600, width=1200)

                df_xlsx_2 = download_excel(filtered_df_2)
                # Код для ссылки на скачивание с применением стилей кнопки
                download_link = f'''
                    <a href="data:application/octet-stream;base64,{base64.b64encode(df_xlsx_2).decode()}"
                    download="Аномалии_2-й_группы.xlsx" style="{button_style}">
                    Скачать данные в Excel
                    </a>
                '''
                st.markdown(download_link, unsafe_allow_html=True)


    with tab3:
        if not selected:
            st.metric("Кол-во аномалий, когда срок близок к завершению, а процент вполнения сильно отстает", value = f'{df_3.shape[0]}')
            df_delay_3 = df_3.groupby('фильтр', as_index=False)['obj_key'].count().sort_values('obj_key',ascending=False)
            df_delay_3.columns = ['Объект', 'Кол-во аномалий']
            df_delay_3 = df_delay_3.astype(str)
            st.data_editor(
                df_delay_3,
                column_config={
                    "Кол-во аномалий":st.column_config.ProgressColumn(
                        "Кол-во аномалий",
                        format="%u",
                        min_value=df_delay_3['Кол-во аномалий'].min(),
                        max_value=df_delay_3['Кол-во аномалий'].max()
                    ),
                },
                hide_index=False
            )
            st.dataframe(df_3.astype(str), height=600, width=1200)
            df_xlsx_3 = download_excel(df_3)
            # Код для ссылки на скачивание с применением стилей кнопки
            download_link = f'''
                <a href="data:application/octet-stream;base64,{base64.b64encode(df_xlsx_2).decode()}"
                download="Аномалии_3-й_группы.xlsx" style="{button_style}">
                Скачать данные в Excel
                </a>
            '''
            st.markdown(download_link, unsafe_allow_html=True)
        else:
            filtered_df_3 = df_3[df_3['фильтр'].isin(selected)]

            if filtered_df_3.shape[0] == 0:
                st.success('Аномалий не обнаружено')
                
            else:
                df_delay_3 = filtered_df_3.groupby('фильтр', as_index=False)['obj_key'].count().sort_values('obj_key',ascending=False)
                df_delay_3.columns = ['Объект', 'Кол-во аномалий']
                df_delay_3 = df_delay_3.astype(str)
                st.metric("Кол-во аномалий, когда срок близок к завершению, а процент вполнения сильно отстает", value = f'{filtered_df_3.shape[0]}')
                st.data_editor(
                    df_delay_3,
                    column_config={
                        "Кол-во аномалий":st.column_config.ProgressColumn(
                            "Кол-во аномалий",
                            format="   %u",
                            min_value=df_delay_3['Кол-во аномалий'].min(),
                            max_value=df_delay_3['Кол-во аномалий'].max()
                        ),
                    },
                    hide_index=False
                )
                st.dataframe(filtered_df_3.reset_index().astype(str), width=1200)

                df_xlsx_3 = download_excel(filtered_df_3)
                # Код для ссылки на скачивание с применением стилей кнопки
                download_link = f'''
                    <a href="data:application/octet-stream;base64,{base64.b64encode(df_xlsx_3).decode()}"
                    download="Аномалии_2-й_группы.xlsx" style="{button_style}">
                    Скачать данные в Excel
                    </a>
                '''
                st.markdown(download_link, unsafe_allow_html=True)