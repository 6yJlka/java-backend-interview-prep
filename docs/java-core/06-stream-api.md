# Stream API в Java

Декларативный способ обработки последовательности элементов: код описывает, какие
преобразования нужны, а библиотека управляет обходом.

```java
List<String> activeEmails = users.stream()
        .filter(User::isActive)
        .map(User::getEmail)
        .toList();
```

Stream не является структурой данных — это вычислительный конвейер.

| Collection | Stream |
|---|---|
| хранит данные | описывает обработку данных |
| обходится многократно | используется один раз |
| предоставляет добавление и удаление | не изменяет источник |
| вычислена заранее | промежуточные операции ленивы |

```text
Collection → где лежат элементы
Stream     → что сделать с элементами
```

---

## Устройство конвейера

```text
источник
    ↓
промежуточные операции
    ↓
терминальная операция
```

```java
long urgentCount = orders.stream()                  // источник
        .filter(order ->                            // промежуточная
                order.getPriority() == URGENT)
        .count();                                   // терминальная
```

Промежуточная операция возвращает новый `Stream` и выполняется лениво.
Терминальная запускает конвейер и завершает использование stream.

### Создание

```java
Stream<User> users = userList.stream();

Stream<Order> orders = Arrays.stream(orderArray);

Stream<String> priorities = Stream.of("LOW", "HIGH", "URGENT");

Stream<User> empty = Stream.empty();
```

Для массива примитивов создаётся специализированный stream:

```java
IntStream numbers = Arrays.stream(new int[]{1, 2, 3});
```

`Stream.iterate()` создаёт последовательность по правилу:

```java
List<Integer> numbers = Stream.iterate(1, value -> value + 1)
        .limit(5)
        .toList();                                  // [1, 2, 3, 4, 5]
```

Без ограничивающей операции такой stream бесконечен. В Java 9 появился вариант с
условием продолжения:

```java
Stream.iterate(1, value -> value <= 5, value -> value + 1)
        .toList();
```

### Ленивость

Вызов промежуточной операции только строит следующий этап.

```java
Stream<User> activeUsers = users.stream()
        .filter(user -> {
            System.out.println(user.getId());
            return user.isActive();
        });
```

Пока нет терминальной операции, фильтр не выполняется и строки не печатаются.
Конвейер запустится только здесь:

```java
List<User> result = activeUsers.toList();
```

### Поэлементное выполнение

Операции выполняются не отдельными полными проходами, а поэлементно.

```java
users.stream()
        .filter(User::isActive)
        .map(User::getEmail)
        .limit(2)
        .toList();
```

```text
user 1 → filter → map → limit
user 2 → filter → отброшен
user 3 → filter → map → limit → достаточно элементов
```

`limit()` может остановить обработку источника раньше, а `findFirst()` после
`filter()` завершится на первом подходящем элементе.

---

## Промежуточные операции

### filter

Оставляет элементы, для которых `Predicate<T>` вернул `true`.

```java
List<User> activeUsers = users.stream()
        .filter(User::isActive)
        .toList();
```

### map

Преобразует каждый элемент в другой через `Function<T, R>`, меняя тип потока.

```java
List<String> emails = users.stream()
        .map(User::getEmail)
        .toList();
```

### flatMap

Преобразует каждый элемент в stream и объединяет вложенные stream в один плоский.

```java
List<List<String>> groups = List.of(
        List.of("network", "database"),
        List.of("security")
);

List<String> values = groups.stream()
        .flatMap(List::stream)
        .toList();
```

```text
группа 1 → [network, database]
группа 2 → [security]

flatMap → [network, database, security]
```

Разница видна по типу результата:

```java
Stream<Stream<String>> nested = groups.stream().map(List::stream);
Stream<String> flat = groups.stream().flatMap(List::stream);
```

```text
map     → один вход превращается в одно значение
flatMap → один вход превращается в несколько, затем уровни объединяются
```

### distinct и sorted

`distinct()` удаляет дубликаты по `equals()` и `hashCode()`. Если контракт нарушен
или равенство сущности выбрано неверно, результат тоже будет неверным.

```java
List<String> emails = users.stream()
        .map(User::getEmail)
        .sorted()
        .toList();
```

Без аргумента `sorted()` требует, чтобы элементы реализовывали `Comparable`, иначе
во время выполнения будет `ClassCastException`. Пользовательский порядок задаётся
компаратором:

