from datetime import date

from openpyxl.workbook import Workbook

from const import Good


def save_to_excel(data: list[Good], scan_date: date):
    wb = Workbook()
    ws = wb.active
    ws.append(['Code', 'Name', 'Price', 'Status'])
    for good in data:
        ws.append([good.code, good.name, good.price, good.status])

    file_name = f'goods_{scan_date}.xlsx'
    wb.save(file_name)
