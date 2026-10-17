"""
Logs
"""

from yoyo import step

__depends__ = {'20261016_01_yH2KX-initial'}

steps = [
    step("""
CREATE TABLE AUDIT_LOGS (
  ID BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  USER_ID INT,                        -- Кто изменил (передается из FastAPI)
  ACTION VARCHAR(20) NOT NULL,        -- 'INSERT', 'UPDATE', 'DELETE'
  TABLE_NAME VARCHAR(100) NOT NULL,   -- Название таблицы
  RECORD_ID INT NOT NULL,             -- ID измененной записи
  OLD_VALUES JSONB,                   -- Слепок строки ДО изменения
  NEW_VALUES JSONB,                   -- Слепок строки ПОСЛЕ изменения
  CREATED_AT TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE INDEX IX_AUDIT_LOGS_TABLE_NAME ON AUDIT_LOGS(TABLE_NAME);
CREATE INDEX IX_AUDIT_LOGS_CREATED_AT_DESC ON AUDIT_LOGS(CREATED_AT DESC);



CREATE OR REPLACE FUNCTION process_audit_logging()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id INT;
    v_old JSONB := NULL;
    v_new JSONB := NULL;
BEGIN
    -- Извлекаем ID сессии, который FastAPI выставит через SET LOCAL перед коммитом
    BEGIN
        v_user_id := current_setting('app.current_user_id', true)::INT;
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;

    -- Упаковываем данные в JSONB в зависимости от типа операции
    IF (TG_OP = 'DELETE') THEN
        v_old := to_jsonb(OLD);
    ELSIF (TG_OP = 'INSERT') THEN
        v_new := to_jsonb(NEW);
    ELSIF (TG_OP = 'UPDATE') THEN
        v_old := to_jsonb(OLD);
        v_new := to_jsonb(NEW);
    END IF;

    -- Делаем запись в общую таблицу аудита
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

CREATE TRIGGER audit_grades_trigger
AFTER INSERT OR UPDATE OR DELETE ON GRADES
FOR EACH ROW EXECUTE FUNCTION process_audit_logging();

CREATE TRIGGER audit_assignments_trigger
AFTER INSERT OR UPDATE OR DELETE ON ASSIGNMENTS
FOR EACH ROW EXECUTE FUNCTION process_audit_logging();

CREATE TRIGGER audit_users_trigger
AFTER INSERT OR UPDATE OR DELETE ON USERS
FOR EACH ROW EXECUTE FUNCTION process_audit_logging();

CREATE TRIGGER audit_groups_trigger
AFTER INSERT OR UPDATE OR DELETE ON GROUPS
FOR EACH ROW EXECUTE FUNCTION process_audit_logging();

CREATE TRIGGER audit_course_assignment_trigger
AFTER INSERT OR UPDATE OR DELETE ON COURSE_ASSIGNMENTS
FOR EACH ROW EXECUTE FUNCTION process_audit_logging();

CREATE TRIGGER audit_students_trigger
AFTER INSERT OR UPDATE OR DELETE ON STUDENTS
FOR EACH ROW EXECUTE FUNCTION process_audit_logging();
""")
]
