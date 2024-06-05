function updateWeeklyGoalValue(value) {
    document.getElementById("weekly-goal-value").innerText = value;
}

function togglePrompts(isEnabled) {
    const customizePromptsSection = document.getElementById("customize-prompts-section");
    if (isEnabled) {
        customizePromptsSection.style.display = "block";
    } else {
        customizePromptsSection.style.display = "none";
    }
}

function saveCustomPrompts() {
    const customPromptsInput = document.getElementById("custom-prompts-input").value.trim();
    if (customPromptsInput) {
        prompts = customPromptsInput.split(',').map(prompt => prompt.trim());
        alert('Custom prompts saved successfully!');
    }
}

function renderPrompts() {
    const promptsList = document.getElementById("prompts-list");
    promptsList.innerHTML = "";
    const prompts = JSON.parse(document.getElementById('promptsInput').textContent);
    prompts.forEach((prompt, index) => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `
            <input type="text" class="prompt-text" name="prompts[]" value="${prompt}" onchange="updatePrompt(${index}, this.value)">
            <button class="remove-prompt-btn" onclick="removePrompt(${index})">Remove</button>
        `;
        promptsList.appendChild(listItem);
    });
}

function updatePrompt(index, newValue) {
    prompts[index] = newValue;
}

function removePrompt(index) {
    prompts.splice(index, 1);
    renderPrompts();
}

function addPrompt() {
    const newPrompt = document.getElementById("new-prompt").value.trim();
    if (newPrompt) {
        prompts.push(newPrompt);
        document.getElementById("new-prompt").value = "";
        renderPrompts();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const isPromptsEnabled = document.getElementById("toggle-prompts").checked;
    togglePrompts(isPromptsEnabled);
    renderPrompts();
});
