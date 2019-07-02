import sqlite3
from Page import *
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import time
import random

DB = "wikipedia.sqlite3"
DELIMITER = ", "

def _create_table_(tablename):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE {0} (
        id integer PRIMARY KEY,
        name text NOT NULL,
        url text NOT NULL UNIQUE,
        children text
    )""".format(tablename))
    conn.commit()
    conn.close()

def update_cids():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM pages")
    all_rows = c.fetchall()
    for row in all_rows:
        pk = row[0]
        print(pk, row[2])
        children = row[3].split(DELIMITER)
        if row[4]:
            print("Skipping")
            continue
        childrenIds = []
        for child_url in children:
            c.execute("SELECT id FROM pages WHERE url = ?", (child_url,))
            child_row = c.fetchone()
            if child_row:
                childrenIds.append(child_row[0])
        childrenIds = [str(i) for i in sorted(childrenIds)]
        childrenIds = DELIMITER.join(childrenIds)
        c.execute("UPDATE pages SET childrenIds = ? WHERE id = ?", (childrenIds, pk))
        conn.commit()
    conn.close()

def add_row(url):
    """Given a url, write it to a new row"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(f"SELECT * FROM pages WHERE url = ?", (url,))
    if c.fetchall() or not url.startswith("http"):
        conn.commit()
        conn.close()
        return None
    page = Page(url)
    children = DELIMITER.join(page.find_child_urls())
    if not children:
        return None
    print(f"Adding new row for '{page.name}' {url}")
    name, url = page.name, page.url
    c.execute(f"INSERT INTO pages (name, url, children) VALUES (?, ?, ?)", (name, url, children))
    conn.commit()
    conn.close()
    return url

def get_children_from_row(url):
    """Get some children from a url"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(f"SELECT * FROM pages WHERE url = ?", (url,))
    fetch = c.fetchall()
    if fetch:
        children = fetch[0][3].split(DELIMITER)
    else:
        children = None
    conn.commit()
    conn.close()
    return children

def populate(start_url):
    #BFS
    count = 0
    procs = 8
    benchmarks = []
    pool = ThreadPool(processes=procs)
    print(f"Populating for: {start_url}")
    while add_row(start_url) is None: #DFS TO FIND UNTOUCHED NODE
        start_url = get_children_from_row(start_url)[random.randint(0, 5)] #Grab a random child
        print(f"Looking for untouched {start_url}")
    q = [start_url]
    while q:
        curr = q.pop(0)
        children = get_children_from_row(curr)
        start_time = time.time()
        mapped = pool.map(add_row, children) #For each child, write to db
        end_time = time.time() - start_time
        benchmarks.append(end_time)
        count += 1
        if count % 10 == 0:
            avg = sum(benchmarks) / len(benchmarks)
            print(f"Average speed for {procs} processes: {avg}")
            #input()
        if mapped:
            for child in mapped:
                if child is not None: #This method populates with all children
                    q.append(child)
        else:
            print(f"Map failed for {curr}")

#SOme duplicate URLS, but that's okay. The duplicates shouldn't mess up the whole thing too badly.
#delete main_page row
