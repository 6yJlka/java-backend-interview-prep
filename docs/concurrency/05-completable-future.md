# CompletableFuture в Java

## Зачем он нужен

Обычный `Future` позволяет запустить задачу в другом потоке и позднее забрать
результат:

```java
Future<Integer> future = executor.submit(() -> calculate());

Integer result = future.get();
```

Проблема появляется, когда нужна последовательность зависимых асинхронных
операций:

```text
получить пользователя
→ загрузить его заказы
→ посчитать сумму
→ вывести результат
```

С обычным `Future` это выглядит так:

```java
Future<User> userFuture = executor.submit(() -> loadUser());
User user = userFuture.get();

Future<List<Order>> ordersFuture = executor.submit(() -> loadOrders(user));
List<Order> orders = ordersFuture.get();

Future<Integer> totalFuture = executor.submit(() -> calculateTotal(orders));
Integer total = totalFuture.get();
```

Получается чередование:

```text
submit → get → submit → get → submit → get
```

Задачи асинхронные, но вызывающий поток блокируется на каждом `get()`.

`CompletableFuture` позволяет описать то же самое как цепочку, не блокируясь:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenApply(User::getName)
        .thenAccept(System.out::println);
```

---

## Создание

### runAsync

Когда операция ничего не возвращает:

```java
CompletableFuture<Void> future =
        CompletableFuture.runAsync(() -> sendNotification());
```

Работает с `Runnable`.

### supplyAsync

Когда операция должна вернуть значение:

```java
CompletableFuture<User> future =
        CompletableFuture.supplyAsync(() -> loadUser());
```

Работает с `Supplier<T>`.

```text
runAsync()    → Runnable    → CompletableFuture<Void>
supplyAsync() → Supplier<T> → CompletableFuture<T>
```

---

## Преобразование результата

### thenApply

Преобразует результат предыдущего этапа:

```java
CompletableFuture<User> userFuture =
        CompletableFuture.supplyAsync(() -> loadUser());

CompletableFuture<String> nameFuture =
        userFuture.thenApply(user -> user.getName());
```

```text
CompletableFuture<User>
        ↓ thenApply
CompletableFuture<String>
```

По смыслу это `T → R`, то есть аналог `map`.

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> 10)
                .thenApply(value -> value * 2);   // 20
```

### thenAccept

Получает результат, но ничего не возвращает:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenAccept(user -> System.out.println(user.getName()));
```

Возвращает `CompletableFuture<Void>`.

### thenRun

Выполняет действие после завершения предыдущего этапа, но результат не получает и
ничего не возвращает:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenRun(() -> System.out.println("Операция завершена"));
```

```text
thenApply()  → получает значение → возвращает новое значение
thenAccept() → получает значение → ничего не возвращает
thenRun()    → не получает значение → ничего не возвращает
```

Полная цепочка:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenApply(User::getName)
        .thenAccept(System.out::println)
        .thenRun(() -> System.out.println("Готово"));
```

---

## thenApply и thenCompose

Одно из главных различий в теме.

Если следующий шаг — обычный метод:

```java
String getUserName(User user);
```

подходит `thenApply()`:

```java
future.thenApply(user -> getUserName(user));   // CompletableFuture<String>
```

Но если следующий метод сам асинхронный:

```java
CompletableFuture<List<Order>> loadOrders(User user);
```

то `thenApply()` даст вложенность:

```text
CompletableFuture<CompletableFuture<List<Order>>>
```

Для этого существует `thenCompose()`, который распрямляет вложенность:

```java
CompletableFuture<List<Order>> ordersFuture =
        future.thenCompose(user -> loadOrders(user));
```

```text
thenApply:   T → R                    → CompletableFuture<R>
thenCompose: T → CompletableFuture<R> → CompletableFuture<R>
```

Удобная аналогия и главное правило:

```text
thenApply   ≈ map
thenCompose ≈ flatMap

функция возвращает обычный R     → thenApply()
функция возвращает Future<R>     → thenCompose()
```

---

## thenCombine

Используется, когда есть две независимые асинхронные операции, результаты которых
нужно объединить.

```java
CompletableFuture<User> userFuture =
        CompletableFuture.supplyAsync(() -> loadUser());

