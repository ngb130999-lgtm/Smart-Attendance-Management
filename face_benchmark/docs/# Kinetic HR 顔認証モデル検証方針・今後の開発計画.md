# Kinetic HR 顔認証モデル検証方針・今後の開発計画

## 1. 概要

現在、チーム開発ポートフォリオとして **Smart Attendance Management / Kinetic HR** の開発を進めている。

最終的には以下の3アプリを開発する予定。

1. 顔認証勤怠確認アプリ
2. 人事専用勤怠管理アプリ
3. 申請アプリ

現在は3アプリのモックアップ作成を先に行い、チームメンバー間で完成時のイメージを共有できる状態にしている。

次の開発段階として、顔認証勤怠確認アプリで使用する**顔認証モデルの選定・精度検証**を進める。

---

# 2. 顔認証モデル検証の目的

今回の検証では、Kinetic HRの顔認証勤怠機能で使用するモデルを決定する。

比較対象は以下の3モデル。

| モデル                | 概要                        |
| ------------------ | ------------------------- |
| `buffalo_l`        | InsightFace Model Zooのモデル |
| `antelopev2`       | InsightFace Model Zooのモデル |
| `JAPANESE_FACE_V1` | FACE01で提供されている日本人向け顔認証モデル |

単純にSimilarityが高いモデルを採用するのではなく、以下を比較する。

- 本人を正しく認証できるか
- 他人を本人として誤認識しないか
- 未登録者を正しく拒否できるか
- 顔の向きによる精度変化
- 眼鏡などによる精度変化
- 明るさによる精度変化
- カメラとの距離による精度変化
- 認証処理時間
- Threshold変更による精度変化
- 1 Identificationでの認識精度

---

# 3. 現在の開発状況

現在 `face_benchmark` として顔認証モデル検証環境を作成している。

現状では主に以下まで実装済み。

- FastAPIによるBenchmark API
- Webカメラ取得
- InsightFaceモデル読み込み
- `buffalo_l` 読み込み
- `antelopev2` を切り替えられるAdapter構造
- CUDA / GPU実行環境
- 顔検出
- Face Embedding生成
- L2 Normalization
- Cosine Similarity計算
- Threshold判定
- 1 Identification
- `.npy` によるEmbedding保存
- CSVによる認証結果保存
- Similarity Score保存
- FMR / FNMR / Precision / Recall / F1 / ROC-AUC解析の基本処理

現在はモデル選定のためのPoC段階であり、Dockerにはまだ移行しない。

モデル検証が完了した後、本システムへの統合段階でDocker環境へ移行する。

---

# 4. 顔登録方式の変更

当初はWeb画面から顔を5枚撮影し、その場で顔登録する方式を実装していた。

しかし、モデル検証では毎回Web画面から登録する必要性が低いため、方式を変更する。

## 変更前

```text
Web画面
↓
Person ID入力
↓
Webカメラで5枚撮影
↓
Embedding生成
↓
顔登録
```

## 変更後

```text
事前に用意した顔写真
↓
enroll_faces.py
↓
顔検出
↓
Alignment
↓
Embedding生成
↓
L2 Normalization
↓
複数Embeddingを統合
↓
登録Template生成
↓
.npy保存
```

Web UIからの顔登録はBenchmarkでは使用しない。

---

# 5. Enrollment用画像

各メンバーを匿名IDで管理する。

```text
person_001
person_002
person_003
person_004
```

事前登録用画像は例えば以下のように統一する。

```text
data/enrollment/

├── person_001/
│   ├── front_01.jpg
│   ├── front_02.jpg
│   ├── slight_left.jpg
│   ├── slight_right.jpg
│   └── expression.jpg
│
├── person_002/
├── person_003/
└── person_004/
```

初期案として各人物5枚程度を使用する。

- 正面1
- 正面2
- 軽い左向き
- 軽い右向き
- 軽い表情差

登録画像と認証精度評価に使用する画像は分離する。

同じ画像を登録と評価の両方に使用しない。

---

# 6. 顔登録時の計算

各画像から顔Embeddingを生成する。

各Embeddingを `e_i` とすると、L2 Normalizationを行う。

[
\hat{e_i} = \frac{e_i}{||e_i||\_2}
]

複数画像のEmbeddingを平均する。

\frac{1}{N}
\sum\_{i=1}^{N}
\hat{e_i}
]

