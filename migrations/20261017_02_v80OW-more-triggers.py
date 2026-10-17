"""
More triggers
"""

from yoyo import step

__depends__ = {'20261017_01_7n6hZ-logs'}

steps = [
    step("""CREATE TRIGGER audit_lessons_trigger
AFTER INSERT OR UPDATE OR DELETE ON LESSONS
FOR EACH ROW EXECUTE FUNCTION process_audit_logging();
""")
]
