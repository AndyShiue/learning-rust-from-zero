# 多個方法的 `trait` 與預設實作

## 本集目標

學會在 `trait` 中定義多個方法，以及用預設實作讓實作者只需覆寫需要的部分。

## 概念說明

第 4 章學 `trait` 的時候，我們的 `trait` 都只有一個方法。其實 `trait` 可以有很多個方法，而且有些方法可以提供**預設實作**——也就是先寫好一個「通用版本」，實作者不喜歡再覆寫。

### 多個方法

```rust,noplayground
trait Describe {
    fn name(&self) -> String;
    fn description(&self) -> String;
}
#
# fn main() {}
```

實作的時候，所有方法都必須提供：

```rust,ignore
# trait Describe {
#     fn name(&self) -> String;
#     fn description(&self) -> String;
# }
#
# struct Cat;
#
impl Describe for Cat {
    fn name(&self) -> String { ... }
    fn description(&self) -> String { ... }
}
#
# fn main() {}
```

### 預設實作

有些方法可以先寫好一個合理的預設版本：

```rust,noplayground
trait Describe {
    fn name(&self) -> String;

    fn description(&self) -> String {
        let n = self.name();
        let mut result = String::from("我是 ");
        result.push_str(&n);
        result
    }
}
#
# fn main() {}
```

`description` 有預設實作，它呼叫了 `name()` 來組合字串。實作 `Describe` 的時候，只需要提供 `name()` 就好——`description()` 會自動使用預設版本。

當然，你也可以覆寫預設實作，提供自己的版本。

### 預設實作可以呼叫其他方法

注意上面的 `description` 預設實作裡呼叫了 `self.name()`。這是允許的——預設實作可以使用同一個 `trait` 中的其他方法。這讓你可以建立「只要提供幾個基本方法，其他方法就自動有了」的設計。

## 範例程式碼

```rust,editable
trait Describe {
    // 必須實作的方法
    fn name(&self) -> String;

    // 預設實作：可以直接用，也可以覆寫
    fn description(&self) -> String {
        let n = self.name();
        let mut result = String::from("我是 ");
        result.push_str(&n);
        result
    }
}

struct Cat {
    nickname: String,
}

struct Dog {
    nickname: String,
}

// Cat 只實作 name，description 用預設的
impl Describe for Cat {
    fn name(&self) -> String {
        self.nickname.clone()
    }
}

// Dog 覆寫 description
impl Describe for Dog {
    fn name(&self) -> String {
        self.nickname.clone()
    }

    fn description(&self) -> String {
        let n = self.name();
        let mut result = String::from("汪汪！我叫 ");
        result.push_str(&n);
        result.push_str("，我是一隻狗！");
        result
    }
}

fn main() {
    let cat = Cat { nickname: String::from("小橘") };
    let dog = Dog { nickname: String::from("阿柴") };

    // Cat 用預設的 description
    println!("{}", cat.name());
    println!("{}", cat.description());

    // Dog 用自訂的 description
    println!("{}", dog.name());
    println!("{}", dog.description());
}
```

## 重點整理

- `trait` 可以定義多個方法
- 方法可以提供**預設實作**——在方法後面直接寫 `{ ... }` 而不是 `;`
- 預設實作可以呼叫同一個 `trait` 中的其他方法
- 實作 `trait` 時，有預設實作的方法可以不寫（使用預設版本），也可以覆寫
