import time
import re
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver

with open("./creds.json", 'r') as file:
    creds = json.loads(file.read())


class ClassBot(webdriver.Chrome):
    _USERNAME = creds['username']
    _PASSWORD = creds['password']

    TRxPATH = """//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div/div/div[2]/table/tbody/tr[{idx}]"""
    JOINxPATH = """//*[@id="meetingSummary"]/div/div/a"""

    def __init__(self, delay=1):
        super().__init__()
        self.delay = delay
        self.get("https://myclass.lpu.in")

    def __repr__(self,):
        return f"""LpuBot(
    username = {self._USERNAME},
    session = {self.session_id}
)"""

    def login(self,):
        username_field = self.find_element_by_name("i")
        password_field = self.find_element_by_name("p")

        username_field.send_keys(self._USERNAME)
        password_field.send_keys(self._PASSWORD)
        password_field.send_keys(Keys.RETURN)

        return self

    def open_time_table(self,):
        self.get(
            "https://lovelyprofessionaluniversity.codetantra.com/secure/tla/m.jsp")
        return self

    def create_time_table(self,) -> dict:
        tr = re.compile("\d+:\d+")
        time_table = {}

        for i in self.find_elements_by_tag_name("a")[13:]:
            start, *_ = tr.findall(i.text)
            H, M = map(int, start.split(":"))
            time_table[H] = {M: {"class": i, "duration": list(
                map(lambda x: list(map(int, x.split(":"))), tr.findall(i.text)))}}

        if not len(time_table):
            return self.create_time_table()
        return time_table

    def attend_class(self, cls):
        cls['class'].click()
        self.find_element_by_xpath(self.JOINxPATH).click()
        return

    def mainloop(self,):
        while True:
            time_table = self.create_time_table()
            ts_h, ts_m = map(int, time.strftime("%I:%M").split(":"))
            pv_h = (ts_h-1)+(int(not bool(ts_h-1))*12)

            if ts_h in time_table:
                ts_h = time_table[ts_h]
                for m in ts_h:
                    return self.attend_class(ts_h[m])

            elif (pv_h in time_table):
                ts_h = time_table[pv_h]
                for m in ts_h:
                    if m > 50:
                        return self.attend_class(ts_h[m])
            else:
                print(f"No Class At : {(ts_h,ts_m)}")
            time.sleep(self.delay)

if __name__ == '__main__':
    ClassBot().login().open_time_table().mainloop()