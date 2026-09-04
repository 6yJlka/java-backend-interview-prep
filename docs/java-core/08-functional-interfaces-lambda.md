# Functional Interfaces и Lambda

# Зачем это нужно

До Java 8 передать поведение в метод можно было только через объект. Чтобы описать
одно действие, приходилось создавать анонимный класс:

```java
button.addListener(new Listener() {
    @Override
    public void onEvent(Event event) {
        log(event);
    }
});
```

Полезной информации здесь одна строка. Остальное — синтаксическая обвязка вокруг
единственного метода.

Lambda позволяет записать то же самое как выражение:

```java
button.addListener(event -> log(event));
```

Тип у выражения при этом никуда не исчезает. Lambda всегда получает тип
функционального интерфейса из контекста, в котором она используется.

---

# Functional Interface

Функциональный интерфейс — интерфейс ровно с одним абстрактным методом.

```java
interface Validator {
    boolean validate(String value);
}
```

Такой интерфейс задаёт одну операцию, поэтому lambda может быть её реализацией:

```java
Validator notBlank = value -> !value.isBlank();
```

## Что не считается абстрактным методом

Наличие других членов не мешает интерфейсу оставаться функциональным.

```java
@FunctionalInterface
interface Validator {

    boolean validate(String value);

    default Validator negate() {
        return value -> !validate(value);
    }

    static Validator alwaysTrue() {
        return value -> true;
    }

    String toString();
}
```

Здесь абстрактный метод по-прежнему один:

```text
default методы           → есть реализация
static методы            → не наследуются как абстрактные
private методы           → есть реализация
public методы Object     → не учитываются
```

Последний пункт нередко спрашивают. Объявление `toString()`, `equals(Object)` или
`hashCode()` в интерфейсе не делает его нефункциональным, потому что любая
реализация уже получает их от `Object`.

## @FunctionalInterface

Аннотация не обязательна. Она не превращает интерфейс в функциональный, а просит
компилятор проверить это условие.

```java
@FunctionalInterface
interface Validator {
    boolean validate(String value);
    boolean check(String value); // ошибка компиляции
}
```

Без аннотации такой интерфейс просто перестал бы подходить для lambda, и ошибка
всплыла бы в другом месте — там, где lambda пытаются присвоить. Аннотация ловит
проблему в точке объявления.

```text
@FunctionalInterface
→ контракт «этот интерфейс предназначен для lambda»
→ защита от случайного добавления второго абстрактного метода
```

---

# Синтаксис lambda

Общая форма:

```text
(параметры) -> тело
```

Варианты записи:

```java
(String value) -> value.length()   // явные типы
(value) -> value.length()          // вывод типов
value -> value.length()            // один параметр, скобки опциональны
() -> log("start")                 // без параметров
(a, b) -> a + b                    // несколько параметров
```

Скобки нельзя опустить для нуля или двух и более параметров, а также при явном
указании типа.

Тело бывает выражением или блоком:

```java
value -> value * 2;

value -> {
    int result = value * 2;
    return result;
};
```

В блочной форме `return` обязателен, если метод возвращает значение.

## var в параметрах

С Java 11 допустимо:

```java
(var value) -> value.length()
```

Это нужно, когда параметру требуется аннотация или модификатор `final`:

```java
(@NonNull var value) -> value.length()
```

Смешивать нельзя: либо все параметры с `var`, либо все с явными типами, либо все
без типов.

---

# Target typing

Lambda не имеет собственного самостоятельного типа. Её тип определяет контекст —
target type.

```java
Runnable task = () -> System.out.println("run");
```

Здесь `() -> ...` получает тип `Runnable`, потому что этого требует переменная.

Одна и та же запись может означать разные типы:

```java
interface Command {
    void execute();
}

Runnable runnable = () -> doWork();
Command command = () -> doWork();
```

Тела идентичны, типы разные. Поэтому невозможно написать:

```java
var action = () -> doWork(); // ошибка компиляции
```

У `var` нет target type, из которого можно вывести интерфейс.

По этой же причине lambda нельзя присвоить `Object`:

```java
Object o = () -> doWork(); // ошибка компиляции
```

`Object` не является функциональным интерфейсом.

Допустимые контексты для target type:

```text
присваивание переменной
аргумент метода
возвращаемое значение
приведение типа
тернарный оператор
```

Приведение решает проблему неоднозначности:

```java
Object o = (Runnable) () -> doWork(); // корректно
```

---

# Lambda и анонимный класс

Внешне похожи, внутри устроены по-разному.

## this

Это главное практическое различие.

```java
class Service {

    private String name = "service";

    void run() {

        Runnable anonymous = new Runnable() {
            @Override
            public void run() {
                System.out.println(this); // экземпляр анонимного класса
            }
        };

        Runnable lambda = () -> {
            System.out.println(this); // экземпляр Service
        };
    }
}
```

Анонимный класс создаёт новую область видимости, и `this` указывает на его
собственный экземпляр. Lambda не создаёт нового scope: `this`, `super` и имена
переменных внутри неё означают ровно то же, что и в окружающем коде.

Отсюда следствие: обратиться к полю внешнего класса из lambda можно напрямую, а
из анонимного класса потребовалось бы `Service.this.name`.

## Затенение имён

```java
void run() {
    String value = "outer";

    Runnable anonymous = new Runnable() {
        @Override
        public void run() {
            String value = "inner"; // допустимо, затеняет внешнюю
        }
    };

    Runnable lambda = () -> {
        String value = "inner"; // ошибка компиляции
    };
}
```

Lambda делит область видимости с методом, поэтому объявить переменную с тем же
именем нельзя.

## Генерация классов

Анонимный класс порождает отдельный `.class`-файл:

```text
Service$1.class
Service$2.class
```

Lambda компилируется в приватный метод класса и инструкцию `invokedynamic`, которая
при первом выполнении через `LambdaMetafactory` создаёт реализацию интерфейса.
Отдельного `.class`-файла на этапе компиляции не появляется.

Практическое следствие: lambda без захвата состояния может переиспользовать один
экземпляр, тогда как `new Runnable() {...}` в цикле создаёт новый объект на каждой
итерации. Но это деталь реализации HotSpot, а не гарантия спецификации, и строить
на ней логику нельзя.

## Сводная таблица

| Критерий | Lambda | Анонимный класс |
|---|---|---|
| Что можно реализовать | только функциональный интерфейс | интерфейс или класс |
| Число абстрактных методов | ровно один | любое |
| `this` | внешний экземпляр | собственный экземпляр |
| Новая область видимости | нет | да |
| Затенение локальных переменных | нельзя | можно |
| Собственное состояние | нет | можно объявить поля |
| Отдельный `.class` | нет | да |
| Механизм | `invokedynamic` | обычное создание объекта |

---

# Effectively final

Lambda может использовать локальные переменные окружающего метода, но только если
они final или effectively final.

```java
void process() {
    String prefix = "id-";                 // effectively final
    Runnable task = () -> log(prefix + 1); // корректно
}
```

`effectively final` означает: переменная не помечена `final`, но и не изменяется
после инициализации. Компилятор проверяет это сам.

Нарушение:

```java
void process() {
    String prefix = "id-";
    prefix = "key-";                       // переприсваивание

    Runnable task = () -> log(prefix);     // ошибка компиляции
}
```

Ошибка возникает независимо от того, идёт присваивание до lambda или после.

## Почему такое ограничение

Локальные переменные живут в стеке потока, который выполняет метод. Lambda может
пережить этот метод и выполниться позже, в другом потоке:

```java
executor.submit(() -> log(prefix));
```

К моменту выполнения кадр стека может быть уничтожен. Поэтому захватывается не
сама переменная, а её значение — копия.

Если бы переменную разрешили менять, возник бы вопрос: какое значение должна
видеть lambda — на момент создания или на момент вызова. Требование effectively
final убирает этот вопрос: значение одно и не меняется.

Это ещё и защита от гонок. Изменяемая разделяемая локальная переменная в
многопоточном коде стала бы источником data race без какой-либо синхронизации.

