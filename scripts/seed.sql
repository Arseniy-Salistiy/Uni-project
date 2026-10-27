-- =====================================================================
-- Тестовые данные (DML). Запускается при старте приложения.
-- Идемпотентен: если данные уже есть (roles/users не пусты) - ничего не делает.
-- Таблицы submissions и attachments не затрагиваются.
--
-- Объём: 4 роли, 5 кафедр, 4 направления, 1 админ, 1 декан,
--        10 преподавателей, 5 групп, 30 студентов, 15 дисциплин,
--        30 назначений дисциплин, 240 занятий, ~1300 записей посещаемости,
--        90 заданий, ~670 оценок.
-- Пароль всех тестовых пользователей: password123 (bcrypt, см. ниже).
-- =====================================================================

ALTER TABLE ROLES DISABLE TRIGGER ALL;
ALTER TABLE DEPARTMENTS DISABLE TRIGGER ALL;
ALTER TABLE MAJORS DISABLE TRIGGER ALL;
ALTER TABLE USERS DISABLE TRIGGER ALL;
ALTER TABLE TEACHERS DISABLE TRIGGER ALL;
ALTER TABLE GROUPS DISABLE TRIGGER ALL;
ALTER TABLE STUDENTS DISABLE TRIGGER ALL; -- Блокируем триггер здесь
ALTER TABLE SUBJECTS DISABLE TRIGGER ALL;
ALTER TABLE COURSE_ASSIGNMENTS DISABLE TRIGGER ALL;
ALTER TABLE LESSONS DISABLE TRIGGER ALL;
ALTER TABLE ATTENDANCE DISABLE TRIGGER ALL;
ALTER TABLE ASSIGNMENTS DISABLE TRIGGER ALL;
ALTER TABLE GRADES DISABLE TRIGGER ALL;
ALTER TABLE SUBMISSIONS DISABLE TRIGGER ALL;
ALTER TABLE ATTACHMENTS DISABLE TRIGGER ALL;

DO $seed$
DECLARE
  v_pwd TEXT;
