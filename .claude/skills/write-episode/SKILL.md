---
name: write-episode
description: エピソード番号指定で、編集・作者・担当者・読者サブエージェントを協調させて異世界ファンタジーWeb小説の1話を執筆/改稿し、再開管理、改稿ループ、品質判定、確定保存、プロット更新まで実行する。`/write-episode <話数> [--max-revisions=N]`、`第N話を書いて`、`改稿ループ込みで執筆して` などの依頼時に使用する。
---

# /write-episode — 異世界ファンタジー自動執筆スキル

## 目的

1話分の執筆ワークフローを、再開可能な状態管理付きで自動オーケストレーションする。

## 入力

- `$ARGUMENTS`: エピソード番号（必須）
- `--max-revisions=N`: リビジョン上限（任意、未指定時は `3`）

## 実行フロー（要約）

1. 再開判定を先に実行する。`workspace/progress.md` を確認し、同話再開・別話警告・破損時フォールバックを判定する。
2. Step 0 から Step 8 を順次実行する。条件分岐は `PASS / PASS_WITH_POLISH / REVISION_NEEDED / FORCE_PASS / FORCE_FAIL` に従う。
3. すべてのエージェント出力で存在確認と内容検証を実施する。不十分な場合は失敗エージェントのみ最大2回リトライする。
4. 完了時はエピソード保存、関連ログ更新、アーカイブ、チームシャットダウン、完了報告まで実行する。

## 必須ルール

- `references/workflow.md` は索引として扱い、実作業は各詳細参照ファイルに従う。
- 手順を省略しない。Step の順序・分岐条件・更新対象ファイルを変更しない。
- 再開モード時は Step 0 をスキップし、前提ファイル検証に失敗した場合のみ新規開始へフォールバックする。
- 判定ロジック（Step 6）は閾値と優先順位を厳密に維持する。
- Step 7.6 の制約を維持する（物語大筋の変更禁止、4話以上先の大幅変更禁止）。

## 参照ファイルの読み分け

- 実行前に必ず読む: `references/resume-and-progress.md`
- Step 1-3 の詳細を読む: `references/step1-3-direction-and-draft.md`
- Step 4-5 の詳細を読む: `references/step4-5-review-and-readers.md`
- Step 6 の判定詳細を読む: `references/step6-judgment.md`
- Step 6.5 の分岐詳細を読む: `references/step6.5-revision-paths.md`
- 出力検証・議論フェーズで読む: `references/discussion-and-validation.md`
- Step 7 以降で読む: `references/finalization-rules.md`
- SendMessage 文面を組み立てるときに読む: `references/prompts.md`
- Step 6 の補助計算をするときに読む: `references/scripts.md`

## 運用メモ

- 参照ファイル間で記述差分がある場合は、該当する詳細参照ファイルを優先する。
- 仕様更新時は、まず詳細参照ファイルを更新し、最後に `references/workflow.md` の索引を同期する。
