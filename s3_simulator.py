"""
S3 API互換の簡易シミュレーター

このモジュールは、Pythonの標準ライブラリのみを使用して、
S3 API互換のHTTPサーバを提供します。
"""


# カスタム例外クラス

class S3SimulatorError(Exception):
    """S3シミュレーターの基底例外クラス"""
    pass


class BucketNotFoundError(S3SimulatorError):
    """指定されたバケットが存在しない場合の例外"""
    pass


class ObjectNotFoundError(S3SimulatorError):
    """指定されたオブジェクト（ファイル）が存在しない場合の例外"""
    pass


class SecurityError(S3SimulatorError):
    """セキュリティ違反（パストラバーサル攻撃など）の例外"""
    pass


class FileTypeError(S3SimulatorError):
    """許可されていないファイルタイプへのアクセス試行の例外"""
    pass


from pathlib import Path


class BucketManager:
    """
    バケットとファイルシステムの管理
    
    ローカルディレクトリをS3バケットとして扱い、
    ファイルの取得とセキュリティチェックを行います。
    
    属性:
        buckets: dict[str, Path] - バケット名とディレクトリパスのマッピング
    """
    
    def __init__(self, bucket_configs: dict[str, str]):
        """
        バケット設定を初期化
        
        引数:
            bucket_configs: {bucket_name: directory_path} の辞書
        
        例外:
            BucketNotFoundError: 指定されたバケットディレクトリが存在しない場合
        """
        self.buckets = {}
        
        for bucket_name, directory_path in bucket_configs.items():
            path = Path(directory_path)
            
            # バケットディレクトリの存在を検証
            if not path.exists():
                raise BucketNotFoundError(
                    f"Bucket directory does not exist: {directory_path}"
                )
            
            if not path.is_dir():
                raise BucketNotFoundError(
                    f"Bucket path is not a directory: {directory_path}"
                )
            
            self.buckets[bucket_name] = path
    
    def _is_safe_path(self, base_path: Path, target_path: Path) -> bool:
        """
        パストラバーサル攻撃を防ぐためのパス検証
        
        target_pathがbase_path配下にあることを確認します。
        resolve()で正規化してから比較することで、
        ../や絶対パスなどの攻撃を防ぎます。
        
        引数:
            base_path: 基準となるディレクトリパス（バケットディレクトリ）
            target_path: 検証対象のファイルパス
        
        戻り値:
            bool: target_pathが安全な場合True、そうでない場合False
        """
        try:
            resolved_target = target_path.resolve()
            resolved_base = base_path.resolve()
            return resolved_target.is_relative_to(resolved_base)
        except (ValueError, OSError):
            return False
    
    def get_file(self, bucket: str, key: str) -> bytes:
        """
        指定されたバケットとキーからファイルを取得
        
        引数:
            bucket: バケット名
            key: オブジェクトキー（ファイルパス）
        
        戻り値:
            bytes: ファイルのバイナリデータ
        
        例外:
            BucketNotFoundError: バケットが存在しない
            ObjectNotFoundError: ファイルが存在しない
            SecurityError: バケット外のファイルアクセス試行
            FileTypeError: PDFファイル以外へのアクセス
        """
        # バケットの存在確認
        if bucket not in self.buckets:
            raise BucketNotFoundError(f"Bucket not found: {bucket}")
        
        bucket_path = self.buckets[bucket]
        
        # ファイルパスを構築
        file_path = bucket_path / key
        
        # セキュリティチェック: パストラバーサル攻撃を防止
        if not self._is_safe_path(bucket_path, file_path):
            raise SecurityError(
                f"Access denied: path is outside bucket directory: {key}"
            )
        
        # ファイルタイプチェック: PDFファイルのみ許可（大文字小文字を区別しない）
        if file_path.suffix.lower() != '.pdf':
            raise FileTypeError(
                f"Invalid file type: only PDF files are allowed, got {file_path.suffix}"
            )
        
        # ファイルの存在確認
        if not file_path.exists():
            raise ObjectNotFoundError(f"Object not found: {key}")
        
        if not file_path.is_file():
            raise ObjectNotFoundError(f"Object is not a file: {key}")
        
        # ファイルをバイナリモードで読み込み
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except OSError as e:
            raise ObjectNotFoundError(f"Failed to read file: {key}") from e


from http.server import BaseHTTPRequestHandler
from urllib.parse import unquote


