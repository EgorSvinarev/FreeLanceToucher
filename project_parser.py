# coding: utf8

import requests
from bs4 import BeautifulSoup
from project import Project
import re
import datetime


class ProjectParser:
    URL = "https://freelancehunt.com/projects?skills%5B%5D=22&skills%5B%5D=99&skills%5B%5D=169&skills%5B%5D=180"

    def __init__(self):
        self.last_time_parsing = self.set_last_time_parsing()	
        self.identirificator = 0;

    def set_last_time_parsing(self):
        now_time = datetime.datetime.now()
        now_time = now_time.replace(hour = now_time.hour + 3)
        return now_time
    def get_data(self):
        respo = requests.get(self.URL)
        html = respo.text

        soup = BeautifulSoup(html, "html.parser")
        projects_div = soup.find("div", id="projects-html")
        projects_trs = projects_div.findAll("tr")

        respo = requests.get(self.URL + "&page=2")
        html = respo.text

        soup = BeautifulSoup(html, "html.parser")
        projects_div = soup.find("div", id="projects-html")
        projects_trs += projects_div.findAll("tr")

        projects = []
        for projects_tr in projects_trs:
            # Премиум заказ пропускаем
            if projects_tr.find("span", class_=("label")) != None:
                continue

            # Извлечение названия и ссылки на заказ
            a_tags = projects_tr.findAll("a")
            if (len(a_tags) == 0):
                continue

            project_url = a_tags[0].attrs["href"]
            projects_name = a_tags[0].text

            # Извлечение времени публикации заказа
            post_time_tag = projects_tr.find("h2")
            if (len(post_time_tag) > 0):
                project_post_time = re.match(
                    r"\d{2}:\d{2}", post_time_tag.text)

                # В публикации заказа может указываться как точное время в формате
                # hh:mm, так и только дата. Нам подходит тольк первый формат.
                if (project_post_time != None):
                    project_post_time = project_post_time.group()
                else:
                    continue

            # Отсеиваем заказы, с момента публикации которых прошло больше
            # получаса
            then_time = datetime.datetime.now().replace(hour = int(project_post_time[0:2]), minute = int(project_post_time[3:5]))
            delta = self.last_time_parsing - then_time

            if (delta.seconds // 3600 > 0 or (delta.seconds // 60 >= 30 and delta.seconds // 3600 == 0)):
                continue

            # Переходим на страницу проекта и парсим оттуда его описание
            respo = requests.get(project_url)
            html = BeautifulSoup(respo.text, "html.parser")
            description_div = html.find("div", id="project-description")
            description_p = description_div.findAll("p")

            project_description = ""

            for p in description_p:
                project_description += p.text + "\n"

            project = Project(projects_name, project_description,
                              project_url, project_post_time, self.identirificator)
            projects.append(project)
            self.identirificator += 1

        self.last_time_parsing = self.set_last_time_parsing()
        return projects
