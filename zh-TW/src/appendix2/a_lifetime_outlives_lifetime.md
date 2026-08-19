# `'a: 'b`

## 本集目標

理解 `'a: 'b` 實際解決什麼問題：當泛型 API 同時處理長期資料與短期操作時，如何明確告訴編譯器哪一段生命週期必須活得比較久。

> 本集是**第 5 章生命週期**的補充。

## 正文

第 5 章看過這種 bound：

```rust,ignore
T: 'a
```

它表示 `T` 裡面的參考都必須活得過 `'a`。bound 的兩邊也可以都是生命週期：

```rust,ignore
'a: 'b
```

這讀成「`'a` **活得過** `'b`」（`'a` outlives `'b`），意思是 `'a` 至少和 `'b` 一樣長。

這種寫法真正的用途不是計算兩個區域變數誰先離開，而是替**泛型程式碼提供一項可以使用的保證**。若 `'a` 和 `'b` 是兩個互不相關的生命週期參數，函數或型別不能自行假設誰比較長；加上 `'a: 'b` 後，程式碼才能安全地把綁在 `'a` 上的資料，放到只需要維持 `'b` 的位置。

### 實務問題：長期設定值作為短期 fallback

假設一個服務有長期存在的設定，也允許每次 request 暫時指定語言：

```rust,noplayground
struct Config {
    default_language: String,
}
#
# fn main() {}
```

我們希望 `language_for_request` 優先回傳 request 指定的語言，沒有指定時就借用設定中的預設值：

```rust,compile_fail
struct Config {
    default_language: String,
}

fn language_for_request<'config, 'request>(
    config: &'config Config,
    requested: Option<&'request str>,
) -> &'request str {
    match requested {
        Some(language) => language,
        None => &config.default_language,
    }
}
#
# fn main() {}
```

這段不能編譯。`Some` 分支回傳的是 `&'request str`，但 `None` 分支回傳的是借用 `config` 的 `&'config str`。函數簽名只宣告了兩個生命週期，沒有說明兩者的長短關係。

對編譯器來說，呼叫者可能拿一個很短的 `config`，卻要求函數回傳活得更久的 `&'request str`。因此它不能直接把 `&'config str` 當成 `&'request str`。

這正是 `'config: 'request` 要解決的問題：

```rust,editable
struct Config {
    default_language: String,
}

fn language_for_request<'config, 'request>(
    config: &'config Config,
    requested: Option<&'request str>,
) -> &'request str
where
    'config: 'request,
{
    match requested {
        Some(language) => language,
        None => &config.default_language,
    }
}

fn main() {
    let config = Config {
        default_language: String::from("zh-TW"),
    };

    {
        let request_language = String::from("en");
        let selected = language_for_request(&config, Some(&request_language));
        println!("request 指定：{selected}");
    }

    {
        let selected = language_for_request(&config, None);
        println!("使用預設值：{selected}");
    }
}
```

`'config: 'request` 保證設定資料在整段 `'request` 期間都仍有效。因此 `None` 分支可以把原本的 `&'config str` **縮短**成 `&'request str`，讓兩個分支回傳同一個型別。

這就是 lifetime outlives lifetime 最直接的實務用途：

- 輸入資料來自兩段角色不同的生命週期。
- API 選定其中一段作為回傳值或操作結果的生命週期。
- 另一段資料若也可能成為結果來源，就必須保證它活得過那段生命週期。

### 哪些 API 會有這種關係？

先不用記很多 API 名稱。這種關係通常只是在描述下面這個情況：

> 有一份活得比較久的資料，我們暫時借用它，做出一個只會使用一小段時間的結果或工具。

剛才的 `Config` 就是如此：

- `config.default_language` 活得比較久。
- `language_for_request` 只需要回傳一個在這次 request 期間有效的 `&str`。
- 因此設定的生命週期必須活得過 request 的生命週期。

接下來的 `DebugStruct` 也是同一件事：

- `Formatter` 和它使用的輸出目標活得比較久。
- `DebugStruct` 只會暫時借用 `Formatter`，協助組合這一次的輸出。
- 因此 `Formatter` 內部資料的生命週期，必須涵蓋 `DebugStruct` 所持參考的生命週期。

一般程式裡，編譯器常常能自動推斷這種關係，所以你不會到處看到 `'long: 'short`。它比較常出現在函式庫的型別簽名中。現階段只要記得：**暫時借用一份長期資料時，長期資料不能比取得的參考更早失效。**

### 真實案例：`DebugStruct<'a, 'b>`

標準庫用來協助實作 `Debug` 的 `DebugStruct`，定義大致如下：

```rust,ignore
pub struct DebugStruct<'a, 'b: 'a> {
    fmt: &'a mut Formatter<'b>,
    // 其他欄位省略
}
```

`'b: 'a` 和下面的 `where` 寫法相同：

```rust,ignore
pub struct DebugStruct<'a, 'b>
where
    'b: 'a,
{
    fmt: &'a mut Formatter<'b>,
}
```

這裡的兩段生命週期各有明確角色：

- `'a` 是 `DebugStruct` 暫時借用 `Formatter` 的期間。
- `'b` 是 `Formatter` 內部輸出目標的生命週期。

