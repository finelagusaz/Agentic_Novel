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

1. Glob ツールで `workspace/*.md` と `workspace/*.txt` を検索し、ファイルが存在する場合のみ `rm -f` で削除する（zsh のグロブエラーを回避するため、ファイルが存在しない場合はスキップする）
2. `workspace/revision-log.md` を作成（空テンプレート）:
   ```
   # リビジョン履歴 — 第{番号}話
   ```
3. 前話のエピソード（episodes/ 内）が存在するか確認
4. revision_count = 0 として初期化
5. `story/handover-notes.md` を読み込み、`[DEFERRED:ep{今回の番号}]` のタグが付いた項目を `[ACTIVE]` に昇格する（該当項目がなければスキップ）

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

各チームメイトは、スポーン時の Task ツールの prompt に作業指示を直接含めてスポーンする。
SendMessage による二段階ハンドシェイクは行わない（初回スポーン時のみ。リビジョンループでの再利用時は SendMessage を使う）。

***

### Step 2: 編集（方針策定）

**editor をスポーン**する。Task ツールの prompt に以下の作業指示を直接含める:

```
第{番号}話の創作方針を策定してください。

以下のファイルを読み込んでください:
- agents/editor.md（あなたの役割定義）
- story/premise.md, story/setting.md, story/characters.md
- story/plot-outline.md, story/writing-guide.md
- story/episode-summaries.md
- story/handover-notes.md（前話からの申し送り事項。存在する場合）
- 前話のエピソード（あれば episodes/ から最新のもの）

agents/editor.md の指示に従い、結果を workspace/current-direction.md に書き出してください。
完了したら報告してください。
```

editor からの完了報告（idle通知）を待ち、`workspace/current-direction.md` が生成されたことを確認。

***

### Step 3: 作者（執筆 / 改稿）

**author をスポーン**する。Task ツールの prompt に以下の作業指示を直接含める。

**初稿の場合** — prompt に以下を含める:

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

author からの完了報告を待ち、`workspace/current-draft.txt` が生成されたことを確認。

***

### Step 4: 担当者（レビュー）

**manager をスポーン**する。Task ツールの prompt に以下の作業指示を直接含める:

```
ドラフトを評価してください。

以下のファイルを読み込んでください:
- agents/manager.md（あなたの役割定義）
- workspace/current-direction.md（編集の方針）
- workspace/current-draft.txt（評価対象のドラフト）
- story/premise.md, story/setting.md, story/characters.md
- story/writing-guide.md, story/episode-summaries.md
- story/handover-notes.md（申し送り事項、あれば）
- workspace/revision-log.md（リビジョン履歴、あれば）

agents/manager.md の指示に従い、ドラフトを評価してください。
現在のリビジョン回数は {revision_count} / {max_revisions} です。
結果を workspace/manager-review.md に書き出してください。
完了したら報告してください。
```

manager からの完了報告を待つ。

***

### Step 5: 読者×3（並列フィードバック）

**reader-ym, reader-af, reader-vet を同時にスポーン**する。各 Task ツールの prompt に以下の作業指示を直接含める（3名並列でスポーン）:

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
agents/readers/reader-veteran.md と story/setting.md, story/characters.md, story/episode-summaries.md（アーク要約＋直近エピソード詳細の両方）も参照し、
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
3. `story/episode-summaries.md` を更新する:
   a. 「直近エピソード詳細」セクションに今話のあらすじを追記（100〜150字）
   b. 直近エピソード詳細が5話を超えた場合:
      - 最も古い話を「直近エピソード詳細」から削除する
      （アーク要約に含まれているため詳細は不要）
   c. アーク境界に達した場合（`story/plot-outline.md` の幕区分を参照）:
      - 当該アークの全話を6〜8行のアーク要約に圧縮する
      - 「アーク要約」セクションの末尾（`<!-- ↑ アークが閉じるたびにここに追加される -->` コメントの直前）に追加する
      - 【主な伏線】にアーク内で張られた重要伏線を列挙する
      - 圧縮後、該当話の詳細あらすじを「直近エピソード詳細」から削除する
      - 第二幕（第6〜13話）は長いため、自然な区切りでサブアーク（例: 第6〜9話 / 第10〜13話）に分割してよい
3.5. `story/handover-notes.md` のライフサイクル管理を行う:
   a. 現在の `story/handover-notes.md` を読み込む
   b. 今話で解決された項目を特定する:
      - `workspace/current-draft.txt`（確定ドラフト）を読み、`[ACTIVE]` 項目のうち今話の本文で対処されたものを `[RESOLVED]` に変更する
   c. `[RESOLVED]` タグの付いた項目を削除する
   d. 新たな申し送り事項を追加する:
      - `workspace/manager-review.md` の「要修正箇所」「良かった点」から抽出
      - `workspace/reader-feedback-young-male.md`, `workspace/reader-feedback-adult-female.md`, `workspace/reader-feedback-veteran.md` から共通指摘・個別要望を抽出
      - 各項目に適切なタグ（`[ACTIVE]` or `[DEFERRED:epN]`）を付与する
   e. セクション内の項目数チェック:
      - 上限: 設定整合性5件 / 未回収伏線7件 / 表現・演出5件 / キャラクター描写5件 / 読者要望5件 / 継続的な指針5件
      - いずれかのセクションが上限を超えた場合、優先度の低い `[ACTIVE]` 項目を `[DEFERRED:epN]` に降格して上限内に収める
   f. 反復する指摘は `[RECURRING]` に昇格して「継続的な指針」セクションへ移動する
   g. 更新後の `story/handover-notes.md` を上書き保存する（見出しの話番号も更新する）
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
