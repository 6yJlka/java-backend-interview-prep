# Java Collections Framework

## Что такое Collections Framework

Java Collections Framework — это набор интерфейсов, реализаций и алгоритмов для хранения и обработки групп объектов.

Фреймворк предоставляет:

- общие интерфейсы для разных типов коллекций;
- готовые реализации структур данных;
- единый набор методов для работы с элементами;
- алгоритмы сортировки, поиска, перемешивания и других операций.

Примеры коллекций:

```java
List<String> names = new ArrayList<>();
Set<Integer> uniqueNumbers = new HashSet<>();
Queue<String> tasks = new ArrayDeque<>();
Map<Long, String> users = new HashMap<>();
```

## Основные понятия

Важно различать три похожих названия:

```text
Collection
Collections
Map
```

### Collection

`Collection<E>` — базовый интерфейс для большинства коллекций.

Он описывает группу отдельных элементов типа `E`.

```java
Collection<String> values = new ArrayList<>();
```

Основные методы:

```java
add(element)
remove(element)
contains(element)
size()
isEmpty()
clear()
iterator()
```

### Collections

`Collections` — утилитный класс.

Он содержит статические методы для работы с коллекциями:

```java
Collections.sort(list);
Collections.reverse(list);
Collections.shuffle(list);
Collections.min(list);
Collections.max(list);
```

Объект класса `Collections` создавать не нужно:

```java
new Collections(); // невозможно
```

### Map

`Map<K, V>` хранит пары:

```text
ключ → значение
```

Пример:

```java
Map<Long, String> users = new HashMap<>();

users.put(1L, "Alice");
users.put(2L, "Bob");
```

`Map` не наследуется от `Collection`.

Коллекция хранит отдельные элементы:

```text
element
element
element
```

Карта хранит соответствия:

```text
key → value
key → value
```

При этом `Map` предоставляет представления своих данных в виде коллекций:

```java
map.keySet();    // Set<K>
map.values();    // Collection<V>
map.entrySet();  // Set<Map.Entry<K, V>>
```

## Упрощённая иерархия

```text
Iterable<E>
    │
    └── Collection<E>
            │
            ├── List<E>
            │
            ├── Set<E>
            │
            └── Queue<E>
                    │
                    └── Deque<E>

Map<K, V> — отдельная иерархия
```

Это упрощённая схема. Некоторые интерфейсы используют множественное наследование интерфейсов.

## Iterable

`Iterable<E>` — базовый интерфейс объектов, элементы которых можно последовательно обходить.

Основной метод:

```java
Iterator<E> iterator();
```

Благодаря `Iterable` коллекцию можно использовать в цикле `for-each`:

```java
List<String> names = List.of("Alice", "Bob", "Charlie");

for (String name : names) {
    System.out.println(name);
}
```

Цикл `for-each` под капотом использует итератор.

Упрощённо:

```java
Iterator<String> iterator = names.iterator();

while (iterator.hasNext()) {
    String name = iterator.next();
    System.out.println(name);
}
```

## List

`List<E>` представляет упорядоченную последовательность элементов.

Основные свойства:

- сохраняет порядок элементов;
- допускает дубликаты;
- поддерживает доступ по индексу;
- один элемент может встречаться несколько раз.

```java
List<String> names = new ArrayList<>();

names.add("Alice");
names.add("Bob");
names.add("Alice");
```

Содержимое:

```text
[Alice, Bob, Alice]
```

Доступ по индексу:

```java
String first = names.get(0);
```

Основные реализации:

```java
ArrayList
LinkedList
```

## Set

`Set<E>` представляет множество уникальных элементов.

Основные свойства:

- не допускает логических дубликатов;
- обычно не предоставляет доступ по индексу;
- уникальность определяется через `equals()` и `hashCode()` либо через порядок сравнения.

```java
Set<String> names = new HashSet<>();

names.add("Alice");
names.add("Bob");
names.add("Alice");
```

В множестве останутся:

```text
[Alice, Bob]
```

Основные реализации:

```java
HashSet
LinkedHashSet
TreeSet
```

## Queue

`Queue<E>` представляет коллекцию элементов, ожидающих обработки.

Часто очередь работает по принципу FIFO:

```text
First In — First Out
```

Первый добавленный элемент обрабатывается первым.

Однако интерфейс `Queue` сам по себе не гарантирует FIFO для всех реализаций. Например, `PriorityQueue` извлекает элементы в соответствии с приоритетом.

Основные операции:

```java
offer(element)
poll()
peek()
```

Пример:

```java
Queue<String> tasks = new ArrayDeque<>();

tasks.offer("first");
tasks.offer("second");
tasks.offer("third");

String next = tasks.poll();
```

