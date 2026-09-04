# Virtual Threads в Java

## 1. Что такое Virtual Threads

**Virtual Threads** — лёгкие потоки, управляемые JVM.

Они были добавлены в Java как часть Project Loom и стали production-ready в Java 21.

Главная идея:

```text
одна задача
→ один virtual thread
```

Virtual Threads особенно полезны для приложений, где существует большое количество одновременно выполняющихся задач, которые значительную часть времени проводят в ожидании:

```text
JDBC
HTTP
файловый I/O
сетевые операции
внешние API
очереди
другие blocking I/O операции
```

Virtual Threads не являются отдельными потоками операционной системы в обычном смысле.

JVM может поддерживать очень большое количество virtual threads и распределять их выполнение по меньшему количеству обычных platform threads.

---

# 2. Platform Thread

Обычный Java-поток называется **platform thread**.

Пример:

```java
Thread thread = new Thread(() -> {
    doWork();
});

thread.start();
```

Platform thread тесно связан с потоком операционной системы.

Упрощённо:

```text
Java Platform Thread
        ↓
OS Thread
        ↓
CPU
```

OS thread — сравнительно дорогой ресурс.

Для него нужны:

```text
память под stack
ресурсы операционной системы
работа scheduler
context switching
```

Поэтому обычно нельзя бездумно создавать десятки или сотни тысяч platform threads.

Вместо этого традиционно используются thread pools:

```java
ExecutorService executor =
        Executors.newFixedThreadPool(100);
```

Получается:

```text
много задач
        ↓
очередь
        ↓
100 platform threads
```

---

# 3. Проблема обычных потоков в backend

Представим обработку HTTP-запроса:

```java
User user = userRepository.findById(id);

Orders orders = ordersClient.load(user);

PaymentInfo payment = paymentClient.load(user);
```

Большую часть времени поток может не выполнять вычисления на CPU.

Он ждёт:

```text
PostgreSQL
HTTP
внешний сервис
файл
сеть
```

Например:

```text
5 мс CPU
+
200 мс ожидание БД
+
100 мс ожидание HTTP
```

Platform thread остаётся связан с этим request на всём протяжении его выполнения.

Если одновременно существуют тысячи таких запросов, возникает проблема масштабирования по количеству platform threads.

---

# 4. Главная идея Virtual Threads

Virtual threads намного легче platform threads.

Поэтому вместо модели:

```text
ограниченный thread pool
+
огромная очередь задач
```

можно использовать:

```text
задача 1 → virtual thread 1
задача 2 → virtual thread 2
задача 3 → virtual thread 3
...
```

Например:

```text
10 000 задач
→ около 10 000 virtual threads
```

Но это не означает:

```text
10 000 virtual threads
=
10 000 OS threads
```

Virtual threads управляются JVM.

---

# 5. Carrier Thread

Virtual thread не исполняет Java-код непосредственно на CPU.

Для выполнения он временно использует обычный platform thread.

Такой platform thread называется:

```text
carrier thread
```

Упрощённо:

```text
Virtual Thread A ─┐
Virtual Thread B ─┤
Virtual Thread C ─┤
Virtual Thread D ─┼──→ Carrier Threads ──→ OS Threads ──→ CPU
Virtual Thread E ─┤
...               │
Virtual Thread N ─┘
```

Virtual thread может в разные моменты времени выполняться на разных carrier threads.

---

# 6. Mount и Unmount

Когда virtual thread начинает выполнять Java-код, JVM может **смонтировать** его на carrier thread.

Это называется:

```text
mount
```

Например:

```text
Virtual Thread A
        ↓
mount
        ↓
Carrier Thread 1
        ↓
выполнение кода
```

Если virtual thread блокируется на поддерживаемой блокирующей операции, JVM может снять его с carrier thread.

Это называется:

```text
unmount
```

Тогда carrier освобождается.

---

# 7. Что происходит при blocking I/O

