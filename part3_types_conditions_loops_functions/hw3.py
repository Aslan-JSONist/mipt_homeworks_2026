from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

PROFIT_MSG = "This month, the profit amounted to"
LOSS_MSG = "This month, the loss amounted to"

DATE_PARTS_COUNT = 3
SHORT_DATE_PART_LENGTH = 2
YEAR_PART_LENGTH = 4
MONTHS_IN_YEAR = 12
FEBRUARY = 2
INCOME_COMMAND_PARTS_COUNT = 3
COST_COMMAND_PARTS_COUNT = 4
STATS_COMMAND_PARTS_COUNT = 2
MAX_NUMBER_PARTS = 2
CATEGORY_PARTS_COUNT = 2
COPECKS_IN_RUBLE = 100

DateTuple = tuple[int, int, int]
TransactionValue = float | str | DateTuple
TransactionData = tuple[int, DateTuple, str | None]
StatsData = tuple[int, int, int, dict[str, int]]
TotalsData = tuple[int, int, int]

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    date_parts = maybe_dt.split("-")
    if not has_valid_date_format(date_parts):
        return None

    parsed_date = parse_date_parts(date_parts)
    if not has_valid_date(parsed_date):
        return None
    return parsed_date


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        return save_failed_transaction(NONPOSITIVE_VALUE_MSG)

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return save_failed_transaction(INCORRECT_DATE_MSG)

    financial_transactions_storage.append({"amount": amount, "date": parsed_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_existing_category(category_name):
        return save_failed_transaction(NOT_EXISTS_CATEGORY)
    if amount <= 0:
        return save_failed_transaction(NONPOSITIVE_VALUE_MSG)

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        return save_failed_transaction(INCORRECT_DATE_MSG)

    financial_transactions_storage.append(
        {"category": category_name, "amount": amount, "date": parsed_date},
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common_category}::{target_category}"
        for common_category, target_categories in EXPENSE_CATEGORIES.items()
        for target_category in target_categories
    )


def stats_handler(report_date: str) -> str:
    parsed_date = extract_date(report_date)
    if parsed_date is None:
        return INCORRECT_DATE_MSG

    stats_data = get_stats_data(parsed_date)
    return build_stats_report(report_date, stats_data)


def has_valid_date_format(date_parts: list[str]) -> bool:
    if len(date_parts) != DATE_PARTS_COUNT:
        return False

    return have_date_parts_expected_length(date_parts) and all_date_parts_are_digits(date_parts)


def have_date_parts_expected_length(date_parts: list[str]) -> bool:
    day_text, month_text, year_text = date_parts
    return (
        len(day_text) == SHORT_DATE_PART_LENGTH
        and len(month_text) == SHORT_DATE_PART_LENGTH
        and len(year_text) == YEAR_PART_LENGTH
    )


def all_date_parts_are_digits(date_parts: list[str]) -> bool:
    day_text, month_text, year_text = date_parts
    return day_text.isdigit() and month_text.isdigit() and year_text.isdigit()


def parse_date_parts(date_parts: list[str]) -> DateTuple:
    day_text, month_text, year_text = date_parts
    return int(day_text), int(month_text), int(year_text)


def has_valid_date(parsed_date: DateTuple) -> bool:
    day, month, year = parsed_date
    if year < 1:
        return False
    if month < 1 or month > MONTHS_IN_YEAR:
        return False
    if day < 1:
        return False
    return day <= get_days_in_month(month, year)


def get_days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        return 29 if is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def extract_amount(maybe_amount: str) -> float | None:
    normalized_number = normalize_number(maybe_amount)
    if normalized_number is None:
        return None
    return float(normalized_number)


def normalize_number(maybe_number: str) -> str | None:
    if not maybe_number:
        return None

    normalized_number = maybe_number.replace(",", ".")
    number_parts = normalized_number.split(".")
    if not has_valid_number_parts(number_parts):
        return None
    return normalized_number


def has_valid_number_parts(number_parts: list[str]) -> bool:
    if len(number_parts) > MAX_NUMBER_PARTS:
        return False

    integer_part = strip_number_sign(number_parts[0])
    fractional_part = get_fractional_part(number_parts)
    return (
        bool(integer_part or fractional_part)
        and is_digits_or_empty(integer_part)
        and is_digits_or_empty(fractional_part)
    )


def strip_number_sign(integer_part: str) -> str:
    if integer_part[:1] in "+-":
        return integer_part[1:]
    return integer_part


def get_fractional_part(number_parts: list[str]) -> str:
    if len(number_parts) == 1:
        return ""
    return number_parts[1]


def is_digits_or_empty(text: str) -> bool:
    return not text or text.isdigit()


def save_failed_transaction(message: str) -> str:
    financial_transactions_storage.append({})
    return message


def is_existing_category(category_name: str) -> bool:
    category_parts = category_name.split("::")
    if len(category_parts) != CATEGORY_PARTS_COUNT:
        return False

    common_category, target_category = category_parts
    return common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]