Результат:

```text
first
```

## Deque

`Deque<E>` — двусторонняя очередь.

Название означает:

```text
Double Ended Queue
```

Она позволяет добавлять, удалять и просматривать элементы с обоих концов.

```java
Deque<String> deque = new ArrayDeque<>();

deque.addFirst("first");
deque.addLast("last");

String first = deque.removeFirst();
String last = deque.removeLast();
```

`Deque` может использоваться:

- как обычная очередь FIFO;
- как стек LIFO;
- как двусторонняя очередь.

Для реализации стека обычно рекомендуется использовать `Deque`, а не устаревший класс `Stack`.

```java
Deque<Integer> stack = new ArrayDeque<>();

stack.push(10);
stack.push(20);

int value = stack.pop();
```

Результат:

```text
20
```

## Map

`Map<K, V>` связывает уникальный ключ со значением.

```java
Map<String, Integer> ages = new HashMap<>();

ages.put("Alice", 25);
ages.put("Bob", 30);
```

Основные свойства:

- ключи уникальны;
- значения могут повторяться;
- новое значение по существующему ключу заменяет старое;
- доступ выполняется по ключу.

```java
ages.put("Alice", 26);
```

После этого:

```text
Alice → 26
Bob   → 30
```

Основные реализации:

```java
HashMap
LinkedHashMap
TreeMap
```

## Sequenced Collections в Java 21

В Java 21 появились интерфейсы для коллекций с определённым порядком обхода:

```java
SequencedCollection<E>
SequencedSet<E>
SequencedMap<K, V>
```

Такие коллекции имеют понятие первого и последнего элемента.

Основные методы:

```java
getFirst()
getLast()
addFirst(element)
addLast(element)
removeFirst()
removeLast()
reversed()
```

Например, `List` и `Deque` являются `SequencedCollection`.

```java
List<String> names = new ArrayList<>();

names.add("Bob");
names.addFirst("Alice");
names.addLast("Charlie");

String first = names.getFirst();
String last = names.getLast();
```

Результат:

```text
first = Alice
last = Charlie
```

Метод `reversed()` возвращает представление коллекции в обратном порядке:

```java
SequencedCollection<String> reversed = names.reversed();
```

## Необязательные операции

Некоторые операции интерфейса `Collection` являются необязательными для конкретной реализации.

Например, неизменяемая коллекция не поддерживает добавление:

```java
List<String> names = List.of("Alice", "Bob");

names.add("Charlie");
```

Результат:

```text
UnsupportedOperationException
```

Наличие метода в интерфейсе не гарантирует, что конкретная реализация разрешает изменение коллекции.

## Программирование через интерфейс

Предпочтительно объявлять переменную через интерфейс:

```java
List<String> names = new ArrayList<>();
Set<Integer> numbers = new HashSet<>();
Map<Long, String> users = new HashMap<>();
```

А не через конкретный класс:

```java
ArrayList<String> names = new ArrayList<>();
HashSet<Integer> numbers = new HashSet<>();
HashMap<Long, String> users = new HashMap<>();
```

Это уменьшает зависимость кода от конкретной реализации.

Реализацию можно заменить:

```java
List<String> names = new LinkedList<>();
```

без изменения типа переменной и большей части использующего её кода.

## Что нужно запомнить

```text
Collection — интерфейс группы элементов
Collections — утилитный класс со статическими методами
Map — отдельная структура ключ → значение
```

Основной выбор:

```text
Нужен порядок и индексы       → List
Нужны уникальные элементы     → Set
Нужна очередь обработки       → Queue
Нужна работа с обоими концами → Deque
Нужно соответствие ключу      → Map
```

# List

`List<E>` — упорядоченная коллекция элементов.

Основные свойства:

- сохраняет порядок добавления;
- допускает дубликаты;
- допускает доступ по индексу;
- может хранить несколько равных элементов;
- обычно допускает `null`, но это зависит от реализации.

```java
List<String> values = new ArrayList<>();

values.add("A");
values.add("B");
values.add("A");
```

Результат:

```text
[A, B, A]
```

## Основные методы List

```java
list.add(element);
list.add(index, element);

list.get(index);
list.set(index, element);

list.remove(index);
list.remove(element);

list.indexOf(element);
list.lastIndexOf(element);

list.subList(fromIndex, toIndex);
```

У метода `remove()` есть две перегрузки:

```java
remove(int index)
remove(Object element)
```

Это особенно важно при работе с `List<Integer>`:

```java
List<Integer> numbers = new ArrayList<>(List.of(10, 20, 30));

numbers.remove(1);
```

Будет удалён элемент по индексу `1`, то есть число `20`.

Чтобы удалить само число `1`, нужно написать:

```java
numbers.remove(Integer.valueOf(1));
```

## ArrayList

`ArrayList` основан на динамическом массиве.

Упрощённо внутри находится массив:

```java
Object[] elementData;
```

Когда массив заполняется, создаётся новый массив большего размера, а элементы копируются.

```text
старый массив
    ↓
создание нового массива
    ↓
копирование элементов
```

## Сложность ArrayList

| Операция | Сложность |
|---|---:|
| Получение по индексу | `O(1)` |
| Изменение по индексу | `O(1)` |
| Добавление в конец | `O(1)` амортизированно |
| Вставка в начало или середину | `O(n)` |
| Удаление из начала или середины | `O(n)` |
| Поиск по значению | `O(n)` |
| Проверка `contains()` | `O(n)` |

## Почему доступ по индексу O(1)

Элемент массива можно получить напрямую по его индексу:

```java
list.get(index);
```

Для доступа не требуется обходить предшествующие элементы.

## Почему вставка в середину O(n)

При вставке элементы после выбранной позиции необходимо сдвинуть вправо.

```text
[A, B, C, D]
       ↑ вставляем X

[A, B, X, C, D]
```

Элементы `C` и `D` должны быть перемещены.

## Амортизированное добавление

Обычное добавление в конец:

```java
list.add(element);
```

выполняется за `O(1)`, пока во внутреннем массиве есть свободное место.

При заполнении массива требуется:

1. создать новый массив;
2. скопировать старые элементы;
3. добавить новый элемент.

Отдельное расширение стоит `O(n)`, но оно происходит не при каждом добавлении. Поэтому средняя стоимость последовательности добавлений считается амортизированным `O(1)`.

## Capacity и size

`size` — количество элементов, фактически находящихся в списке.

`capacity` — размер внутреннего массива.

```java
List<String> values = new ArrayList<>(100);
```

Здесь начальная ёмкость равна `100`, но размер списка по-прежнему равен `0`.

```java
values.size(); // 0
```

Указание начальной ёмкости полезно, если заранее известно примерное количество элементов:

```java
List<Order> orders = new ArrayList<>(expectedCount);
```

Это может сократить количество расширений и копирований массива.

## LinkedList

`LinkedList` основан на двусвязном списке.

Каждый узел содержит:

```text
ссылка на предыдущий узел
значение
ссылка на следующий узел
```

Условно:

```text
null ← [A] ⇄ [B] ⇄ [C] → null
```

`LinkedList` реализует не только `List`, но и `Deque`.

Поэтому его можно использовать как:

- список;
- очередь;
- двустороннюю очередь;
- стек.

## Сложность LinkedList

| Операция | Сложность |
|---|---:|
| Получение по индексу | `O(n)` |
| Поиск по значению | `O(n)` |
| Добавление в начало | `O(1)` |
| Добавление в конец | `O(1)` |
| Удаление первого элемента | `O(1)` |
| Удаление последнего элемента | `O(1)` |
| Вставка по индексу | `O(n)` |
| Удаление по индексу | `O(n)` |

## Почему вставка по индексу не O(1)

Изменение ссылок узлов действительно занимает `O(1)`.

Но перед этим необходимо найти узел по нужному индексу:

```text
поиск узла: O(n)
изменение ссылок: O(1)
итого: O(n)
```

Вставка будет `O(1)`, только если ссылка на нужный узел уже имеется, например при работе через `ListIterator`.

## ArrayList и LinkedList

| Критерий | ArrayList | LinkedList |
|---|---|---|
| Внутренняя структура | Динамический массив | Двусвязный список |
| Доступ по индексу | `O(1)` | `O(n)` |
| Добавление в конец | `O(1)` амортизированно | `O(1)` |
| Вставка по индексу | `O(n)` | `O(n)` |
| Удаление по индексу | `O(n)` | `O(n)` |
| Дополнительная память | Меньше | Больше из-за ссылок |
| Локальность данных | Хорошая | Хуже |
| Реализует Deque | Нет | Да |

## Что выбирать

В большинстве случаев следует начинать с:

```java
ArrayList
```

Он обычно лучше подходит, когда:

- нужен доступ по индексу;
- элементы преимущественно добавляются в конец;
- важна скорость последовательного обхода;
- требуется меньше накладных расходов памяти.

`LinkedList` может быть оправдан, когда:

- активно используются операции с началом и концом;
- требуется реализация `Deque`;
- вставка или удаление выполняется через уже найденный итератор.

Для обычной очереди или стека чаще предпочтительнее:

```java
ArrayDeque
```

а не `LinkedList`.

## Типичные ошибки

### Считать вставку в LinkedList по индексу операцией O(1)

Поиск позиции занимает `O(n)`.

