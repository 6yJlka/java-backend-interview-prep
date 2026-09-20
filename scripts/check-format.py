#!/usr/bin/env python3
"""
Проверка конспектов на соответствие принятому формату.

Запуск из корня репозитория:

    python3 scripts/check-format.py

Код возврата 1, если есть нарушения — можно повесить на CI.

Что проверяется:
  * ровно один заголовок H1 и он первый
  * нет уровней глубже ###
  * нет пропуска уровня: H1 → ### без ## между ними
  * заголовки не нумерованы (кроме вопросов на собеседовании)
  * присутствуют обязательные блоки концовки и идут в нужном порядке
  * вопросы пронумерованы подряд с единицы и у каждого есть «Ответ:»
  * есть блок «См. также», и все относительные ссылки ведут в существующие файлы
  * нет CRLF и посторонних символов
  * каждый конспект указан в topic-tracker.md и имеет метку уровня
"""

import re
import sys
import unicodedata
from pathlib import Path

DOCS = Path("docs")
SKIP = {"progress"}
TRACKER = DOCS / "progress" / "topic-tracker.md"
LEVELS = {"J", "J+", "M", "S"}

ENDING = [
    "Типичные ошибки",
    "Краткая памятка",
    "Краткий ответ для собеседования",
    "Вопросы на собеседовании",
    "См. также",
]

problems = []


def check(path: Path):
    rel = path.relative_to(Path.cwd()) if path.is_absolute() else path
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()

    def bad(msg):
        problems.append(f"{rel}: {msg}")

    if b"\r\n" in raw:
        bad("CRLF вместо LF")

    for ch in set(text):
        if ord(ch) > 0x2E00 and unicodedata.category(ch)[0] == "L":
            bad(f"посторонний символ {ch!r}")
            break

    # заголовки вне блоков кода
    headings, in_code = [], False
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2).strip()))

    h1 = [h for h in headings if h[1] == 1]
    if len(h1) != 1:
        bad(f"заголовков H1: {len(h1)}, должен быть ровно один")
    elif headings[0][1] != 1:
        bad("файл начинается не с H1")

    for line_no, level, title in headings:
        if level > 3:
            bad(f"строка {line_no}: уровень H{level} — глубже ### не используем")

    prev = None
    for line_no, level, title in headings:
        if prev == 1 and level == 3:
            bad(f"строка {line_no}: пропуск уровня — сразу ### после H1")
        prev = level

    in_questions = False
    for line_no, level, title in headings:
        if level == 2:
            in_questions = title.startswith("Вопросы")
        if level == 2 and re.match(r"^\d+[.)]\s", title):
            bad(f"строка {line_no}: нумерованный раздел «{title}»")
        if level == 3 and not in_questions and re.match(r"^(Ошибка|Шаг|Пример)?\s*\d+[.)]\s", title):
            bad(f"строка {line_no}: нумерованный подзаголовок «{title}»")

    # концовка
    h2 = [t for _, lvl, t in headings if lvl == 2]
    present = [name for name in ENDING if name in h2]
    missing = [name for name in ENDING if name not in h2]
    for name in missing:
        bad(f"нет обязательного блока «{name}»")

    order = [h2.index(name) for name in present]
    if order != sorted(order):
        bad("блоки концовки идут не в порядке: " + " → ".join(present))

    # вопросы
    qs = []
    in_q = False
    for line_no, level, title in headings:
        if level == 2:
            in_q = title.startswith("Вопросы")
            continue
        if in_q and level == 3:
            m = re.match(r"^(\d+)\.\s", title)
            if not m:
                bad(f"строка {line_no}: вопрос без номера — «{title}»")
            else:
                qs.append(int(m.group(1)))

    if qs and qs != list(range(1, len(qs) + 1)):
        bad(f"нумерация вопросов не подряд: {qs}")

    n_answers = text.count("**Ответ:**")
    if qs and n_answers < len(qs):
        bad(f"вопросов {len(qs)}, ответов {n_answers}")

    # ссылки
    for target in re.findall(r"\]\((\.\.?/[^)]+\.md)\)", text):
        if not (path.parent / target).resolve().exists():
            bad(f"битая ссылка: {target}")


def check_tracker(files):
    """Каждый конспект должен быть в трекере и иметь метку уровня."""
    if not TRACKER.exists():
        problems.append(f"{TRACKER}: файл не найден, проверка уровней пропущена")
        return

    text = TRACKER.read_text(encoding="utf-8")

    rows = re.findall(
        r"^\|\s*`([^`]+\.md)`\s*\|\s*([^|]+?)\s*\|",
        text,
        re.M,
    )

    tracked = dict(rows)

    for path in files:
        rel = path.relative_to(DOCS).as_posix()

        if rel == "_template.md":
            continue

        if rel not in tracked:
            problems.append(f"{TRACKER}: конспект не указан в трекере — {rel}")
            continue

        level = tracked[rel]

        if level not in LEVELS:
            problems.append(
                f"{TRACKER}: недопустимая метка уровня «{level}» у {rel}"
                f" (ожидается одна из {', '.join(sorted(LEVELS))})"
            )

    existing = {path.relative_to(DOCS).as_posix() for path in files}

    for rel in tracked:
        if rel not in existing:
            problems.append(f"{TRACKER}: в трекере указан несуществующий файл — {rel}")


def main():
    if not DOCS.exists():
        print("Каталог docs/ не найден — запускайте из корня репозитория.")
        return 1

    files = [p for p in sorted(DOCS.rglob("*.md")) if p.parent.name not in SKIP]
    for p in files:
        check(p)

    check_tracker(files)

    print(f"Проверено файлов: {len(files)}")
    if not problems:
        print("Нарушений нет.")
        return 0

    print(f"Нарушений: {len(problems)}\n")
    for line in problems:
        print("  " + line)
    return 1


if __name__ == "__main__":
    sys.exit(main())