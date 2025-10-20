let selectedFile = null;

const dropArea = document.getElementById("drop-area");
const fileElem = document.getElementById("fileElem");
const filenameDisplay = document.getElementById("filename");
const resultDisplay = document.getElementById("result");

dropArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropArea.classList.add("hover");
});

dropArea.addEventListener("dragleave", () => {
  dropArea.classList.remove("hover");
});

dropArea.addEventListener("drop", (e) => {
  e.preventDefault();
  dropArea.classList.remove("hover");

  const file = e.dataTransfer.files[0];
  handleFile(file);
});

fileElem.addEventListener("change", (e) => {
  const file = e.target.files[0];
  handleFile(file);
});

function handleFile(file) {
  selectedFile = file;
  filenameDisplay.textContent = file.name;
}

async function predict() {
  if (!selectedFile) {
    alert("Please select or drop an image file.");
    return;
  }

  if (!resultDisplay) {
    console.error("Result element not found (id='result')");
    return;
  }

  resultDisplay.textContent = "Processing...";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch("/predict", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    
    console.log("Response data:", data); // Debug log

    if (data.label && data.probability !== undefined) {
      let prob = parseFloat(data.probability);
      const labelLower = data.label.toLowerCase();
      
      // Calculate confidence
      let confidence = prob;
      if (labelLower === "benign") {
        confidence = 1 - prob;
      }

      const confidencePercent = (confidence * 100).toFixed(2);
      resultDisplay.textContent = `${data.label} (Confidence: ${confidencePercent}%)`;
      
      console.log(`Label: ${data.label}, Prob: ${prob}, Confidence: ${confidencePercent}%`); // Debug log
    } else {
      resultDisplay.textContent = "Error: " + (data.error || "Unknown error");
    }
  } catch (err) {
    console.error("Fetch error:", err); // Debug log
    resultDisplay.textContent = "Request failed: " + err.message;
  }
}

const checkbox = document.getElementById('theme-checkbox');
const icon = document.getElementById('themeIcon');

const setTheme = (isDark) => {
  if (isDark) {
    document.body.classList.add('dark-mode');
    document.body.classList.remove('light-mode');
    icon.src = '/static/icons/dark_mode.svg';
  } else {
    document.body.classList.add('light-mode');
    document.body.classList.remove('dark-mode');
    icon.src = '/static/icons/light_mode.svg';
  }
  localStorage.setItem('darkMode', isDark ? 'true' : 'false');
};

checkbox.addEventListener('change', () => {
  setTheme(checkbox.checked);
});

// Load saved preference
window.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('darkMode') === 'true';
  checkbox.checked = saved;
  setTheme(saved);
});




