const camera =
    document.getElementById("camera");

const button =
    document.getElementById(
        "verifyButton"
    );

const result =
    document.getElementById("result");


startCamera(camera);


button.addEventListener(
    "click",
    async () => {

        button.disabled = true;

        result.textContent =
            "認証しています...";

        try {

            const actualPerson =
                document
                    .getElementById(
                        "actualPerson"
                    )
                    .value;

            const condition =
                document
                    .getElementById(
                        "condition"
                    )
                    .value;

            const blob =
                await captureFrame(
                    camera
                );

            const formData =
                new FormData();

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