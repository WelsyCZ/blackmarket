import numpy as np
import os
import time
from datetime import datetime
import random
import requests
import pickle
import sqlite3 as sq
import sys

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
sekLimit = 62
if (len(sys.argv) > 1):
    sekLimit = int(sys.argv[1])
    sekLimit = 99999 if sekLimit == 0 else sekLimit
while True:
    #############
    # PULL DATA #
    #############
    ids = ["64qmfknp4sakg7m9akohrgorc7"]
    cookies = {"PHPSESSID":random.choice(ids)}
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"}
    r = requests.get("https://ekura.cz/black_market/sindicate", cookies=cookies, headers=headers)
    r.encoding = "cp1250"
    s = r.text
    start = s.find("black_data = [")
    end = s.find("];</script>") + 1
    #print(s[start:end])
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
    print("  # | YANG [kk]  SD  |  cena 1kkk (v SD)  |  cena 1 SD  | Součet kk | Součet SD | Popisek ")
    print("---------------------------------------------------------")
    rst = False
    counter = 0
    total = 0
    totalSD = 0
    for e in srted:
        if counter >= sekLimit:
            print("... a dalsi ... dohromady %d seku" % pocet_seku)
            break
        
        counter += 1
        total += e[0]
        totalSD += e[1]
        ratio = 100000 if e[2] == 0 else 1000/e[2]
        if highlight in e[3]:
            print(color.MAGENTA, end="")
            rst = True
        elif ratio < 210:
            print(color.GREEN, end="")
            rst = True
        elif ratio < 225:
            print(color.YELLOW, end="")
            rst = True
        elif ratio < 240:
            print(color.ORANGE, end="")
            rst = True
        elif ratio < 250:
            print(color.RED, end="")
            rst = True
        elif ratio >= 250:
            print(color.DBLACK, end="")
            rst = True
            
        print("%3d | %5dkk %4d SD | %04.2f SD / 1kkk | %02.2f kk / 1SD | %6dkk | %5d SD | %s" % \
            (counter, e[0], e[1], -10 if e[2] == 0 else round(ratio, 2), \
                "prazdny" if e[0] == 0 else round(e[0]/e[1],2), total, totalSD, e[3]))
        if rst:
            print(color.RESET, end="")
            rst = False
    #playsound.playsound("D:\\Dokumenty\\Programming\\Python\\Ekura\\necum.wav")
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
