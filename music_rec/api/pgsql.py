from typing import List, Tuple
import re
import logging
import psycopg

logger = logging.getLogger('postgresql_api')


def sep_query_and_params(query: str) -> Tuple[str, Tuple]:
    """
    Prepare a SQL query by replacing numeric and string values with '%s'.
    Correctly handles integers, floating-point numbers, strings in single quotes, and date formats.
    This version ensures that full strings within quotes are not parsed or altered,
    which prevents incorrect separations of literal strings.
    """
    pattern = re.compile(r"'\d{4}-\d{2}-\d{2}'|'\d+\.\d+'|'\d+'|'.+?'|\d+\.\d+|\d+")

    def replace_with_placeholder(match):
        value = match.group(0)
        if value.startswith("'") and value.endswith("'"):
            converted_value = value[1:-1]
        else:
            try:
                converted_value = float(value) if '.' in value else int(value)
            except ValueError:
                converted_value = value
        params.append(converted_value)
        return "%s"

    params = []
    query_with_placeholders = pattern.sub(replace_with_placeholder, query)
    return query_with_placeholders, tuple(params)


def is_sql_allowed(sql_script: str, restricted_cmds: List = None) -> bool:
    """
    Simple validation to check for restricted commands in SQL script.
    """
    for command in restricted_cmds:
        if command in sql_script.upper():
            return False
    return True


def run_sql_script(postgres_conn, sql_script: str, params: tuple = None, commit: bool = True) -> dict:
    """
    Execute an arbitrary SQL script with parameter binding.
    """
    disabled_cmds = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER']
    if not is_sql_allowed(sql_script, disabled_cmds):
        logger.error("Restricted SQL script detected. Execution aborted. ❌")
        return {"status": "failed", "message": "Restricted SQL script detected."}

    try:
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(sql_script, params)
                else:
                    cursor.execute(sql_script)
                if commit:
                    conn.commit()
                    logger.info("SQL script executed successfully and committed to PostgreSQL database. ✅️")
                    return {"status": "success", "message": "SQL script executed and committed successfully."}
                results = cursor.fetchall()
                logger.info("SQL script executed successfully, fetched results. ✅️")
                return {"status": "success", "message": "SQL script executed successfully.", "data": results}
    except psycopg.Error as excep:
        logger.error("%s: SQL script execution failed ❌", excep)
        return {"status": "failed", "message": f"PostgreSQL script execution error: {excep}"}


def insert_bulk_data_into_sql(postgres_conn, tb_name, data_dicts: list, commit: bool = True) -> dict:
    """
    Insert multiple records into a PostgreSQL table with param binding.
    """
    if not data_dicts:
        return {"status": "failed", "message": "No data provided"}

    col_names = ', '.join(data_dicts[0].keys())
    placeholders = ', '.join(['%s'] * len(data_dicts[0]))
    query = f"INSERT INTO {tb_name} ({col_names}) VALUES ({placeholders})".replace("'", '')

    values = [tuple(data_dict.values()) for data_dict in data_dicts]

    try:
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                logger.info("Attempting to bulk insert %d records into PostgreSQL db.", len(values))
                cursor.executemany(query, values)
                if commit:
                    conn.commit()
                    logger.info("%d records bulk inserted into PostgreSQL db.✅️", len(values))
                    return {"status": "success", "message": "Bulk records inserted into PostgreSQL db"}
                logger.info("Bulk record insertion waiting to be committed to PostgreSQL db.🕓")
                return {"status": "success", "message": "Bulk record insertion waiting to be committed."}
    except psycopg.Error as excep:
        logger.error("%s: PostgreSQL bulk record insertion failed ❌", excep)
        return {"status": "failed", "message": f"PostgreSQL bulk record insertion error: {str(excep)}"}


def insert_data_into_sql(postgres_conn, tb_name, data_dict: dict, commit: bool = True) -> dict:
    """
    Insert a record into a PostgreSQL table with param binding.
    """
    col_names = ', '.join(data_dict.keys())
    placeholders = ', '.join(['%s'] * len(data_dict))
    query = f"INSERT INTO {tb_name} ({col_names}) VALUES ({placeholders})".replace("'", '')
    values = tuple(data_dict.values())

    try:
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                if commit:
                    conn.commit()
                    logger.info("Record inserted into PostgreSQL db.✅️")
                    return {"status": "success", "message": "Record inserted into PostgreSQL db"}
                logger.info("Record insertion waiting to be committed to PostgreSQL db.🕓")
                return {"status": "success", "message": "Record insertion waiting to be committed."}
    except psycopg.Error as excep:
        logger.error("%s: PostgreSQL record insertion failed ❌", excep)
        return {"status": "failed", "message": "PostgreSQL record insertion error"}