Допустим:

```java
User user = repository.findById(id);
```

SQL-запрос выполняется 300 мс.

Virtual thread начинает операцию:

```text
Virtual Thread A
        ↓
Carrier 1
        ↓
JDBC
        ↓
ожидание
```

В хорошем случае JVM может сделать:

```text
Virtual Thread A
        ↓
unmount
```

После этого:

```text
Carrier 1
→ свободен
→ выполняет Virtual Thread B
```

Когда ответ от БД готов:

```text
Virtual Thread A
→ становится runnable
→ scheduler
→ mount на свободный carrier
→ продолжает выполнение
```

Причём это не обязательно тот же carrier thread, который выполнял его раньше.

---

# 8. Почему Virtual Threads полезны для I/O-bound задач

Рассмотрим:

```text
5000 задач
каждая:
10 мс CPU
500 мс ожидание HTTP
```

Большую часть времени задачи ждут.

Virtual threads позволяют:

```text
задача ждёт I/O
→ virtual thread unmount
→ carrier выполняет другую задачу
```

Таким образом небольшое количество carrier threads может обслуживать очень большое число ожидающих virtual threads.

Главный выигрыш:

```text
более высокий throughput
```

То есть приложение может одновременно обслуживать больше блокирующих задач.

---

# 9. Virtual Threads не ускоряют CPU-bound задачи

Представим:

```java
calculatePrimeNumbersFor10Minutes();
```

Задача постоянно выполняет вычисления и практически не блокируется.

Тогда:

```text
Virtual Thread
→ постоянно выполняется
→ carrier постоянно занят
```

Virtual thread не может освободить CPU.

Если процессор имеет:

```text
8 ядер
```

создание:

```text
100 000 virtual threads
```

не создаст:

```text
100 000 вычислительных ядер
```

Поэтому:

```text
CPU-bound
→ Virtual Threads почти не дают преимущества

I/O-bound
→ Virtual Threads подходят хорошо
```

Примеры CPU-bound задач:

```text
сложные математические вычисления
кодирование видео
криптография
сжатие данных
обработка больших массивов
```

---

# 10. Throughput и Latency

Virtual Threads в первую очередь помогают увеличить:

```text
throughput
```

То есть количество задач, которое система может эффективно обслуживать одновременно.

Они не предназначены для автоматического уменьшения времени выполнения одной операции.

Например:

```text
HTTP-запрос занимает 500 мс
```

После перехода на virtual threads он не обязательно станет:

```text
100 мс
```

Но сервер сможет эффективнее обслуживать много таких запросов одновременно.

---

# 11. Создание Virtual Thread

Самый простой вариант:

```java
Thread thread = Thread.startVirtualThread(() -> {
    System.out.println("Hello from virtual thread");
});
```

Метод сразу создаёт и запускает virtual thread.

---

# 12. Thread.ofVirtual()

Можно использовать builder:

```java
Thread thread = Thread.ofVirtual()
        .name("request-handler")
        .start(() -> {
            handleRequest();
        });
```

Это удобно, если нужно настроить параметры потока, например имя.

---

# 13. Проверка типа Thread

Можно определить, является ли поток virtual:

```java
Thread.currentThread().isVirtual();
```

Например:

```java
Thread.startVirtualThread(() -> {
    System.out.println(
            Thread.currentThread().isVirtual()
    );
});
```

Результат:

```text
true
```

---

# 14. VirtualThreadPerTaskExecutor

Для большого количества задач обычно удобнее использовать:

```java
Executors.newVirtualThreadPerTaskExecutor()
```

Пример:

```java
try (ExecutorService executor =
         Executors.newVirtualThreadPerTaskExecutor()) {

    executor.submit(() -> task1());
    executor.submit(() -> task2());
    executor.submit(() -> task3());
}
```

Основная модель:

```text
одна submitted task
→ один новый virtual thread
```