CompletableFuture<Rate> rateFuture =
        CompletableFuture.supplyAsync(() -> loadRate());

CompletableFuture<UserDto> result =
        userFuture.thenCombine(
                rateFuture,
                (user, rate) -> new UserDto(user, rate)
        );
```

```text
User Future ──────┐
                  ├→ thenCombine → UserDto
Rate Future ──────┘
```

Разница с `thenCompose()` — в зависимости операций:

```text
thenCompose()               thenCombine()
B зависит от результата A   A и B независимы

A                           A ──┐
↓                               ├→ combine
B(A)                        B ──┘
```

```text
thenCompose: получить User → взять user.id → загрузить Orders
thenCombine: загрузить User + загрузить ExchangeRate → объединить в DTO
```

---

## Обработка ошибок

`CompletableFuture` завершается либо успешно, либо исключительно. Если этап упал,
последующие обычные преобразования не выполняются, пока ошибка не обработана.

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new IllegalStateException("boom");
                })
                .thenApply(value -> value * 2);
```

`thenApply()` здесь не вызывается — future завершается исключительно.

### exceptionally

Обрабатывает ошибку и возвращает запасное значение:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new RuntimeException("boom");
                })
                .exceptionally(ex -> 10)
                .thenApply(value -> value * 2);
```

```text
exception → exceptionally → 10 → thenApply → 20
```

По смыслу это `Throwable → T`. Вызывается только при ошибке, после чего цепочка
считается восстановленной.

### handle

Вызывается и при успехе, и при ошибке, получая пару аргументов:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> 10)
                .handle((result, ex) -> {
                    if (ex != null) {
                        return 0;
                    }

                    return result + 5;
                })
                .thenApply(value -> value * 2);
```

```text
успех:  result = значение, ex = null
ошибка: result = null,     ex = exception
```

```text
10 → handle → 15 → thenApply → 30
```

### whenComplete

Тоже вызывается в обоих случаях, но предназначен для побочных эффектов:
логирования, метрик, очистки.

```java
future.whenComplete((result, ex) -> {
    if (ex != null) {
        log.error("Ошибка", ex);
    } else {
        log.info("Результат: {}", result);
    }
});
```

Ключевое отличие от `handle()` — он не поглощает ошибку и не меняет результат:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new RuntimeException("boom");
                })
                .whenComplete((result, ex) -> System.out.println("finished"))
                .exceptionally(ex -> 5)
                .thenApply(value -> value * 2);
```

```text
exception
↓
whenComplete → печатает finished
↓
ошибка идёт дальше
↓
exceptionally → 5
↓
thenApply → 10
```

```text
exceptionally() → только при ошибке → обычно fallback
handle()        → при успехе и ошибке → может преобразовать результат
whenComplete()  → при успехе и ошибке → side effect, результат и ошибка идут дальше
```

---

## Получение результата

### get

Наследуется от `Future` и работает с проверяемыми исключениями:

```java
try {
    Integer result = future.get();
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
} catch (ExecutionException e) {
    System.out.println(e.getCause());
}
```

Если асинхронная операция бросила исключение, `get()` бросит
`ExecutionException`, а исходная ошибка окажется в `getCause()`.

### join

Проверяемых исключений не требует:

```java
try {
    future.join();
} catch (CompletionException e) {
    System.out.println(e.getCause());
}
```

При исключительном завершении бросает непроверяемое `CompletionException`, и
исходная ошибка снова в `getCause()`.

```text
get()  → ExecutionException, InterruptedException — checked
join() → CompletionException — unchecked
```

Поэтому внутри цепочек и в стримах обычно используют `join()`:

```java
List<User> users = futures.stream()
        .map(CompletableFuture::join)
        .toList();
```

---

## Executor и суффикс Async

### Executor по умолчанию

```java
CompletableFuture.supplyAsync(() -> loadUser());
```

Без явного executor задача обычно выполняется в `ForkJoinPool.commonPool()`. То
же касается большинства методов с суффиксом `Async`.

### Свой executor

```java
ExecutorService executor = Executors.newFixedThreadPool(4);

CompletableFuture<User> future =
        CompletableFuture.supplyAsync(() -> loadUser(), executor);

