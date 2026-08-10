# Java Memory Model

## JVM Runtime Data Areas и Java Memory Model

JVM Runtime Data Areas и Java Memory Model описывают разные стороны выполнения
Java-программы.

JVM Runtime Data Areas отвечают примерно на вопрос:

```text
Какие логические области памяти существуют во время работы JVM?
```

К ним относятся:

- Heap
- JVM Stack
- Method Area
- PC Register
- Native Method Stack

Java Memory Model, или JMM, отвечает на другой вопрос:

```text
Какие гарантии существуют при взаимодействии нескольких потоков
с общей памятью?
```

Главные свойства, о которых приходится рассуждать:

- visibility — когда один поток обязан увидеть запись другого потока
- atomicity — может ли операция наблюдаться как неделимое действие
- ordering — какие отношения порядка обязаны соблюдать потоки

```text
JVM Runtime Data Areas
→ логическая организация памяти во время выполнения

Java Memory Model
→ правила наблюдения действий между потоками
```

JMM не определяет, где физически лежит конкретная переменная. Она задаёт
допустимое поведение программы и гарантии, которые получают корректно
синхронизированные потоки.

Фраза «у каждого потока своя копия Heap» не является корректным описанием JMM.
Heap в модели Runtime Data Areas является общей областью. Для рассуждения о JMM
важны действия чтения и записи, синхронизирующие действия и отношения между ними,
а не воображаемое физическое копирование всего Heap.

## Visibility

Visibility, или видимость, отвечает на вопрос: когда запись одного потока обязана
стать наблюдаемой другим потоком?

Рассмотрим общий флаг:

```java
private boolean ready = false;

void writer() {
    ready = true;
}

void reader() {
    while (!ready) {
    }
}
```

Один поток может выполнить `ready = true`. Однако между этой записью и чтением
`ready` другим потоком нет синхронизации. Поэтому JMM не даёт reader требуемой
гарантии видимости записи.

Из исходного кода нельзя заключить:

```text
writer записал true
→ reader обязательно немедленно увидит true
→ цикл обязательно завершится
```

Обычное чтение общей переменной нельзя использовать как механизм межпоточной
синхронизации. Проблему можно решить, например, объявив флаг `volatile`:

```java
private volatile boolean ready;
```

Запись и последующее чтение этого поля образуют требуемое отношение
happens-before.

Другой вариант — обращаться к состоянию под одним монитором:

```java
private boolean ready;

synchronized void markReady() {
    ready = true;
}

synchronized boolean isReady() {
    return ready;
}
```

Освобождение монитора writer-потоком связано с последующим захватом того же
монитора reader-потоком. `synchronized` поэтому даёт не только взаимное
исключение, но также гарантии visibility и ordering.

## Atomicity

Atomicity, или атомарность, означает, что действие наблюдается как неделимое:
другой поток не может вклиниться внутрь него и увидеть промежуточные шаги.

Выражение:

```java
count++;
```

логически состоит из нескольких действий:

```text
read count
→ modify: прибавить 1
→ write count
```

Нужно различать атомарность отдельного чтения или записи и атомарность составной
операции. Даже если отдельные accesses атомарны, весь `count++` как
read-modify-write не становится атомарным.

Два потока могут выполнить эти шаги с наложением:

```text
count = 0

Thread 1             Thread 2

read 0               read 0
+1                   +1
write 1              write 1

итог: count == 1
ожидалось: count == 2
```

Одна запись потеряна, потому что оба потока вычислили новое значение из одного
старого состояния. Это называется lost update.

Даже если поле объявлено `volatile`, составная операция не становится атомарной:

```java
private volatile int count;

void increment() {
    count++;
}
```

`volatile` применяется к отдельным чтениям и записям поля и создаёт гарантии
видимости и порядка. Он не объединяет последовательность read-modify-write в одну
атомарную операцию.

```text
volatile int count
count++
≠
thread-safe increment
```

