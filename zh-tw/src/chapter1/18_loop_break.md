# `loop` + `break`

## 本集目標

用 `loop` 做出一個無限迴圈，再用 `break` 在適當的時機跳出來。

## 正文

到目前為止，我們的程式都是跑一次就結束。但如果有些事情需要重複做呢？比如倒數計時：5、4、3、2、1、發射！

這就需要**迴圈**。

### `loop` —— 無限迴圈

`loop` 就是一直跑、一直跑，永遠不停：

```rust,no_run
fn main() {
    loop {
        println!("停不下來啊啊啊");
    }
}
```

如果你真的跑了這段程式，它會一直印一直印……你得用 `Ctrl + C` 強制停止它。

所以我們需要一個「出口」。

### `break` —— 跳出迴圈

```rust,editable
fn main() {
    let mut count = 5;
    loop {
        if count == 0 {
            println!("發射！");
            break;
        }
        println!("{}", count);
        count -= 1;
    }
}
```

### 它是怎麼運作的？

1. `count` 從 5 開始
2. 進入 `loop`，先檢查 `count == 0` 嗎？不是，印出 5，然後 `count -= 1`，count 變成 4
3. 再回到 `loop` 的開頭，檢查 `count == 0` 嗎？不是，印出 4，count 變成 3
4. ……一直重複……
5. 當 `count` 變成 0，`if count == 0` 成立，印出「發射！」，然後 `break` 跳出迴圈
6. 程式結束

## 重點整理

- `loop` 會無限重複執行大括號裡的程式碼
- `break` 用來跳出迴圈，讓程式繼續往下跑
- 沒有 `break` 的 `loop` 就是無限迴圈，記得要有出口
