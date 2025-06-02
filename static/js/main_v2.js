document.addEventListener("DOMContentLoaded", function () {
  // Elements
  const reviewText = document.getElementById("review-text");
  const analyzeBtn = document.getElementById("analyze-btn");
  const clearBtn = document.getElementById("clear-btn");
  const resultsContainer = document.getElementById("results-container");
  const sentimentIcon = document.getElementById("sentiment-icon");
  const sentimentText = document.getElementById("sentiment-text");
  const confidenceText = document.getElementById("confidence-text");
  const correctBtn = document.getElementById("correct-btn");
  const incorrectBtn = document.getElementById("incorrect-btn");
  const modelStatus = document.getElementById("model-status");
  const charCount = document.getElementById("char-count");

  const MAX_CHARS = 500;
  let currentToast = null;

  // Character counter
  reviewText.addEventListener("input", function () {
    const length = this.value.length;
    charCount.textContent = length;
    
    if (length > MAX_CHARS) {
      this.value = this.value.substring(0, MAX_CHARS);
      charCount.textContent = MAX_CHARS;
      showToast("warning", "Maximum character limit reached");
    }
  });

  // Clear button
  clearBtn.addEventListener("click", function () {
    reviewText.value = "";
    charCount.textContent = "0";
    resultsContainer.style.display = "none";
  });

  // Check model service status
  async function checkModelService() {
    try {
      const response = await fetch("/info");
      const data = await response.json();
      
      if (data.model_service_status === "connected") {
        modelStatus.innerHTML = '<i class="fas fa-circle"></i><span>Connected</span>';
        modelStatus.classList.add("connected");
        modelStatus.classList.remove("disconnected");
      } else {
        modelStatus.innerHTML = '<i class="fas fa-circle"></i><span>Disconnected</span>';
        modelStatus.classList.add("disconnected");
        modelStatus.classList.remove("connected");
      }
    } catch (error) {
      modelStatus.innerHTML = '<i class="fas fa-circle"></i><span>Error</span>';
      modelStatus.classList.add("disconnected");
      modelStatus.classList.remove("connected");
    }
  }

  // Toast notification system
  function showToast(type, message) {
    if (currentToast) {
      currentToast.remove();
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon;
    switch (type) {
      case "success":
        icon = "check-circle";
        break;
      case "error":
        icon = "times-circle";
        break;
      case "warning":
        icon = "exclamation-circle";
        break;
      default:
        icon = "info-circle";
    }

    toast.innerHTML = `
      <i class="fas fa-${icon}"></i>
      <span>${message}</span>
    `;

    document.body.appendChild(toast);
    currentToast = toast;

    // Trigger reflow to enable transition
    toast.offsetHeight;
    toast.classList.add("visible");

    setTimeout(() => {
      toast.classList.remove("visible");
      setTimeout(() => toast.remove(), 300);
      currentToast = null;
    }, 3000);
  }

  // Analyze sentiment
  analyzeBtn.addEventListener("click", async function () {
    const review = reviewText.value.trim();
    
    if (!review) {
      showToast("warning", "Please enter a review first");
      return;
    }

    try {
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Analyzing...</span>';
      
      const response = await fetch("/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ review }),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze review");
      }

      const data = await response.json();
      
      // Update UI with results
      resultsContainer.style.display = "block";
      
      sentimentIcon.innerHTML = data.sentiment === "positive" 
        ? '<i class="fas fa-smile"></i>'
        : '<i class="fas fa-frown"></i>';
      sentimentIcon.className = `sentiment-icon ${data.sentiment}`;
      
      sentimentText.textContent = `Sentiment: ${data.sentiment}`;
      confidenceText.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
      
      showToast("success", "Analysis complete!");
    } catch (error) {
      showToast("error", "Failed to analyze review. Please try again.");
      console.error("Analysis error:", error);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<i class="fas fa-magic"></i><span>Analyze Sentiment</span>';
    }
  });

  // Feedback handling
  correctBtn.addEventListener("click", function() {
    showToast("success", "Thank you for your feedback!");
  });

  incorrectBtn.addEventListener("click", function() {
    showToast("info", "Thank you for helping us improve!");
  });

  // Initial model service check
  checkModelService();
  
  // Periodic status check
  setInterval(checkModelService, 30000);
}); 