# -*- coding: utf-8 -*-
"""填充《任务4》报告的第四、五、六节。

第四节：操作方法与步骤（正文 + 截图）
第五节：实践结果与分析
第六节：实践体会

图片按页宽等比缩放后插入到指定单元格内。
"""
import sys, io, os, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import docx
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"project/学习//Ai前沿技术/项目4"
DOC = os.path.join(BASE, "++任务4.docx")
SHOTS = os.path.join(BASE, "screenshots")

SONG, TIMES = "宋体", "Times New Roman"
BODY_PT = 12.0          # 小四
CAP_PT = 10.5           # 五号


def set_font(run, size=BODY_PT, bold=False, color=(0, 0, 0), font=SONG):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rPr.insert(0, rf)
    rf.set(qn('w:ascii'), font)
    rf.set(qn('w:hAnsi'), font)
    rf.set(qn('w:eastAsia'), SONG)


def fmt_para(p, size=BODY_PT, align=None, indent_chars=0, space_before=0, space_after=0):
    pf = p.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align
    if indent_chars:
        pf.first_line_indent = Pt(size * indent_chars)
    # 中文段落禁止自动缩进影响：显式设置
    pPr = p._element.get_or_add_pPr()
    for tag in ('w:snapToGrid',):
        pass
    return p


def new_para_after(anchor_p, text="", size=BODY_PT, bold=False, align=None,
                   indent_chars=0, font=SONG):
    """在 anchor_p 之后插入一个新段落（沿用 anchor 的 pPr 基础格式）"""
    new_p = copy.deepcopy(anchor_p._element)
    # 清空所有 run
    for r in new_p.findall(qn('w:r')):
        new_p.remove(r)
    anchor_p._element.addnext(new_p)
    from docx.text.paragraph import Paragraph
    para = Paragraph(new_p, anchor_p._parent)
    fmt_para(para, size=size, align=align, indent_chars=indent_chars)
    if text:
        run = para.add_run(text)
        set_font(run, size=size, bold=bold, font=font)
    return para


def add_pic_after(anchor_p, img_path, caption=None, max_w_cm=13.6):
    """在 anchor_p 之后插入图片（可选图题），返回最后的锚点段落"""
    from docx.text.paragraph import Paragraph
    if not os.path.exists(img_path):
        print("  缺失图片，跳过:", img_path)
        return anchor_p
    # 图片段
    pic_p = new_para_after(anchor_p, "", align=WD_ALIGN_PARAGRAPH.CENTER)
    run = pic_p.add_run()
    run.add_picture(img_path, width=Cm(max_w_cm))
    anchor = pic_p
    if caption:
        cap_p = new_para_after(anchor, caption, size=CAP_PT,
                               align=WD_ALIGN_PARAGRAPH.CENTER)
        set_font(cap_p.runs[0], size=CAP_PT)
        anchor = cap_p
    return anchor


def set_row_height(row, cm):
    trPr = row._tr.get_or_add_trPr()
    h = trPr.find(qn('w:trHeight'))
    if h is None:
        h = OxmlElement('w:trHeight'); trPr.append(h)
    h.set(qn('w:val'), str(int(cm * 567)))
    h.set(qn('w:hRule'), 'atLeast')


