# Concurrent Collections в Java

## 1. Зачем нужны concurrent-коллекции

Обычные коллекции Java, например `HashMap` и `ArrayList`, не гарантируют корректную работу при одновременном изменении из нескольких потоков.

Например:

```java
Map<String, Integer> map = new HashMap<>();
```

Если несколько потоков одновременно изменяют такую коллекцию:

```java
map.put("A", 1);
map.put("B", 2);
```

возникает конкурентный доступ к общей структуре данных. Это может привести к потере изменений, некорректным результатам и другим проблемам.

Для многопоточных сценариев в Java существуют специализированные структуры из `java.util.concurrent`:

- `ConcurrentHashMap`
- `CopyOnWriteArrayList`
- `BlockingQueue`
- `ArrayBlockingQueue`
- `LinkedBlockingQueue`
- `SynchronousQueue`
- `ConcurrentLinkedQueue`

Они рассчитаны на конкурентную работу потоков и предоставляют разные гарантии в зависимости от сценария использования.

---

# 2. Collections.synchronizedMap

Один из простых способов сделать обычную `Map` потокобезопасной:

```java
Map<String, Integer> map =
        Collections.synchronizedMap(new HashMap<>());
```

Внутри всё ещё используется обычный `HashMap`, но доступ к нему оборачивается в синхронизацию.

Отдельные операции:

```java
map.get(key);
map.put(key, value);
map.remove(key);
```

становятся потокобезопасными.

Упрощённо это можно представить как использование общего монитора:

```text
Thread A ─┐
Thread B ─┼──> общий lock ──> HashMap
Thread C ─┘
```

Из-за этого потоки сильнее мешают друг другу, чем при использовании специализированных concurrent-структур.

Особенно важно помнить про итерацию.

Для `synchronizedMap` при ручном обходе требуется внешняя синхронизация:

```java
Map<String, Integer> map =
        Collections.synchronizedMap(new HashMap<>());

synchronized (map) {
    for (Map.Entry<String, Integer> entry : map.entrySet()) {
        System.out.println(entry);
    }
}
```

Для активно используемой общей `Map` обычно предпочтительнее `ConcurrentHashMap`.

---

# 3. ConcurrentHashMap

`ConcurrentHashMap` — потокобезопасная реализация `Map`, специально разработанная для конкурентного доступа.

```java
ConcurrentHashMap<String, Integer> map =
        new ConcurrentHashMap<>();
```

Она позволяет множеству потоков одновременно читать данные и обеспечивает значительно большую параллельность при изменениях, чем одна глобальная блокировка всей коллекции.

Операции:

```java
map.get(key);
map.put(key, value);
map.remove(key);
```

потокобезопасны сами по себе.

Но важное правило:

> Потокобезопасность отдельных операций не означает атомарность произвольной последовательности из нескольких операций.

---

# 4. Compound operations

Рассмотрим:

```java
if (!map.containsKey("user")) {
    map.put("user", 1);
}
```

`containsKey()` потокобезопасен.

`put()` тоже потокобезопасен.

Но вся последовательность:

```text
проверить
→ принять решение
→ изменить
```

не является одной атомарной операцией.

Возможна ситуация:

```text
Thread A                        Thread B

containsKey("user") → false
                                containsKey("user") → false

put("user", 1)
                                put("user", 1)
```

Оба потока успели увидеть отсутствие ключа до того, как один из них выполнил `put()`.

Это классический пример compound operation.

Для подобных случаев `ConcurrentHashMap` предоставляет специальные атомарные методы.

---

# 5. putIfAbsent

Вместо:

```java
if (!map.containsKey("user")) {
    map.put("user", 1);
}
```

можно использовать:

```java
map.putIfAbsent("user", 1);
```

Эта операция атомарно выполняет смысл:

```text
если ключ отсутствует
→ добавить значение
```

Другой поток не сможет вклиниться между проверкой наличия ключа и добавлением значения.

---

# 6. computeIfAbsent

