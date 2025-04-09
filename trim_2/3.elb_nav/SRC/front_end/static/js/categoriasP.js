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

// En static/js/categoriasP.js, dentro del DOMContentLoaded

const agregarBotones = document.querySelectorAll('.btn-agregar-lista'); // Selecciona por la nueva clase

agregarBotones.forEach(button => {
    button.addEventListener('click', function() {
        const productId = this.dataset.productId; // Obtiene el _id del atributo data-product-id

        if (!productId) {
            console.error("No se encontró el ID del producto en el botón.");
            showMessage("❌ Error: No se pudo identificar el producto.");
            return;
        }

        // Opcional: Deshabilitar botón para evitar clics repetidos
        button.disabled = true;
        const originalText = button.textContent;
        button.textContent = 'Agregando...';

        fetch(`/agregar_a_lista/${productId}`, { // Llama al nuevo endpoint
            method: 'POST',
            headers: {
                // La cookie de sesión se envía automáticamente por el navegador
            }
        })
        .then(response => {
            // Es importante verificar si la respuesta fue exitosa (status 2xx)
            if (!response.ok) {
                // Si no fue exitosa, intenta leer el error del cuerpo JSON
                return response.json().then(err => {
                    // Lanza un error con el mensaje del backend o un mensaje genérico
                    throw new Error(err.detail || `Error ${response.status}`);
                });
            }
            // Si fue exitosa, parsea la respuesta JSON
            return response.json();
        })
        .then(data => {
            // Éxito: Muestra el mensaje del backend
            console.log(data.message);
            // Usa tu función showMessage para notificar al usuario
            showMessage(`✅ ${data.message || 'Producto agregado'}`);
        })
        .catch(error => {
            // Error: Muestra el mensaje de error
            console.error('Error al agregar producto:', error);
            showMessage(`❌ Error: ${error.message}`);
        })
        .finally(() => {
            // Siempre se ejecuta, re-habilita el botón
            button.disabled = false;
            button.textContent = originalText; // Restaura texto original
        });
    });
});

// --- Asegúrate de tener tu función showMessage definida ---
// (La que usas para los favoritos, adaptada si es necesario)
function showMessage(msg) {
    const messageBox = document.querySelector('.message'); // Asegúrate que este selector exista
    const closeBtn = messageBox ? messageBox.querySelector('.message__close-btn') : null;
    const progressBar = messageBox ? messageBox.querySelector('.message__progress-bar') : null;
    let messageTimeout;

    if (!messageBox) {
        console.warn("Elemento .message no encontrado para mostrar notificaciones.");
        return;
    }

    // Actualiza el texto (considera si hay otros nodos dentro)
    const textNode = messageBox.firstChild;
    if (textNode && textNode.nodeType === Node.TEXT_NODE) {
        textNode.nodeValue = msg + " ";
    } else {
         // Si no hay nodo de texto o es otra cosa, inserta al principio
         const spanText = document.createElement('span');
         spanText.textContent = msg + " ";
         // Elimina texto anterior si existe para evitar duplicados
         while (messageBox.firstChild && messageBox.firstChild !== closeBtn && messageBox.firstChild !== progressBar) {
             messageBox.removeChild(messageBox.firstChild);
         }
         messageBox.prepend(spanText);
    }

    messageBox.classList.add('show');

    if (progressBar) {
        progressBar.style.animation = 'none'; // Resetea animación
        progressBar.offsetHeight; /* Forzar reflow */
        progressBar.style.animation = null;
        progressBar.style.animation = 'progress 3s linear forwards'; // Reinicia animación CSS
    }

    clearTimeout(messageTimeout);
    messageTimeout = setTimeout(() => {
        messageBox.classList.remove('show');
    }, 3000); // Oculta después de 3 segundos

    // Asegura que el botón de cerrar funcione (solo añade el listener una vez)
    if (closeBtn && !closeBtn.dataset.listenerAttached) {
         closeBtn.addEventListener('click', () => {
            messageBox.classList.remove('show');
            clearTimeout(messageTimeout);
         });
         closeBtn.dataset.listenerAttached = 'true'; // Marca que ya tiene listener
    }
}
