# Java Backend Interview Preparation Roadmap

Полный roadmap подготовки к техническим интервью на позиции Java Backend Developer.

Roadmap ориентирован не на изучение Java вообще, а на подготовку к Junior /
Junior+ Java Backend интервью. Он объединяет Java Core, JVM, Concurrency, Spring,
базы данных, JPA/Hibernate, Kafka, Testing, инфраструктуру и архитектуру.

## Статусы

- `Не начато`
- `В процессе`
- `Изучено`
- `Отложено` — тема сознательно исключена из ближайшей подготовки

## Принцип приоритизации

Порядок изучения определяется не логикой языка, а тем, что реально спрашивают на
Junior / Junior+ собеседовании. Spring, SQL и Hibernate занимают на таком
интервью больше места, чем остаток Java Core, поэтому Java Core закрывается
выборочно, а не целиком.

Темы со статусом `Отложено` не выброшены. Они прочитываются перед собеседованием
обзорно, но конспект по ним не пишется, пока не закрыты приоритетные блоки.

---

# 1. Java Core

## 1.1. Java Language Basics — Изучено

- [x] primitive types
- [x] reference types
- [x] variables
- [x] scopes
- [x] default values
- [x] operators
- [x] control flow
- [x] arrays
- [x] multidimensional arrays
- [x] type casting
- [x] widening conversion
- [x] narrowing conversion
- [x] Java pass-by-value
- [x] передача primitive в метод
- [x] передача object reference в метод
- [x] varargs
- [x] packages
- [x] imports
- [x] access modifiers

---

## 1.2. OOP — Изучено

- [x] class и object
- [x] encapsulation
- [x] inheritance
- [x] polymorphism
- [x] abstraction
- [x] interface
- [x] abstract class
- [x] interface vs abstract class
- [x] overriding
- [x] overloading
- [x] static binding
- [x] dynamic binding
- [x] `this`
- [x] `super`
- [x] `final`
- [x] `static`
- [x] composition vs inheritance
- [x] можно ли override `static`
- [x] можно ли override `private`
- [x] covariant return type

---

## 1.3. Object, String и Wrappers — Изучено

### Object

- [x] `toString`
- [x] `equals`
- [x] `hashCode`
- [x] `getClass`
- [x] runtime type объекта
- [ ] `clone` на концептуальном уровне

### String

- [x] String immutability
- [x] String Pool
- [x] string literals
- [x] `new String(...)`
- [x] `intern`
- [x] concatenation
- [x] `StringBuilder`
- [x] `StringBuffer`
- [x] `StringBuilder` vs `StringBuffer`
- [x] почему `String` immutable

### Primitive Types и Wrappers

- [x] primitives vs wrappers
- [x] boxing
- [x] unboxing
- [x] autoboxing
- [x] Integer cache
- [x] wrapper equality
- [x] `==` vs `equals`
- [x] numeric overflow
- [x] `null` + unboxing
- [x] `Number`

---

## 1.4. Collections Framework — Изучено

- [x] иерархия `Collection`
- [x] `List`
- [x] `Set`
- [x] `Queue`
- [x] `Deque`
- [x] `ArrayList`
- [x] `LinkedList`
- [x] `HashSet`
- [x] `LinkedHashSet`
- [x] `TreeSet`
- [x] `ArrayDeque`
- [x] `PriorityQueue`
- [x] FIFO / LIFO
- [x] `peek` / `element`
- [x] `poll` / `remove`
- [x] основные сложности операций
- [x] `Comparable` vs `Comparator`
- [x] `Iterator`
- [x] `ListIterator`
- [x] fail-fast iterator
- [x] `ConcurrentModificationException`
- [x] immutable collections
- [x] unmodifiable collections
- [x] `List.of`
- [x] `Set.of`
- [x] `Map.of`

---

## 1.5. Map и реализации — Изучено

