"""Константы для jim протокола, настройки"""

ACTION = "action"  # тип сообщения между клиентом и сервером
TIME = "time"  # время запроса
TYPE = "type"  # необязательное поле
USER = "user"  # данные о пользователе - клиенте (вложенный словарь)
ACCOUNT_NAME = "account_name"  # имя пользователя - чата
STATUS = "status"  # статус пользователя
RESPONSE = "response"  # код ответа
ERROR = "error"  # текст ошибки
ALERT = "alert"  # информационное сообщение
TO = "message_to"  # получатель
FROM = "account_name"  # отправитель
MESSAGE = "text"  # текст сообщения

# Значения (Методы протокола (actions))
PRESENCE = "presence"  # присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online
PROBE = "probe"  # проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online
MSG = "msg"  # простое сообщение пользователю или в чат
QUIT = "quit"  # отключение от сервера
AUTHENTICATE = "authenticate"  # авторизация на сервере
JOIN = "join"  # присоединиться к чату
LEAVE = "leave"  # покинуть чат
GET_CONTACTS = "get_contacts"  # получить список контактов

# Коды ответов (будут дополняться)
# 1xx — информационные сообщения
BASIC_NOTICE = 100  # базовое уведомление
IMPORTANT_NOTICE = 101  # важное уведомление
# 2xx — успешное завершение
OK = 200  # OK
CREATED = 201  # объект создан
ACCEPTED = 202  # подтверждение
# 4xx — ошибка на стороне клиента
WRONG_REQUEST = 400  # неправильный запрос/json объект
NOT_AUTORIZED = 401  # не авторизован
WRONG_LOGIN_PASSWORD = 402  # неправильный логин/пароль
FORBIDDEN = 403  # пользователь заблокирован
NOT_FOUND = 404  # пользователь/чат отсутствует на сервере
CONFLICT = 409  # уже имеется подключение с указанным логином
GONE = 410  # адресат существует, но недоступен (offline)
CLOSED = 499  # Client Closed Request (клиент закрыл соединение)
# 5xx — ошибка на стороне сервера
SERVER_ERROR = 500  # ошибка сервера

# Словари - ответы:
# # 200
# RESPONSE_200 = {RESPONSE: 200}
# # 400
# RESPONSE_400 = {
#             RESPONSE: 400,
#             ERROR: None
#         }
# 499
RESPONSE_499 = {
            RESPONSE: 499,
            ERROR: "Client Closed Request"
        }

# Кортеж из кодов ответов
RESPONSE_CODES = (
    BASIC_NOTICE,
    IMPORTANT_NOTICE,
    OK,
    CREATED,
    ACCEPTED,
    WRONG_REQUEST,
    NOT_AUTORIZED,
    WRONG_LOGIN_PASSWORD,
    FORBIDDEN,
    NOT_FOUND,
    CONFLICT,
    GONE,
    SERVER_ERROR
)

# ENCODING = "utf-8"  # кодировка
