const attackForm = document.querySelector(".attack-form");

if (attackForm) {
    const cardInputs = attackForm.querySelectorAll(".attack-card__input");
    const defenderSelect = attackForm.querySelector(".attack-form__select");
    const submitButton = attackForm.querySelector(".attack-form__submit");
    const errorMessage = attackForm.querySelector("[data-error]");

    function updateSubmitState() {
        const cardSelected = attackForm.querySelector(".attack-card__input:checked");
        const defenderSelected = defenderSelect && defenderSelect.value !== "";
        submitButton.disabled = !(cardSelected && defenderSelected);
    }

    cardInputs.forEach((input) => {
        input.addEventListener("change", () => {
            attackForm
                .querySelectorAll(".attack-card__label")
                .forEach((label) => label.classList.remove("attack-card--selected"));

            input.closest(".attack-card__label").classList.add("attack-card--selected");

            if (errorMessage) errorMessage.hidden = true;
            updateSubmitState();
        });
    });

    if (defenderSelect) {
        defenderSelect.addEventListener("change", () => {
            if (errorMessage) errorMessage.hidden = true;
            updateSubmitState();
        });
    }

    attackForm.addEventListener("submit", (event) => {
        const cardSelected = attackForm.querySelector(".attack-card__input:checked");
        const defenderSelected = defenderSelect && defenderSelect.value !== "";

        if (!cardSelected || !defenderSelected) {
            event.preventDefault();
            if (errorMessage) errorMessage.hidden = false;
        }
    });
}