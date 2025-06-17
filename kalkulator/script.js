document.addEventListener("DOMContentLoaded", () => {
  const genderFemaleBtn = document.getElementById("gender_female");
  const genderMaleBtn = document.getElementById("gender_male");
  const competitionSelect = document.getElementById("competition");
  const kettlebellContainer = document.getElementById(
    "kettlebell_weight_container"
  );
  const bodyWeightInput = document.getElementById("body_weight");
  const repetitionsInput = document.getElementById("repetitions");
  const kettlebellWeightInput = document.getElementById("kettlebell_weight");
  const kettlebellWeightLabel = document.querySelector(
    'label[for="kettlebell_weight"]'
  );
  const calculateButton = document.getElementById("calculate_button");
  const resultOutput = document.getElementById("result_output");
  const errorOutput = document.getElementById("error_output");

  let selectedGender = "";

  function setGender(gender) {
    selectedGender = gender;
    if (gender === "female") {
      genderFemaleBtn.classList.add("active");
      genderMaleBtn.classList.remove("active");
    } else {
      genderMaleBtn.classList.add("active");
      genderFemaleBtn.classList.remove("active");
    }
  }

  function updateUI() {
    const competition = competitionSelect.value;
    // Pokaż pole powtórzeń dla snatch i pull_up
    kettlebellContainer.style.display = ["snatch"].includes(competition)
      ? "block"
      : "none";

    // Zaktualizuj etykietę wagi kettlebell w zależności od konkurencji
    if (["see_saw_press", "squat"].includes(competition)) {
      kettlebellWeightLabel.textContent =
        "Waga kettlebell (suma dwóch ciężarów):";
    } else {
      kettlebellWeightLabel.textContent = "Waga kettlebell:";
    }

    // Wyczyść pola formularza po zmianie konkurencji
    clearForm();
  }

  function clearForm() {
    bodyWeightInput.value = "";
    kettlebellWeightInput.value = "";
    repetitionsInput.value = "";
    resultOutput.innerText = "";
    errorOutput.innerText = "";
  }

  function calculatePoints() {
    // Krok 1: Wyczyść poprzednie wyniki i błędy.
    resultOutput.innerText = "";
    errorOutput.innerText = "";

    // Krok 2: Walidacja danych wejściowych.
    if (!selectedGender) {
      errorOutput.innerText = "Wybierz płeć.";
      return;
    }
    const bodyWeight = parseFloat(bodyWeightInput.value);
    const kettlebellWeight = parseFloat(kettlebellWeightInput.value);
    const repetitions = parseFloat(repetitionsInput.value) || 0;

    if (isNaN(kettlebellWeight) || kettlebellWeight <= 0) {
      errorOutput.innerText = "Wprowadź prawidłową wagę kettla.";
      return;
    }
    if (isNaN(bodyWeight) || bodyWeight <= 0) {
      errorOutput.innerText = "Wprowadź prawidłową wagę.";
      return;
    }

    // Krok 3: Wykonaj obliczenia w zależności od konkurencji.
    let points = 0;
    const competition = competitionSelect.value;

    try {
      switch (competition) {
        case "snatch":
          const calculatedResult = repetitions * kettlebellWeight;

          if (selectedGender === "female") {
            const bodyWeightPower = Math.pow(bodyWeight, 0.4);
            const referencePower = Math.pow(65, 0.4);

            points =
              (calculatedResult / bodyWeightPower) * (referencePower / 16);
          } else {
            const bodyWeightPower = Math.pow(bodyWeight, 0.4);
            const referencePower = Math.pow(85, 0.4);
            points =
              (calculatedResult / bodyWeightPower) * (referencePower / 24);
          }
          points = Math.floor((points + 0.25) / 0.5) * 0.5;
          break;
        case "pistol":
          if (selectedGender === "female")
            points =
              (kettlebellWeight / Math.pow(bodyWeight, 0.6)) *
              (Math.pow(65, 0.6) / 40);
          else
            points =
              (kettlebellWeight / Math.pow(bodyWeight, 0.67)) *
              (Math.pow(85, 0.67) / 60);
          break;
        case "see_saw_press":
          if (selectedGender === "female")
            points =
              (kettlebellWeight / Math.pow(bodyWeight, 0.6)) *
              (Math.pow(65, 0.6) / 48);
          else
            points =
              (kettlebellWeight / Math.pow(bodyWeight, 0.67)) *
              (Math.pow(85, 0.67) / 96);
          break;
        case "squat":
          if (selectedGender === "female")
            points =
              (kettlebellWeight / Math.pow(bodyWeight, 0.6)) *
              (Math.pow(65, 0.6) / 72);
          else
            points =
              (kettlebellWeight / Math.pow(bodyWeight, 0.67)) *
              (Math.pow(85, 0.67) / 120);
          break;
        case "tgu":
          let bodyWeightFactor, referenceFactor, divisor;

          if (selectedGender === "female") {
            bodyWeightFactor = Math.pow(bodyWeight, 0.6);
            referenceFactor = Math.pow(65, 0.6);
            divisor = 48;
            points =
              (kettlebellWeight / bodyWeightFactor) *
              (referenceFactor / divisor);
          } else {
            bodyWeightFactor = Math.pow(bodyWeight, 0.67);
            referenceFactor = Math.pow(85, 0.67);
            divisor = 80;
            points =
              (kettlebellWeight / bodyWeightFactor) *
              (referenceFactor / divisor);
          }
          break;
        case "pull_up":
          const finalWeight = bodyWeight + kettlebellWeight;
          if (selectedGender === "female")
            points =
              (finalWeight / Math.pow(bodyWeight, 0.6)) *
              (Math.pow(65, 0.6) / 100);
          else
            points =
              (finalWeight / Math.pow(bodyWeight, 0.67)) *
              (Math.pow(85, 0.67) / 150);
          break;
      }

      if (points < 0 || isNaN(points)) {
        throw new Error("Błąd w obliczeniach. Sprawdź dane wejściowe.");
      }

      // Krok 4: Wyświetl końcowy wynik.
      if (competition === "snatch") {
        resultOutput.innerText = `Finałowy rezultat: ${points.toFixed(1)} punktów`; // Display snatch result with 1 decimal place
      } else {
        resultOutput.innerText = `Finałowy rezultat: ${points.toFixed(
          3
        )} punktów`; // Wyświetla wynik z 3 miejscami po przecinku dla pozostałych konkurencji
      }
    } catch (e) {
      errorOutput.innerText = e.message;
    }
  }

  // --- EVENT LISTENERS ---
  genderFemaleBtn.addEventListener("click", () => setGender("female"));
  genderMaleBtn.addEventListener("click", () => setGender("male"));
  competitionSelect.addEventListener("change", updateUI);
  calculateButton.addEventListener("click", calculatePoints);

  // --- INICJALIZACJA ---
  setGender("female");
  updateUI();
});
