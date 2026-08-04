# Исключения в Java

# Назначение исключений

Исключение сообщает, что метод не смог нормально выполнить свою работу.

Оно отделяет основной сценарий программы от обработки ошибок и переносит сведения
о проблеме по стеку вызовов до уровня, который способен на неё отреагировать.

```java
public User getUser(long userId) {
    return userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));
}
```

Если `UserNotFoundException` не перехвачено в `getUser()`, оно не теряется.
Исключение поднимается вверх по стеку вызовов.

```text
контроллер
    ↓ вызывает
сервис
    ↓ вызывает
репозиторий

репозиторий выбрасывает исключение
    ↑
сервис не перехватил
    ↑
контроллер не перехватил
    ↑
глобальный обработчик формирует HTTP-ответ
```

# Иерархия Throwable

Корнем иерархии ошибок является `Throwable`.

```text
Throwable
├── Error
└── Exception
    ├── RuntimeException
    └── остальные Exception
```

Только объекты `Throwable` и его наследников можно выбрасывать через `throw`.

## Error

`Error` обычно означает серьёзную проблему среды выполнения или JVM.

Примеры:

```text
OutOfMemoryError
StackOverflowError
NoClassDefFoundError
```

Прикладной код обычно не способен корректно восстановиться после таких проблем.
Поэтому `Error` обычно не перехватывают.

## Exception

`Exception` описывает ошибки, которые относятся к выполнению приложения.

Примеры:

```text
IOException
SQLException
IllegalArgumentException
UserNotFoundException
```

Часть таких исключений компилятор требует обработать, а часть нет.

## RuntimeException

`RuntimeException` является базовым классом unchecked-исключений прикладного уровня.

Часто они обозначают:

- нарушение контракта метода
- некорректное состояние объекта
- отсутствие ожидаемой сущности
- программную ошибку

```java
throw new IllegalArgumentException("reporterId must be positive");
```

# Error и Exception

| Критерий | Error | Exception |
|---|---|---|
| Смысл | серьёзная проблема JVM или окружения | ошибка выполнения приложения |
| Ожидаемое восстановление | обычно невозможно | часто возможно обработать или преобразовать |
| Нужно ли обычно ловить | нет | зависит от ситуации |
| Примеры | `OutOfMemoryError` | `IOException`, `IllegalArgumentException` |

`Error` тоже является unchecked с точки зрения компилятора, но это не делает его
обычным способом описания бизнес-ошибок.

# Checked и unchecked exceptions

## Checked exceptions

Checked exception компилятор заставляет обработать одним из двух способов:

- перехватить через `try-catch`
- объявить через `throws`

```java
public String readTemplate(Path path) throws IOException {
    return Files.readString(path);
}
```

Примеры checked exceptions:

```text
IOException
SQLException
ClassNotFoundException
```

## Unchecked exceptions

Unchecked exception не требуется объявлять или перехватывать.

К ним относятся:

- `RuntimeException` и его наследники
- `Error` и его наследники

```java
public Incident getIncident(long incidentId) {
    return incidentRepository.findById(incidentId)
            .orElseThrow(() -> new IncidentNotFoundException(incidentId));
}
```

## Как определить checked exception

Нужно посмотреть на иерархию класса.

```text
наследник RuntimeException → unchecked
наследник Error            → unchecked
остальной наследник Exception → checked
```

Само наличие слова `Exception` в имени ничего не доказывает.

# throw и throws

`throw` выбрасывает конкретный объект исключения.

```java
if (reporterId <= 0) {
    throw new IllegalArgumentException("reporterId must be positive");
}
```

`throws` объявляет в сигнатуре метода возможность выхода исключения.

```java
public Incident importIncident(Path path) throws IOException {
    String content = Files.readString(path);
    return parseIncident(content);
}
```

```text
throw  → действие внутри метода
throws → часть объявления метода
```

Объявлять unchecked exception через `throws` разрешено, но компилятор этого не
требует. Иногда такое объявление используют как документацию контракта.

# Распространение по стеку вызовов

Когда выполняется `throw`, нормальное выполнение текущего блока прекращается.
JVM ищет подходящий `catch` сначала в текущем методе, затем в вызывающем и далее
вверх по стеку.

```java
public IncidentResponse findIncident(long incidentId) {
    Incident incident = incidentService.getIncident(incidentId);
    return mapper.toResponse(incident);
}
```

