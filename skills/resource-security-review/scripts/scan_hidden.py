#!/usr/bin/env python3
"""掃描「人眼看不到、AI 讀得到」的隱藏內容。

用法：python3 scan_hidden.py <路徑> [<路徑> ...]
只讀檔案，不執行任何內容；不跟隨符號連結。輸出裡的隱形字元一律改寫成 [U+XXXX]。
"""
import os
import re
import sys

CATEGORIES = [
    ("零寬 / 隱形字元", re.compile("[\u00ad\u200b-\u200f\u2060-\u2064\ufeff]")),
    ("bidi 控制字元", re.compile("[\u202a-\u202e\u2066-\u2069]")),
    ("Unicode tag 字元", re.compile("[\U000e0000-\U000e007f]")),
]
HTML_COMMENT = re.compile(r"<!--(.*?)(?:-->|\Z)", re.S)
SKIP_DIRS = {".git"}


def visible(text):
    """把隱形字元改寫成 [U+XXXX]，方便引用進報告。"""
    return "".join(
        f"[U+{ord(c):04X}]" if any(p.match(c) for _, p in CATEGORIES) else c
        for c in text
    )


def scan_file(path):
    if os.path.islink(path):
        return [f"{path}: [符號連結] 指向 {os.readlink(path)}，略過"]
    with open(path, "rb") as f:
        data = f.read()
    if b"\0" in data[:8192]:
        return [f"{path}: [二進位檔] 略過，需另外確認用途"]
    text = data.decode("utf-8", errors="replace")
    hits = []
    for lineno, line in enumerate(text.split("\n"), 1):
        for name, pattern in CATEGORIES:
            found = pattern.findall(line)
            if not found:
                continue
            codes = " ".join(sorted({f"U+{ord(c):04X}" for c in found}))
            hit = f"{path}:{lineno}: [{name}] {codes} (共 {len(found)} 個)"
            if pattern is CATEGORIES[2][1]:
                decoded = "".join(chr(ord(c) - 0xE0000) for c in found if 0xE0020 <= ord(c) <= 0xE007E)
                hit += f"，解碼後：{decoded!r}"
            hits.append(hit)
    for m in HTML_COMMENT.finditer(text):
        lineno = text.count("\n", 0, m.start()) + 1
        body = visible(" ".join(m.group(1).split()))
        hits.append(f"{path}:{lineno}: [HTML 註解] {body[:200]}")
    return hits


def main(paths):
    hits = []
    for root in paths:
        if not os.path.isdir(root) or os.path.islink(root):
            hits += scan_file(root)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            # os.walk 不進入指向資料夾的符號連結，但仍要列出來
            links = [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]
            for name in sorted(filenames + links):
                hits += scan_file(os.path.join(dirpath, name))
    print("\n".join(hits) if hits else "未發現隱藏字元、HTML 註解、符號連結或二進位檔")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
