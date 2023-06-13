"""All db connection and command whould be here"""
import json
import sqlite3

import sql_query

# init local db json file for constant text data
DATABASE = {}

"""____________logic to work with JSON__________"""


def read() -> dict:
    global DATABASE
    with open("database.json", 'r', encoding='utf-8') as f:
        DATABASE = json.load(f)


def update() -> bool:
    '''Общая функция обновления файла json'''
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(DATABASE, f, sort_keys=True, ensure_ascii=False, indent=2)
    read()      # refresf db
    return True


def settings_upd(key, value) -> bool:
    '''Обновление настроек словаря "settings" в DATABASE'''
    dict_name = "settings"
    DATABASE[dict_name][key] = value

    # вызываем функцию обновления бд
    if update():
        print(f"LOG: Словарь settings обновлен. Key={key}, value={value}")
        return True
    else:
        print(f"LOG: Словарь settings не обновлен."
              f"неизвестная ошибка Key={key}, value={value}")
        return False


# init database
read()

"""____________sqlite DB connection and methods__________"""


class BotDB:

    def __init__(self, db_file) -> None:
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.rating_fields = ('voice_score', 'video_score')

# Read methods
    def get_group_id(self, group_id):
        """Достаем id чата в базе по его group_id"""
        try:
            result = self.cursor.execute(sql_query.GROUP_ID, (group_id,))
            return result.fetchone()[0]
        except TypeError:
            return False        # no data was found

    def get_group_settings(self, group_id) -> tuple:
        """Достаем настройки чата в базе по его group_id"""
        # Проверка на существования записи
        id = self.get_group_id(group_id)

        # Читаем строку по ключу id
        if id:        # true
            try:
                result = self.cursor.execute(sql_query.SETTINGS, (id,))
                return result.fetchone()    # tuple ('guard', 0)
            except TypeError:
                return False        # no data was found

    def get_rating_id(self, group_id, user_id) -> list:
        """Достаем id записи рейтинга по группе и юзеру в базе"""
        try:
            if user_id is None:
                # select by group only
                result = self.cursor.execute(sql_query.RATING_ID, (group_id,))
                return result.fetchall()    # ->list[tuple]
            else:
                # full key select
                result = self.cursor.execute(sql_query.RATING_ID_FULL,
                                             (group_id, user_id,))
                return result.fetchone()[0]
        except TypeError:
            return False        # no data was found

    def get_records(self, group_id) -> list[tuple]:
        """Получает рейтинг для всей группы"""
        result = self.cursor.execute(sql_query.RATING_RECORD, (group_id,))
        return result.fetchall()

    def get_rating_value(self, group_id, user_id) -> list:
        """Достаем текущее значения рейтинга (rate) по id записи в базе"""
        try:
            result = self.cursor.execute(sql_query.RATING_VALUE,
                                         (self.get_rating_id(group_id,
                                                             user_id),
                                          )
                                         )
            return result.fetchall()[0]
        except (TypeError, IndexError):
            return [False, False]        # no data was found

# Update methods
    def upd_group(self, group_id, mode='polite', video_hate=0) -> None:
        """Обновляем настройки группы в базе"""
        # Проверка на существования записи
        id = self.get_group_id(group_id)

        # обновление\добавление записи в бд
        if id:        # true
            # UPD method
            print(f"dbLOG: обновляем настройки для {group_id},"
                  f"делаем update, mode='{mode}', video={video_hate}")
            self.cursor.execute(sql_query.UPD_GROUP,
                                (mode, video_hate, id,))
        else:         # false
            # insert method
            print(f"dbLOG: добавляем новую группу {group_id}, insert")
            self.cursor.execute(sql_query.INS_GROUP, (group_id,))
        return self.conn.commit()

    def upd_user_rating(self, group_id, user_id, rate='voice_score'):
        """Добавляем в счетчик кол-во для рейтинга юзера в базу
        Параметр rate может принимать на вход только значения из кортежа
        rating_fields
        """
        # Проверка поля рейтинга
        if rate not in self.rating_fields:
            # поле не существует
            return (print("dbLOG: Error, column not exist in bd"))
        else:
            # Cчитаем текущее кол-во
            voice, video = self.rating_fields       # tuple unpacking
            voice_qty, video_qty = self.get_rating_value(group_id, user_id)
            print(f'Возвращается voice: {voice_qty} video: {video_qty}')

            if voice_qty or video_qty:         # true
                # UPD method
                # тернарный оператор
                qty = voice_qty + 1 if rate == voice else video_qty + 1
                print(f"dbLOG: кол-во сущесует, новое = {qty}, делаем update")
                # добавляем в рейтинг (rate) кол-во
                if rate == voice:
                    # `voice_score`
                    self.cursor.execute(sql_query.UPD_RATING_VOICE,
                                        (qty, self.get_rating_id(group_id,
                                                                 user_id),))
                elif rate == video:
                    # `video_score`
                    self.cursor.execute(sql_query.UPD_RATING_VIDEO,
                                        (qty, self.get_rating_id(group_id,
                                                                 user_id),))
            else:            # false
                # insert method
                qty = 1
                print(f"dbLOG: кол-во начальное = {qty}, делаем insert")
                # добавляем в рейтинг (rate) кол-во
                if rate == voice:
                    # `voice_score`
                    self.cursor.execute(sql_query.INS_RATING_VOICE,
                                        (group_id, user_id, qty,))
                elif rate == video:
                    # `video_score`
                    self.cursor.execute(sql_query.INS_RATING_VIDEO,
                                        (group_id, user_id, qty,))

            return self.conn.commit()

# Delete methods
    def delete_group(self, group_id) -> None:
        """Удаляем настройки группы из базы"""
        # Проверка на существования записи
        id = self.get_group_id(group_id)

        # удаление записи из бд
        if id:        # true
            # DELETE method
            print(f"dbLOG: delete_group удаляем {group_id}")
            self.cursor.execute(sql_query.DEL_GROUP, (id,))

            # запускаем очистку таблицы рейтингов по всей группе
            self.delete_user_rating(group_id)

        return self.conn.commit()

    def delete_user_rating(self, group_id, user_id=None):
        """Удаляем записи рейтинга из базы"""
        # Проверка на существования записи
        id = self.get_rating_id(group_id, user_id)

        # удаление записи из бд (Все или выборочно)
        if id and user_id is None:        # true and true
            # DELETE method
            print(f"dbLOG: удаляем записи всей группы= {group_id}")
            for value in id:
                # delete each id from list - id
                print("dbLOG: удаляем в цикле")
                self.cursor.execute(sql_query.DEL_RATING,
                                    (value[0],))
        elif id:        # true
            # DELETE method
            print(f"dbLOG: удаляем запись группы= {group_id} "
                  f"для юзера= {user_id}")
            self.cursor.execute(sql_query.DEL_RATING,
                                (id,))
        else:
            return ("dbLOG: Delete error. Not found")

        return self.conn.commit()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
