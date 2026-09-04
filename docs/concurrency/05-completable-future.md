# CompletableFuture в Java

## 1. Зачем нужен CompletableFuture

Обычный `Future` позволяет запустить задачу в другом потоке и позднее получить её результат:

```java
Future<Integer> future = executor.submit(() -> calculate());

Integer result = future.get();
```

Проблема появляется, когда нужно построить последовательность зависимых асинхронных операций.

Например:

```text
получить пользователя
→ загрузить его заказы
→ посчитать сумму
→ вывести результат
```

С обычным `Future` код может выглядеть так:

```java
Future<User> userFuture =
        executor.submit(() -> loadUser());

User user = userFuture.get();

Future<List<Order>> ordersFuture =
        executor.submit(() -> loadOrders(user));

List<Order> orders = ordersFuture.get();

Future<Integer> totalFuture =
        executor.submit(() -> calculateTotal(orders));

Integer total = totalFuture.get();
```

Проблема:

```text
submit
→ get
→ submit
→ get
→ submit
→ get
```

Несмотря на использование асинхронных задач, вызывающий поток постоянно блокируется через `get()`.

`CompletableFuture` позволяет описать обработку как цепочку:

```text
асинхронная операция
→ преобразование результата
→ следующая операция
→ обработка результата
```

Например:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenApply(User::getName)
        .thenAccept(System.out::println);
```

---

# 2. runAsync и supplyAsync

Для запуска асинхронной операции существуют два основных метода.

## runAsync()

Используется, когда операция ничего не возвращает.

```java
CompletableFuture<Void> future =
        CompletableFuture.runAsync(() -> {
            sendNotification();
        });
```

`runAsync()` работает с `Runnable`.

Смысл:

```text
нет входного значения
→ выполнить действие
→ нет результата
```

Возвращается:

```java
CompletableFuture<Void>
```

---

## supplyAsync()

Используется, когда операция должна вернуть значение.

```java
CompletableFuture<User> future =
        CompletableFuture.supplyAsync(() -> loadUser());
```

`supplyAsync()` работает с `Supplier<T>`.

Смысл:

```text
нет входного значения
→ выполнить вычисление
→ получить T
```

Возвращается:

```java
CompletableFuture<T>
```

Кратко:

```text
runAsync()
→ Runnable
→ CompletableFuture<Void>

supplyAsync()
→ Supplier<T>
→ CompletableFuture<T>
```

---

# 3. thenApply

`thenApply()` используется, когда нужно преобразовать результат предыдущего этапа.

Например:

```java
CompletableFuture<User> userFuture =
        CompletableFuture.supplyAsync(() -> loadUser());

CompletableFuture<String> nameFuture =
        userFuture.thenApply(user -> user.getName());
```

Получается:

```text
CompletableFuture<User>
        ↓
thenApply
        ↓
CompletableFuture<String>
```

По смыслу:

```text
T → R
```

Например:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> 10)
                .thenApply(value -> value * 2);
```

Результат:

```text
20
```

`thenApply()` можно сравнить с обычным `map`.

---

# 4. thenAccept

`thenAccept()` получает результат предыдущего этапа, но ничего не возвращает.

Например:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenAccept(user -> {
            System.out.println(user.getName());
        });
```

По смыслу:

```text
T
↓
выполнить действие с T
↓
Void
```

Возвращается:

```java
CompletableFuture<Void>
```

Например:

```java
CompletableFuture
        .supplyAsync(() -> 42)
        .thenAccept(System.out::println);
```

---

# 5. thenRun

`thenRun()` выполняет действие после завершения предыдущего stage, но:

- не получает результат предыдущего этапа
- ничего не возвращает

Пример:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenRun(() -> {
            System.out.println("Операция завершена");
        });
```

Результат `loadUser()` здесь игнорируется.

Сравнение:

```text
thenApply()
→ получает значение
→ возвращает новое значение

thenAccept()
→ получает значение
→ ничего не возвращает

thenRun()
→ не получает значение
→ ничего не возвращает
```

