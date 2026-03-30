function uploadImage() {

    const input = document.getElementById("imageInput");

    if (input.files.length === 0) {
        alert("Select image first");
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append("image", file);

    fetch("/analyze", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {

        document.getElementById("result").innerText =
            "Particles: " + data.microplastic_count +
            " | Status: " + data.water_status;

        document.getElementById("grayImage").src =
            data.grayscale_image + "?t=" + new Date().getTime();

        // ✅ meter
        let circle = document.getElementById("progressCircle");
        let text = document.getElementById("meterText");

        let percent = 0;

        // 🔴 MUST CHECK FIRST
        if (data.water_status.includes("NOT SAFE")) {
            percent = 100;
            circle.style.stroke = "red";
            text.innerText = "UNSAFE";
            text.style.color = "red";
        }

        // 🟡 MODERATE
        else if (data.water_status.includes("Moderate")) {
            percent = 60;
            circle.style.stroke = "yellow";
            text.innerText = "MODERATE";
            text.style.color = "yellow";
        }

        // 🟢 SAFE
        else {
            percent = 30;
            circle.style.stroke = "limegreen";
            text.innerText = "SAFE";
            text.style.color = "limegreen";
        }

        let offset = 314 - (314 * percent) / 100;
        circle.style.strokeDashoffset = offset;

    })
    .catch(err => {
        console.error(err);
        alert("Something went wrong");
    });
}