Если значение необходимо создать только при отсутствии ключа:

```java
map.computeIfAbsent(
        "user",
        key -> loadUserData(key)
);
```

Например:

```java
ConcurrentHashMap<String, List<String>> map =
        new ConcurrentHashMap<>();

map.computeIfAbsent(
        "java",
        key -> new ArrayList<>()
);
```

`computeIfAbsent()` удобно использовать для ленивого создания значений.

Но здесь появляется важный нюанс.

`ConcurrentHashMap` делает потокобезопасной саму `Map`, но не делает автоматически потокобезопасными объекты, которые в ней хранятся.

Например:

```java
ConcurrentHashMap<String, List<String>> map =
        new ConcurrentHashMap<>();

map.computeIfAbsent(
        "java",
        key -> new ArrayList<>()
).add("Spring");
```

`computeIfAbsent()` корректно создаст значение для ключа.

Но созданный:

```java
new ArrayList<>()
```

по-прежнему не является thread-safe.

Несколько потоков могут получить ссылку на один и тот же `ArrayList` и одновременно выполнять:

```java
list.add(...);
```

`ConcurrentHashMap` не защищает внутреннее состояние этого списка.

Важно различать два уровня:

```text
ConcurrentHashMap
    ↓
потокобезопасно управляет связями key → value

объект value
    ↓
имеет собственные правила потокобезопасности
```

Thread-safe контейнер не делает автоматически thread-safe всё своё содержимое.

---

# 7. compute и merge

Рассмотрим счётчик:

```java
ConcurrentHashMap<String, Integer> counts =
        new ConcurrentHashMap<>();

counts.put("java", 0);
```

Такой код небезопасен:

```java
counts.put(
        "java",
        counts.get("java") + 1
);
```

Несмотря на использование `ConcurrentHashMap`, здесь есть несколько действий:

```text
get
→ вычисление нового значения
→ put
```

Два потока могут выполнить:

```text
начальное значение java = 0

Thread A: get("java") → 0
Thread B: get("java") → 0

Thread A: 0 + 1 → 1
Thread B: 0 + 1 → 1

Thread A: put("java", 1)
Thread B: put("java", 1)
```

Ожидалось:

```text
java = 2
```

Получилось:

```text
java = 1
```

Одно обновление потерялось.

Это называется `lost update`.

Для атомарного изменения можно использовать `compute()`:

```java
counts.compute(
        "java",
        (key, value) -> value + 1
);
```

Для счётчиков часто особенно удобно использовать `merge()`:

```java
counts.merge(
        "java",
        1,
        Integer::sum
);
```

Если ключа нет:

```java
counts.merge("java", 1, Integer::sum);
```

появится:

```text
java = 1
```

Если уже было:

```text
java = 5
```

операция:

```java
counts.merge("java", 1, Integer::sum);
```

даст:

```text
java = 6
```

Таким образом, вместо ручного:

```java
if (!counts.containsKey(key)) {
    counts.put(key, 1);
} else {
    counts.put(key, counts.get(key) + 1);
}
```

лучше использовать:

```java
counts.merge(key, 1, Integer::sum);
```

---

# 8. Итераторы ConcurrentHashMap

Итераторы `ConcurrentHashMap` являются `weakly consistent`.

Например, один поток выполняет:

```java
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry);
}
```

а другой поток одновременно:

```java
map.put("new", 100);
```

Итератор:

- не обязан бросать `ConcurrentModificationException`
- не блокирует конкурентный `put()`
- может увидеть новую запись
- может не увидеть новую запись

То есть текущий обход не является строгим snapshot состояния коллекции на определённый момент времени.

Можно запомнить:

```text
ConcurrentHashMap iterator
→ weakly consistent
→ изменения во время обхода может увидеть, а может не увидеть
```

---

# 9. ConcurrentHashMap и synchronizedMap

Упрощённое сравнение:

```text
Collections.synchronizedMap
→ обычная Map + synchronized wrapper
→ общий монитор
→ меньше параллелизма
→ при ручной итерации нужна внешняя синхронизация

ConcurrentHashMap
→ специализированная concurrent-структура
→ рассчитана на многопоточную работу
→ конкурентные чтения
→ большая параллельность обновлений
→ weakly consistent iterator
```

Для простой ситуации `synchronizedMap` может быть достаточной.

Для общей `Map`, с которой активно работают разные потоки, обычно выбирают `ConcurrentHashMap`.

---

# 10. CopyOnWriteArrayList

`CopyOnWriteArrayList` — потокобезопасный список, оптимизированный для сценариев, где чтений намного больше, чем изменений.

```java
CopyOnWriteArrayList<String> list =
        new CopyOnWriteArrayList<>();
```

Название означает:

```text
Copy On Write
→ копирование при записи
```

При изменении списка создаётся новая копия внутреннего массива.

Например, изначально:

```text
["A", "B", "C"]
```

Выполняется:

```java
list.add("Java");
```

Упрощённо происходит следующее:

```text
старый массив:
["A", "B", "C"]

        ↓ add("Java")

создаётся новый массив:
["A", "B", "C", "Java"]

        ↓

ссылка внутри CopyOnWriteArrayList
переключается на новый массив
```

Изменяющие операции:

```java
add()
remove()
set()
```

требуют копирования массива.

Поэтому запись в `CopyOnWriteArrayList` относительно дорогая.

Особенно плохо такой список подходит для сценария:

```text
очень большой список
+
частые add/remove
```

При каждом изменении приходится копировать значительную часть данных.

---

# 11. Когда использовать CopyOnWriteArrayList

Основной сценарий:

```text
очень много чтений
+
очень мало изменений
```

Например, список обработчиков событий:

```java
CopyOnWriteArrayList<Listener> listeners =
        new CopyOnWriteArrayList<>();
```

Новые listener'ы добавляются редко, но список может очень часто обходиться:

```java
for (Listener listener : listeners) {
    listener.onEvent(event);
}
```

В таком случае дорогая операция добавления не является большой проблемой, зато чтения очень удобны для конкурентной работы.

---

# 12. Итератор CopyOnWriteArrayList

Итератор `CopyOnWriteArrayList` работает со snapshot массива.

Например:

```java
CopyOnWriteArrayList<String> list =
        new CopyOnWriteArrayList<>(
                List.of("A", "B")
        );

Iterator<String> iterator = list.iterator();

list.add("C");
```

На момент создания `iterator` внутренний массив был:

```text
["A", "B"]
```

После:

```java
list.add("C");
```

создаётся новый массив:

```text
старый:
["A", "B"]
↑
iterator продолжает работать с ним

новый:
["A", "B", "C"]
↑
текущий список
```

Поэтому:

```java
while (iterator.hasNext()) {
    System.out.println(iterator.next());
}
```

выведет:

```text
A
B
```

Элемент `"C"` уже созданный итератор не увидит.

Это отличается от `ConcurrentHashMap`.

```text
ConcurrentHashMap iterator
→ weakly consistent
→ конкурентное изменение может увидеть, а может не увидеть

CopyOnWriteArrayList iterator
→ snapshot
→ изменения после создания iterator не увидит
```

---

# 13. BlockingQueue

`BlockingQueue` — интерфейс потокобезопасной очереди, поддерживающей блокирующие операции.

Она особенно удобна в producer-consumer моделях.

Например:

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

Пример:

```java
BlockingQueue<Task> queue =
        new ArrayBlockingQueue<>(100);
```

Producer может добавлять задачи:

```java
queue.put(task);
```

Consumer может получать:

```java
Task task = queue.take();
```

Если очередь заполнена, `put()` может ждать.

Если очередь пуста, `take()` может ждать.

---

# 14. Добавление элементов в BlockingQueue

Допустим:

```java
BlockingQueue<String> queue =
        new ArrayBlockingQueue<>(2);
```

В очереди уже:

```text
["A", "B"]
```

То есть она заполнена.

Существуют разные варианты добавления.

## add()

```java
queue.add("C");
```

Если места нет, будет выброшен:

```text
IllegalStateException
```

Поток не ждёт.

---

## offer()

```java
boolean result = queue.offer("C");
```

Если места нет:

```text
result = false
```

Исключение не выбрасывается.

Поток тоже не ждёт.

---

## put()

```java
queue.put("C");
```

Если очередь заполнена, текущий поток будет ждать, пока не появится место.

Например:

```text
queue = [A, B]

Producer:
put(C)
↓
WAITING

Consumer:
take()
↓
забирает A

queue = [B]

Producer:
разблокируется
↓
добавляет C

queue = [B, C]
```

Можно запомнить:

```text
add()   → нет места → exception
offer() → нет места → false
put()   → нет места → ожидание
```

---

# 15. offer с таймаутом

Есть промежуточный вариант:

```java
boolean result =
        queue.offer(
                task,
                2,
                TimeUnit.SECONDS
        );
```

Поток подождёт максимум две секунды.

Если место появится:

```text
true
```

Если за это время очередь не освободится:

```text
false
```

---

# 16. Получение элементов из BlockingQueue

Теперь очередь пуста:

```java
BlockingQueue<String> queue =
        new ArrayBlockingQueue<>(2);
```

Есть три основных варианта.

## remove()

```java
queue.remove();
```

Если элементов нет:

```text
NoSuchElementException
```

---

## poll()

```java
String value = queue.poll();
```

Если очередь пуста:

```text
value = null
```

---

## take()

```java
String value = queue.take();
```

Если очередь пуста, поток будет ждать появления элемента.

Можно запомнить симметрию:

```text
Добавление:

add()   → exception
offer() → false
put()   → ожидание

Извлечение:

remove() → exception
poll()   → null
take()   → ожидание
```

---

# 17. poll с таймаутом

Можно ждать элемент ограниченное время:

```java
Task task =
        queue.poll(
                2,
                TimeUnit.SECONDS
        );
```

Если элемент появится за это время, метод его вернёт.

Если нет:

```text
null
```

---

# 18. BlockingQueue и interrupt

Блокирующие операции `BlockingQueue` реагируют на interrupt.

Например, очередь заполнена:

```java
queue.put(task);
```

Поток блокируется в ожидании свободного места.

Другой поток выполняет:

```java
thread.interrupt();
```

Тогда `put()` прекращает ожидание и бросает:

```text
InterruptedException
```

Пример:

```java
try {
    queue.put(task);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

То же относится к:

```java
queue.take();
```

Это соответствует общей модели interruptible blocking operations:

```text
sleep()
wait()
join()
BlockingQueue.put()
BlockingQueue.take()
```

После выбрасывания `InterruptedException` interrupt status очищается, поэтому часто его восстанавливают:

```java
Thread.currentThread().interrupt();
```

---

# 19. Backpressure

Одна из главных причин использовать ограниченную `BlockingQueue` — backpressure.

Представим:

```text
producer создаёт 100 задач/сек
consumer обрабатывает 20 задач/сек
```

Если очередь практически неограниченная, каждую секунду появляется backlog примерно:

```text
100 - 20 = 80 задач
```

Через некоторое время:

```text
80
160
240
320
...
```

Количество накопленных задач будет расти.

Это приводит к увеличению потребления памяти, дополнительной нагрузке на GC и потенциально к `OutOfMemoryError`.

Если использовать:

```java
BlockingQueue<Task> queue =
        new ArrayBlockingQueue<>(100);
```

и producer добавляет через:

```java
queue.put(task);
```

получается:

```text
producer быстрее consumer
        ↓
очередь растёт
        ↓
достигает capacity = 100
        ↓
put() блокирует producer
        ↓
consumer забирает элемент
        ↓
освобождается место
        ↓
