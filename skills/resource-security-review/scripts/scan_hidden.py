#!/usr/bin/env python3
"""掃描「人眼看不到、AI 讀得到」的隱藏內容。

用法：python3 scan_hidden.py <路徑> [<路徑> ...]
只讀檔案，不執行任何內容；不開啟符號連結與特殊檔案。輸出裡的隱形與控制字元一律改寫成 [U+XXXX]。
"""
import os
import re
import stat
import sys
import unicodedata

TAGS = range(0xE0000, 0xE0080)
BIDI = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A)) | {0x061C, 0x200E, 0x200F}
VARIATION_SELECTORS = set(range(0xFE00, 0xFE10)) | set(range(0xE0100, 0xE01F0))
INVISIBLE_EXTRA = {0x034F, 0x115F, 0x1160, 0x3164, 0xFFA0}  # CGJ、Hangul filler：不是 Cf 但一樣看不到
HTML_COMMENT = re.compile(r"<!--(.*?)(?:-->|\Z)", re.S)
MAX_HITS_PER_FILE = 20
MAX_COMMENTS_PER_FILE = 10


def kind(c):
    """隱形字元的類別，一般字元回傳 None。variation selector 另外在 line_hits 判斷。"""
    o = ord(c)
    if o in TAGS:
        return "Unicode tag 字元"
    if o in BIDI:
        return "bidi 控制字元"
    if o in INVISIBLE_EXTRA or unicodedata.category(c) == "Cf":
        return "零寬 / 隱形字元"
    return None


def safe(text):
    """把隱形與控制字元改寫成 [U+XXXX]，避免輸出本身夾帶隱藏內容或偽造的行。"""
    return "".join(
        c if c.isprintable() and not kind(c) and ord(c) not in VARIATION_SELECTORS
        else f"[U+{ord(c):04X}]"
        for c in text
    )


def decode_hidden(name, chars):
    """把 tag 字元 / variation selector (emoji smuggling) 藏的內容解碼出來。"""
    if name == "Unicode tag 字元":
        return "".join(chr(ord(c) - 0xE0000) for c in chars if 0xE0020 <= ord(c) <= 0xE007E)
    data = bytes(ord(c) - 0xFE00 if ord(c) < 0xE0100 else ord(c) - 0xE0100 + 16 for c in chars)
    return data.decode("utf-8", errors="replace")


def vs_ok(prev, c):
    """emoji / keycap 後面單獨一個 U+FE0E / U+FE0F 是正常寫法；其他 variation selector 一律算命中。"""
    return ord(c) in (0xFE0E, 0xFE0F) and (unicodedata.category(prev) == "So" or prev in "0123456789#*")


def zwj_ok(prev, nxt):
    """emoji 組合序列 (例：家庭 emoji) 中間的 U+200D 是正常寫法。"""
    return (unicodedata.category(prev) in ("So", "Sk") or ord(prev) == 0xFE0F) and unicodedata.category(nxt) == "So"


def line_hits(line):
    """回傳 {類別: [字元]}。"""
    found = {}
    for i, c in enumerate(line):
        prev = line[i - 1] if i else ""
        nxt = line[i + 1] if i + 1 < len(line) else ""
        if ord(c) in VARIATION_SELECTORS:
            if not (prev and vs_ok(prev, c)):
                found.setdefault("variation selector", []).append(c)
            continue
        if ord(c) == 0x200D and prev and nxt and zwj_ok(prev, nxt):
            continue
        k = kind(c)
        if k:
            found.setdefault(k, []).append(c)
    return found


def error_line(path, e):
    return f"{safe(path)}: [無法讀取] {safe(e.strerror or str(e))}"


def line_list(numbers):
    return ", ".join(map(str, numbers[:30])) + (" …" if len(numbers) > 30 else "")


def scan_file(path, char_hits, comment_hits):
    shown = safe(path)
    try:
        mode = os.lstat(path).st_mode
        if stat.S_ISLNK(mode):
            char_hits.append(f"{shown}: [符號連結] 指向 {safe(os.readlink(path))}，未開啟")
            return
        if not stat.S_ISREG(mode):
            char_hits.append(f"{shown}: [特殊檔案] 不是一般檔案 (FIFO、裝置等)，未開啟")
            return
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        char_hits.append(error_line(path, e))
        return

    if b"\0" in data:
        char_hits.append(f"{shown}: [含 NUL 位元組] 可能是二進位檔，仍照常掃描")
    text = data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")

    zero_width_lines = []
    for lineno, line in enumerate(text.split("\n"), 1):
        if line.isascii():
            continue  # 隱形字元都不是 ASCII
        for name, chars in line_hits(line).items():
            # 零寬類有正常用途 (BOM、印度文字的 ZWJ)，每檔只列前幾筆；tag、variation selector、bidi 一律全列
            if name == "零寬 / 隱形字元":
                zero_width_lines.append(lineno)
                if len(zero_width_lines) > MAX_HITS_PER_FILE:
                    continue
            codes = sorted({f"U+{ord(c):04X}" for c in chars})
            hit = f"{shown}:{lineno}: [{name}] {' '.join(codes[:10])}{' …' if len(codes) > 10 else ''} (共 {len(chars)} 個)"
            if name in ("Unicode tag 字元", "variation selector"):
                hit += f"，解碼後：「{safe(decode_hidden(name, chars))}」"
            char_hits.append(hit)
    rest = zero_width_lines[MAX_HITS_PER_FILE:]
    if rest:
        char_hits.append(f"{shown}: [零寬 / 隱形字元] 另有 {len(rest)} 行未列出，行號 {line_list(rest)}，請回原檔逐行確認")

    lineno, last = 1, 0
    rest = []
    for i, m in enumerate(HTML_COMMENT.finditer(text)):
        lineno += text.count("\n", last, m.start())
        last = m.start()
        if i >= MAX_COMMENTS_PER_FILE:
            rest.append(lineno)
            continue
        body = " ".join(m.group(1).split())
        more = f" …(共 {len(body)} 字，請回原檔看完)" if len(body) > 200 else ""
        comment_hits.append(f"{shown}:{lineno}: [HTML 註解] {safe(body[:200])}{more}")
    if rest:
        comment_hits.append(f"{shown}: [HTML 註解] 另有 {len(rest)} 個未列出，行號 {line_list(rest)}，請回原檔逐一確認")


def main(paths):
    # 字元類命中先印、HTML 註解後印，避免大量無害註解把真正的命中擠到後面
    char_hits, comment_hits = [], []
    for root in paths:
        root = os.path.normpath(root)  # 去掉結尾的 / 與 /.，避免跟進指向外部的符號連結
        if os.path.islink(root) or not os.path.isdir(root):
            scan_file(root, char_hits, comment_hits)
            continue
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: char_hits.append(error_line(e.filename or root, e))):
            git_dir = os.path.join(dirpath, ".git")
            if ".git" in dirnames and not os.path.islink(git_dir):
                dirnames.remove(".git")
                char_hits.append(f"{safe(git_dir)}: [略過] git 資料夾，未掃描 (不是 git clone 產生的就要另外檢查)")
            dirnames.sort()
            # os.walk 不進入指向資料夾的符號連結，但仍要列出來
            links = [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]
            for name in sorted(filenames + links):
                scan_file(os.path.join(dirpath, name), char_hits, comment_hits)
    hits = char_hits + comment_hits
    print("\n".join(hits) if hits else "未發現隱藏字元、HTML 註解、符號連結、特殊檔案或 NUL 位元組")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
