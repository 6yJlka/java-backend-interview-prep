# Locks, Atomics и Executors в Java — Part 2

## Lock и ReentrantLock

`synchronized` и `Lock` решают одну базовую задачу: обеспечивают mutual
exclusion, то есть не позволяют нескольким потокам одновременно выполнять
критическую секцию, защищённую одним и тем же механизмом синхронизации.

```java
synchronized (monitor) {
    updateSharedState();
}
```

`synchronized` работает с intrinsic monitor объекта. Захват и освобождение
монитора встроены в конструкцию языка: при нормальном выходе из блока и при
выходе из-за исключения JVM освобождает монитор автоматически.

Интерфейс `Lock` из `java.util.concurrent.locks` представляет явный lock.
Наиболее часто используется его реализация `ReentrantLock`:

```java
Lock lock = new ReentrantLock();

lock.lock();
try {
    // critical section
} finally {
    lock.unlock();
}
```

`ReentrantLock` требует явного `unlock()`. Поэтому освобождение помещают в
`finally`: этот блок выполняется и при нормальном завершении критической секции,
и при большинстве выходов из неё из-за исключения или `return`. Если забыть
`unlock()`, остальные потоки могут навсегда остаться в ожидании lock.

```text
synchronized  → monitor освобождается автоматически при выходе из блока
ReentrantLock → код обязан вызвать unlock()
```

Из этого не следует, что `ReentrantLock` автоматически «безопаснее при
исключениях». Напротив, безопасность зависит от правильного шаблона `try-finally`.
Оба механизма обеспечивают mutual exclusion и создают необходимые гарантии
видимости памяти при корректном захвате и освобождении. `ReentrantLock` выбирают,
когда нужны дополнительные возможности: неблокирующая попытка захвата, ожидание
с таймаутом, прерываемое ожидание, fairness или несколько `Condition`.

Вызов `lock()` должен находиться до `try`. Если он завершился успешно, поток
владеет lock и обязан освободить его. Если метод захвата сам завершился
исключением, выполнять `unlock()` для незахваченного lock нельзя.

### lock()

```java
lock.lock();
```

Если lock свободен, текущий поток захватывает его и продолжает работу. Если lock
занят другим потоком, текущий поток ждёт. Занятость lock сама по себе не приводит
к немедленному исключению.

Обычный `lock()` не позволяет выйти из ожидания только потому, что ожидающий
поток interrupt'нули. Interrupt status при этом может быть установлен, но захват
продолжает ожидаться. Для прерываемого ожидания существует
`lockInterruptibly()`.

### tryLock()

```java
if (lock.tryLock()) {
    try {
        updateSharedState();
    } finally {
        lock.unlock();
    }
} else {
    doAlternativeWork();
}
```

`tryLock()` немедленно пытается захватить lock:

- возвращает `true`, если захват успешен;
- возвращает `false`, если lock сейчас недоступен.

Он не ждёт освобождения lock бесконечно. `unlock()` вызывают только после
успешного захвата.

### tryLock(timeout, TimeUnit)

```java
boolean acquired = lock.tryLock(500, TimeUnit.MILLISECONDS);

if (acquired) {
    try {
        updateSharedState();
    } finally {
        lock.unlock();
    }
}
```

Перегрузка с таймаутом ждёт освобождения lock не дольше указанного времени.
Она возвращает `true`, если успела захватить lock, и `false`, если время истекло.
Ожидание является прерываемым, поэтому метод также может выбросить
`InterruptedException`.

### lockInterruptibly()

```java
try {
    lock.lockInterruptibly();
    try {
        updateSharedState();
    } finally {
        lock.unlock();
    }
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

`lockInterruptibly()` ждёт lock, но позволяет прервать поток во время ожидания.
В этом случае метод выбрасывает `InterruptedException`, не захватив lock.
Это полезно, когда длительное ожидание должно отменяться, например при остановке
сервиса или отмене задачи.

При выбрасывании `InterruptedException` interrupt status обычно очищается. Если
метод не пробрасывает исключение выше, но вызывающий код должен узнать о
прерывании, status восстанавливают:

```java
Thread.currentThread().interrupt();
```

| Метод | Ждёт занятый lock | Таймаут | Реагирует на interrupt ожидания | Результат |
|---|---:|---:|---:|---|
| `lock()` | да | нет | не выходом через `InterruptedException` | после возврата lock захвачен |
| `tryLock()` | нет | нет | не требуется ожидание | `true` или `false` сразу |
| `tryLock(timeout, unit)` | да, ограниченно | да | да | `true`, `false` или `InterruptedException` |
| `lockInterruptibly()` | да | нет | да | захват или `InterruptedException` |

## Reentrant lock

Reentrant означает повторно входимый. Поток, уже владеющий `ReentrantLock`, может
успешно захватить тот же lock ещё раз. Он не заблокируется на самом себе.

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    System.out.println(lock.getHoldCount()); // 1

    lock.lock();
    try {
        System.out.println(lock.getHoldCount()); // 2
    } finally {
        lock.unlock();
    }

    System.out.println(lock.getHoldCount()); // 1
} finally {
    lock.unlock();
}
```

Lock хранит hold count для владеющего потока. Каждый успешный `lock()` увеличивает
его, каждый `unlock()` уменьшает. Lock становится доступен другим потокам только
после уменьшения hold count до нуля.

```text
lock()   → hold count 1
lock()   → hold count 2
unlock() → hold count 1, lock ещё занят
unlock() → hold count 0, lock свободен
```

Количество `unlock()` должно соответствовать количеству успешных захватов.
Лишний `unlock()` потоком, который не владеет lock, приводит к
`IllegalMonitorStateException`, а недостающий оставляет lock захваченным.

Intrinsic monitor в Java тоже reentrant. `synchronized`-метод может вызвать
другой `synchronized`-метод того же объекта без самоблокировки.

## Fair и unfair ReentrantLock

```java
ReentrantLock unfairLock = new ReentrantLock();
ReentrantLock fairLock = new ReentrantLock(true);
```

Unfair lock используется по умолчанию. Освободившийся lock может получить поток,
который только что начал захват, даже если другие потоки уже ждут. Такое
опережение очереди иногда называют barging. Оно часто повышает throughput:
готовый поток захватывает lock без дополнительных переключений.

Fair lock старается предоставлять lock наиболее долго ожидающим потокам. Это
может уменьшить риск starvation, но дополнительные ограничения порядка часто
снижают throughput.

