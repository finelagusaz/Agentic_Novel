# Step 4-5 仕様（担当者レビュー・読者回収）

***

## 目次

- Step 4: 担当者（レビュー）
- Step 4D: ドラフトディスカッション
- Step 5: 読者フィードバック回収


### Step 4: 担当者（レビュー）

progress.md を更新: `current_step: "step4"`, `step_status: "in_progress"`

SendMessage で **manager** に以下を指示:

**初稿の場合（revision_count == 0）**:

```
ドラフトを評価してください。

以下のファイルを読み込んでください:
- agents/manager.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針）
- workspace/current-draft.txt（評価対象のドラフト）
- story/premise.md, story/setting.md, story/characters.md
- story/writing-guide.md, story/episode-summaries.md
- story/handover-notes.md（申し送り事項、あれば）
- story/series-tracker.md（横断追跡データ — チェック#12, #17 で参照）
- workspace/revision-log.md（リビジョン履歴、あれば）

agents/manager.md の指示に従い、ドラフトを評価してください。
現在のリビジョン回数は {revision_count} / {max_revisions} です。
結果を workspace/manager-review.md に書き出してください。
完了したら報告してください。
```

**リビジョンの場合（revision_count > 0）**:

```
改稿版のドラフトを再評価してください。

以下のファイルを読み込んでください:
- agents/manager.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針）
- workspace/current-draft.txt（改稿されたドラフト）
- workspace/revision-log.md（リビジョン履歴）
- workspace/consolidated-feedback.md（前回のフィードバック統合）
- story/series-tracker.md（横断追跡データ — チェック#12, #17 で参照）

agents/manager.md の指示に従い、改稿版を評価してください。
前回のリビジョン記録と比較し、改善が見られるかも確認してください。
現在のリビジョン回数は {revision_count} / {max_revisions} です。
結果を workspace/manager-review.md に上書きしてください。
完了したら報告してください。
```

manager からの完了報告を待ち、`workspace/manager-review.md` について**共通手順: エージェント出力の検証**に従う。

progress.md を更新: step4 を `[x]`、`current_step: "step4"`, `step_status: "completed"`

***

### Step 4D: ドラフトディスカッション

**書面先行ルール**: `manager-review.md` の出力が検証済みである**後**にのみ本ステップを開始する。

progress.md を更新: `current_step: "step4d"`, `step_status: "in_progress"`

**共通手順: ディスカッション管理**に従い、以下の招待メッセージを送信する:

**author** に SendMessage:
```
担当者のレビューが出ました。workspace/manager-review.md を読んでください。
指摘事項について意図の説明が必要な場合は、manager にメッセージしてください。
※ 判定への異議ではなく、意図の説明・補足に留めてください。
特になければ『確認しました』と報告してください。
```

**editor** に SendMessage:
```
workspace/manager-review.md を読んでください。
方針との整合性について気づいた点があれば共有してください。
特になければ『確認しました』と報告してください。
```

**ディスカッション管理**:
- 全員「確認しました」→ 即 Step 5 へ
- 意見交換 → 最大2ラウンド
- **重要**: 担当者の判定は変更しない（書面先行ルール）

discussion-log.md に記録を追記し、progress.md を更新: step4d を `[x]`、`current_step: "step4d"`, `step_status: "completed"`

***

### Step 5: 読者フィードバック回収

読者は Step 3 完了時にバックグラウンドでスポーン済み。このステップでは結果の回収と検証のみを行う。

progress.md を更新: `current_step: "step5"`, `step_status: "in_progress"`

#### 通常フロー（Step 3 でスポーン済みの場合）

Step 3 で記録した各読者の Task ID を使い、TaskOutput で完了を待つ（block: true）。3名を並列で待機する。

#### 再開フォールバック（読者未スポーンの場合）

セッション再開時など、読者がスポーンされていない場合（progress.md の「Step 5 Detail」が全て `[ ]` かつ Task ID が不明な場合）は、ここで読者をスポーンする:

**再開時の部分完了対応**: progress.md の「Step 5 Detail」を確認し、
`[x]` のリーダーは出力ファイルを Glob + Read で検証する。
検証成功なら再スポーンしない。未完了 `[ ]` のリーダーのみスポーンする。

読者は **team_name なし**のサブエージェントとしてスポーンする。3名を並列で Task スポーンする。

**reader-ym** に（Task、team_name なし）:
```
workspace/current-draft.txt を読んで、ユウキとしてフィードバックを書いてください。
agents/readers/reader-young-male.md の指示に従い、
結果を workspace/reader-feedback-young-male.md に書き出してください。
完了したら報告してください。
```

**reader-af** に（Task、team_name なし）:
```
workspace/current-draft.txt を読んで、サキとしてフィードバックを書いてください。
agents/readers/reader-adult-female.md の指示に従い、
結果を workspace/reader-feedback-adult-female.md に書き出してください。
完了したら報告してください。
```

**reader-vet** に（Task、team_name なし）:
```
workspace/current-draft.txt を読んで、タツヤとしてフィードバックを書いてください。
agents/readers/reader-veteran.md と story/setting.md, story/characters.md, story/episode-summaries.md（アーク要約＋直近エピソード詳細の両方）も参照し、
さらに story/handover-notes.md と workspace/current-direction.md も参照してください（設定整合性チェック時に、既知の計画済み要素を誤検出しないため）。
結果を workspace/reader-feedback-veteran.md に書き出してください。
完了したら報告してください。
```

#### 共通: 出力検証

3名全員からの完了報告（または TaskOutput の結果）を待ち、以下の3ファイルを個別に検証する:
- `workspace/reader-feedback-young-male.md`
- `workspace/reader-feedback-adult-female.md`
- `workspace/reader-feedback-veteran.md`

各ファイルについて**共通手順: エージェント出力の検証**に従う。
失敗したエージェントのみリトライし、成功したエージェントには再指示を送らない。

各リーダーの検証成功時に progress.md の「Step 5 Detail」で該当リーダーを `[x]` に更新する。
全員の検証完了後、progress.md を更新: step5 を `[x]`、`current_step: "step5"`, `step_status: "completed"`

***

