document.addEventListener("DOMContentLoaded", () => {
  // ===== FILTROS DESPLEGABLES EN SIDEBAR =====
  // Seleccionar todas las secciones de filtros
  const filterSections = document.querySelectorAll(".filter-section")

  // Para cada sección de filtro
  filterSections.forEach((section) => {
    // Obtener el título y el contenido
    const title = section.querySelector(".filter-title")
    let content

    // Determinar qué tipo de contenido tiene esta sección
    if (section.querySelector(".category-list")) {
      content = section.querySelector(".category-list")
    } else if (section.querySelector(".checkbox-list")) {
      content = section.querySelector(".checkbox-list")
    } else if (section.querySelector(".location-list")) {
      content = section.querySelector(".location-list")
    }

    // Si encontramos contenido, hacerlo desplegable
    if (content && title) {
      // Agregar flecha al título
      title.innerHTML += ' <i class="fas fa-chevron-down"></i>'
      title.style.cursor = "pointer"
      title.style.display = "flex"
      title.style.justifyContent = "space-between"
      title.style.alignItems = "center"

      // Estado inicial: desplegado
      let isExpanded = true

      // Agregar evento de clic al título
      title.addEventListener("click", () => {
        // Cambiar el estado
        isExpanded = !isExpanded

        // Mostrar u ocultar el contenido
        if (isExpanded) {
          content.style.maxHeight = content.scrollHeight + "px"
          content.style.opacity = "1"
          title.querySelector("i").className = "fas fa-chevron-down"
        } else {
          content.style.maxHeight = "0"
          content.style.opacity = "0"
          title.querySelector("i").className = "fas fa-chevron-up"
        }
      })

      // Establecer el estado inicial: desplegado
      content.style.maxHeight = content.scrollHeight + "px"
      content.style.opacity = "1"
      content.style.overflow = "hidden"
      content.style.transition = "max-height 0.3s ease, opacity 0.3s ease"
    }
  })

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

  // Script para mostrar mensaje al agregar productos
  document.querySelectorAll(".product-card__btn--primary").forEach((btn) => {
    btn.addEventListener("click", () => {
      showMessage("Producto añadido al carrito")
    })
  })
})