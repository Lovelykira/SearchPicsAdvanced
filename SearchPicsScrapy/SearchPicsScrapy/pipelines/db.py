import psycopg2


class DB:
    def __init__(self):
        try:
            self.con = psycopg2.connect(database='spiderdb', user='kira')
        except:
            self.con = None
            print "psycopg2.ConnectionError"

    def execute(self, query, error, return_one = False, return_all = False):
        print(query)
        try:
            cur = self.con.cursor()
            cur.execute(query)
        except:
            print error
            if self.con:
                self.con.rollback()
        finally:
            if self.con:
                self.con.commit()
            if return_one:
                return cur.fetchone()
            if return_all:
                return cur.fetchall()

    def create_table(self, table_name, *args, **kwargs):
        values = ""
        for key, val in kwargs.items():
            if values == "":
                values = "{} {}".format(key, val)
            else:
                values += ", {} {}".format(key, val)
        query = "CREATE TABLE IF NOT EXISTS {} ({});".format(table_name, values)
        self.execute(query, "CreateTable error")

    def insert(self, table_name, returning_id = False, *args, **kwargs):
        fields = ""
        values = ""
        for key, val in kwargs.items():
            if isinstance(val, str):
                val = "'{}'".format(val)
            if fields == "":
                fields = key
                values = str(val)
            else:
                fields += ", {}".format(key)
                values += ", {}".format(str(val))
        query = "INSERT INTO {} ({}) VALUES ({});".format(table_name, fields, values)
        if returning_id:
            query = query[:-1] + "RETURNING id;"
            return self.execute(query, "Insert error", return_one=True)
        return self.execute(query, "Insert error")

    def update(self, table_name, *args, **kwargs):
        set = ""
        parameters = ""
        returning = ""
        for key, val in kwargs.items():
            if isinstance(val, str):
                val = "'{}'".format(val)
            if "set_" in key:
                key = key.split("set_")[1]
                if set == "":
                    set = "{} = {}".format(key, val)
                else:
                    set += ", {} = {}".format(key, val)
            elif "__" in key:
                operator = ""
                if 'contains' in key.split("__")[1]:
                    operator = 'LIKE'
                else:
                    if 'lt' in key.split("__")[1]:
                        operator += '<'
                    if 'gt' in key.split("__")[1]:
                        operator += '>'
                    if 'e' in key.split("__")[1]:
                        operator += '='
                if parameters:
                    parameters += " AND "
                parameters = "{}{} {} {}".format(parameters, key.split("__")[0], operator, str(val))
            elif key == "returning":
                for item in val:
                    returning += "{}, ".format(item)
                returning = returning[:-2]

        query = "UPDATE {} SET {}".format(table_name, set)
        if parameters != "":
            query += " WHERE {}".format(parameters)
        if returning != "":
            query += " RETURNING {}".format(returning)
        query += ";"
        if returning != "":
            return self.execute(query, "Update error", return_one=True)
        return self.execute(query, "Update error")

    def select(self, table_name, **kwargs):
        parameters = ""
        fields = "*"
        for key, value in kwargs.items():
            if isinstance(value, str):
                value="'{}'".format(value)
            if key == "fields":
                for field in value:
                    if fields == "*":
                        fields = field
                    else:
                        fields += ", {}".format(field)
            elif "__" in key:
                operator = ""
                if 'contains' in key.split("__")[1]:
                    operator = 'LIKE'
                else:
                    if 'lt' in key.split("__")[1]:
                        operator += '<'
                    if 'gt' in key.split("__")[1]:
                        operator += '>'
                    if 'e' in key.split("__")[1]:
                        operator += '='
                if parameters:
                    parameters += " AND "
                parameters = "{}{} {} {}".format(parameters, key.split("__")[0], operator, str(value))
            else:
                if parameters:
                    parameters += " AND "
                parameters = "{}{} = {}".format(parameters, key, str(value))
        if len(kwargs) != 0:
            query = 'SELECT {} FROM {} WHERE {};'.format(fields,table_name, parameters)
        else:
            query = 'SELECT {} FROM {};'.format(fields,table_name)
        return self.execute(query, "Select error", return_all=True)
