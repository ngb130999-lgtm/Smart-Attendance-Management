const camera =
    document.getElementById(
        "camera"
    );

const button =
    document.getElementById(
        "verifyButton"
    );

const modelSelect =
    document.getElementById(
        "modelSelect"
    );


const recognitionResult =
    document.getElementById(
        "recognitionResult"
    );

const benchmarkResult =
    document.getElementById(
        "benchmarkResult"
    );

const errorResult =
    document.getElementById(
        "errorResult"
    );


const statusIcon =
    document.getElementById(
        "statusIcon"
    );

const statusText =
    document.getElementById(
        "statusText"
    );

const personResult =
    document.getElementById(
        "personResult"
    );


const actualResult =
    document.getElementById(
        "actualResult"
    );

const predictedResult =
    document.getElementById(
        "predictedResult"
    );

const outcomeResult =
    document.getElementById(
        "outcomeResult"
    );

const similarityResult =
    document.getElementById(
        "similarityResult"
    );

const thresholdResult =
    document.getElementById(
        "thresholdResult"
    );

const rankResult =
    document.getElementById(
        "rankResult"
    );

const secondBestResult =
    document.getElementById(
        "secondBestResult"
    );

const secondSimilarityResult =
    document.getElementById(
        "secondSimilarityResult"
    );

const marginResult =
    document.getElementById(
        "marginResult"
    );

const modelResult =
    document.getElementById(
        "modelResult"
    );

const latencyResult =
    document.getElementById(
        "latencyResult"
    );


const scoreTableBody =
    document.getElementById(
        "scoreTableBody"
    );

const errorMessage =
    document.getElementById(
        "errorMessage"
    );


/*
 * =========================================
 * Initialisation
 * =========================================
 */

async function initialize() {

    try {

        /*
         * 利用可能モデル取得
         */
        await loadModels();


        /*
         * Camera Start
         */
        await startCamera(
            camera
        );

    } catch (error) {

        showError(
            error.message
        );

    }
}


initialize();


/*
 * =========================================
 * Load Models
 * =========================================
 */

async function loadModels() {

    const response =
        await fetch(
            "/api/models"
        );


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.detail ??
            "モデル一覧を取得できませんでした。"
        );

    }


    modelSelect.innerHTML =
        "";


    for (
        const model
        of data.models
    ) {

        /*
         * disabledモデルは表示しない
         */
        if (!model.enabled) {
            continue;
        }


        const option =
            document.createElement(
                "option"
            );


        option.value =
            model.name;


        option.textContent =
            model.name;


        /*
         * Default model
         */
        if (
            model.name ===
            data.default
        ) {

            option.selected =
                true;

        }


        modelSelect.appendChild(
            option
        );

    }


    if (
        modelSelect.options.length
        === 0
    ) {

        throw new Error(
            "利用可能な顔認証モデルがありません。"
        );

    }

}


/*
 * =========================================
 * Recognition
 * =========================================
 */

button.addEventListener(
    "click",
    async () => {

        button.disabled =
            true;

        button.textContent =
            "認証しています...";


        hideResults();


        try {

            /*
             * Model
             */
            const modelName =
                modelSelect.value;


            /*
             * Ground Truth
             */
            const actualPerson =
                document
                    .getElementById(
                        "actualPerson"
                    )
                    .value;


            /*
             * Condition
             */
            const condition =
                document
                    .getElementById(
                        "condition"
                    )
                    .value;


            if (!modelName) {

                throw new Error(
                    "モデルを選択してください。"
                );

            }


            /*
             * Capture current face
             */
            const blob =
                await captureFrame(
                    camera
                );


            if (!blob) {

                throw new Error(
                    "カメラ画像を取得できませんでした。"
                );

            }


            /*
             * Request
             */
            const formData =
                new FormData();


            formData.append(
                "model_name",
                modelName
            );


            formData.append(
                "actual_person",
                actualPerson
            );


            formData.append(
                "condition",
                condition
            );


            formData.append(
                "image",
                blob,
                "verify.jpg"
            );


            /*
             * API
             */
            const response =
                await fetch(
                    "/api/identify",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ??
                    "顔認証処理に失敗しました。"
                );

            }


            /*
             * Recognition Result
             */
            showRecognitionResult(
                data
            );


            /*
             * Benchmark Detail
             */
            showBenchmarkScores(
                data
            );


        } catch (error) {

            showError(
                error.message
            );

        } finally {

            button.disabled =
                false;

            button.textContent =
                "顔認証";

        }

    }
);


/*
 * =========================================
 * Main Recognition Result
 * =========================================
 */

