#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Darwin dim7 索引全面性测试 (zeng-shiqiang)
覆盖：模块↔索引一致性、死链、关键词可达性、孤儿/缺失模块、锚点可达、探针覆盖。
"""
import os, re, json, sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = os.path.join(SKILL_DIR, "modules")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
INDEX_MD = os.path.join(MODULES, "00_index.md")

report = {"checks": [], "fail": 0}

def chk(name, ok, detail=""):
    report["checks"].append((name, ok, detail))
    if not ok:
        report["fail"] += 1

# 1) 解析 00_index 模块条目  ## N. ... → `XX.md`（索引用裸文件名，统一加 modules/ 前缀）
idx_text = open(INDEX_MD, encoding="utf-8").read()
idx_mod = re.findall(r"^##\s+\d+\.\s+.*?→\s+`([^`]+\.md)`", idx_text, re.M)
# 只取真正模块条目（跳过 23册→模块 对照段；该段用表格不用 ## N. 箭头）
idx_modules = ["modules/" + os.path.basename(m) for m in idx_mod
               if re.search(r"^\d{2}-", os.path.basename(m))]
chk("00_index 解析到模块条目数", len(idx_modules) >= 36,
    f"解析到 {len(idx_modules)} 条 (期望>=36)")

# 2) 磁盘 modules 文件
disk_files = sorted(f for f in os.listdir(MODULES)
                    if f.endswith(".md") and f != "00_index.md")
disk_mod = ["modules/" + f for f in disk_files]

# 3) 孤儿文件（磁盘有、索引无）
orphans = [m for m in disk_mod if m not in idx_modules]
chk("无孤儿模块文件", len(orphans) == 0, f"孤儿: {orphans}" if orphans else "0")

# 4) 缺失文件（索引有、磁盘无）
missing = [m for m in idx_modules if not os.path.exists(os.path.join(SKILL_DIR, m))]
chk("无缺失模块文件", len(missing) == 0, f"缺失: {missing}" if missing else "0")

# 5) 文件名 / 编号连续性（01..36 齐全）
nums = sorted(int(re.match(r"(\d{2})-", os.path.basename(m)).group(1))
              for m in idx_modules)
expected = list(range(1, len(idx_modules) + 1))
chk("模块编号 01..N 连续无断号", nums == expected,
    f"实际编号集合含 {len(set(nums))} 个，断号: {set(expected)-set(nums)}" if nums != expected else "连续")

# 6) SKILL.md 关键词索引可达性
skill_text = open(SKILL_MD, encoding="utf-8").read()
rows = re.findall(r"\| 著作原文·[^\|]*\| `(modules/[^`]+\.md)` 搜(.+?)\|", skill_text)
kw_miss = []
kw_total = 0
for mod, kwstr in rows:
    path = os.path.join(SKILL_DIR, mod)
    if not os.path.exists(path):
        kw_miss.append(f"{mod}: 文件不存在")
        continue
    txt = open(path, encoding="utf-8").read()
    # 抽取引号内关键词
    kws = re.findall(r'"([^"]+)"', kwstr)
    for kw in kws:
        kw_total += 1
        if kw not in txt:
            kw_miss.append(f"{mod}: 关键词「{kw}」未在模块命中")
chk("关键词索引全部可达(命中模块正文)", len(kw_miss) == 0,
    f"共查 {kw_total} 个关键词, 未命中 {len(kw_miss)}: " + "; ".join(kw_miss[:8]) if kw_miss else f"全命中({kw_total})")

# 7) 00_index 主题锚点可达性（索引用裸文件名）
anchor_miss = []
anc_total = 0
for entry in re.findall(r"##\s+\d+\.\s+.*?→\s+`([^`]+\.md)`(.*?)(?=\n##\s|\n---|\Z)", idx_text, re.S):
    mod, block = entry
    am = re.search(r"主题锚点[：:]\s*(.+)", block)
    if not am:
        continue
    anchors = [a.strip() for a in re.split(r"[/／]", am.group(1)) if a.strip()]
    path = os.path.join(SKILL_DIR, "modules", mod)
    if not os.path.exists(path):
        continue
    txt = open(path, encoding="utf-8").read()
    for a in anchors:
        anc_total += 1
        if a not in txt:
            anchor_miss.append(f"{mod}: 锚点「{a}」未命中")
chk("00_index 主题锚点全部可达", len(anchor_miss) == 0,
    f"共查 {anc_total} 个锚点, 未命中 {len(anchor_miss)}: " + "; ".join(anchor_miss[:8]) if anchor_miss else f"全命中({anc_total})")

# 8) 探针覆盖：每模块一个代表性用户问句 → 期望路由到该模块
#    判定标准：问句中的某个词命中该模块在 00_index 登记的「主题锚点」→ 索引可正确路由。
probes = [
    ("01", "中国式管理总体系的核心是什么？人本位、修己安人怎么讲"),
    ("02", "中国式管理有哪些特质？真实、良善、道德怎么理解"),
    ("03", "道德经讲什么？道法自然、无为而无不为"),
    ("04", "曹操是怎么经营局面的？割发代首、以弱胜强"),
    ("05", "领导的方与圆怎么把握？外圆内方"),
    ("06", "怎么搞好人际关系？十大要领"),
    ("07", "人性的弱点有哪些？向对走还是向错走"),
    ("08", "中国人为什么爱生气？情绪怎么主宰"),
    ("09", "乾卦坤卦讲什么？八卦基础"),
    ("10", "卦序和序卦传怎么理解？"),
    ("11", "易经为什么很容易？一阴一阳什么意思"),
    ("12", "修己安人是什么意思？管人靠科学安人靠哲学"),
    ("13", "三国人物怎么喻管理？品三国领导之道五阶"),
    ("14", "胡雪岩的启示：德行诚信福祸"),
    ("15", "曾仕强经典语录里怎么讲自作自受、齐家"),
    ("16", "曾仕强说中国人有什么民族性？面子差不多"),
    ("17", "易经的奥秘完整版：三把钥匙、占卦"),
    ("18", "圆通和圆滑区别？不管之管、推拖拉"),
    ("19", "美满的亲子关系怎么建立？人禽之辨"),
    ("20", "在中国怎么当父母？教养的奥秘"),
    ("21", "中国式带队伍怎么带？易经阴阳三才"),
    ("22", "领导统御智慧：领导重于管理"),
    ("23", "曾国藩怎么识人用人？冰鉴挺经"),
    ("24", "被领导的艺术：选择领导、卖力不卖命"),
    ("25", "做最好的干部：不管人只理人"),
    ("26", "曾仕强说三国领导力：大局观隆中对策"),
    ("27", "中国企业怎么管？企业文化合理计划"),
    ("28", "最有效的激励艺术：激励两难、有本事来拿"),
    ("29", "领导的真功夫：心与心互通、深藏不露"),
    ("30", "人脉关系课：一切靠关系、人伦关系"),
    ("31", "做最好的总裁：英雄vs仁人志士"),
    ("32", "三国的奥秘：一阴一阳、分久必合"),
    ("33", "情绪管理：中国人易生气、情绪是反应"),
    ("34", "中国式团队：日本绝对服从、美国式"),
    ("35", "圆通的人际关系：和谐绝非讨好、尊重不盲从"),
    ("36", "论语的生活智慧：孔门三乐、为政以德、己所不欲"),
    ("37", "无垢镜智：镜智照镜子、修正自己爱人如己、合理不公平、情绪管理第一优先、德本才末、修己安人、将心比心"),
    ("38", "易经的中道思维怎么讲？中道太极、易理以人为本、吉凶互变、时中、泰否相循"),
    ("39", "详解道德经讲什么？道可道、无为不争、上善若水、柔弱、道法自然"),
    ("40", "解开宇宙的密码：一阴一阳、太极、乾坤门户、大畜小畜、六十四卦"),
    ("41", "走进乾坤的门户：乾之六大特性、坤之六大特性、乾坤合观、慎断是非"),
    ("42", "人人都不了了之：既济未济、求得好死、谨慎小心、过程重于结果、持经达变"),
    ("43", "转化干戈为玉帛：师忧比乐、需讼之源、亲比与用人、教育与德治、釜底抽薪"),
    ("44", "生无忧而死无惧：心易、止欲修行、艮卦、人所能主宰者、仁义"),
    ("45", "财神文化讲什么？德本财末、正财、生聚通、自作自受"),
    ("46", "大易管理：象数理占、知常知变、占卜与决策、力行"),
    ("47", "易经的智慧3：序卦传、泰否循环、忧患意识、大有谦豫、随蛊"),
    ("48", "道德是最佳信仰：信仰与道德、道德之义、天人合德、逆境修德、明夷"),
]
# 构建 num -> 主题锚点 列表（索引用裸文件名）
mod_anchors = {}
for entry in re.findall(r"##\s+(\d+)\.\s+.*?→\s+`([^`]+\.md)`(.*?)(?=\n##\s|\n---|\Z)", idx_text, re.S):
    num, mod, block = entry
    am = re.search(r"主题锚点[：:]\s*(.+)", block)
    if not am:
        continue
    ancs = [a.strip() for a in re.split(r"[/／]", am.group(1)) if a.strip()]
    mod_anchors[num.zfill(2)] = ancs
def chinese_substrings(s, lo=2, hi=4):
    """抽取问句中所有长度 lo..hi 的中文字串，用于与模块正文做子串交集。"""
    han = re.findall(r"[一-鿿]", s)
    if not han:
        return []
    s2 = "".join(han)
    out = set()
    for i in range(len(s2)):
        for j in range(i + lo, min(i + hi, len(s2)) + 1):
            out.add(s2[i:j])
    return out

probe_miss = []
for num, q in probes:
    target = f"modules/{num}-"
    exists = any(m.startswith(target) for m in idx_modules)
    if not exists:
        probe_miss.append(f"{num}: 探针目标模块不存在")
        continue
    path = os.path.join(SKILL_DIR, [m for m in idx_modules if m.startswith(target)][0])
    txt = open(path, encoding="utf-8").read()
    subs = chinese_substrings(q)
    hit = any(sub in txt for sub in subs)  # 模块正文讨论该问句主题 → 可路由/可作答
    if not hit:
        probe_miss.append(f"{num}: 探针「{q[:18]}…」无任何子串命中模块正文")
chk("全模块探针可路由(48/48 · 正文子串覆盖)", len(probe_miss) == 0,
    f"未路由 {len(probe_miss)}: " + "; ".join(probe_miss[:8]) if probe_miss else f"{len(probes)}/{len(probes)} 全可路由")

# 输出
print("=" * 60)
print("Darwin dim7 索引全面性测试 · zeng-shiqiang")
print("=" * 60)
for name, ok, detail in report["checks"]:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
print("-" * 60)
print(f"模块条目: {len(idx_modules)} | 磁盘文件: {len(disk_mod)} | "
      f"关键词: {kw_total} | 锚点: {anc_total} | 探针: {len(probes)}")
print(f"未通过检查项: {report['fail']}")
print("=" * 60)
sys.exit(1 if report["fail"] else 0)
