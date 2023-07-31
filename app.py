import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from xlsxwriter import Workbook
from modules import upload_ksg_1, show_plot_1

# st.text("This is data anomaly KSG service")

# st.write("**This is just**")

# df=pd.read_csv()

#отображение графиков

# fig, ax = plt.subplots()
# ax.scatter(np.arange(5), np.arange(5)**2)

# st.write(fig)

# заголовки и подзаголовки
st.title("Сервис по поиску аномалий данных в КСГ")
st.header("Пожалуйста, загрузите текущий файл КСГ")
# st.subheader("Subs")

#отображение метрик

# st.metric("NCS stock", value='1234', delta='2')


#загрузка списка объектов и получение объектов, по которым не ведется работа
directory = pd.read_excel('directory/directory.xlsx', sheet_name='objects_spr')
status_list = ['Приостановлен', 'Проектирование приостановлено', 'Строительство приостановлено']
black_objects = directory[directory['status'].isin(status_list)]['obj_key']

#загрузка файла


uploaded_file = st.file_uploader("Загрузите файл с КСГ")



if uploaded_file is not None:
    with st.spinner("Идет загрузка КСГ..."):
        df_1 = upload_ksg_1(uploaded_file)
        
    st.success('КСГ загрузилось успешно')

    st.metric("Кол-во аномалий, когда срок задачи прошел, а процент завершения 0%", value = f'{df_1.shape[0]}')

    st.write(show_plot_1(df_1))
    st.dataframe(df_1.astype(str), width=1200, height=400)

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

    
    df_xlsx = download_excel(df_1)
    # st.download_button(
    #     label="Скачать данные в Excel",
    #     data=df_xlsx,
    #     file_name="Аномалии_1-й_группы.xlsx",
    # )
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

    # Код для ссылки на скачивание с применением стилей кнопки
    download_link = f'''
        <a href="data:application/octet-stream;base64,{base64.b64encode(df_xlsx).decode()}"
        download="Аномалии_1-й_группы.xlsx" style="{button_style}">
        Скачать данные в Excel
        </a>
    '''

    st.markdown(download_link, unsafe_allow_html=True)