import numpy as np
import os
import time
import winsound as ws
from datetime import datetime
import random
import requests
import playsound
import pickle
import sqlite3 as sq

def create_conn(filename):
    conn = None
    try:
        conn = sq.connect(filename)
    except sq.Error as e:
        print(e)
        if(conn):
            conn.close()
        exit()
    return conn

def compar(e):
    return -e[2]

class Color:
    def __init__(self):
        self.RED = "\x1b[31m"
        self.GREEN = "\x1b[1;32m"
        self.YELLOW = "\x1b[1;33m"
        self.ORANGE = "\x1b[1;91m"
        self.BLUE = "\x1b[1;34m"
        self.MAGENTA = "\x1b[1;35m"
        self.CYAN = "\x1b[1;36m"
        self.DBLACK = "\x1b[0;90m"
        self.RESET = "\x1b[0m"

### DB INIT ###
conn = create_conn("seky.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS SEKY(
ID integer PRIMARY KEY AUTOINCREMENT,
TIMESTAMP text NOT NULL,
YANG integer NOT NULL CHECK(YANG >= 0),
SD integer NOT NULL CHECK(SD > 0),
POPIS text);""")
conn.close()

color = Color()
highlight = "Top kek"
while True:
    #############
    # PULL DATA #
    #############
    #ids = ["d1ogg3uqg10geumm6c4h091bd2", "rl9t4om8tr5h34hqe3rv40nud3",
    #        "m3ori7ec6i6su4n53nh4j9ml0c"]
    ids = ["b3lhq367d91frucstdqc2hmpuj", "6mpqghre35p1lmsov4c9cbn7en", "vvstq1h7ee0gsu9minhjl07pdv"]
    cookies = {"PHPSESSID":random.choice(ids), "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    r = requests.get("https://ekura.cz/black_market/sindicate", cookies=cookies)
    r.encoding = "cp1250"
    s = r.text
    start = s.find("black_data = [")
    end = s.find("];</script>") + 1
    exec(s[start:end])

    ##################
    # WORK WITH DATA #
    ##################
    data = np.array(black_data, dtype=np.str)
    ids = data[:, 2] == 'Šek'
    pocet_seku = np.sum(ids)
    seky = data[ids]
    seky = seky.T
    
    yangy = [int(x) for x in seky[30]]
    sdcka = [int(x) for x in seky[45]]
    popisky = [x for x in seky[-2]]
    pomer = [yangy[i]/sdcka[i] for i in range(len(sdcka))]
    dohromady = list(zip(yangy, sdcka, pomer, popisky))
    srted = sorted(dohromady, key=compar)


    os.system("cls")
    now = datetime.now()
    cur = now.strftime("%H:%M")
    #ws.Beep(1000, 100)
    #ws.Beep(1000, 200)
    print("--------------------%s--------------------------------" % cur)
    print(" YANG [kk]  SD  |  cena 1 SD | cena 1kkk (v SD) | Popisek")
    print("---------------------------------------------------------")
    rst = False
    counter = 0
    for e in srted:
        """if e[2] < 3.8:
            print("... a dalsi ... dohromady %d seku" % pocet_seku)
            break"""
        if counter >= 62:
            print("... a dalsi ... dohromady %d seku" % pocet_seku)
            break
        counter += 1
        if highlight in e[3]:
            print(color.MAGENTA, end="")
            rst = True
        elif 1000/e[2] <= 210:
            print(color.GREEN, end="")
            rst = True
        elif 1000/e[2] <= 225:
            print(color.YELLOW, end="")
            rst = True
        elif 1000/e[2] <= 240:
            print(color.ORANGE, end="")
            rst = True
        elif 1000/e[2] <= 250:
            print(color.RED, end="")
            rst = True
        elif 1000/e[2] > 250:
            print(color.DBLACK, end="")
            rst = True
            
        print("%5dkk %4d SD | %02.2f kk/SD | %04.2f SD / 1kkk | %s" % (e[0], e[1], round(e[2], 2), -10 if e[2] == 0 else round(1000/e[2], 2), e[3]))
        if rst:
            print(color.RESET, end="")
            rst = False
    playsound.playsound("D:\\Dokumenty\\Programming\\Python\\Ekura\\necum.wav")
    ## DB ##
    conn = create_conn("seky.db")
    cursor = conn.cursor()
    tosave = list(zip(yangy, sdcka, popisky))
    query = """INSERT INTO SEKY (TIMESTAMP, YANG, SD, POPIS) VALUES (datetime('now', '+2 hours'), ?, ?, ?)"""
    try:
        cursor.executemany(query, tosave)
        conn.commit()
    except sq.Error as e:
        print(e)
        conn.rollback()
    conn.close()
    time.sleep(800 + random.randint(-121, 121))
    os.system("cls")
    print("Fetching new...")
