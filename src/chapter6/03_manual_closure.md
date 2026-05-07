# 手動實作閉包

## 本集目標

透過手動把閉包拆解成 struct + 方法，理解編譯器在背後做了什麼事。你會看到三種閉包各自對應什麼樣的 struct，以及為什麼呼叫閉包其實是在呼叫方法。

## 概念說明

### 閉包 = 匿名 struct + 方法

上一集我們看到閉包可以捕捉外部變數。但它是怎麼「記住」這些變數的？

答案很直接——編譯器幫你做了兩件事：

1. **建立一個匿名 struct**，把捕捉的變數存成欄位
2. **在那個 struct 上 impl 一個方法**，方法的內容就是你寫在 `||` 後面的閉包體

換句話說，你寫的閉包體（`{ ... }` 裡面的程式碼）就是那個方法的實作。

今天我們就來手動做一次編譯器做的事，把三種閉包分別模擬出來。

### 閉包呼叫 = 方法呼叫

當你寫 `f()` 呼叫一個閉包，編譯器其實把它轉換成 struct 上的方法呼叫：

- **FnOnce**：`f()` → `f.call_once()` — 傳 `self`，消耗整個 struct
- **FnMut**：`f()` → `f.call_mut()` — 傳 `&mut self`，可變借用 struct
- **Fn**：`f()` → `f.call()` — 傳 `&self`，唯讀借用 struct

看出來了嗎？這就是第四章學的三種方法接收者：`self`、`&mut self`、`&self`。閉包的三種分類，本質上就是方法接收 `self` 的三種方式。

上一集介紹了 FnOnce（消耗捕捉的值，只能呼叫一次）和 FnMut（修改捕捉的值，可多次呼叫）。**Fn 在上一集沒有出現**——它是第三種：只讀取捕捉的值，不消耗也不修改，可以呼叫任意多次。

接下來我們分別用 struct 手動模擬這三種閉包。注意：**三種閉包的 struct 欄位型別不同**，不是同一個 struct 換三種方法。

### FnOnce：struct 存擁有的值，方法接 `self`

假設我們有這樣的閉包：

```rust
# fn main () {
    let name = String::from("Alice");
    let greet = || {
        let s = name; // 閉包體內把 name 移走了
        println!("Hello, {}!", s);
    };
    greet();
    // greet(); // 編譯錯誤！name 已經被移走，不能再呼叫
# }
```

編譯器會產生類似這樣的東西：

```rust,no_run
struct GreetOnce {
    name: String, // 擁有 name
}

// 建立閉包 = 把捕捉的變數塞進 struct
// let greet = GreetOnce { name };

impl GreetOnce {
    // 呼叫閉包 = 呼叫 struct 上的方法
    fn call_once(self) {
        let s = self.name; // 把 name 從 struct 裡移出來
        println!("Hello, {}!", s);
    }
}
#
# fn main() {}
```

因為方法接收 `self`（by value），呼叫的時候整個 struct 被消耗掉了，所以只能呼叫一次。這就是 FnOnce。

### FnMut：struct 存可變借用，方法接 `&mut self`

假設閉包修改了捕捉的變數：

```rust
# fn main() {
    let mut name = String::from("Alice");
    let mut greet = || {
        name.push_str("!");
        println!("Hello, {}", name);
    };
    greet();
    greet(); // 可以多次呼叫
# }
```

編譯器產生的東西：

```rust,no_run
struct GreetMut<'a> {
    name: &'a mut String, // 可變借用 name
}

// let mut greet = GreetMut { name: &mut name };

impl<'a> GreetMut<'a> {
    fn call_mut(&mut self) {
        self.name.push_str("!");
        println!("Hello, {}", self.name);
    }
}
#
# fn main() {}
```

**為什麼 struct 存 `&mut`，方法又接 `&mut self`？** 因為一個閉包可能捕捉多個變數。假設閉包同時修改了 `a`、`b`、`c` 三個變數，struct 裡就會有三個欄位：

```rust,no_run
struct SomeClosure<'a> {
    a: &'a mut i32,
    b: &'a mut String,
    c: &'a mut Vec<i32>,
}
#
# fn main() {}
```

方法用 `&mut self` 而不是 `self`，因為用 `self` 的話呼叫一次就消耗掉了——那就變成 FnOnce 了。FnMut 需要多次呼叫，所以只能借用整個 struct。

### Fn：struct 存唯讀借用，方法接 `&self`

如果閉包只是讀取捕捉的變數，完全不修改：

