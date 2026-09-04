# OOP, Object, String и Wrapper Classes в Java

# Основные принципы ООП

Классическая четвёрка принципов ООП:

```text
Инкапсуляция
Наследование
Полиморфизм
Абстракция
```

Композиция не входит в классическую четвёрку, но является важным принципом проектирования.

# Инкапсуляция

Инкапсуляция — это сокрытие внутреннего состояния и деталей реализации за контролируемым интерфейсом.

Плохой вариант:

```java
class User {
    public int age;
}
```

Любой код может записать некорректное значение:

```java
user.age = -100;
```

Лучше:

```java
class User {

    private int age;

    public void setAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException();
        }

        this.age = age;
    }
}
```

Класс сам контролирует допустимое состояние.

Важно:

> Инкапсуляция — это не просто `private` + getter/setter.

Часто правильнее предоставить бизнес-операцию:

```java
account.deposit(amount);
```

вместо:

```java
account.setBalance(...);
```

# Абстракция

Абстракция — выделение существенного контракта и сокрытие деталей реализации.

```java
interface PaymentService {
    void pay(Order order);
}
```

Коду, использующему `PaymentService`, не обязательно знать, как выполняется HTTP-запрос, где хранятся данные, как устроена авторизация или какой платёжный провайдер используется.

```text
инкапсуляция
→ как скрыть и защитить внутренности объекта

абстракция
→ какие детали пользователю объекта вообще не нужно знать
```

# Наследование

Наследование выражает отношение:

```text
is-a
```

```java
class Animal {
}

class Dog extends Animal {
}
```

```text
Dog is an Animal
```

# Композиция

Композиция выражает отношение:

```text
has-a
```

```java
class Car {
    private Engine engine;
}
```

```text
Car has an Engine
```

Композиция может быть как `1:1`, так и `1:n`.

```java
class Car {
    private List<Wheel> wheels;
}
```

Часто применяется принцип:

```text
favor composition over inheritance
```

Композиция обычно уменьшает связанность и позволяет легче менять реализацию.

# Полиморфизм

Полиморфизм позволяет работать через общий тип, но получать разное поведение в зависимости от реального объекта.

```java
class Animal {
    void speak() {
        System.out.println("Animal");
    }
}

class Dog extends Animal {
    @Override
    void speak() {
        System.out.println("Dog");
    }
}
```

```java
Animal animal = new Dog();
animal.speak();
```

Результат:

```text
Dog
```

Для переопределённых instance-методов реализация выбирается во время выполнения по реальному типу объекта.

# Тип ссылки и реальный тип

```java
class Animal {
    void speak() {
    }
}

class Dog extends Animal {
    @Override
    void speak() {
    }

    void fetch() {
    }
}
```

```java
Animal animal = new Dog();
```

Так можно:

```java
animal.speak();
```

Так нельзя:

```java
animal.fetch();
```

Потому что компилятор видит ссылку типа `Animal`, а в `Animal` нет `fetch()`.

```text
compile time
→ тип ссылки определяет, какие методы доступны

runtime
→ реальный тип определяет, какая override-реализация вызывается
```

# Overriding

Overriding — переопределение метода родителя в наследнике.

```java
class Animal {
    void speak() {
        System.out.println("Animal");
    }
}

class Dog extends Animal {
    @Override
    void speak() {
        System.out.println("Dog");
    }
}
```

```text
overriding
→ наследование
→ та же сигнатура
→ другая реализация
→ runtime
```

# Overloading

Overloading — несколько методов с одним именем и разными параметрами.

```java
class Printer {
    void print(String value) {
    }

    void print(int value) {
    }
}
```

```text
overloading
→ одно имя
→ разные параметры
→ compile time
```

# Нельзя перегрузить метод только по возвращаемому типу

Так нельзя:

```java
int getValue() {
    return 1;
}

String getValue() {
    return "1";
}
```

Возвращаемый тип сам по себе не различает overload.

# Overloading и тип ссылки

```java
class Parent {
    void print(Object value) {
        System.out.println("Object");
    }
}

class Child extends Parent {
    void print(String value) {
        System.out.println("String");
    }
}
```

```java
Parent obj = new Child();
obj.print("Java");
```

