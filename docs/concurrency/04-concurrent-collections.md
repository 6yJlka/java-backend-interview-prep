# Concurrent Collections в Java

Обычные коллекции вроде `HashMap` и `ArrayList` не гарантируют корректную работу
при одновременном изменении из нескольких потоков: возможны потеря изменений,
некорректные результаты и повреждение внутренней структуры. Для многопоточных
сценариев существует набор специализированных структур из `java.util.concurrent`.

```text
ConcurrentHashMap
CopyOnWriteArrayList
BlockingQueue
    ArrayBlockingQueue
    LinkedBlockingQueue
    SynchronousQueue
ConcurrentLinkedQueue
```

Они рассчитаны на конкурентную работу и дают разные гарантии в зависимости от
сценария. Главная мысль темы, к которой всё сводится: потокобезопасность
контейнера не делает атомарной произвольную операцию над ним и не делает
потокобезопасным его содержимое.

---

## Collections.synchronizedMap

Простейший способ сделать обычную `Map` потокобезопасной:

```java
Map<String, Integer> map =
        Collections.synchronizedMap(new HashMap<>());
```

Внутри остаётся обычный `HashMap`, но каждый доступ оборачивается синхронизацией
по общему монитору:

```text
Thread A ─┐
Thread B ─┼──> общий lock ──> HashMap
Thread C ─┘
```

Отдельные операции `get()`, `put()` и `remove()` становятся потокобезопасными, но
потоки сильнее мешают друг другу, чем при использовании специализированных
структур.

Отдельно нужно помнить про обход: он требует внешней синхронизации.

```java
Map<String, Integer> map =
        Collections.synchronizedMap(new HashMap<>());

synchronized (map) {
    for (Map.Entry<String, Integer> entry : map.entrySet()) {
        System.out.println(entry);
    }
}
```

Для активно используемой общей карты обычно предпочтительнее
`ConcurrentHashMap`.

---

## ConcurrentHashMap

Потокобезопасная реализация `Map`, специально разработанная для конкурентного
доступа.

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
```

Она позволяет множеству потоков одновременно читать и даёт значительно большую
параллельность при изменениях, чем одна глобальная блокировка. Операции `get()`,
`put()` и `remove()` потокобезопасны сами по себе.

> Потокобезопасность отдельных операций не означает атомарность произвольной
> последовательности из нескольких операций.

### Compound operations

```java
if (!map.containsKey("user")) {
    map.put("user", 1);
}
```

`containsKey()` потокобезопасен, `put()` тоже. Но последовательность «проверить →
принять решение → изменить» одной атомарной операцией не является:

```text
Thread A                        Thread B

containsKey("user") → false
                                containsKey("user") → false

put("user", 1)
                                put("user", 1)
```

Оба потока увидели отсутствие ключа до того, как один из них выполнил `put()`.

### putIfAbsent

```java
map.putIfAbsent("user", 1);
```

Атомарно выполняет смысл «если ключа нет — добавить». Другой поток не вклинится
между проверкой и вставкой.

### computeIfAbsent

Когда значение нужно создать только при отсутствии ключа:

```java
map.computeIfAbsent("user", key -> loadUserData(key));
```

Здесь важный нюанс. Карта потокобезопасно управляет связями «ключ — значение», но
не делает потокобезопасными сами значения.

```java
ConcurrentHashMap<String, List<String>> map = new ConcurrentHashMap<>();

map.computeIfAbsent("java", key -> new ArrayList<>())
   .add("Spring");
```

Значение создастся корректно, но созданный `ArrayList` остаётся обычным списком.
Несколько потоков могут получить ссылку на один и тот же список и одновременно
вызывать `add()` — карта их внутреннее состояние не защищает.

```text
ConcurrentHashMap
    ↓
потокобезопасно управляет связями key → value

объект value
    ↓
имеет собственные правила потокобезопасности
```

### compute и merge

```java
ConcurrentHashMap<String, Integer> counts = new ConcurrentHashMap<>();

counts.put("java", 0);
```

Такой код небезопасен, несмотря на `ConcurrentHashMap`:

```java
counts.put("java", counts.get("java") + 1);
```

Здесь три действия: чтение, вычисление, запись.

```text
начальное значение java = 0

Thread A: get("java") → 0
Thread B: get("java") → 0

Thread A: 0 + 1 → 1
Thread B: 0 + 1 → 1

