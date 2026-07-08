```mermaid
erDiagram
    
    employees ||--o{ attendance_logs : "1 to Many"

    employees {
        varchar id PK "社員ID"
        varchar name "氏名"
        varchar department "部署"
        varchar line_user_id "メールユーザーID"
        vector face_embedding "顔特徴量ベクトル (512次元)"
    }

    attendance_logs {
        serial log_id PK "ログID (自動的に増える)"
        varchar employee_id FK "社員ID (外部キー)"
        timestamp timestamp "打刻日時 (顔打刻日時)"
        varchar status "出勤ステータス (ON_TIME / LATE)"
    }
```

### 👥 1. `employees` テーブル 
| 論理名 | 物理名 | 型 | 制約 | 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 社員ID | `id` | VARCHAR(20) | PRIMARY KEY | 例: `NV001`, `NV002` |
| 氏名 | `name` | VARCHAR(100) | NOT NULL | 会社員の名前 |
| 部署 | `department` | VARCHAR(50) | - | 所属している部署 |
| メール| `mail_user_id` | VARCHAR(50) | UNIQUE | メールで当人にお知らせ |
| 顔特徴量 | `face_embedding` | vector(512) | NOT NULL | InsightFaceから抽出する特徴量 |

### ⏰ 2. `attendance_logs` テーブル 
| 論理名 | 物理名 | 型 | 制約  | 備考  |
| :--- | :--- | :--- | :--- | :--- |
| ログID | `log_id` | SERIAL | PRIMARY KEY | IDが自動的に増える |
| 社員ID | `employee_id` | VARCHAR(20) | FOREIGN KEY | `employees(id)`というテーブルに繋がる |
| 打刻日時 | `timestamp` | TIMESTAMP | NOT NULL, DEFAULT NOW() | システム認識時刻 |
| ステータス | `status` | VARCHAR(20) | NOT NULL | `ON_TIME`, `LATE`, `EARLY` |

---
