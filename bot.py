# coding: utf8

from project_parser import ProjectParser
from time import sleep
from project import Project
import requests
import logging

# Твой токен telegram-бота
TOKEN = ""
# Id telegram-канала
CHANNEL_ID = ""

parser = ProjectParser()
cache = {}

# Настроим логирование 
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO, filename = "log.txt")

def send_message(project):
	message = project.name + "\n\n" + project.description + "\n\n" + project.url
	try:
		requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id=@{}&text={}".format(TOKEN, CHANNEL_ID, message))
	except:
		logging.error("Ошибка в отправке запроса. Публикация проекта отменяется.")

iteration_counter = 0;

while True:
	projects = []
	logging.info("Парсим проекты с freelancehunt.com")
	projects = parser.get_data()
	# except:
		# logging.error("Не удалось получить проекты с freelancehunt.com")
		
	logging.info("Всего получено " + str(len(projects)) + " проектов.")

	logging.info("Проекты в кэше: " + ", ".join(list(map(str, list(cache.keys())))))

	logging.info("Начинаем постить проекты в telegram канал.")
	for i in range(len(projects)):
		logging.info("Id проекта в обработке: " + str(projects[i].id_) + ". " + projects[i].name)		
		if (projects[i].id_ not in list(cache.keys())):
			cache[projects[i].id_] = projects[i]
			send_message(projects[i])
			logging.info("Проект опубликова на канале. Delay(180)")
			sleep(180)
		else:
			logging.info("Проект с id = " + str(projects[i].id_) +" уже находится в кэше, поэтому он не публикуется.")	

	logging.info("Обработка проектов завершена. Delay(300)")		

	iteration_counter += 1

	if iteration_counter == 6:
		cache = {}

	sleep(300)
