# `thread::spawn`

## 本集目標

學會建立執行緒，讓程式同時做好幾件事。

## 概念說明

到目前為止，我們的程式都是從頭到尾一行一行執行的。但有些時候你希望程式能**同時**做好幾件事——比如一邊下載檔案一邊更新進度條。這就是**執行緒**的用途。

### 建立執行緒

`std::thread::spawn` 接收一個閉包，在新的執行緒上執行它：

```rust
use std::thread;

fn main() {
    thread::spawn(|| {
        println!("我在另一個執行緒！");
    });
}
```

### 不 `join` 就會死

有個很重要的事：`main` 函數結束時，整個程式就結束了——不管其他執行緒有沒有跑完。

```rust
use std::thread;

fn main() {
    thread::spawn(|| {
        for i in 0..10 {
            println!("子執行緒：{}", i);
        }
    });

    println!("main 結束了");
    // 子執行緒可能只印了一部分，甚至什麼都沒印
}
```

### `JoinHandle`

`thread::spawn` 會回傳一個 `JoinHandle`。呼叫 `.join()` 可以等待那個執行緒跑完：

```rust
use std::thread;

fn main() {
    let handle = thread::spawn(|| {
        for i in 0..5 {
            println!("子執行緒：{}", i);
        }
    });

    handle.join().expect("執行緒發生錯誤"); // 等子執行緒跑完
    println!("全部完成");
}
```

`.join()` 不只是等待——它還能拿到閉包的回傳值。閉包回傳什麼，`.join().expect("執行緒發生錯誤")` 就得到什麼：

```rust
use std::thread;

fn main() {
    let handle = thread::spawn(|| {
        let answer = 21 * 2;
        answer // 閉包的回傳值
    });

    let result = handle.join().expect("執行緒發生錯誤");
    println!("從另一個執行緒拿到的結果：{}", result); // 42
}
```

這是從另一個執行緒把計算結果傳回來最簡單的方式。

### `move` 閉包

如果閉包裡要用到外面的變數，一般需要加 `move`：

```rust,compile_fail
use std::thread;

fn main() {
    let name = String::from("Rust");

    let handle = thread::spawn(move || {
        println!("Hello, {}!", name);
    });

    println!("{}", name); // 編譯錯誤！name 已經被 move 進閉包了

    handle.join().expect("執行緒發生錯誤");
}
```

為什麼需要 `move`？因為 `thread::spawn` 不只能在 `main` 裡呼叫——任何函數都可以 `spawn` 執行緒。新執行緒的生命週期不確定，它可能活得比呼叫它的函數還久。如果閉包只是借用 `name`，而那個函數先結束、把 `name` 丟掉了，閉包就拿著一個懸垂參考。加上 `move` 之後，`name` 的所有權搬進了閉包裡，不管原本的作用域怎麼結束，閉包都能繼續用它。

### 輸出交錯

多個執行緒同時跑的時候，它們的輸出會交錯——每次執行結果可能不一樣：

```rust
use std::thread;

fn main() {
    let h1 = thread::spawn(|| {
        for _ in 0..5 {
            println!("AAA");
        }
    });

    let h2 = thread::spawn(|| {
        for _ in 0..5 {
            println!("BBB");
        }
    });

    h1.join().expect("執行緒發生錯誤");
    h2.join().expect("執行緒發生錯誤");
}
```

跑幾次看看，你會發現 AAA 和 BBB 的順序每次都可能不同。這就是多執行緒的特性——執行順序是不確定的。

## 範例程式碼

```rust
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];

    let handle = thread::spawn(move || {
        let sum: i32 = data.iter().sum();
        println!("子執行緒算出的總和：{}", sum);
        sum
    });

    // data 已經被 move 了，這裡不能再用
    // println!("{:?}", data); // 編譯錯誤

    let result = handle.join().expect("執行緒發生錯誤");
    println!("主執行緒收到結果：{}", result);
}
```

## 重點整理

- `thread::spawn(|| { ... })` 建立一個新的執行緒
- `main` 結束時所有執行緒跟著死，用 `.join()` 等待執行緒完成
- `.join()` 還能拿到閉包的回傳值，是從另一個執行緒傳回結果最簡單的方式
- 閉包裡要用外面的變數一般需要 `move`，因為不確定新執行緒的生命週期
- 多個執行緒的執行順序是不確定的，輸出可能會交錯