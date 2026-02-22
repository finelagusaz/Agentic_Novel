# Step 6.5 仕様（ポリッシュ・リビジョン）

***

## 目次

- Step 6.5P: ポリッシュ（軽微修正）
- Step 6.5D: リビジョンディスカッション


### Step 6.5P: ポリッシュ（軽微修正）【PASS_WITH_POLISH 時のみ】

Step 6 で PASS_WITH_POLISH と判定された場合にのみ実行する。

progress.md を更新: `current_step: "step6.5p"`, `step_status: "in_progress"`

リーダー（あなた自身）が以下を実行する:

1. **指摘箇所の抽出**: Step 6 で特定した軽微な指摘を **最大3件** にまとめる。以下の優先順位で選定:
   - 担当者と読者が共通して指摘した箇所（最優先）
   - Step 4D で editor が指摘した方針との齟齬
   - 読者2名以上が共通して指摘した箇所

2. **author に部分修正を依頼**: SendMessage で author に以下を送信:
   ```
   判定はPASSですが、以下の軽微な箇所のみ修正してください。
   全体の構成は変更しないでください。

   修正箇所:
   1. {指摘1: 箇所と修正内容}
   2. {指摘2: 箇所と修正内容}
   3. {指摘3: 箇所と修正内容}（あれば）

   修正後、workspace/current-draft.txt を上書きしてください。
   完了したら報告してください。
   ```

3. author からの完了報告を待ち、`workspace/current-draft.txt` について**共通手順: エージェント出力の検証**に従う。

4. **担当者の再レビューは不要**（軽微修正のため）
5. **読者の再評価も不要**（スコアは初回評価を使用）

progress.md を更新: step6.5p を `[x]`、`current_step: "step6.5p"`, `step_status: "completed"`

**Step 7 へ進む**。

***

### Step 6.5D: リビジョンディスカッション【REVISION時のみ】

Step 6 で REVISION_NEEDED と判定された場合にのみ実行する。

**共通手順: ディスカッション管理**に従い、全コアメンバーに以下のメッセージを送信する:

**editor** に SendMessage:
```
リビジョンが必要です（{revision_count}/{max_revisions}回目）。

判定結果:
- Manager判定: {judgment}
- 読者: ユウキ★{N} / サキ★{N} / タツヤ★{N}（平均★{avg}）

以下のフィードバックファイルを確認してください:
- workspace/manager-review.md
- workspace/reader-feedback-young-male.md
- workspace/reader-feedback-adult-female.md
- workspace/reader-feedback-veteran.md

全フィードバックを読み、改稿の優先順位について所見を共有してください。
author, manager と議論の上、workspace/consolidated-feedback.md を作成してください。
agents/editor.md の「リビジョン時の対応」セクションに従ってください。
第{番号}話、リビジョン{revision_count}回目です。
深刻度は「{通常改稿 / 重大改稿}」です。

方針の修正が必要な場合は workspace/current-direction.md も更新してください。
```

**author** に SendMessage:
```
リビジョンが必要です（{revision_count}/{max_revisions}回目）。

判定結果:
- Manager判定: {judgment}
- 読者: ユウキ★{N} / サキ★{N} / タツヤ★{N}（平均★{avg}）

以下のフィードバックファイルを確認してください:
- workspace/manager-review.md
- workspace/reader-feedback-young-male.md
- workspace/reader-feedback-adult-female.md
- workspace/reader-feedback-veteran.md

改稿の実現可能性の観点から意見を出してください。
editor と議論し、改稿方針の策定に協力してください。
特になければ『確認しました』と報告してください。
```

**manager** に SendMessage:
```
リビジョンが必要です（{revision_count}/{max_revisions}回目）。

判定結果:
- Manager判定: {judgment}
- 読者: ユウキ★{N} / サキ★{N} / タツヤ★{N}（平均★{avg}）

レビューの重点について補足があれば共有してください。
editor, author と議論に参加してください。
特に補足がなければ『追加情報なし』と報告してください。
```

**ディスカッション管理**:
- 最大3ラウンド（リビジョンは重要なので多めに）
- editor が `consolidated-feedback.md` を書き出した時点で終了
- editor の出力について**共通手順: エージェント出力の検証**に従う

discussion-log.md に記録を追記し、progress.md を更新: `current_step: "step6.5d"`, `step_status: "completed"`

**Step 3 に戻る**（改稿）。

***

