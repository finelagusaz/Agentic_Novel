# /write-episode — 異世界ファンタジー自動執筆スキル

## 概要
マルチエージェントチームによるエピソード自動執筆オーケストレーション。

## 引数
- `$ARGUMENTS` — エピソード番号（例: `1`）。オプションで `--max-revisions=N`（デフォルト3）

## 実行手順

引数からエピソード番号を取得してください。`--max-revisions=N` が指定されていればその値を、なければ3をリビジョン上限とします。

以下の全ステップを**自動的に**順次実行してください。各ステップの実行にはTask toolのsubagentを使います。

---

### Step 0: 初期化

1. workspace/ 内のファイルをすべて削除（クリーンな状態にする）
2. `workspace/revision-log.md` を作成（空テンプレート）:
   ```
   # リビジョン履歴 — 第{番号}話
   ```
3. 前話のエピソード（episodes/ 内）が存在するか確認
4. revision_count = 0 として初期化

---

### Step 1: 編集エージェント（方針策定）

Task toolで `subagent_type: "general-purpose"` のエージェントを起動し、以下を指示:

```
あなたは異世界ファンタジーWeb小説の編集者です。

以下のファイルをすべて読み込んでください:
- agents/editor.md（あなたの役割定義）
- story/premise.md
- story/setting.md
- story/characters.md
- story/plot-outline.md
- story/writing-guide.md
- story/episode-summaries.md
- 前話のエピソード（あれば episodes/ から最新のもの）

agents/editor.md の指示に従い、第{番号}話の創作方針を策定してください。
結果を workspace/current-direction.md に書き出してください。
```

完了後、`workspace/current-direction.md` が生成されたことを確認。

---

### Step 2: 作者エージェント（執筆 / 改稿）

Task toolで `subagent_type: "general-purpose"` のエージェントを起動し、以下を指示:

初稿の場合:
```
あなたは異世界ファンタジーWeb小説の作者です。

以下のファイルをすべて読み込んでください:
- agents/author.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針 — 最優先）
- story/premise.md
- story/setting.md
- story/characters.md
- story/writing-guide.md
- story/episode-summaries.md
- 前話のエピソード（あれば episodes/ から最新のもの）

agents/author.md の指示に従い、第{番号}話を執筆してください。
結果を workspace/current-draft.txt に書き出してください。
本文のみを出力し、メタ情報やコメントは含めないでください。
```

リビジョンの場合（revision_count > 0）:
```
あなたは異世界ファンタジーWeb小説の作者です。改稿を行います。

以下のファイルをすべて読み込んでください:
- agents/author.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針）
- workspace/current-draft.txt（前回のドラフト）
- workspace/manager-review.md（担当者レビュー — 最優先で反映）
- workspace/reader-feedback-young-male.md
- workspace/reader-feedback-adult-female.md
- workspace/reader-feedback-veteran.md
- workspace/revision-log.md
- story/premise.md
- story/setting.md
- story/characters.md
- story/writing-guide.md

担当者レビューの指摘を最優先に、読者フィードバックも参考にして改稿してください。
結果を workspace/current-draft.txt に上書きしてください。
本文のみを出力し、メタ情報やコメントは含めないでください。
```

完了後、`workspace/current-draft.txt` が生成されたことを確認。

---

### Step 3: 担当者エージェント（レビュー）

Task toolで `subagent_type: "general-purpose"` のエージェントを起動し、以下を指示:

```
あなたは異世界ファンタジーWeb小説の担当編集者です。

以下のファイルをすべて読み込んでください:
- agents/manager.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針）
- workspace/current-draft.txt（評価対象のドラフト）
- story/premise.md
- story/setting.md
- story/characters.md
- story/writing-guide.md
- story/episode-summaries.md
- workspace/revision-log.md（リビジョン履歴、あれば）

agents/manager.md の指示に従い、ドラフトを評価してください。
現在のリビジョン回数は {revision_count} / {max_revisions} です。
結果を workspace/manager-review.md に書き出してください。
```

完了後、`workspace/manager-review.md` を読んで判定（OK / REVISION_NEEDED / MAJOR_REVISION）を取得。

---

### Step 4: 読者エージェント×3（並列フィードバック）

**3つのTask toolを同時に起動**（並列実行）:

**ユウキ**（subagent_type: "general-purpose"）:
```
あなたは異世界ファンタジーWeb小説の読者「ユウキ」です。

以下のファイルを読み込んでください:
- agents/readers/reader-young-male.md（あなたのプロフィールと役割）
- workspace/current-draft.txt（評価対象）

reader-young-male.md の指示に従い、ユウキとしてフィードバックを書いてください。
結果を workspace/reader-feedback-young-male.md に書き出してください。
```

**サキ**（subagent_type: "general-purpose"）:
```
あなたは異世界ファンタジーWeb小説の読者「サキ」です。

以下のファイルを読み込んでください:
- agents/readers/reader-adult-female.md（あなたのプロフィールと役割）
- workspace/current-draft.txt（評価対象）

reader-adult-female.md の指示に従い、サキとしてフィードバックを書いてください。
結果を workspace/reader-feedback-adult-female.md に書き出してください。
```

**タツヤ**（subagent_type: "general-purpose"）:
```
あなたは異世界ファンタジーWeb小説の読者「タツヤ」です。

以下のファイルを読み込んでください:
- agents/readers/reader-veteran.md（あなたのプロフィールと役割）
- workspace/current-draft.txt（評価対象）
- story/setting.md（整合性チェック用）
- story/characters.md（整合性チェック用）
- story/episode-summaries.md（連続性チェック用）

reader-veteran.md の指示に従い、タツヤとしてフィードバックを書いてください。
結果を workspace/reader-feedback-veteran.md に書き出してください。
```

---

### Step 5: 判定

1. `workspace/manager-review.md` から判定を読み取る
2. `workspace/reader-feedback-*.md` から各読者の★評価を読み取り、平均を算出
3. 判定ロジック:
   - **Manager判定が OK** かつ **読者平均★ ≥ 3.5** → **PASS**（Step 6へ）
   - **Manager判定が OK** だが **読者平均★ < 3.5** → **REVISION_NEEDED**
   - **Manager判定が REVISION_NEEDED** または **MAJOR_REVISION** → **REVISION_NEEDED**
   - **revision_count ≥ max_revisions** → **FORCE_PASS**（Step 6へ、警告付き）

4. REVISION_NEEDED の場合:
   - revision_count を +1
   - `workspace/revision-log.md` にリビジョン記録を追記:
     ```
     ## リビジョン {回数}
     - Manager判定: {判定}
     - 読者平均★: {平均}
     - 主な指摘: {要約}
     ```
   - 現在のドラフトを `archive/episode-{番号}/draft-v{回数}.txt` にバックアップ
   - **Step 2 に戻る**

5. 判定結果とステータスをユーザーに表示する

---

### Step 6: 確定・保存

1. エピソードタイトルを `workspace/current-direction.md` から取得
2. `workspace/current-draft.txt` を `episodes/{番号:2桁}_{タイトル}.txt` にコピー
3. `story/episode-summaries.md` にあらすじを追記（100〜150字）
4. workspace/ の全ファイルを `archive/episode-{番号:2桁}/` にコピー
5. workspace/ をクリーン

---

### 完了報告

以下の情報をユーザーに報告:
- エピソードタイトル
- 保存先ファイルパス
- リビジョン回数
- 最終の担当者判定
- 読者評価（3名分の★と平均）
- FORCE_PASS の場合は警告メッセージ