## Захват объекта, а не значения

Ограничение относится к самой переменной, но не к состоянию объекта:

```java
List<String> results = new ArrayList<>();     // effectively final

Runnable task = () -> results.add("value");   // корректно
```

Ссылка `results` не меняется, поэтому компилятор доволен. Но объект, на который она
указывает, изменяемый.

```text
final / effectively final
→ ссылку нельзя переприсвоить

final / effectively final
≠
объект immutable
```

Это ровно та же ловушка, что с `volatile`-ссылкой в JMM. И тут она опаснее: код
компилируется, а гонка остаётся. Если такую lambda выполняют несколько потоков,
`ArrayList` нужно заменить на потокобезопасную структуру или собирать результат
через `Stream.collect()`.

## Обход через поле

Поля класса под ограничение не попадают:

```java
class Counter {

    private int count;

    void run() {
        Runnable task = () -> count++; // компилируется
    }
}
```

Компилируется, потому что захватывается `this`, а не `count`. Но потокобезопасным
это не делает: `count++` остаётся составной операцией. Для конкурентного счётчика
нужен `AtomicInteger`.

Обход через массив-обёртку встречается в старом коде:

```java
int[] holder = new int[1];
Runnable task = () -> holder[0]++;
```

Формально работает, но это признак того, что решение стоит пересмотреть.

---

# Closure

Замыкание — функция, которая захватывает переменные из окружающей области
видимости и продолжает иметь к ним доступ после того, как эта область завершилась.

Lambda в Java является замыканием:

```java
Supplier<String> makeGreeter() {
    String prefix = "Hello, ";
    return name -> prefix + name;  // prefix захвачен
}
```

Метод `makeGreeter()` завершился, его кадр стека уничтожен, но возвращённая lambda
по-прежнему знает значение `prefix`.

## Capture by value

Ключевой момент: Java захватывает **значение** переменной, а не саму переменную.

```java
int counter = 0;
Runnable task = () -> System.out.println(counter);
```

В момент создания lambda значение `0` копируется. Даже если бы язык разрешил
изменить `counter` дальше по коду, lambda продолжала бы печатать `0`.

Именно поэтому требование effectively final и существует: раз захватывается копия,
изменение оригинала создало бы два расходящихся значения и постоянный источник
путаницы.

## Сравнение с другими языками

В JavaScript, Groovy и Kotlin замыкание захватывает переменную:

```javascript
let counter = 0;
const task = () => console.log(counter);

counter = 5;
task();  // 5
```

Изменение видно внутри замыкания, потому что захвачена ссылка на переменную, а не
её значение на момент создания.

Java пошла другим путём:

```text
capture by reference (JS, Groovy, Kotlin)
→ замыкание видит текущее значение переменной
→ изменения снаружи отражаются внутри
→ в многопоточном коде требуется синхронизация

capture by value (Java)
→ замыкание видит значение на момент создания
→ переменная обязана быть effectively final
→ гонок по захваченной локальной переменной не возникает
```

Выбор Java продиктован многопоточностью. Lambda часто уходит в другой поток через
`executor.submit()` или parallel stream. Захват по ссылке означал бы разделяемое
изменяемое состояние в стеке чужого потока — без единого явного признака в коде.

## Что это не отменяет

Отсутствие гонки касается только самой захваченной переменной. Объект, на который
она указывает, разделяется полноценно:

```java
List<String> results = new ArrayList<>();

executor.submit(() -> results.add("a"));
executor.submit(() -> results.add("b"));
```

Ссылка `results` скопирована в каждую lambda, но `ArrayList` один на всех. Это
классическая гонка, и компилятор о ней не предупредит.

```text
Java lambda
→ замыкание
→ но замыкание по значению

capture by value
→ защищает захваченную переменную
→ не защищает объект, на который она указывает
```

---

# Method references

Method reference — сокращённая запись lambda, которая только вызывает существующий
метод.

```java
list.forEach(value -> System.out.println(value));
list.forEach(System.out::println);
```