Результат:

```text
Object
```

На этапе компиляции через ссылку `Parent` виден только `print(Object)`.

# Сначала overloading, потом overriding

```java
class Parent {
    void print(Object value) {
        System.out.println("Parent Object");
    }
}

class Child extends Parent {
    @Override
    void print(Object value) {
        System.out.println("Child Object");
    }

    void print(String value) {
        System.out.println("Child String");
    }
}
```

```java
Parent obj = new Child();
obj.print("Java");
```

Результат:

```text
Child Object
```

Логика:

```text
1. compile time
   → выбирается сигнатура print(Object)

2. runtime
   → выбирается реализация Child.print(Object)
```

# Overload и null

```java
void print(String value) {
}

void print(Integer value) {
}
```

```java
print(null);
```

Не скомпилируется:

```text
reference to print is ambiguous
```

Но:

```java
void print(Object value) {
}

void print(String value) {
}
```

```java
print(null);
```

вызовет `print(String)`, потому что `String` более специфичен, чем `Object`.

# Правила overriding: access modifiers

При overriding нельзя уменьшать видимость метода.

Нельзя:

```java
class Parent {
    public void print() {
    }
}

class Child extends Parent {
    @Override
    protected void print() {
    }
}
```

Можно расширять:

```java
class Parent {
    protected void print() {
    }
}

class Child extends Parent {
    @Override
    public void print() {
    }
}
```

# Ковариантный возвращаемый тип

```java
class Parent {
    Animal create() {
        return new Animal();
    }
}

class Child extends Parent {
    @Override
    Dog create() {
        return new Dog();
    }
}
```

Это допустимо, если `Dog extends Animal`.

Наследник может возвращать более конкретный тип.

# Checked exceptions при overriding

```java
class Parent {
    void read() throws IOException {
    }
}
```

Нельзя:

```java
class Child extends Parent {
    @Override
    void read() throws Exception {
    }
}
```

Можно:

```java
void read() throws IOException
```

Можно сузить:

```java
void read() throws FileNotFoundException
```

Можно убрать checked exception:

```java
void read()
```

```text
checked exception при overriding
→ оставить
→ сузить
→ убрать
→ нельзя расширить
```

# Unchecked exceptions при overriding

```java
class Parent {
    void read() {
    }
}

class Child extends Parent {
    @Override
    void read() throws IllegalStateException {
    }
}
```

Это корректно, потому что `IllegalStateException` — unchecked exception.

# private и overriding

```java
class Parent {
    private void test() {
    }
}

class Child extends Parent {
    void test() {
    }
}
```

`Child.test()` — новый метод, а не overriding. `private`-метод родителя не виден наследнику.

# final

Для разных сущностей:

```text
final variable
→ нельзя переназначить

final method
→ нельзя override

final class
→ нельзя extends
```

Пример:

```java
final class Parent {
}
```

От такого класса наследоваться нельзя.

# abstract и final

Так нельзя:

```java
abstract final class Example {
}
```

Потому что:

```text
abstract → предполагает наследование
final    → запрещает наследование
```

# Abstract class

Абстрактный класс нельзя создать напрямую:

```java
abstract class Animal {
}
```

Но он может иметь:

- поля;
- обычные методы;
- abstract-методы;
- конструкторы;
- методы с любыми допустимыми модификаторами доступа.

Пример:

```java
abstract class Animal {

    protected final String name;

    protected Animal(String name) {
        this.name = name;
    }

    abstract void speak();

    void sleep() {
        System.out.println("sleep");
    }
}
```

# Abstract class и interface

`abstract class` обычно выбирают, когда нужны:

- общее состояние;
- общая реализация;
- конструкторы;
- protected-члены;
- общий базовый тип тесно связанных классов.

`interface` чаще используют для контракта поведения:

```java
interface Flyable {
    void fly();
}
```

Класс может наследоваться только от одного класса, но реализовывать несколько интерфейсов.

# Default methods

Интерфейс может иметь метод с реализацией:

```java
interface A {
    default void print() {
        System.out.println("A");
    }
}
```

# Конфликт default methods