Например:

```text
10 000 tasks
→ примерно 10 000 virtual threads
```

Это не fixed thread pool.

---

# 15. Virtual Threads обычно не нужно пулить

Platform threads дорогие.

Поэтому традиционно используется:

```java
Executors.newFixedThreadPool(100);
```

То есть:

```text
10 000 задач
→ 100 workers
→ остальные ждут в очереди
```

Virtual threads дешёвые.

Поэтому модель другая:

```text
10 000 задач
→ 10 000 virtual threads
```

Следовательно, создавать искусственный:

```text
"pool из 100 virtual threads"
```

обычно не нужно.

Основная идея:

```text
не ограничивать количество дешёвых virtual threads
только ради ограничения количества потоков
```

---

# 16. Ограничивать нужно ресурс, а не Virtual Threads

Допустим внешний API разрешает:

```text
30 одновременных запросов
```

Приложение создаёт:

```text
10 000 virtual threads
```

Неправильная идея:

```text
сделаем pool только из 30 virtual threads
```

Проблема находится не в virtual threads.

Ограниченный ресурс:

```text
внешний API
```

Поэтому логичнее использовать:

```java
Semaphore semaphore = new Semaphore(30);
```

Пример:

```java
Semaphore semaphore = new Semaphore(30);

try (ExecutorService executor =
         Executors.newVirtualThreadPerTaskExecutor()) {

    for (Request request : requests) {
        executor.submit(() -> {
            semaphore.acquire();

            try {
                callExternalApi(request);
            } finally {
                semaphore.release();
            }

            return null;
        });
    }
}
```

Получается:

```text
10 000 virtual threads
        ↓
Semaphore(30)
        ↓
максимум 30 запросов к API
```

---

# 17. Semaphore и Virtual Threads

Задачи `Semaphore` и Virtual Threads разные.

```text
Virtual Threads
→ модель конкурентного выполнения

Semaphore
→ ограничение количества одновременных пользователей ресурса
```

Поэтому они хорошо работают вместе.

---

# 18. Virtual Threads и база данных

Представим:

```text
1000 virtual threads
```

и:

```text
HikariCP maximumPoolSize = 20
```

Все 1000 virtual threads пытаются выполнить SQL.

Это не означает:

```text
1000 запросов одновременно выполняются в PostgreSQL
```

Connection pool ограничивает количество одновременно используемых соединений.

Упрощённо:

```text
1000 virtual threads
        ↓
HikariCP
        ↓
20 JDBC connections
        ↓
PostgreSQL
```

Остальные virtual threads ждут свободное соединение.

Virtual Threads не отменяют ограничения:

```text
connection pool
PostgreSQL
external API
rate limit
network
Semaphore
```

Они позволяют эффективнее ждать эти ресурсы.

---

# 19. Virtual Threads не заменяют Connection Pool

Важно:

```text
Virtual Thread
≠ DB connection
```

Даже если создание virtual thread дешёвое, создание тысяч DB connections не становится хорошей идеей.

Connection pool всё ещё нужен.

---

# 20. Pinning

Обычно при блокировке:

```text
Virtual Thread
→ unmount
→ carrier освобождается
```

Но бывают ситуации, когда virtual thread не может быть снят с carrier.

Это называется:

```text
pinning
```

Схема:

```text
Virtual Thread
→ блокируется
→ остаётся mounted
→ Carrier Thread тоже остаётся занят
```

В результате carrier нельзя использовать для другого virtual thread.

---

# 21. Почему Pinning опасен

Главное преимущество virtual threads:

```text
один carrier
→ может обслуживать множество ожидающих virtual threads
```

При pinning:

```text
Virtual Thread A
→ ждёт
→ Carrier 1 тоже ждёт
```

Если pinned virtual threads много, scalability и throughput уменьшаются.

---

# 22. Pinning и synchronized в Java 21

