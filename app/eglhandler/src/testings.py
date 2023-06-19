from datetime import datetime

today = datetime.today().strftime('%Y/%m/%d')

print(today > '2021/06/01')