# Zotero Vault Batch Reading 配置教程

## 先说结论

是的，如果别人想把这个 skill 真正跑起来，通常需要先做一点配置。  
但要分清楚两类：

- **必须配置**：Zotero Desktop、本地 API、Python 依赖。
- **可选配置**：Obsidian、知识库目录组织、和 agent 的个性化提示词。

其中 **Obsidian 不是必须的**。  
这个 skill 的核心输出本质上就是一套 Markdown 文件夹。哪怕不用 Obsidian，只要能管理本地文件，也可以正常使用。

如果用户本来就在用 Obsidian，那这套输出会更顺手，因为可以直接把生成的 `03_reading_notes` 和 `04_deep_reading_notes` 当成知识库的一部分。

---

## 一、这个 skill 依赖什么

要让它工作，至少需要下面这些环境：

1. **Zotero Desktop**
   用来管理论文、分类和附件 PDF。

2. **Zotero Local API**
   skill 通过 `http://127.0.0.1:23119` 读取 collection、条目、附件信息。

3. **Python 3.8+**
   用来运行批处理脚本。

4. **Python 依赖**
   当前脚本需要：
   - `pymupdf`
   - `requests`

5. **Claude / Codex / 兼容 agent 运行环境**
   用来执行这个 skill 的两层流程：
   - 脚本做 prepare / skim
   - agent 做 recommend / deep reading

6. **Obsidian（可选）**
   如果你希望把输出变成一个长期维护的阅读知识库，建议用。

---

## 二、必须配置：Zotero

### 1. 安装 Zotero Desktop

先确保用户本机已经安装 Zotero Desktop，并且可以正常打开自己的文献库。

### 2. 确保论文条目里有 PDF 附件

这个 skill 会从 Zotero 条目下寻找 PDF attachment。  
因此至少要满足：

- 文献在某个 collection 里；
- 该文献下挂了 PDF；
- PDF 本地可访问。

如果 Zotero 条目只有 metadata，没有附件 PDF，这个 skill 仍然能记录条目，但无法完成 PDF 复制和全文 Markdown 转换。

### 3. 打开 Zotero Local API

这个 skill 依赖 Zotero 的本地 API，默认地址是：

```text
http://127.0.0.1:23119
```

用户需要在 Zotero 中确认：

1. 打开 `Edit / Preferences`（或偏好设置）。
2. 找到 `Advanced` 相关设置。
3. 确认本地 API 可用。

然后启动 Zotero Desktop，不要关闭。

### 4. 验证 Zotero API 是否可访问

可以在终端运行：

```powershell
curl http://127.0.0.1:23119/api/users/0/collections
```

如果能返回 JSON，说明本地 API 是通的。

如果不通，常见原因只有几个：

- Zotero 没开；
- 本地 API 没启用；
- 本机安全软件或环境阻止了端口访问。

---

## 三、必须配置：Python 环境

### 1. 安装 Python

确保命令行里能跑：

```powershell
python --version
```

建议 Python 3.8 及以上。

### 2. 安装依赖

进入 skill 目录后执行：

```powershell
pip install -r requirements.txt
```

当前 `requirements.txt` 只包含：

```text
pymupdf>=1.23
requests>=2.31
```

### 3. 验证脚本可运行

可以先测试：

```powershell
python scripts/run_zotero_vault_batch_reading.py --help
```

如果能正常显示帮助信息，说明脚本本身能启动。

---

## 四、必须理解：这个 skill 的输入和输出

### 输入是什么

用户至少要提供三样东西：

1. **collection key**
2. **collection name**
3. **output root**

例如：

```powershell
python scripts/run_zotero_vault_batch_reading.py `
  --collection-key R9MMZ5TY `
  --collection-name "ES" `
  --output-root "./ES" `
  --mode all
```

### 怎么找 collection key

可以用：

```powershell
curl http://127.0.0.1:23119/api/users/0/collections
```

返回结果里会有类似：

```json
[
  {
    "key": "R9MMZ5TY",
    "name": "ES"
  }
]
```

这里的 `key` 就是 `--collection-key`，`name` 就是 `--collection-name`。

### 输出会生成什么

第一次跑完后，通常会得到这样的目录：

```text
<output-root>/
  00_collection_overview.md
  _ProcessLog_进度记录.md
  01_original_pdf/
  02_original_md/
  03_reading_notes/
  04_deep_reading_notes/
  _workflow/
    collection_items.json
```

其中：

- `01_original_pdf/`：从 Zotero 复制出来的 PDF
- `02_original_md/`：由 PDF 转出来的 Markdown
- `03_reading_notes/`：全部论文的泛读笔记
- `04_deep_reading_notes/`：精选论文的精读笔记
- `00_collection_overview.md`：整个 collection 的导航页

---

## 五、可选配置：Obsidian

### Obsidian 是不是必须

不是必须。

这个 skill 输出的是标准 Markdown 文件夹，所以即使完全不用 Obsidian，也能用：

- 文件管理器查看
- VS Code 查看
- 其他 Markdown 工具查看

### 为什么很多人会想配 Obsidian

因为它特别适合长期维护文献阅读知识库：

- 可以按双链方式组织论文笔记；
- 可以把 `00_collection_overview.md` 当索引页；
- 可以继续在 `04_deep_reading_notes/` 上补充自己的批注和关联；
- 可以把精读笔记和研究计划、写作草稿放到同一个 vault 里。

