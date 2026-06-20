# Invoice Status Monitor API (インボイスステータス監視＆Webhook通知API)

## 🎯 概要
本プロジェクトは、13桁の法人番号をキーに適格請求書発行事業者の登録ステータス（登録中、取消し、失効など）を照会・監視できるREST API、および登録ステータス変更時にクライアントへWebhook通知を行う非同期型APIのプロトタイプです。

AIエージェントおよび自動化システムが急増する2026年のAPIエコノミーに対応する戦略的アイデアとして、「動的なバックオフィスデータの監視」と「解約しづらい（高スイッチングコスト）連携機能」をデモするために構築されました。

## 🛠️ 主な機能
1. **インボイス情報照会 (REST API)**:
   * `GET /api/invoice/{corporate_number}`: 法人番号から最新の事業者名、登録日、ステータスを取得。
   * セキュリティ対策として Rate Limiter が適用されています。
2. **監視対象登録 (Webhook登録)**:
   * `POST /api/monitor/register`: 監視したい法人番号と通知先Webhook URLを登録。
3. **ステータス変更シミュレーター (非同期通知)**:
   * `POST /api/monitor/simulate-change`: 模擬的に企業ステータスを変更し、登録済みの全クライアントに対して `BackgroundTasks` を用いた非同期の Webhook イベント通知を送信。

## 📂 ディレクトリ構造
```text
invoice-status-monitor-api/
├── app/
│   ├── main.py                     # アプリ起動、CORS、C3.8.3互換MD5パッチ、ルーター統合
│   ├── core/
│   │   ├── config.py               # Pydantic設定
│   │   └── deps.py                 # SlowAPIリミッター
│   ├── schemas/
│   │   ├── company.py              # インボイス企業情報スキーマ
│   │   └── monitor.py              # Webhook/監視リクエストスキーマ
│   ├── services/
│   │   └── database.py             # 模擬DB管理、非同期Webhook送信ロジック
│   └── routers/
│       ├── r01_invoice_api.py      # 照会APIエンドポイント
│       └── r02_monitor_api.py      # Webhook登録＆シミュレータエンドポイント
├── tests/
│   ├── conftest.py             # TestClientフィクスチャ
│   └── test_endpoints.py       # pytestテストケース
├── requirements.txt            # 依存モジュール
└── .gitignore
```

## 🚀 セットアップ手順

### 1. 仮想環境の構築と依存モジュールのインストール
```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 依存モジュールのインストール
pip install -r requirements.txt
```

### 2. サーバーの起動
```bash
# 仮想環境上でuvicornを起動
.\venv\Scripts\uvicorn app.main:app --reload
```
起動後、ブラウザで [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs) にアクセスするとSwagger UIでAPIをテストできます。

## 🧪 テストの実行
`pytest` を用いて、REST API照会、バリデーションエラー、Webhook登録、ステータス変更による非同期送信スパイのテストを実行します。
```bash
# python -m を用いてsys.pathにカレントディレクトリを含めてテストを実行
.\venv\Scripts\python -m pytest
```
