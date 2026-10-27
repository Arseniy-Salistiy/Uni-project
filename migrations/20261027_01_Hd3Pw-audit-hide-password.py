"""
Не храним хеш пароля в журнале аудита
"""

from yoyo import step

__depends__ = {'20261026_02_7W6rO-'}

steps = [
    step("""
CREATE OR REPLACE FUNCTION process_audit_logging()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id INT;
    v_old JSONB := NULL;
    v_new JSONB := NULL;
BEGIN
    BEGIN
        v_user_id := current_setting('app.current_user_id', true)::INT;
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;

    IF (TG_OP = 'DELETE') THEN
        v_old := to_jsonb(OLD) - 'password';
    ELSIF (TG_OP = 'INSERT') THEN
        v_new := to_jsonb(NEW) - 'password';
    ELSIF (TG_OP = 'UPDATE') THEN
        v_old := to_jsonb(OLD) - 'password';
        v_new := to_jsonb(NEW) - 'password';
    END IF;

    INSERT INTO AUDIT_LOGS (USER_ID, ACTION, TABLE_NAME, RECORD_ID, OLD_VALUES, NEW_VALUES)
    VALUES (
        v_user_id,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.ID, OLD.ID),
        v_old,
        v_new
    );

    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""),
    step("""UPDATE audit_logs
            SET old_values = old_values - 'password',
                new_values = new_values - 'password'
            WHERE table_name = 'users'""")
]
