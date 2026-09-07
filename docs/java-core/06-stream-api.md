# Stream API в Java

## Что такое Stream API

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

## Stream и Collection

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

## Структура pipeline

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

## Создание Stream

### collection.stream()

```java
Stream<User> users = userList.stream();
```

### Arrays.stream()

```java
Incident[] incidents = loadIncidents();
Stream<Incident> stream = Arrays.stream(incidents);
```

Для массива примитивов создаётся специализированный stream.

```java
IntStream numbers = Arrays.stream(new int[]{1, 2, 3});
```

### Stream.of()

```java
Stream<String> priorities = Stream.of(
        "LOW",
        "HIGH",
        "CRITICAL"
);
```

### Stream.empty()

```java
Stream<User> users = Stream.empty();
```

Пустой stream удобен вместо `null`.

### Stream.iterate()

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

## Ленивость промежуточных операций

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

## Поэлементное выполнение pipeline

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

## filter и Predicate

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

## map и Function

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

## flatMap

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

## map и flatMap

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

## distinct

`distinct()` удаляет дубликаты по `equals()` и `hashCode()`.

```java
List<User> uniqueUsers = users.stream()
        .distinct()
        .toList();
```

Если контракт `equals()` и `hashCode()` нарушен или равенство сущности выбрано
неверно, результат `distinct()` тоже будет неверным.

## sorted и Comparator

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

## limit и skip

`limit(n)` оставляет не более первых `n` элементов.

`skip(n)` пропускает первые `n` элементов.

```java
List<Incident> page = incidents.stream()
        .skip(20)
        .limit(10)
        .toList();
```

### Почему это не пагинация в базе данных

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

## peek

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

## Терминальные операции

### toList

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

### collect

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

### forEach

```java
users.stream()
        .map(User::getEmail)
        .forEach(System.out::println);
```

У parallel stream `forEach()` не гарантирует encounter order. Для сохранения
порядка существует `forEachOrdered()`.

### count

```java
long criticalCount = incidents.stream()
        .filter(incident -> incident.getPriority() == CRITICAL)
        .count();
```

### findFirst и findAny

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

### anyMatch, allMatch и noneMatch

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

### min и max

```java
Optional<Incident> newest = incidents.stream()
        .max(Comparator.comparing(Incident::getCreatedAt));
```

Результат является `Optional`, потому что stream может быть пустым.

### reduce

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

## reduce и collect

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

## Collectors.joining

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

## Collectors.groupingBy

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

## Collectors.partitioningBy

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

### groupingBy и partitioningBy

| Операция | Ключ | Количество групп |
|---|---|---|
| `groupingBy` | произвольный | произвольное |
| `partitioningBy` | `Boolean` | две группы `true` и `false` |

`partitioningBy()` означает разделение по условию и не связано с пагинацией.

## Collectors.toMap

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

### Duplicate key

Если два элемента дают одинаковый ключ, перегрузка без merge-функции выбросит
`IllegalStateException` с сообщением о повторяющемся ключе.

```text
Duplicate key
```

### Merge-функция

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

### Почему distinct не решает конфликт ключей

`distinct()` сравнивает целые элементы через `equals()` и `hashCode()`. `toMap()`
определяет конфликт по результату key mapper.

Два разных пользователя могут иметь разные ID и не быть равными, но возвращать
одинаковый email. Они пройдут `distinct()`, после чего `toMap()` обнаружит
повторяющийся ключ. Поэтому `distinct()` не является универсальным решением.

## Method references

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

## Одноразовость Stream

После терминальной операции stream закрыт для повторного использования.

```java
Stream<User> stream = users.stream();

long count = stream.count();
List<User> result = stream.toList();
```

Второй вызов завершится `IllegalStateException`.

Для повторной обработки нужно создать новый stream из источника.

## Stateless и stateful операции

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

## Порядок операций и эффективность

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

## Побочные эффекты

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

## Parallel Stream

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

## IntStream, LongStream и DoubleStream

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

