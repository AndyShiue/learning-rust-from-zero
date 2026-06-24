# Tokio 以外的 runtime

## 本集目標

理解「Rust 語言本身不附 runtime」這件事,認識 Tokio 以外的選擇,以及寫程式庫時該注意的事。

## 概念說明

### 語言只給抽象,runtime 要自己選

這一章我們從頭手刻過一台迷你 runtime,也用了 Tokio。現在來釐清一個容易混淆的分界:**Rust 標準庫只定義了 `Future`、`poll`、`Pin`、`Waker` 這些「語言層的抽象」,但它不提供一個 runtime。**

也就是說,標準庫告訴你「future 長什麼樣、怎麼被 poll」,但**沒有**附一個 executor 去 poll 它、也沒有附 reactor 去等 I/O、沒有附計時器、沒有 `spawn`。這些全都要靠外部的 runtime crate 提供。這就是為什麼從第 1 集開始,我們就得在 `Cargo.toml` 加 `tokio`——沒有它,`async fn` 寫得出來,卻沒有東西去跑它。

(對照一下:很多別的語言,async runtime 是內建在語言或標準庫裡的,你不用選。Rust 選擇把它留給生態系,好處是可以針對不同場景換不同的 runtime,代價就是你得自己挑一個。)

### 一個 runtime 通常包含什麼

把這一章的零件列出來,正好就是一個 runtime 該有的東西:

- **executor**:排程並 poll task(第 6、12 集)。
- **reactor**:等 I/O 事件,好了就喚醒 task(第 14 集)。
- **timer**:計時器,支撐 `sleep`、`timeout`(我們第 7 集手寫過陽春版)。
- **I/O 與 task API**:`TcpStream`、`spawn`、channel、鎖等好用的工具。

### Tokio 以外的選擇

Tokio 是目前最主流、生態最豐富的 runtime,初學就用它準沒錯。但你會在社群裡看到其他名字,簡單認識一下:

- **smol**:走輕量、精簡路線的 runtime,程式碼小、容易讀。
- **async-std**:曾經想做成「async 版的標準庫」,API 風格貼近 std;但**已停止維護**,新專案別選它了,認得這名字、知道它退場了即可。
- **特化型 runtime**:有些 runtime 為特定場景而生,例如 **monoio**、**glommio**(走 thread-per-core、搭配 Linux 的 io_uring,追求極致 I/O 效能),以及 **Embassy**(給沒有作業系統的嵌入式裝置用的 async runtime)。

它們之間的差異主要在:API 長相不同、底層 I/O driver 不同(epoll vs io_uring 等)、task model 不同(會不會跨執行緒搬動 task)。所以**為某個 runtime 寫的程式碼,不一定能直接搬到另一個上面跑**——例如 `tokio::spawn`、`tokio::time::sleep` 是 Tokio 專屬的。

### 寫程式庫時:盡量和 runtime 脫鉤

這帶出一個實務上的好習慣,尤其當你寫的是要給別人用的**程式庫(library)**而不是自己的應用程式時:

> 盡量把**和 runtime 無關**的部分,跟**綁定特定 runtime** 的部分分開。

「組合 future 的邏輯」(接受一個 future、`.await` 它、用 `join` / `select` 把幾個 future 兜起來)是**runtime-agnostic** 的——它只依賴標準庫的 `Future` 抽象,在哪個 runtime 上都能跑。而「`tokio::time::sleep`、`tokio::net::TcpStream`、`tokio::spawn`」這些是**runtime-specific** 的,寫進你的程式庫就等於強迫使用者也得用 Tokio。

所以寫程式庫時,理想是讓核心邏輯只碰 `Future`、把「要怎麼計時、怎麼開連線、怎麼 spawn」這些留給使用者決定(或透過設定切換)。這樣你的程式庫才能服務用不同 runtime 的人。對初學階段、自己寫應用程式來說,直接用 Tokio、不用煩惱這層;但知道有這個分界,以後寫共用的東西會少踩很多坑。

## 範例程式碼

這一集是觀念與生態介紹,沒有新的可執行範例。記住這張分界圖就好:

```text
標準庫(語言層)            外部 runtime(Tokio / smol / ...)
─────────────────         ──────────────────────────────────
Future / poll             executor(排程 + poll)
Pin / Unpin               reactor(等 I/O)
Waker / Context           timer(sleep / timeout)
async / await 語法         I/O 型別、spawn、channel、鎖 ...

→ 語言只給左邊;右邊要自己選一個 runtime 補上
```

## 重點整理

- Rust 標準庫只定義 `Future`／`Pin`／`Waker` 等**抽象**,**不附 runtime**——所以一定要自己加一個(如 Tokio)
- 一個 runtime 通常含 **executor、reactor、timer、I/O 與 task API**(正是這一章手刻過的零件)
- Tokio 最主流;其他有輕量的 **smol**、已停止維護的 **async-std**、特化的 **monoio / glommio / Embassy**
- 不同 runtime 的 API、I/O driver、task model 可能不同,為某個 runtime 寫的程式碼不一定能搬到別的上
- 寫**程式庫**時,盡量把 runtime-agnostic 的 future 組合邏輯,和 runtime-specific 的 I/O／timer／spawn 分開
