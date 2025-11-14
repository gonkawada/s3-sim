# 要件定義書

## はじめに

本ドキュメントは、S3 API互換サーバであるScalityの簡易シミュレーターの要件を定義します。このシミュレーターは、Pythonの標準ライブラリのみを使用し、Windows/Linux両プラットフォームで動作し、認証不要でHTTPリクエストによりPDFファイルをダウンロードできる機能を提供します。

## 用語集

- **Simulator**: S3 API互換の簡易HTTPサーバプログラム
- **Bucket**: ローカルファイルシステム上の特定ディレクトリで、S3バケットとして扱われる
- **Object**: バケット内に格納されるPDFファイル
- **Client**: SimulatorにHTTPリクエストを送信するクライアント（curl、Difyなど）
- **HTTP Server**: Simulatorが提供するHTTPエンドポイント

## 要件

### 要件1

**ユーザーストーリー:** 開発者として、Windows/Linux両方の環境でS3互換シミュレーターを実行できるようにしたい。そうすることで、環境に依存せずにテストができる。

#### 受入基準

1. THE Simulator SHALL execute on Windows operating systems using Python standard library version 3.7 or higher
2. THE Simulator SHALL execute on Linux operating systems using Python standard library version 3.7 or higher
3. THE Simulator SHALL use cross-platform file path handling for Bucket access
4. THE Simulator SHALL start an HTTP Server on a port number specified via command-line argument

### 要件2

**ユーザーストーリー:** 開発者として、認証なしでHTTPリクエストを送信してファイルをダウンロードしたい。そうすることで、シンプルなテスト環境を構築できる。

#### 受入基準

1. WHEN Client sends GET request to HTTP Server, THE Simulator SHALL respond without requiring authentication credentials
2. WHEN Client requests an Object, THE Simulator SHALL return the PDF file content with HTTP status 200
3. IF Client requests a non-existent Object, THEN THE Simulator SHALL return HTTP status 404 with error message
4. THE Simulator SHALL set Content-Type header to "application/pdf" for all successful responses

### 要件3

**ユーザーストーリー:** 開発者として、ローカルディレクトリをS3バケットとして扱いたい。そうすることで、既存のファイル構造をそのまま利用できる。

#### 受入基準

1. THE Simulator SHALL map a specified local directory path to a Bucket name
2. WHEN Simulator starts, THE Simulator SHALL validate that the Bucket directory exists
3. THE Simulator SHALL serve only PDF files with ".pdf" extension from the Bucket
4. THE Simulator SHALL preserve the directory structure within the Bucket as Object key paths

### 要件4

**ユーザーストーリー:** 開発者として、S3 APIに準拠したエンドポイントでファイルをダウンロードしたい。そうすることで、S3クライアントとの互換性を保てる。

#### 受入基準

1. THE Simulator SHALL support GET requests with path format "/{bucket}/{key}"
2. WHEN Client sends GET request with valid bucket and key, THE Simulator SHALL return the corresponding PDF file
3. THE Simulator SHALL decode URL-encoded characters in the Object key path
4. THE Simulator SHALL handle nested directory paths in Object keys

### 要件5

**ユーザーストーリー:** 開発者として、curlコマンドでシミュレーターをテストしたい。そうすることで、基本的な動作を確認できる。

#### 受入基準

1. WHEN Client sends GET request via curl, THE Simulator SHALL respond with PDF file content
2. THE Simulator SHALL provide example curl commands in documentation
3. WHEN HTTP Server receives a request, THE Simulator SHALL log the request details to standard output
4. THE Simulator SHALL handle concurrent requests from multiple Client instances

### 要件6

**ユーザーストーリー:** 開発者として、DifyのHTTPノードからシミュレーターを呼び出したい。そうすることで、ワークフロー内でPDFファイルを取得できる。

#### 受入基準

1. WHEN Dify HTTP node sends GET request, THE Simulator SHALL accept and process the request
2. WHEN Dify workflow passes Object key as variable, THE Simulator SHALL process the variable in the request path
3. THE Simulator SHALL return PDF content in a format that Dify HTTP node can process
4. THE Simulator SHALL provide documentation with Dify HTTP node configuration examples

### 要件7

**ユーザーストーリー:** 開発者として、シミュレーターの設定と使用方法を理解したい。そうすることで、迅速にセットアップできる。

#### 受入基準

1. THE Simulator SHALL provide documentation describing Bucket directory setup
2. THE Simulator SHALL provide documentation with example directory tree structure
3. THE Simulator SHALL provide documentation with curl test commands
4. THE Simulator SHALL provide documentation with Dify HTTP node usage instructions

### 要件8

**ユーザーストーリー:** 開発者として、エラー時に適切なHTTPステータスコードとメッセージを受け取りたい。そうすることで、問題を迅速に特定できる。

#### 受入基準

1. IF Client requests invalid Bucket name, THEN THE Simulator SHALL return HTTP status 404 with error message
2. IF Client requests Object outside Bucket directory, THEN THE Simulator SHALL return HTTP status 403 with error message
3. IF Simulator encounters file read error, THEN THE Simulator SHALL return HTTP status 500 with error message
4. THE Simulator SHALL return error responses in JSON format with error code and message
