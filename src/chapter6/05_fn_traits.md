# Fn / FnMut / FnOnce

## 本集目標
理解 Fn、FnMut、FnOnce 是 trait 而非型別，掌握它們的繼承關係，並學會在 API 設計中選擇正確的 bound。

## 概念說明

### 它們是 trait，不是型別

前幾集我們一直說 FnOnce、FnMut、Fn，但還沒正式說明——它們其實是 **trait**。就像第五章學的 `Clone`、`Display` 一樣，Fn / FnMut / FnOnce 是定義在標準庫裡的 trait。每個閉包的匿名 struct 會自動 impl 對應的 trait（上一集講的推斷規則決定 impl 哪些）。

那這些 trait 到底長什麼樣？

- `FnOnce(Args) -> Ret`：可以被呼叫至少一次（可能會消耗自己）
- `FnMut(Args) -> Ret`：可以被多次呼叫（可能會修改內部狀態）
- `Fn(Args) -> Ret`：可以被多次呼叫（不會修改任何東西）

注意！`fn(i32) -> i32`（小寫）是函數指標**型別**，而 `Fn(i32) -> i32`（大寫）是 **trait**。兩個完全不同的東西。

### 繼承關係

這三個 trait 有繼承（supertrait）關係：

```ignore
Fn : FnMut : FnOnce
```

意思是：
- 所有實作 `Fn` 的東西，自動也實作 `FnMut` 和 `FnOnce`
- 所有實作 `FnMut` 的東西，自動也實作 `FnOnce`
- 但 `FnOnce` 不一定有 `FnMut`，`FnMut` 不一定有 `Fn`

為什麼是這個方向？

- **Fn → FnMut**：如果一個閉包只需要 `&self` 就能執行，那給它 `&mut self` 當然也行（只是多給了它不需要的修改權限）
- **FnMut → FnOnce**：如果一個閉包用 `&mut self` 就能執行，那給它 `self`（整個擁有權）當然也行——擁有一個東西就包含了可以修改它。只是呼叫完之後 struct 被消耗了，不能再呼叫第二次

反過來就不行——一個需要消耗自己（FnOnce）的閉包，不能保證多次呼叫（FnMut）。

### 用 impl Trait 接受閉包

還記得第五章的 `impl Trait` 嗎？用它來接受閉包參數：

```rust,no_run
fn call_once(f: impl FnOnce() -> String) -> String {
    f()
}

fn call_many_times(mut f: impl FnMut()) {
    f();
    f();
    f();
}

fn call_readonly(f: impl Fn() -> i32) -> i32 {
    f() + f()
}
#
# fn main() {}
```

注意 `FnMut` 的參數要加 `mut`——因為呼叫 FnMut 閉包需要 `&mut self`，所以 `f` 本身要是 `mut` 的。

### API 設計原則：選能接受最多種閉包的 bound

當你設計一個接受閉包的函數時，應該選**能接受最多種閉包**的 trait bound：

1. 先試 `FnOnce` —— 如果你只需要呼叫一次
2. 不夠再用 `FnMut` —— 如果你需要多次呼叫
3. 最後才用 `Fn` —— 如果你需要多次呼叫且不允許修改

為什麼？因為 `FnOnce` 能接受所有閉包（所有閉包都至少是 FnOnce），而 `Fn` 只能接受不修改狀態的閉包。選能接受最多種的 bound，使用者傳入的自由度最高。

實務上 `Fn` 很少用到——大部分需要多次呼叫閉包的 API 用 `FnMut` 就夠了（FnMut 也能接受 Fn 的閉包）。只有少數場景需要**保證閉包不修改狀態**時才會用 `Fn`。

### 函數指標也實作了這三個 trait

普通的函數（和函數指標 `fn`）自動實作了 `Fn`、`FnMut`、`FnOnce`。所以你可以把函數名稱傳給任何接受這三個 trait 的地方。

## 範例程式碼

```rust
// 只需要呼叫一次 → 用 FnOnce（能接受最多種閉包）
fn consume_and_print(f: impl FnOnce() -> String) {
    let result = f();
    println!("結果：{}", result);
}

// 需要多次呼叫 → 用 FnMut
fn repeat_three_times(mut f: impl FnMut()) {
    f();
    f();
    f();
}

// 需要多次呼叫且不修改 → 用 Fn
fn sum_two_calls(f: impl Fn(i32) -> i32, x: i32) -> i32 {
    f(x) + f(x)
}

fn main() {
    // FnOnce：閉包消耗了捕捉的值
    let name = String::from("Rust");
    consume_and_print(|| {
        let s = name;  // move name
        format!("Hello, {}!", s)
    });

    // FnMut：閉包修改了捕捉的變數
    let mut count = 0;
    repeat_three_times(|| {
        count += 1;
        println!("第 {} 次呼叫", count);
    });
    println!("總共呼叫了 {} 次", count);

    // Fn：閉包只讀取
    let multiplier = 3;
    let result = sum_two_calls(|x| x * multiplier, 5);
    println!("sum_two_calls 結果：{}", result);

    // 普通函數也能傳進去
    fn double(x: i32) -> i32 {
        x * 2
    }
    let result2 = sum_two_calls(double, 10);
    println!("用普通函數：{}", result2);

    // Fn 的閉包也可以傳給 FnOnce 的參數（因為 Fn: FnMut: FnOnce）
    let greeting = String::from("哈囉");
    consume_and_print(|| {
        format!("{}, 世界！", greeting)  // 只是讀取 greeting，是 Fn
    });
    // greeting 還活著，因為閉包只是借用了它
    println!("greeting 還在：{}", greeting);
}
```

## 重點整理
- `Fn`、`FnMut`、`FnOnce` 是 **trait**，不是型別；`fn` 才是函數指標型別
- 繼承關係：`Fn` ⊂ `FnMut` ⊂ `FnOnce`（FnOnce 能接受所有閉包，Fn 只接受不修改的）
- 用 `impl FnOnce()` / `impl FnMut()` / `impl Fn()` 來接受閉包參數
- `FnMut` 的參數要加 `mut`
- API 設計原則：**先選 FnOnce**，需要多次呼叫再改 FnMut，需要保證不修改才用 Fn
- 函數指標自動實作了 Fn + FnMut + FnOnce
