# Stream API в Java

# Что такое Stream API

Stream API предоставляет декларативный способ обработки последовательности
элементов.

Код описывает, какие преобразования нужны, а библиотека управляет обходом.

```java
List<String> activeEmails = users.stream()
        .filter(User::isActive)
        .map(User::getEmail)
        .toList();
```

Stream не является структурой данных. Он представляет вычислительный pipeline.

# Stream и Collection

| Collection | Stream |
|---|---|
| хранит данные | описывает обработку данных |
| может обходиться многократно | используется один раз |
| предоставляет добавление и удаление | не изменяет источник сам по себе |
| обычно вычислена заранее | промежуточные операции ленивы |

```text
Collection → где лежат элементы
Stream     → что сделать с элементами
```

# Структура pipeline

Pipeline состоит из трёх частей:

```text
источник
    ↓
промежуточные операции
    ↓
терминальная операция
```

```java
long criticalCount = incidents.stream()             // источник
        .filter(incident ->                          // промежуточная
                incident.getPriority() == CRITICAL)
        .count();                                    // терминальная
```

Промежуточная операция возвращает новый `Stream` и выполняется лениво.
Терминальная операция запускает pipeline и завершает использование Stream.

# Создание Stream

## collection.stream()

```java
Stream<User> users = userList.stream();
```

## Arrays.stream()

```java
Incident[] incidents = loadIncidents();
Stream<Incident> stream = Arrays.stream(incidents);
```

Для массива примитивов создаётся специализированный stream.

```java
IntStream numbers = Arrays.stream(new int[]{1, 2, 3});
```

## Stream.of()

```java
Stream<String> priorities = Stream.of(
        "LOW",
        "HIGH",
        "CRITICAL"
);
```

## Stream.empty()

```java
Stream<User> users = Stream.empty();
```

Пустой stream удобен вместо `null`.

## Stream.iterate()

`Stream.iterate()` создаёт последовательность по правилу.

```java
List<Integer> numbers = Stream.iterate(1, value -> value + 1)
        .limit(5)
        .toList();
```

Результат:

```text
[1, 2, 3, 4, 5]
```

Без ограничивающей операции такой stream бесконечен.

В Java 9 появился вариант с условием продолжения.

```java
Stream.iterate(1, value -> value <= 5, value -> value + 1)
        .toList();
```

# Ленивость промежуточных операций

Вызов промежуточной операции только строит следующий этап pipeline.

```java
Stream<User> activeUsers = users.stream()
        .filter(user -> {
            System.out.println(user.getId());
            return user.isActive();
        });
```

Пока нет терминальной операции, фильтр не выполняется и строки не печатаются.

```java
List<User> result = activeUsers.toList();
```

Теперь pipeline запускается.

# Поэлементное выполнение pipeline

Операции часто выполняются не отдельными полными проходами, а поэлементно.

```java
users.stream()
        .filter(User::isActive)
        .map(User::getEmail)
        .limit(2)
        .toList();
```

Упрощённо:

```text
user 1 → filter → map → limit
user 2 → filter → отброшен
user 3 → filter → map → limit → достаточно элементов
```

`limit()` может остановить обработку источника раньше.

# filter и Predicate

`filter()` оставляет элементы, для которых условие возвращает `true`.

```java
List<User> activeUsers = users.stream()
        .filter(User::isActive)
        .toList();
```

Он принимает `Predicate<T>`.

```java
boolean test(T value);
```

```java
Predicate<User> active = User::isActive;
```

# map и Function

`map()` преобразует каждый элемент в другой элемент.

```java
List<String> emails = users.stream()
        .map(User::getEmail)
        .toList();
```

Он принимает `Function<T, R>`.

```java
R apply(T value);
```

Тип входного и выходного элемента может отличаться.

```text
User → String
```

# flatMap

`flatMap()` преобразует каждый элемент в stream и объединяет вложенные stream в
один плоский stream.

```java
List<List<String>> groups = List.of(
        List.of("network", "database"),
        List.of("security")
);

List<String> values = groups.stream()
        .flatMap(group -> group.stream())
        .toList();
```

```text
группа 1 → [network, database]
группа 2 → [security]

flatMap
→ [network, database, security]
```

`flatMap` раскрывает вложенные структуры.

# map и flatMap

```java
Stream<Stream<String>> nested = groups.stream()
        .map(List::stream);
```

