# 古典作品精读：来源与整理说明

本栏目依据馆主指定的逐句材料建立，正文初始只显示希腊文。点击词语查看词形、中文释义及 Pape 德语词条；点击“句读笔记”查看中文译文、施莱尔马赫译文、结构分析。

## 收录范围

| 对话 | 收录范围 | 句读单元 |
| --- | --- | ---: |
| Symposium《会饮篇》 | 172a–223d | 698 |
| Philebus《斐勒布篇》 | 11a–67b | 1373 |
| Sophist《智者篇》 | 216a–242b | 664 |
| Parmenides《巴门尼德篇》 | 126a–166c | 1369 |
| Alcibiades 1《阿尔西比亚德斯 1》 | 103a–135e | 1103 |
| Apology《申辩篇》 | 17a–42a | 345 |
| Alcibiades 2《阿尔西比亚德斯 2》 | 138a–151c | 257 |
| Gorgias《高尔吉亚篇》 | 447a–527e | 1720 |

前三部作品的希腊文及中文译文取自馆主指定的三份材料。结构分析保留理解句子所需的主干、从句、支配关系和省略说明，删去逐项词形清单及泛泛的风格评论，并改写冗长、夸饰的讲解。原 TXT 文件未改动。

标点和顺序保留；两处粘连词在点击区域中拆成两个词，字串保持不变。《会饮篇》183页三处异常混排字符作了最小整理：`οὕτωawi → οὕτως`、`θαυμαστὴruk → θαυμαστή`依材料自己的附注，`ταῦταวั → ταῦτα`移除误混入的泰文字母。各处保留导入校记。

希腊文电子底本入口：

- [Symposium · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg011/)
- [Philebus · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg010/)
- [Sophist · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg007/)
- [Parmenides · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg009/)
- [Alcibiades 1 · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg013/)
- [Apology · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg002/)
- [Alcibiades 2 · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg014/)
- [Gorgias · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg023/)

《高尔吉亚篇》使用该作品URN对应的Perseus官方 `canonical-greekLit` 仓库 `tlg0059.tlg023.perseus-grc2.xml`，SHA-256为 `c0d1fc4fd562d2ed3c3378a04c1965c4883b28d50a745320f9ea91be9b601f9f`。用户本次所贴 `tlg013` 链接实际为《阿尔西比亚德斯 1》，已按明确的作品名称及原精读稿中记载的底本改用 `tlg023`。完整保存447a–527e，沿用材料的1720个句读编号；排除现代标签、书目、注释及编辑拟删文字，保留正文补入文字。引诗的行与行之间补空格，以免词语粘连；不补造原XML空缺处的文字。

本篇前334单元的中文句译取自馆主指定的447a–461b精读稿，结构说明作简化整理；335–1720单元的中文句译与结构说明按馆主明确要求续写，分别保存于 `tools/gorgias-reading/` 和 `tools/gorgias-responses.json`。简短同形答语可复用同一解释，长句另行说明具体的从句、支配、省略与论证转折。原阶段稿保持不变。全篇笔记均可由馆主在网页中修改。

《巴门尼德篇》依 Perseus 的 Burnet 1910 电子本全文导入，收录 126a–166c。原 XML 保存在 `tools/parmenides-source.xml`；保留正文次序及用字，编辑标作删除的 `del` 内容不列入连续阅读正文。馆主提供的 `Parmenides.txt` 含前 1235 个句读单元，最后一句跨至 163a；中文及结构说明以此为参考，后续 134 个单元补充至全篇结束。来源摘要及校验值见 `docs/parmenides-import-report.json`。

《阿尔西比亚德斯 1》及《申辩篇》分别按 Perseus `tlg013.perseus-grc2`、`tlg002.perseus-grc2` 全文核对；原始 XML 保存在 `tools/alcibiades1-source.xml` 和 `tools/apology-source.xml`。中文及结构说明参考馆主上传的 `Acibiades 1.txt`、`Apology.txt`。前者的第577、578条各重复粘贴了一次，导入时各保留一次。中文保留材料原有措辞，少量对应错位及结构说明的修订另存 `tools/additional-classics-edits.json`，仍可由馆主在网页自行修改；本次导入不等于全篇译注已完成语文学终校。