Пример полной цепочки:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenApply(User::getName)
        .thenAccept(System.out::println)
        .thenRun(() -> System.out.println("Готово"));
```

---

# 6. thenApply и thenCompose

Это одно из самых важных различий в `CompletableFuture`.

Допустим:

```java
CompletableFuture<User> future =
        CompletableFuture.supplyAsync(() -> loadUser());
```

Есть обычный метод:

```java
String getUserName(User user);
```

Тогда подходит:

```java
future.thenApply(user -> getUserName(user));
```

Получается:

```text
CompletableFuture<User>
→ CompletableFuture<String>
```

---

Теперь допустим, следующий метод сам уже является асинхронным:

```java
CompletableFuture<List<Order>> loadOrders(User user);
```

Если использовать:

```java
future.thenApply(user -> loadOrders(user));
```

получится:

```text
CompletableFuture<
    CompletableFuture<List<Order>>
>
```

То есть вложенный `CompletableFuture`.

Для этого существует `thenCompose()`:

```java
CompletableFuture<List<Order>> ordersFuture =
        future.thenCompose(user -> loadOrders(user));
```

`thenCompose()` распрямляет вложенность.

По смыслу:

```text
thenApply:

T → R
↓
CompletableFuture<R>
```

```text
thenCompose:

T → CompletableFuture<R>
↓
CompletableFuture<R>
```

Удобная аналогия:

```text
thenApply   ≈ map
thenCompose ≈ flatMap
```

Главное правило:

```text
функция возвращает обычный R
→ thenApply()

функция возвращает CompletableFuture<R>
→ thenCompose()
```

Пример:

```java
CompletableFuture<List<Order>> result =
        CompletableFuture
                .supplyAsync(() -> loadUser())
                .thenCompose(user -> loadOrders(user));
```

---

# 7. thenCombine

`thenCombine()` используется, когда есть две независимые асинхронные операции, результаты которых нужно объединить.

Например:

```java
CompletableFuture<User> userFuture =
        CompletableFuture.supplyAsync(() -> loadUser());

CompletableFuture<Rate> rateFuture =
        CompletableFuture.supplyAsync(() -> loadRate());
```

Они могут выполняться независимо.

После завершения обеих:

```java
CompletableFuture<UserDto> result =
        userFuture.thenCombine(
                rateFuture,
                (user, rate) -> new UserDto(user, rate)
        );
```

Схема:

```text
User Future ──────┐
                  ├→ thenCombine → UserDto
Rate Future ──────┘
```

Разница:

```text
thenCompose()
→ B зависит от результата A

A
↓
B(A)
```

```text
thenCombine()
→ A и B независимы
→ могут выполняться параллельно

A ──┐
    ├→ combine
B ──┘
```

Пример для `thenCompose()`:

```text
получить User
→ взять user.id
→ загрузить Orders по user.id
```

Пример для `thenCombine()`:

```text
загрузить User
+
загрузить ExchangeRate
→ объединить в DTO
```

---

# 8. Ошибки в CompletableFuture

`CompletableFuture` может завершиться:

```text
успешно
или
exceptionally
```

Если stage завершается с ошибкой, последующие обычные преобразования результата обычно не выполняются, пока ошибка не будет обработана.

Например:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new IllegalStateException("boom");
                })
                .thenApply(value -> value * 2);
```

`thenApply()` не получает обычного результата.

Future завершается exceptionally.

---

# 9. exceptionally

`exceptionally()` используется для обработки ошибки и возврата fallback-значения.

Пример:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new IllegalStateException("boom");
                })
                .exceptionally(ex -> 0);
```

Если возникает ошибка:

```text
exception
↓
exceptionally()
↓
fallback = 0
```

После этого цепочка считается восстановленной.

Например:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new RuntimeException("boom");
                })
                .exceptionally(ex -> 10)
                .thenApply(value -> value * 2);
```

Получается:

```text
exception
↓
exceptionally → 10
↓
thenApply → 20
```

Итог:

```text
20
```

По смыслу:

```text
Throwable → T
```

`exceptionally()` вызывается только при ошибке.