Thread A: put("java", 1)
Thread B: put("java", 1)
```

Ожидалось `2`, получилось `1` — одно обновление потерялось. Это `lost update`.

Атомарные варианты:

```java
counts.compute("java", (key, value) -> value + 1);
```

```java
counts.merge("java", 1, Integer::sum);
```

`merge()` особенно удобен для счётчиков: если ключа нет, записывается переданное
значение, если есть — применяется функция объединения.

```text
ключа нет      → java = 1
было java = 5  → java = 6
```

Вместо ручной ветвистой конструкции с `containsKey()` и двумя `put()` достаточно
одной строки:

```java
counts.merge(key, 1, Integer::sum);
```

### Итераторы

Итераторы `ConcurrentHashMap` являются weakly consistent. Пока один поток
обходит карту, другой может выполнить `put()`. Такой итератор:

- не обязан бросать `ConcurrentModificationException`;
- не блокирует конкурентный `put()`;
- может увидеть новую запись, а может не увидеть.

То есть обход не является строгим снимком состояния на определённый момент.

### ConcurrentHashMap и synchronizedMap

```text
Collections.synchronizedMap
→ обычная Map под синхронизирующей обёрткой
→ общий монитор, меньше параллелизма
→ при ручной итерации нужна внешняя синхронизация

ConcurrentHashMap
→ специализированная структура
→ конкурентные чтения, большая параллельность обновлений
→ weakly consistent iterator
```

Для простой ситуации `synchronizedMap` может быть достаточно. Для карты, с
которой активно работают разные потоки, выбирают `ConcurrentHashMap`.

---

## CopyOnWriteArrayList

Потокобезопасный список, оптимизированный для сценариев, где чтений намного
больше, чем изменений.

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
```

При каждом изменении создаётся новая копия внутреннего массива:

```text
старый массив:
["A", "B", "C"]

        ↓ add("Java")

новый массив:
["A", "B", "C", "Java"]

        ↓

ссылка внутри CopyOnWriteArrayList
переключается на новый массив
```

Копирования требуют `add()`, `remove()` и `set()`, поэтому запись относительно
дорогая. Особенно плохо подходит сочетание большого списка и частых изменений.

### Когда использовать

```text
очень много чтений
+
очень мало изменений
```

Классический пример — список обработчиков событий:

```java
CopyOnWriteArrayList<Listener> listeners = new CopyOnWriteArrayList<>();

for (Listener listener : listeners) {
    listener.onEvent(event);
}
```

Новые слушатели добавляются редко, а обход происходит постоянно, поэтому дорогая
запись проблемой не становится.

### Итератор

Итератор работает со снимком массива на момент своего создания.

```java
CopyOnWriteArrayList<String> list =
        new CopyOnWriteArrayList<>(List.of("A", "B"));

Iterator<String> iterator = list.iterator();

list.add("C");
```

```text
старый массив ["A", "B"]
↑ с ним продолжает работать iterator

новый массив ["A", "B", "C"]
↑ текущее состояние списка
```

Обход выведет только `A` и `B`: элемент `C` уже созданный итератор не увидит.

```text
ConcurrentHashMap iterator
→ weakly consistent
→ конкурентное изменение может увидеть, а может не увидеть

CopyOnWriteArrayList iterator
→ snapshot
→ изменения после создания iterator не увидит
```

---

## BlockingQueue

Интерфейс потокобезопасной очереди с блокирующими операциями. Основной сценарий —
producer-consumer.

```text
Producer
   ↓
создаёт задачи
   ↓
BlockingQueue
   ↓
Consumer
   ↓
обрабатывает задачи
```

```java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(100);

queue.put(task);          // producer
Task task = queue.take(); // consumer
```

Если очередь заполнена, `put()` ждёт. Если пуста — ждёт `take()`.

### Добавление элементов

Пусть очередь заполнена:

```java
BlockingQueue<String> queue = new ArrayBlockingQueue<>(2);
```

```java
queue.add("C");                  // IllegalStateException, поток не ждёт
boolean result = queue.offer("C"); // false, поток не ждёт
queue.put("C");                  // ждёт, пока появится место
```

Как работает ожидание:

```text
queue = [A, B]

Producer: put(C) → WAITING

Consumer: take() → забирает A

queue = [B]

Producer: разблокируется → добавляет C

queue = [B, C]
```

### Извлечение элементов

Пусть очередь пуста:

```java
queue.remove();              // NoSuchElementException
String value = queue.poll(); // null
String value = queue.take(); // ждёт появления элемента
```

