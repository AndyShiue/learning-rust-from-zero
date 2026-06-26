# Tokio 以外的 runtime

## 本集目標

認識 Tokio 以外的 `async` runtime，並學會分辨自己寫的程式哪些綁定特定 runtime、哪些不綁。

## 正文

### 標準庫只定義語言層的抽象

這一章我們花了很大力氣，從零手寫了一個 runtime。這趟旅程其實也順帶證明了一件事：**Rust 標準庫並沒有內建 `async` runtime**。

標準庫只定義了**語言層的抽象**——`Future` `trait`、`Poll`、`Context`、`Waker`、`Pin` 這些。但「怎麼真正把 `Future` 跑起來」——executor 怎麼排程、reactor 怎麼盯 I/O、計時器怎麼實作——標準庫一概不管，全部留給第三方 runtime 自由發揮。我們前面手寫的東西（executor、reactor、timer、`Task` 的設計），正是一個 runtime 該包含的那些零件。

### 不只有 Tokio

Tokio 是目前最主流的 runtime，但不是唯一的選擇。因為標準庫不規定 runtime 怎麼寫，社群就長出了各有特色的好幾種：

- **Tokio**：功能最完整、生態最大的通用 runtime，多執行緒、什麼都有。本章後半用的就是它。
- **smol**：走輕量、精簡路線的 runtime，核心很小、容易理解。
- **monoio / glommio**：走 **thread-per-core** 路線的特化 runtime，常搭配 Linux 的 `io_uring`，為極致 I/O 效能而生。
- **Embassy**：給**嵌入式**裝置用的 runtime，能在沒有作業系統、沒有標準庫（`no_std`）的微控制器上跑 `async`。

這些 runtime 在各方面可能都不一樣：用幾條執行緒、怎麼排程、I/O 怎麼做、計時器怎麼實作、`spawn` 的細節與限制。選哪個，取決於你的場景——寫一般網路服務用 Tokio 最省事；做嵌入式就得用 Embassy。

### runtime-agnostic vs runtime-specific

既然有這麼多 runtime，寫程式時最好有個意識：你寫的這段程式碼，到底**綁不綁**特定 runtime？

- **runtime-agnostic（不綁 runtime）的部分**：純粹的 `Future` 組合邏輯。例如你自己 `impl Future`、用 `async` / `.await` 串接、用 `join!` / `select!` 組合、用 `FuturesUnordered`（第 31 集說過它不碰排程）——這些只依賴標準庫的 `Future` 抽象，搬到別的 runtime 上通常照樣能用。
- **runtime-specific（綁 runtime）的部分**：真正碰到外部世界或排程的東西。例如 `tokio::net::TcpStream`（I/O）、`tokio::time::sleep`（timer）、`tokio::spawn`（排程）——這些是 Tokio 提供的，換一個 runtime 就得換成它對應的版本。

實務上不必為了「runtime 中立」而綁手綁腳——大部分專案選定 Tokio 就一路用到底。但知道這個界線，能幫你在「想換 runtime」或「寫一個給別人用、不想綁死 runtime 的函式庫」時，清楚哪些程式碼可以原封不動、哪些得抽換。

### 結語

恭喜你讀完了整本書最硬的一章！回頭看，你從「`.await` 是什麼都不知道」，一路走到親手打造 executor、reactor、狀態機，再回到 Tokio 把各種實用工具一網打盡。`async` 之所以讓很多人卻步，多半是因為只看到表面的語法、不知道底下發生什麼事。而你現在不一樣——你看過底層的每一個齒輪，再看任何 `async` 程式，都能猜到它背後大概在做什麼。這正是這本書從第一頁開始就希望帶給你的能力。

## 重點整理

- Rust 標準庫只定義 `Future` 等**語言層抽象**，不內建 runtime；executor、reactor、timer、I/O、`Task` 設計都由 runtime 提供（正是我們手寫過的那些零件）
- Tokio 是主流通用 runtime；此外還有輕量的 smol、thread-per-core 的 monoio / glommio、嵌入式用的 Embassy 等，各方面設計可能不同
- 寫程式時可留意：純 `Future` 組合邏輯（自訂 `Future`、`join!`、`select!`、`FuturesUnordered`）大多 **runtime-agnostic**；I/O、timer、`spawn` 則是 **runtime-specific**，換 runtime 要抽換
