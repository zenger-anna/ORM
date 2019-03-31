import mysql.connector as mysql


class Database:
    db = None
    cursor = None

    @classmethod
    def connection(cls, host="localhost", user="azenger", password="syncmaster3641", database="db_for_orm"):
        try:
            cls.db = mysql.connect(
                host=host,
                user=user,
                passwd=password,
                database=database
            )
            cls.cursor = cls.db.cursor()
        except:
            print('----------!!!!!!!!!!!!----------\n'
                  'ОШИБКА ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ')


# ДОДЕЛАТЬ
class Field:
    def __init__(self, f_type, required=True, default=None):
        self.f_type = f_type
        self.required = required
        self.default = default

    def validate(self, value):
        if value is None and not self.required:
            return None
        # todo exceptions
        return self.f_type(value)


class IntField(Field):
    def __init__(self, required=True, default=None):
        super().__init__(int, required, default)
        self.sql_format = self.make_sql_field()

    def make_sql_field(self):
        sql_format = "INT"
        if self.default != None:
            sql_format = sql_format + " DEFAULT " + str(self.default)
        if self.required:
            sql_format += " NOT NULL"
        return sql_format



class StringField(Field):
    def __init__(self, required=True, length: int=None, default=None):
        super().__init__(str, required, default)
        self.length = length
        self.sql_format = self.make_sql_field()

    def make_sql_field(self):
        sql_format = "VARCHAR({length})".format(length=self.length)
        if self.default != None:
            sql_format = sql_format + " DEFAULT " + "'{d}'".format(d=self.default)
        if self.required:
            sql_format += " NOT NULL"
        return sql_format



# ДОДЕЛАТЬ
class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')
        if not hasattr(meta, 'table_name'):
            raise ValueError('table_name is empty')

        # todo mro - нужно, чтобы собрать поля со всех классов-родителей при наследовании

        fields = {k: v for k, v in namespace.items()
                  if isinstance(v, Field)}
        namespace['_fields'] = fields
        namespace['_table_name'] = meta.table_name
        return super().__new__(mcs, name, bases, namespace)


class Manage:
    cursor = Database.cursor
    db = Database.db
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
        return self

    @classmethod
    def create(cls, id, name, user_name):
        query = "INSERT INTO users (id, name, user_name) VALUES (%s, %s, %s)"
        values = (id, name, user_name)
        cls.cursor.execute(query, values)
        cls.db.commit()

    @classmethod
    def update(cls):
        query = "UPDATE users SET name = 'Kareem' WHERE id = 1"

        ## executing the query
        cls.cursor.execute(query)

        ## final step to tell the database that we have changed the table data
        cls.db.commit()

    @classmethod
    def delete(cls, **kwargs):
        i = 0
        query = "DELETE FROM users WHERE "
        for key, value in kwargs.items():
            i += 1
            if (type(value) == str):
                value = "'" + value + "'"
            if (i == 1):
                query += "{} = {} ". format(key, value)
            else:
                query += "AND {} = {} ". format(key, value)
        print(query)
        cls.cursor.execute(query)
        cls.db.commit()


class Model(metaclass=ModelMeta):
    class Meta:
        table_name = ''

    objects = Manage()
    # todo DoesNotExist

    @classmethod
    def create_table(cls):
        cursor = Database.cursor
        try:
            cursor.execute("CREATE TABLE {table_name} ({fields})".format(
                table_name=cls._table_name,
                fields=Model.make_fields_sql(cls._fields)
            ))
            print("Таблица {table_name} успешно создана".format(table_name=cls._table_name))
        except mysql.errors.ProgrammingError:
            print("-------!!!!!!!-------\n"
                  "Таблица {table_name} уже существует".format(table_name=cls._table_name))

    @classmethod
    def drop_table(cls):
        try:
            cursor = Database.cursor
            cursor.execute('DROP TABLE {table_name}'.format(table_name=cls._table_name))
            print("Таблица {table_name} цспешно удалена".format(table_name=cls._table_name))
        except mysql.errors.ProgrammingError:
            print("-------!!!!!!!-------\n"
                  "Неизвестная таблица {table_name}".format(table_name=cls._table_name))

    @staticmethod
    def make_fields_sql(fields):
        sql_fields_to_create = ""
        i = 0
        for name, settings in fields.items():
            i += 1
            sql_fields_to_create = sql_fields_to_create + name + " " + settings.sql_format
            if i != len(fields.items()):
                sql_fields_to_create += ", "
        return sql_fields_to_create