Симметрия, которую стоит запомнить целиком:

```text
Добавление:            Извлечение:

add()   → exception    remove() → exception
offer() → false        poll()   → null
put()   → ожидание     take()   → ожидание
```

### Ограниченное ожидание

У обеих операций есть варианты с таймаутом:

```java
boolean result = queue.offer(task, 2, TimeUnit.SECONDS);

Task task = queue.poll(2, TimeUnit.SECONDS);
```

`offer()` вернёт `true`, если место появилось, и `false` по истечении времени.
`poll()` вернёт элемент либо `null`.

### Реакция на interrupt

Блокирующие операции очереди прерываемы. Если поток ждёт в `put()`, а другой
вызывает `thread.interrupt()`, ожидание прекращается выбросом
`InterruptedException`.

```java
try {
    queue.put(task);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

То же относится к `take()`. Это общая модель прерываемых блокирующих операций:

```text
sleep()
wait()
join()
BlockingQueue.put()
BlockingQueue.take()
```

После выброса `InterruptedException` флаг прерывания сбрасывается, поэтому его
восстанавливают явно.

### Backpressure

Главная причина использовать ограниченную очередь.

```text
producer создаёт 100 задач/сек
consumer обрабатывает 20 задач/сек
```

При практически неограниченной очереди backlog растёт на 80 задач в секунду:

```text
80 → 160 → 240 → 320 → ...
```

Это увеличивает потребление памяти, нагружает сборщик мусора и в пределе даёт
`OutOfMemoryError`.

С ограниченной очередью и `put()` получается саморегуляция:

```text
producer быстрее consumer
        ↓
очередь растёт до capacity = 100
        ↓
put() блокирует producer
        ↓
consumer забирает элемент
        ↓
producer продолжает работу
```

Система не позволяет источнику бесконечно генерировать работу быстрее, чем её
успевают обрабатывать.

---

## Реализации BlockingQueue

### ArrayBlockingQueue

Ограниченная очередь на основе массива. Ёмкость задаётся при создании и потом не
меняется.

```java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(100);
```

Главный сценарий — producer-consumer, где нужно ограничить объём накопленных
задач и получить backpressure.

> Наличие ограниченной очереди само по себе не означает автоматическую блокировку
> producer: поведение зависит от выбранного метода.

```text
add()   → exception
offer() → false
put()   → ждёт
```

### LinkedBlockingQueue

С заданной ёмкостью ведёт себя как ограниченная:

```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);
```

Без ёмкости предел составляет `Integer.MAX_VALUE`, поэтому такую очередь считают
практически неограниченной:

```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>();
```

Здесь `put()` почти никогда не заблокируется из-за заполнения — приложение
столкнётся с нехваткой памяти раньше.

```text
LinkedBlockingQueue<>(100) → bounded
LinkedBlockingQueue<>()    → практически unbounded
```

### SynchronousQueue

Ёмкость равна нулю: очередь вообще не хранит элементы, а является точкой
непосредственной передачи между потоками.

```java
BlockingQueue<String> queue = new SynchronousQueue<>();
```

Если producer вызывает `put()`, а consumer ещё не готов, producer ждёт. Когда
другой поток вызовет `take()`, произойдёт прямая передача:

```text
Producer              Consumer

put("task")  ───────→ take()
```

Элемент не лежит внутри очереди ни мгновения.

### SynchronousQueue и CachedThreadPool

`Executors.newCachedThreadPool()` устроен примерно так:

```text
corePoolSize = 0
maximumPoolSize = очень большой
queue = SynchronousQueue
keepAliveTime = 60 секунд
```

Когда приходит задача, пул пытается передать её свободному worker. Если готового
worker нет, задачу некуда положить — очередь не хранит элементы, — поэтому
создаётся новый поток.

```text
много входящих задач
+
долгие задачи
+
SynchronousQueue
+
очень большой maximumPoolSize
=
очень много worker-потоков
```

Отсюда расходы на память под стеки, переключение контекста, работу планировщика и
вымывание процессорного кеша.

Важно не путать `keepAliveTime` с таймаутом выполнения: он определяет, сколько
живёт простаивающий worker, и никак не ограничивает длительность задачи.

---

## ConcurrentLinkedQueue

Потокобезопасная неблокирующая очередь.

```java
Queue<Task> queue = new ConcurrentLinkedQueue<>();
```

При пустой очереди `poll()` сразу возвращает `null`, поток не ждёт. При `offer()`
нет ожидания свободного места, поскольку очередь практически неограниченная и
backpressure не предоставляет.

### Busy waiting

```java
while (true) {
    Task task = queue.poll();

    if (task != null) {
        process(task);
    }
}
```

Если очередь долго пуста, поток не блокируется и не засыпает, а крутит цикл на
полной скорости, бессмысленно нагружая процессор. Это busy waiting, он же busy
spin.

Для классического producer-consumer удобнее блокирующая очередь:

```java
while (!Thread.currentThread().isInterrupted()) {
    Task task = queue.take();
    process(task);
}
```

Если задач нет, consumer ждёт, а не опрашивает пустую очередь.

### Сравнение с BlockingQueue

```text
BlockingQueue
→ поддерживает ожидание: put(), take(), варианты с таймаутом
→ подходит для producer-consumer
→ может обеспечивать backpressure

