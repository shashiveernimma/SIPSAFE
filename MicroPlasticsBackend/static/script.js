function uploadImage() {

    const input = document.getElementById("imageInput");

    if (!input.files.length) {
        alert("Please select an image first");
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append("image", file);

    fetch("/analyze", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("result").innerText =
            "Particles: " + data.microplastic_count +
            " | Water Status: " + data.water_status;

        document.getElementById("grayImage").src =
            data.grayscale_image + "?t=" + new Date().getTime();

        // ✅ WATER METER
        const circle = document.getElementById("progressCircle");
        const text = document.getElementById("meterText");

        let percent = 0;

        if (data.water_status.includes("SAFE")) {
            percent = 30;
            text.innerText = "SAFE 🟢";
            circle.style.stroke = "lime";
        }
        else if (data.water_status.includes("Moderate")) {
            percent = 60;
            text.innerText = "MODERATE 🟡";
            circle.style.stroke = "yellow";
        }
        else {
            percent = 100;
            text.innerText = "UNSAFE 🔴";
            circle.style.stroke = "red";
        }

        let offset = 314 - (314 * percent) / 100;
        circle.style.strokeDashoffset = offset;

    })
    .catch(error => {
        console.error(error);
        alert("Backend error. Check terminal.");
    });
}