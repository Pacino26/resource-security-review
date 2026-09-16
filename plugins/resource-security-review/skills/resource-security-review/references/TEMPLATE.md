# 資源安全評估模板

> 用於評估 Chrome 外掛、GitHub repo、Claude Skill、MCP Server、npm 套件等第三方資源。
> 報告為一次性產物，看完即丟；要存檔時先問使用者存哪 (建議檔名 `<類型>-<名稱>.md`，例：`chrome-voyager.md`)。

---

## 報告呈現格式

- **結論先行**：報告第一行就是 **風險等級**：🟢 安全可用 / 🟡 有條件可用 / 🔴 不建議 + 一句話 (與第 6 節相同)
- **表格化好讀**：第 1 節基本資訊、第 4 節逐項檢查都整理成表格，讓使用者一眼掃完
  - 基本資訊：`| 項目 | 內容 |`，每列內容前帶 ✅ / ⚠️ / ❌
  - 逐項檢查：`| 項目 | 燈號 | 說明 |`，燈號用 🟢 / 🟡 / 🔴 並置中

## 1. 基本資訊

- **名稱**：
- **類型**：Chrome 外掛 / GitHub repo / Claude Skill / MCP Server / npm 套件 / 其他
- **來源**：(完整 URL)
- **作者 / 維護者**：(帳號 + 是否為知名個人或組織)
- **授權**：MIT / Apache-2.0 / 未標示 / 其他
- **最後更新**：YYYY-MM-DD (GitHub 一律以 `pushed_at` 實際 code 變動為準，不用 `updated_at`——後者含 star / 描述異動會虛高)
- **評估版本**：(commit hash / 外掛版本號 / 套件版本 — 評估結論僅對此版本有效)
- **來源真偽**：知名作者的 fork / 同名複製品，要驗實際 repo 與 commit，不能憑原作名聲放行 (名氣 ≠ 信任)
- **熱度指標**：
  - GitHub：Stars / Forks / Open Issues / 最近 commit 距今
  - Chrome Web Store：使用者數 / 評分 / 評論數
  - npm：週下載數

## 2. 功能說明

- **一句話定位**：這個工具做什麼
- **核心功能**：條列 3 – 5 點
- **使用情境**：什麼時候會用到、解決什麼問題
- **運作方式**：本地執行 / 呼叫外部 API / 需要登入帳號

## 3. 權限與資料流

> 這節是安全評估最關鍵的一塊，務必具體到「它會碰到什麼資料」「傳到哪裡」。

- **宣告權限**：(Chrome 的 `permissions` / MCP 的 scope / Skill 會呼叫的工具)
- **外部連線**：會打哪些 domain、有沒有 hard-coded endpoint；留意 telemetry / analytics / improvement 開頭的非宣稱網址；外送的即使不是檔案內容，也要看是不是檔案路徑 / branch 名 / error message 這類中繼資料；logging 的關閉開關是不是真的有效 (有沒有「關了還是照記」)
- **讀取範圍**：只讀目前分頁 / 所有網站 / 剪貼簿 / 本地檔案系統
- **寫入行為**：會不會修改檔案、送出資料、執行 shell 指令
- **驗證方式**：是否需要 API key、token 存在哪裡 (localStorage / 系統 keychain / 明文檔案)

## 4. 安全風險評估

對每項打 ✅ / ⚠️ / ❌ 並附一句說明。

