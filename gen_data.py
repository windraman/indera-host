import sqlite3
import json
import os

app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
conn.row_factory = sqlite3.Row
db = conn.cursor()
rows = db.execute('''SELECT * from moduls''').fetchone()
conn.commit()

gengrup = db.execute('''INSERT INTO grups(name,slug,moduls_id) VALUES ("LED grup","''' + rows['slug'] + '''_led_grup","''' + str(rows['id']) + '''")''')
conn.commit()

grup = db.execute('''SELECT * from grups ORDER BY id DESC LIMIT 1''').fetchone()

gensensor = db.execute('''INSERT INTO sensors(name,slug,pin,grups_id) VALUES ("LED 16","'''+ str(grup['slug']) + '''_led_grup_led_16","16","''' + str(grup['id']) + '''")''')
conn.commit()
gensensor = db.execute('''INSERT INTO sensors(name,slug,pin,grups_id) VALUES ("LED 20","'''+ str(grup['slug']) + '''led_grup_led_20","20","''' + str(grup['id']) + '''")''')
conn.commit()
gensensor = db.execute('''INSERT INTO sensors(name,slug,pin,grups_id) VALUES ("LED 21","'''+ str(grup['slug']) + '''led_grup_led_21","21","''' + str(grup['id']) + '''")''')
conn.commit()

gengrup = db.execute('''INSERT INTO grups(name,slug,moduls_id) VALUES ("Button grup","''' + str(rows['slug']) + '''_button_grup","''' + str(rows['id']) + '''")''')
conn.commit()

grup = db.execute('''SELECT * from grups ORDER BY id DESC LIMIT 1''').fetchone()
conn.commit()
gensensor = db.execute('''INSERT INTO sensors(name,slug,pin,grups_id) VALUES ("Button 5","'''+ str(grup['slug']) + '''button_grup_button_5","5","''' + str(grup['id']) + '''")''')
conn.commit()
gensensor = db.execute('''INSERT INTO sensors(name,slug,pin,grups_id) VALUES ("Button 6","'''+ str(grup['slug']) + '''button_grup_button_6","6","''' + str(grup['id']) + '''")''')
conn.commit()

conn.close()

