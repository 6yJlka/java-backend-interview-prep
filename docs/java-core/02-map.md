# Map в Java

`Map<K, V>` — интерфейс для хранения пар вида:

```text
ключ → значение
```

Где:

- `K` — тип ключа
- `V` — тип значения

Пример:

```java
Map<Long, String> users = new HashMap<>();

users.put(1L, "Alice");
users.put(2L, "Bob");
```

В карте находятся две записи:

```text
1 → Alice
2 → Bob
```

Ключи в `Map` уникальны. Значения могут повторяться.

---

# Map и Collection

`Map` не наследует интерфейс `Collection`.

Упрощённая иерархия:

```text
Iterable
└── Collection
    ├── List
    ├── Set
    └── Queue

Map
```

`Collection` представляет набор отдельных элементов:

```java
Collection<User>
```

`Map` хранит пары ключ–значение:

```java
Map<Long, User>
```

Поэтому для карты требуется отдельный набор операций:

```java
put(key, value);
get(key);
remove(key);
containsKey(key);
```

---

# Основные свойства Map

## Уникальность ключей

В одной карте не может быть двух записей с одинаковым ключом.

```java
Map<String, Integer> ages = new HashMap<>();

ages.put("Dmitry", 22);
ages.put("Dmitry", 23);
```

После второго вызова `put()` старая запись будет заменена:

```text
Dmitry → 23
```

Размер карты:

```java
ages.size(); // 1
```

## Значения могут повторяться

```java
Map<Long, String> cities = new HashMap<>();

cities.put(1L, "Moscow");
cities.put(2L, "Moscow");
```

Обе записи допустимы:

```text
1 → Moscow
2 → Moscow
```

---

# Основные методы Map

## put

```java
V put(K key, V value);
```

Добавляет новую пару или заменяет значение существующего ключа.

```java
Map<String, Integer> scores = new HashMap<>();

scores.put("Alice", 10);
scores.put("Bob", 7);
```

Метод возвращает предыдущее значение.

```java
Integer previous = scores.put("Alice", 15);
```

Результат:

```text
previous = 10
Alice → 15
```

Если ключа раньше не было, обычно возвращается `null`.

```java
Integer previous = scores.put("Charlie", 5);
```

```text
previous = null
```

---

## get

```java
V get(Object key);
```

Возвращает значение по ключу.

```java
Integer score = scores.get("Alice");
```

Если ключ отсутствует, возвращается `null`.

```java
scores.get("Unknown"); // null
```

Возникает неоднозначность:

```java
Map<String, String> map = new HashMap<>();

map.put("existing", null);

map.get("existing"); // null
map.get("missing");  // null
```

По результату `get()` нельзя понять:

- ключ отсутствует
- ключ существует, но связан с `null`

Для точной проверки используется:

```java
map.containsKey("existing");
```

---

## getOrDefault

```java
V getOrDefault(Object key, V defaultValue);
```

Возвращает значение по ключу или переданное значение по умолчанию.

```java
int count = map.getOrDefault("java", 0);
```

Часто применяется при подсчёте частот:

```java
Map<Character, Integer> frequencies = new HashMap<>();

for (char character : text.toCharArray()) {
    frequencies.put(
            character,
            frequencies.getOrDefault(character, 0) + 1
    );
}
```

Для строки:

```text
banana
```

Получится:

```text
b → 1
a → 3
n → 2
```

Если ключ существует и связан с `null`, `getOrDefault()` вернёт `null`, а не значение по умолчанию.

---

## putIfAbsent

```java
V putIfAbsent(K key, V value);
```

Добавляет значение, только если по ключу ещё нет значения.

```java
Map<String, Integer> map = new HashMap<>();

map.put("java", 5);
map.putIfAbsent("java", 10);
```

Результат:

```text
java → 5
```

Старое значение не заменяется.

---

## containsKey

```java
boolean containsKey(Object key);
```

Проверяет наличие ключа.

```java
if (map.containsKey("java")) {
    System.out.println("Ключ найден");
}
```

Для `HashMap` средняя сложность составляет `O(1)`.

