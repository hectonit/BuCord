"""module for my entities"""
import psycopg2


class Cursor(psycopg2.extensions.cursor):
    """my db cursor class"""
    sys_execute = psycopg2.extensions.cursor.execute

    def fetch(self, query, *args):
        """
        fetch all results

        :param query: sql code
        :type query: str
        :param args: params to insert in sql code
        :type args: all when str() available
        :return: list of record objects
        :rtype: list
        """
        self.sys_execute(query, args)
        description = self.description
        rows = self.fetchall()
        return [Record(record, description) for record in rows] if rows else None

    def fetch_row(self, query, *args):
        """
        fetch first row from results

        :param query: sql code
        :type query: str
        :param args: params to insert in sql code
        :type args: all when str() available
        :return: one record
        :rtype: Record
        """
        self.sys_execute(query, args)
        description = self.description
        row = self.fetchone()
        return Record(row, description) if row else None

    def fetch_val(self, query, *args, column=0):
        """
        fetch one value from first row

        :param query: sql code
        :type query: str
        :param args: params to insert in sql code
        :type args: all when str() available
        :param column: index of column(starts with 0)
        :type column: int
        :return: value from column
        :rtype: all
        """
        self.sys_execute(query, args)
        row = self.fetchone()
        return row[column] if row else None

    def execute(self, query, *args):
        """

        :param query: sql code
        :type query: str
        :param args: params to insert in sql code
        :type args: all when str() available
        """
        self.sys_execute(query, args)


class Record:
    """
    my record instance
    """

    def __init__(self, row, description=None):
        if description is None:
            description = [i for i in range(len(row))]
        self.record = {}
        for index, column in enumerate(description):
            self.record[column.name] = row[index]

    def __len__(self):
        return len(self.record)

    def __getitem__(self, item):
        return self.record[item]

    def __contains__(self, item):
        return item in self.record

    def __iter__(self):
        return iter(self.record)

    def get(self, name, default=None):
        """
        dict.get implementation

        :param name: name of key
        :type name: all
        :param default: returns if key not in record
        :type default: all
        :return: default or value
        :rtype: all
        """
        return self.record.get(name, default)

    def keys(self):
        """
        dict.keys implementation

        :return: keys
        :rtype: iter
        """
        return self.record.keys()

    def items(self):
        """
        dict.items implementation

        :return: (field, value) pairs
        :rtype: iter
        """
        return self.record.keys()
