# `panic!` / `todo!` / `unimplemented!` / `unreachable!`

## 本集目標

認識四種會讓程式立即終止的巨集，以及它們各自的使用時機。

> 本集是通用補充，不特定屬於哪一章。

## 概念說明

你可能注意到 `println!()`、`format!()` 這些名字後面都有 `!`。在 Rust 裡，名字帶 `!` 的東西叫做**巨集（macro）**——它和函數不太一樣，但目前你只需要知道怎麼用就好，巨集的原理以後會教。

這集要介紹四個常用的「讓程式直接掛掉」的巨集。它們都會造成 panic（程式中止），但語義不同，傳達給讀程式碼的人的訊息也不同。

### `panic!("訊息")`

最基本的「程式出事了，直接中止」。當你遇到無法處理的錯誤時使用：

```rust,should_panic
# fn main() {
    panic!("發生了不該發生的事！");
# }
```

你可以帶格式化訊息：`panic!("找不到 id: {}", id);`

### `todo!()`

「我還沒寫完，先放個佔位符」。開發中最常用，讓你先把程式架構搭好，細節之後再填：

```rust,noplayground
fn calculate_tax(income: f64) -> f64 {
    todo!() // 之後再實作
}
#
# fn main() {}
```

編譯可以通過，但執行到這裡就會 panic，訊息是「not yet implemented」。

### `unimplemented!()`

「這個功能沒有實作」。跟 `todo!()` 很像，但語義不同——`todo!()` 明確表示「之後會做」，`unimplemented!()` 則**不保證之後會做**。可能是不打算做，可能是目前沒需求，也可能是 `trait` 要求的方法但對這個型別沒意義：

```rust,editable
# trait Foo {
#     fn bar(&self) -> u8;
#     fn baz(&self);
# }
#
# struct MyStruct;
#
impl Foo for MyStruct {
    fn bar(&self) -> u8 {
        1 + 1
    }

    fn baz(&self) {
        // 對 MyStruct 來說 baz 沒意義，但 trait 要求必須定義
        unimplemented!()
    }
}
#
# fn main() {}
```

### `unreachable!()`

「這行程式碼不應該被執行到」。如果你確定某段邏輯不可能走到，用這個來標記：

```rust,editable
# fn main() {
    let direction = "north";
    match direction {
        "north" | "south" | "east" | "west" => println!("有效方向"),
        _ => unreachable!("方向只有四種，不可能走到這裡"),
    }
# }
```

如果真的走到了，表示你的假設有誤，panic 會幫你發現這個 bug。

### 四者比較

- `panic!` — 出事了。用於無法處理的錯誤
- `todo!` — 還沒寫，之後會實作。開發中的佔位符
- `unimplemented!` — 沒有實作，不保證之後會做。可能是沒需求、可能是 `trait` 要求但沒意義
- `unreachable!` — 不該走到這裡。標記邏輯上不可能的分支

## 範例程式碼

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(f64, f64),
    Triangle(f64, f64, f64),
}

fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle(r) => 3.14159 * r * r,
        Shape::Rectangle(w, h) => w * h,
        Shape::Triangle(_, _, _) => todo!("三角形面積之後再實作"),
    }
}

fn describe_score(score: u32) -> &'static str {
    match score {
        90..=100 => "優秀",
        80..=89 => "良好",
        70..=79 => "普通",
        60..=69 => "及格",
        0..=59 => "不及格",
        _ => unreachable!("分數應該在 0-100 之間"),
    }
}

trait Storage {
    fn save(&mut self, data: &str);
    fn load(&self) -> String;
}

struct LocalStorage;

impl Storage for LocalStorage {
    fn save(&mut self, data: &str) {
        println!("儲存到本地：{}", data);
    }

    fn load(&self) -> String {
        // trait 要求定義，但 LocalStorage 不需要這個功能
        unimplemented!()
    }
}

fn main() {
    // todo! — 開發中的佔位符
    let circle = Shape::Circle(5.0);
    println!("圓形面積：{}", area(&circle));

    let rect = Shape::Rectangle(3.0, 4.0);
    println!("矩形面積：{}", area(&rect));

    // 如果取消下一行的註解，會 panic 並顯示 todo! 訊息
    // let tri = Shape::Triangle(3.0, 4.0, 5.0);
    // println!("三角形面積：{}", area(&tri));

    // unreachable! — 不該走到的分支
    let grade = describe_score(85);
    println!("85 分的評等：{}", grade);

    // unimplemented! — 沒有實作的功能
    let mut storage = LocalStorage;
    storage.save("hello");
    // storage.load(); // 取消註解會 panic：not implemented

    // panic! — 直接中止
    // panic!("故意 panic！");
    println!("程式正常結束");
}
```

## 重點整理

- `panic!("msg")` 是最基本的中止方式，用於無法處理的錯誤
- `todo!()` 是開發佔位符，明確表示「之後會實作」
- `unimplemented!()` 表示「沒有實作」，不保證之後會做——可能是沒需求、可能是 `trait` 要求但對該型別沒意義
- `unreachable!()` 標記邏輯上不可能到達的程式碼路徑
- 它們都會造成 panic，差別在於傳達的**意圖**不同——選對的那個，讓程式碼更有表達力
