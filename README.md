# resource-security-review

Claude Code plugin：第三方資源 (Chrome 外掛、GitHub repo、Claude Skill / Plugin、MCP Server、npm / pip 套件) 安裝前的資安評估，產出 🟢🟡🔴 風險報告。

> **只能在 Claude Code 的本機 session 使用**：終端機、Claude 桌面 App 的 Code 分頁 (本機 session)、VS Code / JetBrains 擴充都可以。claude.ai 的聊天模式 (網頁、桌面 App 的 Chat 分頁、手機 App)、Cowork、claude.ai/code 與雲端 session 都用不到。

## 最快的安裝方式

把下面這段貼給你的 Claude Code，它會依照本頁的「安裝步驟」幫你裝：

```
請幫我安裝 resource-security-review 這個 Claude Code plugin，裝好後教我怎麼用。
來源：https://github.com/Pacino26/resource-security-review
```

## 安裝步驟

1. **事前準備**：安裝本身只需要 `git`；下面這些是評估時才用到，可以裝完再補。
   - `gh` (並且已經 `gh auth login`)：抓 GitHub 原始檔、查 repo 的 stars 和更新時間
   - `python3`：掃描隱藏字元。Mac 裝了 git 就會有
   - `curl`、`unzip`：下載與解開 Chrome 外掛、套件。Mac 內建
   - `npm`：評估 npm 套件時才需要
2. **先看過再裝 (建議)**：這是資安工具，自己也該被檢查。裝之前可以先讀 [SKILL.md](skills/resource-security-review/SKILL.md)、[references/TEMPLATE.md](skills/resource-security-review/references/TEMPLATE.md) 和 [scripts/scan_hidden.py](skills/resource-security-review/scripts/scan_hidden.py)，確認它只讀檔、不執行被評估的程式。
3. **安裝**：依你用的環境擇一。終端機、桌面 App 的本機 session、VS Code 擴充共用同一份設定，用哪一種裝，其他兩個都能用。
   - **有 `claude` 指令 (終端機)**：

     ```bash
     claude plugin marketplace add Pacino26/resource-security-review
     claude plugin install resource-security-review@resource-security-review
     ```

   - **VS Code 擴充**：在對話框輸入 `/plugins` 打開 Manage plugins → **Marketplaces** 分頁輸入 `Pacino26/resource-security-review` 新增 → **Plugins** 分頁找到 resource-security-review，按 **Install** 並選 Install for you。
   - **桌面 App，或找不到 `claude` 指令**：把下面這段合併進 `~/.claude/settings.json` (原本就有內容的話合併進去，不要整份覆蓋)。這跟終端機指令寫進設定檔的內容相同，另外多了自動更新。這一步會改到你的 Claude Code 設定檔，請先看過內容再同意。

     ```json
     {
       "extraKnownMarketplaces": {
         "resource-security-review": {
           "source": { "source": "github", "repo": "Pacino26/resource-security-review" },
           "autoUpdate": true
         }
       },
       "enabledPlugins": {
         "resource-security-review@resource-security-review": true
       }
     }
     ```

4. **載入**：重開 Claude Code (桌面 App 開一個新的 session)，或在對話框輸入 `/reload-plugins`。用改設定檔的方式裝時，第一次啟動會在背景下載，還沒出現就再重開一次。
5. **開啟自動更新 (建議)**：見下一節。改設定檔安裝的已經開好了。

### 開啟自動更新

這是第三方 marketplace，Claude Code 預設**不會**自動更新它，不開的話之後出新版你不會收到。開一次就好，擇一：

- **改設定檔 (各環境通用)**：在 `~/.claude/settings.json` 的 `resource-security-review` 那一段，`source` 旁邊加上 `"autoUpdate": true` (寫法見上面安裝步驟的 JSON)
- **終端機**：在終端機的 Claude Code 對話中輸入 `/plugin` → **Marketplaces** 分頁 → 選 `resource-security-review` → **Enable auto-update**

開啟後，送出第一則訊息後的 10 分鐘內會自己檢查新版；更新下載好之後，要重開 Claude Code (或執行 `/reload-plugins`) 才會生效。

沒開自動更新時，在終端機手動更新到新版：

```bash
claude plugin marketplace update resource-security-review
claude plugin update resource-security-review@resource-security-review
```

## 怎麼用

- **在哪裡用**：只能在 Claude Code 的本機 session 用 (見本頁開頭)，claude.ai 聊天模式用不到
- **直接貼連結問**：「<網址> 這個安全嗎？」或「幫我評估 <網址>」，通常就會自動啟動審查
- **手動啟動**：沒有自動啟動時，輸入 `/resource-security-review:resource-security-review`，後面接網址
- **支援**：Chrome 外掛、GitHub repo / CLI 工具、Claude Skill、Claude Code Plugin、MCP Server、npm / pip 套件
- **第一次試用**：可以先評估它自己，「幫我評估 <https://github.com/Pacino26/resource-security-review>」。因為它會在本機跑 shell 指令，依自己的評分規則最高只會拿到 🟡，這是正常的

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