その後、平均Embeddingを再度L2 Normalizationする。

\frac{e\_{avg}}
{||e\_{avg}||\_2}
]

このTemplateを人物ごとの登録情報として保存する。

```text
data/embeddings/

├── buffalo_l/
│   ├── person_001.npy
│   ├── person_002.npy
│   ├── person_003.npy
│   └── person_004.npy
│
├── antelopev2/
│
└── japanese_face_v1/
```

モデルごとにEmbedding空間が異なるため、モデルを変更した場合は、そのモデルを使用して4人分のTemplateを再生成する。

---

# 7. 顔認証時の処理

実際の顔認証ではWebカメラを使用する。

```text
Webカメラ
↓
現在の顔画像取得
↓
顔検出
↓
Alignment
↓
Embedding生成
↓
L2 Normalization
↓
登録済み4人のTemplateと比較
↓
Cosine Similarity
↓
最大Similarityを取得
↓
Threshold判定
↓
人物判定
```

Cosine Similarityは、

\frac{A \cdot B}
{||A||||B||}
]

で計算する。

EmbeddingはL2 Normalization済みのため、

[
Similarity(A,B)=A \cdot B
]

として計算できる。

---

# 8. 1 Identification

Kinetic HRでは、最終的にカメラに映った人物が登録者の誰なのか判定する必要がある。

そのため、主な検証対象は **1 Identification** とする。

例えば `person_002` がカメラに映った場合、

```text
Query Face

↓

person_001 Template → 0.4212
person_002 Template → 0.8124
person_003 Template → 0.5112
person_004 Template → 0.3921

↓

Rank-1
person_002 = 0.8124

↓

Threshold以上

↓

person_002 と認証
```

という処理を行う。

---

# 9. 認証結果の分類

単純な「成功 / 失敗」だけではなく、以下の5種類で分類する予定。

## CORRECT_ACCEPT

本人を本人として認識。

```text
Actual    : person_002
Predicted : person_002
```

## FALSE_REJECT

登録者本人なのにUNKNOWNとして拒否。

```text
Actual    : person_002
Predicted : UNKNOWN
```

## MISIDENTIFICATION

登録者本人を別の登録者として誤認識。

```text
Actual    : person_002
Predicted : person_003
```

## CORRECT_REJECT

未登録者をUNKNOWNとして正しく拒否。

```text
Actual    : UNKNOWN
Predicted : UNKNOWN
```

## FALSE_ACCEPT

未登録者を登録者として誤認識。

```text
Actual    : UNKNOWN
Predicted : person_003
```

勤怠管理では特に、

```text
person_002
↓
person_003として出勤処理
```

のような誤認識を重要な問題として評価する。

---

# 10. Web UI

顔認証Benchmark画面については以下の情報を表示できるように変更する。

```text
Kinetic HR
Face Recognition Benchmark

使用モデル
[ buffalo_l ▼ ]

実際の人物
[ person_002 ▼ ]

撮影条件
[ front ▼ ]

┌─────────────────────────┐
│                         │
│      Web Camera         │
│                         │
└─────────────────────────┘

        [ 顔認証 ]

-----------------------------

✓ 正常認証

Actual Person
person_002

Predicted Person
person_002

Outcome
CORRECT_ACCEPT

Similarity
0.8124

Threshold
0.50

Rank
1

Second Best
person_003 : 0.5112

Score Margin
0.3012

Latency
75.4 ms

Model
buffalo_l
```

これにより、単純に「認証成功」と表示するのではなく、

- 誰として認証されたか
- 本人と一致したか
- Similarity
- Threshold
- 2位候補
- 1位と2位の差
- 処理時間

を確認できるようにする。

---

# 11. UIからのモデル変更

Web UIから以下を選択可能にする予定。

```text
buffalo_l
antelopev2
japanese_face_v1
```

ただし、3モデルを同時にGPUへロードする方式にはしない。

基本的には選択されたモデルのみ使用する。

モデルごとに登録Templateも分離する。

```text
buffalo_l
↓
data/embeddings/buffalo_l/

antelopev2
↓
data/embeddings/antelopev2/

japanese_face_v1
↓
data/embeddings/japanese_face_v1/
```

---

# 12. Threshold

現在の `0.50` は最終Thresholdではなく、初期検証用の暫定値として扱う。

最終的には、

```text
buffalo_l
→ Threshold A

antelopev2
→ Threshold B

JAPANESE_FACE_V1
→ Threshold C
```