- [x] `Map`
- [x] `HashMap`
- [x] `LinkedHashMap`
- [x] `TreeMap`
- [x] hashing
- [x] bucket
- [x] collisions
- [x] связь `equals` и `hashCode`
- [x] `put`
- [x] `get`
- [x] `computeIfAbsent`
- [x] различия реализаций
- [x] treeification bucket
- [x] resize и load factor

---

## 1.6. equals и hashCode — Изучено

- [x] контракт `equals`
- [x] контракт `hashCode`
- [x] связь `equals` и `hashCode`
- [x] `==` vs `equals`
- [x] mutable key в `HashMap`

---

## 1.7. Generics — Изучено

- [x] generic classes
- [x] generic methods
- [x] bounds
- [x] wildcard `?`
- [x] `? extends`
- [x] `? super`
- [x] PECS
- [x] invariance
- [x] type erasure
- [x] raw types
- [ ] heap pollution
- [ ] ограничения `new T()`
- [ ] generic arrays

---

## 1.8. Exceptions — Изучено

- [x] checked exceptions
- [x] unchecked exceptions
- [x] `Error`
- [x] `try/catch/finally`
- [x] propagation
- [x] custom exceptions
- [x] try-with-resources
- [x] `AutoCloseable`
- [x] suppressed exceptions
- [x] multi-catch

---

## 1.9. Functional Interfaces и Lambda — Изучено

- [x] lambda expressions
- [x] method references
- [x] functional interface
- [x] `@FunctionalInterface`
- [x] `Predicate`
- [x] `Function`
- [x] `Consumer`
- [x] `Supplier`
- [x] `UnaryOperator`
- [x] `BinaryOperator`
- [x] effectively final
- [x] closure
- [x] capture by value vs capture by reference
- [x] lambda vs anonymous class
- [x] target typing
- [x] примитивные специализации
- [x] функциональные интерфейсы вне `java.util.function`
- [x] `invokedynamic` и `LambdaMetafactory` на концептуальном уровне

---

## 1.10. Stream API — Изучено

- [x] intermediate operations
- [x] terminal operations
- [x] lazy evaluation
- [x] `map`
- [x] `filter`
- [x] `flatMap`
- [x] `reduce`
- [x] `collect`
- [x] `groupingBy`
- [x] `partitioningBy`
- [x] `toMap`
- [x] side effects
- [x] stream reuse
- [x] parallel streams
- [x] ограничения parallel streams
- [ ] primitive streams и `IntStream` — дописать разделом в существующий конспект

---

## 1.11. Optional — Изучено

- [x] `Optional.of`
- [x] `Optional.ofNullable`
- [x] `Optional.empty`
- [x] `map`
- [x] `flatMap`
- [x] `filter`
- [x] `orElse`
- [x] `orElseGet`
- [x] `orElseThrow`
- [x] `ifPresent`
- [x] `ifPresentOrElse`
- [x] `orElse` vs `orElseGet`
- [x] где `Optional` использовать не стоит
- [x] `Optional` как поле сущности и как параметр метода

---

## 1.12. Modern Java — Изучено

### Enum

- [x] enum как класс
- [x] поля и методы enum
- [x] constructor
- [x] `values`
- [x] `valueOf`
- [x] enum в `switch`
- [x] `EnumSet`
- [x] `EnumMap`

### Record

- [x] record syntax
- [x] generated members
- [x] final components
- [x] accessors
- [x] `equals`
- [x] `hashCode`
- [x] `toString`
- [x] compact constructor
- [x] сценарии применения
- [x] ограничения

### Sealed Classes

- [x] `sealed`
- [x] `permits`
- [x] `non-sealed`
- [x] sealed hierarchy

---

## 1.13. Annotations — Не начато

Нужны как фундамент под Spring: без `RetentionPolicy.RUNTIME` и базовой рефлексии
не объяснить, как работает `@Transactional`.

- [ ] что такое annotation
- [ ] built-in annotations
- [ ] `@Override`
- [ ] `@Deprecated`
- [ ] `@SuppressWarnings`
- [ ] `@FunctionalInterface`
- [ ] custom annotations
- [ ] `@Target`
- [ ] `@Retention`
- [ ] `RetentionPolicy`
- [ ] `@Inherited`
- [ ] reflection + annotations на базовом уровне