```java
Stream<String> flat = groups.stream()
        .flatMap(List::stream);
```

```text
map     → один вход превращается в одно значение
flatMap → один вход превращается в несколько значений, затем уровни объединяются
```

# distinct

`distinct()` удаляет дубликаты по `equals()` и `hashCode()`.

```java
List<User> uniqueUsers = users.stream()
        .distinct()
        .toList();
```

Если контракт `equals()` и `hashCode()` нарушен или равенство сущности выбрано
неверно, результат `distinct()` тоже будет неверным.

# sorted и Comparator

Без аргумента `sorted()` использует естественный порядок.

```java
List<String> emails = users.stream()
        .map(User::getEmail)
        .sorted()
        .toList();
```

Пользовательский порядок задаётся через `Comparator`.

```java
List<Incident> sorted = incidents.stream()
        .sorted(Comparator.comparing(Incident::getCreatedAt).reversed())
        .toList();
```

Если элементы не реализуют `Comparable` и comparator не передан, выполнение
завершится `ClassCastException`.

# limit и skip

`limit(n)` оставляет не более первых `n` элементов.

`skip(n)` пропускает первые `n` элементов.

```java
List<Incident> page = incidents.stream()
        .skip(20)
        .limit(10)
        .toList();
```

## Почему это не пагинация в базе данных

Если данные уже загружены в коллекцию, база передала приложению все строки.
`skip()` и `limit()` уменьшают только результат обработки в памяти.

```text
плохой вариант
БД → 1 000 000 строк → Java → skip → limit 20

правильная пагинация
БД → LIMIT и OFFSET или keyset pagination → Java получает 20 строк
```

Пагинацию нужно выполнять запросом репозитория. `partitioningBy()` к пагинации
отношения не имеет.

# peek

`peek()` позволяет наблюдать элементы при прохождении pipeline и главным образом
предназначен для отладки.

```java
List<String> emails = users.stream()
        .filter(User::isActive)
        .peek(user -> log.debug("Active user {}", user.getId()))
        .map(User::getEmail)
        .toList();
```

Из-за ленивости без терминальной операции `peek()` не выполнится.

Бизнес-логику в `peek()` помещать не следует. Её выполнение зависит от устройства
pipeline, short-circuit операций и оптимизаций. Изменение состояния в `peek()`
делает код неочевидным.

# Терминальные операции

## toList

```java
List<String> emails = users.stream()
        .map(User::getEmail)
        .toList();
```

`Stream.toList()` возвращает немодифицируемый список.

```java
emails.add("new@example.com");
```

Результат:

```text
UnsupportedOperationException
```

Контракт `Stream.toList()` допускает `null`, в отличие от некоторых способов
сбора через collectors.

## collect

`collect()` выполняет изменяемое свёртывание результата.

```java
ArrayList<User> activeUsers = users.stream()
        .filter(User::isActive)
        .collect(Collectors.toCollection(ArrayList::new));
```

Так получают явно изменяемый `ArrayList`.

```java
List<User> result = users.stream()
        .collect(Collectors.toList());
```

Для `Collectors.toList()` не гарантируются ни конкретная реализация списка, ни его
изменяемость. Если нужен гарантированно изменяемый `ArrayList`, следует использовать
`Collectors.toCollection(ArrayList::new)`.

## forEach

```java
users.stream()
        .map(User::getEmail)
        .forEach(System.out::println);
```

У parallel stream `forEach()` не гарантирует encounter order. Для сохранения
порядка существует `forEachOrdered()`.

## count

```java
long criticalCount = incidents.stream()
        .filter(incident -> incident.getPriority() == CRITICAL)
        .count();
```

## findFirst и findAny

```java
Optional<Incident> firstCritical = incidents.stream()
        .filter(incident -> incident.getPriority() == CRITICAL)
        .findFirst();
```

`findFirst()` учитывает encounter order. `findAny()` может вернуть любой подходящий
элемент и даёт больше свободы при параллельной обработке.

```java
Incident incident = incidents.stream()
        .filter(value -> value.getId() == incidentId)
        .findFirst()
        .orElseThrow(() -> new IncidentNotFoundException(incidentId));
```

## anyMatch, allMatch и noneMatch

