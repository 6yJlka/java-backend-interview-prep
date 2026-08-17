# Java Backend Interview Preparation Roadmap

Полный roadmap подготовки к техническим интервью на позиции Java Backend Developer.

Roadmap ориентирован не просто на изучение Java, а на подготовку к Junior / Junior+ Java Backend интервью.  
Он объединяет Java Core, JVM, Concurrency, Spring, базы данных, JPA/Hibernate, Kafka, Testing, инфраструктуру, архитектуру и алгоритмы.

## Статусы

- `Не начато`
- `В процессе`
- `Изучено`
- `Нужно повторить`

---

# 1. Java Core

## 1.1. Java Language Basics — Не начато системно

Базовый синтаксис уже используется на практике, но этот блок нужно пройти именно в формате подготовки к интервью.

- [ ] primitive types
- [ ] reference types
- [ ] variables
- [ ] scopes
- [ ] default values
- [ ] operators
- [ ] control flow
- [ ] arrays
- [ ] multidimensional arrays
- [ ] type casting
- [ ] widening conversion
- [ ] narrowing conversion
- [ ] Java pass-by-value
- [ ] передача primitive в метод
- [ ] передача object reference в метод
- [ ] varargs
- [ ] packages
- [ ] imports
- [ ] access modifiers

---

## 1.2. OOP — Не начато системно

- [ ] class и object
- [ ] encapsulation
- [ ] inheritance
- [ ] polymorphism
- [ ] abstraction
- [ ] interface
- [ ] abstract class
- [ ] interface vs abstract class
- [ ] overriding
- [ ] overloading
- [ ] static binding
- [ ] dynamic binding
- [ ] `this`
- [ ] `super`
- [ ] `final`
- [ ] `static`
- [ ] composition vs inheritance
- [ ] можно ли override `static`
- [ ] можно ли override `private`
- [ ] covariant return type

---

## 1.3. Object, String и Wrappers — Не начато системно

### Object

- [ ] `toString`
- [ ] `equals`
- [ ] `hashCode`
- [ ] `getClass`
- [ ] `clone` на концептуальном уровне
- [ ] runtime type объекта

### String

- [ ] String immutability
- [ ] String Pool
- [ ] string literals
- [ ] `new String(...)`
- [ ] `intern`
- [ ] concatenation
- [ ] `StringBuilder`
- [ ] `StringBuffer`
- [ ] `StringBuilder` vs `StringBuffer`
- [ ] почему `String` immutable

### Primitive Types и Wrappers

- [ ] primitives vs wrappers
- [ ] boxing
- [ ] unboxing
- [ ] autoboxing
- [ ] Integer cache
- [ ] wrapper equality
- [ ] `==` vs `equals`
- [ ] numeric overflow
- [ ] `null` + unboxing
- [ ] `Number`

---

## 1.4. Collections Framework — В процессе

- [x] Иерархия `Collection`
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
- [ ] `Comparable` vs `Comparator` — финальное повторение
- [ ] `Iterator`
- [ ] `ListIterator`
- [ ] fail-fast iterator
- [ ] `ConcurrentModificationException`
- [ ] immutable collections
- [ ] unmodifiable collections
- [ ] `List.of`
- [ ] `Set.of`
- [ ] `Map.of`
- [ ] Финальный контрольный опрос

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
- [ ] Повторить внутреннее устройство `HashMap`
- [ ] Повторить treeification bucket
- [ ] Повторить resize / load factor

---

## 1.6. equals и hashCode — Изучено

- [x] контракт `equals`
- [x] контракт `hashCode`
- [x] связь `equals` и `hashCode`
- [x] `==` vs `equals`
- [x] mutable key в `HashMap`
- [ ] Повторение

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
- [ ] Повторение

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
- [ ] suppressed exceptions
- [ ] multi-catch
- [ ] Повторение

---

## 1.9. Functional Interfaces и Lambda — Не начато системно

- [ ] lambda expressions
- [ ] method references
- [ ] functional interface
- [ ] `@FunctionalInterface`
- [ ] `Predicate`
- [ ] `Function`
- [ ] `Consumer`
- [ ] `Supplier`
- [ ] `UnaryOperator`
- [ ] `BinaryOperator`
- [ ] effectively final
- [ ] closure
- [ ] lambda vs anonymous class

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
- [ ] primitive streams
- [ ] `IntStream`
- [ ] parallel streams
- [ ] ограничения parallel streams
- [ ] Повторение

---

## 1.11. Optional — Не начато системно

- [ ] `Optional.of`
- [ ] `Optional.ofNullable`
- [ ] `Optional.empty`
- [ ] `map`
- [ ] `flatMap`
- [ ] `filter`
- [ ] `orElse`
- [ ] `orElseGet`
- [ ] `orElseThrow`
- [ ] `ifPresent`
- [ ] `ifPresentOrElse`
- [ ] где `Optional` использовать не стоит
- [ ] `orElse` vs `orElseGet`

---

## 1.12. Annotations — Не начато системно

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

## 1.13. Nested Classes — Не начато системно

