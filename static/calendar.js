document.addEventListener("DOMContentLoaded", function() {
    const calendarDays = document.getElementById("calendarDays");
    const monthYear = document.getElementById("monthYear");
    const prevMonth = document.getElementById("prevMonth");
    const nextMonth = document.getElementById("nextMonth");

    let currentDate = initialDate;

    function renderCalendar() {
        calendarDays.innerHTML = "";
        const month = currentDate.getMonth();
        const year = currentDate.getFullYear();

        monthYear.textContent = currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" });

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Adjust firstDay to make Monday the first day of the week
        const startDay = (firstDay === 0 ? 6 : firstDay - 1);

        // Add empty divs for the start day
        for (let i = 0; i < startDay; i++) {
            const emptyDiv = document.createElement("div");
            emptyDiv.classList.add("calendar-day");
            calendarDays.appendChild(emptyDiv);
        }

        // Add the days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayDiv = document.createElement("div");
            const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
            
            dayDiv.classList.add("calendar-day");
            dayDiv.textContent = day;
            
            if (journalEntries[dateStr]) {
                dayDiv.setAttribute("data-entry", "true");
                dayDiv.addEventListener("click", () => {
                    window.location.href = `/entry/${journalEntries[dateStr]}`;
                });
            }

            calendarDays.appendChild(dayDiv);
        }
    }

    prevMonth.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextMonth.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    renderCalendar();
});