## Четыре формы

### Статический метод

```text
ClassName::staticMethod
```

```java
Function<String, Integer> parse = Integer::parseInt;
// эквивалент: value -> Integer.parseInt(value)
```

### Метод конкретного объекта

```text
instance::method
```

```java
Logger logger = new Logger();
Consumer<String> log = logger::info;
// эквивалент: message -> logger.info(message)
```

Объект захватывается в момент создания reference.

### Метод произвольного объекта типа

```text
ClassName::instanceMethod
```

```java
Function<String, Integer> length = String::length;
// эквивалент: value -> value.length()
```

Первый параметр функционального интерфейса становится получателем вызова.

### Конструктор

```text
ClassName::new
```

```java
Supplier<ArrayList<String>> supplier = ArrayList::new;
Function<String, User> factory = User::new;
```

## Неоднозначность двух средних форм

Это классический вопрос на собеседовании.

```java
String prefix = "id-";

Function<String, Boolean> a = prefix::startsWith;
BiFunction<String, String, Boolean> b = String::startsWith;
```

В первом случае получатель зафиксирован — это `prefix`, а аргумент lambda идёт в
параметр метода:

```text
prefix::startsWith
→ value -> prefix.startsWith(value)
```

Во втором получателя нет, поэтому первый аргумент становится получателем:

```text
String::startsWith
→ (a, b) -> a.startsWith(b)
```

Одна и та же форма `ClassName::method` может означать статический метод или метод
произвольного объекта. Компилятор различает их по сигнатуре, поэтому объявление
одноимённого статического и инстанс-метода делает reference неоднозначным.

## Когда method reference не подходит

Только если тело lambda сводится к одному вызову с теми же аргументами в том же
порядке.

```java
value -> service.process(value)         // service::process
value -> service.process(value, LIMIT)  // reference невозможен
value -> process(transform(value))      // reference невозможен
value -> !value.isEmpty()               // reference невозможен
```

---

# Стандартные функциональные интерфейсы

Пакет `java.util.function` содержит готовые интерфейсы. Свои дублирующие
объявления обычно не нужны.

## Основные

| Интерфейс | Метод | Сигнатура | Смысл |
|---|---|---|---|
| `Predicate<T>` | `test` | `T → boolean` | проверка условия |
| `Function<T, R>` | `apply` | `T → R` | преобразование |
| `Consumer<T>` | `accept` | `T → void` | действие без результата |
| `Supplier<T>` | `get` | `() → T` | поставка значения |
| `UnaryOperator<T>` | `apply` | `T → T` | преобразование в тот же тип |
| `BinaryOperator<T>` | `apply` | `(T, T) → T` | свёртка двух значений |

```java
Predicate<String> notBlank = value -> !value.isBlank();
Function<User, String> toEmail = User::getEmail;
Consumer<String> log = System.out::println;
Supplier<Instant> now = Instant::now;
UnaryOperator<String> trim = String::trim;
BinaryOperator<Integer> sum = Integer::sum;
```

## Bi-варианты

```text
BiPredicate<T, U>    (T, U) → boolean
BiFunction<T, U, R>  (T, U) → R
BiConsumer<T, U>     (T, U) → void
```

`BiSupplier` не существует: у поставщика нет входа, который можно было бы удвоить.

## UnaryOperator и BinaryOperator

`UnaryOperator<T>` наследует `Function<T, T>`, а `BinaryOperator<T>` наследует
`BiFunction<T, T, T>`. Это специализации, а не отдельные семейства.

Возникает разумный вопрос: зачем они нужны, если `Function<String, String>`
выражает ровно то же самое.

Первая причина — читаемость сигнатур. Сравните:

```java
void replaceAll(Function<? super E, ? extends E> operator);
void replaceAll(UnaryOperator<E> operator);
```

Второй вариант сразу сообщает: тип на входе и выходе один и тот же. Wildcards в
первом варианте формально гибче, но смысл операции прячут.

Вторая причина — дополнительные фабричные методы, которых у `Function` нет:

```java
BinaryOperator<User> older = BinaryOperator.maxBy(
        Comparator.comparingInt(User::getAge)
);

BinaryOperator<User> younger = BinaryOperator.minBy(
        Comparator.comparingInt(User::getAge)
);
```

```java
UnaryOperator<String> identity = UnaryOperator.identity();
```

Где встречаются в стандартной библиотеке:

```java
list.replaceAll(String::trim);                    // UnaryOperator<E>

map.merge(key, 1, Integer::sum);                  // BiFunction, но по смыслу
                                                  // обычно BinaryOperator

Optional<Integer> total = numbers.stream()
        .reduce(Integer::sum);                    // BinaryOperator<T>

int sum = numbers.stream()
        .reduce(0, Integer::sum);                 // BinaryOperator<T>

Map<String, User> byEmail = users.stream()
        .collect(Collectors.toMap(
                User::getEmail,
                user -> user,
                (existing, replacement) -> existing  // BinaryOperator<U>
        ));
```

Последний пример стоит запомнить отдельно: третий аргумент `toMap()` — merge
function для разрешения конфликта ключей. Без него дубликат ключа приводит к
`IllegalStateException`.

Требование `reduce()` к `BinaryOperator` не случайно. Свёртка комбинирует
аккумулятор и элемент, а результат снова становится аккумулятором. Это возможно
только при совпадении всех трёх типов. Дополнительно операция должна быть
ассоциативной, иначе parallel stream даст другой результат:

```java
numbers.stream().reduce(0, Integer::sum);        // ассоциативна, безопасна
numbers.stream().reduce(0, (a, b) -> a - b);     // не ассоциативна, в parallel
                                                 // результат непредсказуем
```

Для примитивов существуют `IntUnaryOperator`, `IntBinaryOperator` и аналоги для
`long` и `double`. Они не наследуют `IntFunction`, потому что в примитивном
семействе нет общего обобщённого предка.

## Примитивные специализации

Обобщённые интерфейсы работают только со ссылочными типами, поэтому каждое
значение боксится:

```java
Function<Integer, Integer> f = value -> value * 2;
```

```text
int → Integer → int → Integer
```

Для горячих участков существуют специализации без боксинга:

```text
IntPredicate         int → boolean
IntFunction<R>       int → R
IntUnaryOperator     int → int
IntBinaryOperator    (int, int) → int
IntConsumer          int → void
IntSupplier          () → int
ToIntFunction<T>     T → int
IntToLongFunction    int → long
```

Аналогичные наборы существуют для `long` и `double`.

```java
IntUnaryOperator doubler = value -> value * 2; // боксинга нет
```

Именно поэтому `IntStream.sum()` работает быстрее, чем
`Stream<Integer>.reduce(0, Integer::sum)`.

## Композиция

Стандартные интерфейсы содержат default-методы для объединения.

```java
Predicate<String> notNull = Objects::nonNull;
Predicate<String> notBlank = value -> !value.isBlank();

Predicate<String> valid = notNull.and(notBlank);
Predicate<String> invalid = valid.negate();
Predicate<String> any = notNull.or(notBlank);
```

Для `Function` есть два направления:

```java
Function<String, Integer> parse = Integer::parseInt;
Function<Integer, Integer> square = value -> value * value;

Function<String, Integer> a = parse.andThen(square); // parse, потом square
Function<String, Integer> b = square.compose(parse); // parse, потом square
```

```text
f.andThen(g)  → g(f(x))
f.compose(g)  → f(g(x))
```

`Consumer` поддерживает только `andThen`, потому что результата для передачи
дальше у него нет.

---

# Функциональные интерфейсы вне java.util.function

Функциональным интерфейс делает не пакет и не аннотация, а единственный абстрактный
метод. Многие такие интерфейсы появились задолго до Java 8 и работают с lambda без
каких-либо изменений.