---

## 1.14. Nested Classes — Изучено частично

Анонимные классы разобраны в конспекте по лямбдам, остальное дописывается туда же
отдельным разделом.

- [x] anonymous class
- [x] anonymous class vs lambda
- [ ] static nested class
- [ ] inner class
- [ ] local class
- [ ] доступ к outer instance
- [ ] static nested vs inner class

---

## 1.15. Date and Time API — Отложено

Конспект не пишется. Перед собеседованием прочитать обзорно.

- [ ] `LocalDate`
- [ ] `LocalTime`
- [ ] `LocalDateTime`
- [ ] `Instant`
- [ ] `ZonedDateTime`
- [ ] `ZoneId`
- [ ] `Duration`
- [ ] `Period`
- [ ] `DateTimeFormatter`
- [ ] `LocalDateTime` vs `Instant`
- [ ] `Instant` vs `ZonedDateTime`
- [ ] timezone basics

---

## 1.16. Java I/O и NIO — Отложено

Для backend-интервью спрашивают редко. Конспект не пишется.

### I/O

- [ ] byte streams
- [ ] character streams
- [ ] `InputStream`
- [ ] `OutputStream`
- [ ] `Reader`
- [ ] `Writer`
- [ ] buffering
- [ ] `BufferedReader`
- [ ] `BufferedWriter`

### Files / NIO

- [ ] `Path`
- [ ] `Paths`
- [ ] `Files`
- [ ] чтение и запись файла
- [ ] `Files.lines`
- [ ] blocking I/O vs non-blocking I/O на концептуальном уровне

---

# 2. JVM

## 2.1. Runtime Data Areas — Изучено

- [x] Heap
- [x] Stack
- [x] Stack Frame
- [x] Operand Stack
- [x] Method Area
- [x] Metaspace
- [x] PC Register
- [x] Native Method Stack
- [x] `StackOverflowError`
- [x] `OutOfMemoryError`

---

## 2.2. Class Loading — Изучено

Разобрано в конспекте по памяти JVM.

- [x] Loading
- [x] Linking
- [x] Verification
- [x] Preparation
- [x] Resolution
- [x] Initialization
- [x] Bootstrap ClassLoader
- [x] Platform ClassLoader
- [x] Application ClassLoader
- [x] Parent Delegation Model
- [x] когда выполняется static initialization

---

## 2.3. Garbage Collection — Не начато

- [ ] что такое GC
- [ ] GC Roots
- [ ] reachability
- [ ] young generation
- [ ] old generation
- [ ] allocation
- [ ] promotion
- [ ] minor GC
- [ ] major GC
- [ ] full GC
- [ ] Stop-The-World
- [ ] generational hypothesis
- [ ] G1
- [ ] ZGC basics
- [ ] memory leaks в Java

---

## 2.4. Reference Types — Не начато

Пишется вместе с Garbage Collection одним конспектом.

- [ ] strong reference
- [ ] soft reference
- [ ] weak reference
- [ ] phantom reference
- [ ] `ReferenceQueue`
- [ ] `WeakHashMap`

---

## 2.5. Bytecode и JIT — Изучено

Разобрано в конспекте по памяти JVM на нужном для интервью уровне.

- [x] `.java`
- [x] `javac`
- [x] `.class`
- [x] bytecode
- [x] interpreter
- [x] JIT compiler
- [x] HotSpot
- [x] прогрев JVM
- [x] why Java is compiled and interpreted

---

# 3. Java Concurrency

## 3.1. Java Memory Model — Изучено

- [x] visibility
- [x] atomicity
- [x] ordering
- [x] reordering
- [x] as-if-serial
- [x] happens-before
- [x] `volatile`
- [x] `synchronized`
- [x] safe publication
- [x] final-field guarantees
- [x] data race vs race condition

---

