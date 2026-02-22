# 補助スクリプト利用ガイド（write-episode）

Step 6 で再現性が重要な処理は、以下のスクリプトを優先して実行する。

## 1) メタナラティブ検出

- コマンド:
  - `python .claude/skills/write-episode/scripts/detect_metanarrative.py workspace/current-draft.txt`
- 役割:
  - 1行目以外に `第\d+話` が出現する箇所を検出する。
- 出力:
  - `NO_MATCH` もしくは `MATCH line=<行番号> text=<内容>` を1行ずつ出力。

## 2) 読者評価の集計

- コマンド:
  - `python .claude/skills/write-episode/scripts/aggregate_reader_scores.py workspace/reader-feedback-young-male.md workspace/reader-feedback-adult-female.md workspace/reader-feedback-veteran.md`
- 役割:
  - 各ファイルから `★N` 形式の評価を抽出し、平均と中央値を算出する。
- 出力:
  - JSON 形式で `scores`, `average`, `median` を出力。

## 運用ルール

- スクリプト実行に失敗した場合のみ、手計算・手動検出にフォールバックする。
- 判定ロジックそのものは変更しない（Step 6 の閾値は固定）。