Для защиты `count++` нужна единая критическая секция, например `synchronized`,
либо специализированная атомарная операция, например `AtomicInteger.incrementAndGet()`.

## Ordering и reordering

Порядок строк исходного кода не становится автоматически гарантированным порядком,
который смогут наблюдать другие потоки.

Компилятор `javac`, JIT-компилятор и процессор могут применять допустимые
оптимизации. Важно описывать это не как «JVM случайно переставляет строки», а как
преобразования, которым разрешено менять внутренний способ выполнения при
сохранении требуемого поведения.

As-if-serial semantics означает, что внутри одного потока оптимизация не должна
менять допустимое однопоточное поведение программы. Если поток выполняется без
наблюдения со стороны других потоков, результат должен выглядеть так, будто его
действия соблюдают семантику исходной программы.

Это правило само по себе не создаёт межпоточные гарантии.

```java
private int value;
private boolean ready;

void writer() {
    value = 42;
    ready = true;
}

void reader() {
    if (ready) {
        System.out.println(value);
    }
}
```

Внутри writer-потока запись `value` расположена раньше записи `ready`. Но обычное
чтение `ready` в другом потоке не является синхронизирующим действием. Поэтому
только порядок строк не гарантирует reader-потоку наблюдение `value == 42`.

Межпоточный наблюдаемый порядок определяется правилами JMM, прежде всего
happens-before. Правильное решение должно создавать такое отношение, а не
рассчитывать на конкретный компилятор, JIT или процессор.

## Happens-before

Happens-before, или HB, — центральное отношение порядка в JMM.

Если:

```text
A happens-before B
```

то результаты действия `A` должны быть доступны действию `B` в соответствии с
правилами JMM, а допустимые reorderings не должны нарушать эту гарантию.

Happens-before не означает только «A физически произошло раньше B». Два действия
могут идти одно за другим по времени, но при отсутствии правила JMM между ними не
будет HB. И наоборот, HB описывает обязательный порядок наблюдения, а не требует
представлять конкретные инструкции процессора.

```text
раньше по настенным часам
≠
автоматически happens-before
```

### Program order

В одном потоке каждое действие happens-before последующему действию согласно
program order этого потока.

```java
int value = 40;       // A
value = value + 2;   // B
print(value);        // C
```

```text
A HB B
B HB C
```

Program order задаёт отношения внутри потока. Чтобы перенести гарантию в другой
поток, нужна межпоточная синхронизирующая связь.

### Monitor

Освобождение монитора happens-before каждому последующему успешному захвату того
же монитора.

```java
private int value;

synchronized void write() {
    value = 42;
}

synchronized int read() {
    return value;
}
```

Если оба метода вызваны на одном объекте, они используют один монитор `this`:

```text
Thread 1: value = 42
→ unlock this
→ HB
→ lock this
→ Thread 2: read value
```

Слово «того же» принципиально. Синхронизация на разных объектах не создаёт это
monitor happens-before отношение.

### volatile

Запись в `volatile`-переменную synchronizes-with соответствующим последующим
чтением этой `volatile`-переменной. Эта synchronization edge создаёт отношение
happens-before. В обычном примере с одним переключением флага reader, прочитавший
записанное writer-потоком `ready == true`, получает соответствующую HB-гарантию.

```java
private int value;
private volatile boolean ready;

void write() {
    value = 42;
    ready = true;
}

void read() {
    if (ready) {
        System.out.println(value);
    }
}
```

```text
volatile write ready = true
HB
volatile read ready == true
```

### Thread.start()

Действия потока до вызова `thread.start()` happen-before действиям запущенного
потока.

```java
int value = 42;

Thread thread = new Thread(() ->
        System.out.println(value)
);

thread.start();
```

```text
write value = 42
HB
thread.start()
HB
действия нового потока
```

Поэтому новый поток гарантированно увидит подготовленное до `start()` состояние.