## 3.2. Multithreading — Изучено

### Thread Basics

- [x] `Thread`
- [x] `start` vs `run`
- [x] thread states
- [x] `sleep`
- [x] `join`
- [x] interruption

### Synchronization

- [x] `synchronized`
- [x] monitor
- [x] `wait`
- [x] `notify`
- [x] `notifyAll`
- [x] deadlock
- [x] livelock
- [x] starvation

---

## 3.3. Locks, Atomics и Executors — Изучено

- [x] `ReentrantLock`
- [x] `tryLock`
- [x] `lockInterruptibly`
- [x] `Condition`
- [x] Atomic classes
- [x] CAS
- [x] ABA problem
- [x] `ExecutorService`
- [x] `Future`
- [x] `ThreadPoolExecutor`
- [x] rejection policies
- [x] CPU-bound и I/O-bound pools

---

## 3.4. Concurrent Collections — Изучено

- [x] `ConcurrentHashMap`
- [x] `Collections.synchronizedMap`
- [x] `CopyOnWriteArrayList`
- [x] `BlockingQueue`
- [x] `ArrayBlockingQueue`
- [x] `LinkedBlockingQueue`
- [x] `SynchronousQueue`
- [x] `ConcurrentLinkedQueue`
- [x] weakly consistent iterator vs snapshot iterator

---

## 3.5. CompletableFuture — Изучено

- [x] `runAsync`
- [x] `supplyAsync`
- [x] `thenApply`
- [x] `thenAccept`
- [x] `thenRun`
- [x] `thenCompose`
- [x] `thenCombine`
- [x] `exceptionally`
- [x] `handle`
- [x] `whenComplete`
- [x] `allOf`
- [x] `anyOf`
- [x] `get`
- [x] `join`
- [x] cancellation semantics

---

## 3.6. Virtual Threads — Изучено

- [x] platform vs virtual threads
- [x] carrier threads
- [x] mount / unmount
- [x] I/O-bound vs CPU-bound
- [x] `Thread.startVirtualThread`
- [x] `Thread.ofVirtual`
- [x] `newVirtualThreadPerTaskExecutor`
- [x] resource limiting through `Semaphore`
- [x] DB connection pool interaction
- [x] pinning in Java 21
- [x] `ThreadLocal`
- [x] daemon lifecycle
- [x] cancellation and interruption

---

## 3.7. Structured Concurrency и Scoped Values — Отложено

Выходит за рамки Junior / Junior+ интервью.

- [ ] Structured Concurrency
- [ ] Scoped Values

---

# 4. HTTP и REST — Не начато

## 4.1. HTTP

- [ ] request
- [ ] response
- [ ] GET
- [ ] POST
- [ ] PUT
- [ ] PATCH
- [ ] DELETE
- [ ] status codes
- [ ] headers
- [ ] body
- [ ] query params
- [ ] path params
- [ ] cookies
- [ ] idempotency
- [ ] safe methods
- [ ] `PUT` vs `PATCH`
- [ ] `401` vs `403`
- [ ] `400` vs `404`
- [ ] `200` vs `201` vs `204`

---

## 4.2. REST

- [ ] resources
- [ ] URI design
- [ ] statelessness
- [ ] CRUD
- [ ] pagination
- [ ] filtering
- [ ] sorting
- [ ] API versioning
- [ ] error response design

---

# 5. PostgreSQL и SQL — Не начато

## 5.1. SQL

- [ ] `SELECT`
- [ ] `WHERE`
- [ ] `ORDER BY`
- [ ] `GROUP BY`
- [ ] `HAVING`
- [ ] aggregate functions
- [ ] `INNER JOIN`
- [ ] `LEFT JOIN`
- [ ] `RIGHT JOIN`
- [ ] subqueries
- [ ] CTE
- [ ] `UNION`
- [ ] `DISTINCT`
- [ ] `NULL`
- [ ] window functions basics

---

## 5.2. Indexes

