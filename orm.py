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
        if not isinstance(f_type, (type(int), type(str))):
            raise ValueError("Неизвестный тип {f_type}, используйте: int, str".format(f_type=f_type))
        if not isinstance(required, bool):
            raise ValueError("Неверный ввод required, используйте bool: True/False")
        if not isinstance(default, (f_type, type(None))):
            raise ValueError("Неверный ввод default, используйте {f_type}".format(f_type=f_type))
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
        if not isinstance(length, int):
            raise ValueError("Неверный ввод length, используйте: int")
        self.length = length
        self.sql_format = self.make_sql_field()

    def make_sql_field(self):
        sql_format = "VARCHAR({length})".format(length=self.length)
        if self.default != None:
            sql_format = sql_format + " DEFAULT " + "'{d}'".format(d=self.default)
        if self.required:
            sql_format += " NOT NULL"
        return sql_format


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
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
            self.fields = owner._fields
            self.table_name = owner._table_name
        return self

    def validate_input(self, create, kwargs):
        for key, value in kwargs:
            if key not in self.fields:
                raise ValueError("Несуществующие поля таблицы")
            else:
                for field, settings in self.fields.items():
                    if field == key:
                        s = settings
                if not isinstance(value, s.f_type):
                    raise ValueError("Неверно указано значение {key}".format(key=key))
        if create:
            for field_key, field in self.fields.items():
                if field.required and (field_key not in kwargs):
                    raise ValueError('Указаны не все обязательные поля')

    def desc_table(self):
        cursor = Database.cursor
        cursor.execute("DESC {table_name}".format(table_name=self.table_name))
        for row in cursor:
            print(row)

    def create(self, **kwargs):
        self.validate_input(True, kwargs.items())
        cursor = Database.cursor
        db = Database.db
        dict_values = list(kwargs.values())
        for i, item in enumerate(dict_values):
            if isinstance(item, str):
                dict_values[i] = "'"+item+"'"
            else:
                dict_values[i] = str(item)
        cursor.execute("INSERT INTO {table_name} ({fields_names}) VALUES ({fields_values})".format(
            table_name=self.table_name,
            fields_names=', '.join(kwargs.keys()),
            fields_values=', '.join(dict_values)
        ))
        db.commit()

    def update(self, dict_set, dict_where):
        self.validate_input(False, dict_set.items())
        self.validate_input(False, dict_where.items())
        cursor = Database.cursor
        db = Database.db
        update_fields = self.to_do_dict(dict_set)
        control_fields = self.to_do_dict(dict_where)
        cursor.execute("UPDATE {table_name} SET {update_fields} WHERE {control_fields}".format(
            table_name=self.table_name,
            update_fields=update_fields,
            control_fields=control_fields
        ))
        db.commit()

    def to_do_dict(self, dict):
        update_fields = ""
        i = 0
        for key, value in dict.items():
            i += 1
            if isinstance(value, str):
                value = "'" + value + "'"
            update_fields = update_fields + key + " = " + str(value)
            if i != len(dict):
                update_fields += ", "
        return update_fields

    def delete(self, **kwargs):
        self.validate_input(False, kwargs.items())
        cursor = Database.cursor
        db = Database.db
        i = 0
        query = "DELETE FROM {table_name} WHERE ".format(table_name=self.table_name)
        for key, value in kwargs.items():
            i += 1
            if (type(value) == str):
                value = "'" + value + "'"
            if (i == 1):
                query += "{} = {} ". format(key, value)
            else:
                query += "AND {} = {} ". format(key, value)
        cursor.execute(query)
        db.commit()

    def select(self, *args):
        cursor = Database.cursor
        db = Database.db
        if len(args) == 0:
            cursor.execute('SELECT * FROM {table_name}'.format(table_name=self.table_name))
            for row in cursor:
                print(row)
        else:
            select_fields = ""
            i = 0
            for key in args:
                i += 1
                if key not in self.fields:
                    raise ValueError("Несуществующие поля таблицы")
                else:
                    select_fields += key
                    if i != len(args):
                        select_fields += ", "
            cursor.execute('SELECT {select_fields} FROM {table_name}'.format(
                select_fields=select_fields,
                table_name=self.table_name
            ))
            for row in cursor:
                print(row)

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

