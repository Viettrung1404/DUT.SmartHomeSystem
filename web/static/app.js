async function sendCommand(command) {
  const response = await fetch("/api/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command }),
  });

  if (!response.ok) {
    const data = await response.json();
    alert(data.error || "Command failed");
  }
}

async function loadStatus() {
  const response = await fetch("/api/status");
  const data = await response.json();
  const display = document.getElementById("status");
  const temp = document.getElementById("temp");
  const humidity = document.getElementById("humidity");
  const distance = document.getElementById("distance");
  const distanceAlert = document.getElementById("distance-alert");
  const tempValue = data.temperature_c !== null ? `${data.temperature_c} C` : "--";
  const humidityValue = data.humidity !== null ? `${data.humidity} %` : "--";
  const distanceValue = data.distance_cm !== null ? `${data.distance_cm} cm` : "--";
  const alertValue =
    data.distance_alert === null || data.distance_alert === undefined
      ? "--"
      : data.distance_alert
        ? "WARNING"
        : "OK";
  const lines = [
    `device_id: ${data.device_id || "unknown"}`,
    `light: ${data.light || "unknown"}`,
    `fan: ${data.fan || "unknown"}`,
    `temperature_c: ${data.temperature_c ?? "unknown"}`,
    `humidity: ${data.humidity ?? "unknown"}`,
    `distance_cm: ${data.distance_cm ?? "unknown"}`,
    `distance_alert: ${data.distance_alert ?? "unknown"}`,
    `timestamp: ${data.timestamp || 0}`,
  ];
  display.textContent = lines.join("\n");
  if (temp) {
    temp.textContent = tempValue;
  }
  if (humidity) {
    humidity.textContent = humidityValue;
  }
  if (distance) {
    distance.textContent = distanceValue;
  }
  if (distanceAlert) {
    distanceAlert.textContent = alertValue;
    distanceAlert.classList.toggle("alert", alertValue === "WARNING");
  }

  const faceImage = document.getElementById("face-image");
  const facePlaceholder = document.getElementById("face-placeholder");
  const backendUrl = document.body.dataset.backendUrl;
  if (faceImage && backendUrl) {
    faceImage.onload = () => {
      faceImage.style.display = "block";
      if (facePlaceholder) {
        facePlaceholder.textContent = "";
      }
    };
    faceImage.onerror = () => {
      faceImage.style.display = "none";
      if (facePlaceholder) {
        facePlaceholder.textContent = "No image yet";
      }
    };
    faceImage.src = `${backendUrl}/face/last.jpg?ts=${Date.now()}`;
  }
}

document.querySelectorAll("button[data-command]").forEach((button) => {
  button.addEventListener("click", async () => {
    await sendCommand(button.dataset.command);
    await loadStatus();
  });
});

loadStatus();
setInterval(loadStatus, 3000);
