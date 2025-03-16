document.addEventListener("DOMContentLoaded", function () {
    // 📌 1️⃣ Manejo de Carrusel
    const carousels = document.querySelectorAll(".carousel-container");

    carousels.forEach((container) => {
        const carousel = container.querySelector(".carousel");
        const leftArrow = container.querySelector(".arrow.left");
        const rightArrow = container.querySelector(".arrow.right");

        if (carousel && leftArrow && rightArrow) {
            const scrollStep = 300; // Cantidad de píxeles que se moverá el carrusel

            leftArrow.addEventListener("click", function () {
                carousel.scrollBy({ left: -scrollStep, behavior: "smooth" });
            });

            rightArrow.addEventListener("click", function () {
                carousel.scrollBy({ left: scrollStep, behavior: "smooth" });
            });
        }
    });

    // 📌 2️⃣ Manejo de Favoritos
    const favoriteButtons = document.querySelectorAll(".favorite");
    favoriteButtons.forEach(button => {
        button.addEventListener("click", function () {
            this.classList.toggle("active"); // Alternar la clase "active"
        });
    });

    // 📌 3️⃣ Manejo de Calificación de Estrellas
    const starContainers = document.querySelectorAll(".stars");

    starContainers.forEach(starsDiv => {
        const stars = starsDiv.querySelectorAll(".star");

        stars.forEach(star => {
            star.addEventListener("mouseover", function () {
                const rating = this.getAttribute("data-value");
                highlightStars(stars, rating);
            });

            star.addEventListener("click", function () {
                const rating = this.getAttribute("data-value");
                starsDiv.setAttribute("data-rating", rating);
                highlightStars(stars, rating, true);
            });

            starsDiv.addEventListener("mouseleave", function () {
                const selectedRating = starsDiv.getAttribute("data-rating");
                highlightStars(stars, selectedRating);
            });
        });
    });

    function highlightStars(stars, rating, permanent = false) {
        stars.forEach(star => {
            if (star.getAttribute("data-value") <= rating) {
                star.classList.add("active");
            } else {
                if (!permanent) star.classList.remove("active");
            }
        });
    }
});