| Интерфейс | Пакет | Метод | Сигнатура |
|---|---|---|---|
| `Runnable` | `java.lang` | `run` | `() → void` |
| `Callable<V>` | `java.util.concurrent` | `call` | `() → V` (бросает `Exception`) |
| `Comparator<T>` | `java.util` | `compare` | `(T, T) → int` |
| `Iterable<T>` | `java.lang` | `iterator` | `() → Iterator<T>` |
| `AutoCloseable` | `java.lang` | `close` | `() → void` |
| `ActionListener` | `java.awt.event` | `actionPerformed` | `ActionEvent → void` |

```java
Runnable task = () -> log("started");
Callable<String> loader = () -> Files.readString(path);
Comparator<User> byAge = (a, b) -> Integer.compare(a.getAge(), b.getAge());
```

Именно поэтому старый код с анонимными классами почти всегда переписывается на
lambda без правки интерфейсов.

## Runnable и Callable

Пара, которую спрашивают чаще остальных. Различие важно для `ExecutorService`:

```text
Runnable
→ результата нет
→ checked exceptions не объявляет
→ executor.execute() и executor.submit()

Callable<V>
→ возвращает V
→ объявляет throws Exception
→ только executor.submit()
```

Практическое следствие: внутри `Runnable` checked exception обязан быть обработан
на месте, внутри `Callable` — нет, он придёт вызывающему через
`ExecutionException` из `Future.get()`.

Отсюда же неоднозначность при передаче lambda в `submit()`:

```java
executor.submit(() -> doWork());
```

Если `doWork()` возвращает значение, компилятор выберет `Callable`. Если `void` —
`Runnable`. Это влияет на тип возвращаемого `Future`.

## Comparator

Отдельно стоит того, чтобы знать его фабрики: на собеседовании они всплывают чаще,
чем `java.util.function`.

```java
Comparator<User> byName = Comparator.comparing(User::getName);

Comparator<User> byAgeThenName = Comparator
        .comparingInt(User::getAge)
        .thenComparing(User::getName);

Comparator<User> byNameDesc = Comparator
        .comparing(User::getName)
        .reversed();

Comparator<User> nullsLast = Comparator.nullsLast(
        Comparator.comparing(User::getName)
);
```

`comparingInt()` предпочтительнее `comparing()` для примитивов по той же причине,
что и `IntFunction`: нет боксинга на каждом сравнении.

Хотя `Comparator` объявляет `equals(Object)`, он остаётся функциональным: это
публичный метод `Object`, и он не учитывается.

Порядок вычисления при композиции предикатов сохраняет короткое замыкание:

```java
notNull.and(notBlank)
```

Если `notNull` вернул `false`, `notBlank` не вызывается. Это существенно, когда
второй предикат разыменовывает значение.

---

# Lambda и исключения

Стандартные функциональные интерфейсы не объявляют checked exceptions.

```java
Function<Path, String> read = path -> Files.readString(path); // не компилируется
```

`Files.readString()` бросает `IOException`, а `Function.apply()` его не объявляет.

Варианты решения.

## Обработка внутри

```java
Function<Path, String> read = path -> {
    try {
        return Files.readString(path);
    } catch (IOException e) {
        throw new UncheckedIOException(e);
    }
};
```

## Собственный интерфейс

```java
@FunctionalInterface
interface ThrowingFunction<T, R> {
    R apply(T value) throws Exception;
}
```

Подходит, когда контроль над API есть. Со `Stream` не сработает: он принимает
стандартные интерфейсы.

Оборачивание в unchecked внутри stream-конвейера — распространённая практика, но
у неё есть цена: исключение теряет место возникновения в конвейере, а stack trace
из-за `invokedynamic` становится менее читаемым.

---

# Типичные ошибки

## Считать lambda объектом-функцией

Lambda — реализация функционального интерфейса. Тип у неё всегда есть, и берётся он
из контекста.

## Ожидать, что this в lambda укажет на саму lambda

`this` внутри lambda означает экземпляр окружающего класса. Ссылки на «саму
lambda» не существует, поэтому рекурсивную lambda нельзя написать напрямую через
локальную переменную — она ещё не инициализирована в момент захвата.

## Думать, что @FunctionalInterface обязательна

Интерфейс с одним абстрактным методом функционален и без аннотации. Аннотация
добавляет проверку.

