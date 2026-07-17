# `match` guard

## 本集目標

學會在 `match` 分支加上額外的條件判斷（guard）。

## 概念說明

pattern 很擅長檢查資料的形狀、固定值與範圍。不過 pattern 不會執行 `from == to` 這類欄位間的比較，而且使用 `let` 建立的變數不能當作 range pattern 的邊界。需要這類額外運算時，就可以使用 `match` guard。

Rust 的 **`match` guard** 可以在 pattern 後面加上 `if 條件`：

```text
pattern if 條件 => ...
```

例如，一筆感測器讀數會攜帶房間編號和測量值。我們可以先用 pattern 解構欄位，再用 guard 判斷測量值是否超過警戒線：

```rust,editable
enum Reading {
    Temperature { room: i32, celsius: i32 },
    Humidity { room: i32, percent: i32 },
    Offline { room: i32 },
}

fn main() {
    let reading = Reading::Temperature {
        room: 3,
        celsius: 34,
    };
    let heat_warning = 30;

    match reading {
        Reading::Temperature { room, celsius } if celsius >= heat_warning => {
            println!("{} 號房過熱：{} 度", room, celsius);
        }
        Reading::Temperature { room, celsius } => {
            println!("{} 號房溫度正常：{} 度", room, celsius);
        }
        Reading::Humidity { room, percent } if percent > 70 => {
            println!("{} 號房太潮濕：{}%", room, percent);
        }
        Reading::Humidity { room, percent } => {
            println!("{} 號房濕度正常：{}%", room, percent);
        }
        Reading::Offline { room } => {
            println!("{} 號房的感測器離線", room);
        }
    }
}
```

第一個分支可以分成兩步理解：

1. `Reading::Temperature { room, celsius }` 先確認資料是 `Temperature`，並把兩個欄位分別綁定成 `room` 和 `celsius`。
2. `if celsius >= heat_warning` 再使用剛才綁定的 `celsius` 做額外判斷。

pattern 匹配成功後，`room` 和 `celsius` 就能在 guard 與右邊的程式碼中使用。guard 也可以使用 pattern 以外、早已存在的變數，例如上面的 `heat_warning`。

## guard 不成立時會繼續往下

pattern 匹配成功，不代表這個分支一定執行。如果 guard 是 `false`，Rust 會繼續嘗試後面的分支。

以上面的溫度為例：

- 如果是 `Temperature` 而且 `celsius >= heat_warning`，執行第一個分支。
- 如果是 `Temperature` 但沒有達到警戒值，第一個 guard 失敗，接著由第二個 `Temperature` 分支處理。
- 如果根本不是 `Temperature`，第一、第二個 pattern 都不匹配，繼續尋找其他 variant。

所以有 guard 的分支通常放在較一般的分支前面。

guard 不只可以比較一個欄位和門檻，也能比較同一個 pattern 綁定的多個欄位：

下方範例的第一個 guard 比較 `from` 和 `to`，第二個 guard 比較 `amount` 和外部的 `daily_limit`。這類需要欄位間運算或執行時變數的條件，正是 guard 比單純 pattern 更合適的地方。

## 範例程式碼

```rust,editable
enum Request {
    Transfer {
        from: i32,
        to: i32,
        amount: i32,
    },
    CheckBalance {
        account: i32,
    },
}

fn main() {
    let request = Request::Transfer {
        from: 1001,
        to: 2002,
        amount: 1500,
    };
    let daily_limit = 1000;

    match request {
        Request::Transfer { from, to, amount } if from == to => {
            println!("帳戶 {} 不需要轉帳給自己，金額 {}", from, amount);
        }
        Request::Transfer { from, to, amount } if amount > daily_limit => {
            println!(
                "從帳戶 {} 轉 {} 到帳戶 {}，需要額外確認",
                from, amount, to
            );
        }
        Request::Transfer { from, to, amount } => {
            println!("從帳戶 {} 轉 {} 到帳戶 {}", from, amount, to);
        }
        Request::CheckBalance { account } => {
            println!("查詢帳戶 {} 的餘額", account);
        }
    }
}
```

## guard 與窮舉檢查

假設我們為 `Temperature` 寫了兩個分支：

- 一個 guard 是 `celsius >= heat_warning`。
- 另一個 guard 是 `celsius < heat_warning`。

我們看得出來，任何溫度一定會符合其中一個條件，邏輯上已經涵蓋所有可能。但 Rust 編譯器做窮舉檢查時，不見得能從 guard 之間的邏輯關係推論出「所有溫度都處理到了」。即使兩個分支都寫了，編譯器還是可能認為 `Temperature` 沒有被完整處理。

要讓涵蓋範圍對編譯器也很明確，可以保留一個**沒有 guard 的 pattern**。因此，前面的例子會讓第二個 `Temperature` 分支不加 guard：第一個分支處理達到警戒線的溫度，第二個分支接住其餘所有溫度。`Humidity` 和 `Transfer` 的分支也是同樣的安排。

## 重點整理

- `match` guard 的語法是 `pattern if 條件 => ...`。
- Rust 會先匹配 pattern、建立綁定，再檢查 guard。
- guard 可以使用同一個 pattern 綁定的變數，也可以使用外部已存在的變數。
- pattern 匹配但 guard 為 `false` 時，Rust 會繼續嘗試後面的分支。
- 即使幾個 guard 在邏輯上涵蓋所有可能，編譯器仍可能需要一個沒有 guard 的分支，才能確認 `match` 已經窮舉。
- guard 特別適合表達欄位之間的比較、計算，或和執行時門檻的比較。