```java
List<Order> sorted = orders.stream()
        .sorted(Comparator.comparing(Order::getCreatedAt).reversed())
        .toList();
```

### limit и skip

```java
List<Order> page = orders.stream()
        .skip(20)
        .limit(10)
        .toList();
```

Важная оговорка: это **не пагинация в базе данных**. Если данные уже загружены в
коллекцию, база передала приложению все строки.

```text
плохой вариант
БД → 1 000 000 строк → Java → skip → limit 20

правильная пагинация
БД → LIMIT и OFFSET или keyset pagination → Java получает 20 строк
```

Пагинацию выполняют запросом репозитория.

### peek

Позволяет наблюдать элементы при прохождении конвейера и предназначен прежде всего
для отладки.

```java
List<String> emails = users.stream()
        .filter(User::isActive)
        .peek(user -> log.debug("Active user {}", user.getId()))
        .map(User::getEmail)
        .toList();
```

Бизнес-логику в `peek()` помещать нельзя. Операция ленивая и может не выполниться
вовсе, а реализация вправе пропустить её, если результат не влияет на итог —
например, при подсчёте размера у потока с известным числом элементов.

---

## Терминальные операции

### toList и collect

```java
List<String> emails = users.stream()
        .map(User::getEmail)
        .toList();
```

`Stream.toList()` возвращает немодифицируемый список: попытка изменения даст
`UnsupportedOperationException`. В отличие от некоторых сборщиков, он допускает
`null` среди элементов.

`collect()` выполняет изменяемое свёртывание:

```java
ArrayList<User> activeUsers = users.stream()
        .filter(User::isActive)
        .collect(Collectors.toCollection(ArrayList::new));
```

Для `Collectors.toList()` не гарантируются ни конкретная реализация списка, ни его
изменяемость. Если нужен гарантированно изменяемый `ArrayList`, используют
`Collectors.toCollection(ArrayList::new)`.

### forEach, count, find и match

```java
users.stream()
        .map(User::getEmail)
        .forEach(System.out::println);
```

У параллельного stream `forEach()` не гарантирует порядок; для его сохранения
существует `forEachOrdered()`.

```java
long urgentCount = orders.stream()
        .filter(order -> order.getPriority() == URGENT)
        .count();
```

```java
Order order = orders.stream()
        .filter(value -> value.getId() == orderId)
        .findFirst()
        .orElseThrow(() -> new OrderNotFoundException(orderId));
```

`findFirst()` учитывает порядок обхода, `findAny()` может вернуть любой подходящий
элемент и даёт больше свободы при параллельной обработке.

```java
boolean hasUrgent = orders.stream()
        .anyMatch(order -> order.getPriority() == URGENT);

boolean allActive = users.stream().allMatch(User::isActive);
boolean noActive = users.stream().noneMatch(User::isActive);
```

Эти операции используют короткое замыкание и могут не обходить весь источник. Для
пустого stream `allMatch()` и `noneMatch()` возвращают `true`, а `anyMatch()` —
`false`.

```java
Optional<Order> newest = orders.stream()
        .max(Comparator.comparing(Order::getCreatedAt));
```

Результат `Optional`, потому что stream может быть пустым.

### reduce

Объединяет элементы в одно неизменяемое значение.

```java
int totalTitleLength = orders.stream()
        .map(Order::getTitle)
        .map(String::length)
        .reduce(0, Integer::sum);
```

Без начального значения результат оборачивается в `Optional`:

```java
Optional<Integer> maximumTitleLength = orders.stream()
        .map(Order::getTitle)
        .map(String::length)
        .reduce(Integer::max);
```

### reduce против collect

```text
reduce  → комбинирование значений без изменения общего контейнера: 1 + 2 + 3 → 6
collect → накопление в изменяемый контейнер: ArrayList, HashMap, StringBuilder
```

Изменяемые контейнеры собирают через `collect()`, потому что сборщик отдельно
описывает создание, накопление и объединение частей результата — это позволяет
корректно работать и с параллельным stream.

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

Так делать нельзя: нарушается идея неизменяемого накопления и появляется опасное
общее изменяемое состояние.

---

## Collectors

### joining

```java
String emails = users.stream()
        .map(User::getEmail)
        .collect(Collectors.joining(", "));
```

Можно указать разделитель, префикс и суффикс:

```java
String emails = users.stream()
        .map(User::getEmail)
        .collect(Collectors.joining(", ", "[", "]"));
```

### groupingBy и partitioningBy

```java
Map<OrderPriority, List<Order>> byPriority = orders.stream()
        .collect(Collectors.groupingBy(Order::getPriority));
```

Можно передать вложенный сборщик:

```java
Map<OrderPriority, Long> countByPriority = orders.stream()
        .collect(Collectors.groupingBy(
                Order::getPriority,
                Collectors.counting()
        ));
```

`partitioningBy()` делит элементы по булеву условию:

```java
Map<Boolean, List<User>> usersByActivity = users.stream()
        .collect(Collectors.partitioningBy(User::isActive));
```

| Операция | Ключ | Количество групп |
|---|---|---|
| `groupingBy` | произвольный | произвольное |
| `partitioningBy` | `Boolean` | ровно две, `true` и `false` |

Обе группы присутствуют в результате даже пустыми. Название `partitioningBy`
означает разделение по условию и к пагинации отношения не имеет.

### toMap

```java
Map<Long, User> usersById = users.stream()
        .collect(Collectors.toMap(
                User::getId,
                Function.identity()
        ));
```

Если два элемента дают одинаковый ключ, перегрузка без функции слияния выбросит
`IllegalStateException` с сообщением `Duplicate key`.

Для ожидаемых повторов решение принимают явно:

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

Чтобы сохранить последнее, возвращают `replacement`. Выбор правила должен отражать
бизнес-смысл, а не случайно скрывать плохие данные.

Отдельно стоит понимать, почему `distinct()` эту проблему не решает. Он сравнивает
целые элементы через `equals()` и `hashCode()`, а `toMap()` определяет конфликт по
результату функции ключа. Два разных пользователя с разными идентификаторами не
равны между собой, но могут вернуть одинаковую почту: `distinct()` их пропустит, и
`toMap()` всё равно обнаружит повторяющийся ключ.

---

## Особенности выполнения

### Одноразовость

После терминальной операции stream закрыт.

```java
Stream<User> stream = users.stream();

long count = stream.count();
List<User> result = stream.toList();   // IllegalStateException
```

Он не хранит элементы, а связан с источником и состоянием обхода. Для повторной
обработки создают новый stream.

### Stateless и stateful

```text
stateless → filter, map, peek
stateful  → distinct, sorted, limit и skip для упорядоченного parallel stream
```

`sorted()` должен накопить элементы до выдачи результата, `distinct()` — помнить
уже встреченные значения. Такие операции дороже и хуже распараллеливаются.

### Порядок операций

Сначала полезно уменьшить число элементов дешёвой операцией, затем выполнять
дорогую обработку.

```java
List<OrderView> views = orders.stream()
        .filter(order -> order.getStatus() == OrderStatus.OPEN)
        .map(expensiveMapper::toView)
        .limit(20)
        .toList();
```

Если `map()` поставить до `filter()`, дорогое преобразование выполнится и для
элементов, которые затем будут отброшены.

Менять порядок механически нельзя: операции могут зависеть от преобразованного
значения, а `sorted()`, `distinct()` и `limit()` меняют смысл в зависимости от
расположения. `sorted().limit(3)` берёт три наименьших элемента,
`limit(3).sorted()` — сортирует первые три.

### Побочные эффекты

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

Изменение внешней коллекции создаёт гонки при параллельном выполнении, потерю или
повреждение данных, зависимость результата от порядка, непредсказуемое поведение
после изменения конвейера и сложность тестирования. Даже синхронизированный
контейнер не делает алгоритм логически корректным.

---

## Parallel Stream

```java
long urgentCount = orders.parallelStream()
        .filter(order -> order.getPriority() == URGENT)
        .count();
```

Параллельный stream не всегда быстрее. На результат влияют размер источника,
стоимость операции над элементом, возможность эффективно разделить источник,
необходимость сохранять порядок, стоимость объединения результатов и текущая
нагрузка на процессоры.

По умолчанию используется общий `ForkJoinPool.commonPool()`, один на приложение.
Долгая блокирующая операция займёт его потоки и повлияет на другой код процесса.

Общее изменяемое состояние даёт гонку:

```java
List<User> result = new ArrayList<>();

users.parallelStream().forEach(result::add);
```