producer продолжает работу
```

Это и есть один из вариантов backpressure.

Система не позволяет producer бесконечно генерировать работу быстрее, чем downstream способен её обрабатывать.

---

# 20. ArrayBlockingQueue

`ArrayBlockingQueue` — ограниченная блокирующая очередь на основе массива.

Capacity задаётся при создании:

```java
BlockingQueue<Task> queue =
        new ArrayBlockingQueue<>(100);
```

После создания размер изменить нельзя.

Главный сценарий:

```text
producer-consumer
+
нужно ограничить количество накопленных задач
+
нужен backpressure
```

Например:

```java
queue.put(task);
```

при заполненной очереди заставит producer ждать.

Важно:

> Наличие ограниченной очереди само по себе не означает автоматическую блокировку producer.

Поведение зависит от метода.

Для заполненного:

```java
new ArrayBlockingQueue<>(100)
```

получаем:

```text
add()   → exception
offer() → false
put()   → ждёт
```

---

# 21. LinkedBlockingQueue

`LinkedBlockingQueue` — ещё одна реализация `BlockingQueue`.

Можно задать capacity:

```java
BlockingQueue<Task> queue =
        new LinkedBlockingQueue<>(100);
```

Тогда очередь является ограниченной.

Можно создать без capacity:

```java
BlockingQueue<Task> queue =
        new LinkedBlockingQueue<>();
```

В таком случае фактический предел очень большой, порядка `Integer.MAX_VALUE`.

Поэтому такую очередь обычно считают практически неограниченной.

В обычной ситуации `put()` на:

```java
new LinkedBlockingQueue<>()
```

почти никогда не блокируется из-за достижения capacity.

Скорее приложение столкнётся с нехваткой памяти раньше, чем очередь реально достигнет максимального размера.

Поэтому:

```text
LinkedBlockingQueue<>(100)
→ bounded

LinkedBlockingQueue<>()
→ практически unbounded
```

---

# 22. SynchronousQueue

`SynchronousQueue` сильно отличается от обычных очередей.

```java
BlockingQueue<String> queue =
        new SynchronousQueue<>();
```

Её capacity:

```text
0
```

Она вообще не хранит элементы.

`SynchronousQueue` является точкой непосредственной передачи данных между потоками.

Упрощённо:

```text
Producer
   ↓
передача элемента
   ↓
Consumer
```

Если producer вызывает:

```java
queue.put("task");
```

а consumer ещё не готов принять элемент, producer будет ждать.

Когда другой поток вызовет:

```java
queue.take();
```

произойдёт непосредственная передача:

```text
Producer              Consumer

put("task")  ───────→ take()
```

Элемент не лежит какое-то время внутри очереди.

---

# 23. SynchronousQueue и CachedThreadPool

`SynchronousQueue` используется внутри `Executors.newCachedThreadPool()`.

Упрощённо его параметры выглядят примерно так:

```text
corePoolSize = 0
maximumPoolSize = очень большой
queue = SynchronousQueue
keepAliveTime = 60 секунд
```

Когда приходит задача:

```text
задача
↓
SynchronousQueue
↓
есть свободный worker, готовый принять её?
```

Если да:

```text
задача передаётся существующему worker
```

Если нет:

```text
создаётся новый worker
```

Поскольку `SynchronousQueue` не умеет хранить задачи, pool не может просто сложить новую работу в очередь.

Если одновременно приходит много долгих задач:

```text
task 1   → thread 1 занят
task 2   → thread 2 занят
task 3   → thread 3 занят
...
task 100 → thread 100 занят
```

существующие workers не успевают освобождаться, поэтому создаются новые.

Отсюда риск `CachedThreadPool`:

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

Это может привести к большому количеству потоков и дополнительным расходам на:

- память под stacks
- переключение контекста
- работу scheduler
- CPU cache

Важно не путать `keepAliveTime` с таймаутом выполнения задачи.

`keepAliveTime` определяет, сколько может прожить **простаивающий** worker.

Он не ограничивает время выполнения самой задачи.

---

# 24. ConcurrentLinkedQueue

`ConcurrentLinkedQueue` — потокобезопасная неблокирующая очередь.

```java
Queue<Task> queue =
        new ConcurrentLinkedQueue<>();
