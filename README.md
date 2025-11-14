# S3互換シミュレーター

## 概要

このシミュレーターは、S3 API互換サーバ（Scality等）の簡易版として動作するPythonプログラムです。ローカルファイルシステム上のディレクトリをS3バケットとして扱い、HTTPリクエストによりPDFファイルをダウンロードできる機能を提供します。

### 主な機能

- **S3 API互換エンドポイント**: `GET /{bucket}/{key}` 形式でファイルにアクセス
- **認証不要**: シンプルなHTTPリクエストでファイルをダウンロード
- **クロスプラットフォーム**: Windows/Linux両環境で動作
- **標準ライブラリのみ**: 外部依存なしで動作
- **セキュリティ機能**: パストラバーサル攻撃を防止
- **PDFファイル専用**: `.pdf` 拡張子のファイルのみ提供

### 用途

- 開発・テスト環境でのS3互換ストレージのシミュレーション
- Difyワークフローでのローカルファイルアクセス
- curlやHTTPクライアントを使用した簡易ファイルサーバ

## ⚠️ セキュリティ警告

**このシミュレーターは開発・テスト用途専用です。**

- 認証機能がないため、本番環境での使用は推奨されません
- 公開ネットワークでの使用は避けてください
- ローカル開発環境またはプライベートネットワーク内でのみ使用してください

## 要件

- **Python**: 3.7以上
- **依存関係**: なし（標準ライブラリのみ使用）
- **対応OS**: Windows、Linux、macOS

## セットアップ

### 1. バケットディレクトリの準備

シミュレーターで使用するローカルディレクトリを作成し、PDFファイルを配置します。

```bash
# バケットディレクトリの作成
mkdir -p test-bucket/documents
mkdir -p test-bucket/reports/2024

# サンプルPDFファイルの配置（例）
cp sample.pdf test-bucket/documents/manual.pdf
cp report.pdf test-bucket/reports/2024/january.pdf
```

### 2. ディレクトリ構造例

```
test-bucket/
├── documents/
│   ├── manual.pdf
│   ├── guide.pdf
│   └── tutorial.pdf
├── reports/
│   ├── 2024/
│   │   ├── january.pdf
│   │   ├── february.pdf
│   │   └── march.pdf
│   └── 2023/
│       └── summary.pdf
└── presentations/
    ├── overview.pdf
    └── demo.pdf
```

## 使用方法

### 基本的な起動

```bash
python s3_simulator.py --bucket test-bucket=./test-bucket --port 8000
```

### コマンドラインオプション

- `--bucket <name>=<path>`: バケット名とディレクトリパスを指定（複数指定可能）
- `--port <number>`: HTTPサーバのポート番号（デフォルト: 8000）

### 複数バケットの設定

```bash
python s3_simulator.py \
    --bucket documents=./docs \
    --bucket reports=./reports \
    --bucket images=./images \
    --port 8080
```

### 起動例

```bash
# Windowsの場合
python s3_simulator.py --bucket mybucket=C:\Users\username\Documents\bucket --port 8000

# Linuxの場合
python s3_simulator.py --bucket mybucket=/home/username/bucket --port 8000
```

サーバが起動すると、以下のようなメッセージが表示されます：

```
S3 Simulator starting...
Configured buckets:
  - mybucket -> /path/to/bucket
Server running on http://0.0.0.0:8000
Press Ctrl+C to stop
```


## curlでのテスト

### 基本的なダウンロード

```bash
# PDFファイルをダウンロード
curl http://localhost:8000/test-bucket/documents/manual.pdf -o manual.pdf

# ダウンロード成功時の出力例
# Content-Type: application/pdf
# ファイルが manual.pdf として保存されます
```

### ネストされたパスのダウンロード

```bash
# サブディレクトリ内のファイルをダウンロード
curl http://localhost:8000/test-bucket/reports/2024/january.pdf -o january.pdf

# 深い階層のファイル
curl http://localhost:8000/test-bucket/reports/2024/Q1/summary.pdf -o summary.pdf
```

### ヘッダー確認

```bash
# レスポンスヘッダーのみを表示
curl -I http://localhost:8000/test-bucket/documents/manual.pdf

# 出力例:
# HTTP/1.0 200 OK
# Content-Type: application/pdf
# Content-Length: 1234567
```

### 詳細情報の表示

```bash
# 詳細なリクエスト/レスポンス情報を表示
curl -v http://localhost:8000/test-bucket/documents/manual.pdf -o manual.pdf
```

### エラーケースのテスト

```bash
# 存在しないファイル（404エラー）
curl http://localhost:8000/test-bucket/documents/notfound.pdf

# 出力例:
# {"error": {"code": "NoSuchKey", "message": "The specified key does not exist"}}

# 存在しないバケット（404エラー）
curl http://localhost:8000/invalid-bucket/file.pdf

# 出力例:
# {"error": {"code": "NoSuchBucket", "message": "The specified bucket does not exist"}}

# パストラバーサル試行（403エラー）
curl http://localhost:8000/test-bucket/../etc/passwd

# 出力例:
# {"error": {"code": "AccessDenied", "message": "Access denied"}}

# PDF以外のファイル（403エラー）
curl http://localhost:8000/test-bucket/documents/readme.txt

# 出力例:
# {"error": {"code": "InvalidFileType", "message": "Only PDF files are allowed"}}
```

