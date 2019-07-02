#Game categories:
#Number of clicks to Jesus, or Hitler
#Random page to random page
#Generally, find the shortest path from A->B
from collections import namedtuple
import heapq
import time
from populate import DB, DELIMITER, sqlite3
#ID, NAME, URL, CHILDREN

def search_bfs(start, end, loud=True):
    """Returns a list of path from start to end"""
    Node = namedtuple("Node", ['url', 'parent']) #This is much more performant than a class
    if loud:
        def log(*args):
            print(*args)
    else:
        def log(*args):
            return
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(f"SELECT * FROM pages WHERE url = ? OR name = ?", (start, start))
    fetch = c.fetchall()
    if not fetch:
        log(f"Start {start} not found in DB")
        return []
    start_url = fetch[0][2]
    c.execute(f"SELECT * FROM pages WHERE url = ? OR name = ?", (end, end))
    fetch = c.fetchall()
    if not fetch:
        log(f"Target {end} not found in DB")
        return []
    end_url = fetch[0][2]

    if start_url == end_url:
        conn.commit()
        conn.close()
        return [start_url]
    log(f"Searching for {start_url} -> {end_url}")
    #Run BFS
    result = []
    queue = []
    queue.append(Node(start_url, None))
    touched = {}
    num_links_cutoff = 40
    while queue:
        curr_node = queue.pop(0)
        curr_url = curr_node.url
        log(f"Searching {curr_url}")
        touched[curr_url] = True
        c.execute(f"SELECT * FROM pages WHERE url = ?", (curr_url,))
        fetch = c.fetchall()
        if fetch:
            children = fetch[0][3].split(DELIMITER)
            if len(children) > num_links_cutoff:
                for child_url in children:
                    log(f"Touched {child_url}")
                    node = Node(child_url, curr_node)
                    if child_url == end_url:
                        log(f"Found {end_url}")
                        while node:
                            page_name = c.execute(f"SELECT * FROM pages WHERE url = ?", (node.url,)).fetchone()
                            if page_name:
                                page_name = page_name[1]
                            else:
                                page_name = ""
                            result.insert(0, (page_name, node.url))
                            node = node.parent
                        conn.commit()
                        conn.close()
                        return result
                    if touched.get(child_url, None) is None:
                        queue.append(node)
            else:
                log(f"Pruned {curr_url}")
    conn.commit()
    conn.close()
    return result

def pretty_search(s, e, method="bfs"):
    start_time = time.time()
    if method == "bfs":
        path = [name for name, url in search_bfs(s, e, False)]
    elapsed = time.time() - start_time
    if not path:
        message = f"No path found from {s} to {e}"
    else:
        message = " -> ".join(path)
    return path, message, elapsed