def get_stats_data(stats_date: DateTuple) -> StatsData:
    totals = (0, 0, 0)
    category_totals: dict[str, int] = {}

    for transaction in financial_transactions_storage:
        totals = save_transaction_stats(transaction, stats_date, totals, category_totals)

    return totals[0], totals[1], totals[2], category_totals


def save_transaction_stats(
    transaction: dict[str, TransactionValue],
    stats_date: DateTuple,
    totals: TotalsData,
    category_totals: dict[str, int],
) -> TotalsData:
    transaction_data = extract_transaction_data(transaction)
    if transaction_data is None:
        return totals
    if not is_not_later(transaction_data[1], stats_date):
        return totals

    return save_valid_transaction_stats(transaction_data, stats_date, totals, category_totals)


def save_valid_transaction_stats(
    transaction_data: TransactionData,
    stats_date: DateTuple,
    totals: TotalsData,
    category_totals: dict[str, int],
) -> TotalsData:
    updated_totals = save_capital_stats(totals, transaction_data)
    if not is_same_month(transaction_data[1], stats_date):
        return updated_totals
    return save_month_stats(updated_totals, category_totals, transaction_data)


def save_capital_stats(totals: TotalsData, transaction_data: TransactionData) -> TotalsData:
    capital, month_income, month_cost = totals
    amount = transaction_data[0]
    if is_income_transaction(transaction_data):
        return capital + amount, month_income, month_cost
    return capital - amount, month_income, month_cost


def save_month_stats(
    totals: TotalsData,
    category_totals: dict[str, int],
    transaction_data: TransactionData,
) -> TotalsData:
    capital, month_income, month_cost = totals
    amount = transaction_data[0]
    if is_income_transaction(transaction_data):
        return capital, month_income + amount, month_cost

    save_category_total(
        category_totals,
        get_target_category(get_transaction_category(transaction_data)),
        amount,
    )
    return capital, month_income, month_cost + amount


def is_income_transaction(transaction_data: TransactionData) -> bool:
    return transaction_data[2] is None


def get_transaction_category(transaction_data: TransactionData) -> str:
    category_name = transaction_data[2]
    if category_name is None:
        return ""
    return category_name


def extract_transaction_data(transaction: dict[str, TransactionValue]) -> TransactionData | None:
    amount_value = transaction.get("amount")
    if not isinstance(amount_value, int | float):
        return None

    transaction_date = extract_transaction_date(transaction.get("date"))
    if transaction_date is None:
        return None

    category_value = transaction.get("category")
    if category_value is not None and not isinstance(category_value, str):
        return None

    return convert_to_copecks(float(amount_value)), transaction_date, category_value


def extract_transaction_date(date_value: TransactionValue | None) -> DateTuple | None:
    if not isinstance(date_value, tuple) or len(date_value) != DATE_PARTS_COUNT:
        return None

    day_value, month_value, year_value = date_value
    if not isinstance(day_value, int):
        return None
    if not isinstance(month_value, int):
        return None
    if not isinstance(year_value, int):
        return None
    return day_value, month_value, year_value


