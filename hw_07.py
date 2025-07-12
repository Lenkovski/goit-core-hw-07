from collections import UserDict
from datetime import datetime, timedelta
import re

# --- Базові класи полів ---
class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        # Перевірка на коректність номера телефону: рівно 10 цифр
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        # Перевірка формату дати та збереження як рядка у форматі DD.MM.YYYY
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

# --- Клас Record (контакт) та AddressBook (книга контактів) ---
class Record:
    def __init__(self, name):
        self.name = Name(name)  # Ім'я контакту
        self.phones = []        # Список телефонів
        self.birthday = None    # День народження 

    def add_phone(self, phone):
        # Додаємо телефон до списку телефонів
        self.phones.append(Phone(phone))

    def change_phone(self, old, new):
        # Зміна наявного телефону на новий
        for i, ph in enumerate(self.phones):
            if ph.value == old:
                self.phones[i] = Phone(new)
                return
        raise ValueError("Old phone number not found.")

    def add_birthday(self, birthday):
        # Додаємо день народження
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def add_record(self, record):
        # Додаємо запис до книги контактів
        self.data[record.name.value] = record

    def find(self, name):
        # Знаходимо запис за ім'ям
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        # Отримуємо список днів народжень на наступні 7 днів
        today = datetime.today()
        upcoming = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=today.year)
            if bday_date < today:
                bday_date = bday_date.replace(year=today.year + 1)
            days_diff = (bday_date - today).days
            if 0 <= days_diff <= 7:
                greeting_day = bday_date
                # Якщо день народження на вихідний — переносимо на понеділок
                if greeting_day.weekday() in (5, 6):
                    greeting_day += timedelta(days=(7 - greeting_day.weekday()))
                upcoming.append({
                    "name": record.name.value,
                    "birthday": greeting_day.strftime("%d.%m.%Y")
                })
        return upcoming

# --- Декоратор для обробки помилок ---
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter command arguments."
        except AttributeError:
            return "Contact not found."
    return inner

# --- Обробники команд ---
@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.change_phone(old_phone, new_phone)
    return "Phone changed."

@input_error
def phone(args, book):
    name = args[0]
    record = book.find(name)
    return ", ".join(p.value for p in record.phones)

@input_error
def show_all(args, book):
    result = []
    for name, record in book.data.items():
        phones = ", ".join(p.value for p in record.phones)
        bday = f", Birthday: {record.birthday.value}" if record.birthday else ""
        result.append(f"{name}: {phones}{bday}")
    return "\n".join(result)

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    record.add_birthday(bday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record.birthday:
        return "Birthday not found."
    return record.birthday.value

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{entry['name']}: {entry['birthday']}" for entry in upcoming)

# --- Парсер команд та головний цикл ---
# ---  Падіння ?
def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    return command, parts[1:]

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if not command:
            continue

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