- [ ] **程式碼公開且可讀**：原始碼是否開源、是否混淆
- [ ] **權限是否最小化**：有沒有要求過多權限 (例：工具是擷取樣式卻要 `<all_urls>`)
- [ ] **無可疑外部連線**：有沒有送資料到作者自己的伺服器
- [ ] **無已知 CVE / 爭議**：查 GitHub Issues、Reddit、HN 有無資安討論
- [ ] **維護狀態健康**：近 6 個月有更新、Issue 有人回
- [ ] **作者可信度**：過往作品、社群活躍度、是否實名
- [ ] **依賴乾淨**：`package.json` / `requirements.txt` 沒有冷門或已廢棄套件
- [ ] **無危險指令**：不會執行 `curl | sh`、`base64` 解碼後執行、不會寫入 `~/.ssh`、不會動 git config
- [ ] **無 AI 指令注入**：README / SKILL.md / tool description 沒有指示 AI 執行額外動作的語句；無隱形指令 (隱藏 HTML 註解、零寬字元、Word / PDF 的白底白字或 1pt 極小字、異常行距)
- [ ] **無二階段 payload**：不會在執行時才從網路下載並執行內容 (Claude 給你看的可見碼乾淨 ≠ 安全，後續下載的不會再提示一次)
- [ ] **執行環境已釐清**：清楚會跑在哪 (Claude API 沙盒 vs Claude Code 本地)；本地預設無沙箱，等同你的帳號權限
- [ ] **不改持久化設定**：不會寫入 / append / auto-commit 你的 `CLAUDE.md` 或 `settings.json` 來改變 Claude 未來每個 session 的行為 (這是「注入你的未來」，比注入單次對話更難察覺)
- [ ] **不封鎖工具 / 不強制 routing**：沒有 `NEVER use mcp__` / `禁止使用` 封鎖特定工具，也沒有「永遠先呼叫我、不要直接回答」這種剝奪選擇權的強制 routing
- [ ] **無 proactive 自動接管**：不是預設 `proactive: true` + 誘導語 (「we recommend keeping it on」) 讓它不請自來插進每次互動，能完全 opt-in
- [ ] **無暗黑導流**：流程不夾帶第三方服務推廣、`utm_` / `ref=` 連結，或依行為訊號把使用者導去某處

## 5. 紅旗清單 (Red Flags)

若出現以下任一項，預設不使用：

- 混淆 / minify 過的程式碼但又不是 build output
- 要求讀寫所有網站但實際功能用不到
- 近一年無更新但要求敏感權限
- 作者帳號新、無其他作品、無公開身份
- README 與實際程式碼功能對不上
- 有 `eval()`、動態 `import()` 遠端字串
- 會自動安裝其他工具或下載執行檔
- 要求關閉 SIP / 要 sudo / 要 root
- 內容藏有針對 AI agent 的指令注入 (隱藏註解、零寬字元、白底白字 / 1pt 極小字、tool description 內藏指令即 tool poisoning、「ignore previous instructions」類語句)
- 執行時才從網路下載並執行內容 (二階段 payload — 可見程式碼乾淨不代表安全)
- 安裝包含密碼保護 / 加密壓縮檔 (正當軟體不會鎖住安裝包，目的是規避掃描器)
- 無法釘選版本且自動更新，而功能涉及敏感權限 (Chrome 外掛、remote MCP 特別注意 rug pull)
- 自動寫入 / commit 你的 `CLAUDE.md` 或 `settings.json`，改變未來 session 行為
- 封鎖特定工具 (`NEVER use mcp__` / 禁用官方工具) 或強制「永遠先呼叫我」
- 預設 proactive 開啟並用誘導語留住 (不請自來插進每次互動)
- 內建第三方推廣導流 (`utm_` / `ref=` / 自動開啟推廣 URL)

## 6. 總評與建議

- **風險等級**：🟢 安全可用 / 🟡 有條件可用 / 🔴 不建議
- **無紅旗時的分級準則**：紅旗任一命中即 🔴；紅旗全過時，只要符合任一項就上限 🟡 (不給 🟢) —— (a) 會跑本機 shell 或安裝執行檔；(b) 熱度極低且無第三方資安驗證；(c) 把信任轉嫁給外部元件 (`npx` / `pip` / `brew` 拉 repo 外內容、remote server 端可隨時變更)。轉嫁信任時，於報告註明「下載 / 伺服器端內容不在本報告涵蓋範圍」
- **建議用法**：
  - 先在隔離的測試專案試用
  - 限定專案使用
  - 可加入全域
  - 不採用
- **替代方案**：(如有更安全或更成熟的同類工具)
- **一句話結論**：

---

## 附註：不同類型工具的評估重點

### Chrome 外掛
- 看 `manifest.json` 的 `permissions` 和 `host_permissions`
- 看 `content_scripts.matches` 範圍
- 有無 `background` service worker 長駐並對外連線

### GitHub Repo / CLI 工具
- `package.json` 的 `scripts` 有沒有可疑的 pre/post install
- 有沒有 `install.sh` 會動系統設定
- 是否需要讀取 `.env`、`~/.aws/`、`~/.ssh/` 等敏感路徑

