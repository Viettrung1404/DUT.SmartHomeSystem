async function sendCommand(command) {
  try {
    const response = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(data.detail || data.error || "Command failed");
      return;
    }
  } catch (err) {
    alert(`FE->BE error: ${err?.message || err}`);
  }
}

async function loadStatus() {
  let data = {};
  let loadError = "";
  try {
    const response = await fetch("/api/status");
    data = await response.json();
    if (!response.ok) {
      loadError = data.error || data.detail || `HTTP ${response.status}`;
    }
  } catch (err) {
    loadError = `FE->BE error: ${err?.message || err}`;
    data = {};
  }
  const display = document.getElementById("status");
  const temp = document.getElementById("temp");
  const humidity = document.getElementById("humidity");
  const distance = document.getElementById("distance");
  const distanceAlert = document.getElementById("distance-alert");
  const distanceLight = document.getElementById("distance-light");
  const gasDetected = document.getElementById("gas-detected");
  const rainDetected = document.getElementById("rain-detected");
  const denKhach = document.getElementById("den-khach");
  const denNgu = document.getElementById("den-ngu");
  const quatKhach = document.getElementById("quat-khach");
  const quatNgu = document.getElementById("quat-ngu");
  const buzzer = document.getElementById("buzzer");
  const door = document.getElementById("door");
  const tempValue = data.temperature_c !== null ? `${data.temperature_c} C` : "--";
  const humidityValue = data.humidity !== null ? `${data.humidity} %` : "--";
  const distanceValue = data.distance_cm !== null ? `${data.distance_cm} cm` : "--";
  const alertValue =
    data.distance_alert === null || data.distance_alert === undefined
      ? "--"
      : data.distance_alert
        ? "WARNING"
        : "OK";
  const distanceLightValue =
    data.distance_light === null || data.distance_light === undefined
      ? "--"
      : String(data.distance_light).toUpperCase();
  const gasDetectedValue =
    data.gas_detected === null || data.gas_detected === undefined
      ? "--"
      : data.gas_detected
        ? "DETECTED"
        : "CLEAR";
  const rainDetectedValue =
    data.rain_detected === null || data.rain_detected === undefined
      ? "--"
      : data.rain_detected
        ? "WET"
        : "DRY";
  const buzzerValue =
    data.buzzer === null || data.buzzer === undefined
      ? "--"
      : String(data.buzzer).toUpperCase();
  const doorValue =
    data.door === null || data.door === undefined
      ? "--"
      : String(data.door).toUpperCase();
  const denKhachValue =
    data.den_khach === null || data.den_khach === undefined
      ? "--"
      : String(data.den_khach).toUpperCase();
  const denNguValue =
    data.den_ngu === null || data.den_ngu === undefined
      ? "--"
      : String(data.den_ngu).toUpperCase();
  const quatKhachValue =
    data.quat_khach === null || data.quat_khach === undefined
      ? "--"
      : String(data.quat_khach).toUpperCase();
  const quatNguValue =
    data.quat_ngu === null || data.quat_ngu === undefined
      ? "--"
      : String(data.quat_ngu).toUpperCase();
  const lines = [
    `device_id: ${data.device_id || "unknown"}`,
    `den_khach: ${data.den_khach ?? "unknown"}`,
    `den_ngu: ${data.den_ngu ?? "unknown"}`,
    `quat_khach: ${data.quat_khach ?? "unknown"}`,
    `quat_ngu: ${data.quat_ngu ?? "unknown"}`,
    `light: ${data.light || "unknown"}`,
    `fan: ${data.fan || "unknown"}`,
    `distance_light: ${data.distance_light ?? "unknown"}`,
    `gas_detected: ${data.gas_detected ?? "unknown"}`,
    `rain_detected: ${data.rain_detected ?? "unknown"}`,
    `buzzer: ${data.buzzer ?? "unknown"}`,
    `door: ${data.door ?? "unknown"}`,
    `temperature_c: ${data.temperature_c ?? "unknown"}`,
    `humidity: ${data.humidity ?? "unknown"}`,
    `distance_cm: ${data.distance_cm ?? "unknown"}`,
    `distance_alert: ${data.distance_alert ?? "unknown"}`,
    `timestamp: ${data.timestamp || 0}`,
    `error: ${loadError || data.error || "none"}`,
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
  if (distanceLight) {
    distanceLight.textContent = distanceLightValue;
    distanceLight.classList.toggle("active", distanceLightValue === "ON");
  }
  if (gasDetected) {
    gasDetected.textContent = gasDetectedValue;
    gasDetected.classList.toggle("alert", gasDetectedValue === "DETECTED");
  }
  if (rainDetected) {
    rainDetected.textContent = rainDetectedValue;
    rainDetected.classList.toggle("alert", rainDetectedValue === "WET");
  }
  if (denKhach) {
    denKhach.textContent = denKhachValue;
    denKhach.classList.toggle("active", denKhachValue === "ON");
  }
  if (denNgu) {
    denNgu.textContent = denNguValue;
    denNgu.classList.toggle("active", denNguValue === "ON");
  }
  if (quatKhach) {
    quatKhach.textContent = quatKhachValue;
    quatKhach.classList.toggle("active", quatKhachValue !== "OFF" && quatKhachValue !== "--");
  }
  if (quatNgu) {
    quatNgu.textContent = quatNguValue;
    quatNgu.classList.toggle("active", quatNguValue !== "OFF" && quatNguValue !== "--");
  }
  if (buzzer) {
    buzzer.textContent = buzzerValue;
    buzzer.classList.toggle("alert", buzzerValue === "ON");
  }
  if (door) {
    door.textContent = doorValue;
    door.classList.toggle("active", doorValue === "OPEN");
  }

  const faceImage = document.getElementById("face-image");
  const facePlaceholder = document.getElementById("face-placeholder");
  const backendUrl = document.body.dataset.backendUrl;
  const homeId = document.body.dataset.homeId || "";
  const deviceId = document.body.dataset.deviceId || "";
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
    const idQuery =
      homeId && deviceId
        ? `home_id=${encodeURIComponent(homeId)}&device_id=${encodeURIComponent(deviceId)}&`
        : "";
    faceImage.src = `${backendUrl}/face/last.jpg?${idQuery}ts=${Date.now()}`;
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