- [ ] зачем нужны индексы
- [ ] B-tree
- [ ] composite indexes
- [ ] порядок колонок
- [ ] selectivity
- [ ] read vs write cost
- [ ] когда индекс не используется
- [ ] `EXPLAIN`
- [ ] `EXPLAIN ANALYZE`

---

## 5.3. Transactions

- [ ] ACID
- [ ] isolation levels
- [ ] dirty read
- [ ] non-repeatable read
- [ ] phantom read
- [ ] lost update
- [ ] locks
- [ ] optimistic locking
- [ ] pessimistic locking
- [ ] MVCC basics

---

# 6. Spring Framework — Не начато

## 6.1. Spring Core / IoC / DI

- [ ] IoC
- [ ] Dependency Injection
- [ ] `ApplicationContext`
- [ ] Bean
- [ ] component scanning
- [ ] `@Component`
- [ ] `@Service`
- [ ] `@Repository`
- [ ] constructor injection
- [ ] setter injection
- [ ] field injection
- [ ] почему constructor injection предпочтительнее

---

## 6.2. Bean Lifecycle

- [ ] bean creation
- [ ] dependency injection
- [ ] initialization
- [ ] destruction
- [ ] `@PostConstruct`
- [ ] `@PreDestroy`
- [ ] `BeanPostProcessor`

---

## 6.3. Bean Scopes

- [ ] singleton
- [ ] prototype
- [ ] request
- [ ] session
- [ ] Spring singleton vs GoF Singleton

---

## 6.4. Configuration

- [ ] `@Configuration`
- [ ] `@Bean`
- [ ] `@ComponentScan`
- [ ] `@Value`
- [ ] properties
- [ ] profiles
- [ ] `@Profile`

---

## 6.5. Spring AOP

Ключ к пониманию `@Transactional`, поэтому изучается до транзакций.

- [ ] AOP
- [ ] aspect
- [ ] advice
- [ ] pointcut
- [ ] proxy
- [ ] JDK Dynamic Proxy
- [ ] CGLIB basics

---

# 7. Spring Boot — Не начато

- [ ] зачем Spring Boot
- [ ] auto-configuration
- [ ] starters
- [ ] `application.yml`
- [ ] `application.properties`
- [ ] configuration properties
- [ ] profiles
- [ ] embedded server
- [ ] Actuator basics
- [ ] Spring Boot startup flow на базовом уровне

---

# 8. Spring MVC — Не начато

- [ ] `DispatcherServlet`
- [ ] `@RestController`
- [ ] `@RequestMapping`
- [ ] `@GetMapping`
- [ ] `@PostMapping`
- [ ] `@PutMapping`
- [ ] `@PatchMapping`
- [ ] `@DeleteMapping`
- [ ] `@RequestBody`
- [ ] `@PathVariable`
- [ ] `@RequestParam`
- [ ] `ResponseEntity`
- [ ] DTO
- [ ] validation
- [ ] `@Valid`
- [ ] `@ControllerAdvice`
- [ ] `@ExceptionHandler`

---

# 9. JPA и Hibernate — Не начато

## 9.1. JPA Basics

- [ ] ORM
- [ ] Entity
- [ ] EntityManager
- [ ] Persistence Context
- [ ] entity lifecycle
- [ ] transient
- [ ] managed
- [ ] detached
- [ ] removed
- [ ] `persist`
- [ ] `merge`
- [ ] dirty checking
- [ ] flush
- [ ] `@Entity`
- [ ] `@Id`
- [ ] `@GeneratedValue`

---

## 9.2. Relationships

- [ ] `@OneToOne`
- [ ] `@OneToMany`
- [ ] `@ManyToOne`
- [ ] `@ManyToMany`
- [ ] owning side
- [ ] inverse side
- [ ] `mappedBy`

---

## 9.3. Fetching

- [ ] LAZY
- [ ] EAGER
- [ ] N+1
- [ ] join fetch
- [ ] EntityGraph

---

## 9.4. Cascade

