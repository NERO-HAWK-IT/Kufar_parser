import psycopg2
from psycopg2 import extras
from environs import Env

env = Env()
env.read_env()

db_name = env('DBNAME')
db_user = env('DBUSER')
db_password = env('DBPASSWORD')
db_host = env('HOST')
db_port = env('PORT')


class DB_Postgres:
    __instance = None

    def __new__(cls, *args, **kwargs):  #
        if cls.__instance in None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, db_name, user, password, host, port):
        self.__dbname = db_name
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port

    def fetch_one(self, query: str, data: tuple = None, factory=None, clean=None):
        """"""
        try:
            with self.__connect(factory) as cursor:
                self.__execute(cursor, query, data)
                return self.__fetch(cursor, clean)
        except (Exception, psycopg2.Error) as error:
            self.__error(error)

    def fetch_all(self, query: str, data: tuple = None, factory=None):
        try:
            with self.__connect(factory) as cursor:
                self.__execute(cursor, query, data)
                return self.fetch_all()
        except (Exception, psycopg2.Error) as error:
            self.__error(error)

    def update_query(self, query: str, data: tuple = None, many = False, message = 'OK'):
        try:
            with self.__connect() as cursor:
                self.__execute(cursor, query, data, many)
                print(message)
        except (Exception, psycopg2.Error) as error:
            self.__error(error)

    def __connect(self, factory: str = None):
        """

        :param factory: в каком виде будут выводиться данные
        :return: cursor
        """
        connection = psycopg2.connection(
            db_name=self.__dbname,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )
        connection.autocommit = True

        if factory == 'dict':
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        elif factory == 'list':
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        else:
            cursor = connection.cursor()

        return cursor

    @staticmethod
    def __execute(cursor, query, argument=None, many=False):
        if many:
            if argument:
                cursor.executemany(query, argument)
            else:
                cursor.execute(query)
        else:
            if argument:
                cursor.execute(query, argument)
            else:
                cursor.execute(query)

    @staticmethod
    def __fetch(cursor, clean):
        """

        :param cursor:
        :param clean:
        :return:
        """
        if clean is None:
            fetch = cursor.fetchone()
        else:
            fetch = cursor.fetchone()[0]

        return fetch

    @staticmethod
    def __error(error):
        """

        :param error:
        :return:
        """
        print(error)


db =DB_Postgres(db_name, db_user, db_password, db_host, db_port)