### Thread.join()

Все действия завершившегося потока happen-before успешному возврату из
`thread.join()` в ожидающем потоке.

```java
int[] result = new int[1];

Thread worker = new Thread(() -> result[0] = 42);

worker.start();
worker.join();

System.out.println(result[0]);
```

```text
worker: write result[0] = 42
→ worker завершается
→ HB
→ join успешно возвращается
→ read result[0]
```

### Transitivity

Happens-before транзитивно:

```text
A HB B
B HB C

=>

A HB C
```

Например, writer записывает обычное поле, затем volatile-флаг, а reader читает
флаг и после него поле:

```java
value = 42;       // A
ready = true;     // B, volatile write

if (ready) {      // C, volatile read
    print(value); // D
}
```

```text
A HB B     program order
B HB C     volatile rule
C HB D     program order

=>

A HB D
```

Транзитивность связывает локальный порядок обоих потоков с межпоточной
синхронизацией.

## volatile

`volatile` подходит для состояния, где нужны visibility и ordering, но не нужна
взаимная блокировка составной модификации.

`volatile` обеспечивает:

- visibility guarantees
- ordering guarantees вокруг volatile-доступов

`volatile` не обеспечивает:

- mutual exclusion
- атомарность произвольных составных операций
- атомарность `count++`
- согласованное изменение нескольких независимых полей как одной транзакции

Рассмотрим публикацию данных через флаг:

```java
private volatile boolean ready;
private int value;

void writer() {
    value = 42;
    ready = true;
}

void reader() {
    if (ready) {
        System.out.println(value);
    }
}
```

Если reader прочитал значение `ready == true`, записанное writer-потоком, он
гарантированно увидит предшествующую запись `value == 42`.

```text
value = 42
HB
volatile write ready = true
HB
volatile read ready == true
HB
read value
```

Первая и последняя связи следуют из program order, средняя — из правила
`volatile`. Итоговая гарантия получается через транзитивность.

При этом `volatile` не блокирует другие потоки. Несколько потоков могут
одновременно читать и записывать поле.

## Порядок операций с volatile

Расположение обычной записи относительно volatile-записи принципиально.

### Обычная запись до volatile write

```java
private int value;
private volatile boolean ready;

void writer() {
    value = 42;
    ready = true;
}
```

Запись `value = 42` находится до `volatile write`. Reader, который прочитал
соответствующее значение `ready == true`, получает через HB видимость
предшествующей записи `value`.

```text
write value
→ volatile write ready
→ volatile read ready
→ read value
```

### Обычная запись после volatile write

```java
private int value;
private volatile boolean ready;

void writer() {
    ready = true;
    value = 42;
}
```

Теперь запись `value = 42` следует после volatile-записи в program order.
Volatile-связь между записью и чтением `ready` не переносит назад действие,
которое writer выполнит позже.

```text
volatile write ready = true
→ volatile read ready == true
→ reader может прочитать value

writer: value = 42 находится после публикации
→ нет нужной HB-цепочки к read value
```

Запоминаемое правило:

> volatile write публикует то, что было сделано до него, а не то, что будет
> сделано после него.

## synchronized

`synchronized` работает через монитор объекта или класса.

Он обеспечивает:

- mutual exclusion
- visibility
- ordering

```java
private int count;

public synchronized void increment() {
    count++;
}
```

Instance synchronized-метод захватывает монитор `this`. Только один поток может
одновременно выполнять код, защищённый этим монитором.

```text
Thread 1

lock this
read
modify
write
unlock this

        HB

Thread 2

lock this
read
modify
write
unlock this
```

`count++` остаётся составной операцией, но вся последовательность выполняется в
одной критической секции. Другой поток, использующий тот же монитор, не может
вклиниться между read и write.

Кроме взаимного исключения, `unlock` первого потока happens-before последующему
`lock` второго потока. Поэтому второй поток получает видимость изменений первого.

