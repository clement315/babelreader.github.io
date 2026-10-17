# 《神學大全》中拉平行閱讀

網站入口為 `summa.html?part=I&q=1&art=1`。書架封面、書名與閱讀按鈕均進入專用 JSON 閱讀器；原有 EPUB 書籍沿用既有入口。

資料涵蓋 I、I_II、II_II、III、SUPPL 五部共611問、3115節，另含補編兩篇附錄共10節。全書前言、部序和補編導覽亦可從目錄開啟。最初匯入時與校對初修HTML逐問相同；2026-10-17另完成中文引號與書名號OCR專項修復，拉丁文及資料結構保留。

## 載入方式

- `data/summa/catalog.json` 提供完整目錄。
- 正文按 `data/summa/${part}/q${q}.json` 載入，一次只請求當前一問，瀏覽器保留最近12問。
- 各次資料請求包含內容版本，避免網站更新後讀到舊的快取。
- `summa.html` 內置已修訂的第一問；直接雙擊開啟或目錄載入失敗時，會明確退回第一問示例。
- 附錄網址使用 `?part=APPENDICES&q=1&art=1`，顯示徽章為 `ST.SUPPL.App1.A1`。

## 校對狀態

這是原PDF校對初修，共202筆修訂，尚未全書逐字校畢。只處理能由原頁確認的OCR錯字、漏行、標點、版面殘留和段落錯置；不潤色、不改寫，不由拉丁文補譯中文。

第一部第71、72問現已分入對應的質疑、反之、正解與釋疑。II_II第170問的相鄰掃描頁，印刷頁碼由473跳至476；現存第二節正解及釋疑已歸回第二節，缺失內容留空並有提示。SUPPL第64問保留先前核定的中拉節號對照。

- [逐項修訂記錄](summa/revisions.txt)
- [待校說明與漏字線索](summa/pending-review.txt)
- [結構化修訂記錄](summa/corrections.json)
- [中文引號與書名號專項修復](summa/punctuation-repairs.md)
- [本次規則及各檔案統計](summa/punctuation-repairs.json)
- [標點待人工複核線索](summa/punctuation-pending.json)

## 更新資料

從已校訂的獨立HTML匯入：

```text
python tools/import_proofread_summa.py /path/to/proofread/summa.html
```

此工具保留所有中拉正文，輸出逐問JSON、目錄、版本及第一問fallback。原始掃描本與OCR頁面快取不需要上傳。

重新匯入舊版初修HTML後，須另執行 `python tools/repair_summa_punctuation.py --write`，套用標點修復並更新快取版本；不加 `--write` 則只檢查，不寫入資料。原有 `import-validation.json` 是初次匯入的歷史記錄，本次修復的統計另存於 `punctuation-repairs.json`。

## 查詞與主題接口

`assets/summa-integrations.js` 保留 `window.SUMMA_LOOKUP`、`summa:word` 及 `summa:render` 事件；沒有載入只適用於EPUB的閱讀腳本。深色模式沿用 `babel-reading-theme`。

## 檢查

`docs/summa/import-validation.json` 記錄與修訂HTML逐問比對的結果。瀏覽器檢查涵蓋逐問載入、所有613個閱讀單元、全部雙語列、書架入口、附錄、校對提示、手機及離線fallback。
