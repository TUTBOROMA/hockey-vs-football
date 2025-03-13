function submitQuiz() {
    const form = document.getElementById("quiz-form");
    const formData = new FormData(form);
    let quizResults = {};
    // Собираем все ответы, кроме скрытого поля
    for (let [key, value] of formData.entries()) {
        if (key !== "quiz_data") {
            quizResults[key] = value;
        }
    }
    document.getElementById("quiz_data").value = JSON.stringify(quizResults);
    form.submit();
}
