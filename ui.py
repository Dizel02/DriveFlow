import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date


class StudentDialog(tk.Toplevel):
    def __init__(self, parent, db, student_data=None, on_success=None):
        super().__init__(parent)
        self.db = db
        self.student_data = student_data
        self.on_success = on_success

        self.title("Редактировать студента" if student_data else "Новый студент")
        self.geometry("380x230")
        self.resizable(False, False)
        self.grab_set()
        self.init_ui()

    def init_ui(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="ФИО студента:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_fio = ttk.Entry(frame, width=30)
        self.ent_fio.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Телефон:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ent_phone = ttk.Entry(frame, width=30)
        self.ent_phone.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Паспортные данные:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ent_passport = ttk.Entry(frame, width=30)
        self.ent_passport.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Учебная группа:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.groups = self.db.get_groups_list()
        self.group_map = {g: g for g in self.groups}
        self.cmb_group = ttk.Combobox(frame, values=list(self.group_map.keys()), state="readonly", width=27)
        self.cmb_group.grid(row=3, column=1, pady=5)
        if self.groups:
            self.cmb_group.current(0)

        if self.student_data:
            self.ent_fio.insert(0, self.student_data)
            self.ent_phone.insert(0, self.student_data or "")
            self.ent_passport.insert(0, self.student_data or "")
            if self.student_data in self.group_map:
                self.cmb_group.set(self.student_data)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Сохранить", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def save_data(self):
        fio = self.ent_fio.get().strip()
        phone = self.ent_phone.get().strip()
        passport = self.ent_passport.get().strip()
        group_id = self.group_map.get(self.cmb_group.get())

        if not fio:
            messagebox.showwarning("Ошибка", "Поле ФИО не может быть пустым!", parent=self)
            return

        try:
            if self.student_data:
                self.db.update_student(self.student_data, fio, phone, passport, group_id)
            else:
                self.db.add_student(fio, phone, passport, group_id)
            if self.on_success:
                self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e), parent=self)


class LoginWindow(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("DriveFlow — Авторизация")
        self.geometry("350x230")
        self.resizable(False, False)

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        self.init_ui()

    def init_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="DriveFlow", font=("Segoe UI", 18, "bold"), foreground="#1E88E5").pack()
        ttk.Label(frame, text="Система автоматизации автошколы", foreground="#64748B").pack(pady=(0, 15))

        form = ttk.Frame(frame)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_login = ttk.Entry(form, width=28)
        self.ent_login.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ent_password = ttk.Entry(form, width=28, show="*")
        self.ent_password.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Войти в систему", command=self.handle_login).pack(pady=15, fill=tk.X)

    def handle_login(self):
        login = self.ent_login.get().strip()
        password = self.ent_password.get().strip()
        try:
            user = self.db.check_auth(login, password)
            if user:
                role_id, fio = user, user
                self.destroy()
                main_app = MainWindow(self.db, role_id, fio)
                main_app.mainloop()
            else:
                messagebox.showwarning("Ошибка входа", "Неверный логин или пароль!")
        except Exception as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к БД:\n{e}")
