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
- [x] primitive streams
- [x] `IntStream`, `LongStream`, `DoubleStream`
- [x] boxing и unboxing в stream

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
- [x] `or` и `stream`
- [x] `isEmpty`
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
- [x] constant-specific behaviour
- [x] enum как singleton
- [x] `EnumSet`
- [x] `EnumMap`
- [x] `ordinal` и `@Enumerated(EnumType.STRING)`

### Record

- [x] record syntax
- [x] generated members
- [x] final components
- [x] accessors
- [x] `equals`
- [x] `hashCode`
- [x] `toString`
- [x] compact constructor
- [x] поверхностная неизменяемость
- [x] сценарии применения
- [x] ограничения
- [x] record как проекция запроса

### Sealed Classes

- [x] `sealed`
- [x] `permits`
- [x] `non-sealed`
- [x] sealed hierarchy
- [x] исчерпывающий `switch`

---

## 1.13. Annotations — Изучено

- [x] что такое annotation
- [x] built-in annotations
- [x] `@Override`
- [x] `@Deprecated`
- [x] `@SuppressWarnings`
- [x] `@FunctionalInterface`
- [x] `@SafeVarargs`
- [x] custom annotations
- [x] допустимые типы элементов
- [x] `@Target`
- [x] `@Retention`
- [x] `RetentionPolicy`
- [x] `@Inherited`
- [x] `@Repeatable`
- [x] reflection + annotations на базовом уровне
- [x] annotation processing на концептуальном уровне
- [x] как аннотации работают в Spring

---

## 1.14. Nested Classes — Изучено

Разобраны в конспекте по функциональным интерфейсам и lambda.

- [x] static nested class
- [x] inner class
- [x] local class
- [x] anonymous class
- [x] anonymous class vs lambda
- [x] доступ к outer instance
- [x] static nested vs inner class
- [x] скрытая ссылка на внешний экземпляр и утечки
- [x] nestmates

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

## 2.3. Garbage Collection — Изучено

Основы в конспекте по памяти JVM, алгоритмы и сборщики — в отдельном конспекте.

- [x] что такое GC
- [x] GC Roots
- [x] reachability
- [x] циклические ссылки
- [x] young generation
- [x] old generation
- [x] generational hypothesis
- [x] minor GC
- [x] major GC
- [x] full GC
- [x] Stop-The-World
- [x] mark-sweep, mark-compact, copying
- [x] allocation, bump-the-pointer, TLAB
- [x] escape analysis
- [x] promotion и `MaxTenuringThreshold`
- [x] преждевременное продвижение
- [x] card table и write barrier
- [x] Serial, Parallel, CMS
- [x] G1
- [x] ZGC basics
- [x] Shenandoah и Epsilon
- [x] throughput / latency / footprint
- [x] базовые флаги и GC-логи
- [x] memory leaks в Java
- [x] диагностика: heap dump, retained size

---

## 2.4. Reference Types — Изучено

- [x] strong reference
- [x] soft reference
- [x] weak reference
- [x] phantom reference
- [x] `ReferenceQueue`
- [x] `WeakHashMap`
- [x] `finalize` и почему он удалён
- [x] `Cleaner`

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

# 4. HTTP и REST — Изучено

## 4.1. HTTP

- [x] request
- [x] response
- [x] GET
- [x] POST
- [x] PUT
- [x] PATCH
- [x] DELETE
- [x] status codes
- [x] headers
- [x] body
- [x] query params
- [x] path params
- [x] cookies
- [x] idempotency
- [x] safe methods
- [x] `PUT` vs `PATCH`
- [x] `401` vs `403`
- [x] `400` vs `404`
- [x] `200` vs `201` vs `204`

---

## 4.2. REST

- [x] resources
- [x] URI design
- [x] statelessness
- [x] CRUD
- [x] pagination
- [x] filtering
- [x] sorting
- [x] API versioning
- [x] error response design

---

# 5. PostgreSQL и SQL — Изучено

## 5.1. SQL

- [x] `SELECT`
- [x] `WHERE`
- [x] `ORDER BY`
- [x] `GROUP BY`
- [x] `HAVING`
- [x] aggregate functions
- [x] `INNER JOIN`
- [x] `LEFT JOIN`
- [x] `RIGHT JOIN`
- [x] subqueries
- [x] CTE
- [x] `UNION`
- [x] `DISTINCT`
- [x] `NULL`
- [x] window functions basics

