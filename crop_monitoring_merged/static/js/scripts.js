console.log("SmartFarm scripts loaded");

// SENSOR CHARTS (on dashboard)
// Only run if charts exist on page
async function loadSensorCharts() {
  const tempCtx = document.getElementById("tempChart");
  const moistureCtx = document.getElementById("moistureChart");
  const pestCtx = document.getElementById("pestChart");

  if (!tempCtx || !moistureCtx || !pestCtx) return;

  let tempChart, moistureChart, pestChart;

  async function fetchAndUpdate() {
    const res = await fetch("/get_sensor_data");
    const data = await res.json();
    const labels = data.labels.length ? data.labels.map(l => (new Date(l)).toLocaleTimeString()) : data.temperature.map((_, i) => `#${i+1}`);

    if (!tempChart) {
      tempChart = new Chart(tempCtx, {
        type: "line",
        data: { labels: labels, datasets: [{ label: "Temperature (°C)", data: data.temperature, borderColor: "red", fill: false }] }
      });
    } else {
      tempChart.data.labels = labels;
      tempChart.data.datasets[0].data = data.temperature;
      tempChart.update();
    }

    if (!moistureChart) {
      moistureChart = new Chart(moistureCtx, {
        type: "line",
        data: { labels: labels, datasets: [{ label: "Soil Moisture (%)", data: data.moisture, borderColor: "blue", fill: false }] }
      });
    } else {
      moistureChart.data.labels = labels;
      moistureChart.data.datasets[0].data = data.moisture;
      moistureChart.update();
    }

    if (!pestChart) {
      pestChart = new Chart(pestCtx, {
        type: "line",
        data: { labels: labels, datasets: [{ label: "Pest Level (%)", data: data.pest, borderColor: "green", fill: false }] }
      });
    } else {
      pestChart.data.labels = labels;
      pestChart.data.datasets[0].data = data.pest;
      pestChart.update();
    }

    // Alerts in page (if any) - basic: show in console now
    const latestTemp = data.temperature[data.temperature.length-1] || null;
    const latestMoist = data.moisture[data.moisture.length-1] || null;
    const latestPest = data.pest[data.pest.length-1] || null;
    if (latestTemp && latestTemp > 40) console.warn("High Temperature Alert:", latestTemp);
    if (latestMoist && latestMoist < 20) console.warn("Low Moisture Alert:", latestMoist);
    if (latestPest && latestPest > 70) console.warn("Pest Risk Alert:", latestPest);
  }

  // initial
  fetchAndUpdate();
  // auto refresh every 5 seconds
  setInterval(fetchAndUpdate, 5000);
}

// Called on crop_health submit to store sensor demo entries
async function submitSensor() {
  const temp = parseFloat(document.getElementById("temp_input").value || 0);
  const moisture = parseFloat(document.getElementById("moisture_input").value || 0);
  const pest = parseFloat(document.getElementById("pest_input").value || 0);

  const res = await fetch("/analyze_sensor", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({temperature: temp, moisture: moisture, pest_level: pest})
  });
  const data = await res.json();
  alert("Saved sensor data. Prediction: " + data.prediction + (data.alerts.length ? ("\nAlerts: " + data.alerts.join(" | ")) : ""));
}

// NDVI demo chart on crop_health
if (document.getElementById("ndviChart")) {
  new Chart(document.getElementById("ndviChart"), {
    type: "line",
    data: {
      labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
      datasets: [{label:"NDVI Index", data:[0.65,0.72,0.70,0.80], borderColor:"#27ae60", backgroundColor:"rgba(39,174,96,0.2)"}]
    }
  });
}

// soil/other demo charts
if (document.getElementById("soilMoistureChart")) {
  new Chart(document.getElementById("soilMoistureChart"), {
    type: "bar",
    data: { labels: ["Field A","Field B","Field C"], datasets:[{label:"Soil Moisture (%)", data:[45,60,52], backgroundColor:"#3498db"}] }
  });
}
if (document.getElementById("soilPhChart")) {
  new Chart(document.getElementById("soilPhChart"), {
    type: "pie",
    data: { labels:["Acidic","Neutral","Alkaline"], datasets:[{data:[20,60,20], backgroundColor:["#e74c3c","#2ecc71","#f1c40f"]}] }
  });
}
if (document.getElementById("pestZoneChart")) {
  new Chart(document.getElementById("pestZoneChart"), {
    type: "radar",
    data: { labels:["North","South","East","West"], datasets:[{label:"Pest Risk", data:[80,40,60,30], borderColor:"#8e44ad", backgroundColor:"rgba(142,68,173,0.2)"}] }
  });
}

// Initialize sensor charts if on dashboard
document.addEventListener("DOMContentLoaded", () => {
  loadSensorCharts();
});

