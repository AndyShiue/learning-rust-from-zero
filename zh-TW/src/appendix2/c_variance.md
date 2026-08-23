# variance

## 本集目標

理解 covariance、invariance 與 contravariance，知道型別包在參考、`Cell` 或函數裡之後，原本的 subtype 關係會怎麼變化。

> 本集是**第 5 章生命週期**與本附錄前兩集的補充。

## 概念說明

前面我們已經知道：若 `'long: 'short`，一個 `&'long T` 可以縮短成 `&'short T`。這表示生命週期之間存在一種 **subtype**（子型別）關係：保證較長的參考，可以用在只要求較短保證的地方。

但把型別放進其他型別後，這個關係不一定照原樣保留。研究「包裝前後的 subtype 關係如何變化」，就是 variance。

### covariance：方向保持不變

先看共享參考：

```rust,editable
fn use_short<'short>(value: &'short str, _marker: &'short ()) {
    println!("{value}");
}

fn main() {
    let forever: &'static str = "我活到程式結束";

    {
        let marker = ();
        use_short(forever, &marker);
    }
}
```

`&'static str` 的生命週期很長，但 `use_short` 只要求和 `marker` 一樣短。Rust 可以把長參考當成短參考使用。

我們說 `&'a T` 對 `'a` 是 **covariant**（協變）的：如果 `'long` 是 `'short` 的 subtype，`&'long T` 也會是 `&'short T` 的 subtype，方向沒有改變。

`Box<T>`、`Vec<T>`、`Option<T>` 等擁有值的常見型別，對 `T` 通常也是 covariant。例如，若 `'long: 'short`，`Vec<&'long str>` 就能用在需要 `Vec<&'short str>` 的地方。這種用法會把整個 `Vec` 的所有權一起交出去，原本的位置不能再用較長的生命週期型別存取同一個 `Vec`。

### invariance：內層型別不能跟著轉換

可變參考比較特別。`&'a mut T` 對生命週期 `'a` 仍然可以縮短，但它對裡面的 `T` 是 **invariant**（不變）的。

原因是 `&mut T` 不只讓你讀 `T`，還讓你放進一個新的 `T`。

假設我們想執行下面這個賦值：

```rust,ignore
*slot = short;
```

`short` 的型別是 `&'short str`。要讓賦值成立，左邊的 `*slot` 也必須是 `&'short str`。而 `slot` 解參考後會得到 `*slot`，所以 `slot` 的型別必須是：

```rust,ignore
&mut &'short str
```

因此，負責放入短期參考的函數會寫成：

```rust,noplayground
fn replace_with_short<'short>(
    slot: &mut &'short str,
    short: &'short str,
) {
    *slot = short;
}
#
# fn main() {}
```

函數裡的賦值沒有問題，因為 `*slot` 和 `short` 都是 `&'short str`。問題會出現在呼叫端：

```rust,compile_fail
fn replace_with_short<'short>(
    slot: &mut &'short str,
    short: &'short str,
) {
    *slot = short;
}

fn main() {
    let mut forever: &'static str = "原本的長期資料";

    {
        let temporary = String::from("短期資料");
        replace_with_short(&mut forever, &temporary);
    }

    println!("{forever}");
}
```

`forever` 的型別是 `&'static str`，所以 `&mut forever` 的型別是 `&mut &'static str`。但 `temporary` 只能提供 `&'short str`，因此 `replace_with_short` 的第一個參數需要 `&mut &'short str`。

若允許呼叫，編譯器就得進行這項轉換：

```rust,ignore
&mut &'static str → &mut &'short str
```

接著函數裡的 `*slot = short` 便會把短期參考寫進 `forever`。可變借用結束後，`forever` 的型別仍宣稱自己是 `&'static str`，實際卻可能已經懸垂。因此 Rust 禁止的是呼叫端的轉換，不是函數裡那個兩邊型別相同的賦值。

因此，即使 `&'static str` 可以當成較短的 `&str`，`&mut &'static str` 也不能跟著任意轉成 `&mut &'short str`。包進 `&mut` 後，內層 `T` 的 subtype 關係被鎖住了。

