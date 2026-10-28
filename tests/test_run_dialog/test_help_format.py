"""Тесты подсветки markdown-справки в терминале."""

from app.run_dialog.help_format import colorize_markdown
from cfg.color import Colors


def test_heading_colored_by_level() -> None:
    """Заголовки разных уровней получают свои цвета, решётки убираются."""
    assert colorize_markdown('# Заголовок\n') == f'{Colors.HEADER}{Colors.BOLD}Заголовок{Colors.END_COLOR}\n'
    assert colorize_markdown('## Раздел\n') == f'{Colors.OK_BLUE}{Colors.BOLD}Раздел{Colors.END_COLOR}\n'
    assert colorize_markdown('### Подпункт\n') == f'{Colors.OK_CYAN}{Colors.BOLD}Подпункт{Colors.END_COLOR}\n'
    assert colorize_markdown('#### Глубокий\n') == f'{Colors.OK_GREEN}{Colors.BOLD}Глубокий{Colors.END_COLOR}\n'


def test_plain_line_unchanged() -> None:
    """Обычная строка без разметки остаётся как есть."""
    assert colorize_markdown('обычный текст\n') == 'обычный текст\n'


def test_inline_bold_code_and_link() -> None:
    """Жирный, инлайн-код и ссылка обрамляются своими кодами."""
    colored = colorize_markdown('см. **важно** и `код` и [ссылка](http://x)\n')
    assert f'{Colors.BOLD}важно{Colors.END_COLOR}' in colored
    assert f'{Colors.OK_CYAN}код{Colors.END_COLOR}' in colored
    assert f'ссылка ({Colors.UNDERLINE}http://x{Colors.END_COLOR})' in colored


def test_internal_anchor_link_hides_address() -> None:
    """Внутренняя ссылка-якорь показывает только подпись, без `#...`."""
    colored = colorize_markdown('- [Раздел](#раздел)\n')
    assert colored == f'- {Colors.UNDERLINE}Раздел{Colors.END_COLOR}\n'


def test_fenced_code_block_is_colored() -> None:
    """Строки внутри блока ``` красятся, как и открывающая/закрывающая кавычки."""
    colored = colorize_markdown('```\nключ: значение\n```\n')
    assert f'{Colors.WARNING}```{Colors.END_COLOR}' in colored
    assert f'{Colors.OK_GREEN}ключ: значение{Colors.END_COLOR}' in colored


def test_output_ends_with_newline() -> None:
    """Итог всегда завершается переводом строки, даже если исходник без него."""
    assert colorize_markdown('текст').endswith('\n')
