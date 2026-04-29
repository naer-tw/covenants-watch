"""共用 markdown frontmatter 工具(Wave 36 抽出)

提供:
- YAML_RE                          — 抓 frontmatter 的 regex
- parse_yaml(text) -> dict          — 解析 YAML(優先 pyyaml,fallback 自製)
- split_frontmatter(text) -> (dict, body) — 拆出 frontmatter 與 body
- load_md(path) -> (dict, body)     — 讀檔 + 拆 frontmatter

設計原則:
- Issue #8 修法:優先用 pyyaml.safe_load(穩固),fallback 純 stdlib parser(可能 fail edge case)
- 不修改 Markdown,只讀
- 純函式,無副作用
"""
from __future__ import annotations

import re
from pathlib import Path

YAML_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


# Issue #8 修法:優先用 pyyaml(支援多行 list、引號、特殊字元),fallback 自製 parser
# QA #5 修法:fallback 加 block-style list 支援 + 環境警示
import sys


def _fallback_parse_yaml(text: str) -> dict:
    """fallback 自製 YAML parser(支援 inline + block-style list)。

    支援格式:
      key: value           # 純值
      key: [a, b, c]       # inline list
      key: true / false    # 布林
      key:                 # block-style list 起始
        - item1
        - item2
    """
    out: dict = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line or line.startswith("#"):
            i += 1
            continue
        # block-style list item — 應該被前面的 key 處理掉,這裡略過
        if line.lstrip().startswith("- "):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val == "":
            # 可能是 block-style list:看下一行是否為「  - xxx」
            block_items = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                stripped = nxt.lstrip()
                if stripped.startswith("- "):
                    block_items.append(stripped[2:].strip())
                    j += 1
                elif nxt.strip() == "":
                    j += 1
                    continue
                else:
                    break
            if block_items:
                out[key] = block_items
                i = j
                continue
            out[key] = ""
            i += 1
            continue
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        elif val.lower() in ("true", "false"):
            val = val.lower() == "true"
        out[key] = val
        i += 1
    return out


try:
    import yaml as _yaml

    def parse_yaml(text: str) -> dict:
        """解析 YAML frontmatter。優先用 pyyaml.safe_load。"""
        return _yaml.safe_load(text) or {}

    HAS_PYYAML = True
except ImportError:
    HAS_PYYAML = False
    _warned_no_pyyaml = False

    def parse_yaml(text: str) -> dict:
        """fallback 自製 YAML parser(支援 inline + block-style list)。

        QA #5 修法:加 block-style list 支援 + 環境警示。
        若需 100% YAML spec 相容,請 .venv/bin/pip install pyyaml。
        """
        global _warned_no_pyyaml
        if not _warned_no_pyyaml:
            print(
                "⚠ _md_frontmatter:pyyaml 未安裝,使用 fallback parser。"
                "block-style list 已支援,但複雜 YAML(引號跳脫、巢狀)可能失敗。"
                "建議:.venv/bin/pip install pyyaml",
                file=sys.stderr,
            )
            _warned_no_pyyaml = True
        return _fallback_parse_yaml(text)


def split_frontmatter(text: str) -> tuple[dict, str]:
    """拆 frontmatter 與 body。若無 frontmatter,回 ({}, text)。"""
    m = YAML_RE.match(text)
    if not m:
        return {}, text
    return parse_yaml(m.group(1)), text[m.end():]


def load_md(path: Path) -> tuple[dict, str]:
    """讀檔 + 拆 frontmatter(便利包裝)。"""
    return split_frontmatter(path.read_text(encoding="utf-8"))
