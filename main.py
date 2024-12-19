from email.mime import image
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
from datetime import datetime, timedelta
from PIL import Image, ImageTk


DB_FILE = "system.db"
def init_db():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        fullname TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        manufacturer TEXT,
        price REAL,
        discount REAL,
        stock INTEGER,
        image TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        total_amount REAL,
        discount_amount REAL,
        status TEXT,
        pickup_point TEXT,
        pickup_code TEXT,
        created_at TEXT,
        delivery_date TEXT
    )''')
    connection.commit()
    connection.close()


def generate_captcha():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=4))

def verify_captcha(input_captcha, real_captcha):
    return input_captcha == real_captcha


class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1600x900")
        self.root.title("ООО «Пиши-стирай»")
        self.root.configure(bg="white")
        self.create_login_screen()
        self.captcha_attempts = 0
        self.locked_until = None
        self.cart = [] 

    def create_login_screen(self):

        self.clear_window()
        
        logo_image = Image.open("logo.png")  
        logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)  # Изменяем размер логотипа
        logo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self.root, image=logo,  bg="white")
        logo_label.image = logo  # Сохраняем ссылку на изображение, чтобы оно не исчезло
        logo_label.pack(pady=50)

        tk.Label(self.root, text="Добро пожаловать!", font=("Comic Sans MS", 18, 'bold'), fg="#498C51", bg="white").pack(pady=20)

        frame = tk.Frame(self.root, bg="white")

        frame.pack(pady=20)

        self.captcha_text = generate_captcha()
        
        tk.Label(frame, text="Логин:", font=("Comic Sans MS", 14), fg="#498C51", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.login_entry = ttk.Entry(frame, font=("Comic Sans MS", 14), width=25)
        self.login_entry.grid(row=0, column=1, padx=10, pady=10)

        self.login_entry.configure(style="TEntry")

        tk.Label(frame, text="Пароль:", font=("Comic Sans MS", 14), fg="#498C51", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = ttk.Entry(frame, font=("Comic Sans MS", 14), width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.password_entry.configure(style="TEntry")
        
        button_frame = tk.Frame(self.root, bg="white")
        button_frame.pack(pady=20)

        
        captcha_frame = tk.Frame(self.root, bg="#498C51", bd=2)
        captcha_frame.pack(pady=20, ipadx=10, ipady=10)

      
        self.captcha_label = tk.Label(captcha_frame, text=self.captcha_text, font=("Comic Sans MS", 24, "bold"), fg="white", bg="#498C51")
        self.captcha_label.pack(pady=10)

       
        self.captcha_input = tk.Entry(captcha_frame, font=("Comic Sans MS", 24, 'bold'), justify="center", fg="#498C51", bg="white", relief="flat")
        self.captcha_input.pack(pady=10, padx=10)

        
    
        tk.Button(button_frame, text="Войти", font=("Comic Sans MS", 14), bg='#498C51', fg='white', command=self.handle_login).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="Гостевой режим", font=("Comic Sans MS", 14), bg='#498C51', fg='white', command=lambda: self.load_main_screen("Гоcтевой режим", "Гость")).pack(side=tk.LEFT, padx=20)

    def handle_login(self):
        if self.locked_until and datetime.now() < self.locked_until:
            messagebox.showwarning("Заблокировано", "Пожалуйста, подождите, прежде чем попробовать снова.")
            return

        username = self.login_entry.get()
        password = self.password_entry.get()

        if self.captcha_attempts >= 1:  
            real_captcha = self.captcha_text
            input_captcha = self.captcha_input.get()
            if not verify_captcha(input_captcha, real_captcha):
                messagebox.showerror("Ошибка", "Неверная CAPTCHA")
                self.locked_until = datetime.now() + timedelta(seconds=10)
                self.create_login_screen()
                return

        if self.authenticate_user(username, password):
            role = self.get_user_role(username)
            fullname = self.get_user_fullname(username)
            messagebox.showinfo("Успех", f"Вошли как {role} - {fullname}")
            self.load_main_screen(role, fullname)
        else:
            self.captcha_attempts += 1
            self.captcha_label.pack()
            self.captcha_input.pack()
            messagebox.showerror("Ошибка", "Неверные учетные данные")

    def authenticate_user(self, username, password):
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        connection.close()
        return user

    def get_user_role(self, username):
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        role = cursor.fetchone()[0]
        connection.close()
        return role

    def get_user_fullname(self, username):
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT fullname FROM users WHERE username = ?", (username,))
        fullname = cursor.fetchone()[0]
        connection.close()
        return fullname

    def guest_mode(self):
        messagebox.showinfo("Гость", "Переход в режим гостя")
        self.load_main_screen("Guest", "Guest")

    def load_main_screen(self, role, fullname):
        self.clear_window()
        self.current_role = role
        self.current_fullname = fullname
        logo_image = Image.open("logo.png")  
        logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)  # Изменяем размер логотипа
        logo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self.root, image=logo,  bg="white")
        logo_label.image = logo  # Сохраняем ссылку на изображение, чтобы оно не исчезло
        logo_label.pack(pady=50)
        tk.Label(self.root, text=f"{fullname} ({role})", font=("Comic Sans MS", 20, 'bold'), fg="#498C51", bg="white").pack(pady=150)
        if role == "Admin":
            tk.Button(self.root, text="Управление заказами", font=("Comic Sans MS", 20), bg='#498C51', fg='white', command=self.manage_orders).pack()
        tk.Button(self.root, text="Просмотр товаров", font=("Comic Sans MS", 20), bg='#498C51', fg='white', command=self.view_products).pack(pady=20)
        tk.Button(self.root, text="Выйти", font=("Comic Sans MS", 14), bg='#498C51', fg='white', command=self.create_login_screen).pack(pady=30)
        tk.Button(
            self.root,
            text="Перейти в корзину",
            font=("Comic Sans MS", 20),
            bg='#498C51',
            fg='white',
            command=self.view_cart
        ).pack(pady=20)
        

    def view_products(self):
        self.clear_window()
        tk.Label(self.root, text="Список товаров", font=("Comic Sans MS", 14), bg='#498C51', fg='white').pack()

        # Создаем canvas для прокрутки
        canvas = tk.Canvas(self.root, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Создаем scrollbar и связываем его с canvas
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Фрейм внутри canvas
        product_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=product_frame, anchor="nw")

        # Загружаем данные о товарах из базы данных
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, description, price, discount, stock, image FROM products")
        products = cursor.fetchall()
        connection.close()

        # Добавляем товары в product_frame
        for product in products:
            # Фрейм для каждого товара
            item_frame = tk.Frame(product_frame, bg="white", bd=2, relief="ridge")
            item_frame.pack(fill=tk.X, padx=10, pady=5)

            # Загружаем изображение товара
            if product[6]:  # Если указано изображение
                try:
                    img = Image.open(product[6])
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(item_frame, image=photo, bg="white")
                    img_label.image = photo  # Сохраняем ссылку на изображение
                    img_label.pack(side=tk.LEFT, padx=10)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                    tk.Label(item_frame, text="Нет изображения", bg="white").pack(side=tk.LEFT, padx=10)

            # Информация о товаре
            text = f"Название: {product[1]}\nОписание: {product[2]}\nЦена: {product[3]} ₽\nСкидка: {product[4]}%\nОстаток: {product[5]}"
            tk.Label(item_frame, text=text, font=("Comic Sans MS", 12), bg="white", justify="left").pack(side=tk.LEFT, padx=10)

            # Кнопка добавления товара в корзину
            add_to_cart_button = tk.Button(
                item_frame,
                text="Добавить в корзину",
                font=("Comic Sans MS", 12),
                bg="#498C51",
                fg="white",
                command=lambda product=product: self.add_product_to_cart(product)
            )
            add_to_cart_button.pack(side=tk.RIGHT, padx=10)

        # Обновляем область прокрутки
        product_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Кнопка назад
        tk.Button(self.root, text="Назад", font=("Comic Sans MS", 14), bg='#498C51', fg='white', command=lambda: self.load_main_screen("Гость", "Гость")).pack(pady=20)

    def add_product_to_cart(self, product):
        self.cart.append(product)
        messagebox.showinfo("Корзина", f"Товар '{product[1]}' добавлен в корзину.")


    def view_cart(self):
        self.clear_window()
        tk.Label(self.root, text="Ваша корзина", font=("Comic Sans MS", 20), bg='#498C51', fg='white').pack(pady=20)

        if not self.cart:
            tk.Label(self.root, text="Корзина пуста.", font=("Comic Sans MS", 16), bg='white', fg='#498C51').pack()
        else:
            for product in self.cart:
                tk.Label(
                    self.root,
                    text=f"{product[1]} - {product[3]} ₽",
                    font=("Comic Sans MS", 16),
                    bg="white",
                    fg="#498C51"
                ).pack(pady=5)

        tk.Button(
            self.root,
            text="Назад",
            font=("Comic Sans MS", 14),
            bg='#498C51',
            fg='white',
            command=lambda: self.load_main_screen(self.current_role, self.current_fullname)
        ).pack(pady=20)



    def sort_column(self, col):
        col_idx = ["ID", "Name", "Description", "Price", "Discount", "Stock"].index(col)
        self.products.sort(key=lambda x: x[col_idx])
        self.tree.delete(*self.tree.get_children())
        for product in self.products:
            self.tree.insert("", tk.END, values=product)

    def view_cart(self):
        self.clear_window()
        tk.Label(self.root, text="Ваша корзина", font=("Comic Sans MS", 14), bg='#498C51', fg='white').pack()

        for item in self.cart:
            tk.Label(self.root, text=f"{item[1]} - {item[3]}₽", font=("Comic Sans MS", 14),bg='white', fg='#498C51').pack()

        

        tk.Button(self.root, text="Назад",font=("Comic Sans MS", 14), bg='#498C51', fg='white', command=self.view_products).pack(side=tk.BOTTOM)

    def manage_orders(self):
        self.clear_window()
        tk.Label(self.root, text="Управление заказами", font=("Comic Sans MS", 14), bg='#498C51', fg='white').pack()

        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT id, user_id, total_amount, discount_amount, status, pickup_point, pickup_code, created_at, delivery_date FROM orders")
        orders = cursor.fetchall()
        connection.close()

        columns = ("ID", "ID пользователя", "Итого", "Скидка", "Статус", "Пункт выдачи", "Код pickup", "Дата создания", "Дата доставки")
        self.order_tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.order_tree.heading(col, text=col)

        for order in orders:
            self.order_tree.insert("", tk.END, values=order)

        self.order_tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.root, text="Обновить статус", font=("Comic Sans MS", 14), bg='#498C51', fg='white', command=self.update_order_status).pack()
        tk.Button(self.root, text="Назад", font=("Comic Sans MS", 14), bg='#498C51', fg='white',command=lambda: self.load_main_screen("Admin", "Admin")).pack()

    def update_order_status(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showwarning("Нет выбора", "Пожалуйста, выберите заказ для обновления.")
            return

        order = self.order_tree.item(selected_item, 'values')
        new_status = tk.simpledialog.askstring("Обновить статус", f"Введите новый статус для заказа ID {order[0]}:")
        if new_status:
            connection = sqlite3.connect(DB_FILE)
            cursor = connection.cursor()
            cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order[0]))
            connection.commit()
            connection.close()
            messagebox.showinfo("Обновлено", f"Статус заказа ID {order[0]} обновлен на {new_status}.")
            self.manage_orders()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    init_db()  
    root = tk.Tk()
    app = App(root)
    root.mainloop()
