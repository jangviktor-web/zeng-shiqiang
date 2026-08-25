#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_keyword_refs.py — 曾仕强 skill 注册前引用自检。

职责（对应 SKILL.md 第十三章「注册前跑 scripts/validate_keyword_refs.py 验证 0 失效」）：
  扫描 SKILL.md 与 modules/00_index.md 中出现的 `modules/XX-name.md` 引用，
  逐一校验文件是否真实存在。全部命中则退出码 0（0 失效），否则退出码 1 并打印缺失清单。

用法：
  python scripts/validate_keyword_refs.py            # 自动定位 skill 根目录
  python scripts/validate_keyword_refs.py /path/to/zeng-shiqiang   # 指定根目录

合规：只读检查，不修改任何文件。
"""
import re
import sys
from pathlib import Path

# 脚本在 <skill>/scripts/ 下，skill 根目录 = 父目录的父目录
DEFAULT_SKILL_DIR = Path(__file__).resolve().parent.parent

# 形如 `modules/01-zhong-guo-shi-guan-li-quan-ji.md`
REF_PATTERN = re.compile(r"`?(modules/[0-9]{2}-[a-z0-9-]+\.md)`?")


def collect_refs(text: str) -> list[str]:
    return REF_PATTERN.findall(text)


def main() -> int:
    skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SKILL_DIR
    skill_dir = skill_dir.resolve()
    if not skill_dir.is_dir():
        print(f"[ERROR] skill 目录不存在: {skill_dir}")
        return 1

    targets = [skill_dir / "SKILL.md", skill_dir / "modules" / "00_index.md"]
    missing: list[str] = []
    checked = 0

    for tgt in targets:
        if not tgt.is_file():
            print(f"[WARN] 跳过不存在的索引文件: {tgt}")
            continue
        text = tgt.read_text(encoding="utf-8")
        for ref in collect_refs(text):
            checked += 1
            ref_path = skill_dir / ref
            if not ref_path.is_file():
                missing.append(f"{tgt.name} -> {ref}")

    print(f"检查引用总数: {checked}")
    if missing:
        print(f"[FAIL] 失效引用 {len(missing)} 条:")
        for m in missing:
            print(f"  - {m}")
        return 1

    print("[OK] 0 失效 — 所有 modules/*.md 引用均存在。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