```java
boolean hasCritical = incidents.stream()
        .anyMatch(incident -> incident.getPriority() == CRITICAL);

boolean allActive = users.stream()
        .allMatch(User::isActive);

boolean noActive = users.stream()
        .noneMatch(User::isActive);
```

Эти операции используют короткое замыкание и могут не обходить весь источник.

Для пустого stream `allMatch()` и `noneMatch()` возвращают `true`, а `anyMatch()`
возвращает `false`.

## min и max

```java
Optional<Incident> newest = incidents.stream()
        .max(Comparator.comparing(Incident::getCreatedAt));
```

Результат является `Optional`, потому что stream может быть пустым.

## reduce

`reduce()` объединяет элементы в одно неизменяемое значение.

```java
int totalTitleLength = incidents.stream()
        .map(Incident::getTitle)
        .map(String::length)
        .reduce(0, Integer::sum);
```

Без начального значения результат оборачивается в `Optional`.

```java
Optional<Integer> maximumTitleLength = incidents.stream()
        .map(Incident::getTitle)
        .map(String::length)
        .reduce(Integer::max);
```

# reduce и collect

`reduce()` подходит для комбинирования значений без изменения общего контейнера.

```text
1 + 2 + 3 → 6
```

`collect()` предназначен для накопления в изменяемый контейнер.

```text
элементы → ArrayList
элементы → HashMap
элементы → StringBuilder
```

Изменяемые контейнеры собирают через `collect()`, потому что collector отдельно
описывает создание, накопление и объединение частей результата. Это позволяет
корректно работать и с parallel stream.

Плохой вариант:

```java
List<User> result = users.stream()
        .reduce(
                new ArrayList<>(),
                (list, user) -> {
                    list.add(user);
                    return list;
                },
                (left, right) -> {
                    left.addAll(right);
                    return left;
                }
        );
```

Здесь нарушается идея неизменяемого накопления `reduce()` и появляется опасное
общее изменяемое состояние.

# Collectors.joining

`joining()` соединяет строки.

```java
String emails = users.stream()
        .map(User::getEmail)
        .collect(Collectors.joining(", "));
```

Можно указать разделитель, префикс и суффикс.

```java
String emails = users.stream()
        .map(User::getEmail)
        .collect(Collectors.joining(", ", "[", "]"));
```

# Collectors.groupingBy

`groupingBy()` создаёт группы по произвольному ключу.

```java
Map<IncidentPriority, List<Incident>> byPriority = incidents.stream()
        .collect(Collectors.groupingBy(Incident::getPriority));
```

Количество групп зависит от полученных ключей.

Можно использовать downstream collector.

```java
Map<IncidentPriority, Long> countByPriority = incidents.stream()
        .collect(Collectors.groupingBy(
                Incident::getPriority,
                Collectors.counting()
        ));
```

# Collectors.partitioningBy

`partitioningBy()` делит элементы по boolean-условию.

```java
Map<Boolean, List<User>> usersByActivity = users.stream()
        .collect(Collectors.partitioningBy(User::isActive));
```

Результат содержит две группы с ключами `true` и `false`.

```text
true  → активные пользователи
false → неактивные пользователи
```

## groupingBy и partitioningBy

| Операция | Ключ | Количество групп |
|---|---|---|
| `groupingBy` | произвольный | произвольное |
| `partitioningBy` | `Boolean` | две группы `true` и `false` |

`partitioningBy()` означает разделение по условию и не связано с пагинацией.

# Collectors.toMap

`toMap()` собирает элементы в карту.

```java
Map<Long, User> usersById = users.stream()
        .collect(Collectors.toMap(
                User::getId,
                Function.identity()
        ));
```

```java
Map<String, User> usersByEmail = users.stream()
        .collect(Collectors.toMap(
                User::getEmail,
                Function.identity()
        ));
```

## Duplicate key

Если два элемента дают одинаковый ключ, перегрузка без merge-функции выбросит
`IllegalStateException` с сообщением о повторяющемся ключе.

```text
Duplicate key
```

## Merge-функция

Для ожидаемых повторов нужно явно решить, какое значение сохранить.

```java
Map<String, User> usersByEmail = users.stream()
        .collect(Collectors.toMap(
                User::getEmail,
                Function.identity(),
                (existing, replacement) -> existing
        ));
```

```text
existing    → значение, уже находящееся в Map
replacement → новое значение с тем же ключом
```

Можно сохранить последнее значение.

