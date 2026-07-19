const counterForm = document.querySelector(".counter-form");

if (counterForm) {
    const cardInputs = counterForm.querySelectorAll(".counter-card__input");
    const submitButton = counterForm.querySelector(".counter-form__submit");
    const errorMessage = counterForm.querySelector("[data-error]");

    cardInputs.forEach((input) => {
        input.addEventListener("change", () => {
            counterForm
                .querySelectorAll(".counter-card__label")
                .forEach((label) => label.classList.remove("counter-card--selected"));

            input.closest(".counter-card__label").classList.add("counter-card--selected");

            submitButton.disabled = false;

            if (errorMessage) {
                errorMessage.hidden = true;
            }
        });
    });

    counterForm.addEventListener("submit", (event) => {
        const selected = counterForm.querySelector(".counter-card__input:checked");

        if (!selected) {
            event.preventDefault();
            if (errorMessage) {
                errorMessage.hidden = false;
            }
        }
    });
}