function showRecognitionResult(
    data
) {

    recognitionResult
        .classList
        .remove(
            "hidden"
        );


    /*
     * Basic Result
     */

    actualResult.textContent =
        data.actual_person;


    predictedResult.textContent =
        data.person_id ??
        "UNKNOWN";


    outcomeResult.textContent =
        data.outcome;


    similarityResult.textContent =
        Number(
            data.similarity
        ).toFixed(4);


    thresholdResult.textContent =
        Number(
            data.threshold
        ).toFixed(4);


    rankResult.textContent =
        data.rank ?? "-";


    secondBestResult.textContent =
        data.second_best_person ??
        "-";


    if (
        data.second_best_similarity
        != null
    ) {

        secondSimilarityResult
            .textContent =
                Number(
                    data
                        .second_best_similarity
                )
                .toFixed(4);

    } else {

        secondSimilarityResult
            .textContent =
                "-";

    }


    if (
        data.score_margin
        != null
    ) {

        marginResult.textContent =
            Number(
                data.score_margin
            ).toFixed(4);

    } else {

        marginResult.textContent =
            "-";

    }


    modelResult.textContent =
        data.model;


    latencyResult.textContent =
        `${Number(
            data.latency_ms
        ).toFixed(2)} ms`;


    /*
     * Outcome Display
     */

    switch (
        data.outcome
    ) {

        /*
         * 本人を本人として認証
         */
        case "CORRECT_ACCEPT":

            recognitionResult.className =
                "recognition-result recognition-success";

            statusIcon.textContent =
                "✓";

            statusText.textContent =
                "本人認証成功";

            personResult.textContent =
                `${data.actual_person} を正しく認証しました。`;

            break;


        /*
         * 未登録者を正しく拒否
         */
        case "CORRECT_REJECT":

            recognitionResult.className =
                "recognition-result recognition-success";

            statusIcon.textContent =
                "✓";

            statusText.textContent =
                "未登録者を拒否";

            personResult.textContent =
                "未登録者を正しく拒否しました。";

            break;


        /*
         * 本人なのに拒否
         */
        case "FALSE_REJECT":

            recognitionResult.className =
                "recognition-result recognition-failure";

            statusIcon.textContent =
                "✕";

            statusText.textContent =
                "本人拒否";

            personResult.textContent =
                `${data.actual_person} を認証できませんでした。`;

            break;


        /*
         * 未登録者を登録者として受入
         */
        case "FALSE_ACCEPT":

            recognitionResult.className =
                "recognition-result recognition-warning";

            statusIcon.textContent =
                "⚠";

            statusText.textContent =
                "未登録者誤受入";

            personResult.textContent =
                `未登録者を ${data.person_id} として認証しました。`;

            break;


        /*
         * 登録者Aを登録者Bとして認証
         */
        case "MISIDENTIFICATION":

            recognitionResult.className =
                "recognition-result recognition-warning";

            statusIcon.textContent =
                "⚠";

            statusText.textContent =
                "人物誤認識";

            personResult.textContent =
                `${data.actual_person} を ${data.person_id} と誤認識しました。`;

            break;


        default:

            recognitionResult.className =
                "recognition-result";

            statusIcon.textContent =
                "?";

            statusText.textContent =
                "不明な判定";

            personResult.textContent =
                data.outcome ??
                "UNKNOWN";

    }

}


/*
 * =========================================
 * Benchmark Scores
 * =========================================
 */

function showBenchmarkScores(
    data
) {

    benchmarkResult
        .classList
        .remove(
            "hidden"
        );


    scoreTableBody.innerHTML =
        "";


    if (!data.scores) {

        return;

    }


    /*
     * Highest similarity first
     */
    const sortedScores =
        Object.entries(
            data.scores
        )
        .sort(
            (a, b) =>
                b[1] - a[1]
        );


    sortedScores.forEach(
        (
            [personId, similarity],
            index
        ) => {

            const row =
                document
                    .createElement(
                        "tr"
                    );


            /*
             * Rank
             */
            const rankCell =
                document
                    .createElement(
                        "td"
                    );

            rankCell.textContent =
                index + 1;


            /*
             * Person
             */
            const personCell =
                document
                    .createElement(
                        "td"
                    );

            personCell.textContent =
                personId;


            /*
             * Similarity
             */
            const similarityCell =
                document
                    .createElement(
                        "td"
                    );

            similarityCell.textContent =
                Number(
                    similarity
                ).toFixed(4);


            /*
             * Threshold
             */
            const thresholdCell =
                document
                    .createElement(
                        "td"
                    );


            if (
                similarity >=
                data.threshold
            ) {

                thresholdCell
                    .textContent =
                        "PASS";

            } else {

                thresholdCell
                    .textContent =
                        "NO";

            }


            /*
             * Rank-1 highlight
             */
            if (index === 0) {

                row.classList.add(
                    "best-score"
                );

            }


            row.appendChild(
                rankCell
            );

            row.appendChild(
                personCell
            );

            row.appendChild(
                similarityCell
            );

            row.appendChild(
                thresholdCell
            );


            scoreTableBody
                .appendChild(
                    row
                );

        }
    );

}


/*
 * =========================================
 * Error
 * =========================================
 */

function showError(
    message
) {

    recognitionResult
        .classList
        .add(
            "hidden"
        );

    benchmarkResult
        .classList
        .add(
            "hidden"
        );

    errorResult
        .classList
        .remove(
            "hidden"
        );

    errorMessage.textContent =
        message;

}


/*
 * =========================================
 * Hide Results
 * =========================================
 */

function hideResults() {

    recognitionResult
        .classList
        .add(
            "hidden"
        );

    benchmarkResult
        .classList
        .add(
            "hidden"
        );

    errorResult
        .classList
        .add(
            "hidden"
        );

}