# Copyright (C) 2015 Chris Cummins.
#
# Labm8 is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Labm8 is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with labm8.  If not, see <http://www.gnu.org/licenses/>.
import atexit
import csv
import sqlite3 as sql

import labm8 as lab
from labm8 import fs
from labm8 import io


class Error(Exception):
    """
    Module-level base error class.
    """
    pass


class SchemaError(Exception):
    """
    Error thrown in case of conflicting schemas.
    """
    pass


class Database(object):
    def __init__(self, path, tables={}):
        """
        Arguments:
            path (str): The path to the database file.
            tables (dictionary of {str: tuple of str}, optional): A diction
              of {name: schema} pairs, where a schema is list of tuple pairs,
              of the form: (name, type).
        """
        self.path = fs.path(path)

        # Create directory if needed.
        fs.mkdir(fs.dirname(path))

        self.connection = sql.connect(self.path)
        self.tables = {}

        for name,schema in tables.iteritems():
            self.create_table(name, schema)

        io.debug("Opened connection to '{0}'".format(self.path))

        # Register exit handler
        atexit.register(self.close)

    def export_csv(self, table, path=None):
        """
        Export table to CSV file.

        Arguments:
            table The name of the table as a string.
            path (optional) The path to the exported csv. If not given,
                defaults to the path of the database, with the suffix
                "-{table_name}.csv".
        """
        if path is None:
            path = self.path + "-" + str(table) + ".csv"

        with open(path, 'wb') as file:
            writer = csv.writer(file)
            writer.writerow([x[0] for x in self.tables[table]])
            data = self.execute("SELECT * FROM " + str(table))
            writer.writerows(data)

    def export_csvs(self, prefix=None):
        """
        Export all tables to CSV files.

        Arguments:
            prefix (optional) If supplied, the filename prefix to use.
        """
        if prefix is None:
            prefix = self.path + "-"

        for table in self.tables:
            csv_path = prefix + table + ".csv"
            self.export_csv(table, path=csv_path)

    def close(self):
        self.connection.close()
        io.debug("Closed connection to '{0}'".format(self.path))

    def create_table(self, name, schema):
        self.tables[name] = schema

        schema_str = "(" + ", ".join([" ".join([str(a) for a in x])
                                     for x in schema]) + ")"
        cmd_str = "CREATE TABLE IF NOT EXISTS " + name + "\n" + schema_str
        self.execute(cmd_str)
        # io.debug(cmd_str)

    def escape_value(self, table, i, value):
        if self.tables[table][i][1].upper() == "TEXT":
            return "'" + str(value) + "'"
        else:
            return value

    def lookup_keytype(self, table, key):
        for schema in self.tables[table]:
            if schema[0] == key:
                return schema[1]
        raise SchemaError(("Failed to lookup key '{key}' in table {table}"
                           .format(key=key, table=table)))

    def escape_keyval(self, table, key, value):
        keytype = self.lookup_keytype(table, key)
        if keytype.upper() == "TEXT":
            return "'" + str(value) + "'"
        else:
            return value

    def _insert(self, table, values, ignore_duplicates=False):
        escaped_values = [self.escape_value(table, i, values[i])
                          for i in range(len(values))]

        cmd = ["INSERT"]
        if ignore_duplicates:
            cmd.append("OR IGNORE")
        cmd.append("INTO")
        cmd.append(table)
        cmd.append("VALUES (")
        cmd.append(", ".join([str(x) for x in escaped_values]))
        cmd.append(")")

        cmd_str = " ".join(cmd)
        # io.debug(cmd_str)

        self.execute(cmd_str)
        self.commit()

    def insert(self, table, values):
        return self._insert(table, values)

    def insert_unique(self, table, values):
        return self._insert(table, values, ignore_duplicates=True)

    def execute(self, *args):
        return self.connection.cursor().execute(*args)

    def commit(self):
        return self.connection.commit()

    def select(self, table, select, where):
        cmd = ["SELECT", select, "FROM", table, "WHERE", where]
        cmd_str = " ".join(cmd)
        return self.execute(cmd_str)

    def select1(self, table, select, where):
        return self.select(self, table, select, where).fetchone()

    def count(self, table, where=None):
        cmd = ["SELECT Count(*) FROM", table]
        if where is not None:
            cmd += ["WHERE", where]
        cmd_str = " ".join(cmd)
        return self.execute(cmd_str).fetchone()[0]

    def merge(self, rhs):
        """
        Merge the contents of the supplied database.

        Arguments:
            rhs Another Database instance to merge into this database.

        Raises:
            SchemaError If the schema of the merged database does not match.
        """
        # Throw an "eppy" if the schemas do not match.
        if self.tables.keys() != rhs.tables.keys():
            raise SchemaError("Schema of merged table does not match")

        self.execute("ATTACH '" + rhs.path + "' as rhs")

        for table in self.tables:
            self.execute("INSERT OR IGNORE INTO " + table +
                         " SELECT * FROM rhs." + table)

        # Tidy up.
        self.commit()
        self.execute("DETACH rhs")