```java
interface A {
    default void print() {
        System.out.println("A");
    }
}

interface B {
    default void print() {
        System.out.println("B");
    }
}

class Example implements A, B {
}
```

Не скомпилируется. Класс должен разрешить конфликт:

```java
class Example implements A, B {
    @Override
    public void print() {
        A.super.print();
    }
}
```

# Class wins over interface

```java
class Parent {
    public void print() {
        System.out.println("Parent");
    }
}

interface A {
    default void print() {
        System.out.println("A");
    }
}

class Child extends Parent implements A {
}
```

```java
new Child().print();
```

Выведет:

```text
Parent
```

Метод класса имеет приоритет над default-методом интерфейса.

# Более специфичный интерфейс

```java
interface A {
    default void print() {
        System.out.println("A");
    }
}

interface B extends A {
    @Override
    default void print() {
        System.out.println("B");
    }
}

class Example implements B {
}
```

```java
new Example().print();
```

Выведет:

```text
B
```

# Static methods интерфейса

```java
interface A {
    static void print() {
        System.out.println("A");
    }
}
```

Вызывается:

```java
A.print();
```

Static-метод интерфейса не наследуется реализующим классом.

# Static methods класса и method hiding

```java
class Animal {
    static void speak() {
        System.out.println("Animal");
    }
}

class Dog extends Animal {
    static void speak() {
        System.out.println("Dog");
    }
}
```

```java
Animal animal = new Dog();
animal.speak();
```

Выведет:

```text
Animal
```

Static-методы не участвуют в runtime polymorphism. Это method hiding.

# Поля и field hiding

```java
class Parent {
    int value = 10;
}

class Child extends Parent {
    int value = 20;
}
```

```java
Parent obj = new Child();
System.out.println(obj.value);
```

Выведет:

```text
10
```

Поля выбираются по типу ссылки.

# Поля и методы вместе

```java
class Parent {
    int value = 10;

    int getValue() {
        return value;
    }
}

class Child extends Parent {
    int value = 20;

    @Override
    int getValue() {
        return value;
    }
}
```

```java
Parent obj = new Child();

System.out.println(obj.value);
System.out.println(obj.getValue());
```

Результат:

```text
10
20
```

# this и super

```java
class Parent {
    int value = 10;
}

class Child extends Parent {
    int value = 20;

    void print() {
        System.out.println(super.value);
        System.out.println(this.value);
    }
}
```

```text
super.value → поле родителя
this.value  → поле текущего объекта
```

# super.method()

```java
class Parent {
    void print() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    @Override
    void print() {
        super.print();
        System.out.println("Child");
    }
}
```

Результат:

```text
Parent
Child
```

# Cast не отключает полиморфизм

```java
Child child = new Child();

((Parent) child).print();
```

Если `print()` переопределён, всё равно будет вызван `Child.print()`.

Чтобы вызвать именно реализацию родителя из наследника:

```java
super.print();
```

# Конструкторы не наследуются

Конструкторы родителя не становятся конструкторами наследника автоматически.

```java
class Parent {
    Parent(int value) {
    }
}
```

Это не создаёт автоматически `Child(int value)`.

# Порядок вызова конструкторов

```java
class Parent {
    Parent() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    Child() {
        System.out.println("Child");
    }
}
```

```java
new Child();
```

Вывод:

```text
Parent
Child
```

# Неявный super()

Если конструктор наследника не вызывает `this(...)` или `super(...)`, компилятор пытается вставить:

```java
super();
```

Если у родителя конструктора без аргументов нет, нужно вызвать существующий явно:

```java
class Child extends Parent {
    Child() {
        super(10);
    }
}
```

# super() и this() должны быть первыми

Так нельзя:

```java
Child() {
    System.out.println("Before");
    super();
}
```

`super(...)` или `this(...)` должен быть первым вызовом конструктора.

# Цепочка this() и super()

```java
class Parent {
    Parent(int value) {
        System.out.println("Parent(int)");
    }
}

class Child extends Parent {
    Child() {
        this(10);
        System.out.println("Child()");
    }

    Child(int value) {
        super(value);
        System.out.println("Child(int)");
    }
}
```

```java
new Child();
```

Результат:

```text
Parent(int)
Child(int)
Child()
```

