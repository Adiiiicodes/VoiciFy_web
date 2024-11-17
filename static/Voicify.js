// JavaScript for VoxiFy Interactivity

const rateInput = document.getElementById("rate");
const rateValue = document.getElementById("rate-value");
const maleInput = document.getElementById("male");
const femaleInput = document.getElementById("female");
const textInput = document.getElementById("text-input");
const pdfUpload = document.getElementById("pdf-upload");
const convertButton = document.getElementById("convert");
const playButton = document.getElementById("play");
const downloadButton = document.getElementById("download");
const languageSelect = document.getElementById("language-select"); // Add this for language selection

let audioUrl = null;

// Update speech rate dynamically
rateInput.addEventListener("input", () => {
  rateValue.textContent = `${rateInput.value}x`;
});

// Change background based on selected voice
function updateBackground() {
  if (maleInput.checked) {
    document.body.classList.add("male-selected");
    document.body.classList.remove("female-selected");
  } else if (femaleInput.checked) {
    document.body.classList.add("female-selected");
    document.body.classList.remove("male-selected");
  }
}

maleInput.addEventListener("change", updateBackground);
femaleInput.addEventListener("change", updateBackground);

// Convert Text to Speech via Backend
convertButton.addEventListener("click", async () => {
  const text = textInput.value.trim();
  const language = languageSelect ? languageSelect.value : 'en'; // Get selected language, default to 'en' if not selected

  // Check if text is entered
  if (!text) {
    alert("Please enter text to convert.");
    return;
  }

  try {
    const response = await fetch('/convert', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        language: language
      })
    });

    if (!response.ok) {
      throw new Error("Failed to convert text to speech.");
    }

    // Get the audio file URL
    audioUrl = URL.createObjectURL(await response.blob());

    // Enable play and download buttons
    playButton.disabled = false;
    downloadButton.disabled = false;

    alert("Text converted to speech successfully!");
  } catch (error) {
    console.error(error);
    alert("Error converting text to speech.");
  }
});


// Play the Converted Audio
playButton.addEventListener("click", () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play()
        .catch(error => {
          console.error("Error playing audio:", error);
          alert("There was an issue playing the audio: " + error.message);
        });
    }
  });
  

// Download the Converted Audio
downloadButton.addEventListener("click", () => {
  if (audioUrl) {
    const link = document.createElement("a");
    link.href = audioUrl;
    link.download = "speech.mp3"; // Set default download file name
    link.click();
  }
});