### 如果要配 Obsidian，怎么配

最简单的做法不是“让 Obsidian 去适应 skill”，而是反过来：

1. 先选定一个输出目录，比如：

```text
D:\paper\research\ES
```

2. 在 Obsidian 中把这个目录作为一个 vault 打开；

3. 以后每次 skill 更新：
   - `03_reading_notes/`
   - `04_deep_reading_notes/`
   - `00_collection_overview.md`

Obsidian 会自动看到这些变化。

### 推荐的 Obsidian 使用方式

如果用户准备用 Obsidian，建议这样理解目录：

- `00_collection_overview.md`：入口页
- `03_reading_notes/`：批量初筛层
- `04_deep_reading_notes/`：真正进入研究知识库的层
- 用户自己的研究笔记：另外单独放，比如 `notes/` 或 `projects/`

这样不会把自动生成内容和手写内容混在一起。

---

## 六、agent 侧需要怎么配

### 1. 让 agent 知道研究主题

这个 skill 最重要的不是“能批量处理 PDF”，而是“能围绕研究问题筛论文和精读”。

因此建议用户至少告诉 agent：

- 研究什么主题；
- 关注哪个地区；
- 重点是暴露、健康负担、预测还是机制；
- 关键变量是什么；
- 想让 agent 推荐精读，还是全部精读。

这些内容可以：

- 直接在对话里告诉 agent；
- 或者写进 `CLAUDE.md` / `AGENTS.md` 一类项目说明文件。

### 2. 让 agent 明确当前输出目录

最好不要让 agent 自己猜输出目录。  
直接约定，例如：

```text
本次 Zotero collection 输出目录是 D:\paper\research\ES
```

这样可以避免多次运行后输出位置混乱。

### 3. 明确泛读和精读的边界

这个 skill 的设计前提是：

- `03` 是泛读
- `04` 是精读

所以不要把 `03` 当成最终阅读成果。  
真正要在研究里引用、比较方法、提炼结论的论文，应该进入 `04`。

---

## 七、推荐的首次使用流程

第一次给别人用时，建议按这个顺序走：

### 第一步：确认 Zotero collection 可读

先跑：

```powershell
curl http://127.0.0.1:23119/api/users/0/collections
```

确认 collection key 存在。

### 第二步：先做 prepare

第一次不要直接全量深读，先跑：

```powershell
python scripts/run_zotero_vault_batch_reading.py `
  --collection-key <KEY> `
  --collection-name "<NAME>" `
  --output-root "<OUTPUT>" `
  --mode prepare
```

确认：

- PDF 能复制；
- Markdown 能生成；
- `_workflow/collection_items.json` 正常写出。

### 第三步：再做 skim

然后跑：

```powershell
python scripts/run_zotero_vault_batch_reading.py `
  --collection-key <KEY> `
  --collection-name "<NAME>" `
  --output-root "<OUTPUT>" `
  --mode skim
```

确认 `03_reading_notes/` 和 `00_collection_overview.md` 正常生成。

### 第四步：让 agent 做 recommend

不要一开始就对所有论文精读。  
先让 agent 基于研究问题从 `03_reading_notes/` 里挑出值得精读的论文。

### 第五步：再做 deep reading

最后只对真正关键的论文生成 `04_deep_reading_notes/`。

这样最符合这个 skill 的设计逻辑，也最省时间。

---

## 八、常见问题

### 1. 没有 Obsidian 能不能用

可以。  
Obsidian 只是更方便，不是依赖项。

### 2. Zotero 里只有 metadata，没有 PDF，能不能用

可以部分用。  
能生成条目级处理结果，但不能做完整的 PDF 复制和全文 Markdown 转换，因此也无法稳定支撑精读。

### 3. 为什么不直接让 agent 一次性读完全部论文

因为这会把“批量机械处理”和“高成本理解”混在一起。  
这个 skill 的价值就在于先批量整理，再有选择地深入。

### 4. 输出目录能不能直接放在 Obsidian vault 里

可以，而且这是推荐用法之一。  
只要你能接受：

- 自动生成内容会持续更新；
- 你最好把自己的手写笔记和自动产物分区管理。

### 5. 这个 skill 能不能直接证明复合事件健康协同效应

不能。  
它只是一个文献处理和阅读工作流，不负责替代领域方法论判断。  
是否存在协同效应，要看具体论文证据和研究设计。

---

## 九、一套最实用的建议

如果要让别人第一次就尽量顺利地用起来，可以直接告诉他：

1. 安装并打开 Zotero。
2. 确保目标 collection 里的论文带 PDF。
3. 打开 Zotero 本地 API。
4. 安装 Python 和依赖。
5. 先跑 `prepare`，再跑 `skim`。
6. 把输出目录用 Obsidian 打开，或者直接当普通 Markdown 文件夹使用。
7. 最后让 agent 根据研究问题挑精读论文，而不是一上来全读。

---

## 一句话总结

这套 skill 真正需要配置的只有 **Zotero + 本地 API + Python 依赖**。  
**Obsidian 是增强项，不是前置条件。**  
如果用户本来就在做长期科研阅读，Obsidian 会让这套输出更好用；如果没有，也完全不影响这套 skill 的核心工作流。
