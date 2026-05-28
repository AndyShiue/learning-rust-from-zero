# fully qualified syntax

## 本集目標

學會三種不同層級的方法呼叫語法，以及在 `trait` 方法名稱衝突時如何消歧義。

> 本集是**第 5 章**的補充。

## 概念說明

在 Rust 裡，呼叫一個方法其實有三種寫法，從簡單到完整：

### 第一種：方法語法

```rust,noplayground
# trait Animal {
#     fn speak(&self);
# }
#
# struct Dog;
#
# impl Animal for Dog {
#     fn speak(&self) {
#         println!("汪！");
#     }
# }
#
# fn main() {
#     let dog = Dog;
    dog.speak();
# }
```

最常用的寫法。編譯器會自動找到對應的方法。

### 第二種：指定 `trait` 或型別

```rust,noplayground
# trait Animal {
#     fn speak(&self);
# }
#
# struct Dog;
#
# impl Animal for Dog {
#     fn speak(&self) {
#         println!("汪！");
#     }
# }
#
# fn main() {
#     let dog = Dog;
    Animal::speak(&dog);
# }
```

明確告訴編譯器「我要呼叫 `Animal` `trait` 上的 `speak`」。`&dog` 就是原本的 `&self`。

### 第三種：完全限定語法（fully qualified syntax）

```rust,noplayground
# trait Animal {
#     fn speak(&self);
# }
#
# struct Dog;
#
# impl Animal for Dog {
#     fn speak(&self) {
#         println!("汪！");
#     }
# }
#
# fn main() {
#     let dog = Dog;
    <Dog as Animal>::speak(&dog);
# }
```

最明確的寫法：「在 `Dog` 實作的 `Animal` `trait` 上，呼叫 `speak` 方法，傳入 `&dog`」。

### 什麼時候需要用到？

大部分時候第一種就夠了。但當**多個 `trait` 定義了同名方法**的時候，編譯器不知道你要呼叫哪一個，就需要更明確的語法：

```rust,noplayground
trait Animal {
    fn name(&self) -> &str;
}

trait Robot {
    fn name(&self) -> &str;
}
#
# fn main() {}
```

如果某個型別同時實作了 `Animal` 和 `Robot`，呼叫 `.name()` 時編譯器會報錯。這時候就需要第二種或第三種的語法來消歧義。

### associated function 更常需要

如果是沒有 `self` 參數的 **associated function**，因為沒有接收者可以讓編譯器推斷，更容易需要完全限定語法：

```rust,noplayground
# trait TraitA {
#     fn create() -> i32;
# }
#
# trait TraitB {
#     fn create() -> i32;
# }
#
# struct MyType;
#
# impl TraitA for MyType {
#     fn create() -> i32 {
#         0
#     }
# }
#
# impl TraitB for MyType {
#     fn create() -> i32 {
#         1
#     }
# }
#
# fn main() {
    // 如果多個 trait 都有 create() 這個 associated function
    let x = <MyType as TraitA>::create();
# }
```

### 存取 associated type

完全限定語法也可以用來存取某個型別在特定 `trait` 上的 **associated type**：

```rust,noplayground
// Iterator trait 有一個 associated type 叫 Item
// 用完全限定語法取得它的具體型別：
type MyItem = <Vec<i32> as Iterator>::Item; // i32
#
# fn main() {}
```

有些地方可以直接寫 `Type::TypeName`，但如果有歧義或是編譯器無法推斷，就需要用完全限定語法明確指定。

## 範例程式碼

```rust,editable
trait Animal {
    fn speak(&self);
    fn category() -> &'static str;
}

trait Robot {
    fn speak(&self);
    fn category() -> &'static str;
}

struct CyberDog {
    name: String,
}

impl Animal for CyberDog {
    fn speak(&self) {
        println!("{} 汪汪叫！（動物）", self.name);
    }

    fn category() -> &'static str {
        "哺乳類"
    }
}

impl Robot for CyberDog {
    fn speak(&self) {
        println!("{} 嗶嗶叫！（機器人）", self.name);
    }

    fn category() -> &'static str {
        "人工智慧"
    }
}

// CyberDog 自己也有 speak
impl CyberDog {
    fn speak(&self) {
        println!("{} 汪嗶汪嗶！（本體）", self.name);
    }
}

fn main() {
    let dog = CyberDog {
        name: String::from("小白"),
    };

    // 第一層：方法語法 — 優先呼叫型別本身的方法
    dog.speak(); // "小白 汪嗶汪嗶！（本體）"

    // 第二層：指定 trait
    Animal::speak(&dog); // "小白 汪汪叫！（動物）"
    Robot::speak(&dog);  // "小白 嗶嗶叫！（機器人）"

    // 第三層：完全限定語法
    <CyberDog as Animal>::speak(&dog); // "小白 汪汪叫！（動物）"
    <CyberDog as Robot>::speak(&dog);  // "小白 嗶嗶叫！（機器人）"

    // associated function（沒有 self）— 更需要完全限定語法
    // Animal::category(); // 編譯錯誤！編譯器不知道是哪個型別的實作
    let animal_cat = <CyberDog as Animal>::category();
    let robot_cat = <CyberDog as Robot>::category();
    println!("動物分類：{}", animal_cat);
    println!("機器人分類：{}", robot_cat);

    // 存取 associated type
    // Vec<i32> 實作了 IntoIterator，它的 Item 是 i32
    // 用完全限定語法取得 associated type：
    let _: <Vec<i32> as IntoIterator>::Item = 42; // 型別是 i32
    println!("Vec<i32> 的 IntoIterator::Item 是 i32");
}
```

## 重點整理

- 方法呼叫有三種層級：`object.method()` → `Trait::method(&object)` → `<Type as Trait>::method(&object)`
- 通常用最簡單的就好，有衝突時才升級
- 當多個 `trait` 定義同名方法時，需要指定要呼叫哪個 `trait` 的版本
- 型別本身的方法優先於 `trait` 方法
- associated function（沒有 `self`）更常需要完全限定語法
- 完全限定語法的格式：`<Type as Trait>::function(args)`
- 也可以用來存取 associated type：`<Type as Trait>::TypeName`
