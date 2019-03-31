import orm

orm.Database.connection()

class Users(orm.Model):
    id = orm.IntField(required=True)
    name = orm.StringField(length=22, default='no_name', required=False)
    age = orm.IntField(required=False, default=20)

    class Meta:
        table_name = 'Users_for_orm'

# Тестим создание таблицы/обработку ошибки "таблица уже существует"
# Users.create_table()

# class Us(orm.Model):
#     id = orm.IntField(required=True)
#
#     class Meta:
#         table_name = 'Us'

# Тестим обработку ошибки "неизвестная таблица"
# Us.drop_table()

# Users.objects.desc_table()
# Users.objects.create(id=3, name='Sergey', age=20)
# Users.objects.delete(id=2)

# Users.objects.update({"name": "Kochka", "age": 21}, {"id": 3})
print("SELECT ALL:")
Users.objects.select()
print("SELECT ID, NAME:")
Users.objects.select("id", "name")