def select_data_from_sql_with_id(postgres_conn, tb_name, data_id: int) -> dict:
    """
    Query PostgreSQL db to get the data record using the unique data_id.
    """
    query = f"SELECT * FROM {tb_name} WHERE id = %s"
    values = (data_id,)

    try:
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                data = cursor.fetchone()
                if data is None:
                    logger.warning("PostgreSQL record with id: %s does not exist ❌.", data_id)
                    return {"status": "failed", "message": f"PostgreSQL record with id: {data_id} does not exist"}
                logger.info("Data with id: %s retrieved from PostgreSQL db.✅️", data_id)
                return {"status": "success", "message": f"Record matching id: {data_id} retrieved from PostgreSQL db", "data": data}
    except psycopg.Error as excep:
        logger.error("%s: PostgreSQL record retrieval failed ❌", excep)
        return {"status": "failed", "message": "PostgreSQL record retrieval error"}


def select_all_data_from_sql(postgres_conn, tb_name) -> dict:
    """
    Query PostgreSQL db to get all data.
    """
    query = f"SELECT * FROM {tb_name}"

    try:
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                if not data:
                    logger.warning("No PostgreSQL records were found ❌.")
                    return {"status": "failed", "message": "No PostgreSQL records were found."}
                logger.info("All records retrieved from PostgreSQL db.✅️")
                return {"status": "success", "message": "All records retrieved from PostgreSQL db", "data": data}
    except psycopg.Error as excep:
        logger.error("%s: PostgreSQL record retrieval failed ❌", excep)
        return {"status": "failed", "message": "PostgreSQL record retrieval error"}


def delete_data_from_sql_with_id(postgres_conn, tb_name, data_id: int, commit: bool = True) -> dict:
    """
    Delete a record from PostgreSQL db using the unique data_id.
    """
    select_query = f"SELECT * FROM {tb_name} WHERE id = %s"
    del_query = f"DELETE FROM {tb_name} WHERE id = %s"

    try:
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_query, (data_id,))
                if not cursor.fetchone():
                    logger.error("Data with id: %s does not exist in PostgreSQL db.❌", data_id)
                    return {"status": "failed", "message": f"PostgreSQL record with id: {data_id} does not exist in db"}

                cursor.execute(del_query, (data_id,))
                if commit:
                    conn.commit()
                    logger.info("Data with id: %s deleted from PostgreSQL db.✅️", data_id)
                    return {"status": "success", "message": "Record deleted from PostgreSQL db"}
                logger.info("Record deletion waiting to be committed to PostgreSQL db.🕓")
                return {"status": "success", "message": "Record deletion waiting to be committed."}
    except psycopg.Error as excep:
        logger.error("%s: PostgreSQL record deletion failed ❌", excep)
        return {"status": "failed", "message": "PostgreSQL record deletion error"}


def table_exists(postgres_conn, tb_name: str) -> bool:
    """Check if table exists in the PostgreSQL database"""
    try:
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT to_regclass('{tb_name}')")
                result = cursor.fetchone()
                return result[0] is not None
    except psycopg.Error as e:
        print(f"Error checking if table exists: {e}")
        return False


def entries_exist(postgres_conn, tb_name: str, conditions: dict, logic: str = 'AND') -> bool:
    """
    Check if entries exist in a PostgreSQL table.
    """
    try:
        assert logic in {"AND", "OR"}
        with postgres_conn() as conn:
            with conn.cursor() as cursor:
                clause = f" {logic} ".join([f"{column} = %s" for column in conditions.keys()])
                query = f"SELECT 1 FROM {tb_name} WHERE {clause} LIMIT 1"
                values = tuple(value for value in conditions.values())
                cursor.execute(query, values)
                result = cursor.fetchone()
                return result is not None
    except psycopg.Error as e:
        print(f"Error checking if entries exist: {e}")
        return False