---

## containsValue

```java
boolean containsValue(Object value);
```

Проверяет наличие значения.

```java
map.containsValue(10);
```

В `HashMap` операция работает за `O(n)`, потому что по значению нельзя вычислить конкретный бакет. Необходимо проверить записи карты.

```text
containsKey   → O(1) в среднем
containsValue → O(n)
```

---

## remove

Удаляет запись по ключу:

```java
V remove(Object key);
```

```java
Integer removed = map.remove("java");
```

Метод возвращает удалённое значение.

Есть перегруженный вариант:

```java
boolean remove(Object key, Object value);
```

```java
map.remove("java", 10);
```

Запись удалится только в случае совпадения ключа и значения.

---

## replace

Заменяет значение только для существующего ключа.

```java
map.replace("java", 20);
```

В отличие от `put()`, новый ключ создан не будет.

Можно проверить старое значение:

```java
map.replace("java", 10, 20);
```

Значение изменится только тогда, когда текущим значением является `10`.

---

## size

```java
int size();
```

Возвращает количество пар ключ–значение.

```java
map.size();
```

Размер определяется количеством ключей, а не количеством уникальных значений.

---

## isEmpty

```java
boolean isEmpty();
```

Проверяет, пуста ли карта.

---

## clear

```java
void clear();
```

Удаляет все записи.

---

# Представления Map

Карта предоставляет три основных представления своего содержимого:

```java
keySet();
values();
entrySet();
```

Они связаны с исходной картой и обычно не являются независимыми копиями.

---

## keySet

```java
Set<K> keySet();
```

Возвращает множество ключей.

```java
Set<String> keys = map.keySet();
```

Используется `Set`, потому что ключи уникальны.

```java
for (String key : map.keySet()) {
    System.out.println(key);
}
```

Удаление элемента через `keySet()` удалит соответствующую запись из карты:

```java
map.keySet().remove("java");
```

---

## values

```java
Collection<V> values();
```

Возвращает коллекцию значений.

```java
Collection<Integer> values = map.values();
```

Используется `Collection`, а не `Set`, потому что значения могут повторяться.

```java
Map<String, Integer> map = new HashMap<>();

map.put("A", 10);
map.put("B", 10);
```

Результат:

```text
[10, 10]
```

---

## entrySet

```java
Set<Map.Entry<K, V>> entrySet();
```

Возвращает множество пар ключ–значение.

```java
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer value = entry.getValue();

    System.out.println(key + " = " + value);
}
```

`entrySet()` является стандартным способом обхода карты, когда одновременно нужны ключ и значение.

---

# Map.Entry

`Map.Entry<K, V>` представляет одну запись карты.

Основные методы:

```java
entry.getKey();
entry.getValue();
entry.setValue(newValue);
```

Пример изменения значений:

```java
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    if (entry.getValue() < 0) {
        entry.setValue(0);
    }
}
```

---

# Почему лучше использовать entrySet

Можно обходить карту так:

```java
for (String key : map.keySet()) {
    Integer value = map.get(key);
}
```

Но предпочтительнее:

```java
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer value = entry.getValue();
}
```

В первом варианте для каждого ключа повторно выполняется поиск значения.

`entrySet()` сразу предоставляет пару и точнее выражает намерение программы.

---

# Методы вычисления значений

Интерфейс `Map` содержит методы, позволяющие вычислять значения:

```text
compute
computeIfAbsent
computeIfPresent
merge
replaceAll
```

---

## computeIfAbsent

```java
V computeIfAbsent(
        K key,
        Function<? super K, ? extends V> mappingFunction
);
```

Возвращает существующее значение или создаёт новое, если значения по ключу нет.

```java
Map<String, List<String>> groups = new HashMap<>();

groups.computeIfAbsent(
        "backend",
        ignored -> new ArrayList<>()
).add("Java");
```

Логика:

1. Проверяется ключ.
2. Если значения нет, вызывается функция.
3. Созданное значение добавляется в карту.
4. Значение возвращается вызывающему коду.

Без `computeIfAbsent()`:

```java
if (!groups.containsKey("backend")) {
    groups.put("backend", new ArrayList<>());
}

groups.get("backend").add("Java");
```

Через `computeIfAbsent()`:

```java
groups.computeIfAbsent(
        "backend",
        ignored -> new ArrayList<>()
).add("Java");
```

Если функция вернёт `null`, новая запись не будет добавлена.

Метод использовался в задаче `Group Anagrams`:

```java
groups.computeIfAbsent(
        key,
        ignored -> new ArrayList<>()
).add(word);
```

---

## computeIfPresent

Вычисляет новое значение, только если ключ уже существует.

```java
map.computeIfPresent(
        "java",
        (key, value) -> value + 1
);
```

Если ключ отсутствует, функция не вызывается.

Если функция вернёт `null`, запись удаляется.

---

## compute

Всегда выполняет вычисление для указанного ключа.

```java
map.compute(
        "java",
        (key, value) -> value == null ? 1 : value + 1
);
```

Функция получает:

- ключ
- текущее значение
- `null`, если значения нет

Если функция вернёт `null`, запись будет удалена.

```java
map.compute("java", (key, value) -> null);
```

---

## merge

```java
V merge(
        K key,
        V value,
        BiFunction<? super V, ? super V, ? extends V> remappingFunction
);
```

Удобен для подсчёта частот.

```java
Map<String, Integer> frequencies = new HashMap<>();

frequencies.merge("java", 1, Integer::sum);
frequencies.merge("java", 1, Integer::sum);
```

Результат:

```text
java → 2
```

Логика:

- если ключ отсутствует, добавляется переданное значение
- если ключ существует, старое и новое значения объединяются функцией

Вариант через `getOrDefault()`:

```java
frequencies.put(
        "java",
        frequencies.getOrDefault("java", 0) + 1
);
```

Вариант через `merge()`:

```java
frequencies.merge("java", 1, Integer::sum);
```

---

# Основные реализации Map

Наиболее распространённые реализации:

```text
HashMap
LinkedHashMap
TreeMap
```

Краткое сравнение:

| Реализация | Порядок | Поиск | Структура |
|---|---|---:|---|
| `HashMap` | Не гарантирован | `O(1)` в среднем | Хеш-таблица |
| `LinkedHashMap` | Порядок вставки или доступа | `O(1)` в среднем | Хеш-таблица и связный список |
| `TreeMap` | Сортировка по ключам | `O(log n)` | Красно-чёрное дерево |

---

# HashMap

`HashMap` — основная реализация `Map`.

```java
Map<String, Integer> map = new HashMap<>();
```

Подходит, когда:

- нужен быстрый поиск по ключу
- порядок элементов не важен
- ключи имеют корректные `equals()` и `hashCode()`

Средняя сложность:

| Операция | Сложность |
|---|---:|
| `put` | `O(1)` |
| `get` | `O(1)` |
| `remove` | `O(1)` |
| `containsKey` | `O(1)` |
| `containsValue` | `O(n)` |
| обход | `O(n)` |

`O(1)` является средней, а не гарантированной сложностью.

---

# Внутреннее устройство HashMap

Упрощённо `HashMap` содержит массив бакетов:

```text
table
```

Пример:

```text
index 0 → null
index 1 → Entry
index 2 → Entry → Entry
index 3 → null
index 4 → Entry
```

Каждая запись содержит примерно следующие данные:

```text
hash
key
value
next
```

Поле `next` используется для связи записей, попавших в один бакет.

При большом количестве записей связный список может быть преобразован в красно-чёрное дерево.

---

# Что происходит при put

```java
map.put("java", 10);
```

Упрощённый алгоритм:

1. Вычисляется `hashCode()` ключа.
2. Биты хеша дополнительно перемешиваются.
3. Вычисляется индекс бакета.
4. Проверяется содержимое бакета.
5. Если равного ключа нет, добавляется новая запись.
6. Если равный ключ найден, его значение заменяется.
7. При превышении порога выполняется расширение таблицы.

```text
hashCode
→ смешивание хеша
→ индекс бакета
→ поиск через hash и equals
→ добавление или замена
→ возможный resize
```