としてモデルごとに実測結果から決定する。

そのため、

```yaml
models:

  buffalo_l:
    threshold: 0.50

  antelopev2:
    threshold: 0.50

  japanese_face_v1:
    threshold: 0.50
```

のような設定方式へ変更する予定。

---

# 13. 認証条件

Live Benchmarkでは以下を初期検証条件とする予定。

```text
front
left
right
glasses
bright
dark
near
far
```

各条件5回程度を想定する。

4人の場合、

```text
8条件
×
5回
×
4人

= 160回 / model
```

3モデルなら、

```text
160
×
3

= 480回
```

程度になる。

実際の検証量については開発期間と負担を見ながら調整する。

---

# 14. 人物別CSV

チームメンバー4人が同じCSVを更新するとGit上で競合する可能性がある。

そのため、結果ファイルを人物単位で分離する。

モデルごとに以下の構造を予定。

```text
results/
└── buffalo_l/

    ├── enrollment/
    │   ├── person_001_enrollment.csv
    │   ├── person_002_enrollment.csv
    │   ├── person_003_enrollment.csv
    │   └── person_004_enrollment.csv
    │
    ├── recognition/
    │   ├── person_001_recognition.csv
    │   ├── person_002_recognition.csv
    │   ├── person_003_recognition.csv
    │   └── person_004_recognition.csv
    │
    ├── scores/
    │   ├── person_001_scores.csv
    │   ├── person_002_scores.csv
    │   ├── person_003_scores.csv
    │   └── person_004_scores.csv
    │
    └── analysis/
        ├── combined_recognition.csv
        ├── combined_scores.csv
        └── threshold_analysis.csv
```

同じ構造を、

```text
antelopev2/
japanese_face_v1/
```

にも作成する。

---

# 15. Enrollment CSV

Enrollment時には、例えば以下を保存する。

```csv
person_id,model,image_name,pose,face_detected,face_count,embedding_dimension,embedding_norm,used_for_template
person_001,buffalo_l,front_01.jpg,front,True,1,512,1.0000,True
person_001,buffalo_l,front_02.jpg,front,True,1,512,1.0000,True
person_001,buffalo_l,slight_left.jpg,slight_left,True,1,512,1.0000,True
person_001,buffalo_l,slight_right.jpg,slight_right,True,1,512,1.0000,True
```

Embedding本体はCSVには保存せず `.npy` に保存する。

---

# 16. Recognition CSV

顔認証1回ごとの結果を保存する。

```csv
timestamp,model,actual_person,predicted_person,condition,similarity,threshold,outcome,correct,latency_ms
2026-09-25T20:10:00,buffalo_l,person_001,person_001,front,0.8124,0.50,CORRECT_ACCEPT,True,74.8
2026-09-25T20:10:20,buffalo_l,person_001,UNKNOWN,dark,0.4812,0.50,FALSE_REJECT,False,79.1
```

---

# 17. Score CSV

Threshold解析のため、1位のSimilarityだけではなく登録者全員とのSimilarityを保存する。

```csv
timestamp,model,actual_person,reference_person,condition,similarity,label
2026-09-25T20:10:00,buffalo_l,person_001,person_001,front,0.8124,1
2026-09-25T20:10:00,buffalo_l,person_001,person_002,front,0.4221,0
2026-09-25T20:10:00,buffalo_l,person_001,person_003,front,0.5112,0
2026-09-25T20:10:00,buffalo_l,person_001,person_004,front,0.3921,0
```

`label=1` を本人ペア、`label=0` を他人ペアとして扱う。

---

# 18. チームメンバーが同時に集まれない問題

4人全員が同じ日に集まって検証する必要はない。

例えば、

```text
person_001
9月に測定

person_002
別日に測定

person_003
別日に測定

person_004
別日に測定
```

として、それぞれ人物別CSVへ結果を保存する。

最後に、

```text
person_001
person_002
person_003
person_004

↓

merge_results.py

↓

combined_recognition.csv
combined_scores.csv
```

として統合する。

---

# 19. Offline Benchmark

4人が集まれない問題に対応するため、Live Webカメラ検証だけではなく **Offline Benchmark** も実装する。

```text
事前に取得したTest画像
↓
run_offline_benchmark.py
↓
buffalo_l
↓
全画像自動認証
↓
CSV

同じ画像
↓
antelopev2
↓
CSV

同じ画像
↓
JAPANESE_FACE_V1
↓
CSV
```

