# resource-security-review

Claude Code plugin：第三方資源 (Chrome 外掛、GitHub repo、Claude Skill / Plugin、MCP Server、npm / pip 套件) 安裝前的資安評估，產出 🟢🟡🔴 風險報告。

> **只能在 Claude Code 使用**：終端機、Claude 桌面 App 的 Code 分頁、VS Code / JetBrains 擴充都可以。claude.ai 的聊天模式 (網頁、桌面 App 的 Chat 分頁、手機 App) 用不到。

## 最快的安裝方式

把下面這段貼給你的 Claude Code，它會依照本頁的「安裝步驟」幫你裝：

```
請幫我安裝 resource-security-review 這個 Claude Code plugin，裝好後教我怎麼用。
來源：https://github.com/Pacino26/resource-security-review
```

## 安裝步驟

1. **事前準備**：需要 `gh` (並且已經 `gh auth login`)、`python3`、`curl`、`unzip`。評估時會用 `gh api` 抓原始檔、查 repo 的 stars 和更新時間；掃描隱藏字元會用到 `python3`。Mac 裝了 git 就會有 `python3`，`curl` 和 `unzip` 是內建的。
2. **先看過再裝 (建議)**：這是資安工具，自己也該被檢查。裝之前可以先讀 `skills/resource-security-review/SKILL.md` 和 `skills/resource-security-review/scripts/scan_hidden.py`，確認它只讀檔、不執行被評估的程式。
3. **安裝**：在終端機執行

   ```bash
   claude plugin marketplace add Pacino26/resource-security-review
   claude plugin install resource-security-review@resource-security-review
   ```

   找不到 `claude` 指令時 (例如只用桌面 App)，改在 Claude Code 對話框輸入

   ```
   /plugin marketplace add Pacino26/resource-security-review
   /plugin install resource-security-review@resource-security-review
   ```

4. **載入**：輸入 `/reload-plugins` 或重開 Claude Code，新功能才會出現。
5. **開啟自動更新 (建議)**：見下一節。

### 開啟自動更新

這是第三方 marketplace，Claude Code 預設**不會**自動更新它，不開的話之後出新版你不會收到。開一次就好：

1. 在 Claude Code 對話中輸入 `/plugin`
2. 切到 **Marketplaces** 分頁，選 `resource-security-review`
3. 選 **Enable auto-update**

開啟後，每次開 Claude Code 送出第一則訊息後，會在 10 分鐘內自己檢查新版；更新下載好之後，要重開 Claude Code (或執行 `/reload-plugins`) 才會生效。

沒開自動更新時，手動更新到新版：

```
/plugin marketplace update resource-security-review
/plugin update resource-security-review@resource-security-review
```

## 怎麼用

- **直接貼連結問**：「<網址> 這個安全嗎？」或「幫我評估 <網址>」，就會自動啟動審查
- **手動啟動**：輸入 `/resource-security-review:resource-security-review`，後面接網址
- **支援**：Chrome 外掛、GitHub repo / CLI 工具、Claude Skill、Claude Code Plugin、MCP Server、npm / pip 套件
- **第一次試用**：可以先評估它自己，「幫我評估 https://github.com/Pacino26/resource-security-review」

## 功能說明

**一句話**：要裝外掛、skill、MCP 或套件之前，先讓 Claude 做一次「資安健檢」，看這個東西能不能放心用。

**它會做的事**
1. 抓目標的實際內容 (manifest、package.json、SKILL.md、原始碼)，**只讀，不安裝、不執行任何程式**
2. 用 `gh api` 等工具實際查作者、stars、最後更新時間、open issues，不憑印象
3. 逐項檢查：要了哪些權限、資料會傳到哪個網域、有沒有可疑的外部連線或安裝腳本
4. 比對紅旗清單 (例如：索取用不到的金鑰、夾帶執行檔、`curl | bash`、base64 混淆、偷改 CLAUDE.md / settings.json)
5. 開頭直接給結論：🟢 安全可用 / 🟡 有條件可用 / 🔴 不建議，後面用表格列出每項的燈號與理由；需要的話可以另外產一份 HTML 報告

**跟一般檢查不同的地方**：現在有攻擊會在 README 或 SKILL.md 裡藏給 AI 看的指令 (隱藏註解、零寬字元、白底白字)，讓「幫你檢查的 AI」先被騙。這個 skill 會把目標內容全部當成資料，不照著做；一發現這類藏起來的指令，就直接判 🔴。

**限制**
- 結論只對「評估當下的版本」有效，工具更新後建議重評 (特別是會自動更新的 Chrome 外掛和遠端 MCP)
- 工具安裝時才另外下載的程式 (npx、pip、遠端伺服器) 不在報告的檢查範圍內
- 權限很大的工具，還是建議在隔離環境 (VM、測試帳號) 實際試過再用