Fairness относится к политике получения конкретного lock, а не к управлению CPU
scheduler. Fair lock не гарантирует, что разблокированный поток немедленно
получит процессорное время, и не устанавливает абсолютную справедливость всей
программы. Кроме того, вызов `tryLock()` без таймаута может захватить доступный
fair lock, не соблюдая очередь ожидающих.

## Condition

`Condition` связывается с конкретным `Lock` и позволяет потокам ожидать изменения
логического условия:

```java
Lock lock = new ReentrantLock();
Condition condition = lock.newCondition();
```

Для первого знакомства полезна аналогия с monitor API:

```text
wait()        → await()
notify()      → signal()
notifyAll()   → signalAll()
```

Это не полностью одинаковые API. `wait/notify` принадлежат `Object` и работают с
intrinsic monitor, а `await/signal` принадлежат `Condition`, связанному с явным
`Lock`. У одного lock может быть несколько отдельных conditions.

### Поведение await()

Вызывающий поток должен владеть lock. Затем `await()`:

1. атомарно освобождает связанный lock;
2. переводит поток в ожидание сигнала, прерывания или другого допустимого события;
3. после пробуждения заставляет поток снова конкурировать за lock;
4. возвращает управление только после повторного успешного захвата lock.

```text
владение lock
→ await()
→ освобождение lock и ожидание
→ signal()
→ ожидание повторного захвата lock
→ lock снова захвачен
→ await() возвращает управление
```

`signal()` не передаёт lock немедленно. Сигналящий поток продолжает владеть им до
`unlock()`. Вызов `await()`, `signal()` или `signalAll()` без владения lock
приводит к `IllegalMonitorStateException`.

Условие всегда проверяют в `while`:

```java
lock.lock();
try {
    while (queue.isEmpty()) {
        notEmpty.await();
    }

    Task task = queue.remove();
} finally {
    lock.unlock();
}
```

Причин две:

- возможен spurious wakeup — возврат из ожидания без нужного логического события;
- после сигнала и до повторного захвата lock другой поток может снова изменить
  условие, например забрать последний элемент очереди.

`if` проверил бы условие только до ожидания и позволил бы продолжить с уже ложным
предположением. `while` проверяет его заново после каждого пробуждения.

### Несколько Condition для одного Lock

Bounded queue имеет по крайней мере два разных условия:

```java
class BoundedQueue<T> {
    private final Queue<T> queue = new ArrayDeque<>();
    private final int capacity;
    private final Lock lock = new ReentrantLock();
    private final Condition notEmpty = lock.newCondition();
    private final Condition notFull = lock.newCondition();

    BoundedQueue(int capacity) {
        this.capacity = capacity;
    }

    void put(T element) throws InterruptedException {
        lock.lockInterruptibly();
        try {
            while (queue.size() == capacity) {
                notFull.await();
            }
            queue.add(element);
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
    }

    T take() throws InterruptedException {
        lock.lockInterruptibly();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();
            }
            T element = queue.remove();
            notFull.signal();
            return element;
        } finally {
            lock.unlock();
        }
    }
}
```

Производители ожидают `notFull`, потребители — `notEmpty`. После добавления можно
сигнализировать потребителю, а после удаления — производителю. С одним monitor
wait set такое разделение невозможно: `notify()` не различает причины ожидания.

## Atomic classes

Пакет `java.util.concurrent.atomic` содержит классы для атомарной работы с
отдельным значением без явной критической секции в пользовательском коде:

- `AtomicInteger` — атомарное значение `int`;
- `AtomicLong` — атомарное значение `long`;
- `AtomicBoolean` — атомарное значение `boolean`;
- `AtomicReference<T>` — атомарная ссылка на объект типа `T`.

```java
AtomicInteger counter = new AtomicInteger(10);

int current = counter.get();       // прочитать 10
counter.set(20);                    // записать 20
int after = counter.incrementAndGet(); // записать 21, вернуть 21
int before = counter.getAndIncrement(); // вернуть 21, записать 22
int total = counter.addAndGet(5);       // записать 27, вернуть 27
boolean changed = counter.compareAndSet(27, 30); // true, значение 30
```

Ключевое различие операций инкремента — возвращаемое значение:

```text
исходное значение: 10

incrementAndGet() → сначала увеличить до 11, затем вернуть 11
getAndIncrement() → сначала вернуть 10, затем увеличить до 11
```

Обе операции выполняют инкремент атомарно. Отличается не итоговое состояние, а
значение, полученное вызывающим кодом.

```java
AtomicLong sequence = new AtomicLong();
long id = sequence.incrementAndGet();

AtomicBoolean initialized = new AtomicBoolean();
if (initialized.compareAndSet(false, true)) {
    initializeOnce();
}

AtomicReference<String> state = new AtomicReference<>("NEW");
state.compareAndSet("NEW", "RUNNING");
```

Atomic-класс не делает автоматически атомарным произвольный алгоритм вокруг
нескольких переменных. Если инвариант охватывает несколько значений, может
потребоваться lock, неизменяемый holder в `AtomicReference` либо другой механизм.

## Почему volatile count++ не потокобезопасен

```java
private volatile int count;

void increment() {
    count++;
}
```

`count++` является составной read-modify-write операцией:

```text
read count
→ increment локально прочитанное значение
→ write новое значение в count
```

Два потока могут прочитать одно исходное значение:

```text
count = 0

Thread 1             Thread 2
read 0               read 0
increment to 1       increment to 1
write 1              write 1

итог: 1
ожидалось: 2
```

Один инкремент потерян — это lost update. `volatile` даёт гарантии visibility и
ordering для чтений и записей поля, но не объединяет три шага `count++` в одну
атомарную операцию.

```java
private final AtomicInteger count = new AtomicInteger();

void increment() {
    count.incrementAndGet();
}
```

`incrementAndGet()` выполняет обновление атомарно, поэтому два успешных вызова
дают увеличение на два.

## CAS

CAS, или Compare-And-Set, — атомарная условная операция обновления:

```java
boolean result = value.compareAndSet(expected, update);
```

Её семантика:

1. прочитать текущее значение;
2. атомарно сравнить его с `expected`;
3. если значения совпадают, записать `update` и вернуть `true`;
4. если не совпадают, ничего не менять и вернуть `false`.

Сравнение и условная запись наблюдаются как единое атомарное действие. CAS не
означает просто «проверить значение и увеличить»: новое значение может быть
любым, а вычисление `update` часто выполняет пользовательский код.

### CAS loop

Атомарный инкремент можно представить циклом:

```java
int current;
int next;

do {
    current = value.get();
    next = current + 1;
} while (!value.compareAndSet(current, next));
```

