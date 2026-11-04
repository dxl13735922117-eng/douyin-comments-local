# 页面批次格式

`scripts/export.py` 接受本次运行目录下 `raw/dom_*.json`，UTF-8，结构如下（这里全部是虚构数据）：

```json
{
  "schema": "dyc-dom-v1",
  "mode": "browser-ui",
  "video_id": "123",
  "comments": [{
    "cid": "t1",
    "author": "示例用户",
    "text": "这是虚构评论，不是真实采集结果。",
    "likes_text": "12",
    "time_text": "昨天",
    "replies": [{"cid": "r1", "author": "示例回复者", "text": "虚构回复。", "likes_text": "0"}]
  }]
}
```

- 视频 ID、评论 ID 都用字符串，避免 JavaScript 大整数精度损失。`cid` 缺失或空字符串时使用内容指纹。
- `text` 必须非空；昵称、点赞、时间未知就缺省或留空，不写猜测值。只读 DOM 提取器保留混合正文中的图片表情 alt。
- 一批可只保存新增一级评论，或为新增回复重复带上父评论；导出器按 ID 合并。不得把同一个回复 ID 归到不同父评论。
- ID 可来自已观察到的评论节点属性或其菜单 `tooltip_数字` 属性。字段 `id_source` 只说明来源是 DOM 属性，不保证等同于平台接口 ID。
- `comments_replies.json` 的 `parent_cid` 指向一级父评论；不代表回复链中的直接被回复对象。
- 按 ID 去重保留不同 ID 的相同正文；无 ID 时用视频、一级父评论、昵称或已读资料标识、正文、显示时间生成 SHA-256 指纹。指纹的不可区分与相对时间变化限制会写入报告。
- 点赞简写保留原文，`likes_approx` 仅用于近似排序。缺失点赞是 null，不是 0。
- 提取器的 `matched_top_nodes`、`next_offset`、`has_more` 只描述本次 DOM 分页，不代表抖音服务端是否还有更多。
- 提取器的 `unexpanded` 和 `bottom_excerpt` 是辅助证据；要结合当前页面状态判断底部，不能仅因提取批次为空就宣称完成。
