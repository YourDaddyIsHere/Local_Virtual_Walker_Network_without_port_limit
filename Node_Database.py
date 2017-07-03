import sys
import os
BASE = os.path.dirname(os.path.abspath(__file__))
if sys.platform == "darwin":
    # Workaround for annoying MacOS Sierra bug: https://bugs.python.org/issue27126
    # As fix, we are using pysqlite2 so we can supply our own version of sqlite3.
    import pysqlite2.dbapi2 as sqlite3
else:
    import sqlite3

class Node(object):
    def __init__(self,database_record=None):
        if database_record:
            self.id = database_record[0]
            self.honest = database_record[1]
            self.public_key = str(database_record[2])
            self.private_key = str(database_record[3])
            self.member_identity = str(database_record[4])
            self.ip = str(database_record[5])
            self.port = str(database_record[6])
        else:
            self.id = None
            self.honest = None
            self.public_key = None
            self.private_key = None
            self.member_identity = None
            self.ip = "0.0.0.0"
            self.port=0

    def pack_db_insert(self):
        return(self.honest,buffer(self.public_key),buffer(self.private_key),buffer(self.member_identity),buffer(self.ip),self.port)

    def set(self,id=None,honest=None,public_key=None,private_key=None,member_identity=None,ip="0.0.0.0",port=0):
        self.honest = honest
        self.public_key = public_key
        self.private_key = private_key
        self.member_identity = member_identity
        self.ip = ip
        self.port=port


class NodeDatabase(object):
    def __init__(self,database_name=os.path.join(BASE, 'NodeDatabase.db')):
        if os.path.isfile(database_name):
            os.remove(database_name)
        self.conn = sqlite3.connect(database_name)
        cursor = self.conn.cursor()
        create_node_table = u"""
                CREATE TABLE IF NOT EXISTS node(
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                honest                 INTEGER NOT NULL,
                public_key           TEXT NOT NULL,
                private_key      TEXT NOT NULL,
                member_identity          TEXT NOT NULL,
                ip                       TEXT,
                port                     INTEGER,
                insert_time          TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                CONSTRAINT name_unique UNIQUE (public_key)
                );

                """
        cursor.execute(create_node_table)
        self.conn.commit()

    def add_node(self,node):
        cursor = self.conn.cursor()
        insert_script = """
                        INSERT INTO node(honest,public_key,private_key,member_identity,ip,port) VALUES(?,?,?,?,?,?)
                        """
        cursor.execute(insert_script,node.pack_db_insert())
        self.conn.commit()

    def add_nodes(self,nodes):
        cursor = self.conn.cursor()
        insert_script = """
                        INSERT INTO node(honest,public_key,private_key,member_identity,ip,port) VALUES(?,?,?,?,?,?)
                        """
        for node in nodes:
            cursor.execute(insert_script,node.pack_db_insert())
        self.conn.commit()

    def get_node_between(self,start_index,end_index):
        cursor = self.conn.cursor()
        query_script = """
                        SELECT * from node  WHERE id>=? and id<=?
                        """
        cursor.execute(query_script,(start_index,end_index))
        self.conn.commit()
        records = cursor.fetchall()
        nodes=[]
        for record in records:
            node = Node(database_record = record)
            nodes.append(node)
        return nodes

    def get_node_by_id(self,id):
        cursor = self.conn.cursor()
        query_script = """
                        SELECT * from node  WHERE id=?
                        """
        cursor.execute(query_script,(id,))
        self.conn.commit()
        record = cursor.fetchone()
        node = Node(database_record=record)
        return node

    def get_node_by_public_key(self,public_key):
        cursor = self.conn.cursor()
        query_script = """
                        SELECT * from node  WHERE public_key=?
                        """
        cursor.execute(query_script,(buffer(public_key),))
        self.conn.commit()
        record = cursor.fetchone()
        node = Node(database_record=record)
        return node

    def get_node_by_ip_and_port(self,ip,port):
        query_script = """
                        SELECT * from node  WHERE ip=? AND port=?
                        """
        cursor = self.conn.cursor()
        cursor.execute(query_script,(buffer(ip),int(port)))
        self.conn.commit()
        record = cursor.fetchone()
        node = Node(database_record=record)
        return node
    def set_ip_and_port_by_public_key(self,ip,port,public_key):
        cursor = self.conn.cursor()
        query_script = """
                        UPDATE node SET ip=?,port=? WHERE public_key=?
                        """
        cursor.execute(query_script,(buffer(ip),port,buffer(public_key)))
        #self.conn.commit()

    def set_ip_and_port_by_id(self,ip,port,id):
        cursor = self.conn.cursor()
        query_script = """
                        UPDATE node SET ip=?,port=? WHERE id=?
                        """
        cursor.execute(query_script,(buffer(ip),port,id))
        #self.conn.commit()

    def get_honest_nodes(self,number):
        pass
    def get_evil_nodes(self,number):
        pass

    def close(self):
        self.conn.close()
    def commit(self):
        self.conn.commit()







if __name__ == "__main__":
    database = NodeDatabase()