Так делать нельзя. `parallelStream()` применяют после измерений на реалистичных
данных и проверки корректности. Для запросов к базе или внешним сервисам нужен
явно управляемый механизм конкурентности.

---

## Примитивные stream

```text
IntStream
LongStream
DoubleStream
```

```java
int total = IntStream.of(10, 20, 30).sum();

double average = orders.stream()
        .mapToInt(order -> order.getTitle().length())
        .average()
        .orElse(0.0);
```

Они дают операции `sum()`, `average()` и `summaryStatistics()` без создания
объекта-обёртки на каждое значение.

`Stream<Integer>` хранит ссылки на обёртки, `IntStream` работает с примитивами:

```java
IntStream ids = users.stream()
        .mapToInt(user -> Math.toIntExact(user.getId()));

Stream<Integer> boxed = ids.boxed();
```

На больших объёмах лишняя упаковка создаёт дополнительные объекты и нагрузку на
сборщик мусора.

---

## Optional в Stream API

Операции, которые могут не найти значение, возвращают `Optional`.

```java
Optional<Order> order = orders.stream()
        .filter(value -> value.getId() == orderId)
        .findFirst();
```

```java
Order found = order.orElseThrow(() -> new OrderNotFoundException(orderId));
```

Вызывать `get()` без проверки не следует.

Извлекая значение, важно помнить о различии `orElse()` и `orElseGet()`: аргумент
первого вычисляется всегда, даже когда значение присутствует. Для константы это
безразлично, для запроса к базе или другого дорогого вызова — нет.

```java
String name = order.map(Order::getTitle).orElse("не найден");
```

---

## Checked exceptions внутри lambda

Стандартные функциональные интерфейсы не объявляют проверяемых исключений:

```java
public interface Function<T, R> {
    R apply(T value);
}
```

Поэтому такой код не компилируется:

```java
paths.stream()
        .map(Files::readString)
        .toList();
```

Исключение обрабатывают внутри лямбды или выносят адаптацию в отдельный метод:

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

`UncheckedIOException` сохраняет исходное исключение как причину. Если обработка
нужна для каждого элемента отдельно, обычный цикл читается лучше.

---

## Когда обычный цикл лучше

```text
алгоритм содержит сложные ветвления
нужны break или continue
требуется изменять несколько связанных состояний
checked exceptions делают lambda громоздкой
важен точный пошаговый контроль
Stream-версия хуже объясняет намерение
```

```java
for (Order order : orders) {
    if (order.getStatus() != OrderStatus.OPEN) {
        continue;
    }

    try {
        exporter.export(order);
    } catch (IOException exception) {
        handleExportFailure(order, exception);
    }
}
```

Stream API — инструмент, а не обязательная замена циклов.

---

## Типичные ошибки

### Отсутствие терминальной операции

Промежуточные операции остаются ленивыми и ничего не выполняют.

### Повторное использование Stream

После терминальной операции тот же stream использовать нельзя.

### Изменение списка из Stream.toList

Результат немодифицируемый.

### Бизнес-логика в peek

Выполнение зависит от фактического прохождения элемента через конвейер и может не
произойти вовсе.

### Побочные эффекты во внешней коллекции

Результат зависит от порядка, плохо тестируется и становится опасным при
параллельной обработке.

### Автоматический parallelStream

Параллелизм имеет накладные расходы, использует общий пул и может замедлить
операцию.

### toMap без функции слияния

Повторяющийся ключ приводит к `IllegalStateException`.

### distinct перед toMap как универсальное решение

Равенство целых объектов не совпадает с уникальностью выбранного ключа.

### limit и skip после загрузки всех строк

Это не уменьшает объём данных, прочитанных из базы.

### Дорогая операция перед filter

Лишние элементы обрабатываются до того, как будут отброшены.

### reduce для изменяемого контейнера

Списки и карты накапливают через `collect()`.

### Игнорирование Optional

Безусловный `get()` даёт `NoSuchElementException` для пустого результата.

### Непонимание orElse

Запасное значение вычисляется даже при непустом `Optional`.

### Checked exception напрямую в Function

Интерфейс не объявляет `throws IOException`, поэтому лямбда не компилируется без
обработки или оборачивания.

---

## Краткая памятка

```text
источник → ленивые промежуточные → терминальная → stream использован

Collection → хранит данные
Stream     → описывает обработку, одноразовый, источник не меняет
элементы проходят конвейер поэлементно, а не полными проходами
```

