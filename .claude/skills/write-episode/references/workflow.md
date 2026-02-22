# ワークフロー索引（write-episode）

このファイルは導線専用の索引。詳細仕様は下記の参照ファイルを読む。

## 読み順

1. `references/resume-and-progress.md`
2. `references/step1-3-direction-and-draft.md`
3. `references/step4-5-review-and-readers.md`
4. `references/step6-judgment.md`
5. `references/step6.5-revision-paths.md`
6. `references/discussion-and-validation.md`
7. `references/finalization-rules.md`
8. `references/prompts.md`
9. `references/scripts.md`

## ステート遷移（要約）

- Start -> Resume判定
- Resume判定 -> Step 0 または Step 1
- Step 1 -> Step 2 -> Step 2D -> Step 3 -> Step 4 -> Step 4D -> Step 5 -> Step 6
- Step 6 (PASS) -> Step 7
- Step 6 (PASS_WITH_POLISH) -> Step 6.5P -> Step 7
- Step 6 (REVISION_NEEDED) -> Step 6.5D -> Step 3
- Step 6 (FORCE_PASS) -> Step 7
- Step 6 (FORCE_FAIL) -> 中断（チーム終了のみ）
- Step 7 -> Step 7.5 -> Step 7.6 -> Step 8 -> 完了報告

## 分岐判定の正本

- 判定条件と閾値は `references/step6-judgment.md` を正本とする。
- Step 6 の補助計算（メタ検出・読者評価集計）は `references/scripts.md` のスクリプト利用を優先する。

## 変更ポリシー

- 仕様更新は、まず該当する詳細参照ファイルを更新し、その後この索引を同期する。
- 参照ファイル間で不整合があれば、各詳細ファイルを正とし、本索引は導線のみ維持する。