### URLエンコードされたパス

```bash
# スペースを含むファイル名
curl http://localhost:8000/test-bucket/documents/my%20file.pdf -o myfile.pdf

# 日本語ファイル名（UTF-8エンコード）
curl http://localhost:8000/test-bucket/documents/%E3%83%AC%E3%83%9D%E3%83%BC%E3%83%88.pdf -o report.pdf
```


## Dify連携

DifyワークフローのHTTPノードを使用して、シミュレーターからPDFファイルを取得できます。

### HTTPノードの設定

#### 基本設定

- **Method**: `GET`
- **URL**: `http://localhost:8000/{{bucket}}/{{file_path}}`
- **Headers**:
  - `Accept: application/pdf`

#### URL形式の例

```
# 固定パスの場合
http://localhost:8000/test-bucket/documents/manual.pdf

# 変数を使用する場合
http://localhost:8000/{{bucket}}/{{file_path}}

# 複数の変数を組み合わせる場合
http://localhost:8000/{{bucket}}/{{folder}}/{{filename}}
```

### 変数の設定方法

Difyワークフローで以下の変数を定義します：

```yaml
変数名: bucket
値: test-bucket
説明: S3バケット名

変数名: file_path
値: documents/manual.pdf
説明: バケット内のファイルパス
```

### 設定例1: 固定ファイルの取得

```yaml
HTTPノード設定:
  名前: PDFファイル取得
  Method: GET
  URL: http://localhost:8000/test-bucket/reports/2024/january.pdf
  Headers:
    Accept: application/pdf
  
出力変数:
  pdf_content: レスポンスボディ（PDFバイナリデータ）
```

### 設定例2: 動的ファイルパスの使用

```yaml
HTTPノード設定:
  名前: 動的PDFファイル取得
  Method: GET
  URL: http://localhost:8000/{{bucket}}/{{file_path}}
  Headers:
    Accept: application/pdf
  
入力変数:
  bucket: documents
  file_path: reports/2024/{{month}}.pdf
  
出力変数:
  pdf_content: レスポンスボディ
  status_code: HTTPステータスコード
```

### レスポンス処理

#### 成功時（HTTP 200）

```yaml
レスポンス:
  Status Code: 200
  Content-Type: application/pdf
  Body: PDFファイルのバイナリデータ
  
処理方法:
  - レスポンスボディをワークフロー変数に保存
  - 次のノードでPDF解析や保存処理を実行
```

#### エラー時（HTTP 4xx/5xx）

```yaml
レスポンス例（404）:
  Status Code: 404
  Content-Type: application/json
  Body: {"error": {"code": "NoSuchKey", "message": "The specified key does not exist"}}
  
処理方法:
  - ステータスコードをチェック
  - エラーメッセージを取得してログ出力
  - 条件分岐ノードでエラーハンドリング
```

### Difyワークフロー例

```
[開始] 
  ↓
[変数設定]
  bucket = "test-bucket"
  file_path = "documents/manual.pdf"
  ↓
[HTTPノード: PDFファイル取得]
  URL: http://localhost:8000/{{bucket}}/{{file_path}}
  ↓
[条件分岐]
  ├─ 成功（200）→ [PDF処理ノード]
  └─ エラー → [エラーハンドリング]
```

### トラブルシューティング（Dify）

#### 接続エラー

```
エラー: Connection refused
原因: シミュレーターが起動していない
解決: python s3_simulator.py を実行してサーバを起動
```

#### 404エラー

```
エラー: {"error": {"code": "NoSuchKey", ...}}
原因: ファイルパスが間違っている
解決: 
  - バケット名とファイルパスを確認
  - ファイルが実際に存在するか確認
  - パスの区切り文字は "/" を使用
```

#### 403エラー

```
エラー: {"error": {"code": "InvalidFileType", ...}}
原因: PDFファイル以外を指定している
解決: .pdf 拡張子のファイルを指定
```


## トラブルシューティング

### ポート使用中エラー

#### エラーメッセージ

```
OSError: [Errno 48] Address already in use
または
OSError: [WinError 10048] 通常、各ソケット アドレスに対してプロトコル、ネットワーク アドレス、またはポートのどれか 1 つのみを使用できます。
```

#### 原因

指定したポート（デフォルト: 8000）が既に他のプログラムで使用されています。

#### 解決方法

**方法1: 別のポートを使用**

```bash
python s3_simulator.py --bucket test-bucket=./test-bucket --port 8001
```

**方法2: 使用中のプロセスを確認して終了**

Windows:
```cmd
# ポート8000を使用しているプロセスを確認
netstat -ano | findstr :8000

# プロセスIDを確認して終了
taskkill /PID <プロセスID> /F
```

Linux/macOS:
```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill <プロセスID>
```

### バケットディレクトリが見つからないエラー

#### エラーメッセージ