```

Она отличается от `BlockingQueue`.

Если очередь пуста:

```java
Task task = queue.poll();
```

будет возвращено:

```text
null
```

Поток не будет ждать появления элемента.

При:

```java
queue.offer(task);
```

также нет ожидания свободного места.

`ConcurrentLinkedQueue` практически неограниченная и не предоставляет backpressure.

---

# 25. Busy waiting

Рассмотрим consumer:

```java
while (true) {
    Task task = queue.poll();

    if (task != null) {
        process(task);
    }
}
```

Если `ConcurrentLinkedQueue` долго остаётся пустой:

```text
poll() → null
poll() → null
poll() → null
poll() → null
...
```

Поток не блокируется и не засыпает.

Он продолжает выполнять цикл на высокой скорости.

Это называется:

```text
busy waiting
```

или:

```text
busy spin
```

В результате поток может бессмысленно загружать CPU, хотя полезной работы нет.

Для классического producer-consumer сценария часто удобнее:

```java
while (!Thread.currentThread().isInterrupted()) {
    Task task = queue.take();
    process(task);
}
```

с `BlockingQueue`.

Если задач нет, consumer будет ждать, а не постоянно проверять пустую очередь.

---

# 26. BlockingQueue и ConcurrentLinkedQueue

Основное различие:

```text
BlockingQueue
→ поддерживает ожидание
→ put()
→ take()
→ timed operations
→ подходит для producer-consumer
→ может обеспечивать backpressure

ConcurrentLinkedQueue
→ non-blocking
→ poll() сразу возвращает null при пустой очереди
→ поток сам решает, что делать дальше
→ backpressure отсутствует
```

`ConcurrentLinkedQueue` полезна, когда поток не должен блокироваться на очереди и приложение самостоятельно управляет дальнейшим поведением.

---

# 27. Как выбрать concurrent-коллекцию

## ConcurrentHashMap

Использовать, когда:

```text
нужна общая Map
+
много потоков одновременно читают и обновляют данные
```

Пример:

```java
ConcurrentHashMap<String, User> cache;
```

Для составных операций использовать:

```text
putIfAbsent()
computeIfAbsent()
compute()
merge()
```

а не ручные последовательности `get()` + `put()`.

---

## CopyOnWriteArrayList

Использовать, когда:

```text
чтений очень много
+
изменений мало
```

Пример:

```java
CopyOnWriteArrayList<Listener> listeners;
```

Не подходит для частых `add/remove`, особенно при большом количестве элементов.

---

## ArrayBlockingQueue

Использовать, когда:

```text
producer-consumer
+
нужен фиксированный максимальный размер
+
нужен backpressure
```

Например:

```java
new ArrayBlockingQueue<>(500);
```

---

## LinkedBlockingQueue

Использовать как blocking queue.

При заданной capacity:

```java
new LinkedBlockingQueue<>(500);
```

может использоваться как bounded queue.

Без capacity:

```java
new LinkedBlockingQueue<>();
```

она практически неограниченная.

---

## SynchronousQueue

Использовать, когда нужна непосредственная передача элемента между потоками без промежуточного хранения.

```text
capacity = 0
```

Известный пример применения:

```text
CachedThreadPool
```

---

## ConcurrentLinkedQueue

Использовать, когда нужна:

```text
thread-safe
+
non-blocking
+
неограниченная очередь
```

Но она сама не предоставляет механизм ожидания и backpressure.

---

# 28. Сравнение итераторов

Важно различать поведение разных concurrent-коллекций.

## ConcurrentHashMap

```text
weakly consistent iterator
```

Изменения во время обхода:

```text
может увидеть
или
может не увидеть
```

При обычных конкурентных изменениях не требуется поведение fail-fast обычного `HashMap`.

## CopyOnWriteArrayList

```text
snapshot iterator
```

Итератор работает с массивом, существовавшим на момент его создания.

Все изменения после создания iterator текущий обход не увидит.

---

# 29. Основные методы BlockingQueue

Краткая шпаргалка.

## Добавление

```text
add(element)
→ при заполнении exception