---

## 5.2. Indexes

- [x] зачем нужны индексы
- [x] B-tree
- [x] composite indexes
- [x] порядок колонок
- [x] selectivity
- [x] read vs write cost
- [x] когда индекс не используется
- [x] `EXPLAIN`
- [x] `EXPLAIN ANALYZE`

---

## 5.3. Transactions

- [x] ACID
- [x] isolation levels
- [x] dirty read
- [x] non-repeatable read
- [x] phantom read
- [x] lost update
- [x] locks
- [x] optimistic locking
- [x] pessimistic locking
- [x] MVCC basics

---

# 6. Spring Framework — Изучено

## 6.1. Spring Core / IoC / DI

- [x] IoC
- [x] Dependency Injection
- [x] `ApplicationContext`
- [x] Bean
- [x] component scanning
- [x] `@Component`
- [x] `@Service`
- [x] `@Repository`
- [x] constructor injection
- [x] setter injection
- [x] field injection
- [x] почему constructor injection предпочтительнее

---

## 6.2. Bean Lifecycle

- [x] bean creation
- [x] dependency injection
- [x] initialization
- [x] destruction
- [x] `@PostConstruct`
- [x] `@PreDestroy`
- [x] `BeanPostProcessor`

---

## 6.3. Bean Scopes

- [x] singleton
- [x] prototype
- [x] request
- [x] session
- [x] Spring singleton vs GoF Singleton

---

## 6.4. Configuration

- [x] `@Configuration`
- [x] `@Bean`
- [x] `@ComponentScan`
- [x] `@Value`
- [x] properties
- [x] profiles
- [x] `@Profile`

---

## 6.5. Spring AOP

Ключ к пониманию `@Transactional`, поэтому изучается до транзакций.

- [x] AOP
- [x] aspect
- [x] advice
- [x] pointcut
- [x] proxy
- [x] JDK Dynamic Proxy
- [x] CGLIB basics

---

# 7. Spring Boot — Изучено

- [x] зачем Spring Boot
- [x] auto-configuration
- [x] starters
- [x] `application.yml`
- [x] `application.properties`
- [x] configuration properties
- [x] profiles
- [x] embedded server
- [x] Actuator basics
- [x] Spring Boot startup flow на базовом уровне

---

# 8. Spring MVC — Изучено

- [x] `DispatcherServlet`
- [x] `@RestController`
- [x] `@RequestMapping`
- [x] `@GetMapping`
- [x] `@PostMapping`
- [x] `@PutMapping`
- [x] `@PatchMapping`
- [x] `@DeleteMapping`
- [x] `@RequestBody`
- [x] `@PathVariable`
- [x] `@RequestParam`
- [x] `ResponseEntity`
- [x] DTO
- [x] validation
- [x] `@Valid`
- [x] `@ControllerAdvice`
- [x] `@ExceptionHandler`

---

# 9. JPA и Hibernate — Изучено

## 9.1. JPA Basics

- [x] ORM
- [x] Entity
- [x] EntityManager
- [x] Persistence Context
- [x] entity lifecycle
- [x] transient
- [x] managed
- [x] detached
- [x] removed
- [x] `persist`
- [x] `merge`
- [x] dirty checking
- [x] flush
- [x] `@Entity`
- [x] `@Id`
- [x] `@GeneratedValue`

---

## 9.2. Relationships

- [x] `@OneToOne`
- [x] `@OneToMany`
- [x] `@ManyToOne`
- [x] `@ManyToMany`
- [x] owning side
- [x] inverse side
- [x] `mappedBy`

---

## 9.3. Fetching

- [x] LAZY
- [x] EAGER
- [x] N+1
- [x] join fetch
- [x] EntityGraph

---

## 9.4. Cascade

- [x] `PERSIST`
- [x] `MERGE`
- [x] `REMOVE`
- [x] `ALL`
- [x] `orphanRemoval`

---

## 9.5. Hibernate Problems

- [x] `equals/hashCode` для Entity
- [x] `LazyInitializationException`
- [x] N+1
- [x] pagination + join fetch
- [x] transaction boundaries

---

# 10. Spring Transactions — Изучено

Точка, где смыкаются Spring-прокси и уровни изоляции из раздела 5.3.

- [x] `@Transactional`
- [x] proxy mechanism
- [x] transaction boundary
- [x] rollback
- [x] checked vs unchecked exceptions
- [x] propagation
- [x] isolation
- [x] `readOnly`
- [x] self-invocation problem

