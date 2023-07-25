import inspect
import logging
import sqlite3
from datetime import datetime, timedelta


class SqliteDB:
    """Class for handling booking_dict data in the database.
    
    :param db_file: database file (full path)
    :param table_name: name of the table in the database.
    Should be used first time running.
    """

    db_file: str
    table_name: str
    conn: sqlite3.Connection
    column: str
    booking_dict: dict


    def __init__(self, db_file: str, table_name: str='egl_bookings') -> None:
        self.db_file = db_file
        self.table_name = table_name
        self.conn = self._create_connection()
        self.column = None
        self.booking_dict = None


    def _create_connection(self) -> sqlite3.Connection:
        """Create a database connection to the SQLite database
        specified by db_file upon creation of class.

        :return: Connection object or None
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                self.conn = conn
            return self.conn
        
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")
        return None
    
    
    def _check_table_name(self, table_name: str) -> None:
        """Check if table name is set. If not, raise error.

        :param table_name: name of the table
        """

        table_name_check = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
            ).fetchall()
        if table_name_check:
            return table_name_check[0][0]
        elif table_name is None:
            raise ValueError("table_name not set, and no table in database. Set a table_name when creating the SqliteDB class.")
        return None
    
    
    def create_table(self, columns:dict) -> None:
        """Create a new Sql table. If table name already exists, do nothing.

        :param table_name: name of the table
        :param columns: dictionary of columns and their data types (text/int))
        """

        if not isinstance(columns, dict):
            raise TypeError("columns must be a dictionary")
        

        sql_table = f'''
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            {', '.join(f"{key} {value}" for key, value in columns.items())}
        );'''

        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_table)
    
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")


    def create_booking(self, booking_dict: dict) -> None:
        """Create a new booking_dict from a dictionary of booking_dict data.

        :param booking_dict: dictionary of booking_dict data
        """

        sql_booking = f'''
        INSERT INTO {self.table_name}(
            {', '.join(f"{key}" for key in booking_dict.keys())})
        VALUES(
            {', '.join(f"'{value}'" for value in booking_dict.values())}
            );'''

        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_booking)
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")


    def _select_sql_row_data(self) -> dict:
        """Select a row of booking_dict data by the booking_dict id.
        
        :return: dictionary of booking_dict data
        """

        sql_select = f'''SELECT * FROM {self.table_name}
        WHERE {self.column} = {self.booking_dict[self.column]}'''

        try:
            with self.conn as conn:
                cur = conn.cursor()
                row_data = cur.execute(sql_select).fetchone()            
            return row_data
        
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")
        return None


    def update_booking(self, booking_dict:dict, column: str='booking_no', booking_in_navis: bool=True) -> dict:
        """Update a booking_dict by the booking_dict id.

        :param column: column to search by
        :param booking_dict: dictionary of booking_dict data
        :param booking_in_navis: boolean value for booking_in_navis column. If False, change to 0.
        :return: dictionary of boolean values for each column,
        True if the column was updated, False if not
        """

        self.column = column
        self.booking_dict = booking_dict

        sql_row_data = self._select_sql_row_data()

        # Do not want to overwrite 'tod' and 'navis_voy' if it exists in Db but not in booking_dict
        if booking_dict.get('tod') is None or len(booking_dict.get('tod')) == 0:
            if sql_row_data[8] is not None or len(sql_row_data[8]) > 0:
                booking_dict['navis_voy'] = sql_row_data[6]
                booking_dict['tod'] = sql_row_data[8]
                
        bool_dict = {}
        for sql_value, booking_key in zip(sql_row_data, booking_dict.keys()):
            if sql_value == booking_dict.get(booking_key):
                bool_dict[booking_key] = False
            else:
                bool_dict[booking_key] = True
        
        # If argument booking_in_navis is False then change to 0
        if not booking_in_navis:
            booking_dict['booking_in_navis'] = 0
        # If booking_in_navis is true then do not increment pdf name string in sqlite
        # as it may cause exponential growth of pdf name string
        else:
            booking_dict['pdf_name'] = f"{sql_row_data[22]}, {booking_dict.get('pdf_name')}"

        sql_update = f"UPDATE {self.table_name} SET " + ', '.join(
            f"{key}=?" for key in booking_dict.keys()) + f" WHERE {column}=?"
        #cur = self.conn.cursor()
        
        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_update, tuple(booking_dict.values()) + (booking_dict[column],))
            
            return bool_dict
        
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")
        return None
    
    
    def update_booking_with_cancellation(self, booking_dict:dict, column: str='booking_no') -> None:
        """
        TODO: docstring
        """

        self.column = column
        self.booking_dict = booking_dict

        sql_row_data = self._select_sql_row_data()
        
        booking_dict['pdf_name'] = f"{sql_row_data[22]}, {booking_dict.get('pdf_name')}"

        revised_no = sql_row_data[1]
        if booking_dict['revised_no'] > revised_no:
            revised_no = booking_dict['revised_no']

        sql_update = f"UPDATE {self.table_name} SET revised_no=?, cancellation =?, pdf_name=? WHERE {column} = ?"
        
        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_update, (revised_no, booking_dict['cancellation'], booking_dict['pdf_name'], booking_dict[column],))
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")


    def update_booking_even_if_lower_revised_no(self, booking_dict:dict, column: str='booking_no') -> None:
        """
        TODO: docstring
        """

        self.column = column
        self.booking_dict = booking_dict

        sql_row_data = self._select_sql_row_data()
        
        booking_dict['pdf_name'] = f"{sql_row_data[22]}, {booking_dict.get('pdf_name')}"

        revised_no = sql_row_data[1]
        if int(booking_dict['revised_no']) > revised_no:
            revised_no = booking_dict['revised_no']

        sql_update = f'''
        UPDATE {self.table_name} SET pdf_name=? WHERE {column}=?'''
        
        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_update, (booking_dict['pdf_name'], booking_dict[column],))
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")


    def when_cancellation_exists_in_db(self, booking_dict:dict, column: str='booking_no') -> None:
        """
        TODO: docstring
        """

        self.column = column
        self.booking_dict = booking_dict

        sql_row_data = self._select_sql_row_data()
        
        booking_dict['pdf_name'] = f"{sql_row_data[22]}, {booking_dict.get('pdf_name')}"

        revised_no = sql_row_data[1]
        if int(booking_dict['revised_no']) > revised_no:
            revised_no = booking_dict['revised_no']

        sql_update = f'''
        UPDATE {self.table_name} SET revised_no=?, pdf_name=? WHERE {column}=?'''
        
        cur = self.conn.cursor()
        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_update, (booking_dict['revised_no'], booking_dict['pdf_name'], booking_dict[column],))
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")
    

    def get_booking_data(self, booking: str|dict, column: str='booking_no') -> dict:
        """Get booking_dict data by the booking_dict id.

        :param column: column to search by
        :param booking_dict: dictionary of booking_dict data
        """

        self.column = column

        if isinstance(booking, dict):
            self.booking_dict = booking
        else:
            self.booking_dict = {column: booking}
        
        return self._select_sql_row_data()
    

    def add_column_to_table(self, column: str|list, type: str|list) -> None:
        """Add columns to the table.

        :param column: name of the column, can be string or list of strings
        :param type: data type of the column, can be string or list of strings
        """

        if isinstance(column, list) and isinstance(type, list):
            sql_add_columns = f'''
            ALTER TABLE {self.table_name}
            ADD COLUMN {', '.join(f"{column[i]} {type[i]}" for i in range(len(column)))};
            '''
        else:
            sql_add_columns = f'''
            ALTER TABLE {self.table_name}
            ADD COLUMN {column} {type};
            '''


        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_add_columns)
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")

    
    def update_values_in_column(self, column: str, value: str, where_column: str=None,
                                where_value: str=None) -> None:
        """Update values in a column, optionally search by another column.

        :param column: column to update
        :param value: value to update to
        :param where_column: column to search by. If None, update all values in column
        :param where_value: value to search by. If None, update all values in column
        """

        sql_update = f'''UPDATE {self.table_name} SET {column} = "{value}"'''

        # If below params are not None, add WHERE clause to sql statement
        if where_column is not None and where_value is not None:
            sql_update += f''' WHERE {where_column} = {where_value}'''
        
        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_update)

        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")


    def _get_list_where_values_not_in_database(self, navis_voy: bool=None, terminal: bool=None) -> list:
        """Get bookings where navis voyage or terminal is not in database.
        Called by get_booking_numbers_where_navis_voy_or_terminal_not_in_database.
        
        :param navis_voy: navis voyage to search by
        :param terminal: terminal to search by
        :return: list of booking numbers
        """

        if navis_voy is not None:
            sql = f'''
            SELECT booking_no, navis_voy
            FROM {self.table_name} WHERE booking_in_navis=False'''

        # Only get bookings dated from today and one year ahead
        elif terminal is not None:
            date_today = datetime.today().strftime('%Y/%m/%d')
            one_year_from_today = (
                datetime.today() + timedelta(days=365)
                ).strftime('%Y/%m/%d')
            sql = f'''
            SELECT booking_no FROM {self.table_name}
            WHERE (tod = '' or tod IS NULL)
            AND (etd BETWEEN '{date_today}'
            AND '{one_year_from_today}')'''

        else: return None
    
        try:
            with self.conn as conn:
                cur = conn.cursor()
                db_list = cur.execute(sql).fetchall()
            return db_list
        
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")


    def get_bookings_where_navis_voy_not_in_database(self) -> list:
        """Get bookings where navis voyage is not in database."""
        return self._get_list_where_values_not_in_database(navis_voy=True)
    

    def get_bookings_where_terminal_not_in_database(self) -> list:
        """Get bookings where terminal is not in database."""
        return self._get_list_where_values_not_in_database(terminal=True)


    def drop_column_from_table(self, column: str) -> None:
        """Drop a column from the table."""

        sql = f'''
        ALTER TABLE {self.table_name} DROP COLUMN {column}'''

        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql)
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")


    def delete_booking(self, booking: str, column: str='booking_no') -> None:
        """Delete a booking_dict by booking_dict id.

        :param column: column to search by
        :param booking: booking_dict id
        """

        sql_delete = f'''
        DELETE FROM {self.table_name}
        WHERE {column} = {booking}
        '''

        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_delete) 
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")
        

    def delete_all_bookings(self) -> None:
        """Delete all rows in the bookings table."""

        sql_delete = f'''
        DELETE FROM {self.table_name}
        '''

        try:
            with self.conn as conn:
                cur = conn.cursor()
                cur.execute(sql_delete)
            
        except sqlite3.Error as e:
            logging.error(e)
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}", "\n",
                  f"Error: {e}")