Если другой поток изменил значение между `get()` и `compareAndSet()`, CAS
возвращает `false`. После неудачи нужно заново прочитать актуальное значение и
пересчитать `next`. Повтор со старым `expected` и старым `update` может никогда не
стать корректным либо записать результат, рассчитанный из устаревшего состояния.

```text
T1 читает 10 и вычисляет 11
T2 успешно меняет 10 → 11
T1: CAS(10, 11) → false
T1 снова читает 11, вычисляет 12 и повторяет CAS
```

### Lock-based и CAS-based подходы

При lock-based подходе один поток получает эксклюзивный доступ, а остальные
ожидают освобождения lock:

```text
lock → один владелец → критическая секция → unlock
```

При CAS-based подходе несколько потоков могут одновременно вычислять обновление
и пытаться его применить. Один побеждает и меняет значение, остальные обнаруживают
конфликт и повторяют попытку:

```text
read → calculate → CAS
                  ├→ success
                  └→ failure → read again → recalculate → CAS
```

CAS тоже является механизмом синхронизации: атомарные операции имеют определённые
гарантии видимости и порядка. Отсутствие явного lock не означает отсутствие
синхронизации. CAS хорошо подходит для коротких обновлений отдельного состояния,
но при высокой конкуренции повторные попытки расходуют CPU, а сложные инварианты
часто проще и надёжнее выразить через lock.

## ABA problem

Обычный CAS проверяет текущее значение, но не историю его изменений:

```text
T1 прочитал A

T2: A → B → A

T1 снова видит A
CAS с expected A может пройти
```

Хотя текущее значение снова равно `A`, состояние успело измениться. T1 может
ошибочно решить, что ничего не происходило. Особенно это важно для lock-free
структур данных, где промежуточные изменения ссылки могут означать удаление,
повторную вставку узла или изменение связей между узлами.

Один из способов обнаружить такую историю — хранить версию вместе со значением.
`AtomicStampedReference<T>` атомарно сравнивает и ссылку, и stamp:

```text
A, stamp=1
→ B, stamp=2
→ A, stamp=3
```

CAS, ожидающий `A` со `stamp=1`, не пройдёт для `A` со `stamp=3`.

```java
AtomicStampedReference<String> reference =
        new AtomicStampedReference<>("A", 1);

int[] stampHolder = new int[1];
String current = reference.get(stampHolder);
int currentStamp = stampHolder[0];

boolean changed = reference.compareAndSet(
        current,
        "B",
        currentStamp,
        currentStamp + 1
);
```

ABA обычно не является основной проблемой обычного монотонного счётчика
`AtomicInteger`: для инкремента важно актуальное числовое значение, а возврат к
старому значению обычно не является частью алгоритма. Но ABA нужно анализировать,
если смысл операции зависит от того, менялось ли состояние между чтением и CAS.

## ExecutorService и thread pool

Постоянное создание потоков через `new Thread(...).start()` связывает каждую
задачу с новым системным потоком. Создание потоков требует памяти для stack и
других структур, времени на запуск и участия scheduler. При большом потоке задач
их число легко становится неконтролируемым.

Thread pool содержит набор worker threads и принимает отдельные задачи:

```java
ExecutorService executor = Executors.newFixedThreadPool(4);
```

```text
task          → описание работы
worker thread → поток, который берёт и выполняет задачи
```

Один worker последовательно выполняет много задач, поэтому потоки
переиспользуются. Executor также централизует очередь, ограничение параллелизма,
остановку и обработку перегрузки.

```java
executor.execute(() -> System.out.println("fire and forget"));
Future<Integer> future = executor.submit(() -> 42);
```

Завершив работу с executor, его нужно корректно остановить. Иначе non-daemon
worker threads могут продолжать поддерживать жизнь JVM.

## execute и submit

`execute(Runnable)` принимает задачу и не возвращает объект результата:

```java
executor.execute(() -> processEvent());
```

`submit(...)` возвращает `Future`, через который можно ожидать завершение,
получить результат, узнать состояние или запросить отмену:

```java
Future<Integer> future = executor.submit(() -> {
    return 42;
});
```

`Runnable` и `Callable<T>` имеют разные контракты:

```java
Runnable runnable = () -> doWork();

Callable<Integer> callable = () -> {
    return calculateValue();
};
```

- `Runnable.run()` не возвращает значение результата задачи через `return` и не
  объявляет checked exceptions;
- `Callable<T>.call()` возвращает `T` и может бросать checked exceptions.

`submit(Runnable)` тоже допустим. Его `Future<?>` сообщает о завершении, но
успешный `get()` обычно возвращает `null`, если отдельно не передан результат.

Есть важное различие обработки неперехваченных исключений. Исключение из задачи,
переданной через `submit`, сохраняется в `Future` и проявляется при `get()` как
`ExecutionException`. У `execute` нет `Future`; исключение покидает `run()`
worker'а и обрабатывается механизмом uncaught exception конкретного потока.

## Future

`Future<T>` представляет результат, который может появиться позже.

### get()

```java
T result = future.get();
```

Если задача ещё не завершена, `get()` блокирует вызывающий поток. После успешного
завершения он возвращает результат. Это не делает саму задачу синхронной:
она выполняется worker thread, а caller в точке `get()` ждёт её результат.

```java
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(3000);
    return 42;
});

System.out.println("A");
System.out.println(future.get());
System.out.println("B");
```

Порядок:

```text
A
ожидание примерно до завершения задачи
42
B
```

`sleep()` выполняет worker thread. На `future.get()` блокируется поток, который
вызвал `get()`, например `main`.

### get(timeout, unit)

```java
Integer result = future.get(2, TimeUnit.SECONDS);
```

Метод ждёт не дольше таймаута. Если результат не появился, он выбрасывает
`TimeoutException`. Таймаут ожидания не отменяет задачу автоматически: worker
может продолжить выполнение. Для запроса отмены нужно отдельно вызвать
`future.cancel(...)`.

### Проверка состояния

```java
boolean done = future.isDone();
boolean cancelled = future.isCancelled();
```

`isDone()` возвращает `true`, если Future завершён любым способом: нормальным
результатом, исключением или отменой. Он не означает обязательно успешный
результат. `isCancelled()` возвращает `true`, если Future был отменён до
нормального завершения.

```java
boolean cancellationAccepted = future.cancel(true);
```

`cancel` запрашивает отмену и возвращает, удалось ли перевести Future в
cancelled-состояние.

## Exceptions в Future

Ожидание результата связано с четырьмя основными исключениями.

### ExecutionException