---

# 10. handle

`handle()` выполняется:

- при успешном завершении
- при ошибке

Он получает два аргумента:

```java
(result, exception)
```

Например:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> calculate())
                .handle((result, ex) -> {
                    if (ex != null) {
                        return 0;
                    }

                    return result * 2;
                });
```

При успешном результате:

```text
result = значение
ex = null
```

При ошибке:

```text
result = null
ex = exception
```

`handle()` способен вернуть новое значение.

Например:

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

Получается:

```text
10
→ handle → 15
→ thenApply → 30
```

---

# 11. whenComplete

`whenComplete()` тоже вызывается как при успехе, так и при ошибке.

Но обычно он используется для side effects:

```text
логирование
метрики
cleanup
```

Например:

```java
future.whenComplete((result, ex) -> {
    if (ex != null) {
        log.error("Ошибка", ex);
    } else {
        log.info("Результат: {}", result);
    }
});
```

В отличие от `handle()`, `whenComplete()` обычно не используется для преобразования результата.

Например:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> 10)
                .whenComplete((result, ex) -> {
                    System.out.println("result = " + result);
                })
                .thenApply(value -> value * 2);
```

Вывод:

```text
result = 10
```

Итоговый результат:

```text
20
```

---

Если предыдущий stage упал:

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new RuntimeException("boom");
                })
                .whenComplete((result, ex) -> {
                    System.out.println("finished");
                })
                .exceptionally(ex -> 5)
                .thenApply(value -> value * 2);
```

Произойдёт:

```text
exception
↓
whenComplete
→ finished
↓
ошибка продолжает идти дальше
↓
exceptionally
→ 5
↓
thenApply
→ 10
```

`whenComplete()` сам по себе ошибку не поглощает.

---

# 12. exceptionally, handle и whenComplete

Краткое сравнение:

```text
exceptionally()
→ вызывается только при ошибке
→ обычно возвращает fallback

handle()
→ вызывается при успехе и ошибке
→ может преобразовать результат

whenComplete()
→ вызывается при успехе и ошибке
→ обычно выполняет side effect
→ исходный результат или ошибка продолжают цепочку
```

---

# 13. get и join

Результат `CompletableFuture` можно получить через:

```java
future.get();
```

или:

```java
future.join();
```

Оба метода могут ждать завершения future.

---

## get()

`get()` наследуется от `Future`.

```java
T result = future.get();
```

Он работает с checked exceptions:

```text
InterruptedException
ExecutionException
```

Пример:

```java
try {
    Integer result = future.get();
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
} catch (ExecutionException e) {
    System.out.println(e.getCause());
}
```

Если async-операция бросила:

```java
throw new IllegalStateException("boom");
```

`get()` бросит:

```text
ExecutionException
```

а исходная ошибка будет доступна через:

```java
e.getCause()
```

---

## join()

`join()` не требует обработки checked exceptions:

```java
T result = future.join();
```

Если future завершился exceptionally, обычно выбрасывается:

```text
CompletionException
```

Исходная ошибка находится в:

```java
e.getCause()
```

Например:

```java
try {
    future.join();
} catch (CompletionException e) {
    System.out.println(e.getCause());
}
```

Сравнение:

```text
get()
→ ExecutionException
→ InterruptedException
→ checked exceptions

join()
→ CompletionException
→ unchecked exception
```

Поэтому внутри кода с `CompletableFuture` часто используется `join()`.

Например:

```java
List<User> users = futures.stream()
        .map(CompletableFuture::join)
        .toList();
```

---

# 14. Executor по умолчанию

Если написать:

```java
CompletableFuture.supplyAsync(() -> loadUser());
```

без передачи своего `Executor`, асинхронная задача обычно будет выполняться через:

```text
ForkJoinPool.commonPool()
```

То же касается большинства `*Async` методов без явно указанного executor.

Например:

```java
.thenApplyAsync(value -> process(value))
```

обычно использует default async execution facility, которой обычно является:

```text
ForkJoinPool.commonPool()
```

---

# 15. Свой Executor

Можно явно передать executor:

```java
ExecutorService executor =
        Executors.newFixedThreadPool(4);

