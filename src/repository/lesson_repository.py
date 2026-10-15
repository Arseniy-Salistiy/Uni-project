from fastapi import Depends
from typing import Dict, Any, List

from src.db.database import get_db
from src.schemas.lessons_schemas import *

class LessonsRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_lesson(self, payload: CreateLesson) -> Dict[str, Any]:
        query = """INSERT INTO lessons (course_assignment_id, lesson_type, lesson_date, start_time, end_time, room)
                    VALUES(%s, %s, %s, %s, %s, %s)
                    RETURNING *
                """
        with self.conn.cursor() as cur:
            cur.execute(query, (payload.course_assignment_id,
                                payload.lesson_type, payload.lesson_date,
                                payload.start_time, payload.end_time,
                                payload.room,))
            return cur.fetchone()

    def get_lessons_by_group(self, group_id: int, lesson_date: LessonDate) -> List[Dict[str, Any]]:
        query = """SELECT l.* FROM lessons as l
                    JOIN course_assignments as ca ON l.course_assignment_id = ca.id
                    WHERE ca.group_id=%s AND l.lesson_date BETWEEN %s AND %s"""

        with self.conn.cursor() as cur:
            cur.execute(query, (group_id, lesson_date.start_date,
                                lesson_date.end_date,))
            return cur.fetchall()

    def get_lesson_by_id(self, lesson_id: int) -> None | Dict[str, Any]:
        query = """SELECT * FROM lessons WHERE id=%s"""

        with self.conn.cursor() as cur:
            cur.execute(query, (lesson_id,))
            return cur.fetchone()

    def patch_lesson(self, lesson_id: int, payload: LessonPatch) -> Dict[str, Any]:
        data = payload.model_dump(exclude_unset=True)

        if not data:
            return {}

        keys = ', '.join([f'{i}=%s' for i in data.keys()])
        query = f"""UPDATE lessons SET {keys} WHERE id=%s
                    RETURNING *
                """

        with self.conn.cursor() as cur:
            cur.execute(query, (*data.values(), lesson_id,))
            return cur.fetchone()

    def delete_lesson(self, lesson_id: int) -> Dict[str, Any]:
        query = """DELETE FROM lessons WHERE id=%s
                    RETURNING *
                """

        with self.conn.cursor() as cur:
            cur.execute(query, (lesson_id,))
            return cur.fetchone()

    def mark_attendance(self, payload: CreateAttendance) -> Dict[str, Any]:
        query = """INSERT INTO attendance (lesson_id, student_id, status)
                    VALUES(%s, %s, %s)
                    RETURNING *"""
        with self.conn.cursor() as cur:
            cur.execute(query, (payload.lesson_id,
                                payload.student_id,
                                payload.status,))
            return cur.fetchone()

    def get_attendence_by_student(self, course_id: int, student_id: int, timeline: StudentDate, filter: AttendanceFilter) -> List[Dict[str, Any]]:
        query = """SELECT a.* FROM attendance as a
                    JOIN lessons as l ON l.id = a.lesson_id
                    WHERE l.course_assignment_id=%s AND a.student_id=%s
                """
        params = [course_id, student_id]
        dates = timeline.model_dump(exclude_unset=True)
        filt = filter.model_dump(exclude_unset=True)
        print(dates, filt)
        if filt:
            d = """AND a.status=%s"""
            query += d
            params += [filt['status']]
        
        if dates.get('start_date') and dates.get('end_date'):
            d = """AND l.lesson_date BETWEEN %s AND %s"""
            query += d
            params += [dates['start_date'], dates['end_date']]

        with self.conn.cursor() as cur:
            cur.execute(query, tuple(params))
            return cur.fetchall()
    
    def get_attendance_group_course(self):
        pass

    def get_student_attendance_period(self, payload: AttendancePeriod) -> List[Dict[str, Any]]:
        query = """SELECT a.* FROM attendance as a
                    JOIN lessons as l ON l.id = a.lesson_id
                    WHERE a.student_id=%s AND l.lesson_date BETWEEN %s AND %s
                """
        
        with self.conn.cursor() as cur:
            cur.execute(query, (payload.student_id,
                                payload.start_date,
                                payload.end_date,))
            return cur.fetchall()

    def get_attendance_by_id(self, attendance_id: int) -> None | Dict[str, Any]:
        query = """SELECT * FROM attendance WHERE id=%s"""

        with self.conn.cursor() as cur:
            cur.execute(query, (attendance_id,))
            return cur.fetchone()

    def patch_attendance(self, attendance_id: int, payload: AttendancePatch) -> Dict[str, Any]:
        data = payload.model_dump(exclude_unset=True)

        if not data:
            return {}

        keys = ', '.join([f'{i}=%s' for i in data.keys()])
        query = f"""UPDATE attendance SET {keys} WHERE id=%s
                    RETURNING *
                """

        with self.conn.cursor() as cur:
            cur.execute(query, (*data.values(), attendance_id,))
            return cur.fetchone()

def get_lesson_repo(conn=Depends(get_db)) -> LessonsRepository:
    return LessonsRepository(conn)