Если `Callable` завершился исключением, `get()` не бросает исходное исключение
напрямую. Он бросает `ExecutionException`, а исходная причина доступна через
`getCause()`:

```java
Future<Integer> future = executor.submit(() -> {
    throw new IllegalStateException("boom");
});

try {
    future.get();
} catch (ExecutionException e) {
    Throwable cause = e.getCause();
    System.out.println(cause.getClass());   // IllegalStateException
    System.out.println(cause.getMessage()); // boom
}
```

Обёртка нужна потому, что `Future.get()` имеет единый контракт и заранее не знает,
какое исключение может выбросить произвольная задача.

### InterruptedException

`InterruptedException` означает, что был прерван поток, ожидающий в `get()`, а не
обязательно worker, выполняющий задачу. Само по себе прерывание caller не отменяет
Future. Если сигнал нельзя пробросить выше, interrupt status обычно
восстанавливают.

### TimeoutException

```java
future.get(2, TimeUnit.SECONDS);
```

`TimeoutException` означает только, что caller ждал две секунды и не получил
результат. Задача может продолжать работу. При необходимости политика вызывающего
кода отдельно решает, вызвать ли `cancel(true)`.

### CancellationException

После успешной отмены `get()` не возвращает результат задачи, а бросает
unchecked `CancellationException`. Это верно даже если код worker'а после запроса
отмены успел вычислить и вернуть некоторое значение: контракт Future уже
зафиксировал отменённое состояние.

## Future.cancel()

```java
future.cancel(false);
future.cancel(true);
```

`cancel(false)` не разрешает interrupt уже выполняющего задачу worker. Отмена
может быть принята и для уже запущенной задачи: тогда Future станет cancelled, но
её код сможет продолжить выполнение. `cancel(true)` при выполняющейся задаче
пытается interrupt'нуть worker.

`cancel(true)` не является принудительным убийством потока. Interruption —
кооперативный механизм. Если задача игнорирует interrupt status и не вызывает
прерываемые методы, она может продолжать выполнять код, хотя Future уже cancelled.

```java
Future<?> future = executor.submit(() -> {
    while (!Thread.currentThread().isInterrupted()) {
        doOneUnitOfWork();
    }
});

future.cancel(true);
```

После установки interrupt status цикл может завершиться. Если внутри цикла есть
`sleep`, `wait`, `join` или другая interruptible blocking operation, она может
выбросить `InterruptedException` и очистить status. Задача должна корректно
обработать исключение — завершиться, пробросить его или восстановить status в
зависимости от контракта.

Независимо от того, насколько быстро worker отреагировал, после успешного
`cancel(...)` Future остаётся cancelled, а `get()` бросает
`CancellationException` вместо возврата итогового значения.

## shutdown и shutdownNow

### shutdown()

```java
executor.shutdown();
```

После `shutdown()` executor:

- перестаёт принимать новые задачи;
- продолжает выполнять уже принятые и находящиеся в очереди задачи;
- завершает worker threads после обработки принятой работы.

Попытка передать новую задачу после начала shutdown приводит к
`RejectedExecutionException`.

`shutdown()` не ждёт завершения задач и обычно возвращает сразу. Для ожидания
termination используют `awaitTermination`:

```java
executor.shutdown();

if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
    executor.shutdownNow();
}
```

### shutdownNow()

```java
List<Runnable> notStarted = executor.shutdownNow();
```

`shutdownNow()`:

- перестаёт принимать новые задачи;
- пытается interrupt'нуть выполняющиеся задачи;
- удаляет из очереди и возвращает задачи, которые ещё не начали выполняться.

Это best-effort попытка остановки, а не гарантированное мгновенное завершение
worker threads. Если выполняющийся код игнорирует interruption, worker может
продолжать работу. Возвращённый список также не является результатами задач — это
объекты задач, не запущенные к моменту остановки.

## Типы pool через Executors

Фабричные методы `Executors` удобно создают распространённые конфигурации. Они не
«запрещены» и не всегда плохи, но важно понимать скрытые параметры очереди и
числа потоков.

### FixedThreadPool

```java
ExecutorService executor = Executors.newFixedThreadPool(n);
```

- поддерживает фиксированное число workers;
- лишние задачи ждут в очереди;
- использует практически неограниченную `LinkedBlockingQueue`;
- `maximumPoolSize` фактически не помогает при перегрузке, потому что очередь
  продолжает принимать задачи.

Если producers долго отправляют задачи быстрее, чем workers обрабатывают их,
очередь может сильно вырасти и потребить много памяти.

### SingleThreadExecutor

```java
ExecutorService executor = Executors.newSingleThreadExecutor();
```

Один worker выполняет задачи последовательно. Это удобно, когда нужен порядок и
не должна выполняться более чем одна задача одновременно. Если worker аварийно
завершится, executor при необходимости создаст замену. Очередь здесь тоже может
неограниченно расти при устойчивой перегрузке.

### CachedThreadPool

```java
ExecutorService executor = Executors.newCachedThreadPool();
```

Cached pool переиспользует свободные workers, а при отсутствии свободного worker
может создавать новый. Внутри используется `SynchronousQueue`: у неё практически
нет обычного буфера для накопления задач — передача требует непосредственной
встречи producer и consumer.

Если готового worker нет, pool старается добавить поток. Поэтому число потоков
может очень сильно вырасти. Риски:

- memory consumption для thread stacks и связанных объектов;
- большое число context switches;
- нагрузка на scheduler;
- неконтролируемая конкуренция за downstream-ресурсы.

В production иногда предпочитают явно настроенный `ThreadPoolExecutor`, чтобы
сделать видимыми и ограничить число потоков, capacity очереди, thread naming и
политику rejection. Выбор зависит от нагрузки, а не от универсального запрета на
`Executors.*`.

## ThreadPoolExecutor

Базовая форма конструктора:

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
        corePoolSize,
        maximumPoolSize,
        keepAliveTime,
        TimeUnit.SECONDS,
        workQueue
);
```

Полная форма дополнительно принимает `ThreadFactory` и
`RejectedExecutionHandler`:

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
        2,
        4,
        60,
        TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(10),
        threadFactory,
        new ThreadPoolExecutor.AbortPolicy()
);
```

### Параметры

`corePoolSize` — целевое базовое число workers. По умолчанию core threads обычно
создаются по мере поступления задач, а не обязательно все в конструкторе. Метод
`prestartAllCoreThreads()` позволяет запустить их заранее.

`maximumPoolSize` — верхняя граница числа workers, до которой pool может вырасти,
когда очередь больше не принимает новые задачи.

