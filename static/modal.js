 // Pass prompts to JavaScript
 const prompts = ["What are you grateful for today?",
    "What was the highlight of your day?",
    "What did you learn today?",
    "Describe a challenge you faced and how you overcame it.",
    "What made you smile today?"];
        
 // Get modal elements
 const modal = document.getElementById("promptModal");
 const span = document.getElementsByClassName("close")[0];
 const promptBtn = document.getElementById("prompt-btn");
 const promptText = document.getElementById("prompt-text");

 // Show a random prompt in the modal
 promptBtn.onclick = function() {
     const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)];
     promptText.textContent = randomPrompt;
     modal.style.display = "flex";
 }

 // Close the modal
 span.onclick = function() {
     modal.style.display = "none";
     // focus on the textarea at the end of text
     text = document.getElementsByTagName("textarea")[0];
     text.focus();
     text.selectionStart = text.value.length;
 }

 // Close the modal when clicking outside of it
 window.onclick = function(event) {
     if (event.target == modal) {
         modal.style.display = "none";
         // focus on the textarea at the end of text
         text = document.getElementsByTagName("textarea")[0];
         text.focus();
         text.selectionStart = text.value.length;
     }
 }