# Вызов overridable method из конструктора

```java
class Parent {
    Parent() {
        print();
    }

    void print() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    private int value = 20;

    @Override
    void print() {
        System.out.println(value);
    }
}
```

```java
new Child();
```

Выведет:

```text
0
```

`Child.print()` вызывается до того, как поле `value` получит значение `20`.

Поэтому переопределяемые методы из конструктора обычно вызывать не следует.

# private method в конструкторе

```java
class Parent {
    private void print() {
        System.out.println("Parent");
    }

    Parent() {
        print();
    }
}

class Child extends Parent {
    void print() {
        System.out.println("Child");
    }
}
```

```java
new Child();
```

Выведет:

```text
Parent
```

`private`-метод не переопределяется.

# Liskov Substitution Principle

Плохая модель:

```java
class Bird {
    void fly() {
    }
}

class Penguin extends Bird {
}
```

Если базовый тип обещает способность летать, `Penguin` ломает ожидания.

Лучше:

```java
class Bird {
}

interface Flyable {
    void fly();
}

class Sparrow extends Bird implements Flyable {
    @Override
    public void fly() {
    }
}

class Penguin extends Bird {
}
```

# Dependency on abstraction

Жёсткая зависимость:

```java
class ReportService {
    private PdfGenerator generator = new PdfGenerator();
}
```

Лучше:

```java
class ReportService {

    private final ReportGenerator generator;

    ReportService(ReportGenerator generator) {
        this.generator = generator;
    }
}

interface ReportGenerator {
    void generate();
}
```

Так класс зависит от абстракции, а реализацию можно подменять.

# Object

Все Java-классы прямо или косвенно наследуются от `java.lang.Object`.

Основные методы:

```text
equals(Object obj)
hashCode()
toString()
getClass()
clone()
wait()
notify()
notifyAll()
```

`equals/hashCode` и `wait/notify` обычно разбираются отдельными темами.

# Object.toString()

Если `toString()` не переопределён:

```java
class User {
}
```

```java
System.out.println(new User());
```

результат примерно:

```text
com.example.User@3f99bd52
```

Упрощённо стандартный формат:

```java
getClass().getName()
        + "@"
        + Integer.toHexString(hashCode());
```

Часть после `@` не является гарантированным адресом объекта в памяти.

# getClass()

```java
Animal animal = new Dog();

animal.getClass() == Animal.class // false
animal.getClass() == Dog.class    // true
```

`getClass()` возвращает точный runtime-класс объекта.

# getClass и instanceof

```java
animal instanceof Animal // true
animal instanceof Dog    // true
```

```text
getClass()
→ точный runtime-класс
→ возвращает Class<?>

instanceof
→ проверяет совместимость по иерархии
→ возвращает boolean
```

# String

`String` — immutable-класс.

```java
String s = "Java";

s.concat(" Backend");

System.out.println(s);
```

Выведет:

```text
Java
```

`concat()` возвращает новый `String`, но исходный объект не меняется.

# String Pool

```java
String a = "Java";
String b = "Java";
```

Обычно:

```java
a == b // true
```

Обе ссылки указывают на один объект из String Pool.

# new String()

```java
String a = "Java";
String b = new String("Java");
```

```java
a == b       // false
a.equals(b)  // true
```

`new String()` создаёт отдельный объект.

# Compile-time concatenation

```java
String a = "Ja" + "va";
String b = "Java";
```

```java
a == b // true
```

Компилятор сворачивает константное выражение до `"Java"`.

# Runtime concatenation

```java
String part = "Ja";

String a = part + "va";
String b = "Java";
```

Обычно:

```java
a == b       // false
a.equals(b)  // true
```

Конкатенация выполняется во время выполнения.

# final compile-time constant

```java
final String part = "Ja";

String a = part + "va";
String b = "Java";
```

Компилятор может свернуть выражение, поэтому:

```java
a == b // true
```

# intern()

```java
String a = new String("Java");
String b = a.intern();
String c = "Java";
```

```java
a == b // false
b == c // true
```

`intern()` возвращает каноническую ссылку из String Pool.

# StringBuilder

```text
mutable
not thread-safe
```

