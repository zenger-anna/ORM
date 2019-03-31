import orm

orm.Database.connection()

class Users(orm.Model):
    id = orm.IntField(required=True)
    name = orm.StringField(length=22, default='no_name', required=False)
    age = orm.IntField(required=False, default=20)

    class Meta:
        table_name = 'Users_for_orm'

# Тестим создание таблицы/обработку ошибки "таблица уже существует"
Users.create_table()

class Us(orm.Model):
    id = orm.IntField(required=True)

    class Meta:
        table_name = 'Us'

# Тестим обработку ошибки "неизвестная таблица"
Us.drop_table()


# user = User(id=3, name='fro', user_name='wefwerqw')
# user.create()
# # User.objects.create(id=1, name='name')
# # User.objects.update(id=1)
# User.delete(id=3, name='fro')
#
# User.objects.filter(id=2).filter(name='petya')
#
# user.name = '2'
# user.update()
# user.delete()