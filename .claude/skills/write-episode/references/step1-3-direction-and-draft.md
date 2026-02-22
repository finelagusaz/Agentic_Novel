# Step 1-3 仕様（チーム作成・方針策定・執筆）

***

## 目次

- Step 1: チーム作成 + コアメンバースポーン
- Step 2: 編集（方針策定）
- Step 2D: 方針ディスカッション
- Step 3: 作者（執筆 / 改稿）


### Step 1: チーム作成 + コアメンバースポーン

TeamCreate で `"novel-ep{番号}"` という名前のチームを作成する。

**コアチームメンバー**を一斉にスポーンする（team_name 指定あり）。3名を並列で Task スポーンする。

| チームメイト | subagent_type | name | model | スポーンタイミング |
|------------|---------------|------|-------|--------------------|
| 編集 | novel-editor | editor | opus | Step 1（一斉スポーン） |
| 作者 | novel-author | author | opus | Step 1（一斉スポーン） |
| 担当者 | novel-manager | manager | sonnet | Step 1（一斉スポーン） |

各メンバーの Task prompt:
```
あなたは第{番号}話の執筆チームの{役割}です。
agents/{ファイル}.md を読み込み、チームリーダーからの指示を待ってください。
```

**読者**は Step 3 完了直後にバックグラウンドでスポーンする（team_name **なし**のサブエージェント）。Step 4/4D と並行してフィードバックを生成し、Step 5 で結果を回収する。

| チームメイト | subagent_type | name | スポーンタイミング |
|------------|---------------|------|------------------|
| ユウキ | novel-reader-ym | reader-ym | Step 3 完了直後（バックグラウンド） |
| サキ | novel-reader-af | reader-af | Step 3 完了直後（バックグラウンド） |
| タツヤ | novel-reader-vet | reader-vet | Step 3 完了直後（バックグラウンド） |

progress.md を更新: step1 を `[x]`、`current_step: "step1"`, `step_status: "completed"`

***

### Step 2: 編集（方針策定）

progress.md を更新: `current_step: "step2"`, `step_status: "in_progress"`

SendMessage で **editor** に以下を指示:

```
第{番号}話の創作方針を策定してください。

以下のファイルを読み込んでください:
- agents/editor.md（あなたの役割定義）
- story/series-tracker.md（横断追跡データ — 最初に読み、警告事項を確認してから方針を組み立てること）
- story/premise.md, story/setting.md, story/characters.md
- story/plot-outline.md, story/writing-guide.md
- story/episode-summaries.md
- story/handover-notes.md（前話からの申し送り事項。存在する場合）
- 前話のエピソード（あれば episodes/ から最新のもの）

agents/editor.md の指示に従い、結果を workspace/current-direction.md に書き出してください。
完了したら報告してください。
```

editor からの完了報告（idle通知）を待ち、`workspace/current-direction.md` について**共通手順: エージェント出力の検証**に従う。

#### 方針固有の構造検証

共通の出力検証に加え、以下の追加検証を行う:

1. `workspace/current-direction.md` を Read で読み、「## アクション配分確認」セクションが存在し、直前2話の区分が具体的に記入されているか確認する
2. 「## エピソードタイプ・文字数」セクションが存在し、A/B/C の指定があるか確認する
3. 「## 伏線・布石」セクション内に「グリモワール六行目の進捗」の記載があり、「進展あり/なし」と記入され、「あり」の場合は series-tracker.md の最終進展内容と重複しない具体的な状態変化が記載されているか確認する。また「series-tracker警告への対応」が記入されているか確認する
4. `story/series-tracker.md` を Read で読み、警告事項（「現在の警告」行）と方針の整合性を確認する。警告が出ているのに方針が対応していない場合（例: 未進展2話以上の要素に言及がない、キャラ登場警告が出ているのに出番が設定されていない）、editor に不足箇所を明示して再出力を依頼する

不備がある場合: editor に不足セクションを明示して再出力を依頼する（共通手順のリトライフローに準じる）

progress.md を更新: step2 を `[x]`、`current_step: "step2"`, `step_status: "completed"`

***

### Step 2D: 方針ディスカッション

progress.md を更新: `current_step: "step2d"`, `step_status: "in_progress"`

**共通手順: ディスカッション管理**に従い、以下の招待メッセージを送信する:

**author** に SendMessage:
```
workspace/current-direction.md を読んでください。
作者として、執筆の実現可能性や構成について意見はありますか？
特に気になる点があれば editor にメッセージしてください。
特になければ『方針了解』と報告してください。
```

**manager** に SendMessage:
```
workspace/current-direction.md を読んでください。
品質・設定整合性の観点から、事前に懸念される点はありますか？
特に気になる点があれば editor にメッセージしてください。
特になければ『問題なし』と報告してください。
```

**ディスカッション管理**:
- 全員「問題なし」系 → 即 Step 3 へ
- 意見あり → エージェント間の直接メッセージを許容（**最大2ラウンド**）
- 打ち切り: 「方針を確定します。次のステップに進みます。」
- editor が direction を更新した場合、出力を検証する

discussion-log.md に記録を追記し、progress.md を更新: step2d を `[x]`、`current_step: "step2d"`, `step_status: "completed"`

***

### Step 3: 作者（執筆 / 改稿）

progress.md を更新: `current_step: "step3"`, `step_status: "in_progress"`

**初稿の場合（revision_count == 0）** — SendMessage で **author** に以下を指示:

```
第{番号}話を執筆してください。

以下のファイルを読み込んでください:
- agents/author.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針 — 最優先）
- story/premise.md, story/setting.md, story/characters.md
- story/writing-guide.md, story/episode-summaries.md（「直近エピソード詳細」セクションのみ）
- 前話のエピソード（あれば episodes/ から最新のもの）

agents/author.md の指示に従い、第{番号}話を執筆してください。
結果を workspace/current-draft.txt に書き出してください。
本文のみを出力し、メタ情報やコメントは含めないでください。
完了したら報告してください。
```

**リビジョンの場合（revision_count > 0）** — SendMessage で **author** に以下を指示:

```
改稿を行ってください。

以下のファイルを読み込んでください:
- agents/author.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針）
- workspace/current-draft.txt（前回のドラフト）
- workspace/consolidated-feedback.md（編集が統合したフィードバック — これが改稿の主要な指針です）
- workspace/revision-log.md

workspace/consolidated-feedback.md の指示に従って改稿してください。
結果を workspace/current-draft.txt に上書きしてください。
本文のみを出力し、メタ情報やコメントは含めないでください。
完了したら報告してください。
```

author からの完了報告を待ち、`workspace/current-draft.txt` について**共通手順: エージェント出力の検証**に従う。

progress.md を更新: step3 を `[x]`、`current_step: "step3"`, `step_status: "completed"`

#### Step 3 完了時: 読者バックグラウンドスポーン

Step 3 の出力検証が成功した直後、読者3名をバックグラウンドでスポーンする。Step 4（レビュー）/ Step 4D（議論）はドラフトを変更しないため、読者はレビュー・議論と並行して安全にフィードバックを生成できる。

読者は **team_name なし**、**run_in_background: true** のサブエージェントとしてスポーンする。3名を並列で Task スポーンする。

**reader-ym** に（Task、team_name なし、run_in_background: true）:
```
workspace/current-draft.txt を読んで、ユウキとしてフィードバックを書いてください。
agents/readers/reader-young-male.md の指示に従い、
結果を workspace/reader-feedback-young-male.md に書き出してください。
完了したら報告してください。
```

**reader-af** に（Task、team_name なし、run_in_background: true）:
```
workspace/current-draft.txt を読んで、サキとしてフィードバックを書いてください。
agents/readers/reader-adult-female.md の指示に従い、
結果を workspace/reader-feedback-adult-female.md に書き出してください。
完了したら報告してください。
```

**reader-vet** に（Task、team_name なし、run_in_background: true）:
```
workspace/current-draft.txt を読んで、タツヤとしてフィードバックを書いてください。
agents/readers/reader-veteran.md と story/setting.md, story/characters.md, story/episode-summaries.md（アーク要約＋直近エピソード詳細の両方）も参照し、
さらに story/handover-notes.md と workspace/current-direction.md も参照してください（設定整合性チェック時に、既知の計画済み要素を誤検出しないため）。
結果を workspace/reader-feedback-veteran.md に書き出してください。
完了したら報告してください。
```

progress.md の「Step 5 Detail」を初期化（全リーダーを `[ ]` に設定）。各読者の Task ID を記録しておく（Step 5 での回収に使用）。

***

