import os
import sys
import numpy as np
import sqlite3
import json
import pandas as pd
import time


def create_database():
    with open("./config/col_path_mapping.json") as f:
        col_path_mapping = json.load(f)
    jsonfiles = {}
    for item in col_path_mapping.items():
        col = item[0]
        pathlist = item[1]
        jsonfile = pathlist[0]
        if jsonfiles.get(jsonfile) is None:
            jsonfiles[jsonfile] = []
        jsonfiles[jsonfile].append(col)

    conn = sqlite3.connect('./database/test.db')
    print("Opened database successfully")
    c = conn.cursor()

    # create tables of json files
    varcharlist = ["data_source", "celltype", "brain_atlas", "recon_method"]
    for jsonfile, colnames in jsonfiles.items():
        if jsonfile == "info.json":
            colstring = "ID VARCHAR(45) PRIMARY KEY,\n"
        else:
            colstring = "ID VARCHAR(45),\n"

        for col in colnames:
            if col.startswith("has"):
                datatype = "INT2(1)"
            elif col in varcharlist:
                datatype = "VARCHAR"
            else:
                datatype = "FLOAT"
            colstring += "'{}' {},\n".format(col, datatype)
        colstring = colstring.rstrip(",\n")
        if jsonfile == "info.json":
            SQL = '''
            CREATE TABLE {0}
            (
                {1}
            );
            '''.format(jsonfile[:-5], colstring)
        else:
            SQL = '''
            CREATE TABLE {0}
            (
                {1},
                FOREIGN KEY (ID) references info (ID)
            );
            '''.format(jsonfile[:-5], colstring)
        c.execute('''DROP TABLE IF EXISTS {}'''.format(jsonfile[:-5]))
        c.execute(SQL)
        if jsonfile == "info.json":
            c.execute('''CREATE UNIQUE INDEX ID_index on {} (ID);'''.format(jsonfile[:-5]))
        print(jsonfile[:-5] + " table created successfully")
    # create table of img_src
    Imglist = ['Img_Brain_Full_YZ.png', 'Img_Brain_Full_XZ.png', 'Img_Brain_Full_XY.png', 'Img_Full_YZ.png',
               'Img_Full_XZ.png', 'Img_Full_XY.png', 'Img_Dendrite_YZ.png', 'Img_Dendrite_XZ.png',
               'Img_Dendrite_XY.png', 'Img_Axon_YZ.png', 'Img_Axon_XZ.png', 'Img_Axon_XY.png']
    colstring = "ID VARCHAR(45) PRIMARY KEY,\n"
    for s in Imglist:
        colstring += "'{0}' INT2(1),\n".format(s)
    colstring = colstring.rstrip(",\n")
    SQL = '''
    CREATE TABLE img_src
    (
        {0}
    );
    '''.format(colstring)
    c.execute('''DROP TABLE IF EXISTS img_src''')
    c.execute(SQL)
    print("img_src" + " table created successfully")

    conn.commit()

    # populate partial json values from 'Web_Data' folder
    path = r"/Neuron_Morphology_Table/Web_Data"
    folders = os.listdir(path)
    for i, folder in enumerate(folders):
        ID = folder
        print(i)
        fpath = os.path.join(path, folder)
        jsonmap = {}
        # populate ID col of json tables
        for jsonname in jsonfiles.keys():
            SQL = '''
                INSERT INTO {0} ('ID') VALUES ('{1}');
            '''.format(jsonname[:-5], ID)
            c.execute(SQL)

            jsonpath = os.path.join(fpath, jsonname)
            if os.path.exists(jsonpath):
                with open(jsonpath) as f:
                    jsonmap[jsonname] = json.load(f)
            else:
                jsonmap[jsonname] = None
        # populate all cols of img_src table
        popvalue = "'{0}',".format(ID)
        for s in Imglist:
            if os.path.exists(os.path.join(fpath, s)):
                popvalue += "1,"
            else:
                popvalue += "0,"
        SQL = '''
            INSERT INTO img_src VALUES ({0});
        '''.format(popvalue[:-1])
        c.execute(SQL)

        # UPDATE other elements of json tables
        passjsonname = []
        for querryname, pathlist in col_path_mapping.items():
            jsonname = pathlist[0]
            if jsonmap.get(jsonname) is None:
                if jsonname not in passjsonname:
                    c.execute('''DELETE FROM {0} WHERE ID = '{1}';'''.format(jsonname[:-5], ID))
                    passjsonname.append(jsonname)
                continue

            tree = pathlist[1:]
            tempjson = jsonmap[jsonname]
            for t in tree:
                tempjson = tempjson.get(t)
                if tempjson is None:
                    break
            if tempjson is None:
                continue
            sqlvalues = tempjson
            if querryname in varcharlist:
                SQL = '''
                    UPDATE {0} SET '{1}' = '{2}' WHERE ID = '{3}';
                '''.format(jsonname[:-5], querryname, sqlvalues, ID)
            elif querryname.startswith("has"):
                SQL = '''
                    UPDATE {0} SET '{1}' = {2} WHERE ID = '{3}';
                '''.format(jsonname[:-5], querryname, 1 if sqlvalues >= 1 else 0, ID)
            else:
                SQL = '''
                    UPDATE {0} SET '{1}' = {2} WHERE ID = '{3}';
                '''.format(jsonname[:-5], querryname, sqlvalues, ID)
            # print(SQL)
            c.execute(SQL)
    conn.commit()
    conn.close()


class DB(object):

    def __init__(self, db_file_path):
        # connect sqlite db
        self._db_file_path = db_file_path
        self.conn = sqlite3.connect(self._db_file_path, check_same_thread=False, isolation_level=None, timeout=1000)
        # create cursor
        self.cur = self.conn.cursor()

    def queryall(self, sql, values: tuple = None):
        """
        查询所有的数据及对应的列名
        :param sql:
        :param values:
        :return:
        """
        with self.conn:  # 确保使用新的游标
            cur = self.conn.cursor()
            if values is None:
                cur.execute(sql)
            else:
                cur.execute(sql, values)
            st1 = time.time()
            # 获取查询结果的列名
            columns_tuple = cur.description
            columns_list = [field_tuple[0] for field_tuple in columns_tuple]
            st2 = time.time()
            # 获取查询结果
            query_result = cur.fetchall()
            st3 = time.time()
            # print("value cost", st3 - st2, "col cost", st2 - st1)
            if sql.find("limit 1") != -1:
                if query_result:
                    return dict(zip(columns_list[1:], query_result[0][1:]))
                else:
                    return {}
            else:
                return pd.DataFrame(query_result, columns=columns_list)

    def close(self):
        self.conn.close()