```java
(existing, replacement) -> replacement
```

Выбор merge-правила должен отражать бизнес-смысл, а не случайно скрывать плохие
данные.

## Почему distinct не решает конфликт ключей

`distinct()` сравнивает целые элементы через `equals()` и `hashCode()`. `toMap()`
определяет конфликт по результату key mapper.

Два разных пользователя могут иметь разные ID и не быть равными, но возвращать
одинаковый email. Они пройдут `distinct()`, после чего `toMap()` обнаружит
повторяющийся ключ. Поэтому `distinct()` не является универсальным решением.

# Method references

Method reference является компактной записью lambda, когда она только вызывает
существующий метод.

```java
user -> user.isActive()
User::isActive
```

Основные формы:

```java
User::getEmail          // метод экземпляра произвольного объекта типа
userService::activate  // метод конкретного объекта
User::new               // конструктор
Objects::nonNull        // статический метод
```

Method reference не создаёт новый механизм вызова. Он должен соответствовать
сигнатуре функционального интерфейса.

# Одноразовость Stream

После терминальной операции stream закрыт для повторного использования.

```java
Stream<User> stream = users.stream();

long count = stream.count();
List<User> result = stream.toList();
```

Второй вызов завершится `IllegalStateException`.

Для повторной обработки нужно создать новый stream из источника.

# Stateless и stateful операции

Stateless-операции обрабатывают элемент независимо от остальных.

```text
filter
map
peek
```

Stateful-операциям нужно помнить уже встреченные элементы или увидеть значительную
часть источника.

```text
distinct
sorted
limit и skip для упорядоченного parallel stream
```

Например, `sorted()` обычно должен накопить элементы до выдачи отсортированного
результата, а `distinct()` должен отслеживать уже встреченные значения.

# Порядок операций и эффективность

Сначала полезно уменьшить число элементов дешёвой операцией, а затем выполнять
дорогую обработку.

```java
List<IncidentView> views = incidents.stream()
        .filter(incident ->
                incident.getStatus() == IncidentStatus.OPEN)
        .map(expensiveMapper::toView)
        .limit(20)
        .toList();
```

Если `map()` поставить до `filter()`, дорогая трансформация выполнится и для
элементов, которые затем будут отброшены.

Порядок нельзя менять механически. Операции могут зависеть от преобразованного
значения, а `sorted()`, `distinct()` и `limit()` меняют семантику в зависимости от
расположения.

# Побочные эффекты

Lambda с побочным эффектом изменяет состояние вне своего результата.

```java
List<String> emails = new ArrayList<>();

users.stream()
        .map(User::getEmail)
        .forEach(emails::add);
```

Такой код хуже безопасного сбора:

```java
List<String> emails = users.stream()
        .map(User::getEmail)
        .toList();
```

Изменение внешнего `ArrayList` опасно не только для производительности. Оно
создаёт:

- гонки при параллельном выполнении
- потерю или повреждение данных
- зависимость результата от порядка выполнения
- непредсказуемое поведение после изменения pipeline
- сложность тестирования и повторного использования

Даже синхронизированный контейнер не всегда делает алгоритм логически корректным.

# Parallel Stream

Parallel stream разбивает обработку на части и выполняет их параллельно.

```java
long criticalCount = incidents.parallelStream()
        .filter(incident -> incident.getPriority() == CRITICAL)
        .count();
```

Но parallel stream не всегда быстрее. На результат влияют:

- размер источника
- стоимость операции над элементом
- возможность эффективного разделения источника
- необходимость сохранять порядок
- стоимость объединения результатов
- доступное число процессоров и текущая нагрузка

По умолчанию parallel stream использует общую `ForkJoinPool.commonPool()`. Долгая
блокирующая операция может занять её потоки и повлиять на другой код процесса.

Общее изменяемое состояние создаёт гонки.

```java
List<User> result = new ArrayList<>();
users.parallelStream().forEach(result::add);
```

Так делать нельзя.

`parallelStream()` нельзя применять автоматически. Его используют после измерений
на реалистичных данных и проверки корректности. Для запросов к базе или внешним
сервисам обычно нужен явно управляемый механизм конкурентности.

# IntStream, LongStream и DoubleStream

Для примитивов существуют специализированные stream:

```text
IntStream
LongStream
DoubleStream
```