- [ ] static nested class
- [ ] inner class
- [ ] local class
- [ ] anonymous class
- [ ] доступ к outer instance
- [ ] static nested vs inner class

---

## 1.14. Modern Java — Не начато системно

### Enum

- [ ] enum как класс
- [ ] поля и методы enum
- [ ] constructor
- [ ] `values`
- [ ] `valueOf`
- [ ] enum в `switch`
- [ ] `EnumSet`
- [ ] `EnumMap`

### Record

- [ ] record syntax
- [ ] generated members
- [ ] final components
- [ ] accessors
- [ ] `equals`
- [ ] `hashCode`
- [ ] `toString`
- [ ] compact constructor
- [ ] сценарии применения
- [ ] ограничения

### Sealed Classes

- [ ] `sealed`
- [ ] `permits`
- [ ] `non-sealed`
- [ ] `final`
- [ ] sealed hierarchy

---

## 1.15. Date and Time API — Не начато системно

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

## 1.16. Java I/O и NIO — Не начато

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
- [ ] чтение файла
- [ ] запись файла
- [ ] `Files.lines`
- [ ] file attributes на базовом уровне
- [ ] blocking I/O vs non-blocking I/O на концептуальном уровне

---

# 2. JVM

## 2.1. Runtime Data Areas — Изучено

- [x] Heap
- [x] Stack
- [x] Metaspace
- [x] PC Register
- [x] Native Method Stack
- [ ] Повторение

---

## 2.2. Class Loading — Не начато

- [ ] Loading
- [ ] Linking
- [ ] Verification
- [ ] Preparation
- [ ] Resolution
- [ ] Initialization
- [ ] Bootstrap ClassLoader
- [ ] Platform ClassLoader
- [ ] Application ClassLoader
- [ ] Parent Delegation Model
- [ ] когда выполняется static initialization

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

- [ ] strong reference
- [ ] soft reference
- [ ] weak reference
- [ ] phantom reference
- [ ] `ReferenceQueue`
- [ ] `WeakHashMap`

---

## 2.5. Bytecode и JIT — Не начато

- [ ] `.java`
- [ ] `javac`
- [ ] `.class`
- [ ] bytecode
- [ ] interpreter
- [ ] JIT compiler
- [ ] HotSpot
- [ ] runtime optimization basics
- [ ] why Java is compiled and interpreted

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
- [ ] Повторение

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

### Locks и Atomics

- [x] `ReentrantLock`
- [x] `tryLock`
- [x] `lockInterruptibly`
- [x] `Condition`
- [x] Atomic classes
- [x] CAS
- [x] ABA problem

### Executors

- [x] `ExecutorService`
- [x] `Future`
- [x] `ThreadPoolExecutor`
- [x] rejection policies

### Concurrent Collections

- [x] `ConcurrentHashMap`
- [x] `Collections.synchronizedMap`
- [x] `CopyOnWriteArrayList`
- [x] `BlockingQueue`
- [x] `ArrayBlockingQueue`
- [x] `LinkedBlockingQueue`
- [x] `SynchronousQueue`
- [x] `ConcurrentLinkedQueue`

### CompletableFuture

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

### Virtual Threads

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

### Advanced Later

- [ ] Structured Concurrency
- [ ] Scoped Values

---

# 4. Java Ecosystem

## 4.1. Build Tools — Не начато системно

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
- [ ] `clean`
- [ ] `compile`
- [ ] `test`
- [ ] `package`
- [ ] `install`
- [ ] Maven vs Gradle

---

## 4.2. JDBC — Не начато системно

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

## 4.3. Logging — Не начато системно

- [ ] зачем нужен logging
- [ ] logging levels
- [ ] TRACE
- [ ] DEBUG
- [ ] INFO
- [ ] WARN
- [ ] ERROR
- [ ] SLF4J
- [ ] Logback
- [ ] facade vs implementation
- [ ] parameterized logging
- [ ] почему не использовать `System.out.println`
- [ ] exception logging
- [ ] structured logging на базовом уровне
- [ ] correlation / trace id на концептуальном уровне

---

# 5. Spring Framework

## 5.1. Spring Core / IoC / DI — Не начато

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

## 5.2. Bean Lifecycle — Не начато

- [ ] bean creation
- [ ] dependency injection
- [ ] initialization
- [ ] destruction
- [ ] `@PostConstruct`
- [ ] `@PreDestroy`
- [ ] `BeanPostProcessor`

---

## 5.3. Bean Scopes — Не начато

- [ ] singleton
- [ ] prototype
- [ ] request
- [ ] session
- [ ] Spring singleton vs GoF Singleton

---

## 5.4. Configuration — Не начато

- [ ] `@Configuration`
- [ ] `@Bean`
- [ ] `@ComponentScan`
- [ ] `@Value`
- [ ] properties
- [ ] profiles
- [ ] `@Profile`

---

## 5.5. Spring AOP — Не начато

- [ ] AOP
- [ ] aspect
- [ ] advice
- [ ] pointcut
- [ ] proxy
- [ ] JDK Dynamic Proxy
- [ ] CGLIB basics

---

# 6. Spring Boot — Не начато

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