`keepAliveTime` — сколько простаивающий worker сверх core size может ждать новую
работу до удаления.

`workQueue` — очередь принятых, но ещё не начавших выполняться задач. Её тип и
capacity принципиально влияют на рост pool и перегрузку.

`ThreadFactory` создаёт workers. Через неё задают понятные имена потоков,
daemon-флаг, priority и `UncaughtExceptionHandler`. Фабрика не должна возвращать
`null`, если ожидается нормальное создание worker.

`RejectedExecutionHandler` определяет, что делать с задачей, которую executor не
может принять из-за saturation или shutdown.

### Алгоритм при поступлении задачи

Для обычного работающего `ThreadPoolExecutor` алгоритм принципиально важен:

1. Если workers меньше `corePoolSize`, создать worker для новой задачи.
2. Иначе попытаться положить задачу в `workQueue`.
3. Если очередь не принимает задачу и workers меньше `maximumPoolSize`, создать
   дополнительный worker для новой задачи.
4. Если очередь не принимает задачу и workers уже достигли
   `maximumPoolSize`, применить rejection policy.

```text
new task
  ↓
workers < core? ── да → create worker
  │ нет
  ↓
queue accepts? ─── да → enqueue
  │ нет
  ↓
workers < max? ─── да → create extra worker
  │ нет
  ↓
reject
```

`maximumPoolSize` начинает играть роль только после того, как очередь больше не
принимает новые задачи. Это одна из самых частых ошибок при настройке pool.

### Пример: core=2, max=4, queue=10

Пусть одновременно отправлены 15 долгих задач, ни одна не успевает завершиться
во время заполнения:

```text
задачи 1–2   → создаются 2 core workers, задачи выполняются
задачи 3–12  → 10 задач помещаются в queue
задачи 13–14 → queue заполнена, создаются 2 extra workers
задача 15    → workers == max и queue заполнена, rejection
```

Итог:

- 4 задачи выполняются;
- 10 задач ждут в queue;
- 1 задача rejected.

### Пример: core=3, max=5, queue=4

Для 10 долгих задач:

```text
3 → core workers
4 → queue
2 → extra workers после заполнения queue
1 → rejected
```

Итог: 5 выполняются, 4 ждут, 1 rejected.

Эти расчёты предполагают, что задачи достаточно долгие и во время отправки ни
один worker не успел освободить место. В реальной системе результат зависит от
времени выполнения и конкуренции между submitter и workers.

## keepAliveTime

Дополнительные workers сверх `corePoolSize` могут быть уничтожены после периода
простоя:

```text
core = 2
max = 4
keepAlive = 60 секунд
```

Под нагрузкой pool вырос до четырёх workers. После завершения нагрузки два
дополнительных idle workers могут быть удалены примерно после заданного времени,
и pool вернётся к двум.

По умолчанию core threads не завершаются только из-за `keepAliveTime`. Их тоже
можно сделать чувствительными к простою через
`allowCoreThreadTimeOut(true)`. Тогда keep-alive должен быть больше нуля, и даже
число workers ниже core может уменьшаться при отсутствии работы.

## Rejection policies

Rejection происходит, когда работающий pool исчерпал workers и capacity очереди,
а также при отправке задачи после shutdown. Стандартные политики реализованы как
вложенные классы `ThreadPoolExecutor`.

### AbortPolicy

```java
new ThreadPoolExecutor.AbortPolicy()
```

Политика по умолчанию. `execute` выбрасывает `RejectedExecutionException`, поэтому
caller явно узнаёт, что задача не принята.

### CallerRunsPolicy

```java
new ThreadPoolExecutor.CallerRunsPolicy()
```

Если executor не shutdown, задачу синхронно выполняет поток, который пытался
передать её в executor.

```java
executor.execute(longTask);
System.out.println("after");
```

Если pool переполнен, `longTask.run()` выполняется прямо в caller thread.
`execute` вернёт управление только после нормального завершения задачи, поэтому
`after` будет напечатано позже. Если `longTask` выбросит неперехваченное
`RuntimeException`, оно пойдёт прямо через caller, и выполнение до `after` может
не дойти.

Это создаёт простую форму backpressure: перегруженный consumer заставляет
producer самому тратить время на обработку, поэтому producer временно перестаёт
отправлять новые задачи. При shutdown `CallerRunsPolicy` задачу не выполняет, а
молча отбрасывает.

### DiscardPolicy

```java
new ThreadPoolExecutor.DiscardPolicy()
```

Задача молча отбрасывается. Такая семантика допустима только там, где потеря
работы осознана и наблюдаемость обеспечена отдельно.

### DiscardOldestPolicy

```java
new ThreadPoolExecutor.DiscardOldestPolicy()
```

Удаляется одна из старых ожидающих задач из головы queue, после чего executor
повторно пытается принять новую. Уже выполняющиеся задачи не вытесняются. Политика
может нарушить ожидания порядка и также приводит к потере работы.

| Policy | Поведение при rejection |
|---|---|
| `AbortPolicy` | бросить `RejectedExecutionException` |
| `CallerRunsPolicy` | выполнить задачу в caller thread, если executor не shutdown |
| `DiscardPolicy` | отбросить новую задачу |
| `DiscardOldestPolicy` | убрать старую ожидающую и повторить приём новой |

## CPU-bound и I/O-bound pools

### CPU-bound задачи

CPU-bound задачи большую часть времени выполняют вычисления:

- сложные математические вычисления;
- компрессия;
- обработка изображений;
- некоторые виды парсинга.

Доступное JVM число processors можно узнать так:

```java
int processors = Runtime.getRuntime().availableProcessors();
```

Для CPU-bound нагрузки размер pool обычно выбирают примерно около числа доступных
processors, затем проверяют измерениями. JVM физически может создать намного
больше потоков, чем CPU cores. Но 200 вычисляющих platform threads на машине с
восемью доступными processors обычно не выполняют вычисления быстрее разумного
малого pool. Они конкурируют за ограниченный CPU и добавляют:

- context switching;
- конкуренцию за CPU;
- scheduler overhead;
- ухудшение cache locality.

### I/O-bound задачи

I/O-bound задачи значительную часть времени ожидают внешние операции:

- HTTP;
- database;
- files;
- внешние сервисы.

Пока один worker ждёт I/O, другой может использовать CPU. Поэтому pool для такой
нагрузки может быть больше числа processors. Универсальной магической формулы нет:
production-конфигурацию выбирают по реальной доле ожидания и измеряют по:

- latency;
- throughput;
- CPU;
- памяти;
- downstream limits;
- connection pools;
- очередям и rejection-метрикам.

