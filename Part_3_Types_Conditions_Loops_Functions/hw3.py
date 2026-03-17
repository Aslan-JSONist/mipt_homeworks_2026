#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

UNKNOWN_COMMAND_OUTPUT = "Неизвестная команда!"
NONPOSITIVE_VALUE_OUTPUT = "Значение должно быть больше нуля!"
INCORRECT_DATE_OUTPUT = "Неправильная дата!"
OP_SUCCESS_OUTPUT = "Добавлено"
PROFIT_OUTPUT = "\u0412 этом месяце прибыль составила"
LOSS_OUTPUT = "\u0412 этом месяце убыток составил"

DATE_PARTS_COUNT = 3
SHORT_DATE_PART_LENGTH = 2
YEAR_PART_LENGTH = 4
MONTHS_IN_YEAR = 12
FEBRUARY = 2
INCOME_COMMAND_PARTS_COUNT = 3
COST_COMMAND_PARTS_COUNT = 4
STATS_COMMAND_PARTS_COUNT = 2
MAX_NUMBER_PARTS = 2
COPECKS_IN_RUBLE = 100

DateTuple = tuple[int, int, int]
IncomeEntry = tuple[int, DateTuple]
CostEntry = tuple[str, int, DateTuple]
StatsData = tuple[int, int, int, dict[str, int]]
IncomeStats = tuple[int, int]
CostStats = tuple[int, int, dict[str, int]]


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
        return NONPOSITIVE_VALUE_OUTPUT
    if extract_date(income_date) is None:
        return INCORRECT_DATE_OUTPUT
    return OP_SUCCESS_OUTPUT


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


def extract_amount(maybe_amount: str) -> int | None:
    normalized_number = normalize_number(maybe_amount)
    if normalized_number is None:
        return None
    return round(float(normalized_number) * COPECKS_IN_RUBLE)


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


def build_stats_report(
    incomes: list[IncomeEntry],
    costs: list[CostEntry],
    stats_date: DateTuple,
    stats_date_text: str,
) -> str:
    stats_data = get_stats_data(incomes, costs, stats_date)
    report_lines = get_report_lines(stats_date_text, stats_data)
    add_category_lines(report_lines, stats_data[3])
    return "\n".join(report_lines)


def get_stats_data(
    incomes: list[IncomeEntry],
    costs: list[CostEntry],
    stats_date: DateTuple,
) -> StatsData:
    income_capital, month_income = get_income_stats(incomes, stats_date)
    cost_capital, month_cost, category_totals = get_cost_stats(costs, stats_date)
    return income_capital - cost_capital, month_income, month_cost, category_totals


def get_income_stats(incomes: list[IncomeEntry], stats_date: DateTuple) -> IncomeStats:
    capital_income = 0
    month_income = 0

    for income_entry in incomes:
        if is_not_later(get_income_date(income_entry), stats_date):
            capital_income += get_income_amount(income_entry)
            if is_same_month(get_income_date(income_entry), stats_date):
                month_income += get_income_amount(income_entry)
    return capital_income, month_income


def get_cost_stats(costs: list[CostEntry], stats_date: DateTuple) -> CostStats:
    capital_cost = 0
    month_cost = 0
    category_totals: dict[str, int] = {}

    for cost_entry in costs:
        if is_not_later(get_cost_date(cost_entry), stats_date):
            capital_cost += get_cost_amount(cost_entry)
            if is_same_month(get_cost_date(cost_entry), stats_date):
                month_cost += get_cost_amount(cost_entry)
                save_category_total(
                    category_totals,
                    get_cost_category(cost_entry),
                    get_cost_amount(cost_entry),
                )
    return capital_cost, month_cost, category_totals


def get_income_amount(income_entry: IncomeEntry) -> int:
    return income_entry[0]


def get_income_date(income_entry: IncomeEntry) -> DateTuple:
    return income_entry[1]


def get_cost_category(cost_entry: CostEntry) -> str:
    return cost_entry[0]


def get_cost_amount(cost_entry: CostEntry) -> int:
    return cost_entry[1]