### Использовать LinkedList только потому, что часто выполняются вставки

Нужно учитывать стоимость поиска места вставки.

### Использовать List для частых удалений с начала

```java
arrayList.remove(0);
```

Для `ArrayList` это `O(n)`, потому что оставшиеся элементы сдвигаются.

Для очереди лучше использовать:

```java
Queue<Element> queue = new ArrayDeque<>();
```

### Путать size и capacity

Начальная ёмкость не создаёт элементы и не изменяет `size()`.

# Set

`Set<E>` — коллекция уникальных элементов.

Основные свойства:

- не допускает логических дубликатов;
- не предоставляет доступ по индексу;
- может хранить элементы в произвольном, вставочном или отсортированном порядке — в зависимости от реализации;
- повторное добавление равного элемента не изменяет множество.

```java
Set<String> names = new HashSet<>();

names.add("Alice");
names.add("Bob");
names.add("Alice");
```

В множестве останутся два элемента:

```text
Alice
Bob
```

Метод `add()` возвращает:

- `true`, если элемент был добавлен;
- `false`, если равный элемент уже находился в множестве.

```java
boolean first = names.add("Alice");  // true
boolean second = names.add("Alice"); // false
```

## Основные реализации

```java
HashSet
LinkedHashSet
TreeSet
```

Они отличаются порядком хранения, внутренней структурой и сложностью операций.

# HashSet

`HashSet` основан на хешировании.

Основные свойства:

- не сохраняет порядок вставки;
- операции поиска, добавления и удаления выполняются за `O(1)` в среднем;
- уникальность определяется с помощью `hashCode()` и `equals()`;
- допускает один `null`;
- внутри использует `HashMap`.

```java
Set<Integer> numbers = new HashSet<>();

numbers.add(30);
numbers.add(10);
numbers.add(20);
```

Нельзя рассчитывать, что обход будет выглядеть так:

```text
30, 10, 20
```

Порядок элементов не является частью контракта `HashSet`.

## Устройство HashSet

Элементы множества хранятся как ключи внутреннего `HashMap`.

Условно:

```text
элемент → PRESENT
```

Для всех ключей используется одно служебное значение-заглушка.

Поэтому корректная работа `HashSet` зависит от правильной реализации:

```java
equals()
hashCode()
```

## Сложность HashSet

| Операция | Средняя сложность |
|---|---:|
| `add()` | `O(1)` |
| `contains()` | `O(1)` |
| `remove()` | `O(1)` |
| обход всех элементов | `O(n)` |

Худший случай может быть хуже при большом количестве коллизий.

# LinkedHashSet

`LinkedHashSet` сочетает:

- хеш-таблицу;
- связную структуру, сохраняющую порядок элементов.

Основные свойства:

- сохраняет порядок вставки;
- не допускает дубликаты;
- операции добавления, поиска и удаления выполняются за `O(1)` в среднем;
- требует больше памяти, чем `HashSet`;
- допускает один `null`.

```java
Set<Integer> numbers = new LinkedHashSet<>();

numbers.add(30);
numbers.add(10);
numbers.add(20);
```

Обход гарантированно даст:

```text
30, 10, 20
```

`LinkedHashSet` полезен, когда нужны одновременно:

- уникальность;
- сохранение порядка первого появления элементов.

Например, удаление дубликатов из списка с сохранением порядка:

```java
List<Integer> values = List.of(3, 1, 3, 2, 1);

Set<Integer> unique = new LinkedHashSet<>(values);
```

Результат:

```text
[3, 1, 2]
```

# TreeSet

`TreeSet` хранит элементы в отсортированном порядке.

Внутри он основан на сбалансированном дереве и реализует интерфейсы:

```java
NavigableSet<E>
SortedSet<E>
```

Основные свойства:

- элементы автоматически сортируются;
- операции добавления, удаления и поиска выполняются за `O(log n)`;
- уникальность определяется сравнением элементов;
- можно использовать естественный порядок или `Comparator`;
- обычно `null` не поддерживается;
- предоставляет операции поиска ближайших элементов.

```java
Set<Integer> numbers = new TreeSet<>();

numbers.add(30);
numbers.add(10);
numbers.add(20);
```

Порядок обхода:

```text
10, 20, 30
```

## Естественный порядок

Если компаратор не передан, элементы должны реализовывать `Comparable`.

```java
Set<String> names = new TreeSet<>();
```

Строки будут храниться в естественном лексикографическом порядке.

## Пользовательский Comparator

```java
Set<String> names = new TreeSet<>(
        Comparator.comparingInt(String::length)
                  .thenComparing(Comparator.naturalOrder())
);
```

Элементы будут отсортированы сначала по длине, затем по алфавиту.

