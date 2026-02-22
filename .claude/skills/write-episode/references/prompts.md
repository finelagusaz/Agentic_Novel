# エージェント指示テンプレート集（write-episode）

このファイルは、Step 実行中に再利用する送信文テンプレートをまとめる。
詳細な完全版は `references/workflow.md` の各 Step を正本とする。

## 使用ルール

- まず `references/workflow.md` で対象 Step の必須入力ファイルと完了条件を確認する。
- その後、このテンプレートを話数・判定値・ファイル名で具体化して送信する。
- テンプレートと `workflow.md` に差分がある場合、`workflow.md` を優先する。

## editor への方針策定依頼（Step 2）

```text
第{番号}話の創作方針を策定してください。

以下のファイルを読み込んでください:
- agents/editor.md
- story/series-tracker.md
- story/premise.md, story/setting.md, story/characters.md
- story/plot-outline.md, story/writing-guide.md
- story/episode-summaries.md
- story/handover-notes.md（存在する場合）
- 前話のエピソード（存在する場合）

結果を workspace/current-direction.md に書き出してください。
完了したら報告してください。
```

## author への初稿依頼（Step 3, revision_count == 0）

```text
第{番号}話を執筆してください。

以下のファイルを読み込んでください:
- agents/author.md
- workspace/current-direction.md
- story/premise.md, story/setting.md, story/characters.md
- story/writing-guide.md
- story/episode-summaries.md（直近詳細）
- 前話のエピソード（存在する場合）

結果を workspace/current-draft.txt に書き出してください。
本文のみを出力し、メタ情報やコメントは含めないでください。
完了したら報告してください。
```

## author への改稿依頼（Step 3, revision_count > 0）

```text
改稿を行ってください。

以下のファイルを読み込んでください:
- agents/author.md
- workspace/current-direction.md
- workspace/current-draft.txt
- workspace/consolidated-feedback.md
- workspace/revision-log.md

workspace/consolidated-feedback.md の指示に従って改稿し、
workspace/current-draft.txt を上書きしてください。
完了したら報告してください。
```

## manager へのレビュー依頼（Step 4）

```text
ドラフトを評価してください。

以下のファイルを読み込んでください:
- agents/manager.md
- workspace/current-direction.md
- workspace/current-draft.txt
- story/premise.md, story/setting.md, story/characters.md
- story/writing-guide.md, story/episode-summaries.md
- story/handover-notes.md（存在する場合）
- story/series-tracker.md
- workspace/revision-log.md

結果を workspace/manager-review.md に書き出してください。
現在のリビジョン回数は {revision_count} / {max_revisions} です。
完了したら報告してください。
```

## 再出力依頼（共通リトライ）

```text
{期待ファイル} が確認できません。ファイルを生成して報告してください。
```

## ディスカッション招待の共通末尾

```text
特に意見がなければ「問題ありません」と報告してください。
```

## ディスカッション終了通知（共通）

```text
ディスカッション終了。現在の方針/判定で進めます。
```
