let stream = null;

async function startCamera(video) {
    stream =
        await navigator.mediaDevices
            .getUserMedia({
                video: {
                    width: 1280,
                    height: 720
                },
                audio: false
            });

    video.srcObject = stream;

    await video.play();
}


function captureFrame(video) {

    const canvas =
        document.createElement("canvas");

    canvas.width =
        video.videoWidth;

    canvas.height =
        video.videoHeight;

    const context =
        canvas.getContext("2d");

    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    return new Promise(resolve => {

        canvas.toBlob(
            resolve,
            "image/jpeg",
            0.95
        );

    });
}