CompletableFuture<User> future =
        CompletableFuture.supplyAsync(
                () -> loadUser(),
                executor
        );
```

Можно передать executor и continuation:

```java
future.thenApplyAsync(
        user -> process(user),
        executor
);
```

Это позволяет контролировать, где именно выполняются задачи.

Для долгих или блокирующих операций часто разумнее использовать отдельный executor, а не нагружать общий `ForkJoinPool.commonPool()`.

---

# 16. thenApply и thenApplyAsync

Это важное различие.

Обычный:

```java
thenApply(...)
```

не требует обязательного отдельного scheduling через executor.

Если предыдущий stage завершается и continuation уже зарегистрирован, continuation может выполнить поток, который завершил предыдущий stage.

Например:

```java
CompletableFuture
        .supplyAsync(() -> 10)
        .thenApply(value -> value * 2);
```

Один worker может выполнить:

```text
supplyAsync
↓
thenApply
```

Но нельзя утверждать, что `thenApply()` всегда выполняется именно в том же потоке.

Если future уже завершён к моменту присоединения continuation:

```java
CompletableFuture<Integer> future =
        CompletableFuture.completedFuture(10);

future.thenApply(value -> {
    System.out.println(Thread.currentThread().getName());
    return value * 2;
});
```

continuation может выполнить поток, который вызывает `thenApply()`.

Главное правило:

```text
thenApply()
→ отдельное async scheduling не требуется
```

---

`thenApplyAsync()`:

```java
future.thenApplyAsync(value -> value * 2);
```

планирует continuation как async-задачу.

Без executor обычно используется:

```text
ForkJoinPool.commonPool()
```

Со своим executor:

```java
future.thenApplyAsync(
        value -> value * 2,
        executor
);
```

будет использован указанный executor.

---

# 17. Async-варианты методов

Подобные пары существуют для многих операций:

```text
thenApply()
thenApplyAsync()

thenAccept()
thenAcceptAsync()

thenRun()
thenRunAsync()

thenCompose()
thenComposeAsync()

thenCombine()
thenCombineAsync()
```

Упрощённо:

```text
без Async
→ отдельное переключение в executor не обязательно

с Async
→ continuation отдельно планируется через executor
```

Если написать:

```java
thenApplyAsync(fn)
```

обычно используется:

```text
ForkJoinPool.commonPool()
```

Если:

```java
thenApplyAsync(fn, executor)
```

используется переданный executor.

---

# 18. Почему Async не нужно использовать везде

Не стоит автоматически писать:

```java
supplyAsync(...)
        .thenApplyAsync(...)
        .thenApplyAsync(...)
        .thenAcceptAsync(...)
```

Каждый async-stage требует дополнительного scheduling.

У этого есть стоимость:

```text
постановка задачи
→ очередь executor
→ выбор worker
→ выполнение
```

Если после асинхронной операции нужно выполнить небольшое быстрое преобразование:

```java
CompletableFuture
        .supplyAsync(() -> loadUser())
        .thenApply(User::getName)
        .thenApply(String::toUpperCase);
```

обычных continuation часто достаточно.

Если работу нужно сознательно отправить в другой executor:

```java
.thenApplyAsync(
        this::heavyCalculation,
        cpuExecutor
)
```

тогда Async имеет смысл.

---

# 19. allOf

`CompletableFuture.allOf()` используется, когда нужно дождаться завершения нескольких futures.

Например:

```java
CompletableFuture<User> userFuture =
        CompletableFuture.supplyAsync(() -> loadUser());

CompletableFuture<List<Order>> ordersFuture =
        CompletableFuture.supplyAsync(() -> loadOrders());

CompletableFuture<Balance> balanceFuture =
        CompletableFuture.supplyAsync(() -> loadBalance());
```

Можно создать:

```java
CompletableFuture<Void> all =
        CompletableFuture.allOf(
                userFuture,
                ordersFuture,
                balanceFuture
        );