```text
filter  → отбор, Predicate
map     → преобразование, Function
flatMap → раскрытие вложенности
distinct → по equals и hashCode
sorted  → без компаратора требует Comparable, иначе ClassCastException
limit / skip → не пагинация в базе
peek    → только отладка
```

```text
toList  → немодифицируемый список
изменяемый ArrayList → collect(toCollection(ArrayList::new))

reduce  → одно неизменяемое значение
collect → изменяемый контейнер, корректен при parallel

findFirst → учитывает порядок, findAny → любой
пустой stream: allMatch и noneMatch → true, anyMatch → false
```

```text
groupingBy     → произвольное количество групп
partitioningBy → ровно две, true и false
toMap + повторяющиеся ключи → нужна функция слияния
distinct её не заменяет: конфликт по ключу, а не по элементу
```

```text
stateless → filter, map, peek
stateful  → distinct, sorted, limit

фильтрацию раньше дорогого map
sorted().limit(3) ≠ limit(3).sorted()
```

```text
parallelStream
→ не применять автоматически
→ общий ForkJoinPool.commonPool()
→ избегать общего изменяемого состояния
→ измерять

IntStream / LongStream / DoubleStream → без упаковки
sum, average, summaryStatistics
```

```text
Function<T, R> не объявляет checked exception
→ обработать внутри или обернуть в UncheckedIOException
orElse вычисляется всегда, orElseGet — только при отсутствии
```

---

## Краткий ответ для собеседования

Stream API описывает одноразовый конвейер обработки данных. Коллекция хранит
элементы, а stream задаёт вычисление над источником и сам его не меняет. Конвейер
состоит из источника, ленивых промежуточных операций и одной терминальной, которая
запускает вычисление и закрывает stream.

Ленивость не просто откладывает работу: элементы идут через цепочку поэлементно,
поэтому `findFirst()` после `filter()` останавливается на первом подходящем, а
`limit()` прекращает чтение источника раньше.

Из операций основные три: `filter()` отбирает, `map()` превращает один элемент в
один результат, `flatMap()` раскрывает вложенные структуры. Для накопления в
изменяемый контейнер служит `collect()`, для свёртки в одно значение — `reduce()`.
Собирать список через `reduce()` с изменяемым аккумулятором нельзя: при
параллельном выполнении это даёт гонку, тогда как сборщик отдельно описывает
создание, накопление и объединение частей.

Отдельно стоит помнить про `toMap()`: при совпадении ключей без функции слияния
будет `IllegalStateException`, и `distinct()` эту проблему не решает, потому что
сравнивает элементы целиком, а конфликт возникает по ключу.

Побочные эффекты делают конвейер непредсказуемым и опасным при параллельном
выполнении, поэтому накопление во внешнюю коллекцию заменяют на `collect()`.
`parallelStream()` применяют только после измерений: он добавляет накладные
расходы и работает в общем `ForkJoinPool`, одном на приложение.

Наконец, стандартный `Function<T, R>` не объявляет проверяемых исключений, поэтому
`IOException` внутри лямбды нужно обработать или обернуть в непроверяемое.

---

## Вопросы на собеседовании

### 1. Что такое Stream API?

**Ответ:** средство декларативной обработки последовательностей элементов.
Описывает, что нужно сделать с данными, а не как обходить коллекцию.

### 2. Чем Stream отличается от Collection?

**Ответ:** коллекция хранит элементы, stream их только пропускает через себя. Он
не имеет собственного хранилища, не изменяет источник, вычисляется лениво и может
быть использован один раз.

### 3. Из каких частей состоит конвейер?

**Ответ:** из источника, произвольного числа промежуточных операций и одной
терминальной. Без терминальной операции ничего не выполняется.

### 4. Какими способами можно создать Stream?

**Ответ:** из коллекции через `stream()`, из массива через `Arrays.stream()`, из
значений через `Stream.of()`, генерацией через `Stream.iterate()` и
`Stream.generate()`, из строк файла через `Files.lines()`, а также через
`IntStream.range()`.

### 5. Что означает ленивость промежуточных операций?

**Ответ:** они не выполняются в момент вызова, а лишь строят цепочку. Работа
начинается при вызове терминальной операции, и это позволяет не обрабатывать
лишние элементы.

### 6. Как выполняется конвейер по элементам?

