import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000'
PASSWORD = 'password123'
USERS = {
    'admin': 'admin@university.test',
    'dean': 'dean@university.test',
    'teacher': 'ivanov.sp@university.test',
    'student': 's01@student.university.test',
}

results = []
tokens = {}


def call(method, path, token=None, json_body=None, form=None, query=None):
    url = BASE + path
    if query:
        url += '?' + urllib.parse.urlencode(query)
    headers = {}
    data = None
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if json_body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(json_body).encode()
    if form is not None:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        data = urllib.parse.urlencode(form).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, raw


def check(tc, title, role, expected, actual, extra_ok=True, note=''):
    passed = actual == expected and extra_ok
    results.append({'id': tc, 'title': title, 'role': role, 'expected': expected,
                    'actual': actual, 'status': 'PASS' if passed else 'FAIL', 'note': note})
    print('{:<6} {:<4} {:<10} ожид. {:<4} факт {:<4} {}'.format(
        tc, 'OK' if passed else 'FAIL', role, expected, actual, title))
    return passed


def login(email, password=PASSWORD):
    return call('POST', '/users/login', form={'username': email, 'password': password})


def fio(u):
    return ' '.join([u['first_name'], u['middle_name'], u['last_name']])


def main():
    for role, email in USERS.items():
        code, body = login(email)
        tokens[role] = body['access_token'] if code == 200 else None
    adm, dean, tch, std = tokens['admin'], tokens['dean'], tokens['teacher'], tokens['student']
    stamp = str(int(time.time()))
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    code, body = login(USERS['admin'])
    check('TC-01', 'Вход с верными email и паролем', 'admin', 200, code,
          code == 200 and body.get('role') == 'admin' and bool(body.get('access_token')))
    code, _ = login(USERS['admin'], 'wrong-password')
    check('TC-02', 'Вход с неверным паролем', 'гость', 401, code)
    code, _ = login('nobody@university.test')
    check('TC-03', 'Вход с несуществующим email', 'гость', 401, code)
    code, _ = call('GET', '/users/me')
    check('TC-04', 'Запрос профиля без токена', 'гость', 401, code)
    code, _ = call('GET', '/users/me', token='abc.def.ghi')
    check('TC-05', 'Запрос с поддельным токеном', 'гость', 401, code)

    me = {}
    for n, role in enumerate(['admin', 'dean', 'teacher', 'student']):
        code, body = call('GET', '/users/me', token=tokens[role])
        me[role] = body
        check('TC-0{}'.format(6 + n), 'Профиль /users/me возвращает роль «{}»'.format(role), role, 200, code,
              code == 200 and body.get('role') == role)

    code, groups = call('GET', '/info/groups')
    check('TC-10', 'Справочник групп доступен без входа (нужен для регистрации)', 'гость', 200, code,
          code == 200 and len(groups) > 0)
    code, _ = call('GET', '/info/roles', token=std)
    check('TC-11', 'Справочник ролей недоступен студенту', 'student', 403, code)

    new_student = {
        'first_name': 'Тест', 'last_name': 'Студентов', 'middle_name': 'Иванович',
        'email': 'autotest{}@mail.ru'.format(stamp), 'phone': '+7999{}'.format(stamp[-7:]),
        'password': 'secret123', 'role_id': 1, 'date_of_birth': '2005-01-01', 'gender': 'М',
        'group_id': groups[0]['id'], 'funding_type': 'бюджет', 'enrollment_date': '2024-09-01',
    }
    code, body = call('POST', '/students/signup', json_body=new_student)
    check('TC-12', 'Регистрация студента; переданный role_id=1 игнорируется', 'гость', 200, code,
          code == 200 and body.get('role_id') == 4, 'выдана роль {}'.format(body.get('role_id') if code == 200 else '-'))
    code, _ = call('POST', '/students/signup', json_body=new_student)
    check('TC-13', 'Повторная регистрация с тем же email', 'гость', 409, code)
    bad = dict(new_student, email='autotest{}b@mail.ru'.format(stamp), phone='12345')
    code, _ = call('POST', '/students/signup', json_body=bad)
    check('TC-14', 'Регистрация с некорректным телефоном', 'гость', 422, code)
    bad = dict(new_student, email='autotest{}c@mail.ru'.format(stamp), phone='+7998{}'.format(stamp[-7:]), group_id=99999)
    code, _ = call('POST', '/students/signup', json_body=bad)
    check('TC-15', 'Регистрация в несуществующую группу', 'гость', 404, code)
    bad = dict(new_student, email='autotest{}d@mail.ru'.format(stamp), phone='+7997{}'.format(stamp[-7:]), password='123')
    code, _ = call('POST', '/students/signup', json_body=bad)
    check('TC-16', 'Регистрация с паролем короче 6 символов', 'гость', 422, code)

    new_teacher = {
        'first_name': 'Тест', 'last_name': 'Преподов', 'middle_name': 'Петрович',
        'email': 'autoteacher{}@mail.ru'.format(stamp), 'phone': '+7996{}'.format(stamp[-7:]),
        'password': 'secret123', 'department_id': 1, 'position': 'доцент', 'degree': 'к.т.н.',
    }
    code, _ = call('POST', '/teachers/signup', json_body=new_teacher)
    check('TC-17', 'Регистрация преподавателя без входа запрещена', 'гость', 401, code)
    code, _ = call('POST', '/teachers/signup', token=std, json_body=new_teacher)
    check('TC-18', 'Студент не может создать преподавателя', 'student', 403, code)
    code, teacher_body = call('POST', '/teachers/signup', token=adm, json_body=new_teacher)
    check('TC-19', 'Администратор создаёт аккаунт преподавателя', 'admin', 200, code,
          code == 200 and teacher_body.get('role_id') == 3)

    code, users = call('GET', '/admin/users', token=adm)
    check('TC-20', 'Администратор видит список всех пользователей с ролями', 'admin', 200, code,
          code == 200 and len(users) >= 42 and all('role_name' in u for u in users))
    code, _ = call('GET', '/admin/users', token=dean)
    check('TC-21', 'Декан не видит панель пользователей', 'dean', 403, code)
    if code_ok(teacher_body):
        tid = teacher_body['id']
        code, body = call('PATCH', '/admin/roles/{}'.format(tid), token=adm, json_body=2)
        check('TC-22', 'Администратор повышает преподавателя до декана', 'admin', 200, code,
              code == 200 and body.get('role_id') == 2 and 'password' not in body)
        call('PATCH', '/admin/roles/{}'.format(tid), token=adm, json_body=3)
        code, _ = call('PATCH', '/admin/roles/{}'.format(tid), token=adm, json_body=4)
        check('TC-23', 'Нельзя сделать студентом пользователя без карточки студента', 'admin', 409, code)
    code, _ = call('PATCH', '/admin/roles/{}'.format(me['admin']['id']), token=adm, json_body=4)
    check('TC-24', 'Нельзя изменить роль администратору', 'admin', 403, code)
    code, _ = call('PATCH', '/admin/roles/{}'.format(me['student']['id']), token=adm, json_body=9)
    check('TC-25', 'Назначение несуществующей роли', 'admin', 422, code)
    code, _ = call('PATCH', '/admin/roles/{}'.format(me['student']['id']), token=dean, json_body=1)
    check('TC-26', 'Декан не может менять роли', 'dean', 403, code)
    code, logs = call('GET', '/admin/logs', token=adm, query={'page': 1, 'per_page': 5})
    check('TC-27', 'Администратор просматривает журнал событий', 'admin', 200, code, code == 200 and len(logs) > 0)
    code, _ = call('GET', '/admin/logs', token=std)
    check('TC-28', 'Студент не видит журнал событий', 'student', 403, code)
    code, _ = call('POST', '/admin/backup', token=adm)
    check('TC-29', 'Администратор запускает резервное копирование', 'admin', 202, code)

    teacher_fio = fio(me['teacher'])
    own = other = None
    for g in groups:
        code, cas = call('GET', '/study/group/{}/course/assignments'.format(g['id']), token=dean)
        if code != 200:
            continue
        for ca in cas:
            if ca['teacher'] == teacher_fio and own is None:
                own = dict(ca, group_id=g['id'])
            if ca['teacher'] != teacher_fio and other is None:
                other = dict(ca, group_id=g['id'])
    code, students = call('GET', '/students/', token=tch)
    own_student = next(s for s in students if s['group_id'] == own['group_id'] and s['status'] == 'числится')
    stranger = next(s for s in students if s['group_id'] != own['group_id'])

    subjects = call('GET', '/info/subjects', token=dean)[1]
    course = {'group_id': own['group_id'], 'subject_id': subjects[0]['id'], 'teacher_id': me['teacher']['id'],
              'term': 1, 'academic_year': '2099/2100'}
    code, ca_body = call('POST', '/study/course/assignments', token=dean, json_body=course)
    check('TC-30', 'Декан назначает дисциплину группе', 'dean', 201, code)
    code, _ = call('POST', '/study/course/assignments', token=dean, json_body=course)
    check('TC-31', 'Повторное назначение той же дисциплины', 'dean', 409, code)
    code, _ = call('POST', '/study/course/assignments', token=tch, json_body=dict(course, term=2))
    check('TC-32', 'Преподаватель не может назначать дисциплины', 'teacher', 403, code)
    if ca_body and 'id' in ca_body:
        call('DELETE', '/study/course/assignments/{}'.format(ca_body['id']), token=dean)

    code, body = call('GET', '/analytics/reports/debtors', token=dean)
    check('TC-33', 'Декан формирует отчёт по должникам', 'dean', 200, code)
    code, _ = call('GET', '/analytics/reports/debtors', token=tch)
    check('TC-34', 'Преподаватель не видит отчёт по должникам', 'teacher', 403, code)
    code, body = call('GET', '/analytics/reports/stats/' + urllib.parse.quote('Группа'), token=dean)
    check('TC-35', 'Декан смотрит статистику успеваемости по группам', 'dean', 200, code, code == 200 and len(body) > 0)

    lesson = {'course_assignment_id': own['id'], 'lesson_type': 'лекция', 'lesson_date': tomorrow,
              'start_time': '09:00:00', 'end_time': '10:30:00', 'room': 'Т-101'}
    code, lesson_body = call('POST', '/study/lessons', token=tch, json_body=lesson)
    check('TC-36', 'Преподаватель создаёт занятие по своей дисциплине', 'teacher', 200, code)
    code, _ = call('POST', '/study/lessons', token=tch, json_body=dict(lesson, course_assignment_id=other['id']))
    check('TC-37', 'Преподаватель не может создать занятие по чужой дисциплине', 'teacher', 403, code)
    code, _ = call('POST', '/study/lessons', token=tch, json_body=dict(lesson, start_time='12:00:00', end_time='11:00:00'))
    check('TC-38', 'Занятие с окончанием раньше начала', 'teacher', 422, code)
    code, _ = call('POST', '/study/lessons', token=std, json_body=lesson)
    check('TC-39', 'Студент не может создавать занятия', 'student', 403, code)
    code, _ = call('PATCH', '/study/lessons/{}'.format(lesson_body.get('id')), token=tch, json_body={})
    check('TC-66', 'Изменение занятия с пустым телом запроса', 'teacher', 400, code)

    lid = lesson_body.get('id') if isinstance(lesson_body, dict) else None
    att = {'lesson_id': lid, 'student_id': own_student['id'], 'status': 'присутствовал'}
    code, _ = call('POST', '/study/attendance', token=tch, json_body=att)
    check('TC-40', 'Преподаватель отмечает посещаемость студента своей группы', 'teacher', 200, code)
    code, _ = call('POST', '/study/attendance', token=tch, json_body=att)
    check('TC-41', 'Повторная отметка того же студента на том же занятии', 'teacher', 409, code)
    code, _ = call('POST', '/study/attendance', token=tch, json_body=dict(att, student_id=stranger['id']))
    check('TC-42', 'Отметка студента из другой группы', 'teacher', 400, code)

    asg = {'course_assignment_id': own['id'], 'title': 'Автотест ' + stamp, 'type': 'лабораторная',
           'coefficient': 1, 'max_grade': 5}
    code, asg_body = call('POST', '/performace/assignments', token=tch, json_body=asg)
    check('TC-43', 'Преподаватель создаёт задание по своей дисциплине', 'teacher', 200, code)
    aid = asg_body.get('id') if isinstance(asg_body, dict) else None
    code, _ = call('POST', '/performace/assignments', token=tch, json_body=dict(asg, course_assignment_id=other['id']))
    check('TC-44', 'Преподаватель не может создать задание по чужой дисциплине', 'teacher', 403, code)
    code, _ = call('DELETE', '/performace/assignments/{}'.format(aid), token=std)
    check('TC-45', 'Студент не может удалить задание', 'student', 403, code)
    code, body = call('GET', '/performace/assignments/{}'.format(aid), token=std)
    check('TC-46', 'Получение задания по id', 'student', 200, code, code == 200 and body.get('id') == aid)

    grade = {'student_id': own_student['id'], 'course_assignment_id': own['id'], 'assignment_id': aid,
             'grade': 5, 'is_final': False, 'submission_id': None}
    code, grade_body = call('POST', '/performace/grades', token=tch, json_body=grade)
    check('TC-47', 'Преподаватель выставляет оценку за задание', 'teacher', 200, code)
    code, _ = call('POST', '/performace/grades', token=tch, json_body=grade)
    check('TC-48', 'Повторная оценка за то же задание', 'teacher', 409, code)
    code, _ = call('POST', '/performace/grades', token=tch, json_body=dict(grade, grade=6))
    check('TC-49', 'Оценка вне шкалы (6)', 'teacher', 422, code)
    code, _ = call('POST', '/performace/grades', token=tch, json_body=dict(grade, course_assignment_id=other['id']))
    check('TC-50', 'Оценка по чужой дисциплине', 'teacher', 403, code)
    code, _ = call('POST', '/performace/grades', token=dean, json_body=grade)
    check('TC-51', 'Декан не выставляет оценки (только преподаватель дисциплины)', 'dean', 403, code)

    if isinstance(grade_body, dict) and 'id' in grade_body:
        call('DELETE', '/performace/grades/{}'.format(grade_body['id']), token=tch)
    code, _ = call('DELETE', '/performace/assignments/{}'.format(aid), token=tch)
    check('TC-52', 'Преподаватель удаляет своё задание', 'teacher', 200, code)
    code, _ = call('DELETE', '/study/lessons/{}'.format(lid), token=tch)
    check('TC-53', 'Преподаватель удаляет своё занятие', 'teacher', 200, code)

    sid = me['student']['id']
    other_sid = next(s['id'] for s in students if s['id'] != sid)
    code, body = call('GET', '/students/{}'.format(sid), token=std)
    check('TC-54', 'Студент получает свою карточку с группой', 'student', 200, code, code == 200 and body.get('group_id'))
    gid = body.get('group_id') if isinstance(body, dict) else 0
    code, _ = call('GET', '/students/{}'.format(other_sid), token=std)
    check('TC-55', 'Студент не видит карточку другого студента', 'student', 403, code)
    code, body = call('GET', '/study/lessons/groups/{}'.format(gid), token=std,
                      query={'start_date': '2026-01-01', 'end_date': '2026-12-31'})
    check('TC-56', 'Студент видит расписание своей группы за период', 'student', 200, code, code == 200 and len(body) > 0)
    code, body = call('GET', '/analytics/reports/student-summary/{}'.format(sid), token=std)
    check('TC-57', 'Студент видит свою сводную ведомость', 'student', 200, code, code == 200 and len(body) > 0)
    code, _ = call('GET', '/analytics/reports/student-summary/{}'.format(other_sid), token=std)
    check('TC-58', 'Студент не видит чужую ведомость', 'student', 403, code)
    code, body = call('GET', '/performace/students/{}/gpa'.format(sid), token=std)
    check('TC-59', 'Студент видит свой средний балл', 'student', 200, code, code == 200 and body.get('gpa', 0) > 0)
    code, body = call('GET', '/study/attendance', token=std,
                      query={'student_id': sid, 'start_date': '2026-01-01', 'end_date': '2026-12-31'})
    check('TC-60', 'Студент видит свою посещаемость', 'student', 200, code, code == 200 and len(body) > 0)
    code, _ = call('GET', '/study/attendance', token=std, query={'student_id': other_sid})
    check('TC-61', 'Студент не видит чужую посещаемость', 'student', 403, code)
    code, _ = call('GET', '/students/', token=std)
    check('TC-62', 'Студент не видит общий список студентов', 'student', 403, code)

    code, body = call('PATCH', '/users/me', token=dean, json_body={'middle_name': me['dean']['middle_name']})
    check('TC-63', 'Декан редактирует свой профиль', 'dean', 200, code)
    code, body = call('PATCH', '/users/me', token=std, json_body={'phone': '+7 (930) 000-00-01'})
    check('TC-64', 'Студент меняет телефон в профиле', 'student', 200, code)
    call('PATCH', '/users/me', token=std, json_body={'phone': me['student']['phone']})
    new_tok = login(new_student['email'], new_student['password'])[1].get('access_token')
    code, _ = call('PATCH', '/users/me', token=new_tok, json_body={'email': 'renamed{}@mail.ru'.format(stamp)})
    check('TC-65', 'Профиль: email меняется, токен остаётся рабочим', 'student', 200, code,
          call('GET', '/users/me', token=new_tok)[0] == 200)

    with open('tests/api_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    passed = sum(r['status'] == 'PASS' for r in results)
    print('\nИтого: {} из {} пройдено'.format(passed, len(results)))
    return 0 if passed == len(results) else 1


def code_ok(body):
    return isinstance(body, dict) and 'id' in body


if __name__ == '__main__':
    sys.exit(main())
