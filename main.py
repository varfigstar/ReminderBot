import telebot
import threading
import time 
import config 
import os
import json
import logging


logging.basicConfig(level=logging.INFO)


bot = telebot.TeleBot(config.TOKEN)



def write_in_json(data, mode="+a"):

	with open("messages.json", mode, encoding="utf-8") as f:

		json_data = json.dumps(data, ensure_ascii=True, indent=4)
		f.write(json_data)

		logging.debug("New recording")


if os.path.exists("messages.json"):

	print("[System]: file with messages already exists")

else:

	print("[System]: file with messages isn't exist. Creating automaticly in current working directory")
	
	write_in_json([{"user_id": 0, "message_text": "", "is_active": False, "seconds_left": 0}])


def remind_to_user(bot):

	print("Thread with reminder runned")

	while  True:

		with open("messages.json", "r", encoding="utf-8") as file:
			data = file.read()

		number_of_dict = 0

		users_data = json.loads(data)
		for user in users_data:

			if user["user_id"] != 0 and user["is_active"] == True:

				if user["seconds_left"] != 0:

					user["seconds_left"] -= 1
					users_data[number_of_dict] = user
					write_in_json(users_data, "w")

				else:

					bot.send_message(user["user_id"], user["message_text"])
					user["seconds_left"] = 3595
					users_data[number_of_dict] = user
					write_in_json(users_data, "w")

			number_of_dict += 1

		time.sleep(1)






@bot.message_handler(commands=["start", "help"])
def getting_welcome(message):

	bot.send_message(message.chat.id, "Привет! С моей помощью ты можешь поставить себе напоминалку, и я буду оповещать тебя каждый час! Для того, чтобы остановить напоминалки, отправь мне команду /stop")


@bot.message_handler(commands=["stop"])
def stop_remind(message):

	bot.send_message(message.chat.id, "Хорошо! Напоминалки прекращаются и я удаляю ваше сообщение из базы! Для того, чтобы возобновить работу, просто отправьте мне сообщение")
	
	users_data = json.loads(open("messages.json").read())

	number_of_dict = 0
	for user in users_data:
		if user["user_id"] == message.chat.id:
			users_data.pop(number_of_dict)
		number_of_dict += 1

	write_in_json(users_data, mode="w")


@bot.message_handler(content_types=["text"])
def send_message(message):

	data = open("messages.json", "r", encoding="utf-8").read()
	json_data = json.loads(data)

	is_user_registered = False

	number_of_dict = 0
	for user in json_data:
		if int(user["user_id"]) == message.chat.id:
			is_user_registered = True
			json_data[number_of_dict]["message_text"] = message.text
			break
		number_of_dict += 1

	if not is_user_registered: 
		json_data.append({
			"user_id": message.chat.id, 
			"message_text": message.text,
			"is_active": True,
			"seconds_left": 3595
			})

	write_in_json(json_data, mode="w")




if __name__=="__main__":

	reminder_thread = threading.Thread(target=remind_to_user, args=(bot, ))
	reminder_thread.start()

	bot.polling(none_stop=False)