Если `getIncident()` выбросит `IncidentNotFoundException`, строка с `mapper` не
выполнится. При отсутствии локального `catch` исключение перейдёт вызывающему коду.

Если подходящего обработчика нет во всём потоке, поток завершается. Перед этим
стандартный обработчик обычно выводит stack trace.

# Stack trace

Stack trace показывает тип исключения, сообщение и цепочку вызовов.

```text
IncidentNotFoundException: Incident not found: 42
    at IncidentService.getIncident(IncidentService.java:31)
    at IncidentController.getIncident(IncidentController.java:24)
    at ...
Caused by: java.sql.SQLException: connection closed
    at ...
```

Порядок чтения:

1. Прочитать тип и сообщение верхнего исключения
2. Найти первую строку `at` из собственного кода
3. Проследить путь вызовов сверху вниз
4. Изучить секции `Caused by`, начиная с самой глубокой причины
5. Проверить секцию `Suppressed`, если она есть

Первая строка стека обычно указывает место создания или выбрасывания исключения.
Это не обязательно место, где находится первопричина ошибки в данных или логике.

# try-catch

`try` содержит код, который может завершиться исключением. `catch` обрабатывает
подходящий тип исключения.

```java
try {
    String content = Files.readString(path);
    importService.importIncident(content);
} catch (IOException exception) {
    throw new IncidentImportException("Cannot read " + path, exception);
}
```

`catch` нужен только тогда, когда текущий уровень способен:

- восстановиться и продолжить работу
- преобразовать исключение в ошибку своего уровня
- дополнить ошибку полезным контекстом
- выполнить осмысленную компенсацию

Если уровень ничего из этого не делает, исключению обычно дают подняться выше.

# Порядок нескольких catch

Блоки `catch` располагают от конкретного типа к общему.

```java
try {
    importIncident(path);
} catch (NoSuchFileException exception) {
    handleMissingFile(exception);
} catch (IOException exception) {
    handleReadFailure(exception);
}
```

Обратный порядок не скомпилируется, потому что общий `catch` уже перехватит все
подклассы и сделает конкретный обработчик недостижимым.

# Multi-catch

Одинаковую обработку нескольких несвязанных типов можно записать в одном блоке.

```java
try {
    loadIncident(source);
} catch (IOException | ParseException exception) {
    throw new IncidentImportException("Import failed", exception);
}
```

Типы в multi-catch не должны находиться в отношении предок и потомок.
Переменная исключения внутри такого `catch` фактически является `final`.

# finally

`finally` выполняется после `try` и возможного `catch` независимо от того, было ли
исключение.

```java
Lock lock = new ReentrantLock();
lock.lock();

try {
    updateIncident();
} finally {
    lock.unlock();
}
```

`finally` подходит для освобождения ресурса, если для него нельзя использовать
try-with-resources.

## Почему нельзя использовать return внутри finally

`return` в `finally` может заменить результат из `try` или `catch`.

```java
public int value() {
    try {
        return 1;
    } finally {
        return 2;
    }
}
```

Метод вернёт `2`.

Ещё опаснее то, что `return` в `finally` способен подавить летящее исключение.

```java
public int value() {
    try {
        throw new IllegalStateException("failure");
    } finally {
        return 2;
    }
}
```

Вызывающий код не увидит `IllegalStateException`. Поэтому `return` внутри
`finally` использовать нельзя.

## Когда finally может не выполниться

Гарантия выполнения `finally` не абсолютна. Блок может не выполниться, если:

- процесс принудительно завершён
- вызван `System.exit()`
- JVM аварийно остановилась
- питание или машина отключились
- поток навсегда завис до входа в `finally`

# Try-with-resources

Try-with-resources автоматически закрывает ресурсы.

```java
try (BufferedReader reader = Files.newBufferedReader(path)) {
    return reader.readLine();
}
```

Закрытие выполняется и при успешном завершении, и при исключении. Такой код обычно
короче и безопаснее ручного закрытия в `finally`.

# AutoCloseable

Ресурс для try-with-resources должен реализовывать `AutoCloseable`.

```java
public final class IncidentExport implements AutoCloseable {

    @Override
    public void close() {
        System.out.println("export closed");
    }
}
```

Метод интерфейса:

```java
void close() throws Exception;
```

Более узкий интерфейс `Closeable` предназначен прежде всего для ресурсов ввода и
вывода. Его `close()` объявляет `IOException`.

# Порядок закрытия ресурсов

