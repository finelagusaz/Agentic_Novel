---
name: write-episode
description: マルチエージェントチームで異世界ファンタジーWeb小説のエピソードを自動執筆する。引数にエピソード番号を指定（例: /write-episode 1）
---

# /write-episode — 異世界ファンタジー自動執筆スキル

## 概要

エージェントチーム機能を活用し、tmux 分割ペインで各エージェントが独立して動作するエピソード自動執筆オーケストレーション。

## 引数

- `$ARGUMENTS` — エピソード番号（例: `1`）。オプションで `--max-revisions=N`（デフォルト3）

## 実行手順

引数からエピソード番号を取得してください。`--max-revisions=N` が指定されていればその値を、なければ3をリビジョン上限とします。

以下の全ステップを**自動的に**順次実行してください。

***

### Step 0: 初期化

1. workspace/ 内のファイルをすべて削除（クリーンな状態にする）
2. `workspace/revision-log.md` を作成（空テンプレート）:
   ```
   # リビジョン履歴 — 第{番号}話
   ```
3. 前話のエピソード（episodes/ 内）が存在するか確認
4. revision_count = 0 として初期化

***

### Step 1: チーム作成

TeamCreate で `"novel-ep{番号}"` という名前のチームを作成する。

チームメイトは以下の6名だが、**必要になった時点で段階的にスポーン**する（遅延スポーン方式）。
一斉にスポーンしないこと。各ステップの冒頭でスポーンし、即座に作業指示を送る。

| チームメイト | subagent_type | name | スポーンタイミング |
|------------|---------------|------|------------------|
| 編集 | novel-editor | editor | Step 2 開始時 |
| 作者 | novel-author | author | Step 3 開始時 |
| 担当者 | novel-manager | manager | Step 4 開始時 |
| ユウキ | novel-reader-ym | reader-ym | Step 5 開始時 |
| サキ | novel-reader-af | reader-af | Step 5 開始時 |
| タツヤ | novel-reader-vet | reader-vet | Step 5 開始時 |

各チームメイトのスポーン時プロンプトは以下のようにする:

```
あなたはエージェントチームの一員です。
【重要】リーダーから具体的な作業指示が届くまで、workspace/ のファイルを読んだり作業を開始しないでください。
指示が届いたら、まず自分のエージェント定義ファイルを読み、その役割に従って作業してください。
作業が完了したら、結果を workspace/ に書き出し、リーダーに完了を報告してください。
```

***

### Step 2: 編集（方針策定）

**editor をスポーン**（まだスポーンしていない場合）し、即座に以下を指示する。
SendMessage で **editor** に以下を指示:

```
第{番号}話の創作方針を策定してください。

以下のファイルを読み込んでください:
- agents/editor.md（あなたの役割定義）
- story/premise.md, story/setting.md, story/characters.md
- story/plot-outline.md, story/writing-guide.md
- story/episode-summaries.md
- 前話のエピソード（あれば episodes/ から最新のもの）

agents/editor.md の指示に従い、結果を workspace/current-direction.md に書き出してください。
完了したら報告してください。
```

editor からの完了報告（idle通知）を待ち、`workspace/current-direction.md` が生成されたことを確認。

***

### Step 3: 作者（執筆 / 改稿）

**author をスポーン**（まだスポーンしていない場合）し、即座に以下を指示する。

**初稿の場合** — SendMessage で **author** に以下を指示:

```
第{番号}話を執筆してください。

以下のファイルを読み込んでください:
- agents/author.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針 — 最優先）
- story/premise.md, story/setting.md, story/characters.md
- story/writing-guide.md, story/episode-summaries.md
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

author からの完了報告を待ち、`workspace/current-draft.txt` が生成されたことを確認。

***

### Step 4: 担当者（レビュー）

**manager をスポーン**（まだスポーンしていない場合）し、即座に以下を指示する。
SendMessage で **manager** に以下を指示:

```
ドラフトを評価してください。

以下のファイルを読み込んでください:
- agents/manager.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針）
- workspace/current-draft.txt（評価対象のドラフト）
- story/premise.md, story/setting.md, story/characters.md
- story/writing-guide.md, story/episode-summaries.md
- workspace/revision-log.md（リビジョン履歴、あれば）

