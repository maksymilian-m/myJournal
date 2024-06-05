document.addEventListener('DOMContentLoaded', () => {
    const quoteText = "The soul becomes dyed with the color of its thoughts.";
    let index = 0;

    function typeWriter() {
        if (index < quoteText.length) {
            document.getElementById("quote").innerHTML += quoteText.charAt(index);
            index++;
            setTimeout(typeWriter, 100); // Adjust typing speed
        }
    }

    typeWriter();
});