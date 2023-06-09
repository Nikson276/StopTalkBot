"""All db connection and command whould be here"""
import json
import sqlite3

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

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.rating_fields = ('voice_score', 'video_score')

# Read methods
    def get_group_id(self, group_id):
        """Достаем id чата в базе по его group_id"""
        try:
            result = self.cursor.execute("SELECT `id` FROM `group_settings` WHERE `group_id` = ?", 
                                        (group_id,))
            return result.fetchone()[0]
        except TypeError:
            return False        #no data was found

    def get_group_settings(self, group_id) -> tuple:
        """Достаем настройки чата в базе по его group_id"""
        # Проверка на существования записи
        id = self.get_group_id(group_id)
        
        #Читаем строку по ключу id
        if id:        #true        
            try:
                result = self.cursor.execute("SELECT `mode`, `video_hate` FROM `group_settings` WHERE `id` = ?", 
                                            (id,))
                return result.fetchone()    #tuple ('guard', 0)
            except TypeError:
                return False        #no data was found


    def get_rating_id(self, group_id, user_id):
        """Достаем id записи рейтинга по группе и юзеру в базе"""
        try:
            if user_id is None:
                #select by group only
                print("Select с возвращением всего списка.")
                result = self.cursor.execute("SELECT `id` FROM `rating_board` WHERE `group_id` = ?", 
                                            (group_id,))
                return result.fetchall()    #->list[tuple] 
            else:
                #full key select
                result = self.cursor.execute("SELECT `id` FROM `rating_board` WHERE `group_id` = ? AND `user_id` = ?", 
                                            (group_id, user_id,))
                return result.fetchone()[0]
        except TypeError:
            return False        #no data was found        
    
    
    def get_records(self, group_id):
        """Получает рейтинг для всей группы"""
        #это все лучше потом вынесты в отдельный модуль (файл)
        db_query_rating = """
        SELECT *
        FROM `rating_board` 
        WHERE `group_id` = ?
        """
         
        result = self.cursor.execute(db_query_rating, (group_id,))
        return result.fetchall()

    def get_rating_value(self, group_id, user_id) -> list[tuple]:
        """Достаем текущее значения рейтинга (rate) по id записи в базе"""
        try:
            result = self.cursor.execute("SELECT `voice_score`, `video_score` FROM `rating_board` WHERE `id` = ?", 
                                        (self.get_rating_id(group_id, user_id),))
            return result.fetchall()[0]
        except TypeError:
            return None        #no data was found   

#Update methods
    def upd_group(self, group_id, mode='polite', video_hate=0):
        """Обновляем настройки группы в базе"""
        #Проверка на существования записи
        id = self.get_group_id(group_id)
        
        #обновление\добавление записи в бд
        if id:        #true
            #UPD method
            print(f"dbLOG: upd_group обновляем настройки для {group_id}, делаем update, mode='{mode}', video={video_hate}")
            self.cursor.execute("UPDATE `group_settings` SET `mode` = ?, `video_hate` = ? WHERE `id` = ?", 
                                (mode, video_hate, id,))
        else:         #false
            #insert method 
            print(f"dbLOG: upd_group добавляем новую группу {group_id}, делаем insert")
            self.cursor.execute("INSERT INTO `group_settings` (`group_id`) VALUES (?)", 
                                (group_id,))
        return self.conn.commit()    
    
    def upd_user_rating(self, group_id, user_id, rate='voice_score'):
        """Добавляем в счетчик кол-во для рейтинга юзера в базу
        Параметр rate может принимать на вход только значения из кортежа
        rating_fields
        """
        #Проверка поля рейтинга
        if rate not in self.rating_fields:
            #поле не существует
            return(print("dbLOG: Error, column not exist in bd"))
        else:
            #Cчитаем текущее кол-во
            voice, video = self.rating_fields       #tuple unpacking
            voice_qty, video_qty = self.get_rating_value(group_id, user_id)
            print(f'Возвращается voice: {voice_qty} video: {video_qty}')
            
            if voice_qty or video_qty:         #true
                #UPD method
                #тернарный оператор
                qty = voice_qty + 1 if rate == voice else video_qty + 1
                print(f"dbLOG: upd_rating кол-во сущесует, новое = {qty}, делаем update")
                #добавляем в рейтинг (rate) кол-во
                if rate == voice:
                    #`voice_score`
                    self.cursor.execute("UPDATE `rating_board` SET `voice_score` = ? WHERE `id` = ?", 
                                        (qty, self.get_rating_id(group_id, user_id),))
                elif rate == video:
                    #`video_score`
                    self.cursor.execute("UPDATE `rating_board` SET `video_score` = ? WHERE `id` = ?", 
                                        (qty, self.get_rating_id(group_id, user_id),))                    
            else:            #false
                #insert method
                qty = 1
                print(f"dbLOG: upd_rating кол-во начальное = {qty}, делаем insert")
                #добавляем в рейтинг (rate) кол-во
                if rate == voice:
                    #`voice_score`        
                    self.cursor.execute("INSERT INTO `rating_board` (`group_id`, `user_id`, `voice_score`) VALUES (?,?,?)", 
                                        (group_id, user_id, qty,))                         
                elif rate == video:
                    #`video_score` 
                    self.cursor.execute("INSERT INTO `rating_board` (`group_id`, `user_id`, `video_score`) VALUES (?,?,?)", 
                                        (group_id, user_id, qty,))                                                   
                
            return self.conn.commit()
    
    