---

# Вычисление индекса бакета

Упрощённая формула:

```text
index = hash & (capacity - 1)
```

Вместимость таблицы обычно является степенью двойки:

```text
16
32
64
128
```

Например:

```text
capacity = 16
capacity - 1 = 15
```

В двоичном виде:

```text
15 = 00001111
```

Побитовая операция позволяет быстро определить индекс бакета.

---

# hashCode и equals

Для поиска ключа используются оба метода.

## hashCode

```java
key.hashCode();
```

Помогает определить бакет.

## equals

```java
existingKey.equals(searchKey);
```

Используется для поиска точного ключа внутри бакета.

Условие логического совпадения ключей:

```text
подходящий hash
и
equals возвращает true
```

Главное правило контракта:

> Если два объекта равны по `equals()`, их `hashCode()` обязан совпадать.

```text
a.equals(b) == true
→
a.hashCode() == b.hashCode()
```

Обратное утверждение неверно.

Одинаковый `hashCode()` не означает, что объекты равны.

Подробно контракт `equals()` и `hashCode()` рассматривается в отдельной теме.

---

# Коллизии

Коллизия возникает, когда разные ключи попадают в один бакет.

```text
key A → bucket 5
key B → bucket 5
```

Это нормальная ситуация для хеш-таблицы.

В бакете может образоваться цепочка:

```text
A → B → C
```

Для поиска записи `HashMap`:

1. Находит бакет.
2. Сравнивает хеши.
3. Сравнивает ключи через `equals()`.
4. Возвращает найденное значение.

Большое количество коллизий ухудшает производительность.

---

# Преобразование списка в дерево

Если в бакете становится много записей, связный список может быть преобразован в красно-чёрное дерево.

Сложность поиска:

```text
связный список → O(n)
красно-чёрное дерево → O(log n)
```

Основные внутренние пороги:

```text
TREEIFY_THRESHOLD = 8
MIN_TREEIFY_CAPACITY = 64
```

Это означает, что при достижении длинной цепочки карта рассматривает преобразование в дерево.

Если таблица ещё маленькая, сначала обычно выполняется расширение.

---

# Capacity

`Capacity` — количество бакетов во внутренней таблице.

Стандартная начальная вместимость:

```text
16
```

При создании пустой карты внутренний массив может быть выделен только при первом добавлении.

Можно задать ожидаемую вместимость:

```java
Map<Long, User> users = new HashMap<>(100);
```

Это полезно, когда примерное количество записей известно заранее.

Правильно выбранная вместимость уменьшает количество расширений.

---

# Load factor

`Load factor` — коэффициент, определяющий допустимое заполнение таблицы до расширения.

Стандартное значение:

```text
0.75
```

Порог вычисляется так:

```text
threshold = capacity × loadFactor
```

Для вместимости `16`:

```text
threshold = 16 × 0.75 = 12
```

После превышения порога карта выполняет расширение.

---

# Threshold

`Threshold` — конкретное количество элементов, после которого запускается расширение.

```text
capacity = 16
load factor = 0.75
threshold = 12
```

Важно различать:

```text
load factor → коэффициент
threshold → количество элементов
```

---

# Resize

`Resize` — процесс увеличения внутренней таблицы.

Обычно вместимость увеличивается в два раза:

```text
16 → 32
32 → 64
64 → 128
```

После изменения вместимости записи перераспределяются между бакетами.

Операция дорогая, потому что необходимо обработать множество элементов.

Однако resize выполняется не при каждом `put()`. Поэтому средняя стоимость добавления остаётся амортизированной `O(1)`.

```text
load factor → коэффициент заполнения
threshold → порог количества элементов
resize → процесс расширения
capacity → количество бакетов
```

---

# Почему HashMap работает за O(1) только в среднем

При хорошем распределении ключей каждый бакет содержит мало записей.

```text
ключ → хеш → конкретный бакет
```

В плохом случае большое количество ключей попадает в один бакет.

Тогда сложность поиска ухудшается:

```text
список → O(n)
дерево → O(log n)
```

Поэтому корректная формулировка:

> `HashMap` выполняет поиск, добавление и удаление за `O(1)` в среднем.

---

# null в HashMap

`HashMap` допускает:

- один `null`-ключ
- несколько `null`-значений

```java
Map<String, String> map = new HashMap<>();

map.put(null, "value");
map.put("first", null);
map.put("second", null);
```

Почему `null`-ключ может быть только один:

- ключи уникальны
- все попытки добавить `null` используют один и тот же ключ

Для `null` применяется специальная обработка. Обычно такая запись попадает в нулевой бакет.

---

# Изменяемые ключи

Ключи `HashMap` желательно делать неизменяемыми.

Допустим, `equals()` и `hashCode()` объекта зависят от email:

```java
class UserKey {

    private String email;
}
```

Использование:

```java
UserKey key = new UserKey("old@example.com");

map.put(key, "value");

key.changeEmail("new@example.com");
```

После изменения email изменяется `hashCode()`.

Запись физически остаётся в бакете, вычисленном по старому хешу. Но поиск выполняется по новому хешу.

```java
map.get(key); // может вернуть null
map.remove(key); // может вернуть null
```

Правило:

> Поля, участвующие в `equals()` и `hashCode()`, не должны изменяться, пока объект используется как ключ хешированной коллекции.

Подходящие ключи:

```text
String
Integer
Long
UUID
record
immutable value object
```

---

# LinkedHashMap

`LinkedHashMap` основан на `HashMap`, но дополнительно поддерживает порядок записей.

```java
Map<String, Integer> map = new LinkedHashMap<>();

map.put("B", 2);
map.put("A", 1);
map.put("C", 3);
```

Порядок обхода:

```text
B
A
C
```

По умолчанию сохраняется порядок вставки.

Для поддержки порядка используется дополнительный двусвязный список.

Основные операции обычно сохраняют среднюю сложность `O(1)`, но `LinkedHashMap` требует больше памяти, чем `HashMap`.

---

# Порядок доступа LinkedHashMap

Можно создать карту с порядком последнего доступа:

```java
Map<String, Integer> map =
        new LinkedHashMap<>(16, 0.75f, true);
```

Последний параметр:

```text
accessOrder = true
```

После обращения к записи она перемещается в конец порядка.

```java
map.put("A", 1);
map.put("B", 2);
map.put("C", 3);

map.get("A");
```

Порядок станет:

```text
B
C
A
```

`A` использовалась последней.

Этот режим применяется для реализации LRU-кеша.

---

# LRU cache

LRU означает:

```text
Least Recently Used
```

При переполнении удаляется запись, к которой дольше всего не обращались.

Пример:

```java
public class LruCache<K, V> extends LinkedHashMap<K, V> {

    private final int capacity;

    public LruCache(int capacity) {
        super(capacity, 0.75f, true);
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(
            Map.Entry<K, V> eldest
    ) {
        return size() > capacity;
    }
}
```

`accessOrder = true` означает порядок последнего доступа, а не порядок добавления.

---

# TreeMap

`TreeMap` хранит ключи в отсортированном порядке.

```java
Map<Integer, String> map = new TreeMap<>();

map.put(3, "C");
map.put(1, "A");
map.put(2, "B");
```

Порядок обхода:

```text
1
2
3
```

Внутри используется красно-чёрное дерево.

Основные сложности:

| Операция | Сложность |
|---|---:|
| `put` | `O(log n)` |
| `get` | `O(log n)` |
| `remove` | `O(log n)` |

---

# Сравнение ключей в TreeMap

`TreeMap` может использовать естественный порядок или переданный `Comparator`.

## Comparable

```java
Map<Integer, String> map = new TreeMap<>();
```

`Integer` реализует `Comparable<Integer>`.

Сравнение выполняется через:

```java
first.compareTo(second);
```

## Comparator

```java
Map<String, Integer> map =
        new TreeMap<>(Comparator.reverseOrder());
```

Ключи будут отсортированы в обратном порядке.

---

# Уникальность ключей в TreeMap