agents/manager.md の指示に従い、ドラフトを評価してください。
現在のリビジョン回数は {revision_count} / {max_revisions} です。
結果を workspace/manager-review.md に書き出してください。
完了したら報告してください。
```

manager からの完了報告を待つ。

***

### Step 5: 読者×3（並列フィードバック）

**reader-ym, reader-af, reader-vet を同時にスポーン**（まだスポーンしていない場合）し、スポーン完了後に即座に以下を指示する。
以下の **3名に同時に** SendMessage を送る（並列実行）:

**reader-ym** に:
```
workspace/current-draft.txt を読んで、ユウキとしてフィードバックを書いてください。
agents/readers/reader-young-male.md の指示に従い、
結果を workspace/reader-feedback-young-male.md に書き出してください。
完了したら報告してください。
```

**reader-af** に:
```
workspace/current-draft.txt を読んで、サキとしてフィードバックを書いてください。
agents/readers/reader-adult-female.md の指示に従い、
結果を workspace/reader-feedback-adult-female.md に書き出してください。
完了したら報告してください。
```

**reader-vet** に:
```
workspace/current-draft.txt を読んで、タツヤとしてフィードバックを書いてください。
agents/readers/reader-veteran.md と story/setting.md, story/characters.md, story/episode-summaries.md も参照し、
結果を workspace/reader-feedback-veteran.md に書き出してください。
完了したら報告してください。
```

3名全員からの完了報告を待つ。

***

### Step 6: 判定

リーダー（あなた自身）が以下を直接実行する:

1. `workspace/manager-review.md` を Read で読み、判定（OK / REVISION_NEEDED / MAJOR_REVISION）を確認
2. `workspace/reader-feedback-young-male.md`, `workspace/reader-feedback-adult-female.md`, `workspace/reader-feedback-veteran.md` を Read で読み、各読者の総合評価★を確認して平均を算出
3. 判定ロジック:
   - **revision_count ≥ max_revisions** → **FORCE_PASS**（Step 7へ、警告付き）
   - **Manager判定が OK** かつ **読者平均★ ≥ 3.5** → **PASS**（Step 7へ）
   - **Manager判定が OK** だが **読者平均★ < 3.5** → **REVISION_NEEDED**
   - **Manager判定が REVISION_NEEDED** または **MAJOR_REVISION** → **REVISION_NEEDED**

4. REVISION_NEEDED の場合:
   - revision_count を +1
   - `workspace/revision-log.md` にリビジョン記録を追記:
     ```
     ## リビジョン {回数}
     - Manager判定: {判定}
     - 読者平均★: {平均}
     - 主な指摘: {要約}
     ```
   - 現在のドラフトを `archive/episode-{番号:2桁}/draft-v{回数}.txt` にバックアップ
   - **Step 6.5 へ進む**

5. FORCE_PASS の場合:
   - Step 6.5 は**スキップ**し、直接 Step 7 へ進む

6. 判定結果とステータスをユーザーに表示する

***

### Step 6.5: 編集（フィードバック統合）【REVISION時のみ】

Step 6 で REVISION_NEEDED と判定された場合にのみ実行する。

SendMessage で **editor** に以下を指示:

```
リビジョンに向けたフィードバック統合を行ってください。

以下のファイルを読み込んでください:
- agents/editor.md（あなたの役割定義 — 特に「リビジョン時の対応」セクション）
- workspace/manager-review.md（担当者レビュー）
- workspace/reader-feedback-young-male.md（ユウキのフィードバック）
- workspace/reader-feedback-adult-female.md（サキのフィードバック）
- workspace/reader-feedback-veteran.md（タツヤのフィードバック）
- workspace/current-direction.md（現在の創作方針）
- workspace/current-draft.txt（現在のドラフト）

agents/editor.md の「リビジョン時の対応」セクションの指示に従い、フィードバックを統合してください。
第{番号}話、リビジョン{revision_count}回目です。

結果を workspace/consolidated-feedback.md に書き出してください。
方針の修正が必要な場合は workspace/current-direction.md も更新してください。
完了したら報告してください。
```

editor からの完了報告を待ち、`workspace/consolidated-feedback.md` が生成されたことを確認し、**Step 3 に戻る**（改稿）。

***

### Step 7: 確定・保存

リーダー（あなた自身）が直接実行する:

1. エピソードタイトルを `workspace/current-direction.md` から取得
2. `workspace/current-draft.txt` を `episodes/{番号:2桁}_{タイトル}.txt` にコピー
3. `story/episode-summaries.md` にあらすじを追記（100〜150字）
4. workspace/ の全ファイルを `archive/episode-{番号:2桁}/` にコピー
5. workspace/ をクリーン

***

### Step 8: チームクリーンアップ

全チームメイトに `shutdown_request` を送り、全員がシャットダウンしたことを確認してから TeamDelete を実行する。

***

### 完了報告

以下の情報をユーザーに報告:
- エピソードタイトル
- 保存先ファイルパス
- リビジョン回数
- 最終の担当者判定
- 読者評価（3名分の★と平均）
- FORCE_PASS の場合は警告メッセージ