Несколько ресурсов закрываются в порядке, обратном объявлению.

```java
try (
        InputStream input = Files.newInputStream(source);
        OutputStream output = Files.newOutputStream(target)
) {
    input.transferTo(output);
}
```

```text
создание: input → output
закрытие: output → input
```

# Suppressed exceptions

Если основной код выбросил исключение, а `close()` выбросил другое, основным
остаётся исключение из тела `try`. Исключение из `close()` сохраняется вместе с
ним как suppressed exception.

```text
основное исключение из try
└── suppressed exception из close()
```

```java
try (IncidentExport export = openExport()) {
    throw new IllegalStateException("write failed");
}
```

Получить сохранённые исключения можно так:

```java
for (Throwable suppressed : exception.getSuppressed()) {
    log.debug("Resource closing failed", suppressed);
}
```

Это позволяет не потерять ошибку закрытия и одновременно сохранить исходную
причину сбоя операции.

# Собственные исключения

Собственный тип делает ошибку понятной для вызывающего кода.

```java
public class UserNotFoundException extends RuntimeException {

    public UserNotFoundException(long userId) {
        super("User not found: " + userId);
    }
}
```

```java
public class IncidentNotFoundException extends RuntimeException {

    public IncidentNotFoundException(long incidentId) {
        super("Incident not found: " + incidentId);
    }
}
```

Checked-собственное исключение наследуют от `Exception`, unchecked-собственное
исключение наследуют от `RuntimeException`.

# Cause и оборачивание

При преобразовании исключения нужно сохранять исходную причину.

