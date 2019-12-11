#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Библиотека Twisted
#
#  https://twistedmatrix.com/
#  https://pypi.org/project/Twisted/
#
#  Работа с TCP протоколами Twisted, базовой сервер
#
#  1. pip install twisted - установка пакета
#  2. from twisted import ... - подключить в файле .py
#

#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
#  Ctrl + Alt + L - форматирование кода
#
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver

class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        # Потенциальный баг для внимательных =)
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def send_history(self):
        # отсылаем историю
        for h_rec in self.factory.history_list:
            self.sendLine(h_rec.encode())

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Message from {self.login}: {content}"
            # добавляем в историю сообщение
            self.factory.history_list.append(content)
            if len(self.factory.history_list) > 10:
                # оставляем последние 10
                self.factory.history_list = self.factory.history_list[len(self.factory.history_list)-10:]

            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())
        else:
            # login:admin -> admin
            if content.startswith("login:"):
                content = content.replace("login:", "")
                # проверка что логин уже зареган
                if not content in self.factory.login_list:
                    self.login = content
                    self.factory.login_list.append(content)
                    self.sendLine(("Welcome! " + self.login).encode())
                    self.send_history()
                else: # логин уже зареган !
                  self.sendLine((f"Login Name < {content} > is already use, try anothe login name").encode())
            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    login_list : list
    history_list : list

    def startFactory(self):
        self.clients = []
        self.login_list = []
        self.history_list = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
