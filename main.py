from openpyxl import load_workbook
import re

wb = load_workbook("./input_data/IR_Spring2021_ph12_7k.xlsx")
sheet = wb.active

content_list = []
url_list = []

for i in range(2, 7002):
    data_id = int(sheet.cell(i, 1).value)
    data_content = sheet.cell(i, 2).value
    data_url = sheet.cell(i, 3).value
    content_list.append(data_content)
    url_list.append(data_url)

a = content_list[2]
a = re.sub('\.', ' ', a)
a = re.sub('،', ' ', a)
a = re.sub('\n', ' ', a)
a = re.sub(':', ' ', a)
a = re.sub(';', ' ', a)
a = re.sub(r' +', ' ', a)

token_list = re.split(" ", a)
for token in token_list:
    print(token)
