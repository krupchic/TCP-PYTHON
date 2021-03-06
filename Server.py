# -*- coding: utf-8 -*-


__author__ = "Voronin Denis Albertovich"
# connection-oriented server

import socket
import sqlite3
import os
import datetime
import threading
import time
import hashlib
import DM
from INSTALL import read_ini
from SysLog import AddToLog
# Server options

class SessionData:
    client_name = 'unknown'
    ip = '127.0.0.1'
    dt = datetime.datetime.now
    data = ''

    def parse_inp_str(self, inp_str):
        if inp_str.find('pc_name', 0, len(inp_str)) != -1:
            self.client_name = inp_str[inp_str.find('pc_name:', 0) + 8: inp_str.find('ip:', 0)]

            self.ip = inp_str[inp_str.find('ip:', 0) + 3: inp_str.find('dt:', 0)]

            self.dt = inp_str[inp_str.find('dt:', 0) + 3:]

    def sql_ins_session(self):
        try:
            conn = sqlite3.connect('sessions.db')
            c = conn.cursor()
            c.execute('''INSERT INTO SES VALUES(:s1,:s2,:s3)''', (self.client_name, self.ip, self.dt))
            conn.commit()
            conn.close()
        except sqlite3.DatabaseError:
            AddToLog("Database Error")

    def sql_ins_data(self):
        try:
            conn = sqlite3.connect('sessions.db')
            c = conn.cursor()
            c.execute('''INSERT INTO DATA(dt,data) VALUES(:d2,:d3)''',
                      ((datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),  self.data)))
            conn.commit()
            conn.close()
            AddToLog(self.ip + '---' + "Writing to base ... Ок")
        except sqlite3.DatabaseError:
            AddToLog(self.ip + '---' + "Error:" + sqlite3.DatabaseError)

    def sql_ins_user(self, name):

            conn = sqlite3.connect('sessions.db')
            c = conn.cursor()
            c.execute('''INSERT INTO USERS(name) VALUES(:d2)''', (name,) )
            conn.commit()
            conn.close()

            AddToLog(self.ip + '---' + "Writing to base ... Ок")


            AddToLog(self.ip + '---' + "Error:" + (sqlite3.DatabaseError))

    def sql_ins_photo(self, name):

            conn = sqlite3.connect('sessions.db')
            c = conn.cursor()
            c.execute('''INSERT INTO USERS(name) VALUES(:d2)''', (name,) )
            conn.commit()
            conn.close()

            AddToLog(self.ip + '---' + "Writing to base ... Ок")


            AddToLog(self.ip + '---' + "Error:" + (sqlite3.DatabaseError))





# Our thread class:
class ClientThread(threading.Thread):
    sess = SessionData()
    clients = []

    # Override Thread's __init__ method to accept the parameters needed:

    def __init__(self, channel, details):
        self.channel = channel
        self.details = details
        self.killed = False
        self.thread = threading.current_thread()
        threading.Thread.__init__(self)

    def kill(self):
        self.killed = True

    def run(self):
        #self.get_session_info()
        try:
            while True:
                if self.type_input_data() == 'info':
                    self.get_session_info()
                if self.type_input_data() == 'data':
                    self.get_data()
        except Exception:
            AddToLog('Unknown reserving data type')


    def listen_data(self):
        answer = ((str(self.channel.recv(1024).decode("utf-8"))));
        if (answer != ''):
            return answer;

    def type_input_data(self):

        data = self.listen_data()

        if data.find('info//', 0) != -1:
            self.sess.parse_inp_str(data)
            return 'info'

        if data.find('data//', 0) != -1:
            self.sess.data = data
            return 'data'

    def get_session_info(self):

        try:

            AddToLog("-----------------------------------------------------------------")
            AddToLog(self.sess.ip + '---' + 'Reserve session data... <-- ' +
            self.sess.client_name + ' ' + self.sess.dt + ' ' + self.sess.ip)
            self.sess.sql_ins_session()
            AddToLog(self.sess.ip + '---' + 'Send confirm data... --> ' + self.details[0])
            self.channel.send(bytes('sess_ok ' + str(self.channel), 'utf-8'))
            time.sleep(1)
        except Exception:
            AddToLog('Connection refuse...' + self.details[0])

    def get_data(self):
        try:
            AddToLog(self.sess.ip + '---' + 'Reserve main data...<-- ' + self.sess.data[5:])
            self.sess.sql_ins_data()
            AddToLog(self.sess.ip + '---' + 'Send confirm data...  --> ' + self.details[0])
            self.channel.send(bytes('data_ok'+"\r\n", 'utf-8'))
            AddToLog("-----------------------------------------------------------------")

            time.sleep(1)


        except Exception:
            AddToLog(self.sess.ip + '---' + 'Connection refuse...' + self.details[0])

    def data_parse(self):
        pass

curr_sess = SessionData()


class Server:

    run = True

    sessions = []

    base_locate = os.curdir

    def __init__(self, host = 'localhost', port = 1800, clientthread_ =None):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.ClientThread = clientthread_
        DataModul = DM.BASE('sessions.db')
        CreateBase = read_ini()
        if not os.path.exists(self.base_locate + '/sessions.db'):
            if not os.path.isfile(self.base_locate + '/sessions.db'):
                DataModul.cr_base(CreateBase)

    def start_server(self):

        self.run = True
        AddToLog('+++++++++++++++++++++++++++++++++++++++++++++++++++')
        AddToLog("++ TCP Server Start, waiting clients...")
        AddToLog('++ Server address: ' + self.host + '  Port: ' + str(self.port))
        AddToLog('+++++++++++++++++++++++++++++++++++++++++++++++++++')


        try:
            while True:
                if self.run:
                        channel, details = self.server_socket.accept()
                        self.ClientThread(channel, details).start()

        except Exception:
            AddToLog('---Server Stopped!----')


    def stop_server(self):

        try:
            self.run = False
            AddToLog('-----User stop server-----')
            exit(0)
        except Exception:
            AddToLog('---Fail Stop Server!!----')





# def cr_base():
#     global conn
#     try:
#         conn = sqlite3.connect('sessions.db')
#         c = conn.cursor()
#         AddToLog("Initialization Database...")
#         c.execute('CREATE TABLE IF NOT EXISTS SES (CLIENT_NAME TEXT, IP TEXT, DT DATE)')
#         c.execute('CREATE TABLE IF NOT EXISTS DATA (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, DT DATE, DATA TEXT)')
#         c.execute('CREATE TABLE IF NOT EXISTS LOG (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, DT DATE, LOG_SYS TEXT)')
#         conn.commit()
#         AddToLog('Initialization complete.')
#         conn.close()
#     except Exception:
#         conn.close()
#         AddToLog('Initialization Database Error!.')
#         exit()


#DataModul.del_base(); ###Удаление файла базы
#Запуск сервера
#serv.start_server()   ###Запуск    Сервера
#serv.stop_server      ###Остановка Сервера