## Boxing и unboxing

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

## Optional в Stream API

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

Извлекая значение, важно помнить о различии `orElse()` и `orElseGet()`: аргумент
первого вычисляется всегда, даже когда значение присутствует. Для константы это
безразлично, для запроса к базе или другого дорогого вызова — нет.

```java
String name = incident.map(Incident::getTitle).orElse("не найден");
```

Подробно `Optional` разобран в [`09-optional.md`](09-optional.md): создание,
преобразования, различие `orElse()` и `orElseGet()` и случаи, когда его применять
не стоит.

## Checked exceptions внутри lambda

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

## Когда обычный цикл лучше

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

## Типичные ошибки

### Отсутствие терминальной операции

Промежуточные операции остаются ленивыми и ничего не выполняют.

### Повторное использование Stream

После терминальной операции тот же stream использовать нельзя.

### Изменение списка из Stream.toList

Результат `Stream.toList()` немодифицируемый.

### Бизнес-логика в peek

Выполнение `peek()` зависит от фактического прохождения элемента через pipeline.

### Побочные эффекты во внешней коллекции

Результат зависит от порядка, плохо тестируется и становится опасным при
параллельной обработке.

### Автоматический parallelStream

Параллелизм имеет накладные расходы, использует общую pool и может замедлить
операцию.

### toMap без merge-функции

Повторяющийся ключ приводит к `IllegalStateException`.

### distinct перед toMap как универсальное решение

Равенство целых объектов не совпадает с уникальностью выбранного ключа.

### limit и skip после загрузки всех строк

Это не уменьшает объём данных, прочитанных из базы.

### Дорогая операция перед filter

Лишние элементы обрабатываются до того, как будут отброшены.

### reduce для изменяемого контейнера

Списки и карты нужно накапливать через `collect()`.

### Игнорирование Optional

Безусловный `get()` приводит к `NoSuchElementException` для пустого результата.

### Непонимание orElse

Запасное значение вычисляется даже при непустом `Optional`.

### Checked exception напрямую в Function

`Function<T, R>` не объявляет `throws IOException`, поэтому lambda не
компилируется без обработки или оборачивания.

## Краткий ответ для собеседования

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

## Краткая памятка

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

## Вопросы на собеседовании

### 1. Что такое Stream API?

**Ответ:** средство декларативной обработки последовательностей элементов. Описывает
что нужно сделать с данными, а не как обходить коллекцию.

### 2. Чем Stream отличается от Collection?

**Ответ:** коллекция хранит элементы, stream их только пропускает через себя.
Stream не имеет собственного хранилища, не изменяет источник, вычисляется лениво и
может быть использован один раз.

### 3. Из каких частей состоит pipeline?

**Ответ:** из источника, произвольного числа промежуточных операций и одной
терминальной. Без терминальной операции ничего не выполняется.

### 4. Какими способами можно создать Stream?

**Ответ:** из коллекции через `stream()`, из массива через `Arrays.stream()`, из
значений через `Stream.of()`, генерацией через `Stream.iterate()` и
`Stream.generate()`, из строк файла через `Files.lines()`, а также через
`IntStream.range()`.

### 5. Что означает ленивость промежуточных операций?

**Ответ:** они не выполняются в момент вызова, а лишь строят цепочку. Работа
начинается только при вызове терминальной операции, и это позволяет не обрабатывать
лишние элементы.

### 6. Как выполняется pipeline по элементам?

**Ответ:** каждый элемент проходит всю цепочку до конца, и лишь затем берётся
следующий. Обхода коллекции заново на каждую операцию не происходит, поэтому
`findFirst()` после `filter()` остановится на первом подходящем элементе.

### 7. Как связаны filter() и Predicate?

**Ответ:** `filter()` принимает `Predicate<T>` — функцию из элемента в `boolean` —
и оставляет элементы, для которых она вернула истину.

### 8. Как связаны map() и Function?