```

Тип результата:

```java
CompletableFuture<Void>
```

`allOf()` сам не собирает результаты futures в список или DTO.

Он сообщает, что все переданные futures завершены.

Можно:

```java
all.join();
```

а затем получить результаты:

```java
User user = userFuture.join();
List<Order> orders = ordersFuture.join();
Balance balance = balanceFuture.join();
```

---

# 20. allOf со списком futures

Например:

```java
List<CompletableFuture<User>> futures =
        ids.stream()
                .map(id ->
                        CompletableFuture.supplyAsync(
                                () -> loadUser(id)
                        )
                )
                .toList();
```

Дождаться всех:

```java
CompletableFuture.allOf(
        futures.toArray(new CompletableFuture[0])
).join();
```

Затем собрать:

```java
List<User> users =
        futures.stream()
                .map(CompletableFuture::join)
                .toList();
```

Схема:

```text
Future 1 ─┐
Future 2 ─┤
Future 3 ─┤
...       ├→ allOf
Future N ─┘
            ↓
       все завершены
            ↓
     собрать результаты
```

Если один или несколько futures завершаются exceptionally, результат `allOf()` также будет exceptional после завершения требуемой группы futures.

---

# 21. anyOf

`anyOf()` используется, когда нужен первый завершившийся future.

Например:

```java
CompletableFuture<String> server1 =
        CompletableFuture.supplyAsync(() -> requestServer1());

CompletableFuture<String> server2 =
        CompletableFuture.supplyAsync(() -> requestServer2());

CompletableFuture<String> server3 =
        CompletableFuture.supplyAsync(() -> requestServer3());
```

Можно:

```java
CompletableFuture<Object> first =
        CompletableFuture.anyOf(
                server1,
                server2,
                server3
        );
```

Тип:

```java
CompletableFuture<Object>
```

Потому что переданные futures могут иметь разные типы.

Например:

```text
server1 → 3 сек
server2 → 1 сек
server3 → 2 сек
```

`anyOf()` завершится примерно через одну секунду результатом `server2`.

---

# 22. anyOf не отменяет остальные futures

Важно:

```java
CompletableFuture.anyOf(f1, f2, f3)
```

не означает:

```text
получить первый результат
→ автоматически отменить остальные
```

Например:

```text
f1 → 3 секунды
f2 → 1 секунда
f3 → 2 секунды
```

Через одну секунду:

```text
f2 → completed
anyOf → completed
```

Но:

```text
f1 → продолжает работать
f3 → продолжает работать
```

---

# 23. anyOf и ошибки

`anyOf()` ждёт первый **завершившийся** future, а не обязательно первый успешно завершившийся.

Например:

```text
f1 → 3 сек → success
f2 → 1 сек → exception
f3 → 2 сек → success
```

Тогда первым завершится `f2`.

`anyOf()` завершится exceptionally.

Вызов:

```java
CompletableFuture.anyOf(f1, f2, f3).join();
```

может бросить:

```text
CompletionException
```

Он не будет ждать успешный результат `f3`.

При этом `f1` и `f3` сами автоматически не отменяются.

---

# 24. allOf и anyOf

Кратко:

```text
allOf()
→ дождаться всех futures
→ CompletableFuture<Void>

anyOf()
→ дождаться первого завершившегося future
→ CompletableFuture<Object>
```

---

# 25. cancel

`CompletableFuture` можно отменить:

```java
future.cancel(true);
```

Если future ещё не завершён, он переходит в cancelled state.

После успешной отмены:

```java
future.isDone();       // true
future.isCancelled();  // true
```

Попытка получить результат приводит к отмене:

```java
future.join();
```

может завершиться `CancellationException`.

---

# 26. cancel(true) и interrupt

Здесь есть важное отличие от некоторых обычных реализаций `Future`.

У `CompletableFuture`:

```java
future.cancel(true);
```

не гарантирует отправку `interrupt()` потоку, выполняющему underlying computation.

Параметр `mayInterruptIfRunning` не используется как механизм управления выполняющим вычисление потоком.

Поэтому:

```java
CompletableFuture<Integer> future =
        CompletableFuture.supplyAsync(() -> {
            expensiveOperation();
            return 42;
        });

