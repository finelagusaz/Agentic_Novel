# 異世界ファンタジーWeb小説 マルチエージェント執筆システム

## プロジェクト概要

異世界ファンタジーのWeb小説を、Claude Codeのsubagent機能（Task tool）を活用したマルチエージェントチームで自動執筆するシステム。「編集」「作者」「担当者」「想定読者」の4種のエージェントが対話的に協力し、1コマンドで1エピソード（1500〜4000字、標準2000〜3000字）を自動的に執筆・レビュー・改稿する。リビジョン上限到達時は品質ゲートを適用し、最低基準未達の場合はユーザーに手動介入を求める。

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
│   ├── discussion-log.md             # ディスカッション記録（実行中のみ存在）
│   └── progress.md                    # 進捗トラッカー（実行中のみ存在）
└── archive/                           # 過去ドラフト保存
    └── episode-XX/
```

## エージェント構成

コアメンバー（編集・作者・担当者）はチームメンバーとしてスポーンされ、SendMessageによる議論が可能。読者はサブエージェント（独立Task）で生の読者反応を提供する。

| エージェント | ファイル | 方式 | 役割 |
|-------------|---------|------|------|
| **編集** | `agents/editor.md` | チームメンバー（Opus） | 全体プロット・設定を踏まえ、各話の創作方針を決定 |
| **作者** | `agents/author.md` | チームメンバー（Opus） | 編集の方針に従い本文を執筆・改稿 |
| **担当者** | `agents/manager.md` | チームメンバー（Sonnet） | ドラフトの品質評価と判定 |
| **読者×3** | `agents/readers/*.md` | サブエージェント | 3ペルソナ視点で感想と★評価 |

### モデル非対称性への対策

担当者（Sonnet）が作者（Opus）に議論で「言い負かされる」リスクを以下で防止:
- **書面先行ルール**: 担当者は `manager-review.md` を書き切ってから議論に参加する
- **判定不変の原則**: 書面に記載した判定は議論で変更しない
- **議論の非対称制限**: 作者→担当者は「意図の説明」のみ許可。「判定への異議」は禁止

## ワークフロー

`/write-episode <番号>` で起動。`SKILL.md` と同じステップ体系（0〜8 + 補助ステップ）で実行される。

1. **Step 0 初期化 / 再開判定**: progress.md をチェック。新規なら workspace をクリーン、再開なら中断地点から継続
2. **Step 1 チーム作成 + コアメンバー一斉スポーン**: 編集・作者・担当者をチームメンバーとしてスポーン
3. **Step 2 編集（方針策定）**: current-direction.md を出力（`series-tracker.md` を冒頭参照）
4. **Step 2D 方針ディスカッション**: 作者・担当者が方針に意見があれば議論（なければ即時合意）
5. **Step 3 作者（執筆/改稿）**: current-draft.txt を出力 → 読者3名をバックグラウンドスポーン
6. **Step 4 担当者（レビュー）**: manager-review.md を出力（読者は並行してフィードバック生成）
7. **Step 4D ドラフトディスカッション**: 作者・編集がレビュー所見をすり合わせ（必要時のみ）
8. **Step 5 読者フィードバック回収**: バックグラウンドスポーン済みの読者結果を回収・検証
9. **Step 6 判定**: OK かつ 読者平均★≥3.5 なら PASS。要修正なら Step 6.5D（最大3回）
10. **Step 6.5P ポリッシュ（条件付き）**: PASSだが軽微な共通指摘ありの場合のみ部分修正
11. **Step 6.5D リビジョンディスカッション（条件付き）**: 三者で改稿方針を議論し Step 3 へ戻る
12. **Step 7 確定・保存**: episodes/ 保存、episode-summaries/quality-log/series-tracker 更新、archive 退避
13. **Step 7.5 申し送り事項更新**: editor が `story/handover-notes.md` を更新
14. **Step 7.6 プロット更新ディスカッション**: editor と manager が `plot-outline.md` 更新要否を検討
15. **Step 8 チームシャットダウン**: 全メンバーに shutdown_request → TeamDelete

### series-tracker の運用サイクル

1. **参照（Step 2）**: editor が方針策定の冒頭で `story/series-tracker.md` を確認し、警告対応を `current-direction.md` に反映
2. **検証（Step 4）**: manager が tracker の制約（構造多様性・登場密度）に照らしてドラフトを評価
3. **更新（Step 7）**: リーダーが確定本文を基に tracker の全テーブルをスライド更新
4. **引き継ぎ（次話 Step 2）**: 更新済み tracker を次話方針の入力に再利用

## ルール

- コアメンバー間の通信は SendMessage による直接メッセージで行う
- 成果物（方針・ドラフト・レビュー等）は workspace/ 内のファイルとして出力する
- 各エージェントは自分のプロンプトファイル（agents/*.md）に定義された役割に忠実に従う
- story/ 内のファイルは全エージェントが参照する共有設定
- リビジョンは最大3回（`--max-revisions=N` で変更可能）
- エピソードの文字数: 編集が方針策定時にエピソードタイプ（A: 重要回 3000〜4000字 / B: 標準回 2000〜3000字 / C: つなぎ回 1500〜2000字）を指定。未指定時はB
- 読者フィードバックはサブエージェントの並列実行で効率化する
- ディスカッションは自然発生型: 意見がある場合のみ議論、なければ即進行
- ディスカッションの知見は成果物への【〇〇ディスカッション反映】注記と `workspace/discussion-log.md` に記録

## 中断復帰（レジュメ）

セッション中断（レート制限、クラッシュ等）に対する復帰機能:

- `/write-episode N` 実行中、進捗は `workspace/progress.md` に逐次記録される
- セッション中断後に同じ `/write-episode N` を実行すると、自動的に中断地点から再開する
- エピソード番号が異なる progress.md が残っている場合はユーザーに確認を求める
- エピソード確定時（Step 7）に progress.md はアーカイブ後に自動削除される
- チームはセッション間で維持されないため、再開時も Step 2（チーム作成）は必ず実行される
- 手動で `workspace/progress.md` を削除すると強制的に新規開始できる