class MainWindow(tk.Tk):
    def __init__(self, db, role_id, user_fio):
        super().__init__()
        self.db = db
        self.role_id = role_id
        self.user_fio = user_fio
        self.students_cache = []

        self.title("DriveFlow — Автоматизация работы автошколы")
        self.geometry("920x550")

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.init_ui()
        self.refresh_all_data()

    def init_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        # ВКЛАДКА 1: УЧЕНИКИ (CRUD)
        tab_students = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_students, text="Ученики (CRUD)")

        toolbar = ttk.Frame(tab_students)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="+ Добавить ученика", command=self.open_add_student).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Редактировать", command=self.open_edit_student).pack(side=tk.LEFT, padx=5)
        self.btn_delete = ttk.Button(toolbar, text="Удалить", command=self.delete_student)
        self.btn_delete.pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Обновить", command=self.refresh_all_data).pack(side=tk.RIGHT)

        cols = ("ID", "ФИО студента", "Телефон", "Паспорт", "Учебная группа")
        self.tree_students = ttk.Treeview(tab_students, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree_students.heading(col, text=col)
            self.tree_students.column(col, width=150 if col != "ID" else 50)
        self.tree_students.pack(fill=tk.BOTH, expand=True)

        # ВКЛАДКА 2: БИЗНЕС-ПРОЦЕССЫ
        tab_business = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_business, text="Бизнес-процессы")

        frame_bf1 = ttk.LabelFrame(tab_business, text="Бизнес-функция №1: Оформление оплаты со скидкой", padding=15)
        frame_bf1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(frame_bf1, text="Студент:").pack(anchor=tk.W)
        self.cmb_pay_student = ttk.Combobox(frame_bf1, state="readonly", width=35)
        self.cmb_pay_student.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(frame_bf1, text="Базовая цена (руб.):").pack(anchor=tk.W)
        self.ent_base_price = ttk.Entry(frame_bf1)
        self.ent_base_price.insert(0, "35000")
        self.ent_base_price.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(frame_bf1, text="Акция / Скидка:").pack(anchor=tk.W)
        self.cmb_discount = ttk.Combobox(frame_bf1, state="readonly", width=35)
        self.cmb_discount.pack(fill=tk.X, pady=(2, 10))

        self.lbl_final_sum = ttk.Label(frame_bf1, text="Итого к оплате: 35000.00 руб.", font=("Segoe UI", 11, "bold"), foreground="#16A34A")
        self.lbl_final_sum.pack(pady=10)

        ttk.Button(frame_bf1, text="Рассчитать сумму", command=self.calculate_discount).pack(fill=tk.X, pady=3)
        ttk.Button(frame_bf1, text="Провести оплату в БД", command=self.process_payment).pack(fill=tk.X, pady=3)

        frame_bf2 = ttk.LabelFrame(tab_business, text="Бизнес-функция №2: Запись на вождение (контроль накладок)", padding=15)
        frame_bf2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(frame_bf2, text="Студент:").pack(anchor=tk.W)
        self.cmb_lesson_student = ttk.Combobox(frame_bf2, state="readonly", width=35)
        self.cmb_lesson_student.pack(fill=tk.X, pady=(2, 8))

        dt_frame = ttk.Frame(frame_bf2)
        dt_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dt_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W)
        self.ent_date = ttk.Entry(dt_frame, width=15)
        self.ent_date.insert(0, date.today().strftime("%Y-%m-%d"))
        self.ent_date.grid(row=1, column=0, padx=(0, 10))

        ttk.Label(dt_frame, text="Время (ЧЧ:ММ):").grid(row=0, column=1, sticky=tk.W)
        self.ent_time = ttk.Entry(dt_frame, width=12)
        self.ent_time.insert(0, "10:00")
        self.ent_time.grid(row=1, column=1)

        ttk.Button(frame_bf2, text="Записать на вождение", command=self.book_driving_lesson).pack(fill=tk.X, pady=10)

        l_cols = ("ID", "Студент", "Дата", "Время")
        self.tree_lessons = ttk.Treeview(frame_bf2, columns=l_cols, show="headings", height=8)
        for col in l_cols:
            self.tree_lessons.heading(col, text=col)
            self.tree_lessons.column(col, width=90 if col != "ID" else 40)
        self.tree_lessons.pack(fill=tk.BOTH, expand=True)

        # ВКЛАДКА 3: АДМИНИСТРИРОВАНИЕ
        self.tab_admin = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab_admin, text="Администрирование")

        adm_text = (
            "Панель администратора системы DriveFlow\n\n"
            "• Полный доступ к удалению записей студентов и платежей\n"
            "• Управление справочниками инструкторов, автомобилей и тарифов\n"
            "• Конфигурация подключения к серверу MySQL"
        )
        ttk.Label(self.tab_admin, text=adm_text, font=("Segoe UI", 11)).pack(anchor=tk.W)

        role_title = "Администратор (Полный доступ)" if self.role_id == 1 else "Менеджер (Ограниченный доступ)"
        status_bar = ttk.Label(self, text=f"Сотрудник: {self.user_fio}  |  Роль: {role_title}", relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        if self.role_id != 1:
            self.notebook.tab(2, state="disabled")
            self.btn_delete.config(state=tk.DISABLED)
    def refresh_all_data(self):
        try:
            self.students_cache = self.db.get_all_students()
            for item in self.tree_students.get_children():
                self.tree_students.delete(item)

            self.student_combo_map = {}
            for st in self.students_cache:
                st_id, fio, phone, passport, group_name, _ = st
                self.tree_students.insert("", tk.END, values=(st_id, fio, phone or "", passport or "", group_name))
                label = f"{fio} ({group_name})"
                self.student_combo_map[label] = st_id

            st_labels = list(self.student_combo_map.keys())
            self.cmb_pay_student["values"] = st_labels
            self.cmb_lesson_student["values"] = st_labels
            if st_labels:
                self.cmb_pay_student.current(0)
                self.cmb_lesson_student.current(0)

            self.discount_map = {"Без скидки (0%)": (None, 0)}
            for d_id, d_name, perc in self.db.get_active_discounts():
                self.discount_map[f"{d_name} (-{perc}%)"] = (d_id, perc)
            self.cmb_discount["values"] = list(self.discount_map.keys())
            self.cmb_discount.current(0)

            for item in self.tree_lessons.get_children():
                self.tree_lessons.delete(item)
            for les in self.db.get_lessons():
                l_id, st_fio, l_date, l_time, _ = les
                self.tree_lessons.insert("", tk.END, values=(l_id, st_fio, str(l_date), str(l_time)[:5]))
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки данных:\n{e}")

    def open_add_student(self):
        StudentDialog(self, self.db, on_success=self.refresh_all_data)

    def open_edit_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите ученика в таблице для редактирования!")
            return
        idx = self.tree_students.index(selected)
        StudentDialog(self, self.db, student_data=self.students_cache[idx], on_success=self.refresh_all_data)

    def delete_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите ученика для удаления!")
            return
        idx = self.tree_students.index(selected)
        st_id, st_fio = self.students_cache[idx], self.students_cache[idx]

        if messagebox.askyesno("Подтверждение", f"Удалить ученика {st_fio}?"):
            try:
                self.db.delete_student(st_id)
                self.refresh_all_data()
            except Exception as e:
                messagebox.showerror("Ошибка удаления", str(e))

    def calculate_discount(self):
        try:
            base = float(self.ent_base_price.get())
            _, perc = self.discount_map[self.cmb_discount.get()]
            final = base - (base * (perc / 100.0))
            self.lbl_final_sum.config(text=f"Итого к оплате: {final:.2f} руб.")
            return final
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректную базовую стоимость!")
            return None

    def process_payment(self):
        final_amount = self.calculate_discount()
        if final_amount is None:
            return
        st_label = self.cmb_pay_student.get()
        if not st_label:
            return
        student_id = self.student_combo_map[st_label]
        discount_id, _ = self.discount_map[self.cmb_discount.get()]

        try:
            self.db.register_payment_with_discount(student_id, final_amount, discount_id)
            messagebox.showinfo("Оплата проведена", f"Платеж на сумму {final_amount:.2f} руб. успешно сохранен в БД!")
        except Exception as e:
            messagebox.showerror("Ошибка платежа", str(e))

    def book_driving_lesson(self):
        st_label = self.cmb_lesson_student.get()
        if not st_label:
            return
        student_id = self.student_combo_map[st_label]
        date_str = self.ent_date.get().strip()
        time_str = self.ent_time.get().strip() + ":00"

        try:
            success, message = self.db.schedule_lesson_safe(student_id, date_str, time_str)
            if success:
                messagebox.showinfo("Запись подтверждена", message)
                self.refresh_all_data()
            else:
                messagebox.showwarning("Конфликт расписания", message)
        except Exception as e:
            messagebox.showerror("Ошибка записи", str(e))
