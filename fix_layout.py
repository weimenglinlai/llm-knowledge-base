# -*- coding: utf-8 -*-
"""报告排版最终修正：

1. 删除模板自带的「填写说明」图片（红箭头示意图）与高亮的说明性文字
   —— 这些是给学生看的填写指引，不应出现在提交的正式报告里
2. 表格宽度撑满版心（说明图要求「表格上下边框要与页面上下边沿对齐」）
3. 允许长行跨页断开
4. 单元格内图片按版心宽度自适应
"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import docx
from docx.shared import Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"project/学习//Ai前沿技术/项目4"
DOC = os.path.join(BASE, "++任务4.docx")
NS = '{http://schemas.openxmlformats.org/drawingml/2006/main}'

# 需要删除的模板说明性文字（以这些开头）
GUIDE_PREFIXES = (
    "【说明】",
    "【内容要求】",
    "【文字格式要求】",
    "【注意】",
    "【报告格式要求】",
    "字体:中文：黑色、小四、宋体",
    "行距：单倍行距；",
    "间距：段前段后0行。",
    "代码显示能够清晰明了",
)


def usable_width_cm(doc):
    s = doc.sections[0]
    return s.page_width.cm - s.left_margin.cm - s.right_margin.cm


def is_guide(text):
    t = text.strip()
    return any(t.startswith(p) for p in GUIDE_PREFIXES)


def squeeze_label_spaces(cell):
    """把「时    间」这类标签的连续空格压成2个，避免被挤成两行"""
    import re
    for p in cell.paragraphs:
        if re.match(r'^[一-龥]{2}\s+[一-龥]{2}$', p.text.strip()):
            for r in p.runs:
                if '  ' in r.text:
                    r.text = re.sub(r'\s{2,}', '  ', r.text)


def trim_trailing_blanks(cell, keep=1):
    """删掉单元格末尾连续的空段落（模板留白会把整页撑开）"""
    paras = list(cell.paragraphs)
    blanks = []
    for p in reversed(paras):
        if p.text.strip() == "" and not p._element.findall('.//' + NS + 'blip'):
            blanks.append(p)
        else:
            break
    for p in blanks[keep:]:
        p._element.getparent().remove(p._element)


def strip_highlight(p):
    """去掉高亮底色（w:highlight）与彩色文字，还原为黑色"""
    for r in p.runs:
        rPr = r._element.find(qn('w:rPr'))
        if rPr is None:
            continue
        for tag in ('w:highlight', 'w:shd'):
            el = rPr.find(qn(tag))
            if el is not None:
                rPr.remove(el)
        color = rPr.find(qn('w:color'))
        if color is not None:
            color.set(qn('w:val'), '000000')


def delete_paragraph(p):
    p._element.getparent().remove(p._element)


def remove_guide_images(cell):
    """删除没有图题的孤立说明图（正文图后面都跟着「图x.x ...」图题段）"""
    removed = 0
    paras = list(cell.paragraphs)
    for i, para in enumerate(paras):
        blips = para._element.findall('.//' + NS + 'blip')
        if not blips:
            continue
        # 往后找最近的非空文字段：如果是图题则保留，否则视为说明图删除
        nxt = ""
        for j in range(i + 1, min(i + 3, len(paras))):
            txt = paras[j].text.strip()
            if txt:
                nxt = txt
                break
        if nxt.startswith("图"):
            continue
        para._element.getparent().remove(para._element)
        removed += len(blips)
    return removed


def set_table_full_width(doc, table):
    """让表格左右边框与页面版心对齐。

    原表总宽 16.28cm 大于版心 14.65cm（模板本意是略微超出版心，
    使边框与页面上下的正文区对齐）。这里保留各列的原始比例，
    整体按比例缩放到版心宽度，并把短列保底宽度补足，
    避免「时间」「」等短标签被挤成竖排。
    """
    uw = usable_width_cm(doc)
    grid = table._tbl.find(qn('w:tblGrid'))
    if grid is None:
        return
    cols = grid.findall(qn('w:gridCol'))
    widths = [int(c.get(qn('w:w'))) for c in cols]
    total = sum(widths)
    if total <= 0:
        return

    # 短列保底：2.35cm 起步（“时 间”“学 号”各需约2.4cm 才不换行）
    MIN_CM = 2.30
    min_tw = int(MIN_CM * 567)
    scaled = [max(int(w * uw * 567 / total), min_tw) for w in widths]
    # 超出的部分从最宽的列扣回
    over = sum(scaled) - int(uw * 567)
    if over > 0:
        widest = scaled.index(max(scaled))
        scaled[widest] -= over
    # 首行第二格（地点内容）单独放宽
    scaled[1] = max(scaled[1], int(3.30 * 567))
    over = sum(scaled) - int(uw * 567)
    if over > 0:
        widest = scaled.index(max(scaled))
        scaled[widest] -= over
    target = int(uw * 567)
    scaled[-1] += target - sum(scaled)

    for c, w in zip(cols, scaled):
        c.set(qn('w:w'), str(w))

    tblPr = table._tbl.tblPr
    tblW = tblPr.find(qn('w:tblW'))
    if tblW is None:
        tblW = OxmlElement('w:tblW'); tblPr.append(tblW)
    tblW.set(qn('w:w'), str(target))
    tblW.set(qn('w:type'), 'dxa')

    jc = tblPr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc'); tblPr.append(jc)
    jc.set(qn('w:val'), 'left')

    ind = tblPr.find(qn('w:tblInd'))
    if ind is None:
        ind = OxmlElement('w:tblInd'); tblPr.append(ind)
    ind.set(qn('w:w'), '0')
    ind.set(qn('w:type'), 'dxa')

    # 每个单元格的 tcW 按新列宽设置
    for row in table.rows:
        seen = set()
        col_idx = 0
        for cell in row.cells:
            if id(cell._tc) in seen:
                continue
            seen.add(id(cell._tc))
            # 该 cell 跨越的列数 = gridSpan
            tcPr = cell._tc.tcPr
            gs = tcPr.find(qn('w:gridSpan'))
            span = int(gs.get(qn('w:val'))) if gs is not None else 1
            w = sum(scaled[col_idx:col_idx + span])
            tcW = tcPr.find(qn('w:tcW'))
            if tcW is None:
                tcW = OxmlElement('w:tcW'); tcPr.append(tcW)
            tcW.set(qn('w:w'), str(w))
            tcW.set(qn('w:type'), 'dxa')
            col_idx += span


def allow_row_split(table):
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        el = trPr.find(qn('w:cantSplit'))
        if el is not None:
            trPr.remove(el)


def scale_images(cell, max_w_cm):
    for ext in cell._tc.findall('.//' + NS + 'ext'):
        cx = ext.get('cx')
        if not cx:
            continue
        cur = int(cx) / 360000.0
        if cur > max_w_cm:
            ratio = max_w_cm / cur
            ext.set('cx', str(int(int(cx) * ratio)))
            ext.set('cy', str(int(int(ext.get('cy')) * ratio)))


def main():
    doc = docx.Document(DOC)
    t = doc.tables[0]
    uw = usable_width_cm(doc)
    print("版心宽: %.2f cm" % uw)

    # 1) 删除模板说明性文字与说明图
    for row in t.rows:
        cell = row.cells[0]
        # 先删说明图（第四节末尾的那张红箭头图）
        n = remove_guide_images(cell)
        if n:
            print("  删除说明图 x%d" % n)
        # 再删说明性文字段
        for p in list(cell.paragraphs):
            if is_guide(p.text):
                delete_paragraph(p)
        squeeze_label_spaces(cell)
        trim_trailing_blanks(cell)

    # 2) 表格满宽
    set_table_full_width(doc, t)
    allow_row_split(t)

    # 3) 图片自适应
    for row in t.rows:
        for cell in row.cells:
            scale_images(cell, uw - 1.6)

    # 4) 去掉剩余高亮
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                strip_highlight(p)

    doc.save(DOC)
    print("saved")


if __name__ == "__main__":
    main()