- [ ] `PERSIST`
- [ ] `MERGE`
- [ ] `REMOVE`
- [ ] `ALL`
- [ ] `orphanRemoval`

---

## 9.5. Hibernate Problems

- [ ] `equals/hashCode` для Entity
- [ ] `LazyInitializationException`
- [ ] N+1
- [ ] pagination + join fetch
- [ ] transaction boundaries

---

# 10. Spring Transactions — Не начато

Точка, где смыкаются Spring-прокси и уровни изоляции из раздела 5.3.

- [ ] `@Transactional`
- [ ] proxy mechanism
- [ ] transaction boundary
- [ ] rollback
- [ ] checked vs unchecked exceptions
- [ ] propagation
- [ ] isolation
- [ ] `readOnly`
- [ ] self-invocation problem

---

# 11. Java Ecosystem — Не начато

## 11.1. JDBC

- [ ] что такое JDBC
- [ ] JDBC Driver
- [ ] `Connection`
- [ ] `Statement`
- [ ] `PreparedStatement`
- [ ] `ResultSet`
- [ ] SQL injection
- [ ] почему `PreparedStatement` предпочтительнее
- [ ] transactions в JDBC
- [ ] `commit`
- [ ] `rollback`
- [ ] auto-commit
- [ ] connection pooling
- [ ] JDBC vs JPA/Hibernate

---

## 11.2. Logging

- [ ] зачем нужен logging
- [ ] logging levels
- [ ] TRACE / DEBUG / INFO / WARN / ERROR
- [ ] SLF4J
- [ ] Logback
- [ ] facade vs implementation
- [ ] parameterized logging
- [ ] почему не использовать `System.out.println`
- [ ] exception logging
- [ ] structured logging на базовом уровне
- [ ] correlation / trace id на концептуальном уровне

---

## 11.3. Build Tools — Отложено

Есть практика. Конспект пишется в последнюю очередь.

### Gradle

- [ ] зачем нужен Gradle
- [ ] Gradle Wrapper
- [ ] `build.gradle`
- [ ] plugins
- [ ] dependencies
- [ ] configurations
- [ ] tasks
- [ ] build lifecycle
- [ ] multi-module basics

### Maven

- [ ] зачем нужен Maven
- [ ] `pom.xml`
- [ ] dependencies
- [ ] plugins
- [ ] scopes
- [ ] Maven lifecycle
- [ ] `clean` / `compile` / `test` / `package` / `install`
- [ ] Maven vs Gradle

---

# 12. Testing — Не начато

## 12.1. JUnit 5

- [ ] `@Test`
- [ ] assertions
- [ ] lifecycle
- [ ] `@BeforeEach`
- [ ] `@AfterEach`
- [ ] parameterized tests

---

## 12.2. Mockito

- [ ] mock
- [ ] stub
- [ ] spy
- [ ] `when`
- [ ] `thenReturn`
- [ ] `verify`
- [ ] `ArgumentCaptor`
- [ ] `@Mock`
- [ ] `@InjectMocks`

---

## 12.3. Spring Testing

- [ ] `@SpringBootTest`
- [ ] `@WebMvcTest`
- [ ] `@DataJpaTest`
- [ ] MockMvc
- [ ] integration tests
- [ ] Testcontainers basics

---

# 13. Apache Kafka — Не начато

Практический опыт есть, знания нужно систематизировать для интервью.

- [ ] broker
- [ ] topic
- [ ] partition
- [ ] producer
- [ ] consumer
- [ ] consumer group
- [ ] offset
- [ ] replication
- [ ] key
- [ ] ordering внутри partition
- [ ] rebalancing
- [ ] at-most-once
- [ ] at-least-once
- [ ] exactly-once
- [ ] idempotent producer
- [ ] retries
- [ ] duplicate messages
- [ ] DLQ
- [ ] consumer error handling

---

# 14. Backend Architecture — Не начато

