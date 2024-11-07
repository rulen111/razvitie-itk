import psycopg
import asyncio
import random

DB_NAME = "postgres_task_queue"
DB_USER = "postgres"
DB_PASSWORD = "postgres"


async def create_table(cur):
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


async def flush_db(cur):
    await cur.execute("""
        DROP TABLE IF EXISTS tasks;
        DROP TYPE IF EXISTS status_type;
        DROP FUNCTION IF EXISTS update_timestamp();
        """)


async def run_in_transaction(conn, func, *args, **kwargs):
    async with conn.transaction():
        result = await func(*args, **kwargs)
        return result


async def add_task(cur, task_name):
    await cur.execute("""
        INSERT INTO tasks (task_name) VALUES
        (%s)
        """, (task_name,))


async def fetch_task(cur, worker_id):
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


async def do_task(cur, task_id):
    await asyncio.sleep(random.randint(1, 10))
    await cur.execute("""
        SELECT id, status FROM tasks
            WHERE id = %s FOR UPDATE
        
        UPDATE tasks SET status = 'completed'
        """, (task_id,))


async def main():
    async with await psycopg.AsyncConnection.connect(
            f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}", autocommit=True) as aconn:
        async with aconn.cursor() as acur:

            await flush_db(acur)
            await create_table(acur)
            for task_name in range(1, 11):
                await add_task(acur, f"task_{task_name}")

            await asyncio.sleep(3)
            for worker_id in range(1, 11):
                task = await run_in_transaction(aconn, fetch_task, acur, worker_id)
                print(task)
                # async with aconn.transaction():
                #     print(f"Worker {worker_id} fetching task...")
                #     task = await fetch_task(acur, worker_id)
                #     print(f"Worker {worker_id} fetched task {task}")
                #     print(task)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
    asyncio.run(main())