ConcurrentLinkedQueue
→ неблокирующая
→ poll() сразу возвращает null при пустой очереди
→ поток сам решает, что делать дальше
→ backpressure отсутствует
```

---

## Как выбрать

| Структура | Когда брать | На что смотреть |
|---|---|---|
| `ConcurrentHashMap` | общая карта, много потоков читают и обновляют | составные операции только через `putIfAbsent`, `computeIfAbsent`, `compute`, `merge` |
| `CopyOnWriteArrayList` | много чтений, мало изменений | не подходит для частых `add` и `remove`, особенно на больших списках |
| `ArrayBlockingQueue` | producer-consumer с фиксированным пределом | даёт backpressure при использовании `put()` |
| `LinkedBlockingQueue` | то же, с ёмкостью или без | без ёмкости практически неограниченная, backpressure нет |
| `SynchronousQueue` | прямая передача между потоками без хранения | ёмкость `0`, используется в `CachedThreadPool` |
| `ConcurrentLinkedQueue` | нужна неблокирующая неограниченная очередь | нет ожидания и backpressure, легко получить busy waiting |

---

## Связь с ThreadPoolExecutor

Выбор очереди напрямую определяет поведение пула потоков.

```java
new ThreadPoolExecutor(
        2,
        4,
        30,
        TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(10)
);
```

Алгоритм приёма задачи:

```text
пришла задача
↓
workers < corePoolSize?
├─ да → создать core worker
└─ нет
     ↓
попробовать положить задачу в queue
     ↓
queue заполнена?
├─ нет → задача ждёт в очереди
└─ да
     ↓
workers < maximumPoolSize?
├─ да → создать дополнительный worker
└─ нет → rejection policy
```

Отсюда прямые следствия:

```text
ArrayBlockingQueue
→ задачи буферизуются, объём backlog ограничен

LinkedBlockingQueue без capacity
→ огромный backlog
→ pool может никогда не дойти до создания дополнительных workers

SynchronousQueue
→ задачи не буферизуются
→ нужен свободный worker или создаётся новый
```

---

## Типичные ошибки

### Считать несколько потокобезопасных операций одной атомарной

```java
if (!map.containsKey(key)) {
    map.put(key, value);
}
```

Между проверкой и вставкой вклинивается другой поток. Нужен
`map.putIfAbsent(key, value)`.

### Делать read-modify-write вручную

```java
map.put(key, map.get(key) + 1);
```

Классический lost update. Нужен `map.merge(key, 1, Integer::sum)`.

### Считать значение внутри ConcurrentHashMap потокобезопасным

Карта защищает связи «ключ — значение», а не внутреннее состояние объектов.
Обычный `ArrayList` в качестве значения остаётся небезопасным.

### Использовать CopyOnWriteArrayList при частых изменениях

Каждая запись копирует внутренний массив целиком.

### Использовать неограниченную очередь при постоянной перегрузке

Если producer стабильно быстрее consumer, backlog растёт до проблем с памятью.
Контроль даёт ограниченная очередь.

### Опрашивать пустую ConcurrentLinkedQueue в цикле

Превращается в busy waiting и бессмысленно нагружает процессор. Нужна
блокирующая очередь с `take()`.

### Считать, что ограниченная очередь всегда блокирует producer

Блокирует только `put()`. `add()` бросит исключение, `offer()` вернёт `false`.

### Путать keepAliveTime с таймаутом задачи

Он ограничивает жизнь простаивающего worker, а не длительность выполнения.

### Обходить synchronizedMap без внешней синхронизации

Отдельные операции защищены, итерация — нет.

---

## Краткая памятка

```text
ConcurrentHashMap
→ отдельные операции thread-safe
→ compound operations — только специальные методы:
  putIfAbsent / computeIfAbsent / compute / merge