## Важная особенность TreeSet

Для `HashSet` равенство определяется через:

```java
hashCode()
equals()
```

Для `TreeSet` элементы считаются одинаковыми, если сравнение возвращает `0`:

```java
compare(a, b) == 0
```

или:

```java
a.compareTo(b) == 0
```

Это важно, потому что компаратор может считать два объекта одинаковыми, даже если `equals()` возвращает `false`.

Пример:

```java
Set<String> values =
        new TreeSet<>(Comparator.comparingInt(String::length));

values.add("cat");
values.add("dog");
```

Обе строки имеют длину `3`, поэтому компаратор возвращает `0`.

В результате в множестве останется только одна строка.

Чтобы сохранить обе, нужно добавить дополнительный критерий:

```java
Comparator.comparingInt(String::length)
          .thenComparing(Comparator.naturalOrder())
```

# NavigableSet

`TreeSet` предоставляет методы навигации по отсортированным данным.

```java
NavigableSet<Integer> numbers =
        new TreeSet<>(List.of(10, 20, 30, 40));
```

Основные методы:

```java
numbers.lower(30);   // 20 — строго меньше
numbers.floor(30);   // 30 — меньше или равно

numbers.higher(30);  // 40 — строго больше
numbers.ceiling(30); // 30 — больше или равно
```

Также:

```java
numbers.first();
numbers.last();

numbers.pollFirst();
numbers.pollLast();

numbers.headSet(30);
numbers.tailSet(30);
numbers.subSet(20, true, 40, false);
```

# Сравнение реализаций Set

| Критерий | HashSet | LinkedHashSet | TreeSet |
|---|---|---|---|
| Уникальность | Да | Да | Да |
| Порядок вставки | Нет | Да | Нет |
| Сортировка | Нет | Нет | Да |
| `add()` | `O(1)` в среднем | `O(1)` в среднем | `O(log n)` |
| `contains()` | `O(1)` в среднем | `O(1)` в среднем | `O(log n)` |
| `remove()` | `O(1)` в среднем | `O(1)` в среднем | `O(log n)` |
| Дополнительная память | Средняя | Больше | Больше |
| Механизм уникальности | `equals/hashCode` | `equals/hashCode` | `compareTo/Comparator` |
| `null` | Один | Один | Обычно нельзя |

# Что выбирать

```text
Нужна только уникальность
→ HashSet

Нужна уникальность и порядок вставки
→ LinkedHashSet

Нужна уникальность и сортировка
→ TreeSet
```

В большинстве задач начинаем с `HashSet`, если дополнительных требований к порядку нет.

# Типичные ошибки

## Ожидать порядок от HashSet

```java
Set<Integer> values = new HashSet<>();
```

Порядок обхода не гарантирован.

## Использовать TreeSet только для удаления дубликатов

Если сортировка не нужна, `HashSet` обычно быстрее:

```text
HashSet → O(1) в среднем
TreeSet → O(log n)
```

## Забыть про equals и hashCode

Для пользовательских объектов в `HashSet` необходимо корректно переопределить оба метода.

## Некорректный Comparator

Если компаратор возвращает `0` для разных объектов, `TreeSet` считает их дубликатами.

## Использовать изменяемый объект как элемент HashSet

Если поля, участвующие в `equals()` и `hashCode()`, изменить после добавления объекта, множество может перестать корректно его находить.

```java
Set<User> users = new HashSet<>();

User user = new User(1L, "Alice");
users.add(user);

user.setId(2L);
```

После изменения `id`:

```java
users.contains(user);
```

может вернуть неожиданный результат, потому что объект находится уже не в той корзине, которая соответствует его новому хешу.

# Что нужно запомнить

```text
HashSet       → уникальность
LinkedHashSet → уникальность + порядок вставки
TreeSet       → уникальность + сортировка
```

Механизм уникальности:

```text
HashSet и LinkedHashSet → equals() + hashCode()
TreeSet                 → compareTo() или Comparator
```

## Queue

`Queue` представляет структуру данных, в которой элементы обычно обрабатываются
по принципу FIFO: first in, first out.

Основные пары методов:

| Операция | Исключение при неудаче | Специальное значение |
|---|---|---|
| Добавление | `add()` | `offer()` |
| Получение с удалением | `remove()` | `poll()` |
| Просмотр без удаления | `element()` | `peek()` |

Для обычной очереди чаще используются `offer()`, `poll()` и `peek()`.

```java
Queue<Integer> queue = new ArrayDeque<>();

queue.offer(10);
queue.offer(20);
queue.offer(30);

int first = queue.poll();
int next = queue.peek();
```

## Deque