`DebugStruct` 在 `'a` 期間會透過 `Formatter<'b>` 寫入輸出目標，所以該輸出目標不能在 builder 還存在時先失效。`'b: 'a` 就是這項要求：`Formatter` 內部借用的資料，必須活得過外層 builder 持有的參考。

使用者通常不必親自寫出這兩個生命週期：

```rust,editable
use std::fmt;

struct Account {
    id: u64,
    token: String,
}

impl fmt::Debug for Account {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("Account")
            .field("id", &self.id)
            .field("token", &"<已隱藏>")
            .finish()
    }
}

fn main() {
    let account = Account {
        id: 7,
        token: String::from("secret-token"),
    };

    println!("{account:?}");
}
```

這段程式真正使用了 `DebugStruct`，但 `Formatter::debug_struct` 已經把正確的生命週期關係寫在 API 裡，呼叫者只要滿足它即可。你通常是在閱讀標準庫文件、替這類 builder 建立泛型包裝，或設計自己內含多層參考的型別時，才會直接看到或寫出 `'b: 'a`。

### 分開兩段生命週期有什麼好處？

`DebugStruct` 為什麼不只使用一個生命週期？我們可以寫一組簡化版來比較。

先用 `FormatterLike` 代表 `Formatter`。它借用真正存放輸出文字的 `String`：

```rust,ignore
struct FormatterLike<'buffer> {
    output: &'buffer mut String,
}
```

如果 builder 只使用一個 `'a`，外層對 `FormatterLike` 的參考和裡面對 `String` 的參考會被迫使用同一段生命週期：

```rust,compile_fail
struct FormatterLike<'buffer> {
    output: &'buffer mut String,
}

struct BadBuilder<'a> {
    formatter: &'a mut FormatterLike<'a>,
}

impl BadBuilder<'_> {
    fn field(&mut self, text: &str) {
        self.formatter.output.push_str(text);
    }
}

fn write_two_parts<'buffer>(formatter: &mut FormatterLike<'buffer>) {
    let mut first = BadBuilder { formatter };
    first.field("第一段");

    formatter.output.push(' ');

    let mut second = BadBuilder { formatter };
    second.field("第二段");
}
#
# fn main() {}
```

`FormatterLike<'buffer>` 裡的 `String` 可能會被借用很久，但 `BadBuilder` 其實只需要暫時借用 `formatter`。把兩者都寫成 `'a` 後，編譯器卻得把外層可變參考和內層資料綁成同樣長，導致第一個 builder 用完後仍無法再次使用 `formatter`。

分成兩段生命週期就能準確描述需求：

```rust,editable
struct FormatterLike<'buffer> {
    output: &'buffer mut String,
}

struct Builder<'borrow, 'buffer: 'borrow> {
    formatter: &'borrow mut FormatterLike<'buffer>,
}

impl Builder<'_, '_> {
    fn field(&mut self, text: &str) {
        self.formatter.output.push_str(text);
    }
}

fn write_two_parts<'buffer>(formatter: &mut FormatterLike<'buffer>) {
    let mut first = Builder { formatter };
    first.field("第一段");

    formatter.output.push(' ');

    let mut second = Builder { formatter };
    second.field("第二段");
}

fn main() {
    let mut output = String::new();
    let mut formatter = FormatterLike {
        output: &mut output,
    };
    write_two_parts(&mut formatter);

    println!("{output}");
}
```

這裡的 `'buffer` 是內部 `String` 被借用的時間，`'borrow` 則是某一個 builder 暫時借用 `FormatterLike` 的時間。`'buffer: 'borrow` 只要求內部輸出活得過這個短期參考，不會反過來延長短期參考的生命週期。

兩個版本的變數與作用域完全一樣，唯一差別就是 builder 的生命週期設計。在正確版本中，`first` 最後一次被使用後，編譯器便能結束它所持有的 `formatter` 參考；接著可以直接寫入 `formatter`，也能建立第二個 `Builder`。`DebugStruct<'a, 'b: 'a>` 使用兩段生命週期，帶來的正是這種彈性：**底層輸出可以長期存在，每一個格式化 builder 只在需要時短暫借用 `Formatter`。**

### 反過來不能延長

outlives bound 只允許把較長的保證縮短使用，不能讓短期資料憑空活得更久：

```rust,compile_fail
fn extend<'short, 'long>(short: &'short str, _long: &'long str) -> &'long str
where
    'long: 'short,
{
    short
}
#
# fn main() {}
```

`'long: 'short` 表示 `'long` 比 `'short` 長，但函數卻想把只保證活到 `'short` 的參考回傳成 `&'long str`。bound 沒有提供這項保證，因此不能編譯。

## 重點整理

- 兩個生命週期參數預設互不相關；泛型程式不能自行假設誰比較長。
- `'long: 'short` 提供「`'long` 至少和 `'short` 一樣長」的保證。
- 有了這項保證，`&'long T` 可以縮短成 `&'short T`，用作短期操作的回傳值或內部參考。
- 長期設定值作為短期 request 的 fallback，是這種 bound 的直接應用。
- 一般呼叫端多半靠推斷；設計或閱讀保留多段生命週期角色的泛型 API 時，才常直接遇到 `'a: 'b`。
- outlives bound 只能證明既有關係，不能延長任何資料的壽命。