Для **Java 21** важный сценарий pinning связан с блокировкой внутри `synchronized`.

Например:

```java
synchronized (lock) {
    response = remoteService.call();
}
```

Если:

```text
remoteService.call()
```

ждёт сеть несколько секунд, virtual thread может оставаться pinned к carrier thread.

Получается:

```text
Virtual Thread
→ synchronized
→ blocking I/O
→ pinning
→ carrier тоже ждёт
```

Это потенциально плохо для масштабируемости.

---

# 23. Короткий synchronized не является катастрофой

Например:

```java
synchronized (lock) {
    counter++;
}
```

Критическая секция выполняется очень быстро.

Поэтому проблема не в самом наличии `synchronized`, а особенно в сочетании:

```text
долгий synchronized
+
blocking operation
```

---

# 24. ReentrantLock и Java 21

Для сценариев, где нужно избежать длительного удержания carrier внутри `synchronized`, в Java 21 иногда рассматривается `ReentrantLock`.

Пример:

```java
lock.lock();

try {
    // критическая секция
} finally {
    lock.unlock();
}
```

Но правильная архитектура всё равно должна стремиться не выполнять длительный blocking I/O внутри критической секции без необходимости.

---

# 25. Важное замечание про новые JDK

Поведение pinning зависит от версии Java.

В Java 21 блокировки через Java monitors и `synchronized` были важным источником pinning.

В более новых JDK реализация virtual threads была улучшена, и многие случаи pinning, связанные с `synchronized`, были устранены.

Поэтому при обсуждении pinning важно уточнять:

```text
какая версия Java используется
```

Для Java 21 правило:

```text
долгий blocking I/O внутри synchronized
→ потенциально проблемный сценарий
```

остаётся важным.

---

# 26. ThreadLocal

Virtual threads поддерживают:

```java
ThreadLocal
```

Каждый virtual thread может иметь собственное значение.

Но появляется проблема масштаба.

---

# 27. ThreadLocal и память

Представим:

```text
100 000 virtual threads
```

Каждый хранит:

```text
1 MB
```

Получается около:

```text
100 GB
```

Сами virtual threads дешёвые.

Но объекты, находящиеся в `ThreadLocal`, дешевле от этого не становятся.

Поэтому:

```text
Virtual Thread
→ дешёвый

Virtual Thread
+ большой ThreadLocal
→ потенциально огромный расход памяти
```

---

# 28. ThreadLocal как кэш

Особенно опасна старая модель:

```java
ThreadLocal<ExpensiveObject> cache;
```

В fixed thread pool:

```text
100 workers
→ максимум около 100 кэшированных объектов
```

С virtual-thread-per-task:

```text
100 000 задач
→ 100 000 virtual threads
```

и потенциально может появиться огромное количество таких объектов.

Поэтому не стоит использовать `ThreadLocal` как тяжёлый per-thread cache без необходимости.

---

# 29. Virtual Threads и Blocking Code

Одна из сильных сторон Virtual Threads — возможность сохранить обычный последовательный blocking style.

Например:

```java
User user = loadUser();
Orders orders = loadOrders(user);
Payment payment = loadPayment(user);
```

Код остаётся последовательным и читаемым.

При этом virtual thread может эффективно парковаться на блокирующих операциях.

---

# 30. Virtual Threads и CompletableFuture

Virtual Threads и `CompletableFuture` решают разные задачи.

`CompletableFuture`:

```text
→ асинхронные pipeline
→ composition
→ thenApply
→ thenCompose
→ thenCombine
→ обработка ошибок
```

Virtual Threads:

```text
→ дешёвые потоки
→ позволяют писать обычный blocking code
→ хорошо масштабируются для I/O-bound задач
```

Они не являются прямой заменой друг другу.

---

# 31. Virtual Threads и ExecutorService

Пример:

```java
try (ExecutorService executor =
         Executors.newVirtualThreadPerTaskExecutor()) {

    Future<User> userFuture =
            executor.submit(() -> loadUser());

    Future<Orders> ordersFuture =
            executor.submit(() -> loadOrders());

    User user = userFuture.get();
    Orders orders = ordersFuture.get();
}
```

Каждая submitted task получает отдельный virtual thread.

---

# 32. try-with-resources

`ExecutorService` можно использовать через:

```java
try (ExecutorService executor = ...) {
}
```

Это удобный способ контролировать lifecycle executor.

---

# 33. Virtual Threads являются daemon threads

Virtual threads всегда являются:

```text
daemon threads
```

Они не удерживают JVM живой сами по себе.

---

# 34. Virtual Threads и завершение JVM

Например:

```java
public static void main(String[] args) {

    Thread.startVirtualThread(() -> {
        try {
            Thread.sleep(5000);
            System.out.println("done");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    });

    System.out.println("main finished");
}
```

Если `main` завершился и других non-daemon threads нет:

```text
JVM может завершиться
```

Поэтому `"done"` не обязано успеть напечататься.

---

# 35. join()

Если нужно обязательно дождаться virtual thread:

```java
Thread thread = Thread.startVirtualThread(() -> {
    doWork();
});

thread.join();
```

`join()` заставляет вызывающий поток ждать завершения указанного virtual thread.

---

# 36. Interrupt

Virtual threads поддерживают механизм interruption.

Пример:

```java
Thread thread = Thread.startVirtualThread(() -> {
    try {
        Thread.sleep(10_000);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
});

thread.interrupt();
```

Как и с обычными потоками, interrupt является кооперативным механизмом.

Это не force kill.

---

# 37. Future.cancel(true) с VirtualThreadPerTaskExecutor

Если задача отправлена:

```java
try (ExecutorService executor =
         Executors.newVirtualThreadPerTaskExecutor()) {

    Future<?> future =
            executor.submit(() -> longOperation());

    future.cancel(true);
}
```

`Future.cancel(true)` может попытаться прервать thread, выполняющий эту задачу.

Но код задачи всё равно должен корректно реагировать на interruption.

---

# 38. Отличие от CompletableFuture.cancel(true)

Не следует путать:

```java
Future.cancel(true)
```

для задачи, выполняемой executor,

и:

```java
CompletableFuture.cancel(true)
```

У `CompletableFuture` параметр `mayInterruptIfRunning` не означает гарантированный interrupt underlying computation.

---

# 39. Что Virtual Threads не решают

Virtual Threads не решают автоматически:

```text
медленные SQL-запросы
плохие индексы
ограничения PostgreSQL
rate limit внешнего API
нехватку DB connections
race conditions
deadlocks
ошибки синхронизации
CPU bottleneck
плохую архитектуру
```

Они решают конкретную проблему:

```text
стоимость большого количества одновременно ожидающих потоков
```

---

# 40. Virtual Threads не отменяют synchronization

Если несколько virtual threads работают с общими mutable данными:

```java
counter++;
```

race condition остаётся race condition.

Virtual Threads не делают код автоматически thread-safe.

По-прежнему могут потребоваться:

```text
synchronized
Lock
Atomic*
Concurrent Collections
immutability
```

---

# 41. Virtual Threads и Java Memory Model

Для virtual threads действуют те же правила JMM:

```text
visibility
atomicity
ordering
happens-before
```

Virtual Thread всё ещё является `Thread` с точки зрения модели многопоточности Java.

---

# 42. Когда использовать Virtual Threads

Хорошие сценарии:

```text
HTTP server
JDBC
REST clients
blocking network I/O
file operations
много одновременных запросов
thread-per-request модель
```

Особенно если:

```text
задачи большую часть времени ждут
```

---

# 43. Когда Virtual Threads мало помогают

Плохой кандидат:

```text
тяжёлые CPU-bound вычисления
```

Например:

```text
рендеринг
кодирование видео
сложная математика
криптография
массовое сжатие
```

Причина:

```text
carrier постоянно занят CPU
→ unmount почти не происходит
→ преимущества нет
```

---

# 44. Основной принцип архитектуры

С platform threads часто думают:

```text
Сколько потоков я могу себе позволить?
```

С virtual threads вопрос смещается:

```text
Какой реальный ресурс является ограниченным?
```

Например:

```text
DB connections = 20
external API concurrency = 50
rate limit = 100 requests/sec
CPU cores = 8
```

И ограничивать нужно именно эти ресурсы.

---

# 45. Типичные ошибки

## Ошибка 1. Использовать Virtual Threads для ускорения CPU-bound работы

Virtual threads не добавляют CPU cores.

```text
CPU-bound
→ выигрыша почти нет
```

## Ошибка 2. Создавать fixed pool из virtual threads без причины

Virtual threads дешёвые.

Обычно используется:

```text
one task
→ one virtual thread
```

## Ошибка 3. Считать, что 1000 Virtual Threads означают 1000 параллельных SQL-запросов

Connection pool может иметь только 20 connections и станет реальным ограничением.

## Ошибка 4. Игнорировать Pinning в Java 21

Особенно:

```java
synchronized (lock) {
    slowBlockingOperation();
}
```

может быть проблемным для virtual threads в Java 21.

## Ошибка 5. Хранить огромные объекты в ThreadLocal

При десятках или сотнях тысяч virtual threads это может привести к огромному потреблению памяти.

## Ошибка 6. Думать, что Virtual Threads делают код thread-safe

Race conditions остаются.

## Ошибка 7. Забывать про daemon-поведение

Если выполнение обязательно нужно дождаться:

```java
thread.join();
```

## Ошибка 8. Путать throughput и latency

Virtual Threads обычно повышают способность приложения обслуживать много одновременных блокирующих задач.

Они не обязаны ускорять отдельный request.

---

# 46. Типичные вопросы на собеседовании

## Что такое Virtual Thread?

Лёгкий поток, управляемый JVM, который позволяет эффективно поддерживать большое количество одновременно выполняющихся и блокирующих задач.

## Чем Virtual Thread отличается от Platform Thread?

Platform thread тесно связан с OS thread и является сравнительно дорогим ресурсом.

Virtual thread значительно легче и может временно выполняться на одном из carrier platform threads.

## Что такое Carrier Thread?

Platform thread, на котором в данный момент выполняется virtual thread.

## Что такое Mount?

Момент, когда virtual thread начинает выполняться на carrier thread.

## Что такое Unmount?

Снятие virtual thread с carrier, например во время подходящей блокирующей операции.

## Почему Virtual Threads хорошо подходят для I/O-bound задач?

Потому что во время ожидания I/O virtual thread может освободить carrier thread.

## Почему Virtual Threads почти не помогают CPU-bound задачам?

CPU-bound задача постоянно выполняет вычисления и удерживает carrier.

Количество CPU cores не увеличивается.

## Нужно ли создавать pool Virtual Threads?

Обычно нет.

Рекомендуемая модель:

```text
one task
→ one virtual thread
```

## Как ограничить количество одновременных запросов к внешнему API?

Ограничивать конкретный ресурс, например через:

```java
Semaphore semaphore = new Semaphore(30);
```

## Что произойдёт, если 1000 Virtual Threads обращаются к БД, а DB pool содержит 20 connections?

Около 20 задач смогут одновременно использовать connections.

Остальные будут ждать свободное соединение.

## Что такое Pinning?

Ситуация, когда заблокированный virtual thread не может быть unmounted с carrier.

Carrier остаётся занят вместе с ним.

## Почему Pinning плохо?

Carrier thread не может выполнять другие virtual threads.

При большом количестве pinning scalability уменьшается.

## Что важно знать о Pinning в Java 21?