これにより、

- 同一PC
- 同一GPU
- 同一画像
- 同一撮影条件

で3モデルを比較できる。

モデルそのものの比較はこちらを中心とする。

Live Benchmarkは、実際の勤怠利用に近いリアルタイム評価として別に行う。

---

# 20. Git / GitHub運用

顔写真やEmbeddingはGitHubへPushしない。

```text
GitHub管理

○ ソースコード
○ 設定ファイル
○ README
○ 分析プログラム
○ 匿名化・集計済み結果
○ レポート

GitHub管理しない

× 顔写真
× Test顔画像
× Enrollment顔画像
× 生Embedding
× .npy
```

`.gitignore` で除外する。

---

# 21. ブランチ

現在のBenchmark開発では、

```text
develop
│
└── feature/face-model-benchmark　→ここが検証用のブランチ
　　└── 現在isuureを立てて、【9-taskinsight-faceのモデル検証をmainブランチから分けて検証用のプランチ専用の場所で行う】で行っている。
```

を基本とする。

必要であれば人物別検証について、

```text
feature/face-model-benchmark

├── benchmark/person-001
├── benchmark/person-002
├── benchmark/person-003
└── benchmark/person-004
```

のように分離する。

各メンバーが自分の結果ファイルのみ更新することで、CSVのGitコンフリクトを減らす。

---

# 22. 評価指標

最終的には以下を比較する予定。

## Verification系

- FMR
- FNMR
- Precision
- Recall
- F1
- ROC-AUC

## Identification系

- Rank-1 Accuracy
- FPIR
- FNIR
- Misidentification数
- False Accept数
- False Reject数

## Performance

- 平均Latency
- Median
- P95
- Min
- Max

## 条件別

- 正面
- 左右
- 眼鏡
- 明所
- 暗所
- 近距離
- 遠距離

---

# 23. 3モデルの検証順序

以下の順で進める予定。

```text
buffalo_l
↓
Enrollment
↓
Offline Benchmark
↓
Live Benchmark
↓
Threshold分析

↓

antelopev2
↓
同じ条件で検証

↓

JAPANESE_FACE_V1
↓
同じ条件で検証

↓

3モデル比較

↓

Kinetic HR採用モデル決定
```

モデル間でEmbeddingは使い回さず、モデルごとにEnrollment Templateを再生成する。

---

# 24. JAPANESE_FACE_V1について

`JAPANESE_FACE_V1` は `buffalo_l` / `antelopev2` と同じInsightFace Model Packではない。

そのため、

```text
JapaneseFaceAdapter
```

として別Adapterを実装する。

FACE01側の実装を確認し、

- Face Detection
- Landmark
- Alignment
- Input Size
- RGB / BGR
- Normalization
- ONNX Input
- Embedding Output
- L2 Normalization

などの前処理を合わせたうえで比較する。

前処理が異なる状態では公平なモデル比較にならないため、ここは実装確認後に進める。

---

# 25. Dockerについて

現在のモデル検証段階では、Windowsローカル環境 + NVIDIA GPUで進める。

```text
現在

Windows
↓
Python venv
↓
ONNX Runtime GPU
↓
InsightFace
↓
RTX GPU
```

モデル選定後、

```text
採用モデル決定
↓
FaceRecognitionService作成
↓
Kinetic HR Backend統合
↓
Docker化
↓
3アプリとの統合
```

へ進む。

Benchmark段階と本番統合段階を分離する。

---

# 26. 今後追加する予定のファイル

```text
scripts/

├── enroll_faces.py
│   └── Enrollment画像からTemplate生成
│
├── run_offline_benchmark.py
│   └── Test画像による自動Benchmark
│
├── merge_results.py
│   └── 4人分CSV統合
│
├── analyze_results.py
│   └── Threshold・精度分析
│
├── inspect_embeddings.py
│   └── Embedding確認
│
└── check_gpu.py
    └── GPU環境確認
```

必要に応じて、

```text
app/api/model.py
app/services/model_service.py
```

なども追加し、UIからモデルを変更できるようにする。

---

# 27. 今後の開発順序

## Step 1

現在発生している誤認識表示の問題を修正する。

特にFrontendのActual PersonとPredicted Personの比較処理を確認する。

---

## Step 2