`Deque` — двусторонняя очередь, которая позволяет добавлять, удалять и
просматривать элементы с обоих концов.

| Операция | Начало | Конец |
|---|---|---|
| Добавление | `offerFirst()` | `offerLast()` |
| Удаление | `pollFirst()` | `pollLast()` |
| Просмотр | `peekFirst()` | `peekLast()` |

```java
Deque<Integer> deque = new ArrayDeque<>();

deque.offerFirst(10);
deque.offerLast(20);

int first = deque.pollFirst();
int last = deque.pollLast();
```
# PriorityQueue

`PriorityQueue<E>` — очередь с приоритетом. Внутри она основана на куче (`heap`).

По умолчанию первым извлекается минимальный элемент в соответствии с естественным порядком.

```java
PriorityQueue<Integer> queue = new PriorityQueue<>();

queue.offer(10);
queue.offer(3);
queue.offer(7);

queue.poll(); // 3
```

Порядок определяется:

- естественным порядком через `Comparable`;
- переданным `Comparator`.

## Max-heap

Чтобы первым извлекался максимальный элемент, можно передать обратный компаратор.

```java
PriorityQueue<Integer> maxHeap =
        new PriorityQueue<>(Comparator.reverseOrder());

maxHeap.offer(10);
maxHeap.offer(3);
maxHeap.offer(7);

maxHeap.poll(); // 10
```

Для пользовательского типа:

```java
PriorityQueue<User> queue = new PriorityQueue<>(
        Comparator.comparingInt(User::getPriority).reversed()
);
```

## Сложность PriorityQueue

| Операция | Сложность |
|---|---:|
| `offer()` / `add()` | `O(log n)` |
| `poll()` / `remove()` первого элемента | `O(log n)` |
| `peek()` / `element()` | `O(1)` |
| поиск произвольного элемента | `O(n)` |

Важно: внутренний массив `PriorityQueue` не обязан быть полностью отсортирован.
Гарантируется только то, что элемент с наивысшим приоритетом доступен через `peek()` / `poll()`.

Типичные применения:

```text
получение минимума или максимума
Top K
scheduler по приоритету
алгоритм Дейкстры
heap-задачи
```

# Comparable и Comparator

Оба интерфейса задают порядок объектов, но делают это по-разному.

## Comparable

`Comparable<T>` задаёт естественный порядок самого класса.

```java
public class User implements Comparable<User> {

    private final long id;

    @Override
    public int compareTo(User other) {
        return Long.compare(this.id, other.id);
    }
}
```

Основной метод:

```java
int compareTo(T other);
```

Результат сравнения:

```text
< 0 → текущий объект меньше
= 0 → объекты равны с точки зрения порядка
> 0 → текущий объект больше
```

Естественный порядок используется, например, здесь:

```java
Collections.sort(users);
```

Если `Comparator` явно не передан, элементы должны иметь естественный порядок.

## Comparator

`Comparator<T>` задаёт внешнюю стратегию сравнения.

```java
Comparator<User> byName =
        Comparator.comparing(User::getName);
```

Для одного класса можно создать сколько угодно стратегий:

```java
Comparator<User> byAge =
        Comparator.comparingInt(User::getAge);

Comparator<User> byName =
        Comparator.comparing(User::getName);

Comparator<User> bySalary =
        Comparator.comparing(User::getSalary);
```

Основной метод:

```java
int compare(T first, T second);
```

## Comparable и Comparator

```text
Comparable
→ естественный порядок
→ логика находится внутри класса
→ compareTo()

Comparator
→ внешний или альтернативный порядок
→ логика находится отдельно
→ compare()
```

Компараторы можно объединять:

```java
Comparator<User> comparator =
        Comparator.comparingInt(User::getAge)
                  .thenComparing(User::getName);
```

Также можно развернуть порядок:

```java
Comparator<User> byAgeDescending =
        Comparator.comparingInt(User::getAge).reversed();
```

## Collections.sort и List.sort

Оба варианта сортируют список на месте.

```java
Collections.sort(list);
```

Без явного `Comparator` используется естественный порядок элементов.

```java
list.sort(comparator);
```

Использует переданный `Comparator`.

Ни один из этих вызовов не создаёт новый отсортированный список.

# Iterator и ListIterator

`Iterator<E>` — интерфейс последовательного обхода элементов.

```java
Iterator<String> iterator = list.iterator();
```

Основные методы:

```java
hasNext();
next();
remove();
```

Цикл `for-each` использует `Iterator` под капотом.

```java
for (String value : list) {
    System.out.println(value);
}
```

Упрощённо эквивалентен:

```java
Iterator<String> iterator = list.iterator();

while (iterator.hasNext()) {
    String value = iterator.next();
    System.out.println(value);
}
```