Размер thread pool не отменяет ограничений следующего ресурса:

```text
DB connection pool = 20
Thread pool = 200
```

Это не означает 200 одновременно выполняющихся SQL-запросов. Не более доступного
числа connections смогут обращаться к DB одновременно, а многие workers будут
ждать connection. Такое ожидание потребляет память, увеличивает latency и может
переносить перегрузку на весь сервис.

## Типичные ошибки

### Забывать unlock()

Успешный захват `ReentrantLock` требует соответствующего `unlock()`. Иначе lock
может навсегда остаться недоступным другим потокам.

### Вызывать unlock() не в finally

Исключение или ранний `return` пропустит обычную строку `unlock()`. Освобождение
помещают в `finally` после успешного захвата.

### Считать, что tryLock() ждёт бесконечно

`tryLock()` без аргументов возвращает `true` или `false` сразу. Ограниченно ждёт
перегрузка с timeout.

### Считать, что lock() сразу бросает exception при занятом lock

Занятый lock — нормальная причина ожидания `lock()`, а не исключение.

### Использовать if вокруг Condition.await()

После spurious wakeup или изменения условия до повторного захвата lock условие
может быть ложным. Его повторно проверяют в `while`.

### Считать volatile count++ атомарным

`volatile` даёт visibility и ordering, но `count++` остаётся read-modify-write и
допускает lost update.

### Понимать CAS как обычную проверку

Сравнение с expected и условная запись выполняются атомарно. Отдельные обычные
`if` и присваивание не эквивалентны CAS.

### Повторять CAS со старым expected

После неудачи нужно снова прочитать актуальное состояние и пересчитать update.
Иначе попытка использует устаревшие предположения.

### Забывать про ABA

Совпадение текущего значения с expected не доказывает, что оно не менялось по
пути `A → B → A`. Для чувствительных алгоритмов применяют версию, например
`AtomicStampedReference`.

### Считать Future.get() неблокирующим

Если задача не завершена, `get()` блокирует вызывающий поток.

### Считать TimeoutException автоматической отменой

Timeout ограничивает ожидание caller, но worker может продолжать задачу. Отмена —
отдельное решение и отдельный вызов.

### Считать shutdownNow() принудительным убийством потоков

Метод лишь пытается interrupt'нуть workers. Задачи должны кооперативно реагировать
на interruption.

### Считать maximumPoolSize числом сразу создаваемых потоков

Сначала pool растёт до core, затем заполняет queue и только после отказа queue
создаёт workers сверх core.

### Забывать, что queue заполняется раньше extra workers

При стандартном алгоритме дополнительный worker появляется лишь тогда, когда
queue больше не принимает задачу.

### Считать 200 CPU-bound threads быстрее восьми на 8-core машине

JVM может создать 200 потоков, но они конкурируют за восемь processors и обычно
увеличивают switching и scheduler overhead без роста вычислительной мощности.

### Забывать ограничения downstream

Большой executor не расширяет DB connection pool, лимиты внешнего API или
пропускную способность сети. Он может лишь увеличить число ожидающих задач.

## Вопросы на собеседовании

### 1. Чем synchronized отличается от ReentrantLock?

**Ответ:** `synchronized` работает с intrinsic monitor и автоматически
освобождает его при выходе. `ReentrantLock` — явный lock с ручным `unlock()` и
дополнительными возможностями: `tryLock`, timeout, interruptible acquisition,
fairness и несколькими `Condition`. Оба обеспечивают mutual exclusion.

### 2. Почему unlock() помещают в finally?

**Ответ:** чтобы освободить успешно захваченный lock при нормальном выходе,
`return` и исключении. Иначе можно навсегда заблокировать конкурентов.

### 3. Чем lock() отличается от tryLock()?

**Ответ:** `lock()` ждёт, пока lock станет доступен. `tryLock()` без аргументов
немедленно возвращает `true` или `false`.

### 4. Как ведёт себя tryLock(timeout, unit)?

**Ответ:** ждёт захват не дольше таймаута, возвращает `false` при его истечении и
может выбросить `InterruptedException` при прерывании ожидания.

### 5. Для чего нужен lockInterruptibly()?

**Ответ:** он позволяет прекратить ожидание занятого lock через interrupt и
`InterruptedException`.

### 6. Что означает reentrant?

**Ответ:** владеющий поток может повторно захватить тот же lock. Каждый успешный
захват увеличивает hold count и требует своего освобождения.

### 7. Является ли synchronized reentrant?

**Ответ:** да, поток может повторно войти в synchronized-код с тем же monitor.

### 8. Чем fair ReentrantLock отличается от unfair?

**Ответ:** fair lock старается обслуживать давно ожидающие потоки, уменьшая риск
starvation, но часто снижает throughput. Unfair используется по умолчанию.

### 9. Гарантирует ли fair lock немедленное CPU time?

**Ответ:** нет. Он влияет на порядок захвата lock, но не управляет CPU scheduler.

### 10. Что такое Condition?

**Ответ:** связанный с `Lock` объект ожидания логического условия. Он предоставляет
`await`, `signal` и `signalAll`; у одного lock может быть несколько conditions.

### 11. Что делает await()?

**Ответ:** требует владения lock, освобождает его, ждёт, затем повторно захватывает
lock и только после этого возвращает управление.

### 12. Почему await() окружают while, а не if?

**Ответ:** из-за spurious wakeup и возможности повторного изменения условия
другим потоком до reacquisition lock.

### 13. Зачем нужны несколько Condition у одного Lock?

**Ответ:** чтобы разделить группы ожидающих по логическим условиям, например
`notEmpty` и `notFull`, и сигнализировать нужную группу.

### 14. Для чего нужен AtomicInteger?

**Ответ:** для атомарных операций над отдельным `int`, например increment, add и
compare-and-set, без явного lock в пользовательском коде.

### 15. Чем incrementAndGet() отличается от getAndIncrement()?

**Ответ:** первый возвращает значение после увеличения, второй — значение до
увеличения. Сам инкремент атомарен в обоих случаях.

### 16. Почему volatile count++ не потокобезопасен?

**Ответ:** `count++` состоит из read, increment и write. `volatile` обеспечивает
visibility и ordering отдельных accesses, но не атомарность всей последовательности.

### 17. Что такое CAS?

**Ответ:** атомарная операция: если текущее значение равно expected, записать
update и вернуть `true`; иначе ничего не менять и вернуть `false`.

### 18. Почему после неудачного CAS нужно перечитать значение?

**Ответ:** другой поток изменил состояние. Новое значение нужно вычислять из
актуального состояния, а не повторять устаревшую попытку.