def convert_to_copecks(amount: float) -> int:
    return round(amount * COPECKS_IN_RUBLE)


def save_category_total(category_totals: dict[str, int], category_name: str, amount: int) -> None:
    current_total = category_totals.get(category_name, 0)
    category_totals[category_name] = current_total + amount


def get_target_category(category_name: str) -> str:
    return category_name.split("::", maxsplit=1)[1]


def build_stats_report(stats_date_text: str, stats_data: StatsData) -> str:
    report_lines = get_report_lines(stats_date_text, stats_data)
    add_category_lines(report_lines, stats_data[3])
    return "\n".join(report_lines)


def get_report_lines(stats_date_text: str, stats_data: StatsData) -> list[str]:
    month_result = stats_data[1] - stats_data[2]
    formatted_month_result = format_total(abs(month_result))
    return [
        f"Your statistics as of {stats_date_text}:",
        f"Total capital: {format_total(stats_data[0])} rubles",
        f"{get_result_line(month_result)} {formatted_month_result} rubles.",
        f"Income: {format_total(stats_data[1])} rubles",
        f"Expenses: {format_total(stats_data[2])} rubles",
        "",
        "Details (category: amount):",
    ]


def get_result_line(month_result: int) -> str:
    if month_result < 0:
        return LOSS_MSG
    return PROFIT_MSG


def add_category_lines(report_lines: list[str], category_totals: dict[str, int]) -> None:
    for number, category_name in enumerate(sorted(category_totals), start=1):
        category_total = category_totals[category_name]
        report_lines.append(f"{number}. {category_name}: {format_category_total(category_total)}")


def is_same_month(first_date: DateTuple, second_date: DateTuple) -> bool:
    return get_month_key(first_date) == get_month_key(second_date)


def get_month_key(date_tuple: DateTuple) -> tuple[int, int]:
    return date_tuple[1], date_tuple[2]


def is_not_later(left_date: DateTuple, right_date: DateTuple) -> bool:
    return get_date_key(left_date) <= get_date_key(right_date)


def get_date_key(date_tuple: DateTuple) -> tuple[int, int, int]:
    day, month, year = date_tuple
    return year, month, day


def format_total(value: int) -> str:
    rubles = value / COPECKS_IN_RUBLE
    return f"{rubles:.2f}"


def format_category_total(value: int) -> str:
    if value % COPECKS_IN_RUBLE == 0:
        return str(value // COPECKS_IN_RUBLE)

    rubles = value / COPECKS_IN_RUBLE
    formatted_total = f"{rubles:.2f}"
    return formatted_total.rstrip("0").rstrip(".")


def handle_command(command_parts: list[str]) -> str:
    if not command_parts:
        return UNKNOWN_COMMAND_MSG
    if command_parts[0] == "income":
        return handle_income_command(command_parts)
    if command_parts[0] == "cost":
        return handle_cost_command(command_parts)
    if command_parts[0] == "stats":
        return handle_stats_command(command_parts)
    return UNKNOWN_COMMAND_MSG


def handle_income_command(command_parts: list[str]) -> str:
    if len(command_parts) != INCOME_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = extract_amount(command_parts[1])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    return income_handler(amount, command_parts[2])


def handle_cost_command(command_parts: list[str]) -> str:
    if len(command_parts) == STATS_COMMAND_PARTS_COUNT and command_parts[1] == "categories":
        return cost_categories_handler()
    if len(command_parts) != COST_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG
    if not is_existing_category(command_parts[1]):
        return f"{save_failed_transaction(NOT_EXISTS_CATEGORY)}\n{cost_categories_handler()}"

    amount = extract_amount(command_parts[2])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    return cost_handler(command_parts[1], amount, command_parts[3])


def handle_stats_command(command_parts: list[str]) -> str:
    if len(command_parts) != STATS_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(command_parts[1])


def main() -> None:
    raw_command = input().strip()
    while raw_command:
        print(handle_command(raw_command.split()))
        raw_command = input().strip()


if __name__ == "__main__":
    main()