---

# 11. Java Ecosystem — Изучено

## 11.1. JDBC

- [x] что такое JDBC
- [x] JDBC Driver
- [x] `Connection`
- [x] `Statement`
- [x] `PreparedStatement`
- [x] `ResultSet`
- [x] SQL injection
- [x] почему `PreparedStatement` предпочтительнее
- [x] transactions в JDBC
- [x] `commit`
- [x] `rollback`
- [x] auto-commit
- [x] connection pooling
- [x] JDBC vs JPA/Hibernate

---

## 11.2. Logging

- [x] зачем нужен logging
- [x] logging levels
- [x] TRACE / DEBUG / INFO / WARN / ERROR
- [x] SLF4J
- [x] Logback
- [x] facade vs implementation
- [x] parameterized logging
- [x] почему не использовать `System.out.println`
- [x] exception logging
- [x] structured logging на базовом уровне
- [x] correlation / trace id на концептуальном уровне

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

# 12. Testing — Изучен

## 12.1. JUnit 5

- [x] `@Test`
- [x] assertions
- [x] lifecycle
- [x] `@BeforeEach`
- [x] `@AfterEach`
- [x] parameterized tests

---

## 12.2. Mockito

- [x] mock
- [x] stub
- [x] spy
- [x] `when`
- [x] `thenReturn`
- [x] `verify`
- [x] `ArgumentCaptor`
- [x] `@Mock`
- [x] `@InjectMocks`

---

## 12.3. Spring Testing

- [x] `@SpringBootTest`
- [x] `@WebMvcTest`
- [x] `@DataJpaTest`
- [x] MockMvc
- [x] integration tests
- [x] Testcontainers basics

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

## Этап 1. Java Core — завершён

- [x] `Optional`
- [x] `Modern Java`: enum, record, sealed
- [x] `Annotations`
- [x] `Nested Classes` — в конспекте по lambda
- [x] `Primitive streams` — в конспекте по Stream API

Отложено: `Date and Time API`, `Java I/O / NIO`.

## Этап 2. JVM — завершён

- [x] `Garbage Collection` и `Reference Types` — отдельный конспект
- [x] `Class Loading` и `Bytecode / JIT` — в конспекте по памяти JVM

## Этап 3. Ядро backend-интервью

- [ ] 1. `HTTP и REST`
- [ ] 2. `SQL`: выборки, джойны, группировки
- [ ] 3. `Indexes` и планы запросов
- [ ] 4. `Transactions`: ACID, уровни изоляции, аномалии, MVCC
- [ ] 5. `Spring Core`: IoC, DI, bean lifecycle, scopes, configuration
- [ ] 6. `Spring AOP` и proxy
- [ ] 7. `Spring Boot`
- [ ] 8. `Spring MVC`
- [ ] 9. `JPA Basics` и Persistence Context
- [ ] 10. `Relationships`, `Fetching`, `Cascade`
- [ ] 11. `Hibernate Problems`
- [ ] 12. `Spring Transactions`

## Этап 4. Production Backend

- [ ] 13. `JDBC`
- [ ] 14. `Logging`
- [ ] 15. `Testing`
- [ ] 16. `Kafka`
- [ ] 17. `Backend Architecture`
- [ ] 18. `System Design`
- [ ] 19. `Docker / CI/CD`
- [ ] 20. `Git`
- [ ] 21. `Build Tools`

---

# Технический долг репозитория

Не про изучение тем, а про приведение конспектов в порядок. Делается фоном, когда
не хочется браться за новую тему.

- [ ] привести заголовки к единому виду в конспектах `00`–`08`: `#` только для
  названия темы, разделы `##`
- [ ] в `01-collections-framework.md` дополнительно смешаны оба стиля
- [ ] убрать сквозную нумерацию заголовков в `concurrency/04`, `concurrency/05`,
  `concurrency/06`
- [ ] добавить блок «См. также» в `00-java-language-basics.md` и `04-generics.md`
- [ ] снабдить ответами вопросы для самопроверки: `00`, `01`, `02`, `03`, `04`,
  `05`, `06`, `07`
- [ ] в `06-stream-api.md` сократить разбор `orElse` / `orElseGet` до ссылки на
  `09-optional.md`
- [x] удалить неиспользуемый `docs/templates`

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