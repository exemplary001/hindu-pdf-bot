import psycopg

from app.config import DATABASE_URL


def get_last_successful_date():

    with psycopg.connect(
        DATABASE_URL
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT value
                FROM bot_state
                WHERE key = %s
                """,
                ("last_successful_date",)
            )

            row = cur.fetchone()

            if not row:
                return ""

            return row[0]


def save_successful_date(date_str):

    with psycopg.connect(
        DATABASE_URL
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO bot_state
                (
                    key,
                    value
                )
                VALUES
                (
                    %s,
                    %s
                )
                ON CONFLICT (key)
                DO UPDATE SET
                value = EXCLUDED.value
                """,
                (
                    "last_successful_date",
                    date_str
                )
            )

        conn.commit()