offer(element)
→ при заполнении false

put(element)
→ при заполнении ждёт

offer(element, timeout, unit)
→ ждёт ограниченное время
→ true или false
```

## Извлечение

```text
remove()
→ при пустой очереди exception

poll()
→ при пустой очереди null

take()
→ при пустой очереди ждёт

poll(timeout, unit)
→ ждёт ограниченное время
→ element или null
```

---

# 30. Типичные ошибки

## Ошибка 1. Считать несколько thread-safe операций одной атомарной операцией

Плохо:

```java
if (!map.containsKey(key)) {
    map.put(key, value);
}
```

Лучше:

```java
map.putIfAbsent(key, value);
```

---

## Ошибка 2. Делать read-modify-write вручную

Плохо:

```java
map.put(key, map.get(key) + 1);
```

Лучше:

```java
map.merge(key, 1, Integer::sum);
```

---

## Ошибка 3. Считать value внутри ConcurrentHashMap автоматически thread-safe

```java
ConcurrentHashMap<String, List<String>> map =
        new ConcurrentHashMap<>();
```

Если `List` является `ArrayList`, она всё ещё не является thread-safe.

---

## Ошибка 4. Использовать CopyOnWriteArrayList при частых изменениях

Каждая запись требует копирования внутреннего массива.

При большом списке и частых `add/remove` это дорого.

---

## Ошибка 5. Использовать неограниченную очередь при постоянной перегрузке

Если producer быстрее consumer:

```text
producer → очередь → consumer
```

и очередь практически неограниченная, backlog может расти до проблем с памятью.

Для контроля нагрузки можно использовать bounded queue.

---

## Ошибка 6. Делать бесконечный poll() пустой ConcurrentLinkedQueue

```java
while (true) {
    Task task = queue.poll();
}
```

может превратиться в busy waiting и бессмысленно загружать CPU.

---

## Ошибка 7. Считать, что bounded queue всегда блокирует producer

Например:

```java
new ArrayBlockingQueue<>(100);
```

Поведение зависит от метода:

```text
add()   → exception
offer() → false
put()   → ожидание
```

---

# 31. Связь с ThreadPoolExecutor

Concurrent queues напрямую связаны с устройством `ThreadPoolExecutor`.

Например:

```java
new ThreadPoolExecutor(
        2,
        4,
        30,
        TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(10)
);
```

Алгоритм примерно такой:

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

Поэтому выбор очереди сильно влияет на поведение thread pool.

Например:

```text
ArrayBlockingQueue
→ задачи могут буферизоваться
→ количество backlog ограничено

LinkedBlockingQueue без capacity
→ огромный backlog
→ pool может долго не доходить до создания дополнительных workers