`Cell<T>`、`RefCell<T>`、`Mutex<T>` 這類提供 interior mutability 的型別，對 `T` 一律 invariant。雖然表面拿到的可能只是 `&Cell<T>`，它們仍能更換裡面的值。

### contravariance：方向反轉

函數參數會出現第三種情況：**contravariance**（逆變）。

為了只觀察 variance，下面由外層函數先固定 `'short` 與 `'long`：

```rust,noplayground
fn use_as_long_only<'short, 'long: 'short>(
    can_accept_short: fn(&'short str),
) -> fn(&'long str) {
    // fn(&'short str) 在這裡轉成 fn(&'long str)。
    can_accept_short
}
#
# fn main() {}
```

若 `'long: 'short`，`&'long str` 可以當成 `&'short str` 使用。但包進函數參數後，可以轉換的方向會反過來：

```text
&'long str      → &'short str
fn(&'short str) → fn(&'long str)
```

`use_as_long_only` 傳回的函數只會收到 `&'long str`。原本的 `can_accept_short` 只要參考能活到 `'short` 就能處理；活得更久的 `&'long str` 當然也符合要求，所以這項轉換是安全的。

函數**輸入**型別的關係因此和直覺方向相反：要求較少、能接受更廣輸入的函數，可以放到要求較窄輸入的地方。函數參數對其型別是 contravariant。

相對地，函數**回傳值**和一般讀取相同，是 covariant：能回傳保證較長的參考，也就能滿足只要求較短參考的呼叫者。

### 一張速查表

| 型別位置 | 對參數的 variance | 直覺 |
| --- | --- | --- |
| `&'a T` | 對 `'a`、`T` covariant | 只能共享讀取，可以縮短保證 |
| `&'a mut T` | 對 `'a` covariant，對 `T` invariant | 能更換 `T`，不能改寫內層承諾 |
| `*const T` | 對 `T` covariant | 只能透過指標讀取 `T`，方向保持不變 |
| `*mut T` | 對 `T` invariant | 能透過指標更換 `T`，不能改寫內層承諾 |
| `Box<T>`、`Vec<T>`、`Option<T>` | 通常對 `T` covariant | 擁有值，不會從共享入口換入任意 `T` |
| `Cell<T>`、`RefCell<T>` | 對 `T` invariant | 共享狀態下仍可能更換內容 |
| `fn(T) -> U` | 對 `T` contravariant，對 `U` covariant | 能接受更廣的輸入，也能回傳保證更強的值 |

這張表用來查就好，不必背。遇到編譯器拒絕一個看似合理的生命週期縮短時，先問：「這個型別能不能把新的值寫進去？」如果可以，invariance 往往就是原因。

### variance 不會改變執行結果

variance 完全是編譯時期的型別規則，不會在執行時期插入轉換，也不會真的改造參考。編譯器只是在判斷一個型別能不能安全地用在另一個型別的位置。

## 範例程式碼

```rust,editable
fn choose_shorter<'short>(
    long: &'static str,
    short: &'short str,
    use_long: bool,
) -> &'short str {
    if use_long {
        long
    } else {
        short
    }
}

fn print_text(text: &str) {
    println!("函數收到：{text}");
}

fn use_as_long_only<'short, 'long: 'short>(
    can_accept_short: fn(&'short str),
) -> fn(&'long str) {
    // fn(&'short str) 在這裡轉成 fn(&'long str)。
    can_accept_short
}

fn main() {
    let local = String::from("區域字串");

    // 共享參考是 covariant：'static 可以縮短成 local 的生命週期。
    let selected = choose_shorter("長期資料", &local, true);
    println!("選到：{selected}");

    // 函數輸入是 contravariant：參數型別的轉換方向會反過來。
    let print_long: fn(&'static str) = use_as_long_only(print_text);
    print_long("來自字串字面值");
}
```

## 重點整理

- variance 描述把型別放進另一個型別後，原本的 subtype 關係如何變化。
- covariant 保留方向；共享參考、函數回傳值與許多擁有所有權的型別屬於這類。
- invariant 不允許沿著 subtype 關係轉換；可寫入內層值的 `&mut T`、`Cell<T>` 等常見於這類。
- contravariant 反轉方向；函數參數是主要例子。
- variance 是編譯時期規則，不會延長生命週期或產生執行時期轉換。
