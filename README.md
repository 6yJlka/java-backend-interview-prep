# Java Backend Interview Preparation

Теоретический репозиторий для системной подготовки к техническим интервью на
позиции Java Backend Developer.

Здесь собраны конспекты, а не учебные проекты. Код встречается только внутри
теории — как иллюстрация к разбираемому механизму.

## Направления подготовки

- Java Core
- Collections Framework
- JVM
- Java Concurrency
- Spring Framework
- Spring Boot
- HTTP and REST
- PostgreSQL and SQL
- JPA and Hibernate
- Apache Kafka
- Testing
- Backend Architecture
- System Design
- Docker and CI/CD
- Git

## Прогресс

Полный roadmap со всеми темами и чек-листами:

[`docs/progress/backend-roadmap.md`](docs/progress/backend-roadmap.md)

Краткий tracker текущих статусов:

[`docs/progress/topic-tracker.md`](docs/progress/topic-tracker.md)

## Формат конспекта

Каждая тема разбирается по одной схеме:

1. Определение и назначение.
2. Внутренний механизм работы.
3. Сравнения и таблицы там, где есть выбор между вариантами.
4. Типичные ошибки и распространённые заблуждения.
5. Краткая памятка.
6. Связный краткий ответ для устного собеседования.
7. Вопросы с ответами.
8. Блок «См. также» со ссылками на связанные конспекты.

Приоритет отдаётся точности формулировок. Если утверждение верно только для
конкретной реализации или версии Java, это указывается явно.

## Структура

- `docs/java-core` — Java Core;
- `docs/jvm` — JVM;
- `docs/concurrency` — Java Concurrency и многопоточность;
- `docs/spring` — Spring Framework и Spring Boot;
- `docs/databases` — SQL и PostgreSQL;
- `docs/hibernate` — JPA и Hibernate;
- `docs/kafka` — Apache Kafka;
- `docs/testing` — тестирование;
- `docs/system-design` — архитектура и System Design;
- `docs/progress` — roadmap и прогресс подготовки.

## Соглашения по оформлению

- заголовок первого уровня `#` — только название темы в начале файла;
- разделы — `##`, подразделы — `###`;
- заголовки не нумеруются, чтобы вставка раздела не ломала структуру;
- схемы и перечисления оформляются блоком ` ```text `;
- код — блоком ` ```java `;
- имена файлов конспектов начинаются с порядкового номера внутри директории.

## Алгоритмы

Алгоритмическая подготовка ведётся отдельно в репозитории `java-algorithms-prep`.