→ iterator weakly consistent

CopyOnWriteArrayList
→ много чтений, мало изменений
→ изменение копирует массив целиком
→ iterator работает со snapshot
```

```text
BlockingQueue

Добавление:            Извлечение:
add()   → exception    remove() → exception
offer() → false        poll()   → null
put()   → wait         take()   → wait

offer(e, timeout, unit) → true или false
poll(timeout, unit)     → element или null

put() и take() прерываемы: InterruptedException
```

```text
ArrayBlockingQueue    → bounded, capacity фиксируется при создании
LinkedBlockingQueue   → bounded с capacity, иначе практически unbounded
SynchronousQueue      → capacity = 0, прямая передача, CachedThreadPool
ConcurrentLinkedQueue → non-blocking, unbounded, poll() → null, backpressure нет
```

```text
backpressure
bounded queue + put()
→ producer блокируется, пока consumer не освободит место
```

```text
ThreadPoolExecutor
core занят → очередь → очередь полна → до maximumPoolSize → rejection

ArrayBlockingQueue          → ограниченный backlog
LinkedBlockingQueue без cap → pool не растёт выше core
SynchronousQueue            → сразу новый worker
```

```text
главное правило
thread-safe контейнер
≠ атомарность бизнес-операции
≠ потокобезопасность содержимого
```

---

## Краткий ответ для собеседования

Обычные коллекции при конкурентном изменении не дают никаких гарантий, поэтому
для многопоточной работы используют структуры из `java.util.concurrent`.

Самый простой вариант — обёртка `Collections.synchronizedMap`, но она сводит весь
доступ к одному монитору и требует внешней синхронизации при обходе.
`ConcurrentHashMap` спроектирован под конкурентный доступ: чтения идут
параллельно, обновления блокируют лишь небольшую часть структуры.

Ключевая мысль в том, что потокобезопасность отдельных операций не даёт
атомарности их последовательности. Проверка через `containsKey()` с последующим
`put()` или чтение, инкремент и запись значения — это составные операции, в
которые вклинивается другой поток, и результат теряется. Для таких случаев есть
`putIfAbsent`, `computeIfAbsent`, `compute` и `merge`. Точно так же карта не
делает потокобезопасным объект, лежащий в ней значением.

Итераторы различаются: у `ConcurrentHashMap` они weakly consistent и могут
увидеть конкурентное изменение, а могут не увидеть; у `CopyOnWriteArrayList` —
снимок массива на момент создания, поэтому позднейшие изменения в текущем обходе
не появятся никогда. Сам `CopyOnWriteArrayList` копирует массив при каждой
записи, поэтому годится только там, где чтений несравнимо больше изменений.

Для передачи работы между потоками служит `BlockingQueue`. Её методы образуют три
пары: `add` и `remove` бросают исключение, `offer` и `poll` возвращают
специальное значение, `put` и `take` ждут. Ожидание прерываемо. Ограниченная
очередь вместе с `put()` даёт backpressure — производитель замедляется, когда
потребитель не успевает, и backlog перестаёт расти.

Реализации отличаются ёмкостью: `ArrayBlockingQueue` ограничена всегда,
`LinkedBlockingQueue` без параметра практически неограниченна, `SynchronousQueue`
не хранит элементы вовсе и потому заставляет `CachedThreadPool` создавать новый
поток на каждую задачу, для которой нет свободного worker.
`ConcurrentLinkedQueue` неблокирующая: она возвращает `null` вместо ожидания, и
наивный цикл опроса легко превращается в busy waiting.

---

## Вопросы на собеседовании

### 1. Почему ConcurrentHashMap не делает атомарной пару containsKey и put?

**Ответ:** это две отдельные операции, и между ними другой поток может изменить
карту. Нужна атомарная операция — `putIfAbsent()`.

### 2. Почему get() и put() небезопасны для счётчика?

**Ответ:** операция состоит из чтения, вычисления и записи. Несколько потоков
прочитают одинаковое старое значение, и одно из обновлений потеряется. Нужны
`compute()` или `merge()`.

### 3. Чем merge отличается от compute?

**Ответ:** `compute()` получает текущее значение, которое может быть `null`, и
вычисляет новое. `merge()` принимает значение по умолчанию для отсутствующего
ключа и функцию объединения, поэтому для счётчиков он короче и безопаснее.

### 4. Чем ConcurrentHashMap отличается от synchronizedMap?

**Ответ:** второй — синхронизирующая обёртка над обычной картой с общим
монитором. `ConcurrentHashMap` разработан для конкурентного доступа и допускает
значительно большую степень параллелизма.

### 5. Нужна ли внешняя синхронизация при обходе synchronizedMap?

**Ответ:** да. Потокобезопасны только отдельные операции, а итерация состоит из
множества вызовов и должна выполняться под блокировкой самой карты.

### 6. Как ведёт себя итератор ConcurrentHashMap?

**Ответ:** он weakly consistent: не бросает `ConcurrentModificationException`, не
блокирует изменения и может увидеть конкурентное изменение, а может не увидеть.

### 7. Делает ли ConcurrentHashMap потокобезопасными свои значения?

**Ответ:** нет. Она защищает связи ключей со значениями. Обычный `ArrayList`,
положенный значением, остаётся небезопасным при конкурентных `add()`.

### 8. Почему CopyOnWriteArrayList подходит для большого числа чтений?

**Ответ:** изменение создаёт новую копию массива, а читатели продолжают работать
со старой неизменяемой версией без всякой синхронизации.

### 9. Почему он плох при частых записях?

**Ответ:** каждая изменяющая операция копирует внутренний массив целиком.

### 10. Увидит ли существующий итератор CopyOnWriteArrayList новый элемент?

**Ответ:** нет. Он работает со снимком массива на момент своего создания.

### 11. Чем offer отличается от put?

**Ответ:** для заполненной очереди `offer()` сразу возвращает `false`, а `put()`
ждёт освобождения места.

### 12. Чем poll отличается от take?

**Ответ:** для пустой очереди `poll()` сразу возвращает `null`, а `take()` ждёт
появления элемента.

### 13. Что произойдёт с потоком, ждущим в take, при вызове interrupt?

**Ответ:** ожидание прервётся выбросом `InterruptedException`, а флаг прерывания
будет сброшен, поэтому его обычно восстанавливают вручную.

### 14. Что такое backpressure?

**Ответ:** механизм, при котором более медленная часть системы ограничивает
скорость источника нагрузки. Заполненная ограниченная очередь блокирует `put()`,
и производитель замедляется.

### 15. Всегда ли ограниченная очередь блокирует producer?

**Ответ:** нет, только при использовании `put()`. `add()` бросит исключение,
`offer()` вернёт `false`.

### 16. Чем ArrayBlockingQueue отличается от LinkedBlockingQueue?

**Ответ:** первая всегда ограничена и основана на массиве. Вторая может быть
ограниченной, а без указания ёмкости имеет предел `Integer.MAX_VALUE` и считается
практически неограниченной.

### 17. Какова ёмкость SynchronousQueue?

**Ответ:** ноль. Она не хранит элементы, а передаёт их напрямую от производителя
потребителю.

### 18. Почему CachedThreadPool может создать очень много потоков?

**Ответ:** он использует `SynchronousQueue`, которая не хранит задачи. Если
свободного worker нет, пул создаёт новый, а верхний предел очень велик.

### 19. Что означает keepAliveTime в пуле?

**Ответ:** время жизни простаивающего worker. Длительность выполнения задачи он
не ограничивает.

### 20. Чем ConcurrentLinkedQueue отличается от BlockingQueue?

**Ответ:** она неблокирующая: `poll()` при пустой очереди сразу возвращает
`null`, ожидания и backpressure нет.

### 21. Что такое busy waiting?

**Ответ:** поток в цикле проверяет условие вместо того, чтобы заблокироваться и
ждать события. Постоянный `poll()` пустой очереди бессмысленно нагружает
процессор.

### 22. Как выбор очереди влияет на ThreadPoolExecutor?

**Ответ:** пул создаёт дополнительные потоки только после заполнения очереди.
Неограниченная очередь означает, что число потоков никогда не превысит
`corePoolSize`, а `SynchronousQueue` — что новый worker создаётся почти сразу.

---

## См. также

- [`03-locks-atomics-executors.md`](03-locks-atomics-executors.md) — как
  `workQueue` влияет на рост pool и rejection
- [`../java-core/02-map.md`](../java-core/02-map.md) — обычный `HashMap` и почему
  он не подходит для конкурентного доступа
- [`../java-core/01-collections-framework.md`](../java-core/01-collections-framework.md) —
  fail-fast итератор против weakly consistent и snapshot