def main():
    doc = docx.Document(DOC)
    t = doc.tables[0]

    # ───────────────────────── 第四节 ─────────────────────────
    cell = t.rows[5].cells[0]
    ps = cell.paragraphs

    # (一) Ollama 部分：插在段落 4 之后
    anchor = ps[4]
    steps_a = [
        ("步骤1：安装并配置 Ollama。本机为64位Windows系统，下载 Ollama 安装包后完成安装，"
         "在系统环境变量中设置 OLLAMA_MODELS 指向 D:\\JZDSKit\\ollama_models 用于集中存放模型文件。"
         "安装完成后在命令行执行 ollama serve 启动服务，默认监听 127.0.0.1:11434。"),
        ("步骤2：下载所需模型。使用 ollama pull 命令拉取两个模型：对话模型 qwen3:8b（约5.2GB）"
         "和词嵌入模型 nomic-embed-text（约274MB），分别用于生成回答和文档向量化。"),
        ("步骤3：安装并启动 AnythingLLM Desktop v1.19.0。在「设置－大语言模型」中选择 Ollama 提供商，"
         "Base URL 填 http://127.0.0.1:11434，模型选择 qwen3:8b；在「设置－嵌入器」中同样选择 Ollama 提供商，"
         "模型选择 nomic-embed-text:latest；「设置－向量数据库」选择 LanceDB。"),
        ("步骤4：构建知识库。新建工作区并命名为“AI知识库”，"
         "将参考文档与说明等13份文档上传至工作区，AnythingLLM 依次完成文档解析、"
         "分块（chunk）与嵌入（embedding）入库，最终生成115个向量块。"
         "同时在工作区「聊天设置」中将查询模式设为 query（仅基于上传文档回答），"
         "并将相似度阈值设为低（≥0.25）、最大上下文片段设为8，以保证召回率。"),
        ("步骤5：验证智能问答。在工作区中新建 Thread 发起单轮提问，"
         "系统先按相似度检索出相关文档片段，再交由 qwen3:8b 基于片段生成回答，"
         "回答下方同时给出引用来源与相似度分数，可据此判断答案是否确实来自上传资料。"),
    ]
    for s in steps_a:
        anchor = new_para_after(anchor, s, size=BODY_PT, indent_chars=2)
    anchor = new_para_after(anchor, "（一）Ollama 模型列表（ollama list / ollama ps）：",
                             size=BODY_PT, bold=True)
    anchor = add_pic_after(anchor, os.path.join(SHOTS, "00_ollama_list.png"),
                            "图4.1  Ollama 本地模型列表与运行状态")
    anchor = new_para_after(anchor, "（二）AnythingLLM 工作区文件上传记录与知识库构建结果：",
                             size=BODY_PT, bold=True)
    anchor = add_pic_after(anchor, os.path.join(SHOTS, "05_workspace_upload_qa.png"),
                            "图4.2  AnythingLLM 工作区「AI知识库」及文档上传记录")
    anchor = add_pic_after(anchor, os.path.join(SHOTS, "06_vector_115.png"),
                            "图4.3  工作区向量数据库详情（115个向量块、检索参数）")
    anchor = new_para_after(anchor, "（三）大语言模型与嵌入器配置：", size=BODY_PT, bold=True)
    anchor = add_pic_after(anchor, os.path.join(SHOTS, "02_settings_llm.png"),
                            "图4.4  LLM首选项：Ollama 提供商 + qwen3:8b")
    anchor = add_pic_after(anchor, os.path.join(SHOTS, "03_settings_embedder.png"),
                            "图4.5  嵌入器首选项：Ollama 提供商 + nomic-embed-text")
    anchor = new_para_after(anchor, "（四）问答交互界面（含个人信息输出）：", size=BODY_PT, bold=True)
    anchor = add_pic_after(anchor, os.path.join(SHOTS, "08_workspace_personal.png"),
                            "图4.6  知识库问答界面：由文档中提取出、与")
    anchor = add_pic_after(anchor, os.path.join(SHOTS, "07_workspace_qa.png"),
                            "图4.7  问答记录与引用来源")

    # (二) 扣子部分：插在段落 8 之后（此时索引已变化，改用文本定位）
    for i, p in enumerate(cell.paragraphs):
        if p.text.strip().startswith("智能体编排页面3个部分"):
            anchor2 = cell.paragraphs[i + 1]
            break
    else:
        raise RuntimeError("未定位到扣子说明段")

    steps_b = [
        ("步骤1：创建智能体。进入扣子平台个人空间的「项目开发」页面，点击「创建智能体」，"
         "填写名称“AI新闻助手”与功能介绍后确认，进入三栏编排界面。"),
        ("步骤2：编写人设与回复逻辑。左侧面板选择“技能调用（搜索插件）”提示词模板作为基础，"
         "再改写为新闻助手的专用提示词，明确角色定位、两项检索技能、"
         "以及“只输出检索到的真实信息、每条新闻附来源链接、不编造发布日期与引用原文”等约束。"),
        ("步骤3：选择大模型及设置参数。展开「模型」面板，模型选择豆包·2.0·lite，"
         "协议类型为 Chat Api，生成特性选平衡模式；重复语句惩罚设为0、携带上下文轮数设为5、"
         "最大回复长度设为8192，使输出格式稳定且能携带多轮上下文。"),
        ("步骤4：添加插件作为技能。在「编排」面板的插件区添加三个插件："
         "新闻搜索（newsSearch）、每日AI新闻精选（get_ai_news）、AI 搜索（AIS），"
         "分别用于通用新闻检索、AI领域每日精选和主题权威报道补充。"),
        ("步骤5：设计并执行5组测试场景。在右侧「预览与调试」中依次提问，"
         "覆盖每日新闻、主题进展（推理模型、AI Agent、计算机视觉）以及超出能力范围的提问，"
         "逐组记录返回内容的真实性、来源链接完整性与响应耗时。"),
        ("步骤6：发布智能体。补充开场白后进入发布页，选择「扣子商店」作为发布渠道并提交，"
         "发布成功后可在发布管理页查看智能体的状态与运行指标。"),
    ]
    for s in steps_b:
        anchor2 = new_para_after(anchor2, s, size=BODY_PT, indent_chars=2)
    anchor2 = new_para_after(anchor2, "（一）智能体编排页面三部分截图：", size=BODY_PT, bold=True)
    anchor2 = add_pic_after(anchor2, os.path.join(SHOTS, "10_coze_orchestration.jpg"),
                             "图4.8  扣子智能体编排页：人设与回复逻辑、模型参数、预览与调试")
    anchor2 = new_para_after(anchor2, "（二）5组测试场景测试结果：", size=BODY_PT, bold=True)
    anchor2 = add_pic_after(anchor2, os.path.join(SHOTS, "12_coze_trace_cv.png"),
                             "图4.9  测试场景调用链详情（插件调用与执行过程）")
    anchor2 = new_para_after(anchor2, "（三）智能体发布后截图：", size=BODY_PT, bold=True)
    anchor2 = add_pic_after(anchor2, os.path.join(SHOTS, "11_coze_published.png"),
                             "图4.10  智能体发布管理页（扣子商店渠道发布成功）")

    # ───────────────────────── 第五节 ─────────────────────────
    cell5 = t.rows[6].cells[0]
    ps5 = cell5.paragraphs
    anchor5 = ps5[6]

    analysis = [
        ("5.1  本地知识库构建结果",
         "本地知识库共导入13份文档（实践参考文档、说明、Ollama部署文档、"
         "豆包大模型/语音合成/语音识别API开发流程等），文档总量约11万字符。"
         "经 AnythingLLM 解析分块并用 nomic-embed-text 向量化后，工作区最终生成115个向量块，"
         "向量库采用 LanceDB，工作区标识符为 25db1e64-3bff-4d00-81c1-29188b6dc03b。"
         "界面「向量数据库」面板显示的向量数量与检索参数（相似度阈值低、最大上下文片段8）"
         "与配置文件一致，说明整个入库流程已按预期完成。"),
        ("5.2  智能问答效果验证",
         "为排除多轮对话历史对检索的干扰，测试采用 query 模式并为每个问题新建独立 Thread 单轮提问。"
         "5个测试问题全部命中关键知识点，单题耗时9至15秒，"
         "输出 tokens 分别为574、545、392、333、432。"
         "以“任务4的实践目的是什么”为例，系统检索到参考文档原文中"
         "“通过本实践，使学生掌握基于RAG技术的本地知识库搭建流程……同时，使学生掌握智能体的创建与应用基本流程”，"
         "回答与原文高度一致，且每条回答下方均给出引用文档名与相似度分数"
         "（最高0.748），说明答案确实来源于上传资料而非模型自带知识。"
         "提问“说明的作者是谁？是多少？”时，系统从上传的说明文档中"
         "准确提取出、与，验证了 RAG 链路在中文场景下的可靠性。"),
        ("5.3  智能体构建与测试结果",
         "扣子平台创建的“AI新闻助手”采用单Agent自主规划模式，"
         "配置豆包·2.0·lite 模型（重复语句惩罚0、携带上下文5轮、最大回复长度8192）"
         "与新闻搜索、每日AI新闻精选、AI搜索三个插件。"
         "5组测试场景全部返回带可点击来源链接的真实新闻，"
         "耗时分别为68.4秒、30.4秒、45.0秒、32.0秒和67.4秒。"
         "其中第1组命中 MIT 让 GPT-6 Astra 直接修改 Qwen 权重、Anthropic 8954亿美元算力投入等要闻；"
         "第2组检索到美团 LongCat-2.5 原生多模态模型等推理方向进展；"
         "第3组检索到 Coding Agent 产品 ARR 累计达280亿美元、IBM与英伟达绑定智能体安全管控；"
         "第4组检索到 XREAL 1 Pro 3D 化显示、深算三号DCU 适配测试等计算机视觉成果。"),
        ("5.4  边界情况与问题分析",
         "第5组测试故意提问“帮我预测一下明年诺贝尔物理学奖会颁给谁”，"
         "超出智能体的检索能力边界。实测中智能体没有编造获奖人，"
         "而是转为检索物理与生命科学领域的真实新闻，并以“候选方向”的方式标注不确定性，"
         "说明提示词中“不编造发布日期与引用原文”的约束条款切实生效。"),
        ("5.5  调试中遇到的问题及解决",
         "一是 AnythingLLM 的 LLM_PROVIDER 无法通过接口写入（被判为非法值），"
         "改为直接修改 storage/.env 后重启后端解决；"
         "二是后端流式接口的事件类型为 textResponseChunk 而非 textResponse，"
         "且帧并非标准的空行分隔，解析时改用 JSON 深度扫描才能正确提取文本；"
         "三是工作区默认的 automatic 模式会走 Agent 循环导致回答跑偏，"
         "改为 query 模式后结果稳定；"
         "四是扣子平台免费版的模型并发上限，豆包·2.0·pro 在单次16851 tokens 的请求后"
         "立即提示“已超过模型并发上限”，改用豆包·2.0·lite 后5组测试全部跑通。"),
    ]
    for head, body in analysis:
        anchor5 = new_para_after(anchor5, head, size=BODY_PT, bold=True)
        anchor5 = new_para_after(anchor5, body, size=BODY_PT, indent_chars=2)

    # ───────────────────────── 第六节 ─────────────────────────
    cell6 = t.rows[7].cells[0]
    ps6 = cell6.paragraphs
    anchor6 = ps6[5]

    exp = [
        "通过本次实践，我完整走通了“本地大模型部署—知识库构建—智能体编排—发布应用”的完整链路，"
        "对RAG与AI Agent的融合应用有了更具体的认识。",
        "在Ollama+AnythingLLM部分，我最初以为RAG只是把文档丢进向量库即可，实际上每个环节都会影响最终效果。"
        "语料的完整性是前提，向量化的质量是基础，而检索参数与提示词的配合才是决定答案可靠性的关键。"
        "我特意设计了“提问说明作者”这个问题来验证答案是否真的来自上传资料，"
        "系统准确返回了、和，并在回答下方标注引用来源，这让我直观理解了"
        "“可溯源”相比纯模型回答的价值。",
        "调试过程中印象最深的是扣子平台“已超过模型并发上限”的报错。"
        "起初我以为是提示词或插件配置有问题，反复调整无效；"
        "换成轻量模型后立刻恢复正常，才意识到这是平台侧的并发限制而非我的配置错误。"
        "这次经历让我意识到，遇到异常时应先判断问题所在层次——"
        "是代码逻辑、配置参数，还是服务本身的资源限制，避免在错误的方向上反复尝试。",
        "在智能体部分，我体会到提示词中写清约束条款比写清功能描述更重要。"
        "专门设置“不编造发布日期与引用原文”这条约束后，"
        "在超出能力边界的问题上智能体确实没有编造内容，而是转为检索真实信息并标注不确定性。"
        "此外，三个插件的组合也让我理解了检索能力的分层：通用搜索负责广度，"
        "垂直领域的每日精选负责时效性，专业搜索负责补充权威报道。",
        "这次实践也暴露出我在工程化方面的不足——"
        "电子表格与文档处理、命令行操作这些看似基础的环节，"
        "实际做起来远没有想象中顺畅，出现问题时缺乏系统的排查方法。"
        "今后我会更注意记录每一步的现象和尝试过程，提高定位问题的效率。",
    ]
    for e in exp:
        anchor6 = new_para_after(anchor6, e, size=BODY_PT, indent_chars=2)

    doc.save(DOC)
    print("saved", DOC)


if __name__ == "__main__":
    main()