电子正文作三处最小整理：去除《阿尔西比亚德斯 1》105d、《申辩篇》18b混入的 `>`；《申辩篇》36b–c游离的 `τ` 从 `τ τί ἄξιός` 移回 `ἐμαυτὸν ῷ ὄντι`，还原为 `τί ἄξιός`、`ἐμαυτὸν τῷ ὄντι`。后一处对照[希腊语中心所收原文36b–c](https://www.greek-language.gr/digitalResources/ancient_greek/library/browse.html?page=14&text_id=104)；XML原件未改。导入校验将这几项明确整理计入比较，其余连续正文与指定电子本一致。

《阿尔西比亚德斯 2》按 Perseus `tlg014.perseus-grc2` 收录138a–151c全文，共257个句读单元。馆主上传的 `Alcibiades 2.txt` 首行写138a–150d，但实际材料已至151c，导入不按首行截断。中文以该材料为主，少数明显误词已另存修订；结构说明保留有效解释并改写机械清单。连续希腊文逐字核对底本：第171条补回底本的破折号，第184条把单个省略号恢复为底本的三个点；两者仅是标点呈现，原始TXT及XML均不改动。来源及覆盖统计见 `docs/alcibiades2-import-report.json`，词形补注明确保存于 `tools/alcibiades2-morphology.json`；带句读编号的键仅适用于该句，避免把同形的限定动词与分词混为一谈。

Perseus原始电子文本许可：[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/)。具体编辑说明保留于原稿。

## 德文原译：只摘录，不翻译

采用馆主提供的《Gesammelte Werke》EPUB，书内署名译者 **Friedrich Daniel Ernst Schleiermacher**，前三部作品相关部分标注 **Akademie Verlag Berlin 1986**，《巴门尼德篇》、《申辩篇》及《阿尔西比亚德斯 2》标注 **1985**，《阿尔西比亚德斯 1》标注 **1987**。此处书目信息据EPUB自身记录，未另行核对纸本。保留旧拼写、用词与标点，不以新德文替换。

提取位置：

- Symposium：`OEBPS/Text/part0017.xhtml`，正文172–223页；不收录该篇导言。
- Philebus：`OEBPS/Text/part0019.xhtml`，11–67页。
- Sophist：`OEBPS/Text/part0015.xhtml`，216–242页；不收录该篇导言。
- Alcibiades 2：`OEBPS/Text/part0008.xhtml` 中“Der sogenannte Zweite”部分的正文标题“Alkibiades”之后，138–151页；不收录导言、前篇《弥诺斯》及下一部分。EPUB漏标整数页147，对应德文仍在所标146页中连续保留，来源索引不凭空补造页码。
- Alcibiades 1：`OEBPS/Text/part0020.xhtml` 中正文标题“Alkibiades”之后，103–135页；排除前置导言。
- Apology：`OEBPS/Text/part0006.xhtml` 中“Des Sokrates Verteidigung”标题之后，续至 `part0007.xhtml`，止于下一篇之前。整数页码为17–41，42a的结尾德文仍在EPUB所标41页中，保留实际来源页号。
- Parmenides：标题位于 `OEBPS/Text/part0005.xhtml` 末尾，正文在 `part0006.xhtml`，126–166页；不收录前后相邻作品及导言。
- Gorgias：标题位于 `OEBPS/Text/part0009.xhtml`，正文在 `part0010.xhtml`，447–527页；止于下一篇《泰阿泰德篇》之前。本篇标注Akademie Verlag Berlin 1985。全篇1081次发言转换与希腊文逐一核对一致后，再在各自发言内匹配句段。849–850、1660–1661、1716–1717等处保留跨越希腊句读边界的完整德文原句；889–890与1677–1678处另核对句界。未使用原阶段稿的自译德文作为显示译文。

该 EPUB 只有 Stephanus 整数页标记，没有 a–e 小节或逐句编号。句读笔记采用原译中的对应句段：按页码、内容顺序与说话人匹配，并允许一句跨越整数页。德译把数个希腊短句合写时，相关单元共用完整原译句。所摘文字保留原文；匹配采用程序辅助并作抽查，不表示每一处已完成独立的语文学复核。《智者篇》最后一个摘录止于本栏目 242b 的对应句，不把该整数页的后续论述一并显示。

《阿尔西比亚德斯 1》133c中本底本收录的四个句读单元（1001–1004）不见于所供施莱尔马赫译本；另有115d–e的答语及一组问答（391、407–408）、128a–b的衣物类比及答语（792–793）未单独译出。希腊文照收，德文栏明确说明缺少对应译文，数据以 `deStatus: not-in-source` 标记，不以相邻句冒充。德译把相邻提问合写时，只在相应单元共用原译句。

**没有使用机器翻译生成、改写或补齐德文句译。此前材料中的德文句译与词汇德译不作为本栏目显示的译文。**

## 德语词典：Pape

德文词条直接引用 **Wilhelm Pape, Handwörterbuch der griechischen Sprache** 的电子文本；词条开头作为预览，展开可读完整条目，不把词条开头声称为当前句子的唯一义项。

数据来源：[Patristic Text Archive · pta_lexika](https://github.com/PatristicTextArchive/pta_lexika)，`public`分支的`Pape.json`；其整理来源见[词典来源说明](https://github.com/PatristicTextArchive/pta_lexika/blob/public/sources/README.md)。Pape历史词典原文为公版文献；电子整理来源如上署名保留。

匹配词条时将声调、粗细气、下标ι归一；这会使同形或近形词条一并显示。应核对词条头字与实际语境。缺少匹配时显示“暂无 Pape 词条”。未以机器翻译补写德语释义。词语弹窗不再重复句读笔记。

## 词法与语境

使用 **Alessandro Vatri & Barbara McGillivray (2018), The Diorisis Ancient Greek Corpus** 的自动标注，按Stephanus整页与词序逐词对齐，同时补充Morpheus词形候选，避免语料自身误选同形词时漏掉正确词条。原精读稿明确列出的动词词条与形态优先用于筛选候选；这不代表原稿已全部校订。正文仍以用户指定精读稿为准，语料不用于替换正文。同一词形可以有多个词条及多个形态。

- [Diorisis 数据集与引用](https://doi.org/10.6084/m9.figshare.6187256.v1)，[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/)。使用本栏目对应的柏拉图XML文件，不附带分发整个语料库。
- Morpheus/Diogenes词形资料经[Lyceum Archeion](https://github.com/lyceum-quest/archeion)的`v2026.04.09`版`morph.db`分发。下载文件已对照该版本公布的SHA-256校验。
- [Diogenes](https://github.com/pjheslin/diogenes)由P. J. Heslin维护，词形分析源自[Perseus Morpheus](https://github.com/PerseusDL/morpheus)。[Lyceum数据来源说明](https://github.com/lyceum-quest/archeion/releases/download/v2026.04.09/DATA_PROVENANCE.md)。

Diorisis对应不等于人工确认；保留语料中的候选，不把自动选择显示为确定答案。`nom/voc/acc`等复合标签全部展开，避免把中性主宾同形误说成只有主格。词类与性分开显示；有限动词显示人称、数、时态、语态、语气；分词另显示格与性；无屈折词不强填不存在的格或性。

少量专名及语料、词形库没有收录的形式由编辑补注，数据中保留其来源。中文短释来自材料中可明确提取的单词释义和随库保存的中文词汇表；它们与中文句译分开呈现，缺项显示“暂无中文释义”。

## 数据结构与维护

- `data/classics/catalog.json`：作品目录与版本号。
- `data/classics/{work}/catalog.json`：作品范围、页码与导入统计。
- `data/classics/{work}/{page}.json`：该页希腊文、逐词候选索引和 `units.reading` 中的三项句读内容；整数页德文只作来源索引，不显示为另一栏笔记。
- `data/classics/pape.json`：本栏目实际用到的Pape词条，独立载入并缓存。
- `tools/import_classics.py`：可重复运行的导入器，无翻译模型依赖。
- `tools/import_gorgias.py`：全篇《高尔吉亚篇》的导入器；`gorgias-source.xml` 保存原TEI，`gorgias-units.json` 保存完整句读索引，`gorgias-notes.json` 保存三栏笔记；`gorgias-zh-supplement.json` 和 `gorgias-morphology.json` 保存中文词汇及少见词形补注。`docs/gorgias-import-report.json`、`docs/gorgias-alignment-review.json` 记录覆盖与德译对应。Diorisis语料仍按同一数据集署名。
- `tools/import_parmenides.py`、`tools/parmenides-notes.json`：全篇《巴门尼德篇》的导入器及三栏笔记。另有词汇补充表与少量明确标明来源的词形补注。
- `tools/import_additional_classics.py`、`tools/{alcibiades1,apology,alcibiades2}-notes.json`：新增各篇的可复现导入及三栏笔记；对应的 `*-morphology.json`、`additional-classics-zh.json` 保存词形补注及中文短释。
- `docs/{alcibiades1,apology,alcibiades2}-import-report.json`：材料校验值、去重记录、德译匹配组与缺译单元、覆盖率。
- `tools/classics-reading-notes.json`：三部作品的句读内容与摘录对应信息。
- `tools/classics-structure-edits.json`：逐条改写的结构说明。
- `tools/simplify_classics.py`：从原译检索对应句段、整理结构说明并写回网页资料；运行 `--apply` 应用结果。
- `docs/classics-alignment-review.json`：摘录匹配的内部核对记录；相似度为检索指标，不等于译文准确率。
- `docs/classics-import-report.json`：覆盖率与未识别词形，覆盖率表示工具是否返回候选，**不代表正确率**。

运行导入器时提供原项目目录、下载的词形与词典资源目录，以及馆主的EPUB路径。未把EPUB整本或约400MB的词形数据库提交到网站。

## 馆主自行修改

所有作品均提供网页编辑、浏览器本机保存、ZIP 导出与 JSON/ZIP 备份导入。导出的 ZIP 含有修改的完整页资料及可重新导入的备份；上传 GitHub 后才会影响公开网站。本机草稿按作品独立保存，导入时核对句读编号、页码及希腊原文，拒绝错配的备份。具体操作见 [自己修改精读笔记](../classics-help.html)。

网页导出的页面在 `reading.ownerEdited` 中保留馆主修改标记。再次运行导入器时，`tools/owner_notes.py` 会在句读编号、页码和原文均一致时保留这些修改；不会用生成内容覆盖馆主已上传的笔记。

由Diorisis及Perseus文本形成的结构化衍生数据依[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/)提供，保留各来源署名。Pape及Schleiermacher原文保持各自公版文本的属性。馆主原有中文译注的权利不因数据许可说明而自动变更。