def get_cost_date(cost_entry: CostEntry) -> DateTuple:
    return cost_entry[2]


def save_category_total(category_totals: dict[str, int], category_name: str, amount: int) -> None:
    current_total = category_totals.get(category_name, 0)
    category_totals[category_name] = current_total + amount


def get_report_lines(stats_date_text: str, stats_data: StatsData) -> list[str]:
    capital, month_income, month_cost, _ = stats_data
    month_result = month_income - month_cost
    return [
        f"Ваша статистика по состоянию на {stats_date_text}:",
        f"Суммарный капитал: {format_total(capital)} рублей",
        f"{get_result_line(month_result)} {format_total(abs(month_result))} рублей",
        f"Доходы: {format_total(month_income)} рублей",
        f"Расходы: {format_total(month_cost)} рублей",
        "",
        "Детализация (категория: сумма):",
    ]


def add_category_lines(report_lines: list[str], category_totals: dict[str, int]) -> None:
    for number, category_name in enumerate(sorted(category_totals), start=1):
        category_total = category_totals[category_name]
        report_lines.append(f"{number}. {category_name}: {format_category_total(category_total)}")


def get_result_line(month_result: int) -> str:
    if month_result < 0:
        return LOSS_OUTPUT
    return PROFIT_OUTPUT


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


def is_valid_category_name(category_name: str) -> bool:
    return "." not in category_name and "," not in category_name


def handle_income(command_parts: list[str], incomes: list[IncomeEntry]) -> str:
    if len(command_parts) != INCOME_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_OUTPUT

    amount = extract_amount(command_parts[1])
    if amount is None:
        return UNKNOWN_COMMAND_OUTPUT
    if amount <= 0:
        return NONPOSITIVE_VALUE_OUTPUT

    income_date = extract_date(command_parts[2])
    if income_date is None:
        return INCORRECT_DATE_OUTPUT

    incomes.append((amount, income_date))
    return OP_SUCCESS_OUTPUT


def handle_cost(command_parts: list[str], costs: list[CostEntry]) -> str:
    if not has_valid_cost_shape(command_parts):
        return UNKNOWN_COMMAND_OUTPUT

    amount = extract_amount(command_parts[2])
    if amount is None:
        return UNKNOWN_COMMAND_OUTPUT
    if amount <= 0:
        return NONPOSITIVE_VALUE_OUTPUT

    cost_date = extract_date(command_parts[3])
    if cost_date is None:
        return INCORRECT_DATE_OUTPUT

    costs.append((command_parts[1], amount, cost_date))
    return OP_SUCCESS_OUTPUT


def has_valid_cost_shape(command_parts: list[str]) -> bool:
    if len(command_parts) != COST_COMMAND_PARTS_COUNT:
        return False
    return is_valid_category_name(command_parts[1])


def handle_stats(
    command_parts: list[str],
    incomes: list[IncomeEntry],
    costs: list[CostEntry],
) -> str:
    if len(command_parts) != STATS_COMMAND_PARTS_COUNT:
        return UNKNOWN_COMMAND_OUTPUT

    stats_date = extract_date(command_parts[1])
    if stats_date is None:
        return INCORRECT_DATE_OUTPUT

    return build_stats_report(incomes, costs, stats_date, command_parts[1])


def handle_command(
    command_parts: list[str],
    incomes: list[IncomeEntry],
    costs: list[CostEntry],
) -> str:
    if not command_parts:
        return UNKNOWN_COMMAND_OUTPUT
    if command_parts[0] == "income":
        return handle_income(command_parts, incomes)
    if command_parts[0] == "cost":
        return handle_cost(command_parts, costs)
    if command_parts[0] == "stats":
        return handle_stats(command_parts, incomes, costs)
    return UNKNOWN_COMMAND_OUTPUT


def main() -> None:
    incomes: list[IncomeEntry] = []
    costs: list[CostEntry] = []

    raw = input().strip()
    while raw:
        print(handle_command(raw.split(), incomes, costs))
        raw = input().strip()


if __name__ == "__main__":
    main()
