# Sharing Claude Code Plugins

Sharing 團隊共用的 Claude Code plugin marketplace。

## 安裝

前置：已安裝 `gh` CLI 並完成 `gh auth login` (本 repo 為 private，且評估 skill 會用 `gh api` 查 repo 狀態)。

在 Claude Code 對話中：

```
/plugin marketplace add Pacino26/sharing-claude-plugins
/plugin install resource-security-review@sharing-claude-plugins
```

或在終端機：

```bash
claude plugin marketplace add Pacino26/sharing-claude-plugins
claude plugin install resource-security-review@sharing-claude-plugins
```

更新到新版：

```
/plugin marketplace update sharing-claude-plugins
/plugin update resource-security-review@sharing-claude-plugins
```

背景自動更新 private repo 需要 git credential helper：

```bash
gh auth setup-git
```

## Plugins

| Plugin | 用途 |
|--------|------|
| `resource-security-review` | 第三方資源安裝前的資安評估，產出 🟢🟡🔴 風險報告 |

## resource-security-review

**一句話**：要裝外掛、skill、MCP 或套件之前，先讓 Claude 做一次「資安健檢」，看這個東西能不能放心用。

**怎麼用**
- 直接貼連結問，例如「這個 skill 安全嗎？https://github.com/xxx/yyy」，skill 會自動觸發
- 也可以手動打 `/resource-security-review:resource-security-review`
- 支援：Chrome 外掛、GitHub repo / CLI 工具、Claude Skill、Claude Code Plugin、MCP Server、npm / pip 套件

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
