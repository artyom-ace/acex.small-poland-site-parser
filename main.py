import sys
import time
from datetime import datetime
from tkinter import filedialog
from tkinter.messagebox import showinfo
from tkinter.ttk import Progressbar

import settings

from httpx_html import HTMLSession
from db import cookies_load, cookies_save, goods_save, goods_load
from excel import save_to_excel
from parser import goods_on_page_get, make_headers

from tkinter import *


def main_httpx():
    print(f'access to main page {settings.shop_main_url} ...')

    session = HTMLSession()
    cookies_load(session.cookies)

    response = session.get(settings.shop_main_url)

    if response.status_code != 200:
        print(f'unexpected status code after: {response.status_code}')
        exit()

    if response.url == settings.shop_login_url:
        session.cookies.clear()
        response = session.get(settings.shop_login_url)

        print(f'login page {response.url} read successfully')

        # find element 'input[name=_token]', '.form-horizontal'
        token = response.html.find('input[name=_token]', first=True).attrs['value']
        if not token:
            print('error pasring login page ("form" with "_token" not fould)!')
            exit()

        credentials = {'_token': token, **settings.shop_credentials}

        print(f'login with credentials {credentials} ...')

        response = session.post(settings.shop_login_url, data=credentials, headers=make_headers(response.cookies), follow_redirects=True)

        # when follow_redirects=False
        # if response.status_code != 302:
        #     print(f'unexpected status code after: {response.status_code}')
        #     exit()
        # if response.headers['Location'] != 'https://b2b.cedrus.com.pl/produkty':
        #     print(f'unexpected location after: {response.headers["Location"]}')
        #     exit()
        # # follow to redirects
        # response = session.get(response.headers['Location'], headers=headers)  # https://b2b.cedrus.com.pl/produkty

        if response.status_code != 200:
            print(f'unexpected status code after: {response.status_code}')
            exit()

        if response.url != settings.shop_main_url:
            print(f'unexpected location after login: {response.url}')
            exit()

    cookies_save(response.cookies)

    print('start parsing...')

    data = goods_on_page_get(response.html)

    # find element 'div.col-sm-6:nth-child(2) > ul.pagination'
    # if element found:
    #   find element 'li > a[rel="prev"]' named prev
    #   find element 'li:nth-last-child(2) > a' named last
    #   if prev not found:
    #     if last found:
    #       find attr 'href' in last element named lastPage
    #       copy page number from href
    #       for i in range(2, lastPage):
    #         do request with hrefTempl + i

    pagination = response.html.find('div.col-sm-6:nth-child(2) > ul.pagination', first=True)
    if pagination:
        prev = pagination.find('li > a[rel="prev"]', first=True)
        last = pagination.find('li:nth-last-child(2) > a', first=True)
        if not prev:
            if last:
                last_page = int(last.text)
                print(f'last page: {last_page}')
                href = last.attrs['href']
                href_templ = href[:href.rfind('page=') + len('page=')]
                for i in range(2, last_page):
                    time.sleep(1)
                    response = session.get(href_templ + str(i), headers=make_headers(response.cookies), follow_redirects=False)
                    if response.status_code != 200:
                        print(f'unexpected status code after: {response.status_code}')
                        exit()
                    page_data = goods_on_page_get(response.html)
                    data.extend(page_data)

    goods_save(data, datetime.now().date())
    # data = goods_load(datetime.now().date())
    save_to_excel(data, datetime.now().date())

    print(f'parsing finished, {len(data)} goods found')

    print('end')


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Python Tkinter Button")
        self.minsize(640, 400)
        # self.iconbitmap('jar_bean.ico')
        # self.wm_iconbitmap(settings.prog_dir + '/jar_bean.ico')
        self.labelFrame = LabelFrame(self, text="Open File")
        self.labelFrame.grid(column=1, row=2, padx=20, pady=20)

        self.button = Button(self.labelFrame, text="Browse A File", command=self.file_dialog)
        self.button.grid(column=1, row=1)

        self.button2 = Button(self.labelFrame, text="Remove Button", command=self.action_remove_button1)
        self.button2.grid(column=2, row=2)

        self.pb = Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=280
        )
        # place the progressbar
        self.pb.place(x=40, y=20)
        # self.pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

    def file_dialog(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("jpeg files","*.jpg"),("all files","*.*")))
        self.label = Label(self.labelFrame, text = "")
        self.label.grid(column = 1, row = 2)
        self.label.configure(text = self.filename)

    def action_remove_button1(self):
        # self.button.grid_remove()
        # self.pb.start()
        self.pb_progress()

    def pb_progress(self):
        self.pb['maximum'] = 1000
        if self.pb['value'] < self.pb['maximum']:
            self.pb['value'] += 20
            # self.value_label['text'] = update_progress_label()
        else:
            showinfo(message='The progress completed!')


if __name__ == '__main__':
    root = Root()
    root.mainloop()

    # main_httpx()