## Считать, что effectively final делает состояние неизменяемым

Ограничение относится к переменной, а не к объекту. Изменяемую коллекцию,
захваченную lambda, по-прежнему можно испортить из нескольких потоков.

## Собирать результат в общую коллекцию из parallel stream

```java
List<String> result = new ArrayList<>();
stream.parallel().forEach(result::add); // гонка
```

`ArrayList` не потокобезопасен. Нужен `collect(Collectors.toList())`.

## Использовать forEach вместо map

```java
stream.forEach(value -> results.add(transform(value)));
```

Побочный эффект вместо преобразования. Правильнее:

```java
stream.map(this::transform).toList();
```

## Игнорировать примитивные специализации в горячем коде

`Function<Integer, Integer>` боксит каждое значение. В цикле на миллионы итераций
это заметно.

## Считать, что lambda всегда быстрее анонимного класса

Первый вызов lambda дороже: `invokedynamic` требует линковки call site через
`LambdaMetafactory`. Выигрыш появляется потом, на переиспользовании и на
отсутствии лишних классов. Для одного вызова разница несущественна.

## Писать длинные lambda

Тело на пятнадцать строк лучше вынести в метод и сослаться на него. Method
reference получает имя, а имя объясняет намерение.

---

# Вопросы на собеседовании

### 1. Что такое функциональный интерфейс?

**Ответ:** интерфейс ровно с одним абстрактным методом. Default, static и private
методы не учитываются, публичные методы `Object` тоже.

### 2. Обязательна ли аннотация @FunctionalInterface?

**Ответ:** нет. Она включает проверку компилятора и фиксирует намерение, но не
влияет на возможность использовать интерфейс с lambda.

### 3. Есть ли у lambda собственный тип?

**Ответ:** нет. Тип определяется target type — контекстом использования. Поэтому
`var action = () -> doWork()` не компилируется.

### 4. Чем lambda отличается от анонимного класса?

**Ответ:** главное различие — `this`. В анонимном классе он указывает на его
собственный экземпляр, в lambda — на экземпляр внешнего класса. Lambda не создаёт
новую область видимости, не может иметь полей, реализует только функциональный
интерфейс и компилируется в `invokedynamic`, а не в отдельный класс.

### 5. Что такое effectively final?

**Ответ:** локальная переменная, которая не объявлена `final`, но фактически не
меняется после инициализации. Только такие переменные lambda может захватывать.

### 6. Почему это ограничение существует?

**Ответ:** захватывается копия значения, потому что lambda может пережить кадр
стека метода. Разрешение изменять переменную породило бы неоднозначность, какое
значение видит lambda, и открыло бы гонки без синхронизации.

### 7. Можно ли изменять объект, захваченный lambda?

**Ответ:** да. Ограничение относится к переменной, а не к состоянию объекта.
`list.add()` внутри lambda компилируется, но потокобезопасность нужно обеспечивать
отдельно.

### 8. Какие есть виды method reference?

**Ответ:** статический метод (`Integer::parseInt`), метод конкретного объекта
(`logger::info`), метод произвольного объекта типа (`String::length`) и конструктор
(`ArrayList::new`).

### 9. Чем `String::length` отличается от `value::length`?

**Ответ:** в первом случае получателем становится первый аргумент функционального
интерфейса. Во втором получатель зафиксирован — это объект `value`, захваченный при
создании reference.

### 10. Как lambda реализована на уровне байт-кода?

**Ответ:** тело компилируется в синтетический метод класса, а в точке использования
ставится инструкция `invokedynamic`. При первом выполнении `LambdaMetafactory`
создаёт объект-реализацию интерфейса и линкует call site. Отдельного `.class`-файла
на этапе компиляции не создаётся.

### 11. Зачем нужны IntFunction, IntPredicate и подобные?

**Ответ:** чтобы избежать боксинга. Обобщённые интерфейсы работают только со
ссылочными типами, поэтому каждое примитивное значение оборачивается.

### 12. В чём разница между andThen и compose?