## ListIterator

`ListIterator<E>` расширяет `Iterator<E>` и предназначен специально для `List`.

Он умеет двигаться в обе стороны:

```java
hasNext();
next();
hasPrevious();
previous();
```

Также доступны:

```java
nextIndex();
previousIndex();
set(element);
add(element);
remove();
```

Пример изменения элемента:

```java
ListIterator<String> iterator = list.listIterator();

while (iterator.hasNext()) {
    String value = iterator.next();

    if (value.equals("old")) {
        iterator.set("new");
    }
}
```

Кратко:

```text
Iterator
→ общий обход Collection
→ движение вперёд

ListIterator
→ только List
→ вперёд и назад
→ индексы
→ add / set
```

# Fail-fast Iterator

Многие итераторы обычных коллекций Java являются `fail-fast`.

Итератор пытается обнаружить структурное изменение коллекции, выполненное неожиданным способом во время обхода.

Например:

```java
for (String value : list) {
    if (value.equals("delete")) {
        list.remove(value);
    }
}
```

`for-each` использует `Iterator`, а изменение выполняется напрямую через `list`.

Упрощённо многие реализации используют два счётчика:

```text
modCount         → текущее число структурных изменений коллекции
expectedModCount → значение, которое ожидает Iterator
```

Если итератор обнаруживает:

```text
modCount != expectedModCount
```

он может выбросить:

```text
ConcurrentModificationException
```

Важно:

> `ConcurrentModificationException` не означает, что обязательно участвовало несколько потоков.

Его можно получить и в одном потоке.

## Безопасное удаление через Iterator

```java
Iterator<String> iterator = list.iterator();

while (iterator.hasNext()) {
    String value = iterator.next();

    if (value.equals("delete")) {
        iterator.remove();
    }
}
```

Здесь изменение выполняется через сам итератор, поэтому его внутреннее состояние обновляется корректно.

Также для удаления по условию часто подходит:

```java
list.removeIf(value -> value.equals("delete"));
```

## Что означает fail-fast

`fail-fast` — механизм раннего обнаружения неправильного структурного изменения.

Это `best effort`, а не строгая гарантия.

```text
fail-fast
→ пытается быстро обнаружить изменение
→ может выбросить ConcurrentModificationException

fail-fast
≠ механизм thread safety
≠ гарантия исключения при абсолютно любом неправильном изменении
```

# Immutable и Unmodifiable Collections

Важно различать неизменяемую коллекцию и неизменяемое представление другой коллекции.

## Immutable collection

Коллекцию нельзя структурно изменить после создания.

```java
List<String> list = List.of("A", "B");

list.add("C");
```

Результат:

```text
UnsupportedOperationException
```

То же касается:

```java
list.remove(...);
list.set(...);
```

## Unmodifiable view

```java
List<String> original = new ArrayList<>();
original.add("A");

List<String> view =
        Collections.unmodifiableList(original);
```

Через `view` изменять список нельзя:

```java
view.add("B");
```

Результат:

```text
UnsupportedOperationException
```

Но исходная коллекция остаётся изменяемой:

```java
original.add("B");
```

После этого изменение видно и через `view`:

```text
original → [A, B]
view     → [A, B]
```

Кратко:

```text
immutable collection
→ сама коллекция не изменяется

unmodifiable view
→ через эту ссылку менять нельзя
→ backing collection может измениться через другую ссылку
```

# List.copyOf, Set.copyOf и Map.copyOf

`copyOf()` возвращает неизменяемый snapshot текущего содержимого.

```java
List<String> original = new ArrayList<>();
original.add("A");

List<String> copy = List.copyOf(original);

original.add("B");
```

Результат:

```text
original → [A, B]
copy     → [A]
```

В отличие от `Collections.unmodifiableList(original)`, дальнейшие изменения исходной коллекции на результат `copyOf()` не влияют.

Однако `copyOf()` не обязана создавать новый объект, если аргумент уже является подходящей неизменяемой коллекцией.

```java
List<String> original = List.of("A", "B");
List<String> copy = List.copyOf(original);

// original == copy может быть true
```

Гарантируется неизменяемость результата, а не новая identity объекта.

# List.of, Set.of и Map.of

Фабричные методы создают неизменяемые коллекции.

## List.of

```java
List<String> values = List.of("A", "B");
```

Нельзя изменять список и нельзя передавать `null`.

```java
List.of("A", null); // NullPointerException
```

## Set.of

```java
Set<String> values = Set.of("A", "B");
```

Ограничения:

```text
null запрещён
дубликаты запрещены
структурные изменения запрещены
```

```java
Set.of("A", "A"); // IllegalArgumentException
```

## Map.of