**Ответ:** каждый элемент проходит всю цепочку до конца, и лишь затем берётся
следующий. Обхода коллекции заново на каждую операцию не происходит.

### 7. Как связаны filter() и Predicate?

**Ответ:** `filter()` принимает `Predicate<T>` — функцию из элемента в `boolean` —
и оставляет элементы, для которых она вернула истину.

### 8. Как связаны map() и Function?

**Ответ:** `map()` принимает `Function<T, R>` и заменяет каждый элемент
результатом её применения, меняя тип потока.

### 9. Чем map() отличается от flatMap()?

**Ответ:** `map()` возвращает один элемент на входной, `flatMap()` возвращает
поток и разворачивает вложенность. Нужен, когда из каждого элемента получается
коллекция, а на выходе требуется плоский поток.

### 10. От чего зависит результат distinct()?

**Ответ:** от `equals` и `hashCode` элементов. Для объектов без корректной
реализации контракта дубликаты останутся.

### 11. Как sorted() использует Comparator?

**Ответ:** без аргументов требует, чтобы элементы реализовывали `Comparable`,
иначе будет `ClassCastException` во время выполнения. С аргументом использует
переданный компаратор.

### 12. Почему limit() и skip() не заменяют пагинацию в базе?

**Ответ:** они применяются уже после загрузки данных в память. База отдаст все
строки, а отсечение произойдёт в приложении — лишний трафик и расход памяти.
Ограничивать нужно запросом.

### 13. Для чего предназначен peek()?

**Ответ:** для отладки — посмотреть элементы, проходящие через определённое место
цепочки, не изменяя поток.

### 14. Почему бизнес-логика в peek() опасна?

**Ответ:** операция промежуточная и ленивая, поэтому может не выполниться вовсе.
Кроме того, реализация вправе пропустить её, если результат не влияет на итог.

### 15. Какие операции являются терминальными?

**Ответ:** `collect`, `toList`, `forEach`, `reduce`, `count`, `min`, `max`,
`findFirst`, `findAny`, `anyMatch`, `allMatch`, `noneMatch`. После терминальной
операции поток закрыт.

### 16. Можно ли изменять список из Stream.toList()?

**Ответ:** нет, метод возвращает неизменяемый список. Попытка изменения даст
`UnsupportedOperationException`.

### 17. Как собрать результат в изменяемый ArrayList?

**Ответ:** через `collect(Collectors.toCollection(ArrayList::new))`.
`Collectors.toList()` на практике возвращает `ArrayList`, но контракт не
гарантирует ни реализацию, ни изменяемость, поэтому опираться на него не стоит.

### 18. Чем reduce() отличается от collect()?

**Ответ:** `reduce()` предназначен для свёртки в одно неизменяемое значение и
требует ассоциативной операции. `collect()` наполняет изменяемый контейнер и
корректно работает при параллельном выполнении за счёт объединения промежуточных
результатов.

### 19. Почему изменяемый контейнер собирают через collect()?

**Ответ:** `collect()` знает, как создать контейнер, наполнить его и объединить
части. При свёртке через `reduce()` с изменяемым аккумулятором параллельное
выполнение приведёт к гонке.

### 20. Чем findFirst() отличается от findAny()?

**Ответ:** первый учитывает порядок обхода и возвращает именно первый подходящий
элемент, второй вправе вернуть любой, что даёт больше свободы при параллельной
обработке.

### 21. Что вернут allMatch() и anyMatch() для пустого stream?

**Ответ:** `allMatch()` и `noneMatch()` вернут `true`, `anyMatch()` — `false`.

### 22. Для чего нужны joining(), groupingBy() и partitioningBy()?

**Ответ:** `joining()` соединяет строки с разделителем, `groupingBy()` группирует
по ключу, `partitioningBy()` разделяет на две группы по предикату.

### 23. Чем groupingBy() отличается от partitioningBy()?

**Ответ:** первый строит произвольное число групп по значению ключа, второй всегда
даёт ровно две группы с ключами `true` и `false`, причём обе присутствуют в
результате даже пустыми.

### 24. Когда toMap() выбрасывает ошибку Duplicate key?

**Ответ:** когда два элемента дали одинаковый ключ, а функция разрешения конфликта
не задана. Возникает `IllegalStateException`.

### 25. Как работает функция слияния в toMap()?

