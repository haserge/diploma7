import psycopg2, os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

name_table = "weather_table"


# connect to PostgreSQL DB
def db_connect():
    connection = psycopg2.connect(
       database = os.environ["DATABASE_NAME"],
       user = os.environ["DATABASE_USER"],
       password = os.environ["USER_PASSWORD"],
       host = os.environ["DATABASE_HOST"],
       port = "5432"
    )
    return connection


def create_con_cur():
    con = db_connect()
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    return cur


cursor = create_con_cur()
# create table statement
sql_create_table = "create table if not exists " + name_table + \
                   " (id bigint not null primary key, weather_state_name varchar(15), wind_direction_compass varchar(5), " \
                   "created varchar(27), applicable_date date, min_temp float, max_temp float, the_temp float);"
# create a table in PostgreSQL database
cursor.execute(sql_create_table)
# uncomment the following lines to add new columns
# sql_alter_table = "alter table " + name_table + " add column if not exists new_col1 float, add column if not exists new_col2 float;"
# cursor.execute(sql_alter_table)
cursor.close()
print("Table " + name_table + " is ready!")
