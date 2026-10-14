"""Практическое занятие № 15, вариант 11: командировочные расходы."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("travel_expenses.db")
SAMPLE_DATA = [
    (101, "Иванов", "Москва", 18000, 10000, "Проживание", 12500),
    (102, "Петрова", "Казань", 14000, 8000, "Проезд", 9500),
    (103, "Сидоров", "Сочи", 22000, 12000, "Проживание", 16500),
    (104, "Кузнецова", "Москва", 16000, 9000, "Питание", 7200),
    (105, "Смирнов", "Самара", 12000, 6000, "Проезд", 8300),
    (106, "Волкова", "Санкт-Петербург", 24000, 15000, "Проживание", 17800),
    (107, "Орлов", "Казань", 15000, 7000, "Питание", 5800),
    (108, "Морозова", "Екатеринбург", 19000, 11000, "Проезд", 13200),
    (109, "Павлов", "Москва", 17000, 9000, "Проживание", 14200),
    (110, "Федорова", "Ростов-на-Дону", 13000, 7500, "Питание", 6400),
]


def initialize_database(connection):
    """Создать одну таблицу и заполнить её 10 примерами при первом запуске."""
    connection.execute(
        """CREATE TABLE IF NOT EXISTS expense_items (
            order_number INTEGER PRIMARY KEY,
            surname TEXT NOT NULL,
            destination TEXT NOT NULL,
            payment REAL NOT NULL CHECK (payment >= 0),
            advance REAL NOT NULL CHECK (advance >= 0),
            expense_type TEXT NOT NULL,
            expense_amount REAL NOT NULL CHECK (expense_amount >= 0)
        )"""
    )
    if connection.execute("SELECT COUNT(*) FROM expense_items").fetchone()[0] == 0:
        connection.executemany(
            "INSERT INTO expense_items VALUES (?, ?, ?, ?, ?, ?, ?)", SAMPLE_DATA
        )
    connection.commit()


def read_int(prompt):
    """Получить целое число от пользователя."""
    return int(input(prompt).strip())


def read_money(prompt):
    """Получить неотрицательную денежную сумму."""
    value = float(input(prompt).strip().replace(",", "."))
    if value < 0:
        raise ValueError("Сумма не может быть отрицательной")
    return value


def read_text(prompt):
    """Получить непустую строку."""
    value = input(prompt).strip()
    if not value:
        raise ValueError("Поле не может быть пустым")
    return value


def show_rows(rows):
    """Вывести найденные записи в консоль."""
    if not rows:
        print("Записи не найдены.")
        return
    print("№ приказа | Фамилия | Место | Оплата | Аванс | Вид расходов | Расходы")
    for row in rows:
        print(" | ".join(str(value) for value in row))
    print(f"Количество записей: {len(rows)}")


def show_all(connection):
    """Показать всю таблицу."""
    rows = connection.execute(
        "SELECT * FROM expense_items ORDER BY order_number"
    ).fetchall()
    show_rows(rows)


def add_record(connection):
    """Добавить запись по введённым значениям."""
    values = (
        read_int("№ приказа: "),
        read_text("Фамилия: "),
        read_text("Место командировки: "),
        read_money("Оплата: "),
        read_money("Аванс: "),
        read_text("Вид расходов: "),
        read_money("Сумма расходов: "),
    )
    connection.execute("INSERT INTO expense_items VALUES (?, ?, ?, ?, ?, ?, ?)", values)
    connection.commit()
    print("Запись добавлена.")


def search_records(connection):
    """Три варианта SELECT с условием WHERE."""
    print("1 — по фамилии; 2 — по месту; 3 — расходы больше суммы")
    choice = input("Выбор: ").strip()
    if choice == "1":
        surname = read_text("Фамилия (или её часть): ")
        rows = connection.execute(
            "SELECT * FROM expense_items WHERE surname LIKE ? ORDER BY order_number",
            (f"%{surname}%",),
        ).fetchall()
    elif choice == "2":
        destination = read_text("Место (или его часть): ")
        rows = connection.execute(
            "SELECT * FROM expense_items WHERE destination LIKE ? ORDER BY order_number",
            (f"%{destination}%",),
        ).fetchall()
    elif choice == "3":
        limit = read_money("Минимальная сумма расходов: ")
        rows = connection.execute(
            "SELECT * FROM expense_items WHERE expense_amount > ? ORDER BY order_number",
            (limit,),
        ).fetchall()
    else:
        print("Неверный вариант.")
        return
    show_rows(rows)


def edit_records(connection):
    """Три условных UPDATE: место, аванс или сумма расходов."""
    print("1 — изменить место по № приказа")
    print("2 — изменить аванс по № приказа")
    print("3 — изменить расходы по № приказа")
    choice = input("Выбор: ").strip()
    if choice not in ("1", "2", "3"):
        print("Неверный вариант.")
        return
    number = read_int("№ приказа: ")
    if choice == "1":
        value = read_text("Новое место командировки: ")
        cursor = connection.execute(
            "UPDATE expense_items SET destination = ? WHERE order_number = ?",
            (value, number),
        )
    elif choice == "2":
        value = read_money("Новый аванс: ")
        cursor = connection.execute(
            "UPDATE expense_items SET advance = ? WHERE order_number = ?",
            (value, number),
        )
    else:
        value = read_money("Новая сумма расходов: ")
        cursor = connection.execute(
            "UPDATE expense_items SET expense_amount = ? WHERE order_number = ?",
            (value, number),
        )
    connection.commit()
    print(f"Изменено записей: {cursor.rowcount}")


def delete_records(connection):
    """Три условных DELETE: по приказу, фамилии или виду расходов."""
    print("1 — по № приказа; 2 — по фамилии; 3 — по виду расходов")
    choice = input("Выбор: ").strip()
    if choice == "1":
        sql = "DELETE FROM expense_items WHERE order_number = ?"
        value = read_int("№ приказа: ")
    elif choice == "2":
        sql = "DELETE FROM expense_items WHERE surname = ?"
        value = read_text("Фамилия (точно): ")
    elif choice == "3":
        sql = "DELETE FROM expense_items WHERE expense_type = ?"
        value = read_text("Вид расходов (точно): ")
    else:
        print("Неверный вариант.")
        return
    preview = connection.execute(
        sql.replace("DELETE FROM", "SELECT * FROM", 1), (value,)
    ).fetchall()
    show_rows(preview)
    if not preview:
        return
    confirmation = input("Удалить эти записи? (да/нет): ").strip().lower()
    if confirmation != "да":
        print("Удаление отменено.")
        return
    cursor = connection.execute(sql, (value,))
    connection.commit()
    print(f"Удалено записей: {cursor.rowcount}")


def main():
    """Главное меню приложения."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            initialize_database(connection)
            actions = {
                "1": show_all,
                "2": add_record,
                "3": search_records,
                "4": edit_records,
                "5": delete_records,
            }
            while True:
                print("\nКОМАНДИРОВОЧНЫЕ РАСХОДЫ")
                print("1 — показать записи")
                print("2 — добавить запись")
                print("3 — поиск (3 SQL-запроса)")
                print("4 — редактирование (3 SQL-запроса)")
                print("5 — удаление (3 SQL-запроса)")
                print("0 — выход")
                choice = input("Выберите действие: ").strip()
                if choice == "0":
                    print("Работа завершена.")
                    break
                action = actions.get(choice)
                if action is None:
                    print("Выберите пункт от 0 до 5.")
                    continue
                try:
                    action(connection)
                except (ValueError, sqlite3.IntegrityError) as error:
                    print(f"Ошибка данных: {error}")
    except sqlite3.Error as error:
        print(f"Ошибка базы данных: {error}")
    except (KeyboardInterrupt, EOFError):
        print("\nРабота прервана.")


if __name__ == "__main__":
    main()