**Ответ:** `map()` принимает `Function<T, R>` и заменяет каждый элемент результатом
её применения, меняя тип потока.

### 9. Чем map() отличается от flatMap()?

**Ответ:** `map()` возвращает один элемент на входной, `flatMap()` возвращает поток
и разворачивает вложенность. Нужен, когда из каждого элемента получается коллекция,
а на выходе требуется плоский поток.

### 10. От чего зависит результат distinct()?

**Ответ:** от `equals` и `hashCode` элементов. Для объектов без корректной
реализации контракта дубликаты останутся.

### 11. Как sorted() использует Comparator?

**Ответ:** без аргументов требует, чтобы элементы реализовывали `Comparable`, иначе
будет `ClassCastException` во время выполнения. С аргументом использует переданный
компаратор.

### 12. Почему limit() и skip() не заменяют пагинацию в базе?

**Ответ:** они применяются уже после загрузки данных в память. База отдаст все
строки, а отсечение произойдёт в приложении — лишний трафик и расход памяти.
Ограничивать нужно запросом.

### 13. Для чего предназначен peek()?

**Ответ:** для отладки — посмотреть элементы, проходящие через определённое место
цепочки, не изменяя поток.

### 14. Почему бизнес-логика в peek() опасна?

**Ответ:** операция промежуточная и ленивая, поэтому может не выполниться вовсе.
Кроме того, реализация вправе пропустить её, если результат не влияет на итог —
например, при подсчёте размера у потока с известным числом элементов.

### 15. Какие операции являются терминальными?

**Ответ:** `collect`, `toList`, `forEach`, `reduce`, `count`, `min`, `max`,
`findFirst`, `findAny`, `anyMatch`, `allMatch`, `noneMatch`. После терминальной
операции поток закрыт.

### 16. Можно ли изменять список из Stream.toList()?

**Ответ:** нет, метод возвращает неизменяемый список. Попытка изменения даст
`UnsupportedOperationException`.

### 17. Как собрать результат в изменяемый ArrayList?

**Ответ:** через `collect(Collectors.toList())` либо явно
`collect(Collectors.toCollection(ArrayList::new))`, если тип важен.

### 18. Чем reduce() отличается от collect()?

**Ответ:** `reduce()` предназначен для свёртки в одно неизменяемое значение и
требует ассоциативной операции. `collect()` наполняет изменяемый контейнер и
корректно работает при параллельном выполнении за счёт объединения промежуточных
результатов.

### 19. Почему изменяемый контейнер собирают через collect()?

**Ответ:** `collect()` знает, как создать контейнер, наполнить его и объединить
части. При свёртке через `reduce()` с изменяемым аккумулятором параллельное
выполнение приведёт к гонке.

### 20. Для чего нужны joining(), groupingBy() и partitioningBy()?

**Ответ:** `joining()` соединяет строки с разделителем, `groupingBy()` группирует
по ключу, `partitioningBy()` разделяет на две группы по предикату.

### 21. Чем groupingBy() отличается от partitioningBy()?

**Ответ:** первый строит произвольное число групп по значению ключа, второй всегда
даёт ровно две группы с ключами `true` и `false`, причём обе присутствуют в
результате даже пустыми.

### 22. Когда toMap() выбрасывает ошибку Duplicate key?

**Ответ:** когда два элемента дали одинаковый ключ, а функция разрешения конфликта
не задана. Возникает `IllegalStateException`.

### 23. Как работает merge-функция toMap()?

**Ответ:** это третий аргумент, `BinaryOperator`, получающий существующее и новое
значения и возвращающий то, которое останется в карте.

### 24. Почему distinct() не гарантирует уникальность ключей toMap()?

**Ответ:** `distinct()` убирает одинаковые элементы, а конфликт возникает при
одинаковых ключах. Два разных объекта могут дать один ключ, и дубликат останется.

### 25. Какие формы method reference существуют?

**Ответ:** ссылка на статический метод, на метод конкретного объекта, на метод
произвольного объекта типа и на конструктор.

