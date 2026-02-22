# 再開・進捗管理仕様（write-episode）

再開判定、progress.md フォーマット、初期化に関する詳細仕様。実行前に必ず参照する。

***

## 引数

- `$ARGUMENTS` — エピソード番号（例: `1`）。オプションで `--max-revisions=N`（デフォルト3）

## 再開（レジュメ）ロジック

実行手順の**最初のアクション**として、以下の再開チェックを行う:

1. `workspace/progress.md` を Glob で検索する
2. **ファイルが存在しない場合**: 通常の新規開始（Step 0 へ）
3. **ファイルが存在する場合**: Read で読み込み、YAML ブロックから `episode` と `current_step` を確認:
   a. **episode が引数と一致する場合 → 再開モード**
      - ユーザーに「既存の進捗を検出しました。第{N}話の {current_step} から再開します」と表示
      - Step 0 を**スキップ**（workspace のクリーンを行わない）
      - Step 1（チーム作成 + コアメンバースポーン）は**必ず実行**（チームはセッション間で維持されない）
      - `current_step` と `step_status` から再開地点を決定:
        - `step_status` が `completed` → 次のステップから再開
        - `step_status` が `in_progress` → そのステップを再実行（Step 5 は部分完了を考慮）
      - ディスカッションステップ（step2d, step4d）は状態が非永続。中断時はディスカッション全体を再実行
      - 再開前に、再開先ステップの前提ファイルが存在・有効か Glob + Read で検証する。欠落時はユーザーに警告し新規開始にフォールバック
      - `revision_count` を progress.md の値で復元
   b. **episode が引数と異なる場合 → 警告モード**
      - ユーザーに確認: 「workspace に第{M}話の進捗が残っています。第{N}話を開始すると失われます。続行しますか？」
      - 承認 → 通常の新規開始（Step 0 へ）/ 拒否 → 中断
4. **progress.md の形式が不正な場合**: ユーザーに警告し、新規開始にフォールバック

### 前提ファイル一覧（再開時の検証用）

| 再開先 | 必須ファイル |
|-------|------------|
| Step 2 | （なし） |
| Step 2D | `current-direction.md` |
| Step 3 | `current-direction.md`。revision_count > 0 の場合は `consolidated-feedback.md` も |
| Step 4 | `current-direction.md`, `current-draft.txt` |
| Step 4D | `current-direction.md`, `current-draft.txt`, `manager-review.md` |
| Step 5 | `current-draft.txt` |
| Step 6 | `manager-review.md`, `reader-feedback-young-male.md`, `reader-feedback-adult-female.md`, `reader-feedback-veteran.md` |
| Step 6.5P | `current-draft.txt` |
| Step 6.5D | Step 6 と同じ + `current-direction.md`, `current-draft.txt` |
| Step 7 | `current-draft.txt`, `current-direction.md` |
| Step 7.6 | `story/plot-outline.md`, `story/handover-notes.md`, `story/episode-summaries.md` |

## 実行手順

引数からエピソード番号を取得してください。`--max-revisions=N` が指定されていればその値を、なければ3をリビジョン上限とします。

以下の全ステップを**自動的に**順次実行してください。

***

### Step 0: 初期化

**このステップは再開モードではスキップされる（「再開ロジック」参照）。**

1. Glob ツールで `workspace/*.md` と `workspace/*.txt` を検索し、ファイルが存在する場合のみ `rm -f` で削除する（zsh のグロブエラーを回避するため、ファイルが存在しない場合はスキップする）
2. `workspace/revision-log.md` を作成（空テンプレート）:
   ```
   # リビジョン履歴 — 第{番号}話
   ```
3. `workspace/discussion-log.md` を作成（空テンプレート）:
   ```
   # ディスカッションログ — 第{番号}話
   ```
4. **`workspace/progress.md` を作成**（後述のフォーマットに従い初期テンプレートを出力）
5. `mkdir -p archive/episode-{番号:2桁}` でアーカイブディレクトリを事前作成する
6. 前話のエピソード（episodes/ 内）が存在するか確認
7. revision_count = 0 として初期化
8. `story/handover-notes.md` を読み込み、`[DEFERRED:ep{今回の番号}]` のタグが付いた項目を `[ACTIVE]` に昇格する（該当項目がなければスキップ）
9. **progress.md を更新**: `current_step: "step0"`, `step_status: "completed"`, step0 を `[x]` に

***

### progress.md のフォーマット

Step 0 で以下の内容で `workspace/progress.md` を作成する:

```
# Progress Tracker — Episode {番号:2桁}

```yaml
episode: {番号}
max_revisions: {上限}
revision_count: 0
current_step: "step0"
step_status: "completed"
```

## Completed Steps

- [x] step0: Initialize
- [ ] step1: Create Team + Spawn Core
- [ ] step2: Editor Direction
- [ ] step2d: Direction Discussion
- [ ] step3: Author Draft
- [ ] step4: Manager Review
- [ ] step4d: Draft Discussion
- [ ] step5: Reader Feedback (Collect)
- [ ] step6: Judgment
- [ ] step6.5p: Polish (conditional)
- [ ] step7: Finalize
- [ ] step7.6: Plot Update Discussion
- [ ] step8: Team Shutdown

## Step 5 Detail

- [ ] reader-ym
- [ ] reader-af
- [ ] reader-vet

## Revision History

（なし）
```

***

