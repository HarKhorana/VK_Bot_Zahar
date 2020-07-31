from vk_api import VkApi
from random import randint, choice
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from decouple import config
import requests
from bs4 import BeautifulSoup
from os import remove, environ
from reddit_post_finder import get_random_post, save_photo, list_of_memes_subs
from datetime import datetime

# API-key
token = config('TOKEN')

# Community authorization
vk = VkApi(token=token)

# Creates a connection with VK LongPoll server
longpoll = VkLongPoll(vk)


def corona_world_stats():
    url = 'https://www.worldometers.info/coronavirus/?'
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    numbers = soup.find_all('td')

            
    total_cases = numbers[135].text
    additional_cases_this_day = numbers[136].text

    total_deaths = numbers[137].text
    additional_deaths_this_day = numbers[138].text

    total_recoveries = numbers[139].text

    results = 'Случаи заражения в Мире: {} ({})' \
                    '\nКоличество смертей: {} ({})' \
                    '\nКоличество выздоровевших: {}'.format(total_cases, additional_cases_this_day,
                    total_deaths, additional_deaths_this_day, total_recoveries)
    
    return results


def corona_moscow_stats():
    url = 'https://coronavirus-control.ru/coronavirus-moscow/'
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    numbers = soup.find_all('b')

    total_cases = numbers[0].contents[0]
    additional_cases_this_day = numbers[0].contents[1].text

    total_deaths = numbers[2].contents[0]
    additional_deaths_this_day = numbers[2].contents[1].text

    total_recoveries = numbers[3].contents[0]
    additional_recoveries_this_day = numbers[3].contents[1].text

    lethality = numbers[4].contents[0]

    results = 'Случаи заражения в Москве: {} ({})' \
                '\nКоличество смертей: {} ({})' \
                '\nКоличество выздоровевших: {} ({})' \
                '\nЛетальность: {}'.format(total_cases, additional_cases_this_day, 
                total_deaths, additional_deaths_this_day, total_recoveries, 
                additional_recoveries_this_day, lethality)
    return results


# Main Keyboard--------------------------------------------------------------------------
keyboard_main = VkKeyboard(one_time=True)

keyboard_main.add_button('Лама', color=VkKeyboardColor.DEFAULT)
keyboard_main.add_button('Альпака', color=VkKeyboardColor.POSITIVE)

keyboard_main.add_line()  # Переход на вторую строку
keyboard_main.add_button('Мем', color=VkKeyboardColor.NEGATIVE)
keyboard_main.add_button('Коронавирус', color=VkKeyboardColor.PRIMARY)
# ---------------------------------------------------------------------------------------



# Coronavirus Statistics Keyboard--------------------------------------------------------
keyboard_corona_stats = VkKeyboard(one_time=True)

keyboard_corona_stats.add_button('Статистика по Миру', color=VkKeyboardColor.PRIMARY)
keyboard_corona_stats.add_button('Статистика по Москве', color=VkKeyboardColor.POSITIVE)
# ---------------------------------------------------------------------------------------


# Sends response to user with keyboard
def write_msg_with_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard.get_keyboard(),
                                "random_id": randint(1, 2147483647)},
              "a")

# Sends response to user without keyboard
def write_msg_without_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard.get_empty_keyboard(),
                                "random_id": randint(1, 2147483647)},
              "a")


def get_user_info(user_id):
    return vk.method('users.get', {'user_ids': user_id})


# Uploade saved pic from reddit to VK server
def upload_pic(user_id, path, origin):
    server = vk.method('photos.getMessagesUploadServer')
    post_request = requests.post(server['upload_url'], files={'photo': open(path, 'rb')}).json()
    save_message_photo = vk.method('photos.saveMessagesPhoto',
                                   {'photo': post_request['photo'], 'server': post_request['server'],
                                    'hash': post_request['hash']})[0]
    vk.method("messages.send",
              {"peer_id": user_id, "message": "Оригинал: " + origin.shortlink, "random_id": randint(1, 2147483647), 'keyboard': keyboard_main.get_keyboard(),
               "attachment": f'photo{save_message_photo["owner_id"]}_{save_message_photo["id"]}'}, )


# Goes through the whole process of finding, uploading and sending pic to user
def send_pic(user_id, sub):
    start = datetime.now()
    print('Searching for random post...')
    post_to_send = get_random_post(sub)
    print('Random post found', datetime.now() - start)

    start = datetime.now()
    print('Saving pic from post...')
    path_to_pic_file = save_photo(post_to_send)
    print('Pic saved', datetime.now() - start)

    start = datetime.now()
    print('Uploading...')
    upload_pic(user_id, path_to_pic_file, post_to_send)
    remove(path_to_pic_file)
    print('Uploaded successfully!', datetime.now() - start, '------------------------------------------------------')


def main():
    # Main cycle
    for event in longpoll.listen():
        # If a new message is received
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:

                # Message from user
                request = event.text.lower()

                # Request handling
                if request == "привет":
                    user_name = get_user_info(event.user_id)
                    write_msg_with_keyboard(event.user_id, "Привет, " + str(user_name[0]['first_name']) + "!" + " Выбери одну из категорий", keyboard_main)

                elif request == "коронавирус":
                    write_msg_with_keyboard(event.user_id, 'Выбери статистику...', keyboard_corona_stats)

                elif request == "статистика по миру":
                    write_msg_without_keyboard(event.user_id, "Загружаю статистику по миру...", keyboard_main)
                    write_msg_with_keyboard(event.user_id, corona_world_stats(), keyboard_main)

                elif request == "статистика по москве":
                    write_msg_without_keyboard(event.user_id, "Загружаю статистику по Москве...", keyboard_main)
                    write_msg_with_keyboard(event.user_id, corona_moscow_stats(), keyboard_main)

                elif request == "начать":
                    write_msg_with_keyboard(event.user_id, "Привет! Выбери одну из категорий", keyboard_main)

                elif request == "лама":
                    write_msg_without_keyboard(event.user_id, "Загружаю ламу...", keyboard_main)
                    send_pic(event.user_id, 'llama')

                elif request == "мем":
                    meme_sub = choice(list_of_memes_subs)
                    write_msg_without_keyboard(event.user_id, "Загружаю мем...", keyboard_main)
                    send_pic(event.user_id, meme_sub)

                elif request == "альпака":
                    write_msg_without_keyboard(event.user_id, "Загружаю альпаку...", keyboard_main)
                    send_pic(event.user_id, 'alpaca')

                # elif request == "help":
                #     write_msg(event.user_id, "Я пока не многое понимаю, но вот мой список команд:")

                elif request == "спокойной ночи":
                    write_msg_with_keyboard(event.user_id, "Good night, sweet prince", keyboard_main)

                else:
                    user_name = get_user_info(event.user_id)
                    write_msg_with_keyboard(event.user_id, str(user_name[0]['first_name']) + ", выбери одну из категорий...", keyboard_main)

        # elif event.type == VkEventType.USER_TYPING:
        #     write_msg(event.user_id, "ога, печатаешь?")


if __name__ == '__main__':
    print('Bot is initiated...')
    main()