future.thenApplyAsync(user -> process(user), executor);
```

Для долгих и блокирующих операций отдельный executor предпочтителен: общий пул
используется многими частями приложения, включая параллельные стримы.

### thenApply и thenApplyAsync

```java
CompletableFuture
        .supplyAsync(() -> 10)
        .thenApply(value -> value * 2);
```

Вариант без суффикса не требует отдельного планирования: продолжение может
выполнить тот поток, который завершил предыдущий этап. Если же future уже
завершён к моменту присоединения продолжения, его может выполнить поток,
вызывающий `thenApply()`. Утверждать, в каком именно потоке это произойдёт,
нельзя.

Вариант с суффиксом планирует продолжение как отдельную асинхронную задачу — в
`ForkJoinPool.commonPool()` либо в переданном executor.

Такие пары существуют для большинства операций:

```text
thenApply / thenApplyAsync
thenAccept / thenAcceptAsync
thenRun / thenRunAsync
thenCompose / thenComposeAsync
thenCombine / thenCombineAsync
```

### Почему Async не нужен везде

```java
supplyAsync(...)
        .thenApplyAsync(...)
        .thenApplyAsync(...)
        .thenAcceptAsync(...)
```

Каждый асинхронный этап стоит отдельного планирования:

```text
постановка задачи → очередь executor → выбор worker → выполнение
```

Для небольших быстрых преобразований обычных продолжений достаточно:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenApply(User::getName)
        .thenApply(String::toUpperCase);
```

Суффикс `Async` имеет смысл, когда работу сознательно отправляют в другой пул:

```java
.thenApplyAsync(this::heavyCalculation, cpuExecutor)
```

---

## Несколько futures

### allOf

Ждёт завершения всех переданных futures:

```java
CompletableFuture<Void> all =
        CompletableFuture.allOf(userFuture, ordersFuture, balanceFuture);
```

Тип результата — `CompletableFuture<Void>`: сам метод результаты не собирает, он
лишь сообщает, что все завершены. Забирать их нужно отдельно:

```java
all.join();

User user = userFuture.join();
List<Order> orders = ordersFuture.join();
Balance balance = balanceFuture.join();
```

Со списком это выглядит так:

```java
List<CompletableFuture<User>> futures = ids.stream()
        .map(id -> CompletableFuture.supplyAsync(() -> loadUser(id)))
        .toList();

CompletableFuture
        .allOf(futures.toArray(new CompletableFuture[0]))
        .join();

List<User> users = futures.stream()
        .map(CompletableFuture::join)
        .toList();
```

```text
Future 1 ─┐
Future 2 ─┤
Future 3 ─┼→ allOf → все завершены → собрать результаты
Future N ─┘
```

Если один из futures завершился исключительно, результат `allOf()` тоже будет
исключительным.

### anyOf

Ждёт первый завершившийся future:

```java
CompletableFuture<Object> first =
        CompletableFuture.anyOf(server1, server2, server3);
```

Тип результата — `CompletableFuture<Object>`, потому что переданные futures могут
иметь разные типы.

```text
server1 → 3 сек
server2 → 1 сек
server3 → 2 сек
```

Здесь `anyOf()` завершится примерно через секунду результатом второго сервера.

С этим методом связаны два устойчивых заблуждения.

**Он не отменяет остальные.** После завершения первого future оставшиеся
продолжают работу — их нужно отменять вручную, если это нужно.

**Он ждёт первый завершившийся, а не первый успешный.**

```text
f1 → 3 сек → success
f2 → 1 сек → exception
f3 → 2 сек → success
```

Первым завершится `f2`, и `anyOf()` завершится исключительно. Успешного `f3` он
не дождётся, а `join()` бросит `CompletionException`.

```text
allOf() → дождаться всех    → CompletableFuture<Void>
anyOf() → дождаться первого → CompletableFuture<Object>
```

---

## Отмена и состояния

### cancel

```java
future.cancel(true);
```

Если future ещё не завершён, он переходит в отменённое состояние:

```java
future.isDone();       // true
future.isCancelled();  // true
```

Попытка получить результат даст `CancellationException`.

### cancel(true) не прерывает вычисление

Важное отличие от привычной семантики `FutureTask`. У `CompletableFuture`
параметр `mayInterruptIfRunning` не используется как механизм управления потоком,
выполняющим вычисление.