```java
int total = IntStream.of(10, 20, 30).sum();
double average = incidents.stream()
        .mapToInt(incident -> incident.getTitle().length())
        .average()
        .orElse(0.0);
```

Они предоставляют операции `sum()`, `average()` и `summaryStatistics()` без
создания wrapper-объекта для каждого значения.

# Boxing и unboxing

`Stream<Integer>` хранит ссылки на wrapper-объекты. `IntStream` работает с `int`.

```java
IntStream ids = users.stream()
        .mapToInt(user -> Math.toIntExact(user.getId()));
```

Переход к объектному stream:

```java
Stream<Integer> boxed = ids.boxed();
```

Boxing преобразует примитив в wrapper, unboxing выполняет обратное преобразование.
На больших объёмах лишний boxing создаёт дополнительные объекты и нагрузку на GC.

# Optional в Stream API

Операции, которые могут не найти значение, возвращают `Optional`.

```java
Optional<Incident> incident = incidents.stream()
        .filter(value -> value.getId() == incidentId)
        .findFirst();
```

Результат можно обработать явно.

```java
Incident found = incident.orElseThrow(
        () -> new IncidentNotFoundException(incidentId)
);
```

Не следует без проверки вызывать `get()`.

# orElse и orElseGet

Аргумент `orElse()` вычисляется заранее, даже если значение в `Optional` есть.

```java
User user = optionalUser.orElse(createGuestUser());
```

`createGuestUser()` будет вызван всегда.

`orElseGet()` принимает `Supplier` и вычисляет запасное значение только при пустом
`Optional`.

```java
User user = optionalUser.orElseGet(this::createGuestUser);
```

Для дешёвой константы подходит `orElse()`. Для вычисления или побочного эффекта
обычно нужен `orElseGet()`.

# Checked exceptions внутри lambda

Стандартные функциональные интерфейсы Stream API не объявляют checked exceptions.

```java
public interface Function<T, R> {
    R apply(T value);
}
```

Поэтому стандартный `Function<T, R>` не позволяет напрямую пробросить
`IOException`.

```java
paths.stream()
        .map(Files::readString)
        .toList();
```

Такой код не компилируется.

Исключение можно обработать внутри lambda или вынести адаптацию в отдельный метод.

```java
private String readUnchecked(Path path) {
    try {
        return Files.readString(path);
    } catch (IOException exception) {
        throw new UncheckedIOException(exception);
    }
}
```

```java
List<String> contents = paths.stream()
        .map(this::readUnchecked)
        .toList();
```

`UncheckedIOException` сохраняет `IOException` как причину и позволяет передать
сбой через API, не объявляющий checked exception. Если исключение нужно обработать
для каждого элемента отдельно, обычный цикл часто читается лучше.

# Когда обычный цикл лучше

Цикл предпочтительнее, когда:

- алгоритм содержит сложные ветвления
- нужны `break` или `continue`
- требуется изменять несколько связанных состояний
- checked exceptions делают lambda громоздкой
- важен точный пошаговый контроль
- Stream-версия хуже объясняет намерение

```java
for (Incident incident : incidents) {
    if (incident.getStatus() != IncidentStatus.OPEN) {
        continue;
    }

    try {
        exporter.export(incident);
    } catch (IOException exception) {
        handleExportFailure(incident, exception);
    }
}
```

Stream API является инструментом, а не обязательной заменой циклов.

# Типичные ошибки

## Отсутствие терминальной операции

Промежуточные операции остаются ленивыми и ничего не выполняют.

## Повторное использование Stream

После терминальной операции тот же stream использовать нельзя.

## Изменение списка из Stream.toList

Результат `Stream.toList()` немодифицируемый.

## Бизнес-логика в peek

Выполнение `peek()` зависит от фактического прохождения элемента через pipeline.

## Побочные эффекты во внешней коллекции

Результат зависит от порядка, плохо тестируется и становится опасным при
параллельной обработке.

## Автоматический parallelStream

Параллелизм имеет накладные расходы, использует общую pool и может замедлить
операцию.

## toMap без merge-функции

Повторяющийся ключ приводит к `IllegalStateException`.

## distinct перед toMap как универсальное решение

Равенство целых объектов не совпадает с уникальностью выбранного ключа.

## limit и skip после загрузки всех строк

Это не уменьшает объём данных, прочитанных из базы.