future.cancel(true);
```

означает прежде всего:

```text
CompletableFuture
→ считается отменённым
```

но:

```text
expensiveOperation()
```

может продолжать выполняться.

Не следует автоматически переносить сюда модель:

```text
FutureTask.cancel(true)
→ обязательно остановить worker
```

Остановка underlying computation требует отдельной корректно спроектированной кооперативной логики.

---

# 27. Состояния CompletableFuture

Полезные методы:

```java
future.isDone();
future.isCancelled();
future.isCompletedExceptionally();
```

---

## Успешное завершение

```text
isDone()                   = true
isCancelled()              = false
isCompletedExceptionally() = false
```

---

## Завершение с ошибкой

```text
isDone()                   = true
isCancelled()              = false
isCompletedExceptionally() = true
```

---

## Отмена

```text
isDone()                   = true
isCancelled()              = true
isCompletedExceptionally() = true
```

Таким образом:

```java
future.isDone();
```

означает не:

```text
задача успешно выполнена
```

а:

```text
future больше не находится в незавершённом состоянии
```

---

# 28. Ручное завершение CompletableFuture

`CompletableFuture` можно создать без начального вычисления:

```java
CompletableFuture<String> future =
        new CompletableFuture<>();
```

Сначала:

```java
future.isDone(); // false
```

Можно вручную завершить его:

```java
future.complete("OK");
```

После этого:

```java
future.join(); // "OK"
```

---

# 29. complete

Метод:

```java
future.complete(value);
```

пытается успешно завершить future указанным значением.

Он возвращает `boolean`.

Например:

```java
CompletableFuture<Integer> future =
        new CompletableFuture<>();

boolean first = future.complete(42);
boolean second = future.complete(100);
```

Получится:

```text
first  = true
second = false
```

Потому что первое завершение уже определило результат:

```java
future.join(); // 42
```

---

# 30. completeExceptionally

Можно вручную завершить future ошибкой:

```java
CompletableFuture<Integer> future =
        new CompletableFuture<>();

future.completeExceptionally(
        new IllegalStateException("DB unavailable")
);
```

После этого:

```java
future.isDone();                   // true
future.isCompletedExceptionally(); // true
```

А получение результата приведёт к exceptional completion.

---

# 31. Первое завершение побеждает

Если:

```java
CompletableFuture<Integer> future =
        new CompletableFuture<>();

boolean first =
        future.complete(10);

boolean second =
        future.completeExceptionally(
                new RuntimeException("boom")
        );
```

то:

```text
first = true
second = false
```

А:

```java
future.join();
```

вернёт:

```text
10
```

Потому что первый успешный вызов завершения определяет состояние future.

Последующие обычные:

```text
complete()
completeExceptionally()
cancel()
```

не могут просто заменить уже установленный результат.

---

# 32. Типичная асинхронная цепочка

Например:

```java
CompletableFuture<UserDto> result =
        CompletableFuture
                .supplyAsync(
                        () -> loadUser(),
                        ioExecutor
                )
                .thenCompose(
                        user -> loadOrdersAsync(user)
                )
                .thenApply(
                        orders -> calculateStatistics(orders)
                )
                .thenApply(
                        stats -> new UserDto(stats)
                )
                .whenComplete(
                        (dto, ex) -> logResult(dto, ex)
                )
                .exceptionally(
                        ex -> fallbackDto()
                );
```

Смысл:

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

# 33. Когда использовать какой continuation

Шпаргалка:

```text
thenApply()
→ T → R
→ преобразовать значение

thenAccept()
→ T → void
→ использовать значение без результата

thenRun()
→ () → void
→ выполнить действие после завершения

thenCompose()
→ T → CompletableFuture<R>
→ зависимая асинхронная операция

thenCombine()
→ объединить результаты двух независимых futures
```

---

# 34. Обработка ошибок

```text
exceptionally()
→ только exception
→ fallback

handle()
→ success или exception
→ преобразование результата

