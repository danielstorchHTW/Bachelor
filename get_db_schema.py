import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

pg_userid = os.getenv("pg_userid")
pg_password = os.getenv("pg_password")
pg_host = os.getenv("pg_host")
pg_db = os.getenv("pg_db")

if not pg_userid or not pg_password:
    raise EnvironmentError("Umgebungsvariablen pg_userid und pg_password sind nicht gesetzt.")

engine = create_engine(
    f'postgresql+psycopg://{pg_userid}:{pg_password}@{pg_host}/{pg_db}', 
    connect_args = {
        'options': '-c search_path=${user},ugeobln,ugm,uinsta,umisc,umobility,usozmed,public', 
        'keepalives_idle': 120
    },
    pool_size=1, 
    max_overflow=0,
    execution_options={ 'isolation_level': 'AUTOCOMMIT' }
)

def er_diagram_with_keys(schema):
    with engine.connect() as con:
        # Get all Tables from Schema
        sql_tables = f"""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = '{schema}'
        ORDER BY tablename
        """
        df_tables = pd.read_sql_query(text(sql_tables), con)

        # Create Lists to save values for each table
        columns_data = []
        pk_constraints = []
        fk_constraints = []

        # Loop though each table and get column information and not null constraints
        for table in df_tables['tablename']:
            sql_columns = f"""
            SELECT a.attname AS column_name, 
                   format_type(a.atttypid, a.atttypmod) AS data_type,
                   a.attnotnull AS is_not_null
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = '{table}' 
              AND n.nspname = '{schema}' 
              AND a.attnum > 0 
              AND NOT a.attisdropped
            ORDER BY a.attnum
            """
            # Query Database and add information into a dataframe
            df_columns = pd.read_sql_query(text(sql_columns), con)

            # Add information to List as tuple (dataframe to list)
            for _, row in df_columns.iterrows():
                columns_data.append((table, row['column_name'], row['data_type'], row['is_not_null']))

            # get primary Key for each table
            sql_pk = f"""
            SELECT 
                pg_attribute.attname AS "Column", 
                format_type(pg_attribute.atttypid, pg_attribute.atttypmod) AS "Data Type"
            FROM 
                pg_index
                JOIN pg_class ON pg_class.oid = pg_index.indrelid
                JOIN pg_attribute ON pg_attribute.attrelid = pg_class.oid 
                JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
            WHERE 
                pg_namespace.nspname = '{schema}'  
                AND pg_class.relname = '{table}' 
                AND pg_attribute.attnum = ANY(pg_index.indkey)
                AND pg_index.indisprimary;
            """
            # Query database and add primary key information to pandas df
            df_pk = pd.read_sql_query(text(sql_pk), con)

            # Add primary key infomration to list as tuple
            for _, row in df_pk.iterrows():
                pk_constraints.append((table, row['Column']))

            # get foreign key for each table
            sql_fk = f"""
            SELECT
                att2.attname AS column_name,
                cl.relname AS foreign_table_name,
                att.attname AS foreign_column_name
            FROM
                (SELECT unnest(con1.conkey) AS parent, unnest(con1.confkey) AS child, con1.confrelid, con1.conrelid
                FROM pg_class cl
                JOIN pg_namespace ns ON cl.relnamespace = ns.oid
                JOIN pg_constraint con1 ON con1.conrelid = cl.oid
                WHERE con1.contype = 'f'
                AND cl.relname = '{table}'
                AND ns.nspname = '{schema}') AS con
            JOIN pg_attribute att ON att.attnum = con.child AND att.attrelid = con.confrelid
            JOIN pg_class cl ON cl.oid = con.confrelid
            JOIN pg_attribute att2 ON att2.attnum = con.parent AND att2.attrelid = con.conrelid;
            """
            # # Query database and add foreign key values to dataframe
            df_fk = pd.read_sql_query(text(sql_fk), con)

            # add fk information to list as tuple (pointer to related table and related column)
            for _, row in df_fk.iterrows():
                fk_constraints.append((table, row['column_name'], row['foreign_table_name'], row['foreign_column_name']))

        # Add values to Dataframe with 'custom' column names
        df_result = pd.DataFrame(columns_data, columns=['Table', 'Column', 'Data Type', 'Not Null'])
        df_pk = pd.DataFrame(pk_constraints, columns=['Table', 'Primary Key'])
        df_fk = pd.DataFrame(fk_constraints, columns=['Table', 'Foreign Key', 'Referenced Table', 'Referenced Column'])

        return df_result, df_pk, df_fk
    
def dataframe_to_plantuml(df_columns, df_pk, df_fk):
    # create plantuml text
    plantuml = "@startuml\n"
    
    # loop through all tables
    tables = df_columns['Table'].unique()
    for table in tables:
        plantuml += f"class {table} {{\n"
        
        # add columns
        columns = df_columns[df_columns['Table'] == table] 
        pk = df_pk[df_pk['Table'] == table]  # pk 
        fk = df_fk[df_fk['Table'] == table]  # fk

        for _, row in columns.iterrows():
            # if pk -> '[PK]'
            if not pk.empty and row['Column'] in pk['Primary Key'].values:
                plantuml += f"  + {row['Column']} : {row['Data Type']} [PK]"
                if row['Not Null']:
                    plantuml += " [NOT NULL]"
                plantuml += "\n"
            elif not fk.empty and row['Column'] in fk['Foreign Key'].values:
                # if fk -> '[FK]'
                plantuml += f"  + {row['Column']} : {row['Data Type']} [FK]"
                if row['Not Null']:
                    plantuml += " [NOT NULL]"
                plantuml += "\n"
            else:
                plantuml += f"  {row['Column']} : {row['Data Type']}"
                # if not null constraint -> '[NOT NULL]'
                if row['Not Null']:
                    plantuml += " [NOT NULL]"
                plantuml += "\n"
        
        plantuml += "}\n\n"

    # add relationships
    for _, row in df_fk.iterrows():
        plantuml += f"{row['Table']} --> {row['Referenced Table']} : FK({row['Foreign Key']} -> {row['Referenced Column']})\n"

    plantuml += "@enduml"
    
    return plantuml