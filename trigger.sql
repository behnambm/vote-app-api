
CREATE OR REPLACE FUNCTION vote_notify_func() RETURNS trigger as $$ BEGIN PERFORM pg_notify('vote_channel', row_to_json(NEW)::text); RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER vote_notify_trigger AFTER INSERT OR UPDATE ON votes_voters FOR EACH ROW EXECUTE PROCEDURE vote_notify_func();

