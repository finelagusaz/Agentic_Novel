# 異世界ファンタジーWeb小説 マルチエージェント執筆システム

## プロジェクト概要

異世界ファンタジーのWeb小説を、Claude Codeのsubagent機能（Task tool）を活用したマルチエージェントチームで自動執筆するシステム。「編集」「作者」「担当者」「想定読者」の4種のエージェントが対話的に協力し、1コマンドで1エピソード（2000〜3000字）を品質基準を満たすまで自動的に執筆・レビュー・改稿する。

## ディレクトリ構成

```
Agentic_Novel/
├── CLAUDE.md                          # このファイル
├── .claude/skills/write-episode/
│   └── SKILL.md                       # /write-episode スキル
├── agents/
│   ├── editor.md                      # 編集エージェント
│   ├── author.md                      # 作者エージェント
│   ├── manager.md                     # 担当者エージェント
│   └── readers/
│       ├── reader-young-male.md       # ユウキ（17歳男性）
│       ├── reader-adult-female.md     # サキ（28歳女性）
│       └── reader-veteran.md          # タツヤ（35歳ベテラン）
├── story/
│   ├── premise.md                     # 作品コンセプト・あらすじ
│   ├── setting.md                     # 世界観設定
│   ├── characters.md                  # 登録人物
│   ├── plot-outline.md                # 全体プロット
│   ├── episode-summaries.md           # 各話あらすじ蓄積
│   ├── writing-guide.md              # 文体・記法ガイド
│   ├── handover-notes.md             # 次話への申し送り事項
│   └── quality-log.md                # 品質トレンド記録
├── episodes/                          # 確定エピソード（.txt）
├── workspace/                         # エージェント間の作業領域
│   ├── current-direction.md           # 編集の方針
│   ├── current-draft.txt              # 作者のドラフト
│   ├── manager-review.md             # 担当者レビュー
│   ├── reader-feedback-young-male.md
│   ├── reader-feedback-adult-female.md
│   ├── reader-feedback-veteran.md
│   ├── consolidated-feedback.md      # 編集が統合したフィードバック（リビジョン時）
│   ├── revision-log.md               # リビジョン履歴
│   └── progress.md                    # 進捗トラッカー（実行中のみ存在）
└── archive/                           # 過去ドラフト保存
    └── episode-XX/
```

## エージェント構成

| エージェント | ファイル | 役割 |
|-------------|---------|------|
| **編集** | `agents/editor.md` | 全体プロット・設定を踏まえ、各話の創作方針を決定 |
| **作者** | `agents/author.md` | 編集の方針に従い本文を執筆・改稿 |
| **担当者** | `agents/manager.md` | ドラフトの品質評価と判定 |
| **読者×3** | `agents/readers/*.md` | 3ペルソナ視点で感想と★評価 |

## ワークフロー

`/write-episode <番号>` で起動。全ステップ自動実行。

1. **初期化 / 再開判定**: progress.md をチェック。新規なら workspace をクリーン、再開なら中断地点から継続
2. **編集（方針策定）**: current-direction.md を出力
3. **作者（執筆/改稿）**: current-draft.txt を出力
4. **担当者（レビュー）**: manager-review.md を出力
5. **読者×3（並列フィードバック）**: reader-feedback-*.md を出力
6. **判定**: OK かつ 読者平均★≥3.5 → 確定 / 要修正 → Step 6.5 へ（最大3回）
   - **6.5 編集（フィードバック統合）**: consolidated-feedback.md を出力 → Step 3 に戻る
7. **確定・保存**: episodes/ に保存、episode-summaries.md に追記、archive/ にアーカイブ

## ルール

- エージェント間の通信はすべて workspace/ 内のファイル経由で行う
- 各エージェントは自分のプロンプトファイル（agents/*.md）に定義された役割に忠実に従う
- story/ 内のファイルは全エージェントが参照する共有設定
- リビジョンは最大3回（`--max-revisions=N` で変更可能）
- エピソードの文字数目安: 2000〜3000字
- 読者フィードバックは並列実行で効率化する

## 中断復帰（レジュメ）

セッション中断（レート制限、クラッシュ等）に対する復帰機能:

- `/write-episode N` 実行中、進捗は `workspace/progress.md` に逐次記録される
- セッション中断後に同じ `/write-episode N` を実行すると、自動的に中断地点から再開する
- エピソード番号が異なる progress.md が残っている場合はユーザーに確認を求める
- エピソード確定時（Step 7）に progress.md はアーカイブ後に自動削除される
- チームはセッション間で維持されないため、再開時も Step 1（チーム作成）は必ず実行される
- 手動で `workspace/progress.md` を削除すると強制的に新規開始できる