### 19. Чем CAS-based подход отличается от lock-based?

**Ответ:** lock даёт одному потоку эксклюзивную критическую секцию, остальные
ждут. При CAS несколько потоков конкурируют попытками; проигравшие перечитывают
состояние и повторяют обновление.

### 20. Является ли CAS синхронизацией?

**Ответ:** да. CAS — атомарный механизм синхронизации с гарантиями памяти, хотя
явного блокирующего lock нет.

### 21. Что такое ABA problem?

**Ответ:** значение прошло `A → B → A`, поэтому CAS, ожидающий `A`, не замечает
промежуточного изменения, хотя история состояния могла быть важна.

### 22. Как помогает AtomicStampedReference?

**Ответ:** сравнивает и меняет ссылку вместе с версией. `A` со stamp 1 отличается
от того же `A` со stamp 3.

### 23. Зачем нужен ExecutorService?

**Ответ:** он отделяет задачи от worker threads, переиспользует потоки, управляет
очередью, параллелизмом, остановкой и перегрузкой.

### 24. Чем execute отличается от submit?

**Ответ:** `execute(Runnable)` не возвращает результат задачи. `submit` возвращает
`Future`, через который получают результат, исключение, состояние и отмену.

### 25. Чем Runnable отличается от Callable?

**Ответ:** `Runnable.run()` не возвращает task result и не объявляет checked
exceptions. `Callable<T>.call()` возвращает `T` и может бросать checked exceptions.

### 26. Что представляет Future?

**Ответ:** результат асинхронной задачи, который может появиться позже, завершиться
исключением или быть отменён.

### 27. Блокирует ли Future.get()?

**Ответ:** да, вызывающий поток ждёт, если задача ещё не завершена.

### 28. Что произойдёт, если Callable бросит исключение?

**Ответ:** `get()` бросит `ExecutionException`, а исходное исключение будет в
`getCause()`.

### 29. Что означает TimeoutException из get(timeout)?

**Ответ:** результат не получен за время ожидания. Задача автоматически не
отменяется и может продолжать работу.

### 30. Что делает cancel(true)?

**Ответ:** переводит Future в cancelled-состояние, если отмена принята, и пытается
interrupt'нуть выполняющийся worker. Это не принудительное убийство потока.

### 31. Что вернёт get() после успешной отмены?

**Ответ:** ничего; он бросит `CancellationException`.

### 32. Чем shutdown() отличается от shutdownNow()?

**Ответ:** `shutdown()` выполняет уже принятые задачи. `shutdownNow()` пытается
interrupt'нуть выполняющиеся и возвращает ещё не начатые задачи, но мгновенную
остановку не гарантирует.

### 33. Что происходит с новой задачей после shutdown()?

**Ответ:** она rejected; стандартно caller получает `RejectedExecutionException`.

### 34. Как устроен newFixedThreadPool(n)?

**Ответ:** фиксированное число workers и практически неограниченная очередь.
При длительной перегрузке очередь может сильно вырасти.

### 35. Как устроен newCachedThreadPool()?

**Ответ:** он переиспользует idle workers, использует `SynchronousQueue` и при
отсутствии свободного worker может создавать новые, поэтому число потоков может
резко вырасти.

### 36. Как ThreadPoolExecutor принимает новую задачу?

**Ответ:** сначала создаёт workers до core, затем кладёт задачи в queue, после
заполнения queue растёт до max, а затем применяет rejection policy.

### 37. Что означает corePoolSize?

**Ответ:** базовое число workers, до которого pool предпочитает создавать потоки
до постановки задач в queue.

### 38. Когда начинает влиять maximumPoolSize?

**Ответ:** когда число workers уже не меньше core и queue больше не принимает
новую задачу.

### 39. Как workQueue влияет на pool?

**Ответ:** она хранит ожидающие задачи; её capacity определяет, когда начнётся
рост сверх core и когда наступит rejection. Неограниченная queue обычно делает
max практически недостижимым.

### 40. Что делает keepAliveTime?

**Ответ:** позволяет удалить простаивающие workers сверх core после заданного
времени. Core threads по умолчанию от него не завершаются.

### 41. Какие стандартные rejection policies существуют?

**Ответ:** `AbortPolicy`, `CallerRunsPolicy`, `DiscardPolicy` и
`DiscardOldestPolicy`.

### 42. Как работает CallerRunsPolicy?

**Ответ:** если executor перегружен и не shutdown, rejected task синхронно
выполняет caller thread. Это замедляет producer и создаёт backpressure.

### 43. Почему CPU-bound pool обычно близок к числу processors?

**Ответ:** задачи постоянно используют CPU, а лишние потоки добавляют switching,
scheduler overhead и ухудшают cache locality, не добавляя процессоров.

### 44. Почему I/O-bound pool может быть больше?

**Ответ:** workers часто ждут I/O, поэтому другие потоки могут использовать CPU.
Размер всё равно ограничивают по измерениям и downstream capacity.

### 45. Почему thread pool на 200 не обходит DB pool на 20?

**Ответ:** одновременно использовать DB смогут примерно столько задач, сколько
есть доступных connections. Остальные workers будут ждать и увеличивать latency и
потребление ресурсов.

## Задачи на понимание

### Сценарий 1: расчёт заполнения pool

```text
core = 2
max = 4
queue capacity = 5
10 долгих задач
```

**Ответ:** две задачи запускают core workers, пять попадают в queue, две запускают
extra workers, одна rejected. Итого 4 выполняются, 5 ждут, 1 rejected.

### Сценарий 2: исключение Callable

`Callable` бросает `IllegalStateException`. Что произойдёт при `get()`?

**Ответ:** `get()` бросит `ExecutionException`; исходная
`IllegalStateException` доступна через `e.getCause()`.

### Сценарий 3: timeout ожидания

`get(timeout)` получил `TimeoutException`. Остановилась ли задача?

**Ответ:** нет. Истёк только лимит ожидания caller. Worker может продолжить задачу;
для отмены нужен отдельный `cancel`.

### Сценарий 4: cancel(true) и interrupt

Future отменили через `cancel(true)`, задача проверяет `isInterrupted()`.

**Ответ:** executor попытается interrupt'нуть worker, задача может обнаружить
status и завершить работу. Но Future уже cancelled, поэтому `get()` бросит
`CancellationException`, а не вернёт значение.

### Сценарий 5: CallerRunsPolicy

Pool переполнен, используется `CallerRunsPolicy`, а `execute` вызывает `main`.
Кто выполняет задачу?