```java
CompletableFuture<Integer> future =
        CompletableFuture.supplyAsync(() -> {
            expensiveOperation();
            return 42;
        });

future.cancel(true);
```

Это означает прежде всего, что сам future считается отменённым. Метод
`expensiveOperation()` при этом может продолжать выполняться. Остановка
вычисления требует отдельной кооперативной логики.

### Состояния

```java
future.isDone();
future.isCancelled();
future.isCompletedExceptionally();
```

| Исход | `isDone()` | `isCancelled()` | `isCompletedExceptionally()` |
|---|---|---|---|
| Успех | `true` | `false` | `false` |
| Ошибка | `true` | `false` | `true` |
| Отмена | `true` | `true` | `true` |

То есть `isDone()` означает не «задача успешно выполнена», а «future больше не
находится в незавершённом состоянии».

---

## Ручное завершение

Future можно создать без вычисления и завершить руками:

```java
CompletableFuture<String> future = new CompletableFuture<>();

future.isDone();        // false

future.complete("OK");

future.join();          // "OK"
```

Метод `complete()` возвращает `boolean` и сообщает, удалось ли установить
результат:

```java
CompletableFuture<Integer> future = new CompletableFuture<>();

boolean first = future.complete(42);    // true
boolean second = future.complete(100);  // false

future.join();                          // 42
```

Завершить ошибкой можно так:

```java
future.completeExceptionally(new IllegalStateException("DB unavailable"));
```

Правило общее: первое успешное завершение определяет результат. Последующие
`complete()`, `completeExceptionally()` и `cancel()` уже установленный результат
не заменяют.

Этот механизм полезен, когда результат приходит извне — из колбэка библиотеки, из
обработчика сообщения очереди, из ответа сетевого клиента.

---

## Типичная цепочка целиком

```java
CompletableFuture<UserDto> result =
        CompletableFuture
                .supplyAsync(() -> loadUser(), ioExecutor)
                .thenCompose(user -> loadOrdersAsync(user))
                .thenApply(orders -> calculateStatistics(orders))
                .thenApply(stats -> new UserDto(stats))
                .whenComplete((dto, ex) -> logResult(dto, ex))
                .exceptionally(ex -> fallbackDto());
```

```text
loadUser
↓
асинхронно загрузить Orders
↓
преобразовать Orders
↓
собрать DTO
↓
залогировать результат
↓
при ошибке вернуть fallback
```

---

## Типичные ошибки

### Использовать thenApply вместо thenCompose

Если функция возвращает `CompletableFuture<List<Order>>`, то `thenApply()` даст
`CompletableFuture<CompletableFuture<List<Order>>>`. Нужен `thenCompose()`.

### Путать thenCompose и thenCombine

Первый нужен, когда вторая операция зависит от результата первой. Второй — когда
операции независимы и результаты объединяются.

### Ставить Async на каждый этап без причины

Каждое асинхронное продолжение требует отдельного планирования. Для небольших
синхронных преобразований достаточно обычного `thenApply()`.

### Бездумно нагружать commonPool

Без явного executor используется общий пул, который делят все части приложения.
Долгие и блокирующие операции в нём мешают остальным задачам.

### Считать whenComplete обработчиком ошибки

Он выполняет побочный эффект, но ошибку не поглощает — она продолжает идти по
цепочке. Для запасного значения нужен `exceptionally()` или `handle()`.

### Считать anyOf ожиданием первого успешного результата

Он завершается по первому завершившемуся future, включая исключительное
завершение.

### Считать, что anyOf отменяет остальные задачи

Не отменяет. Оставшиеся futures продолжают работу.

### Считать cancel(true) гарантированным прерыванием вычисления

Для `CompletableFuture` это неверно: отмена future и остановка выполняющейся
функции — разные вещи.

### Считать isDone признаком успеха

Он становится `true` при любом завершении, включая ошибку и отмену.

### Вызывать get или join в середине цепочки

Это возвращает ровно ту блокировку вызывающего потока, ради ухода от которой
`CompletableFuture` и нужен.

---

## Краткая памятка

```text
Создание

runAsync()    → Runnable    → CompletableFuture<Void>
supplyAsync() → Supplier<T> → CompletableFuture<T>
```

