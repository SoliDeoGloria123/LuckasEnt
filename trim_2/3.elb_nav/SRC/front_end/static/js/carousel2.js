/*document.addEventListener("DOMContentLoaded", function () {
    // 📌 1️⃣ Manejo de Carrusel
    const carousels = document.querySelectorAll(".carousel-container");

    carousels.forEach((container) => {
        const carousel = container.querySelector(".favoritos-carousel"); // Asegurar que se toma el carrusel correcto
        const leftArrow = container.querySelector(".arrow.left");
        const rightArrow = container.querySelector(".arrow.right");

        if (carousel && leftArrow && rightArrow) {
            const cardWidth = carousel.querySelector(".favorito-card").offsetWidth + 20; // Ancho de tarjeta + margen
            const visibleCards = 3;
            const scrollStep = cardWidth * visibleCards; // Mueve 3 tarjetas a la vez

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
                highlightStars(stars, this.getAttribute("data-value"));
            });

            star.addEventListener("click", function () {
                starsDiv.setAttribute("data-rating", this.getAttribute("data-value"));
                highlightStars(stars, this.getAttribute("data-value"), true);
            });

            starsDiv.addEventListener("mouseleave", function () {
                highlightStars(stars, starsDiv.getAttribute("data-rating"));
            });
        });
    });

    function highlightStars(stars, rating, permanent = false) {
        stars.forEach(star => {
            if (star.getAttribute("data-value") <= rating) {
                star.classList.add("active");
            } else if (!permanent) {
                star.classList.remove("active");
            }
        });
    }
});*/
document.addEventListener("DOMContentLoaded", function () {
    // 📌 Manejo de Carrusel
    const carousels = document.querySelectorAll(".carousel-container");

    carousels.forEach((container) => {
        const carousel = container.querySelector(".carousel, .favoritos-carousel"); // Detecta ambos tipos de carruseles
        const leftArrow = container.querySelector(".arrow.left");
        const rightArrow = container.querySelector(".arrow.right");

        if (carousel && leftArrow && rightArrow) {
            const card = carousel.querySelector(".card, .favorito-card");
            if (!card) return; // Si no hay tarjetas, salimos
            
            const cardWidth = card.offsetWidth + 20; // Ancho de tarjeta + margen
            const visibleCards = Math.floor(container.offsetWidth / cardWidth);
            const scrollStep = cardWidth * visibleCards; // Mueve tantas tarjetas como entren en pantalla

            leftArrow.addEventListener("click", function () {
                carousel.scrollBy({ left: -scrollStep, behavior: "smooth" });
            });

            rightArrow.addEventListener("click", function () {
                carousel.scrollBy({ left: scrollStep, behavior: "smooth" });
            });
        }
    });

    // 📌 Manejo de Favoritos
    document.querySelectorAll(".favorite").forEach(button => {
        button.addEventListener("click", function () {
            this.classList.toggle("active");
        });
    });
      // ===== FAVORITOS Y MENSAJES =====
  // Manejo de botones de favoritos
  const favoriteBorders = document.querySelectorAll(".product-card__favorite-btn")

  favoriteBorders.forEach((favoriteBorder) => {
    favoriteBorder.addEventListener("click", function () {
      this.classList.toggle("liked")
      if (this.classList.contains("liked")) {
        showMessage("Se guardó satisfactoriamente este producto")
      }
    })
  })
  
  function showMessage(text) {
    const message = document.createElement("div")
    message.className = "message show"
    message.innerHTML = `${text} <span class="close-btn">&times;</span><div class="progress-bar"></div>`
    document.body.appendChild(message)

    const closeBtn = message.querySelector(".close-btn")
    closeBtn.addEventListener("click", () => {
      message.classList.remove("show")
      setTimeout(() => {
        document.body.removeChild(message)
      }, 500)
    })

    setTimeout(() => {
      message.classList.remove("show")
      setTimeout(() => {
        document.body.removeChild(message)
      }, 500)
    }, 2500)
  }

});

