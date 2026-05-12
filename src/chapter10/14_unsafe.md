# `unsafe`

## 本集目標

理解 `unsafe` 的意義、能做什麼、以及寫 `unsafe` 程式碼時該注意什麼。

## 概念說明

### 為什麼需要 `unsafe`

Rust 的安全保證建立在一些**假設**上——例如 `&mut T` 一定是獨佔的、參考一定指向有效的資料。編譯器會幫你檢查這些假設是否成立。

但有些操作是編譯器無法驗證的。Rust 不是不讓你做這些事，而是要你明確說「這段我自己負責」——這就是 `unsafe`。

### Rust 的安全保證

safe Rust 保證以下這些事情**不會發生**，不管你的程式碼怎麼寫：

- 不會存取到已經被釋放的記憶體
- 不會有資料競爭（多個執行緒同時讀寫且至少一方在寫）
- 不會有懸垂參考
- 不會同一個值被 `drop` 兩次
- 不會讀到未初始化的記憶體
- 不會把型別搞混（例如把 `i32` 的 bytes 當成 `f32` 來讀）

`unsafe `程式碼的責任就是：即使繞過了編譯器的檢查，也必須確保這些保證**全部成立**。

### `unsafe` 區塊

把需要 `unsafe` 操作的程式碼包在 `unsafe { }` 裡。`unsafe` 不是「關掉所有檢查」——借用規則、型別檢查在 `unsafe` 區塊裡照常運作。`unsafe` 只是多開放幾種特定操作。

### 五種 unsafe 操作

1. **解參考原始指標**（`*const T`、`*mut T`）
2. **呼叫 `unsafe` 函數**
3. **手動實作 `unsafe trait`**
4. **存取 `static mut` 變數**
5. **存取 `union` 的欄位**

### 原始指標

原始指標是沒有借用規則保護的指標。**建立**不需要 `unsafe`，**使用**（解參考）才需要：

```rust
# fn main() {
    let x = 42;
    let ptr: *const i32 = &raw const x; // 建立：不需要 unsafe

    let value = unsafe { *ptr }; // 解參考：需要 unsafe
    println!("{}", value); // 42
# }
```

你也可以用 `as` 從參考轉成原始指標：

```rust,noplayground
# fn main() {
    let x = 42;
    let ptr = &x as *const i32; // &i32 轉成 *const i32
# }
```

但 `&raw const x` 和 `&raw mut x` 更好——它們直接從變數拿到原始指標，不經過建立參考。有時候光是建立參考本身就可能違反規則（例如對未初始化的記憶體取 `&`），用 `&raw` 就沒有這個問題。

### `unsafe fn`

如果一個函數的安全性需要呼叫者自己保證，標記成 `unsafe fn`：

```rust,noplayground
unsafe fn dangerous(ptr: *const i32) -> i32 {
    unsafe { *ptr }
}

fn main() {
    let x = 42;
    let value = unsafe { dangerous(&raw const x) };
}
```

注意：在 Rust 2024 edition 後，即使在 `unsafe fn` 裡面，做 `unsafe` 操作也要寫 `unsafe { }` 區塊——讓每個 `unsafe` 操作都被明確標出。

### `unsafe trait`

有些 `trait` 的正確實作需要滿足編譯器沒辦法自動檢查的條件：

```rust,noplayground
unsafe trait MyGuarantee {
    fn check(&self) -> bool;
}

unsafe impl MyGuarantee for i32 {
    fn check(&self) -> bool { *self >= 0 }
}
#
# fn main() {}
```

`unsafe trait` 的意思是：「實作這個 `trait` 必須滿足某些編譯器沒辦法檢查的條件。」實作時用 `unsafe impl`，表示你保證那些條件成立。

`Send` 和 `Sync` 就是 `unsafe trait`——編譯器自動推導的時候沒問題，但如果你手動實作（覆蓋自動推導），你就必須自己保證多執行緒下的安全性。

注意：**呼叫** `unsafe trait` 的方法不需要 `unsafe`——危險的是實作，不是使用。

### `unsafe` 的邊界

`unsafe` 程式碼必須保證：**不管被什麼 safe code 呼叫，都不會造成未定義行為。**

例如標準庫的 `Vec`：內部用 `unsafe` 管理記憶體，但對外提供 safe 的 API。不管你怎麼用 `Vec` 的 safe API，都不可能觸發未定義行為。

### 寫 `unsafe` 程式碼的注意事項

- **盡量縮小 `unsafe` 區塊**——只包住真正需要 `unsafe` 的那幾行
- **寫 `// SAFETY:` 註解**——解釋為什麼這段 `unsafe` 操作是正確的
- **注意借用規則**——即使用原始指標，「`&mut` 必須獨佔」等規則在語意上仍然有效
- **維護型別的不變量**——例如 `String` 一定是合法 UTF-8、`bool` 一定是 0 或 1
- **考慮 panic safety**——如果 `unsafe` 區塊裡有可能 panic 的操作，確保 panic 後資料結構仍然合法
- **用 Miri 測試**——`cargo +nightly miri test` 可以偵測很多 `unsafe` 的問題

### 常見用途

- 實作資料結構（連結串列、`Vec` 的內部）
- 跟 C 語言互動
- 效能關鍵部分

## 範例程式碼

```rust
fn main() {
    // 原始指標
    let mut x = 42;
    let ptr_const: *const i32 = &raw const x;
    let ptr_mut: *mut i32 = &raw mut x;

    unsafe {
        println!("讀取：{}", *ptr_const);
        *ptr_mut = 100;
        println!("修改後：{}", *ptr_mut);
    }

    // unsafe fn
    unsafe fn add_one(ptr: *mut i32) {
        unsafe { *ptr += 1; }
    }

    let mut val = 10;
    // SAFETY: ptr 指向有效的、已初始化的 i32，且沒有其他參考
    unsafe { add_one(&raw mut val); }
    println!("val = {}", val);
}
```

## 重點整理

- `unsafe` 讓你做編譯器無法驗證的操作，但不是關掉所有檢查
- 五種 `unsafe` 操作：解參考原始指標、呼叫 `unsafe fn`、實作 `unsafe trait`、存取 `static mut`、存取 `union` 欄位
- 原始指標 `*const T` / `*mut T`：沒有借用規則保護的指標，不保證指向有效的資料。建立不需要 `unsafe`，解參考需要
- `&raw const x` / `&raw mut x`：直接拿原始指標，不經過參考
- `unsafe fn` 在 2024 edition 後也要寫 `unsafe { }` 區塊
- `unsafe trait` 的危險在實作，不在使用（呼叫方法不需要 `unsafe`）
- `unsafe` 程式碼的邊界：不管被什麼 safe code 呼叫都不能造成未定義行為