**Ответ:** `f.andThen(g)` вычисляет `g(f(x))`, `f.compose(g)` вычисляет `f(g(x))`.

### 13. Почему нет BiSupplier?

**Ответ:** `Supplier` не принимает аргументов, поэтому удваивать нечего.

### 14. Может ли lambda бросить checked exception?

**Ответ:** только если функциональный интерфейс объявил его в сигнатуре. Стандартные
интерфейсы из `java.util.function` этого не делают, поэтому checked exception нужно
обработать внутри или обернуть в unchecked.

### 15. Что произойдёт при `Object o = () -> doWork()`?

**Ответ:** ошибка компиляции. `Object` не функциональный интерфейс, target type
вывести невозможно. Работает `Object o = (Runnable) () -> doWork()`.

### 16. Является ли lambda в Java замыканием?

**Ответ:** да. Она захватывает переменные окружающей области и сохраняет к ним
доступ после её завершения. Но захват идёт по значению, а не по ссылке на
переменную, в отличие от JavaScript, Groovy или Kotlin.

### 17. В чём разница между capture by value и capture by reference?

**Ответ:** при захвате по значению копируется значение на момент создания lambda,
поэтому переменная обязана быть effectively final. При захвате по ссылке замыкание
видит текущее значение переменной и её изменения снаружи. Java выбрала первый
вариант, чтобы lambda можно было безопасно передавать в другой поток.

### 18. Зачем нужны UnaryOperator и BinaryOperator, если есть Function?

**Ответ:** это специализации для случая, когда входной и выходной типы совпадают.
Они делают сигнатуры API читаемее и добавляют фабрики `identity()`, `minBy()`,
`maxBy()`, которых у `Function` нет.

### 19. Почему reduce требует BinaryOperator, а не BiFunction?

**Ответ:** результат свёртки снова становится аккумулятором, поэтому все три типа
обязаны совпадать. Дополнительно операция должна быть ассоциативной, иначе parallel
stream даст другой результат.

### 20. Есть ли функциональные интерфейсы вне java.util.function?

**Ответ:** да. `Runnable`, `Callable`, `Comparator`, `Iterable`, `AutoCloseable` и
многие интерфейсы слушателей появились раньше Java 8 и работают с lambda без
изменений. Функциональным интерфейс делает единственный абстрактный метод, а не
пакет.

### 21. Чем Runnable отличается от Callable?

**Ответ:** `Runnable` не возвращает результат и не объявляет checked exceptions,
`Callable<V>` возвращает `V` и объявляет `throws Exception`. В `ExecutorService`
оба принимает `submit()`, но `execute()` — только `Runnable`.

---

# Что нужно запомнить

```text
функциональный интерфейс
→ ровно один абстрактный метод
→ default, static, private и методы Object не в счёт

lambda
→ не имеет собственного типа
→ тип берётся из target type

this в lambda
→ внешний экземпляр
→ не сама lambda и не анонимный объект

lambda не создаёт новую область видимости
→ затенить локальную переменную нельзя

effectively final
→ переменную нельзя переприсваивать
→ объект при этом остаётся изменяемым

lambda — это замыкание
→ но замыкание по значению
→ capture by value, а не capture by reference
→ отсюда и требование effectively final

функциональный интерфейс определяется методом, а не пакетом
→ Runnable, Callable, Comparator, Iterable, AutoCloseable

Runnable  → () → void, checked не объявляет
Callable  → () → V, throws Exception

UnaryOperator<T>  extends Function<T, T>
BinaryOperator<T> extends BiFunction<T, T, T>
→ ради читаемости сигнатур и фабрик identity / minBy / maxBy

reduce требует BinaryOperator
→ аккумулятор и результат одного типа
→ операция должна быть ассоциативной

method reference
→ ClassName::staticMethod
→ instance::method
→ ClassName::instanceMethod
→ ClassName::new

примитивные специализации
→ существуют ради отсутствия боксинга

andThen  → g(f(x))
compose  → f(g(x))

стандартные интерфейсы
→ checked exceptions не объявляют
```