Для `static synchronized` метода используется монитор объекта `Class`:

```java
public static synchronized void increment() {
    count++;
}
```

Он не совпадает с монитором `this` конкретного экземпляра.

## synchronized writer и обычный reader

Рассмотрим частично синхронизированный класс:

```java
private int count;

public synchronized void increment() {
    count++;
}

public int getCount() {
    return count;
}
```

Writer освобождает монитор `this`, но reader этот монитор не захватывает. Поэтому
между `unlock` в `increment()` и обычным чтением в `getCount()` нет monitor
happens-before связи.

```text
writer: unlock this

reader: обычный read count

нет парного lock того же монитора
→ нет monitor HB-гарантии
```

Корректный вариант синхронизирует и чтение:

```java
private int count;

public synchronized void increment() {
    count++;
}

public synchronized int getCount() {
    return count;
}
```

Два instance synchronized-метода, вызванные на одном объекте, используют монитор
одного и того же `this`.

Альтернативой для простого независимо читаемого значения иногда служит
`volatile`, но выбор должен учитывать все инварианты класса. Если несколько полей
образуют связанное состояние, одного volatile-поля может быть недостаточно.

## volatile и synchronized

| Свойство | `volatile` | `synchronized` |
|---|---|---|
| Visibility | Да | Да |
| Ordering | Да | Да |
| Mutual exclusion | Нет | Да |
| Делает `count++` атомарным | Нет | Да, если операция целиком находится внутри защищённой критической секции |

`volatile` подходит для:

- флага остановки
- publication flag
- ссылки на безопасно публикуемый snapshot
- простого состояния без составной конкурентной модификации

```java
private volatile boolean stopped;

void stop() {
    stopped = true;
}

void work() {
    while (!stopped) {
        doOneIteration();
    }
}
```

`synchronized` нужен, когда требуется защитить:

- read-modify-write
- check-then-act
- несколько связанных изменений состояния
- критическую секцию

```java
public synchronized boolean withdraw(int amount) {
    if (balance < amount) {
        return false;
    }

    balance -= amount;
    return true;
}
```

Выбор определяется не удобством синтаксиса, а требуемым набором гарантий.

## Thread.start()

Действия, выполненные запускающим потоком до `thread.start()`, happen-before
действиям нового потока.

```java
private int value;

void example() {
    value = 42;

    Thread thread = new Thread(() ->
            System.out.println(value)
    );

    thread.start();
}
```

```text
write value = 42
→ thread.start()
→ HB
→ new thread reads value
```

Новый поток гарантированно увидит `42`, хотя `value` не объявлено `volatile`.
Гарантию создаёт `start()`.

Однако `start()` не создаёт обратную гарантию от действий нового потока к
продолжению запускающего потока:

```java
Thread worker = new Thread(() -> value = 42);

worker.start();

System.out.println(value);
```

После `start()` оба потока могут продолжать выполнение конкурентно. Запускающий
поток может прочитать `value` до записи worker-потока, а HB от записи worker к
этому чтению отсутствует.

```text
start
├── worker: write value = 42
└── starter: read value

порядок этих двух действий не задан start-правилом
```

## Thread.join()

`join()` позволяет дождаться завершения другого потока и создаёт гарантию
видимости его действий.

```java
private int value;

void example() throws InterruptedException {
    Thread worker = new Thread(() -> value = 42);

    worker.start();
    worker.join();

    System.out.println(value);
}
```

Последовательность рассуждения:

```text
worker записывает value = 42
→ worker завершается
→ join успешно возвращается
→ main читает value
```

Действия worker-потока happen-before успешному возврату из `join()` ожидающего
потока. Последующее чтение связано с `join()` через program order. Поэтому main
гарантированно видит `42`.

Поле `value` здесь не обязано быть `volatile`: требуемое отношение уже создаёт
`join()`.

Если ожидание было прервано и `join()` не завершился успешно, нельзя использовать
это правило как доказательство видимости результата.