### Claude Skill / Plugin / MCP Server
- Skill 的 `SKILL.md` 描述的行為是否與實際執行一致
- frontmatter 有無動態 context (`` !`command` ``)：skill 載入時直接執行 shell，跑在任何模型層防護之前 (2026-02 ToxicSkills 攻擊的主要載體)
- `allowed-tools` 宣告了哪些 tool (Bash / Write / WebFetch)、skill 附帶的 scripts 實際做什麼
- Plugin 的 hooks (PreToolUse / SessionStart 等) 會自動執行什麼、marketplace 來源是否可信
- MCP Server 的通訊方式 (stdio / SSE / HTTP) 與目的地
- 有沒有把整個對話內容或檔案上傳到第三方
- rug pull 防範：記下評估版本；remote MCP 伺服器端隨時可變，🟢 結論要打折並註明
- **tool poisoning / 跨 server 汙染**：MCP 的 tool description 本身可能藏給 AI 的指令 (一讀就中)；多個 server 並存時，惡意 server 的 description 可操縱 AI 對另一個正常 server 的行為
- **confused deputy / token passthrough**：代理 OAuth 或持有憑證的 MCP server，可能被誘導拿著你的 token 去打它不該打的對象
- **執行環境決定風險**：同一份 SKILL.md 在 Claude API 是沙盒、在 Claude Code 本地吃滿主機權限；預設無沙箱，你能碰的檔案它都能碰
- **比對要看上下文**：命中 `curl` / `NEVER use X` 這類關鍵字後，務必讀周邊語境——「出現在解釋為何避免 X 的註解 / 反面教材」與「當成給 AI 的指令」意義完全不同，別只靠關鍵字命中就定罪或放行
- **staging 後再裝**：高權限目標建議「先下載到隔離暫存區審查、過關才落地安裝」，不要邊看邊直接裝進 `~/.claude/` 或系統

### 安裝前四招肉眼快速掃描 (Skill / repo 適用)

到 GitHub 用 Raw 檢視 `SKILL.md` 與 repo 檔案，逐招掃過，安裝前先擋掉明顯可疑的：

1. **環境變數 / 金鑰**：功能用不到卻索取 API key、token、env var → 警訊 (寫作工具沒道理要你的金鑰)
2. **夾帶可執行檔**：repo 裡有功能用不到的 `.sh` / `.py` / `.js` / 執行檔 → 帶了用不到的工具，問題常藏在那
3. **危險關鍵字**：全文搜 `curl` / `bash` / `base64` / `eval`；看到密碼保護的 zip → 直接拒裝
4. **陌生外部網址**：宣稱服務以外的 domain，尤其 telemetry / analytics / improvement 開頭

> 注意：肉眼掃描擋得住明碼，但零寬字元、白底白字、1pt 極小字「你看不到、AI 讀得到」— 高權限工具仍應在隔離環境實測，不能只靠肉眼。

### npm / pip 套件
- 下載量與版本歷史 (有無近期突然竄起)
- 名稱是否為 typosquatting (例：`reakt` 假裝 `react`)
- 看 `postinstall` script

---

## 參考資料：2026 上半年 agent 工具鏈供應鏈攻擊研究

報告需要佐證「這類手法真的有人在用」時可引用：

- **Snyk ToxicSkills (2026-02-05)**：掃描 3,984 個 agent skills，13.4% 有嚴重安全問題、36% 含 prompt injection。https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
- **Datadog Security Labs (2026-05-11)**：SKILL.md 動態 context `` !`command` `` 在載入時先執行 shell，跑在模型層防護之前。https://securitylabs.datadoghq.com/articles/malicious-skills-supply-chain-risks-in-coding-agents-with-dynamic-context/
- **Reversec Skill Issues (2026-05)**：惡意 skills / agents 入侵 Claude Code 的手法系列。https://labs.reversec.com/posts/2026/05/skill-issues-compromising-claude-code-with-malicious-skills-agents-part-1
- **Pluto Security**：同一份 SKILL.md 在 Claude API 是沙盒、在 Claude Code 本地繼承完整主機權限。https://pluto.security/blog/claude-extension-ecosystem-security-practitioner-guide/
- **MCP 攻擊模式**：rug pull / typosquatting / tool poisoning (arXiv 2604.01905)；實際案例 postmark-mcp 在 npm 偷收 email (Snyk 2025-09)
- **Koi Security ClawHavoc**：ClawHub 2,632 個 skills 中 341 個惡意，後續增加到 824 個
- **PromptArmor (2026-01)**：Word 白底白字 1pt 隱形指令，誘導 Claude Cowork 外傳房貸文件與 SSN
