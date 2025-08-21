// content.js

// Find the consent banner (adjust the selector as needed)
const banner = document.querySelector("div[role='dialog'], .cookie-banner, .consent, .cookie"); 
if (banner) {
  const payload = {
    html: banner.outerHTML,
    domain: window.location.hostname,
    timestamp: new Date().toISOString()
  };

  console.log("ConsentCanvas: sending payload to backend", payload);

  // Send to FastAPI backend
  fetch("http://127.0.0.1:8000/parse-consent", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => console.log("Backend response:", data))
  .catch(err => console.error("Fetch error:", err));
}