```java
Map<String, Integer> map = Map.of(
        "A", 1,
        "B", 2
);
```

Ограничения:

```text
null-ключи запрещены
null-значения запрещены
повторяющиеся ключи запрещены
изменение карты запрещено
```

# Поверхностная неизменяемость

Неизменяемость коллекции не делает автоматически неизменяемыми объекты внутри неё.

```java
User user = new User("Dima");
List<User> users = List.of(user);

user.setName("Alex");
```

Структура списка не изменилась, но состояние объекта `User` изменилось.

Поэтому:

```text
immutable collection
≠ deep immutability объектов внутри неё
```

# Stack в современном Java-коде

Класс:

```java
java.util.Stack
```

является legacy API и наследуется от `Vector`.

Для нового кода стек обычно реализуют через `Deque`, чаще всего `ArrayDeque`.

```java
Deque<Integer> stack = new ArrayDeque<>();

stack.push(10);
stack.push(20);

stack.pop();  // 20
stack.peek(); // 10
```

`Stack` формально не помечен `@Deprecated`, но `Deque` является предпочтительным API для LIFO.

# Финальная памятка по Collections Framework

```text
ArrayList
→ динамический массив
→ get O(1)
→ add в конец O(1) амортизированно
→ вставка / удаление в середине O(n)
```

```text
LinkedList
→ двусвязный список
→ get O(n)
→ работа с уже найденным узлом O(1)
→ вставка по индексу O(n) из-за поиска
```

```text
HashSet
→ hash table
→ equals + hashCode
→ O(1) в среднем
```

```text
LinkedHashSet
→ HashSet + порядок вставки
→ O(1) в среднем
```

```text
TreeSet
→ красно-чёрное дерево
→ Comparable или Comparator
→ O(log n)
→ compare(...) == 0 означает дубликат для Set
```

```text
ArrayDeque
→ FIFO и LIFO
→ современный вариант для Queue / Stack
```

```text
PriorityQueue
→ heap
→ offer / poll O(log n)
→ peek O(1)
```

```text
Comparable
→ естественный порядок
→ compareTo()

Comparator
→ внешняя стратегия
→ compare()
```

```text
Iterator
→ последовательный обход

ListIterator
→ List
→ вперёд и назад
→ add / set / индексы
```

```text
fail-fast
→ попытка быстро обнаружить неожиданное структурное изменение
→ ConcurrentModificationException
→ не является гарантией и не обеспечивает thread safety
```

```text
Collections.unmodifiableList(original)
→ read-only view
→ изменения original видны

List.copyOf(original)
→ immutable snapshot
→ дальнейшие изменения original не видны
```

```text
List.of / Set.of / Map.of
→ immutable
→ null запрещён

Set.of
→ дубликаты запрещены

Map.of
→ повторные ключи запрещены
```

# Дополнительные вопросы для самопроверки

1. Чем `Comparable` отличается от `Comparator`?
2. Где находится логика естественного порядка?
3. Можно ли иметь несколько `Comparator` для одного класса?
4. Что означает результат `compare(...) == 0` для `TreeSet`?
5. Чем `Iterator` отличается от `ListIterator`?
6. Почему `ConcurrentModificationException` можно получить в одном потоке?
7. Что означает `fail-fast`?
8. Почему `iterator.remove()` допустим во время обхода?
9. Чем immutable collection отличается от unmodifiable view?
10. Чем `List.copyOf()` отличается от `Collections.unmodifiableList()`?
11. Обязана ли `List.copyOf()` создавать новый объект?
12. Можно ли передать `null` в `List.of()`?
13. Что произойдёт при дубликате в `Set.of()`?
14. Какие ограничения есть у `Map.of()`?
15. Делает ли immutable collection неизменяемыми её элементы?
16. Как устроена `PriorityQueue`?
17. Как сделать max-heap?
18. Почему `PriorityQueue` не гарантирует полностью отсортированный порядок обхода?
19. Почему для стека предпочтительнее `ArrayDeque`, а не `Stack`?
20. Чем `Collections.sort(list)` отличается от `list.sort(comparator)`?

---

## См. также

- [`02-map.md`](02-map.md) — `Map` не входит в иерархию `Collection`, но
  разбирается вместе с ней
- [`03-equals-hashcode.md`](03-equals-hashcode.md) — контракт, от которого зависит
  корректность `HashSet` и ключей `Map`
- [`08-functional-interfaces-lambda.md`](08-functional-interfaces-lambda.md) —
  `Comparator` как функциональный интерфейс и его фабрики
- [`../concurrency/04-concurrent-collections.md`](../concurrency/04-concurrent-collections.md) —
  потокобезопасные аналоги и отличие fail-fast итератора от weakly consistent