```java
StringBuilder builder = new StringBuilder();

builder.append("Java");
builder.append(" ");
builder.append("Backend");

String result = builder.toString();
```

`append()` меняет существующий буфер.

# StringBuffer

```text
mutable
thread-safe
```

Похож на `StringBuilder`, но его основные методы синхронизированы.

# Wrapper Classes

| Примитив | Wrapper |
|---|---|
| `byte` | `Byte` |
| `short` | `Short` |
| `int` | `Integer` |
| `long` | `Long` |
| `float` | `Float` |
| `double` | `Double` |
| `char` | `Character` |
| `boolean` | `Boolean` |

Wrapper-классы являются объектами.

# Boxing

```text
primitive → wrapper
```

```java
int value = 10;
Integer boxed = value;
```

Упрощённо:

```java
Integer boxed = Integer.valueOf(value);
```

# Unboxing

```text
wrapper → primitive
```

```java
Integer boxed = 10;
int value = boxed;
```

Упрощённо:

```java
int value = boxed.intValue();
```

# Unboxing null

```java
Integer number = null;

int value = number;
```

Код компилируется, но во время выполнения будет:

```text
NullPointerException
```

# Integer Cache

При autoboxing используется `Integer.valueOf()`.

Как минимум диапазон:

```text
-128 .. 127
```

кэшируется.

```java
Integer a = 127;
Integer b = 127;

a == b // true
```

Но:

```java
Integer a = 128;
Integer b = 128;

a == b // обычно false
```

# equals у Integer

```java
Integer a = 1000;
Integer b = 1000;

a.equals(b); // true
```

`equals()` сравнивает числовое значение для объектов того же wrapper-типа.

# Integer == int

```java
Integer a = 100;
int b = 100;

a == b // true
```

Происходит unboxing:

```text
Integer → int
```

после чего сравниваются примитивы.

# null и ==

```java
Integer a = null;
Integer b = 10;

a == b // false
```

Сравниваются ссылки.

Но:

```java
Integer a = null;

a == 10
```

приведёт к `NullPointerException`, потому что потребуется unboxing.

# Разные wrapper-типы

```java
Integer a = 10;
Long b = 10L;

a.equals(b); // false
```

`Integer.equals()` не выполняет числовое приведение к `Long`.

Но:

```java
a.intValue() == b.longValue()
```

даст:

```text
true
```

потому что сравниваются примитивы, а `int` расширяется до `long`.

# compareTo()

```java
Integer a = 128;
Integer b = 128;

a.compareTo(b); // 0
```

```text
< 0 → меньше
  0 → равно
> 0 → больше
```

# Unboxing + widening

```java
Integer number = 100;
long value = number;
```

Происходит:

```text
Integer → int → long
unboxing   widening
```

# Long value = 100

Так нельзя:

```java
Long value = 100;
```

Литерал `100` имеет тип `int`, а цепочка `int → long → Long` автоматически не выполняется.

Нужно:

```java
Long value = 100L;
```

# Integer value = 100L

Так нельзя:

```java
Integer value = 100L;
```

Нужно было бы выполнить narrowing `long → int`, который автоматически не происходит.

# Number value = 100

Так можно:

```java
Number value = 100;
```

Происходит:

```text
int → Integer → Number
boxing          widening reference
```

# Integer++

```java
Integer number = 10;

number++;
```

Упрощённо:

```text
Integer(10)
→ unboxing
→ int 10
→ +1
→ int 11
→ boxing
→ Integer(11)
→ новая ссылка записывается в number
```

Исходный `Integer` не изменяется.

# Типичные ошибки

- Путать overloading и overriding.
- Считать static-методы полиморфными.
- Считать поля полиморфными.
- Пытаться override `private`-метод.
- Сужать visibility при overriding.
- Расширять checked exception при overriding.
- Считать конструкторы наследуемыми.
- Забывать про `super(...)`.
- Вызывать overridable-метод из конструктора.
- Считать `String` изменяемым.
- Сравнивать строки через `==`.
- Сравнивать значения wrapper-классов через `==`.
- Забывать, что unboxing `null` приводит к `NullPointerException`.

# Краткая памятка

```text
ООП:
инкапсуляция
наследование
полиморфизм
абстракция
```

