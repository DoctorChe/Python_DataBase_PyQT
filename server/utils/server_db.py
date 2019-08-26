from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from server.utils.config_server import SERVER_DATABASE
import datetime


# Класс - серверная база данных:
class ServerStorage:
    Base = declarative_base()

    association_table = Table(
        "association",
        Base.metadata,
        Column("user_id", Integer, ForeignKey("users.id")),
        Column("contact_id", Integer, ForeignKey("contact.id"))
    )

    # Класс - отображение таблицы всех пользователей
    # Экземпляр этого класса = запись в таблице AllUsers
    class AllUsers(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        last_login = Column(String)
        # sessions = relationship("Contact", back_populates="user")
        contact = relationship("Contact",
                               secondary="association")

        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()

    # Класс - отображение таблицы активных пользователей:
    # Экземпляр этого класса = запись в таблице ActiveUsers
    class ActiveUsers(Base):
        __tablename__ = "active_users"
        id = Column(Integer, primary_key=True)
        user = Column(ForeignKey("users.id"), unique=True)
        ip_address = Column(String)
        port = Column(Integer)
        login_time = Column(DateTime)

        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    # Класс - отображение таблицы истории входов
    # Экземпляр этого класса = запись в таблице LoginHistory
    class LoginHistory(Base):
        __tablename__ = "login_history"
        id = Column(Integer, primary_key=True)
        name = Column(ForeignKey("users.id"))
        date_time = Column(DateTime)
        ip = Column(String)
        port = Column(Integer)

        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    class Contact(Base):
        __tablename__ = "contact"
        id = Column(Integer, primary_key=True, autoincrement=True)
        contact_id = Column(ForeignKey("users.id"))
        # user = relationship("AllUsers", back_populates="contacts")
        # add_user_id = Column(ForeignKey("users.id"))
        # add_user_id = Column(Integer)
        # add_user = relationship("AllUsers", back_populates="contacts")

        def __init__(self, contact_id, user, add_user_id):
            self.id = None
            self.contact_id = contact_id
            # self.user = user
            # self.add_user_id = add_user_id

    def __init__(self):
        # Создаём движок базы данных
        # SERVER_DATABASE - sqlite:///server/db/server_db.sqlite3
        # echo=False - отключаем ведение лога (вывод sql-запросов)
        # pool_recycle - По умолчанию соединение с БД через 8 часов простоя обрывается.
        # Чтобы это не случилось нужно добавить опцию pool_recycle = 7200 (переустановка соединения через 2 часа)
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)

        # Метаданные доступны через класс Base
        self.metadata = self.Base.metadata

        # # Таблица доступна через атрибут класса
        # users_table = self.AllUsers.__table__
        # active_users_table = self.ActiveUsers.__table__
        # user_login_history = self.LoginHistory.__table__

        # Создаём таблицы
        self.metadata.create_all(self.database_engine)

        # Создаём сессию
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        # Когда устанавливаем соединение, очищаем таблицу активных пользователей
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # Функция выполняющяяся при входе пользователя, записывает в базу факт входа
    def user_login(self, username, ip_address, port):
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        result = self.session.query(self.AllUsers).filter_by(name=username)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
        # Если нету, то создаздаём нового пользователя
        else:
            # Создаем экземпляр класса self.AllUsers, через который передаем данные в таблицу
            user = self.AllUsers(username)
            self.session.add(user)
            # Комит здесь нужен, чтобы присвоился ID
            self.session.commit()

        # Теперь можно создать запись в таблицу активных пользователей о факте входа.
        # Создаем экземпляр класса self.ActiveUsers, через который передаем данные в таблицу
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # и сохранить в историю входов
        # Создаем экземпляр класса self.LoginHistory, через который передаем данные в таблицу
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        # Сохраняем изменения
        self.session.commit()

    # Функция фиксирующая отключение пользователя
    def user_logout(self, username):
        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы AllUsers
        user = self.session.query(self.AllUsers).filter_by(name=username).first()

        # Удаляем его из таблицы активных пользователей.
        # Удаляем запись из таблицы ActiveUsers
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        # Применяем изменения
        self.session.commit()

    # Функция возвращает список известных пользователей со временем последнего входа.
    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
        )
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращает список активных пользователей
    def active_users_list(self):
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
            ).join(self.AllUsers)
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращающая историю входов по пользователю или всем пользователям
    def login_history(self, username=None):
        # Запрашиваем историю входа
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    # def add_contact(self, username):
    #     user = self.session.query(self.AllUsers).filter_by(name=username).first()
    #     if user:
    #         contact = self.Contact(user.id)
    #         self.session.add(contact)
    #         # Сохраняем изменения
    #         self.session.commit()

    def get_contacts(self, username):
        contact_list = []
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        user_id = user.id
        contacts = self.session.query(self.association_table).filter_by(user_id=user_id)
        for contact in contacts:
            contact_list.append(contact.contact_id)
        return contact_list


# Отладка
if __name__ == "__main__":
    SERVER_DATABASE = "sqlite:///server_db.sqlite3"
    test_db = ServerStorage()
    # выполняем 'подключение' пользователя
    test_db.user_login("client_1", "192.168.1.4", 8888)
    test_db.user_login("client_2", "192.168.1.5", 7777)
    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())
    # выполянем 'отключение' пользователя
    test_db.user_logout("client_1")
    # выводим список активных пользователей
    print(test_db.active_users_list())
    # запрашиваем историю входов по пользователю
    test_db.login_history("client_1")
    # выводим список известных пользователей
    print(test_db.users_list())
    # test_db.add_contact("client_1")
    # int(test_db.get_contacts("client_1"))
