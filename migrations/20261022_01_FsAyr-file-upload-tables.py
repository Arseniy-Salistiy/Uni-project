"""
file upload tables
"""

from yoyo import step

__depends__ = {'20261017_02_v80OW-more-triggers'}

steps = [
    step("""
    CREATE TABLE submissions (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        student_id int not null references students(user_id) on delete cascade,
        assignment_id int references assignments(id) on delete cascade,
        course_assignment_id int not null references course_assignments(id) on delete cascade,
        description text,
        submission_time timestamp not null default now(),
        unique(student_id, assignment_id)
    );
    """),

    step("""
    ALTER TABLE grades ADD COLUMN submission_id int REFERENCES submissions(id) ON DELETE SET NULL;
    """),

    step("""
    CREATE TABLE attachments (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        file_name varchar(255) not null,
        s3_key varchar(512) not null unique,
        file_size bigint,
        mime_type varchar(100),
        parent_type varchar(50) not null,
        parent_id int not null,
        uploaded_by int not null,
        uploaded_at timestamp not null default now()
    );
    """),

    step("""
    CREATE INDEX attachments_parents ON attachments(parent_type, parent_id);
    """)
]