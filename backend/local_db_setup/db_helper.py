from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from config import Config

class DBHelper:
    def __init__(self):
        """
        Initializes MySQL database helper with connection details.
        """
        db_cfg = Config().get_db_config()
        # Define the connection string
        self.connection_string = f"mysql+pymysql://{db_cfg.user}:{db_cfg.password}@{db_cfg.uri}:{db_cfg.port}"
        # Create the SQLAlchemy engine
        self.engine = create_engine(self.connection_string, echo=True)

    def create_database(self, db_name):
        """
        Creates the database if it does not exist.
        """
        sql = f"""CREATE DATABASE IF NOT EXISTS {db_name};"""
        with self.engine.connect() as conn:
            try:
                conn.execute(text(sql))
                print(f"Database {db_name}created or already exists.")
            except SQLAlchemyError as e:
                print(f"Error occurred while creating database: {e}")

    def show_variables(self):
        """
        Shows MySQL variables.
        """
        sql = "SHOW VARIABLES;"

        with self.engine.connect() as conn:
            try:
                result = conn.execute(text(sql))
                for res in result:
                    print(res)
            except SQLAlchemyError as e:
                print(f"Error occurred while fetching variables: {e}")

    def create_table(self, sql, table_name):
        """Creates or replaces a table with the provided SQL.

        Args:
            sql (str): Query content
            table_name (str): db_name.table_name
        """
        # Use the engine to establish a connection within a context manager
        with self.engine.connect() as conn:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.execute(text(sql))
                tab_structure = conn.execute(text(f"SHOW COLUMNS FROM {table_name};"))
                columns = tab_structure.fetchall()
                print(columns)
            except SQLAlchemyError as e:
                print(f"Error occurred while creating table {table_name}: {e}")

    def query_data(self, sql):
        """Query data"""
        try:
            with self.engine.connect() as conn:
                existing_data = pd.read_sql(sql, conn)
            return existing_data
        except Exception as e:
            print(f"Error occurred while selecting date: {e}")
            return pd.DataFrame()

    def save_df_data(self, df, db_name, table_name):
        """Save data to certain table
        Args:
            df (DataFrame): DataFrame
            table_name (str): db_name.table_name
        """
        # Use the engine to establish a connection within a context manager
        try:
            df.to_sql(name=table_name, con=self.engine, schema=db_name, if_exists='append', index=False)
            print(f"Successfully inserted {len(df)} rows into {table_name}!")
        except SQLAlchemyError as e:
            print(f"Error occurred during insert: {e}")