```text
Продолжения

thenApply()   → T → R
thenAccept()  → T → void
thenRun()     → () → void
thenCompose() → T → CompletableFuture<R>, распрямляет вложенность
thenCombine() → Future<A> + Future<B> → Future<R>

thenApply ≈ map, thenCompose ≈ flatMap
```

```text
Ошибки

exceptionally() → только ошибка → fallback
handle()        → успех и ошибка → новый результат
whenComplete()  → успех и ошибка → side effect, ошибка идёт дальше
```

```text
Получение

get()  → ExecutionException, InterruptedException — checked
join() → CompletionException — unchecked
```

```text
Несколько futures

allOf() → ждать всех    → CompletableFuture<Void>, результаты не собирает
anyOf() → первый завершившийся → CompletableFuture<Object>

anyOf ≠ первый успешный
anyOf ≠ отмена остальных
```

```text
Executor

*Async без executor → обычно ForkJoinPool.commonPool()
*Async с executor   → указанный
без суффикса        → отдельное планирование не обязательно
```

```text
Состояния

isDone()                   → завершён любым способом
isCancelled()              → отменён
isCompletedExceptionally() → ошибка или отмена

complete(value) / completeExceptionally(ex)
→ первое успешное завершение определяет результат

cancel(true)
→ future отменён
→ вычисление может продолжаться
```

---

## Краткий ответ для собеседования

`CompletableFuture` появился потому, что обычный `Future` умеет только отдать
результат через блокирующий `get()`. Как только операций становится несколько и
они зависят друг от друга, код превращается в чередование запусков и ожиданий, и
асинхронность теряет смысл.

Он позволяет описать обработку декларативно. Запуск — `supplyAsync()` для
операции с результатом и `runAsync()` для операции без. Дальше идут продолжения:
`thenApply()` преобразует значение, `thenAccept()` использует его без результата,
`thenRun()` просто выполняет действие после завершения.

Важнейшее различие — между `thenApply()` и `thenCompose()`. Если функция
возвращает обычное значение, нужен первый; если она сама возвращает future, то
первый даст вложенный future, и нужен `thenCompose()`, который эту вложенность
распрямляет. Это ровно та же пара, что `map` и `flatMap`. Отдельно стоит
`thenCombine()` — он объединяет результаты двух независимых операций, которые
могут выполняться параллельно.

Ошибки обрабатываются тремя способами. `exceptionally()` срабатывает только при
ошибке и подставляет запасное значение. `handle()` вызывается всегда и может
преобразовать результат. `whenComplete()` тоже вызывается всегда, но предназначен
для побочных эффектов и ошибку не поглощает — она продолжает идти по цепочке.

Результат забирают через `get()` с проверяемыми исключениями или через `join()`,
который бросает непроверяемое `CompletionException`; внутри цепочек удобнее
второй.

Без явного executor всё выполняется в общем `ForkJoinPool`, что для блокирующих
операций плохо: пул делят все части приложения. Суффикс `Async` не нужно ставить
на каждый этап — он означает отдельное планирование задачи и имеет смысл, только
когда работу сознательно переносят в другой пул.

Два момента, на которых чаще всего ловят. `anyOf()` ждёт первый завершившийся
future, а не первый успешный, и остальные при этом не отменяет. И `cancel(true)`
помечает отменённым сам future, но не гарантирует прерывания выполняющегося
вычисления — это принципиальное отличие от `FutureTask`.

---

## Вопросы на собеседовании

### 1. Чем Future отличается от CompletableFuture?

**Ответ:** `Future` только представляет результат асинхронной операции и даёт
`get()` и `cancel()`. `CompletableFuture` дополнительно позволяет строить
цепочки, объединять futures, обрабатывать ошибки и завершать future вручную.

### 2. Чем runAsync отличается от supplyAsync?

**Ответ:** первый принимает `Runnable` и возвращает `CompletableFuture<Void>`,
второй принимает `Supplier<T>` и возвращает `CompletableFuture<T>`.

### 3. Чем thenApply отличается от thenAccept?

**Ответ:** оба получают результат предыдущего этапа, но первый возвращает новое
значение, а второй ничего не возвращает.

