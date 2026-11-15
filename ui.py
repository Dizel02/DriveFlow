import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date

ctk.set_appearance_mode("light")

class StudentDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, student_data=None, on_success=None):
        super().__init__(parent)
        self.db = db
        self.student_data = student_data
        self.on_success = on_success

        self.title("Редактировать ученика" if student_data else "Новый ученик")
        self.geometry("400x330")
        self.resizable(False, False)
        self.grab_set()
        self.init_ui()

    def init_ui(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="ФИО ученика:", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.ent_fio = ctk.CTkEntry(frame, width=360, placeholder_text="Иванов Иван Иванович")
        self.ent_fio.pack(pady=(2, 10))

        ctk.CTkLabel(frame, text="Телефон:", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.ent_phone = ctk.CTkEntry(frame, width=360, placeholder_text="+79001112233")
        self.ent_phone.pack(pady=(2, 10))

        ctk.CTkLabel(frame, text="Паспортные данные:", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.ent_passport = ctk.CTkEntry(frame, width=360, placeholder_text="3418 123456")
        self.ent_passport.pack(pady=(2, 10))

        ctk.CTkLabel(frame, text="Учебная группа:", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.groups = self.db.get_groups_list()
        self.group_map = {}
        for g_id, g_name, _ in self.groups:
            self.group_map[g_name] = g_id

        group_names = list(self.group_map.keys()) or ["Нет групп"]
        self.cmb_group = ctk.CTkComboBox(frame, values=group_names, width=360, state="readonly")
        self.cmb_group.pack(pady=(2, 15))
        if self.groups:
            self.cmb_group.set(group_names)

        if self.student_data:
            _, fio, phone, passport, group_name, _ = self.student_data
            self.ent_fio.insert(0, fio)
            self.ent_phone.insert(0, phone or "")
            self.ent_passport.insert(0, passport or "")
            if group_name in self.group_map:
                self.cmb_group.set(group_name)

        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x")
        ctk.CTkButton(btn_box, text="Сохранить", fg_color="#1D4ED8", hover_color="#1E40AF", command=self.save_data).pack(side="left", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_box, text="Отмена", fg_color="#64748B", hover_color="#475569", command=self.destroy).pack(side="right", expand=True, padx=(5, 0))

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
                st_id, _, _, _, _, _ = self.student_data
                self.db.update_student(st_id, fio, phone, passport, group_id)
            else:
                self.db.add_student(fio, phone, passport, group_id)
            if self.on_success:
                self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e), parent=self)


class RegisterDialog(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("DriveFlow — Регистрация")
        self.geometry("380x300")
        self.resizable(False, False)
        self.grab_set()
        self.init_ui()

    def init_ui(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Регистрация сотрудника", font=("Segoe UI", 18, "bold"), text_color="#1D4ED8").pack(pady=(0, 15))

        self.ent_fio = ctk.CTkEntry(frame, width=340, placeholder_text="Ваше ФИО")
        self.ent_fio.pack(pady=6)

        self.ent_login = ctk.CTkEntry(frame, width=340, placeholder_text="Придумайте логин")
        self.ent_login.pack(pady=6)

        self.ent_password = ctk.CTkEntry(frame, width=340, placeholder_text="Придумайте пароль", show="*")
        self.ent_password.pack(pady=6)

        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(fill="x", pady=(15, 0))
        ctk.CTkButton(btn_box, text="Создать аккаунт", fg_color="#1D4ED8", hover_color="#1E40AF", command=self.do_register).pack(side="left", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_box, text="Отмена", fg_color="#64748B", hover_color="#475569", command=self.destroy).pack(side="right", expand=True, padx=(5, 0))

    def do_register(self):
        fio = self.ent_fio.get().strip()
        login = self.ent_login.get().strip()
        password = self.ent_password.get().strip()

        if not fio or not login or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!", parent=self)
            return

        try:
            ok, msg = self.db.register_user(fio, login, password)
            if ok:
                messagebox.showinfo("Успех", msg, parent=self)
                self.destroy()
            else:
                messagebox.showwarning("Ошибка", msg, parent=self)
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e), parent=self)

class LoginWindow(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("DriveFlow — Вход и регистрация")
        self.geometry("400x360")
        self.eval('tk::PlaceWindow . center')
        self.resizable(False, False)
        self.init_ui()

    def init_ui(self):
        card = ctk.CTkFrame(self, corner_radius=15, fg_color="white", border_width=1, border_color="#CBD5E1")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, text="DriveFlow", font=("Segoe UI", 28, "bold"), text_color="#1D4ED8").pack(pady=(15, 2))
        ctk.CTkLabel(card, text="Система автоматизации автошколы", font=("Segoe UI", 12), text_color="#475569").pack(pady=(0, 20))

        self.ent_login = ctk.CTkEntry(card, width=300, height=36, placeholder_text="Введите логин")
        self.ent_login.pack(pady=6)

        self.ent_password = ctk.CTkEntry(card, width=300, height=36, placeholder_text="Введите пароль", show="*")
        self.ent_password.pack(pady=6)

        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(pady=20, padx=30, fill="x")

        ctk.CTkButton(btn_box, text="Войти", height=36, fg_color="#1D4ED8", hover_color="#1E40AF", font=("Segoe UI", 13, "bold"), command=self.handle_login).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(btn_box, text="Регистрация", height=36, fg_color="#475569", hover_color="#334155", font=("Segoe UI", 13, "bold"), command=self.open_register).pack(side="right", expand=True, fill="x", padx=(6, 0))

        ctk.CTkButton(card, text="Выход из программы", height=34, fg_color="#DC2626", hover_color="#B91C1C", font=("Segoe UI", 12, "bold"), command=self.destroy).pack(pady=(0, 15), padx=30, fill="x")

    def open_register(self):
        RegisterDialog(self, self.db)

    def handle_login(self):
        login = self.ent_login.get().strip()
        password = self.ent_password.get().strip()
        try:
            user = self.db.check_auth(login, password)
            if user:
                role_id, fio = user
                self.destroy()
                main_app = MainWindow(self.db, role_id, fio)
                main_app.mainloop()
            else:
                messagebox.showwarning("Ошибка входа", "Неверный логин или пароль!")
        except Exception as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к БД:\n{e}")

class MainWindow(ctk.CTk):
    def __init__(self, db, role_id, user_fio):
        super().__init__()
        self.db = db
        self.role_id = role_id
        self.user_fio = user_fio
        self.students_map = {}

        self.title("DriveFlow — Автоматизация работы автошколы")
        self.after(0, lambda: self.state("zoomed"))
        self.init_ui()
        self.refresh_all_data()

    def init_ui(self):

        header = ctk.CTkFrame(self, height=55, corner_radius=0, fg_color="#1E3A8A")
        header.pack(fill="x")
        ctk.CTkLabel(header, text="DriveFlow", font=("Segoe UI", 22, "bold"), text_color="white").pack(side="left", padx=20, pady=10)
        
        ctk.CTkButton(header, text="Выйти", width=80, height=30, fg_color="#DC2626", hover_color="#B91C1C", font=("Segoe UI", 12, "bold"), command=self.logout).pack(side="right", padx=(0, 20), pady=12)
        role_title = "Администратор (Полный доступ)" if self.role_id == 1 else "Менеджер (Ограниченный доступ)"
        ctk.CTkLabel(header, text=f"Сотрудник: {self.user_fio}  |  {role_title}", font=("Segoe UI", 13, "bold"), text_color="#DBEAFE").pack(side="right", padx=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#0F172A", fieldbackground="white", rowheight=32, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#EFF6FF", foreground="#1E3A8A", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#2563EB")], foreground=[("selected", "white")])

        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color="#1D4ED8", segmented_button_selected_hover_color="#1E40AF")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        tab_st = self.tabview.add("Ученики (CRUD)")
        tab_biz = self.tabview.add("Бизнес-процессы")
        tab_adm = self.tabview.add("Администрирование")

        # --- ВКЛАДКА 1: УЧЕНИКИ ---
        toolbar = ctk.CTkFrame(tab_st, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(toolbar, text="+ Добавить ученика", fg_color="#1D4ED8", hover_color="#1E40AF", font=("Segoe UI", 12, "bold"), command=self.open_add_student).pack(side="left", padx=(0, 8))
        ctk.CTkButton(toolbar, text="Редактировать", fg_color="#D97706", hover_color="#B45309", font=("Segoe UI", 12, "bold"), command=self.open_edit_student).pack(side="left", padx=8)
        self.btn_delete = ctk.CTkButton(toolbar, text="Удалить", fg_color="#DC2626", hover_color="#B91C1C", font=("Segoe UI", 12, "bold"), command=self.delete_student)
        self.btn_delete.pack(side="left", padx=8)
        ctk.CTkButton(toolbar, text="Обновить", fg_color="#475569", hover_color="#334155", font=("Segoe UI", 12, "bold"), command=self.refresh_all_data).pack(side="right")

        cols = ("ID", "ФИО студента", "Телефон", "Паспорт", "Учебная группа")
        self.tree_students = ttk.Treeview(tab_st, columns=cols, show="headings", selectmode="browse")
        for col in cols:
            self.tree_students.heading(col, text=col)
            self.tree_students.column(col, width=180 if col != "ID" else 60)
        self.tree_students.pack(fill="both", expand=True)

        # --- ВКЛАДКА 2: БИЗНЕС-ПРОЦЕССЫ ---
        bf1 = ctk.CTkFrame(tab_biz, corner_radius=12, fg_color="white", border_width=1, border_color="#CBD5E1")
        bf1.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        ctk.CTkLabel(bf1, text="Бизнес-функция №1: Оплата со скидкой", font=("Segoe UI", 16, "bold"), text_color="#1E3A8A").pack(pady=(15, 15))
        
        ctk.CTkLabel(bf1, text="Выберите ученика:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25)
        self.cmb_pay_student = ctk.CTkComboBox(bf1, width=360, state="readonly")
        self.cmb_pay_student.pack(pady=(2, 12), padx=25, fill="x")

        ctk.CTkLabel(bf1, text="Базовая стоимость курса (руб.):", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25)
        self.ent_base_price = ctk.CTkEntry(bf1)
        self.ent_base_price.insert(0, "35000")
        self.ent_base_price.pack(pady=(2, 12), padx=25, fill="x")

        ctk.CTkLabel(bf1, text="Применить акцию / скидку:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25)
        self.cmb_discount = ctk.CTkComboBox(bf1, width=360, state="readonly")
        self.cmb_discount.pack(pady=(2, 15), padx=25, fill="x")

        self.lbl_final_sum = ctk.CTkLabel(bf1, text="Итого к оплате: 35000.00 руб.", font=("Segoe UI", 16, "bold"), text_color="#047857")
        self.lbl_final_sum.pack(pady=10)

        ctk.CTkButton(bf1, text="Рассчитать сумму", fg_color="#475569", hover_color="#334155", font=("Segoe UI", 13, "bold"), command=self.calculate_discount).pack(pady=5, padx=25, fill="x")
        ctk.CTkButton(bf1, text="Провести оплату в БД", fg_color="#047857", hover_color="#065F46", font=("Segoe UI", 13, "bold"), command=self.process_payment).pack(pady=5, padx=25, fill="x")

        bf2 = ctk.CTkFrame(tab_biz, corner_radius=12, fg_color="white", border_width=1, border_color="#CBD5E1")
        bf2.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

        ctk.CTkLabel(bf2, text="Бизнес-функция №2: Запись на вождение", font=("Segoe UI", 16, "bold"), text_color="#1E3A8A").pack(pady=(15, 15))

        ctk.CTkLabel(bf2, text="Выберите ученика:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25)
        self.cmb_lesson_student = ctk.CTkComboBox(bf2, width=360, state="readonly")
        self.cmb_lesson_student.pack(pady=(2, 10), padx=25, fill="x")

        dt_row = ctk.CTkFrame(bf2, fg_color="transparent")
        dt_row.pack(fill="x", padx=25, pady=5)
        
        self.ent_date = ctk.CTkEntry(dt_row, placeholder_text="ГГГГ-ММ-ДД")
        self.ent_date.insert(0, date.today().strftime("%Y-%m-%d"))
        self.ent_date.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.ent_time = ctk.CTkEntry(dt_row, placeholder_text="ЧЧ:ММ")
        self.ent_time.insert(0, "10:00")
        self.ent_time.pack(side="right", expand=True, fill="x", padx=(5, 0))

        ctk.CTkButton(bf2, text="Записать на вождение (проверка накладок)", fg_color="#1D4ED8", hover_color="#1E40AF", font=("Segoe UI", 13, "bold"), command=self.book_driving_lesson).pack(pady=12, padx=25, fill="x")

        l_cols = ("ID", "Студент", "Инструктор", "Дата", "Время")
        self.tree_lessons = ttk.Treeview(bf2, columns=l_cols, show="headings", height=7)
        col_widths = {"ID": 35, "Студент": 150, "Инструктор": 150, "Дата": 85, "Время": 60}
        for col in l_cols:
            self.tree_lessons.heading(col, text=col)
            self.tree_lessons.column(col, width=col_widths[col], anchor="center" if col in ("ID", "Дата", "Время") else "w")

        self.tree_lessons.pack(fill="both", expand=True, padx=(0, 15), pady=(0, 8))
        l_btn_row = ctk.CTkFrame(bf2, fg_color="transparent")
        l_btn_row.pack(fill="x", padx=25, pady=(0, 15))
        ctk.CTkButton(l_btn_row, text="Перенести на указанное время", fg_color="#D97706", hover_color="#B45309", font=("Segoe UI", 12, "bold"), command=self.edit_driving_lesson).pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.btn_delete_lesson = ctk.CTkButton(l_btn_row, text="Удалить запись", fg_color="#DC2626", hover_color="#B91C1C", font=("Segoe UI", 12, "bold"), command=self.remove_driving_lesson)
        self.btn_delete_lesson.pack(side="right", expand=True, fill="x", padx=(5, 0))


        # --- ВКЛАДКА 3: АДМИНИСТРИРОВАНИЕ ---
        adm_bar = ctk.CTkFrame(tab_adm, fg_color="transparent")
        adm_bar.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(adm_bar, text="Зарегистрированные сотрудники системы:", font=("Segoe UI", 15, "bold"), text_color="#1E3A8A").pack(side="left")
        ctk.CTkButton(adm_bar, text="Удалить менеджера", fg_color="#DC2626", hover_color="#B91C1C", font=("Segoe UI", 12, "bold"), command=self.delete_selected_user).pack(side="right")

        u_cols = ("ID", "ФИО сотрудника", "Логин", "Роль в системе")
        self.tree_users = ttk.Treeview(tab_adm, columns=u_cols, show="headings", selectmode="browse")
        for col in u_cols:
            self.tree_users.heading(col, text=col)
            self.tree_users.column(col, width=180 if col != "ID" else 60)
        self.tree_users.pack(fill="both", expand=True)

        if self.role_id != 1:
            self.btn_delete.configure(state="disabled")
            self.btn_delete_lesson.configure(state="disabled")
            self.tabview.delete("Администрирование")

    def logout(self):
        self.destroy()
        login_win = LoginWindow(self.db)
        login_win.mainloop() 
        
    def refresh_all_data(self):
        try:
            students = self.db.get_all_students()
            for item in self.tree_students.get_children():
                self.tree_students.delete(item)

            self.students_map = {}
            self.student_combo_map = {}
            for st in students:
                st_id, fio, phone, passport, group_name, _ = st
                self.students_map[str(st_id)] = st
                self.tree_students.insert("", "end", iid=str(st_id), values=(st_id, fio, phone or "", passport or "", group_name))
                label = f"{fio} ({group_name})"
                self.student_combo_map[label] = st_id

            st_labels = list(self.student_combo_map.keys()) or ["Нет учеников"]
            self.cmb_pay_student.configure(values=st_labels)
            self.cmb_lesson_student.configure(values=st_labels)
            self.cmb_pay_student.set(st_labels[0])
            self.cmb_lesson_student.set(st_labels[0])

            self.discount_map = {"Без скидки (0%)": (None, 0)}
            for d_id, d_name, perc in self.db.get_active_discounts():
                self.discount_map[f"{d_name} (-{perc}%)"] = (d_id, perc)
            disc_labels = list(self.discount_map.keys())
            self.cmb_discount.configure(values=disc_labels)
            self.cmb_discount.set(disc_labels[0])
            
            for item in self.tree_lessons.get_children():
                self.tree_lessons.delete(item)
            for les in self.db.get_lessons():
                l_id, st_fio, inst_fio, l_date, l_time = les
                self.tree_lessons.insert("", "end", values=(l_id, st_fio, inst_fio, str(l_date), str(l_time)[:5]))

            if self.role_id == 1:
                for item in self.tree_users.get_children():
                    self.tree_users.delete(item)
                for u_id, u_fio, u_login, u_role in self.db.get_all_users():
                    self.tree_users.insert("", "end", iid=str(u_id), values=(u_id, u_fio, u_login, u_role))

        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки данных:\n{e}")

    def open_add_student(self):
        StudentDialog(self, self.db, on_success=self.refresh_all_data)

    def open_edit_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите ученика в таблице для редактирования!")
            return
        (st_iid,) = selected
        StudentDialog(self, self.db, student_data=self.students_map[st_iid], on_success=self.refresh_all_data)

    def delete_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите ученика для удаления!")
            return
        (st_iid,) = selected
        st_id, st_fio, _, _, _, _ = self.students_map[st_iid]

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
            self.lbl_final_sum.configure(text=f"Итого к оплате: {final:.2f} руб.")
            return final
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректную базовую стоимость!")
            return None

    def process_payment(self):
        final_amount = self.calculate_discount()
        if final_amount is None:
            return
        st_label = self.cmb_pay_student.get()
        if st_label not in self.student_combo_map:
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
        if st_label not in self.student_combo_map:
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

    def delete_selected_user(self):
        selected = self.tree_users.selection()
        if not selected:
         messagebox.showwarning("Внимание", "Выберите сотрудника в таблице!")
         return
        (u_iid,) = selected
        vals = self.tree_users.item(u_iid, "values")
        if vals[3] == "Администратор":
            messagebox.showwarning("Защита", "Нельзя удалить учетную запись Администратора!")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить учетную запись менеджера {vals[1]}?"):
            self.db.delete_user(int(u_iid))
            self.refresh_all_data()

    def edit_driving_lesson(self):
        selected = self.tree_lessons.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись в таблице расписания для переноса!")
            return
        (item_id,) = selected
        lesson_id_str, _, _, _, _ = self.tree_lessons.item(item_id, "values")
        lesson_id = int(lesson_id_str)
        new_date = self.ent_date.get().strip()
        new_time = self.ent_time.get().strip() + ":00"

        try:
            ok, msg = self.db.update_lesson_safe(lesson_id, new_date, new_time)
            if ok:
                messagebox.showinfo("Перенесено", msg)
                self.refresh_all_data()
            else:
                messagebox.showwarning("Конфликт расписания", msg)
        except Exception as e:
            messagebox.showerror("Ошибка переноса", str(e))

    def remove_driving_lesson(self):
        selected = self.tree_lessons.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись в таблице расписания для удаления!")
            return
        (item_id,) = selected
        lesson_id_str, st_fio, _, _, _ = self.tree_lessons.item(item_id, "values")
        if messagebox.askyesno("Подтверждение", f"Отменить и удалить занятие ученика {st_fio}?"):
            self.db.delete_lesson(int(lesson_id_str))
            self.refresh_all_data()