# 7. HTTP / REST / Spring MVC

## 7.1. HTTP — Не начато

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

## 7.2. REST — Не начато

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

## 7.3. Spring MVC — Не начато

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

# 8. PostgreSQL and SQL

## 8.1. SQL — Не начато системно

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

## 8.2. Indexes — Не начато системно

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

## 8.3. Transactions — Не начато системно

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

# 9. JPA and Hibernate

## 9.1. JPA Basics — Не начато системно

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

## 9.2. Relationships — Не начато системно

- [ ] `@OneToOne`
- [ ] `@OneToMany`
- [ ] `@ManyToOne`
- [ ] `@ManyToMany`
- [ ] owning side
- [ ] inverse side
- [ ] `mappedBy`

---

## 9.3. Fetching — Не начато системно

- [ ] LAZY
- [ ] EAGER
- [ ] N+1
- [ ] join fetch
- [ ] EntityGraph

---

## 9.4. Cascade — Не начато системно

- [ ] `PERSIST`
- [ ] `MERGE`
- [ ] `REMOVE`
- [ ] `ALL`
- [ ] `orphanRemoval`

---

## 9.5. Hibernate Problems — Не начато системно

- [ ] `equals/hashCode` для Entity
- [ ] `LazyInitializationException`
- [ ] N+1
- [ ] pagination + join fetch
- [ ] transaction boundaries

---

# 10. Spring Transactions — Не начато

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

# 11. Testing

## 11.1. JUnit 5 — Не начато системно

- [ ] `@Test`
- [ ] assertions
- [ ] lifecycle
- [ ] `@BeforeEach`
- [ ] `@AfterEach`
- [ ] parameterized tests

---

## 11.2. Mockito — Не начато системно

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

## 11.3. Spring Testing — Не начато системно

- [ ] `@SpringBootTest`
- [ ] `@WebMvcTest`
- [ ] `@DataJpaTest`
- [ ] MockMvc
- [ ] integration tests
- [ ] Testcontainers basics

---

# 12. Apache Kafka — Не начато системно

Практический опыт есть, но знания нужно систематизировать для интервью.

- [ ] broker
- [ ] topic
- [ ] partition
- [ ] producer
- [ ] consumer
- [ ] consumer group
- [ ] offset
- [ ] replication
- [ ] key
- [ ] ordering
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

# 13. Backend Architecture — Не начато системно

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

# 14. System Design — Не начато системно

Уровень — Junior / Junior+, без ухода в Senior-level distributed systems.

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

# 15. Docker / CI/CD — Есть практика, теория не систематизирована

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

# 16. Git — Есть практика, теория не систематизирована

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

# 17. Алгоритмы

Алгоритмы ведутся отдельно в репозитории `java-algorithms-prep`.

## Пройдено

- [x] Complexity Analysis
- [x] Hashing
- [x] Two Pointers
- [x] Sliding Window
- [x] Prefix Sum

## Далее

- [ ] Stack
- [ ] Queue / Deque
- [ ] Binary Search
- [ ] Linked List
- [ ] Intervals
- [ ] Trees
- [ ] DFS
- [ ] BFS
- [ ] Heap / Priority Queue
- [ ] Graphs
- [ ] Backtracking
- [ ] Dynamic Programming basics

---

# Ближайший порядок прохождения

## Этап 1. Закрыть оставшийся Java Core

1. Закрыть `Collections Framework`.
2. `Java Language Basics` — быстрый interview-oriented проход.
3. `OOP`.
4. `Object`, `String`, primitives и wrappers.
5. `Functional Interfaces` и `Lambda`.
6. `Optional`.
7. `Annotations`.
8. `Nested Classes`.
9. `Modern Java`.
10. `Date and Time API`.
11. `Java I/O / NIO`.

## Этап 2. Закрыть JVM

12. `Class Loading`.
13. `Garbage Collection`.
14. `Reference Types`.
15. `Bytecode / JIT`.

## Этап 3. Java Ecosystem

16. `Gradle / Maven`.
17. `JDBC`.
18. `Logging`.

## Этап 4. Backend Frameworks

19. `Spring Core`.
20. `Spring Boot`.
21. `HTTP / REST`.
22. `Spring MVC`.

## Этап 5. Persistence

23. `SQL / PostgreSQL`.
24. `JPA / Hibernate`.
25. `Spring Transactions`.

## Этап 6. Production Backend

26. `Testing`.
27. `Kafka`.
28. `Backend Architecture`.
29. `System Design`.
30. `Docker / CI/CD`.
31. `Git`.

---

# Как обновлять roadmap

После завершения темы:

1. Отметить соответствующие пункты `[x]`.
2. Обновить статус темы.
3. Добавить или обновить конспект в соответствующей директории `docs`.
4. Обновить `docs/progress/topic-tracker.md`.
5. Вернуться к изученной теме позже через повторение и контрольные вопросы.

Roadmap не должен превращаться в список технологий ради списка.  
Темы изучаются с приоритетом на то, что реально требуется Java Backend Developer и регулярно встречается на Junior / Junior+ технических интервью.