### 4. Чем thenAccept отличается от thenRun?

**Ответ:** `thenAccept()` получает результат предыдущего этапа, `thenRun()` — нет.
Оба возвращают `CompletableFuture<Void>`.

### 5. Чем thenApply отличается от thenCompose?

**Ответ:** `thenApply()` применяется, когда функция возвращает обычное значение, а
`thenCompose()` — когда она возвращает другой `CompletableFuture`. Второй
распрямляет вложенность, как `flatMap`.

### 6. Что получится, если применить thenApply к асинхронной функции?

**Ответ:** вложенный `CompletableFuture<CompletableFuture<R>>`, с которым дальше
работать неудобно.

### 7. Чем thenCompose отличается от thenCombine?

**Ответ:** первый нужен, когда вторая операция зависит от результата первой.
Второй объединяет результаты двух независимых операций после завершения обеих.

### 8. Чем exceptionally отличается от handle?

**Ответ:** `exceptionally()` вызывается только при ошибке, `handle()` — и при
успехе, и при ошибке, получая пару значения и исключения.

### 9. Чем handle отличается от whenComplete?

**Ответ:** `handle()` может преобразовать результат и вернуть другое значение.
`whenComplete()` предназначен для побочных эффектов и оставляет исходный результат
или ошибку без изменений.

### 10. Поглощает ли whenComplete исключение?

**Ответ:** нет. Ошибка продолжает идти по цепочке, и для восстановления нужен
`exceptionally()` или `handle()`.

### 11. Чем get отличается от join?

**Ответ:** `get()` объявляет проверяемые `ExecutionException` и
`InterruptedException`, `join()` бросает непроверяемое `CompletionException`.
Исходная ошибка в обоих случаях лежит в `getCause()`.

### 12. Какой executor используется supplyAsync без явного executor?

**Ответ:** обычно `ForkJoinPool.commonPool()`.

### 13. Чем плохо выполнять блокирующие операции в commonPool?

**Ответ:** этот пул общий для всего приложения, включая параллельные стримы, и
его размер привязан к числу ядер. Блокирующие задачи занимают его надолго и мешают
остальным.

### 14. Чем thenApply отличается от thenApplyAsync?

**Ответ:** первый не требует отдельного планирования и может выполниться в потоке,
завершившем предыдущий этап. Второй планирует продолжение как отдельную задачу в
executor.

### 15. Стоит ли ставить Async на каждый этап?

**Ответ:** нет. Каждое асинхронное продолжение стоит постановки в очередь и
выбора worker. Для быстрых преобразований это лишние накладные расходы.

### 16. Что возвращает allOf?

**Ответ:** `CompletableFuture<Void>`. Результаты он не собирает, их нужно забирать
у исходных futures отдельно.

### 17. Что возвращает anyOf?

**Ответ:** `CompletableFuture<Object>`, поскольку переданные futures могут иметь
разные типы.

### 18. Ждёт ли anyOf первый успешный future?

**Ответ:** нет, он ждёт первый завершившийся, включая завершившийся ошибкой.

### 19. Отменяет ли anyOf остальные futures?

**Ответ:** нет, они продолжают выполняться.

### 20. Что означает isDone?

**Ответ:** что future завершён любым способом — успешно, с ошибкой или отменой.

### 21. Прерывает ли cancel(true) выполняющееся вычисление?

**Ответ:** для `CompletableFuture` — нет. Параметр `mayInterruptIfRunning` здесь
не управляет потоком, и функция может продолжать работу.

### 22. Можно ли завершить CompletableFuture вручную?

**Ответ:** да, через `complete(value)` или `completeExceptionally(exception)`.
Первое успешное завершение определяет результат, последующие вызовы его не
заменяют.

---

## См. также

- [`03-locks-atomics-executors.md`](03-locks-atomics-executors.md) — `Future`,
  `ExecutorService` и семантика `cancel(true)`, которая здесь работает иначе
- [`06-virtual-threads.md`](06-virtual-threads.md) — почему это не
  взаимозаменяемые инструменты
- [`../java-core/08-functional-interfaces-lambda.md`](../java-core/08-functional-interfaces-lambda.md) —
  `Function`, `Supplier` и `BiFunction` в сигнатурах continuation-методов