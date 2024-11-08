from typing import Callable, Any

import psycopg
import asyncio
import random

DB_NAME = "postgres_task_queue"
DB_USER = "postgres"
DB_PASSWORD = "postgres"


async def create_table(cur: psycopg.AsyncCursor) -> None:
    """
    Create enum type, tasks table and a trigger function for automatic timestamping
    :param cur: psycopg.AsyncCursor object
    :return: None
    """
    await cur.execute("""
        CREATE TYPE status_type AS ENUM ('pending', 'processing', 'completed');
        
        CREATE TABLE IF NOT EXISTS tasks (
          id SERIAL PRIMARY KEY,
          task_name TEXT NOT NULL,
          status status_type DEFAULT 'pending',
          worker_id SMALLINT,
          created_at TIMESTAMP DEFAULT NOW(),
          updated_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE OR REPLACE FUNCTION update_timestamp()
        RETURNS TRIGGER AS $update_timestamp$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
        $update_timestamp$ LANGUAGE plpgsql;
        
        CREATE TRIGGER update_timestamp
            BEFORE UPDATE ON tasks
            FOR EACH ROW EXECUTE FUNCTION update_timestamp();
        """)


async def flush_db(cur: psycopg.AsyncCursor) -> None:
    """
    Flush database removing table, type and a function
    :param cur: psycopg.AsyncCursor object
    :return: None
    """
    await cur.execute("""
        DROP TABLE IF EXISTS tasks;
        DROP TYPE IF EXISTS status_type;
        DROP FUNCTION IF EXISTS update_timestamp();
        """)


async def run_in_transaction(conn: psycopg.AsyncConnection, func: Callable, *args, **kwargs) -> Any:
    """
    Run given function inside transaction context
    :param conn: psycopg.AsyncConnectio object
    :param func: callable object
    :param args: args to pass to func
    :param kwargs: kwargs to pass to func
    :return: Any
    """
    async with conn.transaction():
        result = await func(*args, **kwargs)
        return result


async def add_task(cur: psycopg.AsyncCursor, task_name: str) -> None:
    """
    Insert new task into database
    :param cur: psycopg.AsyncCursor object
    :param task_name: name or description of a new task
    :return: None
    """
    await cur.execute("""
        INSERT INTO tasks (task_name) VALUES
        (%s);
        """, (task_name,))


async def fetch_task(cur: psycopg.AsyncCursor, worker_id: int) -> tuple[int, str]:
    """
    Fetch task and assign it to given worker process
    :param cur: psycopg.AsyncCursor object
    :param worker_id: int id of a worker process
    :return: id of the task, name or description of the task
    """
    await cur.execute("""
        WITH row_for_update AS (
            SELECT id, task_name, status, worker_id FROM tasks
                WHERE status = 'pending' ORDER BY updated_at 
                FOR UPDATE SKIP LOCKED
                LIMIT 1
        )
        UPDATE tasks SET status = 'processing', worker_id = %s
            FROM row_for_update AS rfu
            WHERE tasks.id = rfu.id
            RETURNING tasks.id, tasks.task_name;
        """, (worker_id,))

    task_id, task_name = await cur.fetchone()
    return task_id, task_name


async def do_task(cur: psycopg.AsyncCursor, task_id: int, worker_id: int) -> None:
    """
    Simulate work done before completing given task
    :param cur: psycopg.AsyncCursor object
    :param task_id: int id of a task
    :param worker_id: int id of a worker process
    :return: None
    """
    await asyncio.sleep(random.uniform(0., 1.))
    await cur.execute("""
        UPDATE tasks SET status = 'completed'
            WHERE id = %(task_id)s AND worker_id = %(worker_id)s;
        """, {"task_id": task_id, "worker_id": worker_id})


async def main():
    conn_string = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    async with await psycopg.AsyncConnection.connect(conn_string, autocommit=True) as aconn:
        async with aconn.cursor() as acur:
            # Flush db for clean start and create needed resources
            await flush_db(acur)
            await create_table(acur)

            # Populate task table with random tasks
            for task_name in range(1, 41):
                await add_task(acur, f"task_{task_name}")

            # Simulate some kind of task queue usage
            for worker_id in range(1, 21):
                task_id, _ = await run_in_transaction(aconn, fetch_task, acur, worker_id)
                if worker_id % 2 == 0:
                    await run_in_transaction(aconn, do_task, acur, task_id, worker_id)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
    asyncio.run(main())