Длительная blocking operation внутри `synchronized` может привести к pinning.

## Можно ли использовать ThreadLocal с Virtual Threads?

Да.

Но при огромном количестве virtual threads нельзя бездумно хранить большие объекты в `ThreadLocal`.

## Virtual Threads являются daemon threads?

Да.

Virtual thread сам по себе не удерживает JVM живой.

## Как дождаться Virtual Thread?

```java
thread.join();
```

## Делают ли Virtual Threads код автоматически thread-safe?

Нет.

Правила синхронизации и Java Memory Model остаются теми же.

## Virtual Threads заменяют CompletableFuture?

Нет.

Они решают разные задачи.

---

# 47. Сравнение Platform Threads и Virtual Threads

```text
Platform Thread

→ сравнительно дорогой
→ тесно связан с OS thread
→ обычно используется pool
→ большое количество дорого


Virtual Thread

→ лёгкий
→ управляется JVM
→ выполняется на carrier
→ можно создавать очень много
→ при подходящем blocking I/O может unmount
→ обычно one task = one virtual thread
```

---

# 48. Сравнение I/O-bound и CPU-bound

```text
I/O-bound:

5 мс CPU
500 мс HTTP wait

→ Virtual Threads подходят хорошо
```

```text
CPU-bound:

500 мс непрерывных вычислений

→ Virtual Threads почти не дают преимуществ
```

---

# 49. Итоговая шпаргалка

```text
Virtual Thread
→ лёгкий Thread
→ управляется JVM

Platform Thread
→ обычный Java thread
→ тесно связан с OS thread

Carrier Thread
→ platform thread
→ выполняет virtual thread

mount
→ virtual thread начинает выполняться на carrier

unmount
→ virtual thread снимается с carrier

blocking I/O
→ хороший сценарий для Virtual Threads

CPU-bound
→ преимуществ почти нет

newVirtualThreadPerTaskExecutor()
→ одна task = один virtual thread

Virtual Threads обычно не пулить

ограниченный внешний ресурс
→ ограничивать сам ресурс

Semaphore
→ лимит concurrent access

DB pool
→ всё ещё ограничивает SQL concurrency

Pinning
→ virtual thread не может unmount
→ carrier остаётся занят

Java 21:
долгий blocking I/O внутри synchronized
→ потенциальный pinning

ThreadLocal
→ работает
→ опасны большие per-thread объекты при огромном числе threads

Virtual Threads
→ daemon threads

нужно дождаться:
→ join()

Virtual Threads
≠ автоматическая thread safety

Virtual Threads
≠ больше CPU cores

Virtual Threads
→ прежде всего увеличение throughput
  для большого числа blocking tasks
```

# 50. Главное

Virtual Threads меняют привычную модель работы с потоками.

Для platform threads часто используется:

```text
небольшое количество дорогих workers
+
очередь задач
```

Для virtual threads основная модель:

```text
одна задача
→ один дешёвый virtual thread
```

При blocking I/O virtual thread может быть приостановлен, снят с carrier и продолжить работу позднее.

Carrier в это время используется для другой задачи.

Поэтому Virtual Threads особенно хорошо подходят для backend-приложений с большим количеством одновременно ожидающих операций:

```text
JDBC
HTTP
REST
файлы
сеть
```

При этом они не отменяют реальные ограничения системы:

```text
CPU
DB connections
rate limits
external API limits
memory
synchronization
```

Главный принцип:

```text
не ограничивать дешёвые virtual threads без причины
→ ограничивать реальный дефицитный ресурс
```

---

## См. также

- [`02-multithreading-basics.md`](02-multithreading-basics.md) — platform threads
  и их жизненный цикл
- [`03-locks-atomics-executors.md`](03-locks-atomics-executors.md) — почему
  привычная модель пулов здесь не нужна
- [`05-completable-future.md`](05-completable-future.md) — разные задачи, а не
  замена друг другу