**Ответ:** `main`. Вызов `execute` вернётся только после нормального окончания
задачи.

### Сценарий 6: повторный захват

Один поток трижды вызвал `lock.lock()`, затем дважды `unlock()`. Доступен ли lock
другому потоку?

**Ответ:** нет. Hold count равен одному; нужен ещё один `unlock()`.

### Сценарий 7: сигнал Condition

Producer вызвал `notEmpty.signal()`, но ещё не вышел из защищённого блока. Может
ли consumer уже продолжить после `await()`?

**Ответ:** нет. Он должен повторно захватить lock, который пока удерживает
producer.

### Сценарий 8: lost update

Два потока одновременно выполнили `count++` для `volatile int count = 0`.
Обязан ли итог быть равен двум?

**Ответ:** нет. Оба могут прочитать ноль и записать единицу. `volatile` не делает
read-modify-write атомарным.

### Сценарий 9: ABA

T1 ожидает ссылку `A`, stamp 4. T2 меняет её на `B`, stamp 5, затем на `A`, stamp
6. Пройдёт ли stamped CAS T1 с expected `A`, stamp 4?

**Ответ:** нет. Ссылка совпала, но stamp изменился.

### Сценарий 10: core, max и большая queue

```text
core = 2
max = 100
unbounded queue
50 долгих задач
```

Сколько workers обычно будет создано?

**Ответ:** два. После достижения core остальные задачи принимает неограниченная
queue, поэтому условие роста к maximum не наступает.

### Сценарий 11: shutdownNow и задача без interrupt handling

Задача выполняет бесконечный вычислительный цикл и не проверяет interrupt status.
Гарантирует ли `shutdownNow()` её немедленную остановку?

**Ответ:** нет. Метод запросит interrupt, но задача его игнорирует и может
продолжать выполняться.

### Сценарий 12: CallerRunsPolicy и exception

Rejected task выполняется через `CallerRunsPolicy` и бросает неперехваченный
`RuntimeException`. Будет ли caller гарантированно выполнять следующую строку?

**Ответ:** нет. Исключение выполняемой напрямую задачи выйдет в caller и может
прервать его обычный control flow.

## Финальная шпаргалка

### Lock и Condition

- `synchronized` автоматически освобождает intrinsic monitor при выходе;
  `ReentrantLock` требует `unlock()` в `finally`.
- Оба механизма дают mutual exclusion; `ReentrantLock` не становится сам по себе
  безопаснее при исключениях.
- `lock()` ждёт занятый lock; `tryLock()` отвечает сразу;
  `tryLock(timeout)` ждёт ограниченно; `lockInterruptibly()` позволяет прервать
  ожидание.
- После `InterruptedException` status обычно очищен; при необходимости его
  восстанавливают через `Thread.currentThread().interrupt()`.
- Reentrant означает повторный захват тем же потоком. Число `unlock()` должно
  совпадать с числом успешных захватов. `synchronized` тоже reentrant.
- Unfair lock используется по умолчанию и обычно быстрее. Fair lock уменьшает
  риск starvation ценой throughput, но не управляет CPU scheduler.
- `Condition`: `await`, `signal`, `signalAll`. `await()` освобождает lock, ждёт и
  перед возвратом повторно его захватывает.
- Условие вокруг `await()` проверяют в `while`: возможны spurious wakeup и
  повторное изменение состояния.
- Несколько conditions, например `notEmpty` и `notFull`, разделяют группы
  ожидающих одного lock.

### Atomics и CAS

- `AtomicInteger`, `AtomicLong`, `AtomicBoolean`, `AtomicReference` выполняют
  атомарные операции над отдельным значением.
- `incrementAndGet()` возвращает новое значение; `getAndIncrement()` — старое.
- `volatile count++` не thread-safe: это `read → increment → write`, возможен
  lost update. `volatile` даёт visibility и ordering, но не атомарность состава.
- CAS атомарно делает: `current == expected ? write update : do nothing` и
  возвращает успех.
- После failed CAS нужно перечитать состояние и пересчитать update.
- Lock даёт эксклюзивный доступ; при CAS конкуренты делают попытки, победитель
  обновляет, проигравшие повторяют. CAS тоже синхронизация.
- ABA: состояние прошло `A → B → A`, обычный CAS не замечает историю.
  `AtomicStampedReference` добавляет версию: `A/1` не равно `A/3`.

### ExecutorService и Future

- Thread pool отделяет task от worker thread, переиспользует workers и ограничивает
  параллелизм.
- `execute(Runnable)` не возвращает результат. `submit` возвращает `Future`.
- `Runnable` не возвращает task result и не объявляет checked exceptions;
  `Callable<T>` возвращает `T` и может их бросать.
- `Future.get()` блокирует caller, если результат не готов. Работу выполняет
  worker, блокируется вызвавший `get()` поток.
- Ошибка задачи приходит из `get()` как `ExecutionException`; причина находится
  в `getCause()`.
- `get(timeout)` бросает `TimeoutException`, но не отменяет задачу.
- После успешного `cancel` вызов `get()` бросает `CancellationException`.
- `cancel(true)` пытается interrupt'нуть worker, но не убивает его принудительно.
  Задача должна реагировать на interruption.
- `shutdown()` прекращает приём, но выполняет принятые задачи. `shutdownNow()`
  пытается interrupt'нуть выполняемые и возвращает не начатые; мгновенное
  завершение не гарантируется.

### Thread pools

- `newFixedThreadPool(n)`: `n` workers и практически неограниченная queue;
  возможен рост памяти при перегрузке.
- `newSingleThreadExecutor()`: один worker, последовательное выполнение,
  потенциально растущая queue.
- `newCachedThreadPool()`: `SynchronousQueue`, переиспользование idle workers и
  потенциально очень большое число новых потоков.
- Алгоритм `ThreadPoolExecutor`: workers до core → queue → workers до max → reject.
- `maximumPoolSize` влияет только после того, как queue перестала принимать задачи.
- `keepAliveTime` удаляет idle workers сверх core; core threads стандартно
  сохраняются.
- `AbortPolicy` бросает exception; `CallerRunsPolicy` выполняет в caller и создаёт
  backpressure; `DiscardPolicy` теряет новую задачу; `DiscardOldestPolicy` удаляет
  старую ожидающую и повторяет приём новой.
- CPU-bound pool обычно близок к числу processors. Слишком много вычисляющих
  потоков добавляет switching и overhead.
- I/O-bound pool может быть больше, но размер определяют метриками и ограничениями
  downstream. 200 workers не превращают 20 DB connections в 200.