Web UIからの顔登録をBenchmark処理から外す。

---

## Step 3

以下を作成する。

```text
data/enrollment/
├ person_001/
├ person_002/
├ person_003/
└ person_004/
```

---

## Step 4

`enroll_faces.py` を実装する。

```text
Enrollment画像
↓
Embedding
↓
Template
↓
.npy
↓
Enrollment CSV
```

まで自動化する。

---

## Step 5

Benchmark結果を人物別CSVへ変更する。

```text
Enrollment
Recognition
Scores
```

の3種類を人物ごとに分離する。

---

## Step 6

Backendで認証結果を以下の5種類に分類する。

```text
CORRECT_ACCEPT
FALSE_REJECT
MISIDENTIFICATION
CORRECT_REJECT
FALSE_ACCEPT
```

---

## Step 7

Web UIを変更する。

表示対象：

```text
Model
Actual Person
Predicted Person
Condition
Outcome
Similarity
Threshold
Rank
Second Best
Score Margin
Latency
```

---

## Step 8

UIからモデルを変更できるようにする。

```text
buffalo_l
antelopev2
japanese_face_v1
```

---

## Step 9

`run_offline_benchmark.py` を実装する。

4人が同時に集まらなくても、事前取得画像からモデルを公平に比較できるようにする。

---

## Step 10

`merge_results.py` を実装する。

```text
person_001
person_002
person_003
person_004

↓

Combined Dataset
```

を作成する。

---

## Step 11

`analyze_results.py` を拡張する。

モデルごとに、

```text
Threshold
FMR
FNMR
ROC-AUC
Rank-1 Accuracy
FPIR
FNIR
Latency
条件別精度
```

を算出する。

---

## Step 12

`buffalo_l` でBenchmarkを完了する。

---

## Step 13

同じDataset・同じ条件で `antelopev2` を検証する。

---

## Step 14

`JapaneseFaceAdapter` を完成させ、`JAPANESE_FACE_V1` を同じ条件で検証する。

---

## Step 15

3モデルを比較して、Kinetic HRへ採用するモデルを決定する。

---

# 28. 最終的なBenchmark構成

```text
                     Kinetic HR
              Face Recognition Benchmark

                         │
             ┌───────────┴───────────┐
             │                       │
       Offline Benchmark        Live Benchmark
             │                       │
       Test顔画像                 Webカメラ
             │                       │
             └───────────┬───────────┘
                         │
                    Model Adapter
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      buffalo_l      antelopev2   JAPANESE_FACE_V1
          │              │              │
          └──────────────┼──────────────┘
                         │
                      Embedding
                         │
                  L2 Normalization
                         │
                 Cosine Similarity
                         │
                 1:N Identification
                         │
                      Threshold
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      正常認証         本人拒否         誤認識
          │              │              │
          └──────────────┼──────────────┘
                         │
                    Person別CSV
                         │
                    Result Merge
                         │
                    Model Analysis
                         │
         FMR / FNMR / FPIR / FNIR
         Rank-1 / F1 / ROC-AUC
         Latency / 条件別精度
                         │
                  3モデル比較
                         │
              Kinetic HR採用モデル
```

---

# 29. 現時点でのチーム方針

現時点では、すぐに本番Kinetic HRへ顔認証を組み込むのではなく、まず独立した `face_benchmark` でモデルを比較する。

また、4人全員が同じタイミングで集まれないことを前提として、

```text
事前Enrollment
+
Offline Benchmark
+
人物別Live Benchmark
+
人物別CSV
+
最終統合
```

という方式を採用する。

これにより、

- メンバーが同時に集まれない問題
- CSVのGitコンフリクト
- 毎回顔登録する手間
- モデル間の比較条件が異なる問題
- 認証結果が正常なのか誤認識なのか分かりにくい問題

を解決する。

モデル選定後に顔認証処理を本体Kinetic HRへ統合し、その段階でDockerを使用した本番構成へ移行する。

---

# 30. 注意事項

今回の検証はチームメンバー4名を対象とした小規模PoCである。

そのため、

> 今回の結果だけで一般的な日本人全体に対する顔認証精度を保証するものではない。

最終レポートにもこの制約を記載する。

また、顔画像・Embeddingなどの生体情報についてはGitHubの公開Repositoryへ保存しない。

公開ポートフォリオでは、可能な限り匿名化・集計したBenchmark結果のみ掲載する。



