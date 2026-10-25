"""
Change grades
"""

from yoyo import step

__depends__ = {'20261022_01_FsAyr-file-upload-tables'}

steps = [
    step("""ALTER TABLE grades
            ALTER COLUMN grade TYPE SMALLINT USING ROUND(grade)::SMALLINT
        """)
]