class S3SimulatorHandler(BaseHTTPRequestHandler):
    """
    S3 API互換のHTTPリクエストハンドラ
    
    BaseHTTPRequestHandlerを継承し、S3 APIエンドポイントをシミュレートします。
    
    クラス変数:
        bucket_manager: BucketManager - 共有バケットマネージャー
    """
    
    bucket_manager = None
    
    def _parse_s3_path(self, path: str) -> tuple[str, str]:
        """
        S3パスを解析
        
        /{bucket}/{key}形式のパスを解析し、バケット名とオブジェクトキーを抽出します。
        URLエンコードされた文字列はデコードされます。
        
        引数:
            path: リクエストパス（例: /mybucket/docs/file.pdf）
        
        戻り値:
            tuple[str, str]: (bucket_name, object_key)
        
        例外:
            ValueError: パス形式が不正な場合
        """
        # URLデコード
        decoded_path = unquote(path)
        
        # 先頭のスラッシュを除去
        if decoded_path.startswith('/'):
            decoded_path = decoded_path[1:]
        
        # パスを分割
        parts = decoded_path.split('/', 1)
        
        # バケット名とキーが両方存在することを確認
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError(
                f"Invalid S3 path format: expected /{{bucket}}/{{key}}, got {path}"
            )
        
        bucket_name = parts[0]
        object_key = parts[1]
        
        return bucket_name, object_key
    
    def _send_file_response(self, file_data: bytes):
        """
        PDFファイルレスポンスを送信
        
        HTTP 200ステータスとContent-Type: application/pdfヘッダーを設定し、
        ファイルのバイナリデータを送信します。
        
        引数:
            file_data: 送信するファイルのバイナリデータ
        """
        self.send_response(200)
        self.send_header('Content-Type', 'application/pdf')
        self.send_header('Content-Length', str(len(file_data)))
        self.end_headers()
        self.wfile.write(file_data)
    
    def _send_error_response(self, status_code: int, error_code: str, message: str):
        """
        JSON形式のエラーレスポンスを送信
        
        引数:
            status_code: HTTPステータスコード
            error_code: S3互換のエラーコード
            message: エラーメッセージ
        """
        import json
        
        error_response = {
            "error": {
                "code": error_code,
                "message": message
            }
        }
        
        response_body = json.dumps(error_response, ensure_ascii=False).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)
    
    def do_GET(self):
        """
        GETリクエストを処理
        
        S3 API形式のGETリクエストを処理し、指定されたバケットとキーから
        PDFファイルを取得して返します。
        エラーが発生した場合は適切なエラーレスポンスを返します。
        """
        try:
            # パスを解析してバケットとキーを取得
            bucket, key = self._parse_s3_path(self.path)
            
            # ファイルを取得
            file_data = self.bucket_manager.get_file(bucket, key)
            
            # 成功レスポンスを送信
            self._send_file_response(file_data)
            
        except ValueError as e:
            # パス形式が不正
            self._send_error_response(400, "InvalidRequest", str(e))
            
        except BucketNotFoundError as e:
            # バケットが存在しない
            self._send_error_response(404, "NoSuchBucket", str(e))
            
        except ObjectNotFoundError as e:
            # オブジェクトが存在しない
            self._send_error_response(404, "NoSuchKey", str(e))
            
        except SecurityError as e:
            # セキュリティ違反（パストラバーサル）
            self._send_error_response(403, "AccessDenied", str(e))
            
        except FileTypeError as e:
            # ファイルタイプエラー
            self._send_error_response(403, "InvalidFileType", str(e))
            
        except Exception as e:
            # その他の予期しないエラー
            self._send_error_response(500, "InternalError", f"Internal server error: {str(e)}")
    
    def log_message(self, format: str, *args):
        """
        リクエストログを標準出力に出力
        
        タイムスタンプ、メソッド、パス、ステータスコードを含むログを出力します。
        
        引数:
            format: ログメッセージのフォーマット文字列
            *args: フォーマット文字列に渡される引数
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        print(f"{timestamp} {format % args}")


import argparse
from http.server import HTTPServer


def parse_arguments():
    """
    コマンドライン引数を解析
    
    戻り値:
        argparse.Namespace: 解析された引数
            - buckets: list[str] - "name=path"形式のバケット設定リスト
            - port: int - サーバポート番号（デフォルト: 8000）
    """
    parser = argparse.ArgumentParser(
        description='S3 API互換の簡易シミュレーター',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python s3_simulator.py --bucket mybucket=/path/to/bucket --port 8000
  python s3_simulator.py --bucket docs=/home/user/docs --bucket images=/home/user/images
        '''
    )
    
    parser.add_argument(
        '--bucket',
        action='append',
        dest='buckets',
        required=True,
        metavar='NAME=PATH',
        help='バケット設定（name=path形式）。複数指定可能。'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='サーバポート番号（デフォルト: 8000）'
    )
    
    return parser.parse_args()


def main():
    """
    サーバを起動するメイン関数
    
    コマンドライン引数を解析し、BucketManagerを初期化して、
    HTTPサーバを起動します。
    """
    # コマンドライン引数を解析
    args = parse_arguments()
    
    # バケット設定を辞書に変換
    bucket_configs = {}
    for bucket_spec in args.buckets:
        if '=' not in bucket_spec:
            print(f"エラー: バケット設定は 'name=path' 形式で指定してください: {bucket_spec}")
            return 1
        
        name, path = bucket_spec.split('=', 1)
        if not name or not path:
            print(f"エラー: バケット名またはパスが空です: {bucket_spec}")
            return 1
        
        bucket_configs[name] = path
    
    # BucketManagerを初期化
    try:
        bucket_manager = BucketManager(bucket_configs)
    except BucketNotFoundError as e:
        print(f"エラー: {e}")
        return 1
    
    # S3SimulatorHandlerにbucket_managerを設定
    S3SimulatorHandler.bucket_manager = bucket_manager
    
    # HTTPサーバを起動
    server_address = ('', args.port)
    httpd = HTTPServer(server_address, S3SimulatorHandler)
    
    # 起動メッセージを出力
    print(f"S3シミュレーターを起動しました")
    print(f"ポート: {args.port}")
    print(f"バケット:")
    for name, path in bucket_configs.items():
        print(f"  - {name}: {path}")
    print(f"\nサーバを停止するには Ctrl+C を押してください")
    
    # サーバを起動
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nサーバを停止しています...")
        httpd.shutdown()
        print("サーバを停止しました")
        return 0


if __name__ == '__main__':
    import sys
    sys.exit(main() or 0)