```rust
# fn main() {
    let name = String::from("Alice");
    let greet = || {
        println!("Hello, {}!", name);
    };
    greet();
    greet(); // 可以多次呼叫，完全沒問題
# }
```

編譯器產生的東西：

```rust,no_run
struct GreetRef<'a> {
    name: &'a String, // 唯讀借用 name
}

// let greet = GreetRef { name: &name };

impl<'a> GreetRef<'a> {
    fn call_ref(&self) {
        println!("Hello, {}!", self.name);
    }
}
#
# fn main() {}
```

因為方法接收 `&self`，struct 不會被消耗也不會被修改，所以可以呼叫任意多次。這就是 Fn。

### 對照表

| self 類型 | 對應 trait | struct 欄位存什麼 | 能做什麼 |
|----------|----------|-----------------|---------|
| `self` | FnOnce | 擁有的值（如 `String`） | 消耗捕捉的值，只能呼叫一次 |
| `&mut self` | FnMut | 可變借用（如 `&mut String`） | 修改捕捉的值，可以多次呼叫 |
| `&self` | Fn | 唯讀借用（如 `&String`） | 只讀取，可以多次呼叫 |

### 小結：閉包到底是什麼？

把上面的東西串起來：

1. 編譯器幫你建一個匿名 struct，把捕捉的變數存進去
2. 你寫的閉包體就是那個 struct 上方法的實作
3. 當你寫 `f()` 的時候，編譯器根據閉包的種類，呼叫 struct 上的 `.call_once()` / `.call_mut()` / `.call()`

每次你寫一個閉包，編譯器就在幕後做了「建 struct → impl 方法 → 呼叫方法」這些事。

## 範例程式碼

以下的完整程式碼把三種閉包都手動模擬出來。每一個 struct 對應一種閉包，欄位型別和方法接收者都不同：

```rust
// === FnOnce 模擬 ===
// struct 擁有值，方法接 self
struct GreetOnce {
    name: String,
}

impl GreetOnce {
    fn call_once(self) {
        // 閉包體：把 name 移走
        let s = self.name;
        println!("[FnOnce] Hello, {}!", s);
        // self 被消耗了，不能再用
    }
}

// === FnMut 模擬 ===
// struct 存可變借用，方法接 &mut self
struct GreetMut<'a> {
    name: &'a mut String,
}

impl<'a> GreetMut<'a> {
    fn call_mut(&mut self) {
        // 閉包體：修改捕捉的變數
        self.name.push_str("!");
        println!("[FnMut] Hello, {}", self.name);
    }
}

// === Fn 模擬 ===
// struct 存唯讀借用，方法接 &self
struct GreetRef<'a> {
    name: &'a String,
}

impl<'a> GreetRef<'a> {
    fn call_ref(&self) {
        // 閉包體：只讀取，不修改
        println!("[Fn] Hello, {}!", self.name);
    }
}

fn main() {
    // --- FnOnce：呼叫一次就消耗 ---
    let name1 = String::from("Alice");
    let greet_once = GreetOnce { name: name1 };
    greet_once.call_once();
    // greet_once.call_once(); // 編譯錯誤！struct 已經被消耗了

    // --- FnMut：可以多次呼叫，每次修改 ---
    let mut name2 = String::from("Bob");
    {
        let mut greet_mut = GreetMut { name: &mut name2 };
        greet_mut.call_mut(); // Bob!
        greet_mut.call_mut(); // Bob!!
        greet_mut.call_mut(); // Bob!!!
    } // greet_mut 離開作用域，借用結束
    println!("name2 現在是：{}", name2);

    // --- Fn：只讀取，呼叫幾次都行 ---
    let name3 = String::from("Charlie");
    let greet_ref = GreetRef { name: &name3 };
    greet_ref.call_ref();
    greet_ref.call_ref();
    greet_ref.call_ref();
}
```

## 重點整理

- 閉包背後就是一個匿名 struct，捕捉的變數變成 struct 的欄位
- **三種閉包的差別在方法怎麼接收 self**：`self`（FnOnce）、`&mut self`（FnMut）、`&self`（Fn）
- 閉包體就是 struct 上方法的實作內容
- `f()` 會被編譯器轉換成方法呼叫：`self.call_once()` / `self.call_mut()` / `self.call()`
- Fn：只讀取，不修改不消耗，可以無限次呼叫
- 下一集會講編譯器是怎麼**自動判斷**一個閉包該歸類為 FnOnce、FnMut 還是 Fn
