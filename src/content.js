(function () {
  function findBannerText() {
    const nodes = Array.from(document.querySelectorAll("div, section, aside, footer, dialog,[role='dialog']"));
    const found = nodes.find(el => /cookie|consent|privacy/i.test(el.innerText));
    return found ? found.innerText.slice(0, 2000) : null;
  }

  async function sendToBackend(text) {
    try {
      const res = await fetch("http://127.0.0.1:8000/negotiate-consent", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          domain: location.hostname,
          banner_text: text,
          user_preferences: { ads: false, analytics: true, functional: true, personalization: false }
        })
      });
      const data = await res.json();
      console.log("AI Consent Response:", data);
    } catch (e) {
      console.error("ConsentCanvas backend error:", e);
    }
  }

  window.addEventListener("load", () => {
    setTimeout(() => {
      const text = findBannerText();
      if (text) {
        console.log("ConsentCanvas banner text found, sending to backend…");
        sendToBackend(text);
      } else {
        console.log("ConsentCanvas: no banner detected");
      }
    }, 3000);
  });
})();