whenComplete()
→ success или exception
→ side effect
```

---

# 35. Получение результата

```text
get()
→ блокирующее ожидание
→ checked exceptions
→ ExecutionException
→ InterruptedException

join()
→ блокирующее ожидание
→ unchecked CompletionException
```

---

# 36. Управление несколькими futures

```text
allOf()
→ дождаться всех

anyOf()
→ дождаться первого завершившегося
```

При этом:

```text
anyOf()
≠ автоматически отменить остальные
```

---

# 37. Типичные ошибки

## Ошибка 1. Использовать thenApply вместо thenCompose

Плохо:

```java
future.thenApply(user -> loadOrdersAsync(user));
```

если `loadOrdersAsync()` возвращает:

```java
CompletableFuture<List<Order>>
```

Тогда получается:

```text
CompletableFuture<CompletableFuture<List<Order>>>
```

Лучше:

```java
future.thenCompose(user -> loadOrdersAsync(user));
```

---

## Ошибка 2. Путать thenCompose и thenCombine

`thenCompose()`:

```text
B зависит от A
```

`thenCombine()`:

```text
A и B независимы
→ объединить результаты
```

---

## Ошибка 3. Использовать Async для каждого stage без причины

```java
supplyAsync(...)
        .thenApplyAsync(...)
        .thenApplyAsync(...)
        .thenAcceptAsync(...)
```

может создавать ненужное дополнительное scheduling.

Для небольших синхронных преобразований часто достаточно:

```java
thenApply()
```

---

## Ошибка 4. Бездумно использовать commonPool

```java
CompletableFuture.supplyAsync(...)
```

и:

```java
thenApplyAsync(...)
```

без executor обычно используют общий async executor.

Долгие или блокирующие операции могут негативно влиять на другие задачи, использующие тот же pool.

В таких сценариях имеет смысл передавать свой:

```java
ExecutorService executor = ...
```

---

## Ошибка 5. Считать whenComplete обработчиком ошибки

```java
.whenComplete((result, ex) -> log(...))
```

не означает, что ошибка восстановлена.

Exception продолжает цепочку.

Для fallback нужен, например:

```java
.exceptionally(ex -> fallback)
```

---

## Ошибка 6. Считать anyOf ожиданием первого успешного результата

`anyOf()` завершается по первому завершившемуся future.

Если он завершился exceptionally:

```text
anyOf
→ тоже exceptional
```

---

## Ошибка 7. Считать, что anyOf отменяет остальные задачи

Не отменяет.

После завершения одного future остальные могут продолжить работу.

---

## Ошибка 8. Считать cancel(true) гарантированным interrupt underlying computation

Для `CompletableFuture` это неверно.

Отмена future и остановка выполняющейся функции — не одно и то же.

---

# 38. Типичные вопросы на собеседовании

## Чем Future отличается от CompletableFuture?

`Future` в основном представляет результат асинхронной операции и предоставляет методы вроде `get()` и `cancel()`.

`CompletableFuture` дополнительно позволяет строить цепочки вычислений, комбинировать futures, обрабатывать ошибки и вручную завершать future.

---

## Чем runAsync отличается от supplyAsync?

```text
runAsync()
→ Runnable
→ результата нет
→ CompletableFuture<Void>

supplyAsync()
→ Supplier<T>
→ есть результат
→ CompletableFuture<T>
```

---

## Чем thenApply отличается от thenAccept?

```text
thenApply
→ получает T
→ возвращает R

thenAccept
→ получает T
→ ничего не возвращает
```

---

## Чем thenAccept отличается от thenRun?

```text
thenAccept
→ получает результат предыдущего этапа

thenRun
→ результат предыдущего этапа не получает
```

Оба обычно возвращают:

```text
CompletableFuture<Void>
```

---

## Чем thenApply отличается от thenCompose?

```text
thenApply:
T → R

thenCompose:
T → CompletableFuture<R>
```

`thenCompose()` используется для dependent async operation и убирает вложенный `CompletableFuture`.

---

## Чем thenCompose отличается от thenCombine?

```text
thenCompose
→ B зависит от результата A

