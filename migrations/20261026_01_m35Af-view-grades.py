"""
View для grades
"""

from yoyo import step

__depends__ = {'20261025_01_oxoek-new-column-grade'}

steps = [
    step("""CREATE VIEW grades_view AS
                SELECT 
                    g.id AS grade_id,
                    g.grade,
                    g.graded_at,
                    g.student_id,
                    CONCAT(u_stud.last_name, ' ', u_stud.first_name, ' ', u_stud.middle_name) AS student_fio,
                    ca.id AS course_assignment_id,
                    sub.id AS subject_id,
                    sub.name AS subject_name,
                    a.id AS assignment_id,
                    a.title AS assignment_title,
                    a.type AS assignment_type,
                    a.coefficient AS assignment_coefficient,
                    g.graded_by AS teacher_id,
                    CONCAT(u_teach.last_name, ' ', LEFT(u_teach.first_name, 1), '.', LEFT(u_teach.middle_name, 1), '.') AS teacher_fio,
                    g.is_final AS is_final
                FROM grades g
                JOIN students s ON g.student_id = s.user_id
                JOIN users u_stud ON s.user_id = u_stud.id
                JOIN course_assignments ca ON g.course_assignment_id = ca.id
                JOIN subjects sub ON ca.subject_id = sub.id
                LEFT JOIN assignments a ON g.assignment_id = a.id
                LEFT JOIN users u_teach ON g.graded_by = u_teach.id""")
]
