const camera =
    document.getElementById("camera");

const button =
    document.getElementById(
        "registerButton"
    );

const result =
    document.getElementById("result");


function sleep(ms) {
    return new Promise(
        resolve => setTimeout(
            resolve,
            ms
        )
    );
}


startCamera(camera);


button.addEventListener(
    "click",
    async () => {

        button.disabled = true;

        result.textContent =
            "顔を取得しています...";

        try {

            const personId =
                document
                    .getElementById(
                        "personId"
                    )
                    .value
                    .trim();

            if (!personId) {
                throw new Error(
                    "Person IDが必要です。"
                );
            }

            const formData =
                new FormData();

            formData.append(
                "person_id",
                personId
            );

            for (
                let index = 0;
                index < 5;
                index++
            ) {

                const blob =
                    await captureFrame(
                        camera
                    );

                formData.append(
                    "images",
                    blob,
                    `face_${index + 1}.jpg`
                );

                await sleep(300);
            }

            const response =
                await fetch(
                    "/api/register",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail
                );
            }

            result.textContent =
                JSON.stringify(
                    data,
                    null,
                    2
                );

        } catch (error) {

            result.textContent =
                `ERROR: ${error.message}`;

        } finally {

            button.disabled = false;

        }
    }
);