async function getRecommendation() {
    const hand = document.getElementById("hand").value;
    const position = document.getElementById("position").value;
    const stack = parseInt(document.getElementById("stack").value);

    const response = await fetch("https://preflop-zon3.onrender.com/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hand, position, stack, context: "auto" })
    });

    const data = await response.json();
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
}
