from connection_manager import *
import pandas as pd

class TruncateQueriesManager:
    def __init__(self,connection :PgConnecionManager, prefact_table: str):
        self._connection = connection
        self._prefact = prefact_table
        self.query = None
        self.conn = connection.connection
        self.generate_query()

    def generate_query(self):
        self.query = f"TRUNCATE TABLE public.{self._prefact};"

    def truncate_table(self):
        
        try:
            conn = self.conn
            cursor = conn.cursor()
            cursor.execute(self.query)
            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"An error occurred during data truncation: {e}")

        finally:
            if cursor:
                cursor.close()


class InsertQueriesManager:
    def __init__(self,df: pd.DataFrame, connection: PgConnecionManager, prefact_table: str):
        self._df = df
        self._connection = connection
        self._prefact = prefact_table
        self.query = None
        self.conn = connection.connection
        self.generate_query()

    def generate_query(self):
        columns = list(self._df.columns)
        format_columns = [item.lower().replace(' ', '_') for item in columns]
        columns_string = ', '.join(format_columns)
        primary_key = format_columns[0]

        self.query = f"""
        INSERT INTO public.{self._prefact}(
        {columns_string})
        VALUES ({('%s,'*len(columns))[:-1]})
        ON CONFLICT ({primary_key}) DO NOTHING;
        """


    def insert_data(self):
        try:
            conn = self.conn
            cursor = conn.cursor()

            for index, row in self._df.iterrows():
                data =[row[col] for col in self._df.columns]
                cursor.execute(self.query, data)
            conn.commit()
            print(f'\n\t{index+1} rows inserted')

        except Exception as e:
            conn.rollback()
            print(f"An error occurred during data insertion: {e}")

        finally:
            if cursor:
                cursor.close()

class MergeQueriesManager:
    def __init__(self,df: pd.DataFrame, connection: PgConnecionManager, prefact_table: str ,fact_table: str):
        self._df = df
        self._connection = connection
        self._fact = fact_table
        self._prefact = prefact_table
        self.query = None
        self.conn = connection.connection
        self.generate_query()

    def generate_query(self):

        columns = list(self._df.columns)
        format_columns = [item.lower().replace(' ', '_') for item in columns]
        primary_key = format_columns[0]

        update_set = ", ".join([f"{col}=src.{col}" for col in format_columns])

        insert_columns = ", ".join(format_columns)
        insert_values = ", ".join([f"src.{col}" for col in format_columns])

        self.query = f"""
        MERGE INTO {self._fact} AS lve
        USING {self._prefact} AS src
        ON lve.{primary_key} = src.{primary_key}

        WHEN MATCHED THEN
            UPDATE SET 
            {update_set}

        WHEN NOT MATCHED THEN
            INSERT ({insert_columns})
            VALUES ({insert_values});
        """

    def merge_data(self):
    
        try:
            conn = self.conn
            cursor = conn.cursor()
            cursor.execute(self.query)
            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"An error occurred during data merge: {e}")

        finally:
            if cursor:
                cursor.close()

class QueriesManager:
    def __init__(self, df:pd.DataFrame, connection:PgConnecionManager, prefact_table:str, fact_table:str):
        self._truncateManager = TruncateQueriesManager(connection, prefact_table)
        self._insertManager = InsertQueriesManager(df, connection, prefact_table)
        self._mergeManager = MergeQueriesManager(df, connection, prefact_table,fact_table)

    def truncate_data(self):
        self._truncateManager.truncate_table()

    def insert_data(self):
        self._insertManager.insert_data()

    def merge_data(self):
        self._mergeManager.merge_data()

    def process_data(self):
        self.truncate_data()
        self.insert_data()
        self.merge_data()