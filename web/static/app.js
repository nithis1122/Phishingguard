const form = document.querySelector("#scan-form");
const input = document.querySelector("#scan-input");
const inputLabel = document.querySelector("#input-label");
const inputHint = document.querySelector("#input-hint");
const characterCount = document.querySelector("#char-count");
const result = document.querySelector("#result");
const scanButton = document.querySelector("#scan-button");
const modeTabs = [...document.querySelectorAll(".mode-tab")];

let kind = "url";

function setKind(nextKind) {
  kind = nextKind;
  const isEmail = kind === "email";
  inputLabel.textContent = isEmail ? "Paste the suspicious email text" : "Paste a link to check";
  inputHint.textContent = isEmail
    ? "Tip: paste the message text. Do not include passwords or private information."
    : "Tip: copy the link address without opening it.";
  input.placeholder = isEmail
    ? "Your account will be closed today. Verify your details..."
    : "https://example.com/account/verify";
  modeTabs.forEach((tab) => {
    const active = tab.dataset.kind === kind;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-pressed", String(active));
  });
}

modeTabs.forEach((tab) => tab.addEventListener("click", () => setKind(tab.dataset.kind)));
input.addEventListener("input", () => {
  characterCount.textContent = `${input.value.length.toLocaleString()} / 12,000`;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) {
    input.focus();
    return;
  }

  result.hidden = true;
  scanButton.disabled = true;
  scanButton.querySelector("span:first-child").textContent = "Checking patterns…";

  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, kind }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "The scan could not be completed.");
    }

    const state = payload.verdict === "likely_phishing"
      ? { className: "phishing", title: "Potential phishing detected" }
      : payload.verdict === "likely_safe"
        ? { className: "safe", title: "Fewer suspicious patterns found" }
        : { className: "suspicious", title: "Take a closer look" };
    result.className = `result ${state.className}`;
    result.replaceChildren();
    const heading = document.createElement("h3");
    heading.textContent = state.title;
    const description = document.createElement("p");
    description.textContent = payload.message;
    const score = document.createElement("span");
    score.className = "score";
    score.textContent = `Model risk score: ${payload.risk_score}% · ${payload.disclaimer}`;
    result.append(heading, description, score);
    result.hidden = false;
  } catch (error) {
    result.className = "result error";
    result.replaceChildren();
    const message = document.createElement("p");
    message.textContent = error instanceof Error ? error.message : "The scan could not be completed.";
    result.append(message);
    result.hidden = false;
  } finally {
    scanButton.disabled = false;
    scanButton.querySelector("span:first-child").textContent = "Scan for phishing";
  }
});
