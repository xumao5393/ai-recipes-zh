# 连接器工具清单（2026-11-09 17:22 EST，GetDynamicTools 实读）
## Gmail（25 个工具）
只读（9）：get_me, search_emails, read_email, get_thread, list_labels, list_filters, list_send_as, list_drafts, get_draft
可逆写（9）：create_draft, update_draft, create_label, update_label, update_email_labels, mark_email_spam, unmark_email_spam, trash_email, untrash_email
另有 apply_sensitive_message_label / apply_sensitive_thread_label（进垃圾桶或标垃圾，可逆）= 2
不可撤回（5）：send_email, send_draft, forward（真发出）；delete_draft, delete_label（描述写明不可撤销）
合计 9+9+2+5 = 25
## Google Drive（user-Google-drive，98 个工具，按描述归类）
- 只读示例：search, search_files, list_folder, list_recent_files, read_file, read_file_content, get_file_metadata, get_file_permissions, list_comments, download_file, export_file, docs_read_document, sheets_read_range, slides_read_presentation …
- 对外影响最大：share_file（把文件授权给第三方）
- 删除：trash_file 进回收站约30天；描述写明“永久删除刻意不提供”。Sheets/Slides 的清空、删行、删标签页、删对象描述写明“立即且无法通过 API 撤销”。
- 同一搜索提示：Google Docs/Sheets/Slides 独立连接器状态 notInstalled，但 Drive 连接器本身已带 docs_/sheets_/slides_ 编辑工具。
