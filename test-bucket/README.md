# テストバケットディレクトリ

このディレクトリは、S3シミュレーターのテスト用バケットとして使用されます。

## ディレクトリ構造

```
test-bucket/
├── sample.pdf                    # ルートレベルのサンプルPDFファイル
├── documents/                    # ドキュメント用ディレクトリ
│   ├── manual.pdf               # (配置してください)
│   └── guide.pdf                # (配置してください)
├── reports/                      # レポート用ディレクトリ
│   ├── 2024/                    # 2024年のレポート
│   │   ├── january.pdf          # (配置してください)
│   │   └── february.pdf         # (配置してください)
│   └── 2023/                    # 2023年のレポート
│       └── summary.pdf          # (配置してください)
└── presentations/                # プレゼンテーション用ディレクトリ
    └── overview.pdf             # (配置してください)
```

## サンプルPDFファイルの配置方法

### 方法1: 既存のPDFファイルをコピー

既存のPDFファイルを上記のディレクトリ構造に配置してください。

```bash
# Windowsの場合
copy your-file.pdf test-bucket\documents\manual.pdf
copy your-file.pdf test-bucket\reports\2024\january.pdf

# Linux/Macの場合
cp your-file.pdf test-bucket/documents/manual.pdf
cp your-file.pdf test-bucket/reports/2024/january.pdf
```

### 方法2: ダミーPDFファイルの作成

テスト用のダミーPDFファイルを作成する場合は、以下のような方法があります：

#### Pythonを使用する場合

```python
# create_dummy_pdf.py
from reportlab.pdfgen import canvas

def create_dummy_pdf(filename, title):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, title)
    c.drawString(100, 700, "This is a test PDF file.")
    c.save()

# 使用例
create_dummy_pdf("test-bucket/documents/manual.pdf", "Manual Document")
```

注: reportlabライブラリが必要です (`pip install reportlab`)

#### オンラインツールを使用する場合

1. https://www.adobe.com/acrobat/online/word-to-pdf.html などのオンラインツールでPDFを作成
2. 作成したPDFを適切なディレクトリに配置

### 方法3: 既存のsample.pdfをコピー

最も簡単な方法として、既存の`sample.pdf`を各ディレクトリにコピーすることもできます：

```bash
# Windowsの場合
copy test-bucket\sample.pdf test-bucket\documents\manual.pdf
copy test-bucket\sample.pdf test-bucket\documents\guide.pdf
copy test-bucket\sample.pdf test-bucket\reports\2024\january.pdf
copy test-bucket\sample.pdf test-bucket\reports\2024\february.pdf
copy test-bucket\sample.pdf test-bucket\reports\2023\summary.pdf
copy test-bucket\sample.pdf test-bucket\presentations\overview.pdf

# Linux/Macの場合
cp test-bucket/sample.pdf test-bucket/documents/manual.pdf
cp test-bucket/sample.pdf test-bucket/documents/guide.pdf
cp test-bucket/sample.pdf test-bucket/reports/2024/january.pdf
cp test-bucket/sample.pdf test-bucket/reports/2024/february.pdf
cp test-bucket/sample.pdf test-bucket/reports/2023/summary.pdf
cp test-bucket/sample.pdf test-bucket/presentations/overview.pdf
```

## テスト方法

シミュレーターを起動してテストします：

```bash
# シミュレーターを起動
python s3_simulator.py --bucket test-bucket=./test-bucket --port 8000

# 別のターミナルでテスト
curl http://localhost:8000/test-bucket/sample.pdf -o downloaded.pdf
curl http://localhost:8000/test-bucket/documents/manual.pdf -o manual.pdf
curl http://localhost:8000/test-bucket/reports/2024/january.pdf -o january.pdf
```

## 注意事項

- このディレクトリ内には**PDFファイルのみ**を配置してください
- シミュレーターは`.pdf`拡張子のファイルのみを提供します
- パストラバーサル攻撃を防ぐため、このディレクトリ外のファイルにはアクセスできません