BEGIN
  IF EXISTS (SELECT 1 FROM roles) OR EXISTS (SELECT 1 FROM users) THEN
    RAISE NOTICE 'Seed skipped: data already present';
    RETURN;
  END IF;

  -- ---------------------------------------------------------------
  -- Пароль: bcrypt через pgcrypto ($2a$ совместим со Spring BCrypt).
  -- Если расширение недоступно - подставьте готовый bcrypt-хеш вместо заглушки.
  -- ---------------------------------------------------------------
  BEGIN
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    v_pwd := crypt('password123', gen_salt('bf', 10));
  EXCEPTION WHEN OTHERS THEN
    v_pwd := 'REPLACE_WITH_BCRYPT_HASH';
  END;

  -- ---------------------------------------------------------------
  -- ROLES: admin=1, dean=2, teacher=3, student=4
  -- ---------------------------------------------------------------
  INSERT INTO roles (id, name) OVERRIDING SYSTEM VALUE VALUES
    (1, 'ADMIN'),
    (2, 'DEAN'),
    (3, 'TEACHER'),
    (4, 'STUDENT');
  PERFORM setval(pg_get_serial_sequence('roles', 'id'), 4);

  -- ---------------------------------------------------------------
  -- DEPARTMENTS (FACULTY уникален, поэтому у каждой кафедры свой факультет)
  -- ---------------------------------------------------------------
  INSERT INTO departments (name, faculty) VALUES
    ('Кафедра программной инженерии', 'Факультет информационных технологий'),
    ('Кафедра высшей математики',     'Факультет математики и механики'),
    ('Кафедра экономической теории',  'Экономический факультет'),
    ('Кафедра иностранных языков',    'Факультет лингвистики'),
    ('Кафедра общей физики',          'Физический факультет');

  -- ---------------------------------------------------------------
  -- MAJORS
  -- ---------------------------------------------------------------
  INSERT INTO majors (name, code) VALUES
    ('Программная инженерия',                  '09.03.04'),
    ('Информатика и вычислительная техника',   '09.03.01'),
    ('Прикладная математика и информатика',    '01.03.02'),
    ('Экономика',                              '38.03.01');

  -- ---------------------------------------------------------------
  -- USERS: admin и dean
  -- ---------------------------------------------------------------
  INSERT INTO users (first_name, last_name, middle_name, email, phone, password, role_id) VALUES
    ('Игорь',   'Петров',  'Васильевич',   'admin@university.test', '9200000001', v_pwd, 1),
    ('Николай', 'Фёдоров', 'Александрович','dean@university.test',  '9200000002', v_pwd, 2);

  -- ---------------------------------------------------------------
  -- Преподаватели (10)
  -- ---------------------------------------------------------------
  CREATE TEMP TABLE tmp_teachers (
    n INT, last_name TEXT, first_name TEXT, middle_name TEXT,
    email TEXT, dept TEXT, position TEXT, degree TEXT
  ) ON COMMIT DROP;

  INSERT INTO tmp_teachers VALUES
    (1,  'Иванов',   'Сергей',   'Петрович',    'ivanov.sp@university.test',   'Кафедра программной инженерии', 'доцент',                'к.т.н.'),
    (2,  'Смирнова', 'Елена',    'Викторовна',  'smirnova.ev@university.test', 'Кафедра программной инженерии', 'профессор',             'д.т.н.'),
    (3,  'Кузнецов', 'Андрей',   'Николаевич',  'kuznetsov.an@university.test','Кафедра высшей математики',     'доцент',                'к.ф.-м.н.'),
    (4,  'Попова',   'Марина',   'Алексеевна',  'popova.ma@university.test',   'Кафедра высшей математики',     'доцент',                'к.ф.-м.н.'),
    (5,  'Соколов',  'Дмитрий',  'Игоревич',    'sokolov.di@university.test',  'Кафедра экономической теории',  'профессор',             'д.э.н.'),
    (6,  'Лебедева', 'Ольга',    'Сергеевна',   'lebedeva.os@university.test', 'Кафедра экономической теории',  'доцент',                'к.э.н.'),
    (7,  'Морозов',  'Павел',    'Андреевич',   'morozov.pa@university.test',  'Кафедра иностранных языков',    'старший преподаватель', 'к.филол.н.'),
    (8,  'Новикова', 'Татьяна',  'Юрьевна',     'novikova.tyu@university.test','Кафедра иностранных языков',    'старший преподаватель', NULL),
    (9,  'Волков',   'Алексей',  'Михайлович',  'volkov.am@university.test',   'Кафедра общей физики',          'профессор',             'д.ф.-м.н.'),
    (10, 'Зайцева',  'Наталья',  'Олеговна',    'zaitseva.no@university.test', 'Кафедра общей физики',          'доцент',                'к.ф.-м.н.');

  INSERT INTO users (first_name, last_name, middle_name, email, phone, password, role_id)
  SELECT first_name, last_name, middle_name, email,
         '91000000' || lpad(n::text, 2, '0'), v_pwd, 3
  FROM tmp_teachers
  ORDER BY n;

  INSERT INTO teachers (user_id, department_id, position, degree)
  SELECT u.id, d.id, t.position, t.degree
  FROM tmp_teachers t
  JOIN users u       ON u.email = t.email
  JOIN departments d ON d.name  = t.dept;

  -- ---------------------------------------------------------------
  -- Студенты (30) - сначала во временную таблицу
  -- ---------------------------------------------------------------
  CREATE TEMP TABLE tmp_students (
    n INT, last_name TEXT, first_name TEXT, middle_name TEXT,
    gender gender, dob DATE, group_name TEXT,
    funding funding_type, status student_status
  ) ON COMMIT DROP;

  INSERT INTO tmp_students VALUES
    -- ПИ-231
    (1,  'Алексеев',  'Максим',     'Олегович',      'М', '2004-03-14', 'ПИ-231',  'бюджет',  'числится'),
    (2,  'Борисова',  'Анна',       'Дмитриевна',    'Ж', '2004-07-22', 'ПИ-231',  'бюджет',  'числится'),
    (3,  'Васильев',  'Кирилл',     'Сергеевич',     'М', '2004-11-05', 'ПИ-231',  'платное', 'числится'),
    (4,  'Григорьева','Мария',      'Андреевна',     'Ж', '2004-01-30', 'ПИ-231',  'бюджет',  'числится'),
    (5,  'Денисов',   'Артём',      'Владимирович',  'М', '2003-12-19', 'ПИ-231',  'платное', 'академический отпуск'),
    (6,  'Ершова',    'Дарья',      'Павловна',      'Ж', '2004-05-09', 'ПИ-231',  'бюджет',  'числится'),
    -- ПИ-241
    (7,  'Жуков',     'Илья',       'Александрович', 'М', '2005-02-11', 'ПИ-241',  'бюджет',  'числится'),
    (8,  'Захарова',  'Полина',     'Игоревна',      'Ж', '2005-09-03', 'ПИ-241',  'бюджет',  'числится'),
    (9,  'Исаев',     'Роман',      'Евгеньевич',    'М', '2005-04-27', 'ПИ-241',  'платное', 'числится'),
    (10, 'Ковалёва',  'София',      'Максимовна',    'Ж', '2005-08-16', 'ПИ-241',  'бюджет',  'числится'),
    (11, 'Лазарев',   'Тимур',      'Русланович',    'М', '2005-06-01', 'ПИ-241',  'бюджет',  'числится'),
    (12, 'Миронова',  'Екатерина',  'Ильинична',     'Ж', '2005-10-21', 'ПИ-241',  'платное', 'числится'),
    -- ИВТ-241
    (13, 'Никитин',   'Георгий',    'Данилович',     'М', '2005-01-17', 'ИВТ-241', 'бюджет',  'числится'),
    (14, 'Орлова',    'Виктория',   'Романовна',     'Ж', '2005-03-25', 'ИВТ-241', 'бюджет',  'числится'),
    (15, 'Павлов',    'Егор',       'Артёмович',     'М', '2005-07-08', 'ИВТ-241', 'платное', 'числится'),
    (16, 'Романова',  'Алиса',      'Кирилловна',    'Ж', '2005-11-12', 'ИВТ-241', 'бюджет',  'числится'),
    (17, 'Степанов',  'Никита',     'Олегович',      'М', '2004-12-02', 'ИВТ-241', 'бюджет',  'числится'),
    (18, 'Титова',    'Ксения',     'Алексеевна',    'Ж', '2005-05-30', 'ИВТ-241', 'платное', 'числится'),
    -- ПМИ-251
    (19, 'Ушаков',    'Матвей',     'Денисович',     'М', '2006-02-14', 'ПМИ-251', 'бюджет',  'числится'),
    (20, 'Фролова',   'Анастасия',  'Сергеевна',     'Ж', '2006-06-18', 'ПМИ-251', 'бюджет',  'числится'),
    (21, 'Харитонов', 'Даниил',     'Павлович',      'М', '2006-09-09', 'ПМИ-251', 'бюджет',  'числится'),
    (22, 'Цветкова',  'Валерия',    'Николаевна',    'Ж', '2006-04-04', 'ПМИ-251', 'платное', 'числится'),
    (23, 'Чернов',    'Владислав',  'Игоревич',      'М', '2006-01-23', 'ПМИ-251', 'бюджет',  'числится'),
    (24, 'Шарова',    'Юлия',       'Андреевна',     'Ж', '2006-12-07', 'ПМИ-251', 'бюджет',  'числится'),
    -- ЭК-251
    (25, 'Щербаков',  'Антон',      'Валерьевич',    'М', '2006-03-03', 'ЭК-251',  'платное', 'числится'),
    (26, 'Юдина',     'Алёна',      'Витальевна',    'Ж', '2006-08-28', 'ЭК-251',  'платное', 'числится'),
    (27, 'Яковлев',   'Константин', 'Петрович',      'М', '2005-10-10', 'ЭК-251',  'бюджет',  'числится'),
    (28, 'Белова',    'Ирина',      'Михайловна',    'Ж', '2006-05-15', 'ЭК-251',  'платное', 'числится'),
    (29, 'Гусев',     'Фёдор',      'Николаевич',    'М', '2006-07-31', 'ЭК-251',  'бюджет',  'числится'),
    (30, 'Дроздова',  'Вера',       'Леонидовна',    'Ж', '2006-11-19', 'ЭК-251',  'платное', 'отчислен');

  INSERT INTO users (first_name, last_name, middle_name, email, phone, password, role_id)
  SELECT first_name, last_name, middle_name,
         's' || lpad(n::text, 2, '0') || '@student.university.test',
         '93000000' || lpad(n::text, 2, '0'),
         v_pwd, 4
  FROM tmp_students
  ORDER BY n;

  -- ---------------------------------------------------------------
  -- GROUPS (кураторы - преподаватели)
  -- ---------------------------------------------------------------
  INSERT INTO groups (name, major_id, year, education_form, enrollment_year, supervisor_id)
  SELECT v.name, m.id, v.year, v.form::education_form, v.ey, u.id
  FROM (VALUES
    ('ПИ-231',  'Программная инженерия',                 4, 'очное',        2023, 'ivanov.sp@university.test'),
    ('ПИ-241',  'Программная инженерия',                 3, 'очное',        2024, 'smirnova.ev@university.test'),
    ('ИВТ-241', 'Информатика и вычислительная техника',  3, 'очное',        2024, 'kuznetsov.an@university.test'),
    ('ПМИ-251', 'Прикладная математика и информатика',   2, 'очное',        2025, 'popova.ma@university.test'),
    ('ЭК-251',  'Экономика',                             2, 'очно-заочное', 2025, 'lebedeva.os@university.test')
  ) AS v(name, major, year, form, ey, sup_email)
  JOIN majors m ON m.name  = v.major
  JOIN users  u ON u.email = v.sup_email;

  -- ---------------------------------------------------------------
  -- STUDENTS
  -- ---------------------------------------------------------------
  INSERT INTO students (user_id, date_of_birth, gender, group_id, funding_type, status, enrollment_date)
  SELECT u.id, t.dob, t.gender, g.id, t.funding, t.status,
         make_date(g.enrollment_year, 9, 1)
  FROM tmp_students t
  JOIN users  u ON u.email = 's' || lpad(t.n::text, 2, '0') || '@student.university.test'
  JOIN groups g ON g.name  = t.group_name;

  -- ---------------------------------------------------------------
  -- SUBJECTS (15)
  -- ---------------------------------------------------------------
  INSERT INTO subjects (name, description, hours_lectures, hours_seminars, hours_labs, control_form, department_id)
  SELECT v.name, v.descr, v.hl, v.hs, v.hb, v.ctrl::control_form_t, d.id
  FROM (VALUES
    ('Программирование на Java',            'Объектно-ориентированное программирование на Java',          34,  0, 51, 'экзамен',                 'Кафедра программной инженерии'),
    ('Базы данных',                         'Реляционные БД, SQL, проектирование схем',                   34, 17, 34, 'экзамен',                 'Кафедра программной инженерии'),
    ('Веб-разработка',                      'Клиент-серверные приложения и REST API',                     34,  0, 51, 'курсовая',                'Кафедра программной инженерии'),
    ('Алгоритмы и структуры данных',        'Базовые алгоритмы, оценка сложности, структуры данных',      34, 17, 34, 'экзамен',                 'Кафедра программной инженерии'),
    ('Тестирование программного обеспечения','Методы и инструменты тестирования ПО',                      17,  0, 34, 'дифференцированный зачёт','Кафедра программной инженерии'),
    ('Математический анализ',               'Пределы, ряды, дифференциальное и интегральное исчисление',  51, 34,  0, 'экзамен',                 'Кафедра высшей математики'),
    ('Линейная алгебра',                    'Матрицы, системы уравнений, векторные пространства',         34, 34,  0, 'экзамен',                 'Кафедра высшей математики'),
    ('Теория вероятностей и статистика',    'Случайные величины, распределения, статистические выводы',   34, 17,  0, 'зачёт',                   'Кафедра высшей математики'),
    ('Дискретная математика',               'Логика, комбинаторика, теория графов',                       34, 17,  0, 'экзамен',                 'Кафедра высшей математики'),
    ('Микроэкономика',                      'Поведение потребителей и фирм, рыночные структуры',          34, 17,  0, 'экзамен',                 'Кафедра экономической теории'),
    ('Финансовый учёт',                     'Основы бухгалтерского и финансового учёта',                  34, 17,  0, 'дифференцированный зачёт','Кафедра экономической теории'),
    ('Менеджмент',                          'Основы управления организацией',                             17, 17,  0, 'зачёт',                   'Кафедра экономической теории'),
    ('Английский язык',                     'Профессиональный английский язык',                            0, 51,  0, 'зачёт',                   'Кафедра иностранных языков'),
    ('Деловые коммуникации',                'Деловая переписка и переговоры',                             17, 17,  0, 'зачёт',                   'Кафедра иностранных языков'),
    ('Физика',                              'Механика, электричество и магнетизм, оптика',                34, 17, 34, 'экзамен',                 'Кафедра общей физики')
  ) AS v(name, descr, hl, hs, hb, ctrl, dept)
  JOIN departments d ON d.name = v.dept;

  -- ---------------------------------------------------------------
  -- COURSE_ASSIGNMENTS: весенний семестр 2025/2026
  -- term = 2 * (2026 - enrollment_year); преподаватель - с кафедры дисциплины
  -- ---------------------------------------------------------------
  INSERT INTO course_assignments (group_id, subject_id, teacher_id, term, academic_year)
  SELECT g.id, s.id, t.user_id, 2 * (2026 - g.enrollment_year), '2025/2026'
  FROM (VALUES
    ('ПИ-231',  'Программирование на Java'),
    ('ПИ-231',  'Базы данных'),
    ('ПИ-231',  'Веб-разработка'),
    ('ПИ-231',  'Тестирование программного обеспечения'),
    ('ПИ-231',  'Менеджмент'),
    ('ПИ-231',  'Деловые коммуникации'),

    ('ПИ-241',  'Базы данных'),
    ('ПИ-241',  'Алгоритмы и структуры данных'),
    ('ПИ-241',  'Дискретная математика'),
    ('ПИ-241',  'Теория вероятностей и статистика'),
    ('ПИ-241',  'Английский язык'),
    ('ПИ-241',  'Физика'),

    ('ИВТ-241', 'Программирование на Java'),
    ('ИВТ-241', 'Алгоритмы и структуры данных'),
    ('ИВТ-241', 'Линейная алгебра'),
    ('ИВТ-241', 'Теория вероятностей и статистика'),
    ('ИВТ-241', 'Физика'),
    ('ИВТ-241', 'Английский язык'),

    ('ПМИ-251', 'Математический анализ'),
    ('ПМИ-251', 'Линейная алгебра'),
    ('ПМИ-251', 'Дискретная математика'),
    ('ПМИ-251', 'Программирование на Java'),
    ('ПМИ-251', 'Физика'),
    ('ПМИ-251', 'Английский язык'),

    ('ЭК-251',  'Микроэкономика'),
    ('ЭК-251',  'Финансовый учёт'),
    ('ЭК-251',  'Менеджмент'),
    ('ЭК-251',  'Математический анализ'),
    ('ЭК-251',  'Теория вероятностей и статистика'),
    ('ЭК-251',  'Деловые коммуникации')
  ) AS v(group_name, subject_name)
  JOIN groups   g ON g.name = v.group_name
  JOIN subjects s ON s.name = v.subject_name
  CROSS JOIN LATERAL (
    SELECT tt.user_id
    FROM teachers tt
    WHERE tt.department_id = s.department_id
    ORDER BY tt.user_id
    OFFSET ((g.id + s.id) % 2) LIMIT 1
  ) t;

  -- ---------------------------------------------------------------
  -- LESSONS: 8 занятий на каждое назначение, февраль-апрель 2026
  -- ---------------------------------------------------------------
  INSERT INTO lessons (course_assignment_id, lesson_type, lesson_date, start_time, end_time, room)
  SELECT ca.id,
         (CASE
            WHEN s.hours_lectures > 0
                 AND (n % 2 = 1 OR (s.hours_labs = 0 AND s.hours_seminars = 0)) THEN 'лекция'
            WHEN s.hours_labs > 0      THEN 'лабораторная'
            WHEN s.hours_seminars > 0  THEN 'семинар'
            ELSE 'практика'
          END)::lesson_type_t,
         DATE '2026-02-09' + (n - 1) * 7 + (ca.id % 5),
         x.st,
         x.st + INTERVAL '1 hour 30 minutes',
         'А-' || (100 + ca.id % 20)::text
  FROM course_assignments ca
  JOIN subjects s ON s.id = ca.subject_id
  CROSS JOIN generate_series(1, 8) AS n
  CROSS JOIN LATERAL (
    SELECT ((ARRAY['09:00', '10:45', '12:30', '14:15'])[1 + ca.id % 4])::time AS st
  ) x;

  -- ---------------------------------------------------------------
  -- ATTENDANCE: только для студентов со статусом 'числится'
  -- ---------------------------------------------------------------
  INSERT INTO attendance (lesson_id, student_id, status)
  SELECT l.id, st.user_id,
         (CASE abs(hashtext(l.id::text || '-' || st.user_id::text)::bigint) % 20
            WHEN 0 THEN 'отсутствовал'
            WHEN 1 THEN 'отсутствовал'
            WHEN 2 THEN 'опоздал'
            WHEN 3 THEN 'уважительная причина'
            ELSE 'присутствовал'
          END)::attendance_t
  FROM lessons l
  JOIN course_assignments ca ON ca.id = l.course_assignment_id
  JOIN students st ON st.group_id = ca.group_id AND st.status = 'числится';

  -- ---------------------------------------------------------------
  -- ASSIGNMENTS: 3 задания на каждое назначение (шкала 1-5)
  -- ---------------------------------------------------------------
  INSERT INTO assignments (course_assignment_id, title, type, coefficient, max_grade)
  SELECT ca.id, a.title, a.atype::assignment_t, a.coef, 5
  FROM course_assignments ca
  JOIN subjects s ON s.id = ca.subject_id
  CROSS JOIN LATERAL (VALUES
    ('Лабораторная работа №1', 'лабораторная', 1.00),
    ('Контрольная работа №1',  'контрольная',  1.50),
    (CASE WHEN s.control_form = 'курсовая' THEN 'Курсовая работа' ELSE 'Реферат' END,
     CASE WHEN s.control_form = 'курсовая' THEN 'курсовая'        ELSE 'реферат' END,
     CASE WHEN s.control_form = 'курсовая' THEN 2.00              ELSE 0.50 END)
  ) AS a(title, atype, coef);

  -- ---------------------------------------------------------------
  -- GRADES (текущие): каждый действующий студент по каждому заданию группы
  -- ---------------------------------------------------------------
  INSERT INTO grades (student_id, course_assignment_id, assignment_id, grade, graded_by, graded_at, is_final)
  SELECT st.user_id, ca.id, a.id,
         (CASE
            WHEN x.m = 0 THEN 2.0
            WHEN x.m < 3 THEN 3.0
            WHEN x.m < 7 THEN 4.0
            ELSE 5.0
          END)::numeric(3,1),
         ca.teacher_id,
         TIMESTAMP '2026-03-01 10:00'
           + (x.h % 80) * INTERVAL '1 day'
           + (x.h % 8)  * INTERVAL '1 hour',
         false
  FROM assignments a
  JOIN course_assignments ca ON ca.id = a.course_assignment_id
  JOIN students st ON st.group_id = ca.group_id AND st.status = 'числится'
  CROSS JOIN LATERAL (
    SELECT (abs(hashtext(st.user_id::text || '-' || a.id::text)::bigint) % 1000)::int AS h,
           (abs(hashtext(st.user_id::text || '-' || a.id::text)::bigint) % 10)::int   AS m
  ) x;

  -- ---------------------------------------------------------------
  -- GRADES (итоговые): взвешенное среднее по коэффициентам заданий
  -- ---------------------------------------------------------------
  INSERT INTO grades (student_id, course_assignment_id, assignment_id, grade, graded_by, graded_at, is_final)
  SELECT g.student_id,
         g.course_assignment_id,
         NULL::int,
         LEAST(5, GREATEST(2, ROUND(SUM(g.grade * a.coefficient) / SUM(a.coefficient))))::numeric(3,1),
         ca.teacher_id,
         TIMESTAMP '2026-06-15 12:00' + (g.student_id % 10) * INTERVAL '1 day',
         true
  FROM grades g
  JOIN assignments a         ON a.id  = g.assignment_id
  JOIN course_assignments ca ON ca.id = g.course_assignment_id
  WHERE g.is_final = false
  GROUP BY g.student_id, g.course_assignment_id, ca.teacher_id;

  RAISE NOTICE 'Seed completed';
END
$seed$ LANGUAGE plpgsql;
ALTER TABLE ROLES ENABLE TRIGGER ALL;
ALTER TABLE DEPARTMENTS ENABLE TRIGGER ALL;
ALTER TABLE MAJORS ENABLE TRIGGER ALL;
ALTER TABLE USERS ENABLE TRIGGER ALL;
ALTER TABLE TEACHERS ENABLE TRIGGER ALL;
ALTER TABLE GROUPS ENABLE TRIGGER ALL;
ALTER TABLE STUDENTS ENABLE TRIGGER ALL; -- Возвращаем триггер в рабочее состояние
ALTER TABLE SUBJECTS ENABLE TRIGGER ALL;
ALTER TABLE COURSE_ASSIGNMENTS ENABLE TRIGGER ALL;
ALTER TABLE LESSONS ENABLE TRIGGER ALL;
ALTER TABLE ATTENDANCE ENABLE TRIGGER ALL;
ALTER TABLE ASSIGNMENTS ENABLE TRIGGER ALL;
ALTER TABLE GRADES ENABLE TRIGGER ALL;
ALTER TABLE SUBMISSIONS ENABLE TRIGGER ALL;
ALTER TABLE ATTACHMENTS ENABLE TRIGGER ALL;