`TreeMap` определяет равенство ключей через результат сравнения.

```java
compare(first, second) == 0
```

Если результат равен нулю, карта считает ключи одинаковыми.

Это верно даже тогда, когда:

```java
first.equals(second) == false
```

Поэтому `Comparator` должен быть согласован с логикой программы.

---

# null в TreeMap

При использовании естественного порядка `TreeMap` обычно не допускает `null`-ключ.

```java
map.put(null, "value");
```

Результат:

```text
NullPointerException
```

Причина в том, что `null` нельзя сравнить с обычными ключами.

`null`-значения допускаются.

Пользовательский `Comparator` технически может поддерживать `null`, но в стандартном собеседовательном ответе считается, что `TreeMap` не допускает `null`-ключи.

---

# NavigableMap

`TreeMap` реализует интерфейс `NavigableMap`.

Полезные методы:

```java
lowerKey(key);
floorKey(key);
ceilingKey(key);
higherKey(key);
firstKey();
lastKey();
```

Пример:

```java
TreeMap<Integer, String> map = new TreeMap<>();

map.put(10, "A");
map.put(20, "B");
map.put(30, "C");
```

Результаты:

```java
map.lowerKey(20);   // 10
map.floorKey(20);   // 20
map.ceilingKey(25); // 30
map.higherKey(20);  // 30
```

Различия:

```text
lower   → строго меньше
floor   → меньше или равно
ceiling → больше или равно
higher  → строго больше
```

`TreeMap` также позволяет получать диапазоны:

```java
map.headMap(20);
map.tailMap(20);
map.subMap(10, 30);
```

---

# Выбор реализации Map

## HashMap

Используется, когда:

- нужен быстрый поиск по ключу
- порядок элементов не важен
- не нужны диапазонные операции

```java
Map<Long, User> usersById = new HashMap<>();
```

## LinkedHashMap

Используется, когда:

- требуется порядок вставки
- нужен предсказуемый обход
- требуется порядок последнего доступа
- создаётся простой LRU-кеш

```java
Map<String, Object> response = new LinkedHashMap<>();
```

## TreeMap

Используется, когда:

- ключи должны быть отсортированы
- нужны диапазоны
- нужно искать ближайший меньший или больший ключ

```java
NavigableMap<Instant, Event> events = new TreeMap<>();
```

---

# Неизменяемые карты

## Map.of

```java
Map<String, Integer> priorities = Map.of(
        "LOW", 1,
        "HIGH", 2
);
```

Полученная карта неизменяема.

```java
priorities.put("CRITICAL", 3);
```

Результат:

```text
UnsupportedOperationException
```

`Map.of()` не допускает:

- `null`-ключи
- `null`-значения
- повторяющиеся ключи

Для большого количества записей используется:

```java
Map<String, Integer> map = Map.ofEntries(
        Map.entry("A", 1),
        Map.entry("B", 2),
        Map.entry("C", 3)
);
```

---

## Collections.unmodifiableMap

```java
Map<String, Integer> source = new HashMap<>();

Map<String, Integer> view =
        Collections.unmodifiableMap(source);
```

Через `view` нельзя изменять карту:

```java
view.put("A", 1);
```

Но исходная карта остаётся изменяемой:

```java
source.put("A", 1);
```

Изменение будет видно через `view`.

```text
unmodifiableMap → неизменяемое представление исходной карты
```

---

## Map.copyOf

```java
Map<String, Integer> copy = Map.copyOf(source);
```

Создаёт неизменяемую копию текущего содержимого.

Последующие изменения `source` не изменяют `copy`.

```text
Collections.unmodifiableMap → представление
Map.copyOf → неизменяемая копия
```

`Map.copyOf()` не допускает `null`-ключи и `null`-значения.

---

# ConcurrentHashMap

Обычный `HashMap` не является потокобезопасным.

При конкурентном доступе может использоваться:

```java
ConcurrentHashMap<K, V>
```

Основные свойства:

- поддерживает конкурентный доступ
- не блокирует всю карту одной общей блокировкой
- не допускает `null`-ключи
- не допускает `null`-значения
- предоставляет атомарные методы вроде `putIfAbsent()` и `compute()`

Причина запрета `null` связана с однозначностью результата:

```java
map.get(key) == null
```

В конкурентной карте это должно однозначно означать отсутствие значения.

Подробно `ConcurrentHashMap` рассматривается в теме многопоточности.

---

# Частые ошибки

## Использование изменяемого ключа

```java
map.put(user, value);

user.changeEmail(newEmail);
```

Если email участвует в `hashCode()`, запись может перестать находиться.

---

## Надежда на порядок HashMap

`HashMap` не гарантирует порядок.

Даже если порядок кажется стабильным, контракт этого не обещает.

Для порядка вставки используется `LinkedHashMap`.

---

## Использование containsValue для частого поиска

```java
map.containsValue(value);
```

Работает за `O(n)`.

Если требуется быстрый поиск и по ключам, и по значениям, может понадобиться дополнительная структура данных.

---

## Повторный поиск через keySet

Менее предпочтительно:

```java
for (K key : map.keySet()) {
    V value = map.get(key);
}
```

Предпочтительно:

```java
for (Map.Entry<K, V> entry : map.entrySet()) {
    K key = entry.getKey();
    V value = entry.getValue();
}
```

---

## Нарушение equals и hashCode

Если равные по `equals()` ключи имеют разные `hashCode()`, `HashMap` может не найти запись.

---

## Неверный Comparator для TreeMap

Если:

```java
comparator.compare(first, second) == 0
```

`TreeMap` считает ключи одинаковыми.

Некорректный `Comparator` может приводить к неожиданной замене записей.

---

## Автоматическое использование TreeMap ради сортировки

`TreeMap` выполняет каждую операцию за `O(log n)`.

Когда сортировка нужна только один раз, иногда выгоднее:

1. Хранить данные в `HashMap`.
2. Получить список записей.
3. Отсортировать его перед выводом.

Выбор зависит от того, требуется ли постоянно поддерживать порядок.

---

# Сложность операций

| Операция | HashMap | LinkedHashMap | TreeMap |
|---|---:|---:|---:|
| `get` | `O(1)` среднее | `O(1)` среднее | `O(log n)` |
| `put` | `O(1)` среднее | `O(1)` среднее | `O(log n)` |
| `remove` | `O(1)` среднее | `O(1)` среднее | `O(log n)` |
| `containsKey` | `O(1)` среднее | `O(1)` среднее | `O(log n)` |
| `containsValue` | `O(n)` | `O(n)` | `O(n)` |
| обход | `O(n)` | `O(n)` | `O(n)` |
| поддержка порядка | Нет | Вставка или доступ | Сортировка |

---

# Сравнение реализаций

| Характеристика | HashMap | LinkedHashMap | TreeMap |
|---|---|---|---|
| Внутренняя структура | Хеш-таблица | Хеш-таблица и список | Красно-чёрное дерево |
| Порядок | Не гарантирован | Вставка или доступ | Сортировка ключей |
| Скорость поиска | `O(1)` среднее | `O(1)` среднее | `O(log n)` |
| `null`-ключ | Один | Один | Обычно запрещён |
| `null`-значения | Разрешены | Разрешены | Разрешены |
| Требования к ключам | `equals` и `hashCode` | `equals` и `hashCode` | `Comparable` или `Comparator` |
| Типичное применение | Быстрый поиск | Предсказуемый порядок | Сортировка и диапазоны |

---

# Вопросы с собеседований

## Может ли HashMap хранить null

Да.

```text
один null-ключ
несколько null-значений
```

## Может ли TreeMap хранить null

При естественном порядке:

```text
null-ключ запрещён
null-значения разрешены
```

## Почему HashMap работает за O(1)

Хеш ключа позволяет вычислить индекс бакета без полного перебора карты.

Это средняя, а не гарантированная сложность.

## Что такое коллизия

Попадание разных ключей в один бакет.

## Зачем нужны equals и hashCode

```text
hashCode → выбор бакета
equals → поиск точного ключа
```