**Ответ:** это третий аргумент, `BinaryOperator`, получающий существующее и новое
значения и возвращающий то, которое останется в карте.

### 26. Почему distinct() не гарантирует уникальность ключей toMap()?

**Ответ:** `distinct()` убирает одинаковые элементы, а конфликт возникает при
одинаковых ключах. Два разных объекта могут дать один ключ, и дубликат останется.

### 27. Почему Stream является одноразовым?

**Ответ:** он не хранит элементы, а связан с источником и состоянием обхода. После
терминальной операции поток помечается использованным, и повторное обращение даёт
`IllegalStateException`.

### 28. Чем stateless-операции отличаются от stateful?

**Ответ:** stateless обрабатывают элемент независимо от остальных — `filter`,
`map`. Stateful требуют информации о других элементах или всей последовательности
— `sorted`, `distinct`, `limit`. Они дороже и хуже распараллеливаются.

### 29. Как порядок операций влияет на эффективность и результат?

**Ответ:** фильтрацию ставят раньше преобразования и сортировки, чтобы уменьшить
объём работы. Порядок может менять и результат: `sorted().limit(3)` берёт три
наименьших элемента, `limit(3).sorted()` — сортирует первые три.

### 30. Чем опасны побочные эффекты?

**Ответ:** они делают результат зависящим от порядка и способа выполнения, а при
параллельном выполнении приводят к гонке. Накопление во внешнюю коллекцию через
`forEach` следует заменять на `collect`.

### 31. Почему нельзя без измерений применять parallelStream()?

**Ответ:** распараллеливание добавляет накладные расходы на разбиение, передачу
задач и объединение. На малых объёмах и при дешёвой операции оно медленнее
последовательного варианта.

### 32. Какой пул обычно использует parallel stream?

**Ответ:** общий `ForkJoinPool.commonPool()`, размер которого по умолчанию на
единицу меньше числа доступных процессоров. Он один на приложение, поэтому долгая
блокирующая операция задерживает и остальные задачи.

### 33. Для чего нужны IntStream, LongStream и DoubleStream?

**Ответ:** для работы с примитивами без упаковки. Дают специализированные операции
вроде `sum()`, `average()` и `summaryStatistics()`.

### 34. Что такое boxing и unboxing в контексте stream?

**Ответ:** упаковка примитива в обёртку и обратное преобразование.
`Stream<Integer>` создаёт объект на каждое значение, тогда как `IntStream`
работает с примитивами напрямую.

### 35. Почему findFirst() возвращает Optional?

**Ответ:** поток может оказаться пустым, и результата не будет. `Optional` делает
эту возможность видимой в сигнатуре вместо возврата `null`.

### 36. Чем orElse() отличается от orElseGet()?

**Ответ:** аргумент `orElse()` вычисляется всегда, даже когда значение есть.
`orElseGet()` принимает `Supplier` и вызывает его только при отсутствии значения,
поэтому подходит для дорогих вычислений.

### 37. Почему Function<T, R> не принимает IOException напрямую?

**Ответ:** метод `apply()` не объявляет проверяемых исключений, а лямбда не может
выбросить больше, чем объявлено интерфейсом.

### 38. Для чего используется UncheckedIOException?

**Ответ:** чтобы обернуть `IOException` в непроверяемое исключение и передать его
через операции потока, сохранив исходную причину.

### 39. Когда обычный цикл понятнее Stream API?

**Ответ:** при сложном условии выхода, при работе с индексами, при изменении
нескольких переменных сразу и при необходимости прервать обработку по
нетривиальному критерию. Stream выигрывает на преобразованиях и агрегации, цикл —
на императивной логике.

---

## См. также

- [`08-functional-interfaces-lambda.md`](08-functional-interfaces-lambda.md) —
  функциональные интерфейсы в основе операций Stream, формы method reference и
  почему `reduce` требует `BinaryOperator`
- [`01-collections-framework.md`](01-collections-framework.md) — источники stream
- [`09-optional.md`](09-optional.md) — `Optional`, который возвращают
  `findFirst()`, `findAny()` и `reduce()` без начального значения
- [`05-exceptions.md`](05-exceptions.md) — проверяемые исключения и оборачивание в
  непроверяемые
- [`../concurrency/03-locks-atomics-executors.md`](../concurrency/03-locks-atomics-executors.md) —
  `ForkJoinPool.commonPool()`, который использует parallel stream