## Data race

Data race возникает, когда:

- несколько потоков обращаются к одной переменной общей памяти
- обращения конфликтуют
- хотя бы одно обращение является записью
- конфликтующие обращения не упорядочены необходимым отношением happens-before

Два обращения конфликтуют, если они относятся к одной переменной и хотя бы одно
из них — запись.

```text
int value;

Thread 1:
value = 42;

Thread 2:
System.out.println(value);
```

Без синхронизации запись и чтение не упорядочены HB. Это data race.

Data race не определяется фразой «когда нам важно значение переменной». Важность
для бизнес-логики не входит в определение. Определение относится к конфликтующим
доступам и отсутствию happens-before.

Правильно синхронизированная программа не содержит data race на рассматриваемом
состоянии. Это даёт значительно более сильную основу для рассуждения, чем
наблюдение «на моей машине работает».

## Race condition

Race condition — более широкое логическое понятие. Корректность результата зависит
от непредсказуемого interleaving или порядка выполнения конкурентных операций.

```java
if (balance >= amount) {
    balance -= amount;
}
```

Два потока могут оба проверить одно исходное значение `balance`, оба пройти
условие, а затем оба выполнить списание. Операция check-then-act должна быть
защищена как единое целое.

```text
Thread 1: check true
Thread 2: check true
Thread 1: subtract
Thread 2: subtract
```

Data race и race condition часто связаны, но не являются синонимами.

```text
Data race
→ конкретная проблема конфликтующего доступа к памяти без HB

Race condition
→ логическая корректность зависит от порядка выполнения
```

Можно иметь race condition даже при использовании отдельных thread-safe операций,
если их композиция не атомарна. Например, два вызова потокобезопасного API могут
образовывать небезопасную последовательность check-then-act.

## Safe publication

Публикация объекта означает передачу ссылки так, чтобы другой поток смог получить
к ней доступ. Важно опубликовать не только значение ссылки, но и корректно
сконструированное состояние объекта.

Небезопасная публикация:

```java
class Config {
    int timeout;
    String url;
}

private Config config;
```

Writer:

```java
Config c = new Config();
c.timeout = 5000;
c.url = "localhost";

config = c;
```

Reader:

```java
if (config != null) {
    System.out.println(config.timeout);
    System.out.println(config.url);
}
```

Между обычной записью ссылки и обычным чтением ссылки нет необходимой
happens-before связи. JMM поэтому не предоставляет reader-потоку требуемую
гарантию видимости всех записей, которыми writer подготовил объект.

Безопасная публикация через volatile-ссылку:

```java
private volatile Config config;
```

Writer:

```java
Config c = new Config();
c.timeout = 5000;
c.url = "localhost";

config = c;
```

Reader:

```java
Config local = config;

if (local != null) {
    System.out.println(local.timeout);
    System.out.println(local.url);
}
```

HB-цепочка:

```text
write c.timeout = 5000
write c.url = "localhost"
HB
volatile write config = c
HB
volatile read config into local
HB
read local.timeout and local.url
```

Локальная переменная также фиксирует одну прочитанную ссылку. Если `config` позже
будет заменён другим потоком, обе операции чтения всё равно относятся к одному
объекту `local`.

Другие стандартные способы safe publication включают публикацию под тем же
монитором и передачу состояния через механизмы, контракты которых создают
необходимые happens-before отношения.

## Volatile reference не делает поля volatile

Объявление:

```java
private volatile User user;
```

означает, что volatile-семантика применяется к чтению и записи самой ссылки
`user`. Оно не означает:

```text
user.name → volatile
user.age  → volatile
```

Volatile publication обеспечивает видимость состояния объекта, записанного до
публикации ссылки:

```java
User created = new User();
created.name = "Dima";
created.age = 22;

user = created; // volatile write
```

Поток, прочитавший соответствующую ссылку из `user`, получает видимость этих
предшествующих записей.

