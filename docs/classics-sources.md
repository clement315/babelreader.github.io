# 古典作品精读：来源与整理说明

本栏目依据馆主指定的三份逐句精读稿建立，正文初始只显示希腊文；点击词语后查看形态候选、词典与中文笔记。它是持续校订的阅读工具，自动词法分析尚未全部人工复核。

## 收录范围

| 对话 | 精读稿范围 | 句读单元 | 稿件状态 |
| --- | --- | ---: | --- |
| Symposium《会饮篇》 | 172a–223d | 698 | 合订稿；172a–185e原稿待校 |
| Philebus《斐勒布篇》 | 11a–67b | 1373 | 全篇稿 |
| Sophist《智者篇》 | 216a–242b | 664 | 阶段稿；其余内容尚未收录 |

希腊文及中文句译、语法和风格说明来自这三份稿件。标点和顺序保留；两处原稿粘连词在点击区域中拆成两个词，字串保持不变。《会饮篇》183页三处异常混排字符作了最小整理：`οὕτωawi → οὕτως`、`θαυμαστὴruk → θαυμαστή`依原稿自己的附注，`ταῦταวั → ταῦτα`移除误混入的泰文字母。各处保留导入校记，原TXT未改动。没有把原稿待校部分标作校订完成。

希腊文电子底本入口：

- [Symposium · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg011/)
- [Philebus · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg010/)
- [Sophist · Perseus](https://scaife.perseus.org/library/urn:cts:greekLit:tlg0059.tlg007/)

Perseus原始电子文本许可：[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/)。具体编辑说明保留于原稿。

## 德文原译：只摘录，不翻译

采用馆主提供的《Gesammelte Werke》EPUB，书内署名译者 **Friedrich Daniel Ernst Schleiermacher**，相关部分标注 **Akademie Verlag Berlin 1986**。此处书目信息据EPUB自身记录，未另行核对纸本。保留旧拼写、用词与标点，不以新德文替换。

提取位置：

- Symposium：`OEBPS/Text/part0017.xhtml`，正文172–223页；不收录该篇导言。
- Philebus：`OEBPS/Text/part0019.xhtml`，11–67页。
- Sophist：`OEBPS/Text/part0015.xhtml`，216–242页；不收录该篇导言。

该EPUB只有Stephanus整数页标记，没有a–e小节或逐句编号。因此德文显示为**整页参照**，不将它伪装成逐句对齐译文。242页德文可能涵盖本阶段希腊文停止处之后的内容；本栏目希腊文仍仅止于242b。

**没有使用机器翻译生成、改写或补齐德文句译。原精读稿里先前生成的德文句译与词汇德译不用于本栏目。**

## 德语词典：Pape

德文词条直接引用 **Wilhelm Pape, Handwörterbuch der griechischen Sprache** 的电子文本；词条开头作为预览，展开可读完整条目，不把词条开头声称为当前句子的唯一义项。

数据来源：[Patristic Text Archive · pta_lexika](https://github.com/PatristicTextArchive/pta_lexika)，`public`分支的`Pape.json`；其整理来源见[词典来源说明](https://github.com/PatristicTextArchive/pta_lexika/blob/public/sources/README.md)。Pape历史词典原文为公版文献；电子整理来源如上署名保留。

匹配词条时将声调、粗细气、下标ι归一；这会使同形或近形词条一并显示。应核对词条头字与实际语境。缺少匹配的词条明确显示“暂未匹配”，并提供原译页的上下文。未以机器翻译补写德语释义。

## 词法与语境

使用 **Alessandro Vatri & Barbara McGillivray (2018), The Diorisis Ancient Greek Corpus** 的自动标注，按Stephanus整页与词序逐词对齐，同时补充Morpheus词形候选，避免语料自身误选同形词时漏掉正确词条。原精读稿明确列出的动词词条与形态优先用于筛选候选；这不代表原稿已全部校订。正文仍以用户指定精读稿为准，语料不用于替换正文。同一词形可以有多个词条及多个形态。

- [Diorisis 数据集与引用](https://doi.org/10.6084/m9.figshare.6187256.v1)，[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/)。使用三个柏拉图XML文件，不附带分发整个语料库。
- Morpheus/Diogenes词形资料经[Lyceum Archeion](https://github.com/lyceum-quest/archeion)的`v2026.04.09`版`morph.db`分发。下载文件已对照该版本公布的SHA-256校验。
- [Diogenes](https://github.com/pjheslin/diogenes)由P. J. Heslin维护，词形分析源自[Perseus Morpheus](https://github.com/PerseusDL/morpheus)。[Lyceum数据来源说明](https://github.com/lyceum-quest/archeion/releases/download/v2026.04.09/DATA_PROVENANCE.md)。

Diorisis对应不等于人工确认；保留语料中的候选，不把自动选择显示为确定答案。`nom/voc/acc`等复合标签全部展开，避免把中性主宾同形误说成只有主格。词类与性分开显示；有限动词显示人称、数、时态、语态、语气；分词另显示格与性；无屈折词不强填不存在的格或性。

少量专名及语料、词形库没有收录的形式由编辑补注，界面与数据中注明“编辑补注”。中文短释来自原稿中可明确提取的单词释义和随库保存的中文词汇表；它们与中文句译分开呈现，缺项明确保留待补。

## 数据结构与维护

- `data/classics/catalog.json`：作品目录与版本号。
- `data/classics/{work}/catalog.json`：作品范围、页码与导入统计。
- `data/classics/{work}/{page}.json`：该页希腊文、中文笔记、逐词候选索引与德文原译。
- `data/classics/pape.json`：本栏目实际用到的Pape词条，独立载入并缓存。
- `tools/import_classics.py`：可重复运行的导入器，无翻译模型依赖。
- `docs/classics-import-report.json`：覆盖率与未识别词形，覆盖率表示工具是否返回候选，**不代表正确率**。

运行导入器时提供原项目目录、下载的词形与词典资源目录，以及馆主的EPUB路径。未把EPUB整本或约400MB的词形数据库提交到网站。

由Diorisis及Perseus文本形成的结构化衍生数据依[CC BY-SA 3.0 US](https://creativecommons.org/licenses/by-sa/3.0/us/)提供，保留各来源署名。Pape及Schleiermacher原文保持各自公版文本的属性。馆主原有中文译注的权利不因数据许可说明而自动变更。