```java
public class IncidentImportException extends RuntimeException {

    public IncidentImportException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

```java
try {
    return Files.readString(path);
} catch (IOException exception) {
    throw new IncidentImportException(
            "Cannot import incident from " + path,
            exception
    );
}
```

Без `cause` исходный stack trace теряется и диагностика становится сложнее.

# Почему нельзя проглатывать исключения

Пустой `catch` скрывает сбой и позволяет программе продолжить работу с неверным
состоянием.

```java
try {
    updateIncident();
} catch (Exception exception) {
}
```

Вызывающий код решит, что операция успешна. Транзакция или внешний ответ могут не
соответствовать фактическому результату.

# Где логировать исключение

Исключение обычно логируют на границе, где оно окончательно обрабатывается.

Примеры таких границ:

- глобальный HTTP-обработчик
- обработчик сообщения из очереди
- планировщик фоновой задачи
- верхний уровень отдельной команды

На нижнем уровне исключение можно дополнить контекстом и пробросить с `cause`, не
логируя его повторно.

## Почему не следует логировать и пробрасывать на каждом слое

Если одна ошибка логируется в репозитории, сервисе, контроллере и глобальном
обработчике, журнал получает несколько stack trace для одного события.

```text
одна ошибка
→ четыре одинаковых записи
→ шум и ложное ощущение нескольких сбоев
```

Правило по умолчанию:

> Либо обработай и залогируй, либо преобразуй и пробрось с причиной.

# Когда допустим catch Exception

`catch (Exception)` допустим на верхней границе независимой операции, где нужно
не дать одному сбою остановить весь механизм.

```java
public void runScheduledImport() {
    try {
        importService.importAll();
    } catch (Exception exception) {
        log.error("Scheduled incident import failed", exception);
    }
}
```

Он также бывает оправдан при адаптации API, если после перехвата ошибка корректно
преобразуется. В обычной бизнес-логике лучше ловить ожидаемые конкретные типы.

`catch (Throwable)` почти всегда ошибочен, потому что дополнительно ловит `Error`.

# Стандартные unchecked exceptions

## IllegalArgumentException

`IllegalArgumentException` означает, что переданный аргумент нарушает контракт
метода.

```java
public Incident createIncident(long reporterId) {
    if (reporterId <= 0) {
        throw new IllegalArgumentException(
                "reporterId must be positive"
        );
    }

    return createForReporter(reporterId);
}
```

Проверка формата или диапазона аргумента подходит для этого типа. Отсутствие
пользователя с корректным ID лучше выразить `UserNotFoundException`.

## IllegalStateException

`IllegalStateException` означает, что операция недопустима в текущем состоянии
объекта или системы.

```java
public void resolve() {
    if (status != IncidentStatus.IN_PROGRESS) {
        throw new IllegalStateException(
                "Only an incident in progress can be resolved"
        );
    }

    status = IncidentStatus.RESOLVED;
}
```

```text
неверный входной аргумент → IllegalArgumentException
недопустимое текущее состояние → IllegalStateException
```

## NullPointerException и Objects.requireNonNull

`NullPointerException` возникает при использовании `null` там, где ожидается
объект. Для ранней проверки обязательного аргумента применяют
`Objects.requireNonNull()`.

```java
public IncidentService(IncidentRepository incidentRepository) {
    this.incidentRepository = Objects.requireNonNull(
            incidentRepository,
            "incidentRepository must not be null"
    );
}
```

Проверка даёт сбой ближе к источнику ошибки и добавляет понятное сообщение.
Для проверки бизнес-полей DTO часто лучше использовать Bean Validation.

# Исключения и транзакции Spring

Для транзакции, открытой через `@Transactional`, поведение по умолчанию такое:

```text
RuntimeException → rollback
Error            → rollback
checked exception → rollback по умолчанию не гарантирован
```

```java
@Transactional
public Incident createIncident(
        String title,
        String description,
        String category,
        IncidentPriority priority,
        long reporterId
) {
    User reporter = userRepository.findById(reporterId)
            .orElseThrow(() -> new UserNotFoundException(reporterId));

    return incidentRepository.save(new Incident(
            title,
            description,
            category,
            priority,
            reporter
    ));
}
```

`UserNotFoundException` наследуется от `RuntimeException`, поэтому исключение,
вышедшее из транзакционного метода, по умолчанию приводит к rollback.

Для checked exception правило можно задать явно.

```java
@Transactional(rollbackFor = IOException.class)
public void importIncidents(Path path) throws IOException {
    importFrom(path);
}
```

Важно, чтобы исключение вышло за границу транзакционного вызова. Если метод
перехватил и проглотил ошибку, инфраструктура может считать вызов успешным.

## Почему бизнес-исключения обычно unchecked

В Spring бизнес-исключения часто наследуют от `RuntimeException`, потому что:

- вызывающий уровень редко способен продолжить тот же сценарий
- сигнатуры сервисов не перегружаются `throws`
- стандартное правило транзакций выполняет rollback
- исключения удобно преобразовывать в HTTP-ответ глобальным обработчиком

Это соглашение, а не требование языка. Тип исключения должен соответствовать
контракту приложения.

## Self-invocation и proxy

Spring обычно применяет `@Transactional` через proxy. Внутренний вызов одного
метода класса из другого метода того же объекта обходит proxy. Поэтому транзакция,
ожидаемая только из аннотации на вызываемом внутреннем методе, может не начаться.

```text
внешний вызов через proxy → транзакционный перехватчик работает
self-invocation через this → proxy не участвует
```

# Checked exceptions внутри Stream API

Стандартный `Function<T, R>` не объявляет checked exception в сигнатуре.

```java
R apply(T value);
```

Поэтому `IOException` нельзя напрямую пробросить из lambda, переданной в `map()`.

```java
paths.stream()
        .map(path -> Files.readString(path))
        .toList();
```

Такой код не скомпилируется. Исключение нужно обработать или обернуть.

```java
List<String> contents = paths.stream()
        .map(path -> {
            try {
                return Files.readString(path);
            } catch (IOException exception) {
                throw new UncheckedIOException(exception);
            }
        })
        .toList();