Но последующая конкурентная мутация:

```java
user.age = 23;
```

не становится volatile-записью поля `age`. Для неё требуется отдельное решение:
синхронизация, volatile/atomic-семантика самого изменяемого состояния либо отказ
от мутации через immutable snapshot.

Это типичная собеседовательная ловушка:

```text
volatile reference
→ специальные гарантии для доступа к ссылке и предшествующей публикации

volatile reference
≠
транзитивно volatile-граф объектов
```

## final и JMM

JMM предоставляет специальные гарантии для `final`-полей после корректного
завершения конструктора.

```java
final class Config {

    private final String host;
    private final int timeout;

    Config(String host, int timeout) {
        this.host = host;
        this.timeout = timeout;
    }
}
```

Если объект корректно сконструирован и ссылка `this` не утекла из конструктора,
другой поток, получивший ссылку на объект, получает специальные final-field
guarantees для значений, присвоенных этим полям в конструкторе.

Корректное конструирование означает, в частности, что объект не становится
доступен другим потокам до завершения конструктора.

Опасная утечка `this`:

```java
class Listener {

    private final int threshold;

    Listener(Registry registry) {
        registry.register(this);
        threshold = 10;
    }
}
```

`registry.register(this)` может сделать объект доступным другому потоку до
присваивания `threshold`. В таком случае рассуждать о безопасно завершённом
конструировании нельзя.

Immutable objects проще использовать в многопоточном коде, потому что после
создания их состояние не изменяется. Без последующих конкурентных записей
исчезает целый класс гонок. Однако сам способ передачи ссылки всё равно нужно
оценивать по контракту публикации, а final-field guarantees нельзя превращать в
утверждение, что любая небезопасная публикация произвольного состояния безопасна.

Final-field guarantees относятся к корректно установленным `final`-полям. Они не
превращают произвольную небезопасную публикацию объекта в полноценный safe
publication mechanism для всего его mutable state.

`final` у ссылки запрещает переназначение ссылки, но не делает объект по ссылке
неизменяемым:

```java
final List<String> values = new ArrayList<>();

values.add("Java");       // допустимо
values.add("Concurrency"); // допустимо
```

Нельзя выполнить:

```java
values = new ArrayList<>();
```

Но `final` не:

- делает `ArrayList` immutable
- делает `ArrayList` thread-safe
- запрещает изменение элементов или внутреннего состояния списка

```text
final reference
→ ссылку нельзя переназначить

immutable object
→ состояние объекта нельзя изменить
```

## Типичные ошибки

### Считать volatile count++ потокобезопасным

`count++` состоит из read, modify и write. `volatile` не объединяет их в одну
атомарную операцию, поэтому возможен lost update.

### Синхронизировать writer, но оставить reader обычным

Monitor-правило связывает `unlock` с последующим `lock` того же монитора. Обычный
reader не выполняет такой `lock` и не получает эту гарантию.

### Считать поля объекта volatile из-за volatile-ссылки

`volatile User user` применяет volatile-семантику к ссылке. Последующие изменения
`user.name` или `user.age` требуют собственного решения.

### Считать порядок строк межпоточной гарантией

Program order важен внутри потока, но сам по себе не передаёт результат другому
потоку. Нужна синхронизирующая связь и HB-цепочка.

### Использовать Thread.sleep() как синхронизацию

```java
worker.start();
Thread.sleep(1000);
System.out.println(value);
```

`sleep()` не создаёт happens-before между действиями worker и последующим чтением.
Задержка не доказывает ни завершение worker, ни видимость записи. Для ожидания
завершения нужен, например, `join()`.

### Говорить, что у каждого потока своя копия Heap

Это не модель JMM. Heap является общей Runtime Data Area, а JMM описывает гарантии
наблюдения действий с общей памятью.

### Считать data race и race condition синонимами

