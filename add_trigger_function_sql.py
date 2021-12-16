import psycopg2
from decouple import config

print("Connecting to database...")
con = psycopg2.connect(
    host=config("DB_HOST"),
    database=config("DB_NAME"),
    user=config("DB_USER"),
    password=config("DB_PASSWORD"),
)
con.autocommit = True

cur = con.cursor()
print("Creating Pub/Sub function...")
cur.execute(
    """CREATE OR REPLACE FUNCTION vote_notify_func() RETURNS trigger as $$ BEGIN PERFORM pg_notify('vote_channel', row_to_json(NEW)::text); RETURN NEW; END; $$ LANGUAGE plpgsql;
"""
)
print("Add trigger to vote database...")
cur.execute(
    """CREATE TRIGGER vote_notify_trigger AFTER INSERT OR UPDATE ON votes_voters FOR EACH ROW EXECUTE PROCEDURE vote_notify_func();"""
)
cur.close()
con.close()
print("Adding Trigger function was successfull.")