## Дорогая операция перед filter

Лишние элементы обрабатываются до того, как будут отброшены.

## reduce для изменяемого контейнера

Списки и карты нужно накапливать через `collect()`.

## Игнорирование Optional

Безусловный `get()` приводит к `NoSuchElementException` для пустого результата.

## Непонимание orElse

Запасное значение вычисляется даже при непустом `Optional`.

## Checked exception напрямую в Function

`Function<T, R>` не объявляет `throws IOException`, поэтому lambda не
компилируется без обработки или оборачивания.

# Краткий ответ для собеседования

Stream API описывает одноразовый pipeline обработки данных. Collection хранит
элементы, а Stream задаёт вычисление над источником. Pipeline состоит из источника,
ленивых промежуточных операций и терминальной операции, которая запускает
вычисление и завершает использование stream.

`filter()` отбирает элементы, `map()` преобразует один элемент в один результат,
а `flatMap()` раскрывает вложенные структуры. Для накопления изменяемых контейнеров
используют `collect()`, для неизменяемого комбинирования значений подходит
`reduce()`. `Stream.toList()` возвращает немодифицируемый список.

Побочные эффекты делают pipeline непредсказуемым и опасным при параллельном
выполнении. `parallelStream()` применяют только после измерений. Стандартный
`Function<T, R>` не позволяет напрямую выбросить checked exception вроде
`IOException`.

---

# Краткая памятка

```text
источник
→ ленивые промежуточные операции
→ терминальная операция
→ stream использован
```

```text
Collection → хранит данные
Stream     → описывает обработку
```

```text
filter  → отбор
map     → преобразование
flatMap → раскрытие вложенности
```

```text
toList → немодифицируемый List

изменяемый ArrayList
→ collect(toCollection(ArrayList::new))
```

```text
reduce  → одно значение
collect → изменяемый контейнер
```

```text
groupingBy    → произвольное количество групп
partitioningBy → true и false
```

```text
toMap + повторяющиеся ключи
→ нужна merge-функция
```

```text
parallelStream
→ не применять автоматически
→ избегать общего изменяемого состояния
→ измерять производительность
```

```text
Function<T, R>
→ не объявляет checked exception
→ IOException обработать или обернуть
```

---

# Вопросы для самопроверки

1. Что такое Stream API?
2. Чем Stream отличается от Collection?
3. Из каких частей состоит pipeline?
4. Какими способами можно создать Stream?
5. Что означает ленивость промежуточных операций?
6. Как выполняется pipeline по элементам?
7. Как связаны `filter()` и `Predicate`?
8. Как связаны `map()` и `Function`?
9. Чем `map()` отличается от `flatMap()`?
10. От чего зависит результат `distinct()`?
11. Как `sorted()` использует `Comparator`?
12. Почему `limit()` и `skip()` не заменяют пагинацию в базе?
13. Для чего предназначен `peek()`?
14. Почему бизнес-логика в `peek()` опасна?
15. Какие операции являются терминальными?
16. Можно ли изменять список из `Stream.toList()`?
17. Как собрать результат в изменяемый `ArrayList`?
18. Чем `reduce()` отличается от `collect()`?
19. Почему изменяемый контейнер собирают через `collect()`?
20. Для чего нужны `joining()`, `groupingBy()` и `partitioningBy()`?
21. Чем `groupingBy()` отличается от `partitioningBy()`?
22. Когда `toMap()` выбрасывает ошибку `Duplicate key`?
23. Как работает merge-функция `toMap()`?
24. Почему `distinct()` не гарантирует уникальность ключей `toMap()`?
25. Какие формы method reference существуют?
26. Почему Stream является одноразовым?
27. Чем stateless-операции отличаются от stateful?
28. Как порядок операций влияет на эффективность и результат?
29. Чем опасны побочные эффекты?
30. Почему нельзя без измерений применять `parallelStream()`?
31. Какую pool обычно использует parallel stream?
32. Для чего нужны `IntStream`, `LongStream` и `DoubleStream`?
33. Что такое boxing и unboxing?
34. Почему `findFirst()` возвращает `Optional`?
35. Чем `orElse()` отличается от `orElseGet()`?
36. Почему `Function<T, R>` не принимает `IOException` напрямую?
37. Для чего используется `UncheckedIOException`?
38. Когда обычный цикл понятнее Stream API?