SynchronousQueue
→ задачи вообще не буферизуются
→ нужен свободный worker или создаётся новый
```

---

# 32. Типичные вопросы на собеседовании

## Почему ConcurrentHashMap не делает этот код атомарным?

```java
if (!map.containsKey(key)) {
    map.put(key, value);
}
```

Потому что `containsKey()` и `put()` являются двумя отдельными операциями.

Другой поток может изменить `Map` между ними.

Нужно использовать атомарную операцию вроде:

```java
putIfAbsent()
```

---

## Почему get() + put() небезопасны для счётчика?

```java
map.put(key, map.get(key) + 1);
```

Потому что операция состоит из чтения, вычисления и записи.

Несколько потоков могут прочитать одинаковое старое значение и потерять одно из обновлений.

Для этого можно использовать:

```java
compute()
```

или:

```java
merge()
```

---

## Чем ConcurrentHashMap отличается от synchronizedMap?

`synchronizedMap` является синхронизирующей обёрткой над обычной `Map` и сильнее опирается на общий монитор.

`ConcurrentHashMap` изначально разработан для конкурентного доступа и позволяет более высокую степень параллелизма.

---

## Как ведёт себя iterator ConcurrentHashMap?

Он weakly consistent.

Он может увидеть конкурентные изменения, а может не увидеть.

---

## Почему CopyOnWriteArrayList подходит для большого количества чтений?

Потому что изменение создаёт новую копию внутреннего массива, а существующие читатели могут продолжать работать со старой неизменяемой версией.

---

## Почему CopyOnWriteArrayList плох при частых записях?

Потому что при каждой изменяющей операции необходимо копировать внутренний массив.

---

## Увидит ли существующий iterator CopyOnWriteArrayList новый элемент?

Нет.

Он работает со snapshot массива, существовавшим в момент создания iterator.

---

## Чем offer() отличается от put()?

Для заполненной `BlockingQueue`:

```text
offer()
→ сразу false

put()
→ ждёт свободного места
```

---

## Чем poll() отличается от take()?

Для пустой `BlockingQueue`:

```text
poll()
→ сразу null

take()
→ ждёт появления элемента
```

---

## Что такое backpressure?

Это механизм, при котором более медленная часть системы ограничивает скорость источника нагрузки.

Например:

```text
быстрый producer
↓
bounded BlockingQueue заполнена
↓
put() блокируется
↓
producer замедляется
```

---

## Какова capacity SynchronousQueue?

```text
0
```

Она не хранит элементы, а непосредственно передаёт их между producer и consumer.

---

## Почему CachedThreadPool может создать очень много потоков?

Потому что он использует `SynchronousQueue`, которая не хранит задачи.

Если свободного worker нет, а приходит новая задача, pool может создать нового worker.

При большом количестве долгих задач число потоков может быстро вырасти.

---

## Чем ConcurrentLinkedQueue отличается от BlockingQueue?

`ConcurrentLinkedQueue` неблокирующая.

При пустой очереди:

```java
poll();
```

возвращает `null`.

`BlockingQueue` предоставляет операции вроде:

```java
take();
```

которые могут заставить поток ждать появления элемента.

---

## Что такое busy waiting?

Это ситуация, когда поток постоянно проверяет условие вместо того, чтобы заблокироваться и ждать события.

Например:

```java
while (true) {
    Task task = queue.poll();

    if (task != null) {
        process(task);
    }
}
```

при постоянно пустой `ConcurrentLinkedQueue` может бессмысленно загружать CPU.

---

# 33. Итоговая шпаргалка

```text
ConcurrentHashMap
→ concurrent Map
→ отдельные операции thread-safe
→ compound operations требуют специальных методов
→ putIfAbsent / compute / computeIfAbsent / merge
→ iterator weakly consistent

CopyOnWriteArrayList
→ много чтений, мало изменений
→ изменение копирует массив
→ дорогие add/remove
→ iterator работает со snapshot

BlockingQueue
→ producer-consumer
→ может блокировать producer и consumer
→ поддерживает backpressure

ArrayBlockingQueue
→ bounded
→ capacity фиксируется при создании

LinkedBlockingQueue
→ может быть bounded
→ без capacity практически unbounded

SynchronousQueue
→ capacity = 0
→ элементы не хранятся
→ непосредственная передача producer → consumer
→ используется CachedThreadPool

ConcurrentLinkedQueue
→ thread-safe
→ non-blocking
→ практически unbounded
→ poll() возвращает null
→ нет встроенного backpressure
```

## Методы BlockingQueue

```text
Добавление:

add()   → exception
offer() → false
put()   → wait


Получение:

remove() → exception
poll()   → null
take()   → wait
```

## Главное правило

Потокобезопасная коллекция решает проблему конкурентного доступа к самой структуре данных, но не делает автоматически атомарной любую бизнес-операцию и не делает автоматически потокобезопасными объекты, которые хранятся внутри неё.