- [ ] layered architecture
- [ ] controller / service / repository
- [ ] DTO
- [ ] mapper
- [ ] domain model
- [ ] modular monolith
- [ ] microservices basics
- [ ] synchronous communication
- [ ] asynchronous communication
- [ ] REST vs Kafka
- [ ] retries
- [ ] timeout
- [ ] circuit breaker
- [ ] idempotency
- [ ] caching

---

# 15. System Design — Не начато

Уровень Junior / Junior+, без ухода в Senior-level distributed systems.

- [ ] requirements clarification
- [ ] API design
- [ ] DB schema
- [ ] indexes
- [ ] cache
- [ ] concurrency
- [ ] queues
- [ ] horizontal scaling basics
- [ ] failure handling
- [ ] URL Shortener
- [ ] Notification Service
- [ ] Incident Management System
- [ ] Order Service

---

# 16. Docker и CI/CD — Не начато

Есть практика, теория не систематизирована.

- [ ] image
- [ ] container
- [ ] Dockerfile
- [ ] layers basics
- [ ] volume
- [ ] network
- [ ] ports
- [ ] environment variables
- [ ] Docker Compose
- [ ] healthcheck
- [ ] CI
- [ ] CD
- [ ] GitHub Actions
- [ ] basic deployment flow

---

# 17. Git — Не начато

Есть практика, теория не систематизирована.

- [ ] commit
- [ ] branch
- [ ] merge
- [ ] rebase
- [ ] cherry-pick
- [ ] reset
- [ ] revert
- [ ] stash
- [ ] conflicts
- [ ] `fetch` vs `pull`

---

# Порядок прохождения

## Этап 1. Добить Java Core выборочно

1. `Optional`.
2. `Modern Java`: enum и record.
3. `Annotations`.
4. `Nested Classes` — дописать разделом в конспект по лямбдам.
5. `Primitive streams` — дописать разделом в конспект по Stream API.

Отложено: `Date and Time API`, `Java I/O / NIO`.

## Этап 2. JVM, минимально необходимое

6. `Garbage Collection` и `Reference Types` одним конспектом.

`Class Loading` и `Bytecode / JIT` уже покрыты конспектом по памяти JVM.

## Этап 3. Ядро backend-интервью

7. `HTTP и REST`.
8. `SQL`: выборки, джойны, группировки.
9. `Indexes` и планы запросов.
10. `Transactions`: ACID, уровни изоляции, аномалии, MVCC.
11. `Spring Core`: IoC, DI, bean lifecycle, scopes, configuration.
12. `Spring AOP` и proxy.
13. `Spring Boot`.
14. `Spring MVC`.
15. `JPA Basics` и Persistence Context.
16. `Relationships`, `Fetching`, `Cascade`.
17. `Hibernate Problems`.
18. `Spring Transactions`.

## Этап 4. Production Backend

19. `JDBC`.
20. `Logging`.
21. `Testing`.
22. `Kafka`.
23. `Backend Architecture`.
24. `System Design`.
25. `Docker / CI/CD`.
26. `Git`.
27. `Build Tools`.

---

# Технический долг репозитория

Не про изучение тем, а про приведение конспектов в порядок.

- [ ] привести заголовки к единому виду: `#` только для названия темы, разделы `##`
- [ ] убрать сквозную нумерацию заголовков в конспектах по concurrency
- [ ] добавить блок «См. также» в конец каждого конспекта
- [ ] снабдить ответами вопросы для самопроверки в конспекте по исключениям
- [ ] снабдить ответами вопросы для самопроверки в конспекте по OOP
- [ ] удалить неиспользуемый `docs/templates`

---

# Как обновлять roadmap

После завершения темы:

1. Отметить соответствующие пункты `[x]`.
2. Обновить статус темы.
3. Добавить или обновить конспект в соответствующей директории `docs`.
4. Проставить ссылки «См. также» в связанных конспектах.
5. Обновить `docs/progress/topic-tracker.md`.

Roadmap не должен превращаться в список технологий ради списка. Темы изучаются с
приоритетом на то, что реально требуется Java Backend Developer и регулярно
встречается на Junior / Junior+ технических интервью.