#Delete methods
    #here
    def delete_group(self, group_id):
        """Удаляем настройки группы из базы"""
        #Проверка на существования записи
        id = self.get_group_id(group_id)
        
        #удаление записи из бд
        if id:        #true
            #DELETE method
            print(f"dbLOG: delete_group удаляем {group_id}")
            self.cursor.execute("DELETE FROM `group_settings` WHERE `id` = ?", 
                                (id,))
            
            #запускаем очистку таблицы рейтингов по всей группе
            self.delete_user_rating(group_id)

        return self.conn.commit()  
        
    def delete_user_rating(self, group_id, user_id=None):
        """Удаляем записи рейтинга из базы"""
        #Проверка на существования записи
        id = self.get_rating_id(group_id, user_id)
        
        #удаление записи из бд
        if id and user_id is None:        #true and true
            #DELETE method
            print(f"dbLOG: delete_user_id удаляем записи всей группы= {group_id}")
            print("Список ли это id", id)
            for value in id:
                #delete each id from list - id
                print("dbLOG: удаляем в цикле")
                self.cursor.execute("DELETE FROM `rating_board` WHERE `id` = ?", 
                                    (value[0],))
        elif id:        #true
            #DELETE method
            print(f"dbLOG: delete_user_id удаляем запись группы= {group_id} для юзера= {user_id}")
            self.cursor.execute("DELETE FROM `rating_board` WHERE `id` = ?", 
                                (id,))
        else:
            return("dbLOG: Delete error. Not found")            
            
            
        return self.conn.commit()              

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()



















# Use later updates
# import sqlite3

# class BotDB:

#     def __init__(self, db_file):
#         self.conn = sqlite3.connect(db_file)
#         self.cursor = self.conn.cursor()

#     def user_exists(self, user_id):
#         """Проверяем, есть ли юзер в базе"""
#         result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
#         return bool(len(result.fetchall()))

#     def get_user_id(self, user_id):
#         """Достаем id юзера в базе по его user_id"""
#         result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
#         return result.fetchone()[0]

#     def add_user(self, user_id):
#         """Добавляем юзера в базу"""
#         self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
#         return self.conn.commit()

#     def add_record(self, user_id, operation, value):
#         """Создаем запись о доходах/расходах"""
#         self.cursor.execute("INSERT INTO `records` (`users_id`, `operation`, `value`) VALUES (?, ?, ?)",
#             (self.get_user_id(user_id),
#             operation == "+",
#             value))
#         return self.conn.commit()

#     def get_records(self, user_id, within = "all"):
#         """Получаем историю о доходах/расходах"""

#         if within == "day":
#             result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY `date`",
#                 (self.get_user_id(user_id),))
#         elif within == "week":
#             result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY `date`",
#                 (self.get_user_id(user_id),))
#         elif within == "month":
#             result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY `date`",
#                 (self.get_user_id(user_id),))
#         else:
#             result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? ORDER BY `date`",
#                 (self.get_user_id(user_id),))

#         return result.fetchall()

#     def close(self):
#         """Закрываем соединение с БД"""
#         self.connection.close()