```text
наследование → is-a
композиция   → has-a
```

```text
overloading
→ compile time

overriding
→ runtime
```

```text
static method
→ hiding

field
→ тип ссылки

override method
→ реальный тип
```

```text
final variable → нельзя переназначить
final method   → нельзя override
final class    → нельзя extends
```

```text
abstract class
→ поля
→ конструкторы
→ обычные методы
→ abstract methods
→ нельзя new
```

```text
interface
→ контракт
→ default/static/private methods
→ несколько implements
```

```text
String
→ immutable

StringBuilder
→ mutable
→ not thread-safe

StringBuffer
→ mutable
→ thread-safe
```

```text
boxing:
int → Integer

unboxing:
Integer → int
```

```text
Integer null
→ unboxing
→ NullPointerException
```

```text
Integer Cache
→ минимум -128..127
```

```text
wrapper == wrapper
→ ссылки

wrapper.equals(wrapper)
→ значение + совместимый wrapper-тип

wrapper == primitive
→ unboxing
→ сравнение примитивов
```

# Вопросы для самопроверки

1. Какие четыре принципа ООП обычно называют основными?
2. Что такое инкапсуляция?
3. Чем абстракция отличается от инкапсуляции?
4. Что означает отношение `is-a`?
5. Что означает отношение `has-a`?
6. Когда композиция предпочтительнее наследования?
7. Что такое полиморфизм?
8. Чем тип ссылки отличается от реального типа объекта?
9. Чем overriding отличается от overloading?
10. На каком этапе выбирается overload?
11. На каком этапе выбирается override-реализация?
12. Можно ли перегрузить метод только изменением return type?
13. Что такое covariant return type?
14. Можно ли сузить visibility при overriding?
15. Можно ли расширить checked exception при overriding?
16. Можно ли добавить unchecked exception при overriding?
17. Почему `private`-метод не переопределяется?
18. Что означает `final` для переменной, метода и класса?
19. Почему нельзя совместить `abstract` и `final` у класса?
20. Что может содержать abstract class?
21. Чем abstract class отличается от interface?
22. Что такое default method?
23. Что происходит при конфликте двух default-методов?
24. Что означает правило `class wins over interface`?
25. Наследуются ли static-методы интерфейса?
26. Что такое method hiding?
27. Почему поля не участвуют в runtime polymorphism?
28. Что означают `this` и `super`?
29. Наследуются ли конструкторы?
30. Что делает неявный `super()`?
31. Почему `super()` и `this()` должны быть первыми?
32. Почему опасно вызывать overridable-методы из конструктора?
33. Почему cast к родительскому типу не отключает overriding?
34. Какие методы `Object` нужно знать?
35. Что возвращает стандартный `Object.toString()`?
36. Чем `getClass()` отличается от `instanceof`?
37. Почему `String` immutable?
38. Что такое String Pool?
39. Чем `"Java"` отличается от `new String("Java")`?
40. Когда конкатенация строк выполняется на этапе компиляции?
41. Что делает `intern()`?
42. Чем `StringBuilder` отличается от `String`?
43. Чем `StringBuffer` отличается от `StringBuilder`?
44. Что такое boxing?
45. Что такое unboxing?
46. Что произойдёт при unboxing `null`?
47. Что такое Integer Cache?
48. Почему нельзя сравнивать значения `Integer` через `==`?
49. Почему `Integer(10).equals(Long(10))` возвращает `false`?
50. Что происходит при `Integer == int`?
51. Как работает `compareTo()` у wrapper-классов?
52. Почему `Long value = 100` не компилируется?
53. Почему `Integer value = 100L` не компилируется?
54. Почему `Number value = 100` компилируется?
55. Как работает `number++`, если `number` имеет тип `Integer`?

---

## См. также

- [`03-equals-hashcode.md`](03-equals-hashcode.md) — подробный разбор контракта
- [`08-functional-interfaces-lambda.md`](08-functional-interfaces-lambda.md) —
  анонимные классы против lambda, разрешение default-методов у функциональных
  интерфейсов
- [`../jvm/01-jvm-memory.md`](../jvm/01-jvm-memory.md) — String Pool и передача
  параметров по значению