import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "database": "autoschool_db",
    "user": "root",
    "password": ""
}


class Database:
    def __init__(self):
        self.config = DB_CONFIG

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def init_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS Roles (
                id_role INT AUTO_INCREMENT PRIMARY KEY,
                role_name VARCHAR(50) NOT NULL UNIQUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Users (
                id_user INT AUTO_INCREMENT PRIMARY KEY,
                login VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                id_role INT,
                fio VARCHAR(150) NOT NULL,
                FOREIGN KEY (id_role) REFERENCES Roles(id_role) ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Branches (
                id_branch INT AUTO_INCREMENT PRIMARY KEY,
                address VARCHAR(255) NOT NULL,
                phone VARCHAR(20)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Instructors (
                id_instructor INT AUTO_INCREMENT PRIMARY KEY,
                fio VARCHAR(150) NOT NULL,
                phone VARCHAR(20),
                experience_years INT CHECK (experience_years >= 0)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Cars (
                id_car INT AUTO_INCREMENT PRIMARY KEY,
                model VARCHAR(100) NOT NULL,
                gov_number VARCHAR(20) NOT NULL UNIQUE,
                transmission_type VARCHAR(10) CHECK (transmission_type IN ('МКПП', 'АКПП'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS StudyGroups (
                id_group INT AUTO_INCREMENT PRIMARY KEY,
                group_name VARCHAR(50) NOT NULL UNIQUE,
                category VARCHAR(2) CHECK (category IN ('A', 'B', 'C', 'D')),
                id_instructor INT,
                id_car INT,
                start_date DATE NOT NULL,
                base_price DECIMAL(10, 2) NOT NULL CHECK (base_price >= 0),
                FOREIGN KEY (id_instructor) REFERENCES Instructors(id_instructor) ON DELETE SET NULL,
                FOREIGN KEY (id_car) REFERENCES Cars(id_car) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Students (
                id_student INT AUTO_INCREMENT PRIMARY KEY,
                fio VARCHAR(150) NOT NULL,
                phone VARCHAR(20),
                passport_data VARCHAR(50),
                id_group INT,
                FOREIGN KEY (id_group) REFERENCES StudyGroups(id_group) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Discounts (
                id_discount INT AUTO_INCREMENT PRIMARY KEY,
                discount_name VARCHAR(100) NOT NULL,
                percentage INT CHECK (percentage >= 0 AND percentage <= 100),
                is_active BOOLEAN DEFAULT TRUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS DrivingLessons (
                id_lesson INT AUTO_INCREMENT PRIMARY KEY,
                id_student INT,
                lesson_date DATE NOT NULL,
                lesson_time TIME NOT NULL,
                hours_count INT DEFAULT 2,
                status VARCHAR(20) DEFAULT 'Запланировано',
                FOREIGN KEY (id_student) REFERENCES Students(id_student) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS Payments (
                id_payment INT AUTO_INCREMENT PRIMARY KEY,
                id_student INT,
                amount DECIMAL(10, 2) NOT NULL,
                payment_date DATE NOT NULL,
                id_discount INT,
                payment_status VARCHAR(20),
                FOREIGN KEY (id_student) REFERENCES Students(id_student) ON DELETE CASCADE,
                FOREIGN KEY (id_discount) REFERENCES Discounts(id_discount) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        ]

        conn = self.get_connection()
        cur = conn.cursor()
        for q in queries:
            cur.execute(q)

        cur.execute("SELECT COUNT(*) FROM Roles;")
        (roles_count,) = cur.fetchone()
        if roles_count == 0:
            cur.execute("INSERT INTO Roles (role_name) VALUES ('Администратор'), ('Менеджер');")
            cur.execute("INSERT INTO Users (login, password_hash, id_role, fio) VALUES ('admin1', 'admin123', 1, 'Столяров А.С.');")
            cur.execute("INSERT INTO Users (login, password_hash, id_role, fio) VALUES ('admin2', 'admin123', 1, 'Нечаев А.Д.');")
            cur.execute("INSERT INTO Users (login, password_hash, id_role, fio) VALUES ('user', 'user123', 2, 'Козлова Е.П.');")
            cur.execute("INSERT INTO Instructors (fio, phone, experience_years) VALUES ('Петров Сергей Иванович', '+79001112233', 12);")
            cur.execute("INSERT INTO Cars (model, gov_number, transmission_type) VALUES ('Hyundai Solaris', 'А123ВС44', 'МКПП');")
            cur.execute("INSERT INTO StudyGroups (group_name, category, id_instructor, id_car, start_date, base_price) VALUES ('Группа Б-101', 'B', 1, 1, '2026-11-01', 35000);")
            cur.execute("INSERT INTO Discounts (discount_name, percentage, is_active) VALUES ('Студенческая', 10, TRUE), ('Приведи друга', 15, TRUE);")
            cur.execute("INSERT INTO Students (fio, phone, passport_data, id_group) VALUES ('Соколов Дмитрий Андреевич', '+79105554433', '3418 654321', 1);")

        conn.commit()
        cur.close()
        conn.close()
    def check_auth(self, login, password):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_role, fio FROM Users WHERE login = %s AND password_hash = %s;", (login, password))
        res = cur.fetchone()
        cur.close()
        conn.close()
        return res

    def register_user(self, fio, login, password):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Users WHERE login = %s;", (login,))
        (cnt,) = cur.fetchone()
        if cnt > 0:
            cur.close()
            conn.close()
            return False, "Пользователь с таким логином уже существует!"

        cur.execute(
            "INSERT INTO Users (login, password_hash, id_role, fio) VALUES (%s, %s, 2, %s);",
            (login, password, fio)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, "Регистрация прошла успешно! Теперь вы можете войти."

    def get_all_students(self):
        conn = self.get_connection()
        cur = conn.cursor()
        query = """
            SELECT s.id_student, s.fio, s.phone, s.passport_data, COALESCE(g.group_name, 'Без группы'), s.id_group
            FROM Students s
            LEFT JOIN StudyGroups g ON s.id_group = g.id_group
            ORDER BY s.id_student ASC;
        """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def get_groups_list(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_group, group_name, base_price FROM StudyGroups;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def add_student(self, fio, phone, passport, group_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Students (fio, phone, passport_data, id_group) VALUES (%s, %s, %s, %s);",
            (fio, phone, passport, group_id)
        )
        conn.commit()
        cur.close()
        conn.close()

    def update_student(self, student_id, fio, phone, passport, group_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE Students SET fio = %s, phone = %s, passport_data = %s, id_group = %s WHERE id_student = %s;",
            (fio, phone, passport, group_id, student_id)
        )
        conn.commit()
        cur.close()
        conn.close()

    def delete_student(self, student_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM Students WHERE id_student = %s;", (student_id,))
        conn.commit()
        cur.close()
        conn.close()

    def get_active_discounts(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_discount, discount_name, percentage FROM Discounts WHERE is_active = TRUE;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def register_payment_with_discount(self, student_id, final_amount, discount_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Payments (id_student, amount, payment_date, id_discount, payment_status) VALUES (%s, %s, CURDATE(), %s, 'Оплачено');",
            (student_id, final_amount, discount_id)
        )
        conn.commit()
        cur.close()
        conn.close()

    def schedule_lesson_safe(self, student_id, date_str, time_str):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT g.id_instructor FROM Students s
            JOIN StudyGroups g ON s.id_group = g.id_group
            WHERE s.id_student = %s;
        """, (student_id,))
        res = cur.fetchone()
        if not res:
            cur.close()
            conn.close()
            return False, "Студент не прикреплен к группе с инструктором!"

        (instructor_id,) = res
        if not instructor_id:
            cur.close()
            conn.close()
            return False, "За группой не закреплен инструктор!"

        cur.execute("""
            SELECT COUNT(*) FROM DrivingLessons dl
            JOIN Students s ON dl.id_student = s.id_student
            JOIN StudyGroups g ON s.id_group = g.id_group
            WHERE g.id_instructor = %s AND dl.lesson_date = %s AND dl.lesson_time = %s AND dl.status != 'Отменено';
        """, (instructor_id, date_str, time_str))
        
        (conflicts,) = cur.fetchone()
        if conflicts > 0:
            cur.close()
            conn.close()
            return False, "Отказ: У инструктора уже назначено занятие на это время!"

        cur.execute(
            "INSERT INTO DrivingLessons (id_student, lesson_date, lesson_time) VALUES (%s, %s, %s);",
            (student_id, date_str, time_str)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, "Занятие успешно запланировано! Конфликтов нет."

    def get_lessons(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT dl.id_lesson, s.fio, dl.lesson_date, dl.lesson_time, dl.status
            FROM DrivingLessons dl
            JOIN Students s ON dl.id_student = s.id_student
            ORDER BY dl.lesson_date DESC, dl.lesson_time DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