Data race — конфликтующие доступы без HB. Race condition — зависимость логической
корректности от порядка конкурентных событий. Второе понятие шире.

### Считать, что JMM описывает Heap, Stack и Metaspace

Эти сущности относятся к JVM Runtime Data Areas и реализации JVM. JMM отвечает за
visibility, atomicity, ordering и правила межпоточного наблюдения.

### Считать, что volatile всегда заменяет synchronized

`volatile` не предоставляет mutual exclusion и не защищает составные операции или
инварианты нескольких полей.

### Считать synchronized механизмом только атомарности

`synchronized` одновременно предоставляет mutual exclusion, visibility и
ordering. Освобождение и последующее захватывание того же монитора создают HB.

## Как кратко объяснить JMM на собеседовании

Java Memory Model определяет гарантии взаимодействия потоков с общей памятью.
Основные вопросы JMM — visibility изменений, atomicity операций и ordering
действий. Центральный инструмент рассуждения — happens-before: если действие `A`
happens-before `B`, результаты `A` должны быть доступны `B`, а допустимые
переупорядочивания не могут нарушать эту гарантию. `volatile` даёт visibility и
ordering для доступа к полю, но не mutual exclusion и не атомарность `count++`.
`synchronized` через один монитор даёт mutual exclusion, visibility и ordering.
Правила `Thread.start()` и `Thread.join()` также создают happens-before связи.
JMM не следует смешивать с JVM Runtime Data Areas: Heap, Stack и Method Area
описывают логические области памяти, а не правила межпоточного наблюдения.

## Вопросы для самопроверки

1. На какой вопрос отвечает Java Memory Model?
2. Чем JMM отличается от JVM Runtime Data Areas?
3. Почему неверно говорить, что у каждого потока есть собственная копия Heap?
4. Что означают visibility, atomicity и ordering?
5. Почему обычный `boolean ready` не является надёжным механизмом передачи сигнала между потоками?
6. Из каких логических шагов состоит `count++`?
7. Как возникает lost update при двух конкурентных инкрементах?
8. Почему `volatile int count` не делает `count++` потокобезопасным?
9. Что означает as-if-serial semantics?
10. Почему as-if-serial semantics не создаёт межпоточные гарантии?
11. Почему reordering нельзя описывать как случайную перестановку строк JVM?
12. Что означает отношение happens-before?
13. Почему happens-before не равно физическому порядку по времени?
14. Какое happens-before правило задаёт program order?
15. Какое отношение возникает между `unlock` и последующим `lock` того же монитора?
16. Что изменится, если writer и reader синхронизируются на разных объектах?
17. Какое happens-before правило связано с записью и чтением `volatile`-поля?
18. Как транзитивность связывает обычную запись, volatile-флаг и последующее обычное чтение?
19. Почему в коде `value = 42; ready = true;` volatile-поле `ready` может публиковать `value`?
20. Почему порядок `ready = true; value = 42;` не даёт той же гарантии?
21. Какие гарантии предоставляет `synchronized` помимо mutual exclusion?
22. Почему synchronized writer и обычный reader не образуют monitor happens-before связь?
23. Какой монитор используют два instance synchronized-метода одного объекта?
24. Почему новый поток видит данные, записанные до `thread.start()`, без `volatile`?
25. Почему следующий код не гарантирует чтение `42` запускающим потоком?

```java
Thread worker = new Thread(() -> value = 42);
worker.start();
System.out.println(value);
```

26. Почему после успешного `worker.join()` поле `value` не обязано быть `volatile`?
27. По каким четырём признакам определяется data race?
28. Чем race condition отличается от data race на примере check-then-act?
29. Почему следующая публикация объекта небезопасна и как исправить её через `volatile`?

```java
Config created = new Config();
created.timeout = 5000;
config = created;
```

30. Какие гарантии даёт корректное конструирование final-полей, чем опасна утечка `this` и почему `final ArrayList` не является immutable или thread-safe?
