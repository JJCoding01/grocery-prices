import logging

from collections.abc import Iterable

from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)


def column_width(worksheet, standard_width=8.43):
    logger.debug(f"format column width for {worksheet}")
    for icol, col in enumerate(worksheet.columns, 1):
        col_letter = get_column_letter(icol)
        width = standard_width
        for cell in col:
            width = max(width, len(str(cell.value)) + 1)
        worksheet.column_dimensions[col_letter].width = width
    return worksheet


def number_format(worksheet, column_letters, format_=None):
    logger.debug(f"format as numbers for {worksheet} ({column_letters})")
    if not isinstance(column_letters, Iterable):
        column_letters = [column_letters]

    columns = [worksheet[letter] for letter in column_letters]
    for column in columns:
        __number_format(column, format_=format_)


def __number_format(column, format_=None):
    if format_ is None:
        format_ = "General"
    if format_ == "Accounting":
        format_ = r'_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'

    for cell in column:
        cell.number_format = format_