```
Error: Bucket directory does not exist: /path/to/bucket
```

#### 原因

指定したバケットディレクトリが存在しません。

#### 解決方法

**方法1: ディレクトリを作成**

```bash
# Windows
mkdir C:\path\to\bucket

# Linux/macOS
mkdir -p /path/to/bucket
```

**方法2: 正しいパスを指定**

```bash
# 相対パスの使用
python s3_simulator.py --bucket test-bucket=./test-bucket --port 8000

# 絶対パスの使用（Windows）
python s3_simulator.py --bucket test-bucket=C:\Users\username\bucket --port 8000

# 絶対パスの使用（Linux）
python s3_simulator.py --bucket test-bucket=/home/username/bucket --port 8000
```

**方法3: 現在のディレクトリを確認**

```bash
# 現在のディレクトリを表示
pwd  # Linux/macOS
cd   # Windows

# ディレクトリの内容を確認
ls   # Linux/macOS
dir  # Windows
```

### ファイルが見つからないエラー

#### エラーレスポンス

```json
{
  "error": {
    "code": "NoSuchKey",
    "message": "The specified key does not exist"
  }
}
```

#### 原因

指定したファイルパスが存在しないか、ファイル名が間違っています。

#### 解決方法

**1. ファイルの存在を確認**

```bash
# バケットディレクトリ内のファイルを確認
ls -R test-bucket/  # Linux/macOS
dir /s test-bucket\ # Windows
```

**2. パスの区切り文字を確認**

```bash
# 正しい形式（スラッシュを使用）
curl http://localhost:8000/test-bucket/documents/manual.pdf

# 間違った形式（バックスラッシュは使用不可）
# curl http://localhost:8000/test-bucket\documents\manual.pdf
```

**3. ファイル拡張子を確認**

```bash
# PDFファイルのみアクセス可能
curl http://localhost:8000/test-bucket/documents/manual.pdf  # OK
curl http://localhost:8000/test-bucket/documents/manual.txt  # NG (403エラー)
```

**4. 大文字小文字を確認**

Linuxでは大文字小文字が区別されます：

```bash
# ファイル名: Manual.pdf の場合
curl http://localhost:8000/test-bucket/documents/Manual.pdf  # OK
curl http://localhost:8000/test-bucket/documents/manual.pdf  # NG (404エラー)
```

### アクセス拒否エラー

#### エラーレスポンス

```json
{
  "error": {
    "code": "AccessDenied",
    "message": "Access denied"
  }
}
```

#### 原因

パストラバーサル攻撃の試行が検出されました。

#### 解決方法

バケットディレクトリ外のファイルにはアクセスできません。正しいパスを指定してください：

```bash
# 間違った例（バケット外へのアクセス）
curl http://localhost:8000/test-bucket/../etc/passwd  # NG
curl http://localhost:8000/test-bucket/../../file.pdf  # NG

# 正しい例（バケット内のファイル）
curl http://localhost:8000/test-bucket/documents/manual.pdf  # OK
```

### ファイルタイプエラー

#### エラーレスポンス

```json
{
  "error": {
    "code": "InvalidFileType",
    "message": "Only PDF files are allowed"
  }
}
```

#### 原因

PDFファイル以外のファイルにアクセスしようとしています。

#### 解決方法

`.pdf` 拡張子のファイルのみ指定してください：

```bash
# OK
curl http://localhost:8000/test-bucket/documents/manual.pdf

# NG
curl http://localhost:8000/test-bucket/documents/readme.txt
curl http://localhost:8000/test-bucket/images/photo.jpg
```

### サーバが起動しない

#### 症状

`python s3_simulator.py` を実行してもエラーが発生する。

#### 解決方法

**1. Pythonバージョンを確認**

```bash
python --version
# Python 3.7以上が必要
```

**2. ファイルの存在を確認**

```bash
ls s3_simulator.py  # Linux/macOS
dir s3_simulator.py # Windows
```

**3. 構文エラーを確認**

```bash
python -m py_compile s3_simulator.py
```

**4. 詳細なエラーメッセージを確認**

```bash
python s3_simulator.py --bucket test-bucket=./test-bucket --port 8000
# エラーメッセージ全体を確認
```

### 接続できない

#### 症状

curlやDifyから接続できない。

#### 解決方法

**1. サーバが起動しているか確認**

サーバのコンソールに以下のメッセージが表示されているか確認：

```
Server running on http://0.0.0.0:8000
```

**2. ポート番号を確認**

```bash
# サーバ起動時に指定したポート番号を使用
curl http://localhost:8000/test-bucket/file.pdf
```

**3. ファイアウォールを確認**

ファイアウォールがポートをブロックしていないか確認してください。

**4. ホスト名を確認**

```bash
# ローカルホストでアクセス
curl http://localhost:8000/test-bucket/file.pdf

# または
curl http://127.0.0.1:8000/test-bucket/file.pdf
```

## ライセンス

このプロジェクトは開発・テスト用途専用です。

## 貢献

バグ報告や機能要望は、プロジェクトのIssueトラッカーにお願いします。

