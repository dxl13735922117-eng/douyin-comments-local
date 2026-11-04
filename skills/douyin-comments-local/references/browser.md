# 本机 Chrome 页面读取

首先发现并阅读**当前会话**浏览器工具的完整文档。以下是已验证环境中的示意 API，不是固定能力声明；不存在的方法不猜测，也不另建浏览器连接绕过限制。

## 建立连接

若提供 `mcp__cua_repl.js`，首次调用遵守它的初始化要求，例如一次只执行：

```javascript
await cua.getState();
```

从实际返回的浏览器列表选择用户的本机 Chrome，再读取该浏览器文档。例如：

```javascript
var browser = await cua.getBrowser({id: actualChromeId});
```

后续按返回文档命名会话、绑定标签。不要把 `actualChromeId` 当作固定值。若要接管已有标签，从 `browser.user.openTabs()` 的新鲜结果 claim；`tabs.get` 只用于本聊天已拥有的标签。旧聊天仍占有的标签可改用同一浏览器新建标签，不要强占。

```javascript
await browser.nameSession('💬 抖音评论');
var tab = await browser.tabs.new();
await tab.goto(videoUrl);
nodeRepl.write(await tab.playwright.domSnapshot());
```

已选浏览器要复用；单个标签失效不是换浏览器的理由。重启应用后重新发现标签。内核重置时遵守工具的重新初始化要求，不复用已丢失变量。

## 选择器与提取

先观察一个一级评论、其正文、昵称、点赞、时间及展开控件，再展开一楼，确认回复与父评论的 DOM 关系。只查看需要的 DOM 属性和渲染文字；不要读 script、框架内部状态、Cookie 或本地存储。

通过本机文件工具读取 `scripts/read_comments.js`，把完整函数表达式源码传入浏览器工具；不要假定浏览器 REPL 可以读取本地文件。示意：

```javascript
// readerSource 是已经从本地脚本读到的源码字符串。
var cfg = {video_id: verifiedVideoId, offset:0, limit:20};
var batch = await tab.playwright.evaluate(
  '(' + readerSource + ')(' + JSON.stringify(cfg) + ')'
);
nodeRepl.write(JSON.stringify(batch));
```

字符串形式 evaluate 不会自动调用函数，需如上直接调用；不使用 `eval` 或 `new Function`。脚本严格只读 DOM。

默认观察档：

| 字段 | 默认选择器/含义 |
|---|---|
| root | `[data-e2e="comment-list"]` |
| top | `[data-e2e="comment-item"]`，一级和回复共用，脚本按祖先关系区分 |
| body | `.FduGc_lz > .Sh1Da424`，排除相邻身份/点赞标记 |
| author | `.comment-item-info-wrap a` |
| likes | `.VpA2NKl1` |
| time | `.VAQA49VP` |
| id_node | `[data-e2e="video-comment-more"] [id^="tooltip_"]` |
| id_attribute / id_prefix | `id` / `tooltip_` |
| counter | `[data-e2e="feed-comment-icon"]` |

这些是 2026-11 的页面观察，哈希 class 可能变化。改版时用新 DOM 覆盖对应配置，不把默认零匹配当作“0条”。若页面回复不嵌套在一级节点中，不能套用该提取器；逐楼用页面文字形成 `dyc-dom-v1` 批次，或者说明无法可靠关联。

计数节点可能已离开当前渲染区域，`page_count_text` 会留空；这时可从实际页面/AX 确认目标视频计数，再给导出器传 `--page-count`。不要用不可确认的计数补足评论。

`has_more=true` 时，在本次 DOM 改变前用 `next_offset` 读取下一段，直到完成这一屏已加载列表。下一次点击或滚动后从 offset=0 重新读，交给本地按 ID 去重。按输出大小调整 limit，避免 JSON 截断。

## 展开与滚动

点击必须走工具动作接口。使用当前状态中的按钮文字及其父楼来定位；多个“展开2条回复”不能全局取第一个猜测目标。可使用观测过的评论菜单 ID 锁定父楼，或通过唯一正文筛选。

普通动作成功后读取新状态，再决定下一步；重复出现的“展开更多”可能需要分批点击。不在只读 evaluate 内调用 `click()`、`scrollTo()` 或请求接口。

滚动对象来自实际页面结构。可以使用工具支持的滚动或已观察元素上的键盘操作；不要假定整个文档就是滚动容器。读取前后都保存批次，防止虚拟列表丢记录。

保存原始批次时不要把评论文本拼成 shell 表达式。所有动作和状态读取顺序执行，不并发操作同一评论区。

## 结束与交接

记录底部提示原文、剩余展开入口和末次是否有新增。页面评论计数不是抓取计数；二者可以不同，原因未知时不推测。

登录或验证码阻挡时，若当前工具提供 `markHandoff()`，先标记需要保留的标签，再请用户操作。只标记真实需要接续的页面。正常结束清理自己创建的临时标签，释放用户原有标签。