thenCombine
→ A и B независимы
→ ждём оба
→ объединяем результаты
```

---

## Чем exceptionally отличается от handle?

```text
exceptionally
→ только ошибка

handle
→ успех и ошибка
```

---

## Чем handle отличается от whenComplete?

`handle()` может преобразовать результат и вернуть другое значение.

`whenComplete()` чаще используется для side effects и обычно сохраняет исходный результат или ошибку.

---

## Чем get отличается от join?

```text
get
→ ExecutionException
→ InterruptedException
→ checked

join
→ CompletionException
→ unchecked
```

---

## Какой executor используется supplyAsync без executor?

Обычно:

```text
ForkJoinPool.commonPool()
```

---

## Чем thenApply отличается от thenApplyAsync?

```text
thenApply
→ отдельное async scheduling не обязательно

thenApplyAsync
→ continuation планируется через async executor
```

---

## Что возвращает allOf?

```java
CompletableFuture<Void>
```

Он не собирает результаты futures автоматически.

---

## Что возвращает anyOf?

```java
CompletableFuture<Object>
```

---

## Отменяет ли anyOf остальные futures?

Нет.

---

## Ждёт ли anyOf первый успешный future?

Нет.

Он ждёт первый завершившийся future, включая exceptional completion.

---

## Что означает isDone?

Future уже завершён:

```text
успешно
или
с ошибкой
или
отменён
```

---

## Можно ли завершить CompletableFuture вручную?

Да:

```java
complete(value)
```

или:

```java
completeExceptionally(exception)
```

---

# 39. Итоговая шпаргалка

```text
Создание:

runAsync()
→ async Runnable
→ CompletableFuture<Void>

supplyAsync()
→ async Supplier<T>
→ CompletableFuture<T>


Continuation:

thenApply()
→ T → R

thenAccept()
→ T → void

thenRun()
→ () → void

thenCompose()
→ T → CompletableFuture<R>

thenCombine()
→ Future<A> + Future<B> → Future<R>


Ошибки:

exceptionally()
→ exception → fallback

handle()
→ result + exception → новый результат

whenComplete()
→ result + exception → side effect


Получение:

get()
→ ExecutionException
→ InterruptedException
→ checked

join()
→ CompletionException
→ unchecked


Несколько futures:

allOf()
→ ждать всех
→ CompletableFuture<Void>

anyOf()
→ ждать первого завершившегося
→ CompletableFuture<Object>


Executor:

*Async без Executor
→ обычно ForkJoinPool.commonPool()

*Async с Executor
→ указанный executor


Состояния:

isDone()
→ завершён любым способом

isCancelled()
→ отменён

isCompletedExceptionally()
→ завершён exceptionally


Ручное завершение:

complete(value)
completeExceptionally(exception)

→ первое успешное завершение определяет результат
```

# 40. Главное

`CompletableFuture` нужен не просто для запуска работы в другом потоке.

Его основное преимущество — возможность декларативно описывать асинхронный pipeline:

```text
запустить операцию
→ преобразовать результат
→ запустить зависимую операцию
→ объединить независимые результаты
→ обработать ошибку
→ выполнить финальное действие
```

При этом важно понимать три вещи:

```text
1. thenApply и thenCompose решают разные задачи

2. async-цепочка не означает, что нужно везде использовать методы с суффиксом Async

3. CompletableFuture управляет состоянием асинхронного вычисления, но не гарантирует автоматическую остановку underlying computation при cancel()
```

---

## См. также

- [`03-locks-atomics-executors.md`](03-locks-atomics-executors.md) — `Future`,
  `ExecutorService` и семантика `cancel(true)`, которая здесь работает иначе
- [`06-virtual-threads.md`](06-virtual-threads.md) — почему это не
  взаимозаменяемые инструменты
- [`../java-core/08-functional-interfaces-lambda.md`](../java-core/08-functional-interfaces-lambda.md) —
  `Function`, `Supplier` и `BiFunction` в сигнатурах continuation-методов