### 26. Почему Stream является одноразовым?

**Ответ:** он не хранит элементы, а связан с источником и состоянием обхода. После
терминальной операции поток помечается использованным, и повторное обращение даёт
`IllegalStateException`.

### 27. Чем stateless-операции отличаются от stateful?

**Ответ:** stateless обрабатывают элемент независимо от остальных — `filter`,
`map`. Stateful требуют информации о других элементах или всей
последовательности — `sorted`, `distinct`, `limit`. Они дороже и хуже
распараллеливаются.

### 28. Как порядок операций влияет на эффективность и результат?

**Ответ:** фильтрацию ставят раньше преобразования и сортировки, чтобы уменьшить
объём работы. Порядок может менять и результат: `sorted().limit(3)` берёт три
наименьших элемента, `limit(3).sorted()` — сортирует первые три.

### 29. Чем опасны побочные эффекты?

**Ответ:** они делают результат зависящим от порядка и способа выполнения, а при
параллельном выполнении приводят к гонке. Накопление во внешнюю коллекцию через
`forEach` следует заменять на `collect`.

### 30. Почему нельзя без измерений применять parallelStream()?

**Ответ:** распараллеливание добавляет накладные расходы на разбиение, передачу
задач и объединение. На малых объёмах и при дешёвой операции оно медленнее
последовательного варианта.

### 31. Какую pool обычно использует parallel stream?

**Ответ:** общий `ForkJoinPool.commonPool()`, размер которого по умолчанию на
единицу меньше числа доступных процессоров. Он один на приложение, поэтому долгая
блокирующая операция в параллельном потоке задерживает и остальные задачи.

### 32. Для чего нужны IntStream, LongStream и DoubleStream?

**Ответ:** для работы с примитивами без упаковки. Дают специализированные операции
вроде `sum()`, `average()` и `summaryStatistics()`.

### 33. Что такое boxing и unboxing?

**Ответ:** упаковка примитива в обёртку и обратное преобразование. В потоках это
основная скрытая цена: `Stream<Integer>` создаёт объект на каждое значение, тогда
как `IntStream` работает с примитивами напрямую.

### 34. Почему findFirst() возвращает Optional?

**Ответ:** поток может оказаться пустым, и результата не будет. `Optional` делает
эту возможность видимой в сигнатуре вместо возврата `null`.

### 35. Чем orElse() отличается от orElseGet()?

**Ответ:** аргумент `orElse()` вычисляется всегда, даже когда значение есть.
`orElseGet()` принимает `Supplier` и вызывает его только при отсутствии значения,
поэтому подходит для дорогих вычислений.

### 36. Почему Function<T, R> не принимает IOException напрямую?

**Ответ:** метод `apply()` не объявляет проверяемых исключений, а lambda не может
выбросить больше, чем объявлено интерфейсом.

### 37. Для чего используется UncheckedIOException?

**Ответ:** чтобы обернуть `IOException` в непроверяемое исключение и передать его
через операции потока, сохранив исходную причину.

### 38. Когда обычный цикл понятнее Stream API?

**Ответ:** при сложном условии выхода, при работе с индексами, при изменении
нескольких переменных сразу и при необходимости прервать обработку по нетривиальному
критерию. Stream выигрывает на преобразованиях и агрегации, цикл — на императивной
логике.

---

## См. также

- [`08-functional-interfaces-lambda.md`](08-functional-interfaces-lambda.md) —
  функциональные интерфейсы, лежащие в основе операций Stream, и почему `reduce`
  требует `BinaryOperator`
- [`01-collections-framework.md`](01-collections-framework.md) — источники stream
- [`09-optional.md`](09-optional.md) — `Optional`, который возвращают
  `findFirst()`, `findAny()` и `reduce()` без начального значения
- [`../concurrency/03-locks-atomics-executors.md`](../concurrency/03-locks-atomics-executors.md) —
  `ForkJoinPool.commonPool()`, который использует parallel stream