## Почему ключ должен быть неизменяемым

Изменение поля, участвующего в `hashCode()`, может изменить бакет, в котором карта будет искать ключ.

## Чем LinkedHashMap отличается от HashMap

`LinkedHashMap` поддерживает порядок вставки или доступа.

## Чем TreeMap отличается от HashMap

`TreeMap` сортирует ключи и работает за `O(log n)`.

`HashMap` не гарантирует порядок и работает за `O(1)` в среднем.

## Что происходит при повторном put

Старое значение заменяется новым, а метод возвращает предыдущее значение.

## Почему containsValue работает за O(n)

По значению нельзя вычислить конкретный бакет. Необходимо просматривать записи.

## Как TreeMap определяет одинаковые ключи

Через результат `compareTo()` или `Comparator.compare()`.

```java
compare(first, second) == 0
```

## Что такое load factor

Коэффициент, используемый для вычисления порога расширения таблицы.

## Что такое threshold

Количество записей, после которого запускается расширение.

## Что такое resize

Увеличение внутреннего массива бакетов и перераспределение записей.

## Для чего нужен accessOrder

Для хранения записей в порядке последнего доступа. Применяется при реализации LRU-кеша.

---

# Вопросы для самопроверки

1. Почему `Map` не наследует `Collection`?
2. Чем ключ отличается от значения?
3. Что возвращает `put()`?
4. Чем `get()` отличается от `getOrDefault()`?
5. Почему `containsValue()` работает за `O(n)`?
6. Какие типы возвращают `keySet()`, `values()` и `entrySet()`?
7. Для чего используется `computeIfAbsent()`?
8. Чем `compute()` отличается от `computeIfPresent()`?
9. Для чего используется `merge()`?
10. Что происходит внутри `HashMap` при `put()`?
11. Какую роль выполняет `hashCode()`?
12. Какую роль выполняет `equals()`?
13. Что такое коллизия?
14. Как `HashMap` обрабатывает длинные цепочки коллизий?
15. Что такое capacity?
16. Что такое load factor?
17. Что такое threshold?
18. Что происходит при resize?
19. Почему операции `HashMap` работают за `O(1)` только в среднем?
20. Почему ключи желательно делать неизменяемыми?
21. Какие `null` допускает `HashMap`?
22. Чем `LinkedHashMap` отличается от `HashMap`?
23. Для чего используется `accessOrder = true`?
24. Что такое LRU?
25. Чем `TreeMap` отличается от `HashMap`?
26. Как `TreeMap` сравнивает ключи?
27. Какие навигационные методы предоставляет `TreeMap`?
28. Чем `Collections.unmodifiableMap()` отличается от `Map.copyOf()`?
29. Когда следует выбирать `HashMap`?
30. Когда следует выбирать `LinkedHashMap`?
31. Когда следует выбирать `TreeMap`?

---

# Краткая памятка

```text
HashMap:
быстрый поиск
порядок не гарантирован
O(1) в среднем
```

```text
LinkedHashMap:
порядок вставки или доступа
O(1) в среднем
```

```text
TreeMap:
ключи отсортированы
O(log n)
```

```text
hashCode → бакет
equals → точный ключ
```

```text
load factor → коэффициент
threshold → порог элементов
resize → процесс расширения
capacity → количество бакетов
```

```text
keySet   → Set ключей
values   → Collection значений
entrySet → Set пар ключ–значение
```

Главное правило выбора:

> Используй `HashMap` по умолчанию. Выбирай `LinkedHashMap`, когда нужен предсказуемый порядок. Выбирай `TreeMap`, когда ключи должны постоянно храниться отсортированными или нужны диапазонные операции.

---

## См. также

- [`01-collections-framework.md`](01-collections-framework.md) — общая иерархия
  коллекций
- [`03-equals-hashcode.md`](03-equals-hashcode.md) — почему нарушение контракта
  ломает поиск по ключу
- [`../concurrency/04-concurrent-collections.md`](../concurrency/04-concurrent-collections.md) —
  `ConcurrentHashMap`, атомарные операции и запрет `null`