```

Если обработка становится громоздкой, обычный цикл или отдельный метод часто
понятнее pipeline.

# Когда следует перехватывать исключение

Перехватывать исключение следует, когда текущий уровень знает, что делать дальше.

```text
можно повторить безопасную операцию
можно выбрать допустимое резервное значение
можно преобразовать техническую ошибку в ошибку уровня приложения
можно добавить важный контекст и сохранить cause
можно сформировать окончательный внешний ответ
```

Перехват только ради того, чтобы немедленно бросить то же исключение, бесполезен.

# Исключения не заменяют обычное управление потоком

Исключение предназначено для ненормальной ситуации. Ожидаемое ветвление лучше
выражать условием, циклом или подходящим возвращаемым типом.

```java
if (users.isEmpty()) {
    return List.of();
}
```

Использование исключений для ожидаемых проверок:

- скрывает намерение кода
- создаёт и обрабатывает stack trace
- усложняет отладку и метрики ошибок
- смешивает штатный и аварийный сценарии

# Типичные ошибки

## Пустой catch

Ошибка исчезает для вызывающего кода, а программа продолжает работу с неясным
результатом.

## Перехват слишком общего типа

`catch (Exception)` в глубине бизнес-логики скрывает разные причины под одной
обработкой.

## Неверный порядок catch

Общий тип до конкретного делает конкретный обработчик недостижимым.

## Потеря cause

```java
throw new IncidentImportException("Import failed");
```

При оборачивании нужно передать исходное исключение в конструктор.

## Логирование на каждом слое

Одна ошибка создаёт множество одинаковых записей и затрудняет диагностику.

## return в finally

Он способен заменить возвращаемое значение и подавить исключение.

## Ручное закрытие вместо try-with-resources

Ручной код легко теряет исключение закрытия или не закрывает ресурс на одной из
ветвей.

## Неверное ожидание rollback

Checked exception без `rollbackFor` может не откатить Spring-транзакцию.

## Проглатывание исключения в транзакционном методе

Если ошибка не вышла из метода, proxy может завершить транзакцию как успешную.

## Исключения как обычная ветка

Ожидаемое отсутствие результата или проверку состояния не стоит строить на
дорогом и неявном механизме исключений без необходимости.

# Краткий ответ для собеседования

Исключения в Java представлены иерархией `Throwable`. `Error` обычно описывает
серьёзные проблемы JVM, а `Exception` ошибки приложения. Checked-исключения нужно
перехватить или объявить через `throws`. `RuntimeException` и `Error` являются
unchecked. Неперехваченное исключение поднимается вверх по стеку до подходящего
`catch`.

Ловить исключение нужно там, где его можно обработать, преобразовать или дополнить
контекстом. Ресурсы следует закрывать через try-with-resources. Он закрывает их в
обратном порядке и сохраняет ошибку `close()` как suppressed, если уже существует
основная ошибка. При оборачивании нужно передавать `cause`.

В Spring `RuntimeException` и `Error` по умолчанию вызывают rollback, а checked
exception может потребовать `rollbackFor`. Бизнес-исключения поэтому часто делают
unchecked.

---

# Краткая памятка

```text
Throwable
├── Error → unchecked
└── Exception
    ├── RuntimeException → unchecked
    └── остальные → checked
```

```text
throw  → выбросить объект исключения
throws → объявить возможность исключения
```

```text
catch
→ обработать
→ преобразовать
→ дополнить контекстом

иначе исключение поднимается выше
```

```text
несколько catch
→ от конкретного к общему
```

```text
try-with-resources
→ ресурсы закрываются в обратном порядке
→ ошибка close сохраняется как suppressed
```

```text
оборачивание
→ передать cause
```

```text
Spring @Transactional по умолчанию
RuntimeException → rollback
Error            → rollback
checked exception → rollbackFor при необходимости
```

---

# Вопросы для самопроверки

1. Для чего нужны исключения?
2. Как устроена иерархия `Throwable`?
3. Чем `Error` отличается от `Exception`?
4. Какие исключения являются checked и unchecked?
5. Как по иерархии определить checked exception?
6. Чем `throw` отличается от `throws`?
7. Что происходит с неперехваченным исключением?
8. В каком порядке следует читать stack trace?
9. Когда текущему уровню нужен `catch`?
10. Почему `catch` располагают от конкретного типа к общему?
11. Какие ограничения есть у multi-catch?
12. Для чего нужен `finally`?
13. Почему опасен `return` внутри `finally`?
14. В каких случаях `finally` может не выполниться?
15. Как работает try-with-resources?
16. Какую роль играет `AutoCloseable`?
17. В каком порядке закрываются несколько ресурсов?
18. Что такое suppressed exception?
19. Когда собственное исключение наследуют от `RuntimeException`?
20. Почему при оборачивании нужно передавать `cause`?
21. Почему нельзя проглатывать исключения?
22. На каком уровне обычно логируют исключение?
23. Почему не стоит логировать и пробрасывать одну ошибку на каждом слое?
24. Когда допустим `catch (Exception)`?
25. Чем `IllegalArgumentException` отличается от `IllegalStateException`?
26. Для чего нужен `Objects.requireNonNull()`?
27. Какие исключения по умолчанию вызывают rollback в Spring?
28. Как включить rollback для checked exception?
29. Почему бизнес-исключения в Spring часто являются unchecked?
30. Почему self-invocation может помешать работе `@Transactional`?
31. Почему `Function<T, R>` не принимает lambda с `IOException` напрямую?
32. Почему исключения не используют для обычного управления потоком?
