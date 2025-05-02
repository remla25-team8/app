document.addEventListener("DOMContentLoaded", function () {
  const reviewText = document.getElementById("review-text");
  const analyzeBtn = document.getElementById("analyze-btn");
  const resultsContainer = document.getElementById("results-container");
  const sentimentIcon = document.getElementById("sentiment-icon");
  const sentimentText = document.getElementById("sentiment-text");
  const correctBtn = document.getElementById("correct-btn");
  const incorrectBtn = document.getElementById("incorrect-btn");
  const modelStatus = document.getElementById("model-status");

  checkModelStatus();

  // These are someevent listeners
  analyzeBtn.addEventListener("click", analyzeSentiment);
  correctBtn.addEventListener("click", () => submitFeedback(true));
  incorrectBtn.addEventListener("click", () => submitFeedback(false));

  let currentReviewData = null;

  // Check model service status
  function checkModelStatus() {
    fetch("/info")
      .then((response) => response.json())
      .then((data) => {
        if (data.model_service_info && !data.model_service_info.error) {
          modelStatus.textContent = "Connected";
          modelStatus.classList.add("connected");
        } else {
          modelStatus.textContent = "Disconnected";
          modelStatus.classList.add("disconnected");
        }
      })
      .catch((error) => {
        console.error("Error checking model status:", error);
        modelStatus.textContent = "Disconnected";
        modelStatus.classList.add("disconnected");
      });
  }

  function analyzeSentiment() {
    if (!reviewText.value.trim()) {
      alert("Please enter a review to analyze");
      return;
    }

    analyzeBtn.textContent = "Analyzing...";
    analyzeBtn.disabled = true;

    fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        review: reviewText.value,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        currentReviewData = data;

        resultsContainer.style.display = "block";

        if (data.sentiment === "positive") {
          sentimentIcon.className = "sentiment-icon positive-sentiment";
          sentimentText.textContent = "This review appears to be Positive!";
        } else {
          sentimentIcon.className = "sentiment-icon negative-sentiment";
          sentimentText.textContent = "This review appears to be Negative.";
        }

        analyzeBtn.textContent = "Analyze Sentiment";
        analyzeBtn.disabled = false;
      })
      .catch((error) => {
        console.error("Error analyzing sentiment:", error);
        alert(
          "An error occurred while analyzing the review. Please try again later."
        );

        analyzeBtn.textContent = "Analyze Sentiment";
        analyzeBtn.disabled = false;
      });
  }

  function submitFeedback(isCorrect) {
    if (!currentReviewData) {
      return;
    }

    if (isCorrect) {
      alert("Thank you for your feedback!");
    } else {
      const actualSentiment = currentReviewData.prediction === 1 ? 0 : 1;

      fetch("/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          review: currentReviewData.review,
          prediction: currentReviewData.prediction,
          actual_sentiment: actualSentiment,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          alert(
            "Thank you for your feedback! We will use it to improve our model."
          );
        })
        .catch((error) => {
          console.error("Error submitting feedback:", error);
          alert("An error occurred while submitting your feedback.");
        });
    }
  }
});
