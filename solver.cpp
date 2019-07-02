#include <iostream>
#include <cstring>
#include <sqlite3.h> 
#include <unordered_map>
#include <deque>

using namespace std;

class Node {
    public:
        char *url;
        Node *parent;
    
    void show() {
        cout << url;
    }

    Node(char *u, Node *p) {
        url = u;
        parent = p;
    }
};

char* find_children(sqlite3 *db, char const* name) {
    sqlite3_stmt *stmt;
    int rc;

    char const *sql = "SELECT children FROM pages WHERE url = ?";

    rc = sqlite3_prepare_v2(db, sql, strlen(sql), &stmt, NULL);
    if (rc != SQLITE_OK) {
        return NULL;
    }
    rc = sqlite3_bind_text(stmt, 1, name, strlen(name), 0);
    if (rc != SQLITE_OK) {
        sqlite3_finalize(stmt);
        return NULL;
    }
    sqlite3_step(stmt);
    char *col = (char*) sqlite3_column_text(stmt, 0);
    if (col == NULL) {
        return NULL;
    }
    char *result = (char*) malloc(sizeof(char) * strlen(col));
    sprintf(result, "%s", col);
    sqlite3_finalize(stmt);
    return result;
}

char* name_to_url(sqlite3 *db, char const* name) {
    sqlite3_stmt *stmt;
    int rc;

    char const *sql = "SELECT url FROM pages WHERE name = ?";

    rc = sqlite3_prepare_v2(db, sql, strlen(sql), &stmt, NULL);
    if (rc != SQLITE_OK) {
        return NULL;
    }
    rc = sqlite3_bind_text(stmt, 1, name, strlen(name), 0);
    if (rc != SQLITE_OK) {
        sqlite3_finalize(stmt);
        return NULL;
    }
    sqlite3_step(stmt);
    char *col = (char*) sqlite3_column_text(stmt, 0);
    if (col == NULL) {
        return NULL;
    }
    char *result = (char*) malloc(sizeof(char) * strlen(col));
    sprintf(result, "%s", col);
    sqlite3_finalize(stmt);
    return result;
}

int main(int argc, char* argv[]) {
    sqlite3 *db;
    char *zErrMsg = 0;
    int rc;

    rc = sqlite3_open("wikipedia.backup.sqlite3", &db);

    if (rc) {
        cout << "Can't open database: " << sqlite3_errmsg(db) << "\n";
        return 0;
    } else {
        cout << "Opened database successfully.\n";
    }

    char* start_url = name_to_url(db, "Buddhism");
    char* target_url =  name_to_url(db, "Adolf Hitler");

    deque<Node*> queue;
    queue.push_back(new Node(start_url, NULL));

    unordered_map<string, int> seen;

    Node* node;

    while (queue.size() > 0) {
        node = *(queue.begin());
        queue.pop_front();
        seen[string(node->url)] = 1;
        char const* children_str = find_children(db, node->url);
        if (children_str != NULL) {
            int length = strlen(children_str);
            char* buff = (char*) malloc(sizeof(char) * 300);
            int index = 0;
            char* buffcpy;
            for (int i = 0; i < length; i++) {
                if ((i == length-1) || (children_str[i] == ',' && children_str[i+1] == ' ')) {
                    buff[index] = '\0';
                    if (seen.find(string(buff)) == seen.end()) {
                        cout << buff << "\n";
                        buffcpy = (char*) malloc(sizeof(char) * index);
                        strcpy(buffcpy, buff);
                        queue.push_back(new Node(buffcpy, node));
                    }
                    index = 0;
                    i += 2;
                } else {
                    buff[index] = children_str[i];
                }
                index += 1;
            }
            free(buff);
            delete(children_str);
        }
        //Free node once popped
        free(node->url);
        delete(node);
    }

    sqlite3_close(db);
    return 0;
}