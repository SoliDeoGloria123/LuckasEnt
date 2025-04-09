// En Eliminar.js

window.eliminarProducto = function (botonEliminar) {
    const productoItem = botonEliminar.closest('.card, .card2, .producto-item'); // Busca el contenedor padre
    const productId = botonEliminar.dataset.productId; // Obtiene el _id del atributo data-*

    if (productoItem && productId) {
        // Opcional: Deshabilitar botón para evitar clics repetidos
        botonEliminar.disabled = true;
        const icono = botonEliminar.querySelector('img'); // Guarda el icono si existe
        if (icono) icono.style.opacity = '0.5'; // Atenua el icono

        fetch(`/eliminar_de_lista/${productId}`, { // Llama al endpoint de eliminar
            method: 'POST', // o 'DELETE' si configuraste así el backend
            headers: {
                // La cookie de sesión se envía automáticamente
            }
        })
            .then(response => {
                if (!response.ok) {
                    // Si hay error, intenta obtener el mensaje del backend
                    return response.json().then(err => { throw new Error(err.detail || `Error ${response.status}`); });
                }
                // Si la respuesta es OK, parsea el JSON
                return response.json();
            })
            .then(data => {
                // Éxito: El backend eliminó el producto de la lista
                console.log(data.message);
                // Ahora sí, elimina el elemento del DOM
                productoItem.remove();
                // Recalcula el total
                calcularTotal();
                // alert("Producto eliminado"); // Opcional
            })
            .catch(error => {
                // Error en la petición fetch o en la respuesta del backend
                console.error("Error al eliminar:", error);
                alert(`Error al eliminar el producto: ${error.message}`);
                // Habilita el botón de nuevo si falló
                botonEliminar.disabled = false;
                if (icono) icono.style.opacity = '1'; // Restaura opacidad del icono
            });

    } else {
        console.error("No se pudo encontrar el producto o su ID para eliminar.");
        if (!productId) console.error("Asegúrate que el botón eliminar tenga el atributo 'data-product-id'");
        alert("Error interno al intentar eliminar el producto."); // Mensaje para el usuario
    }
}

// --- Asegúrate que la función calcularTotal esté actualizada ---
// Si usaste clases genéricas en cardgrid.html, ajústala aquí también
function calcularTotal() {
    // Usa selectores más genéricos si estandarizaste las clases en cardgrid.html
    const productos = document.querySelectorAll('.card, .card2, .producto-item');
    let total = 0;

    productos.forEach(producto => {
        // Intenta encontrar el precio en '.product-details' o en las clases específicas originales
        const detalleElement = producto.querySelector('.product-details, .makro-7-000-2, .isimo-12-000-3, .existo-17-000-2-1');

        if (detalleElement) {
            const textoDetalle = detalleElement.textContent;
            // Intenta extraer el precio total o el de oferta
            let match = textoDetalle.match(/\$\s?([\d.,]+)/); // Precio normal
            if (!match) {
                match = textoDetalle.match(/Oferta:\s*\$\s?([\d.,]+)/); // Precio oferta
            }

            if (match && match[1]) {
                // Limpia puntos y comas, luego convierte a número
                const precioNumerico = parseFloat(match[1].replace(/[.,]/g, ''));
                if (!isNaN(precioNumerico)) {
                    total += precioNumerico;
                } else {
                    console.warn("Precio no numérico:", match[1], "en:", textoDetalle);
                }
            } else {
                console.warn("Formato de precio no encontrado en:", textoDetalle);
            }
        } else {
            console.warn("Elemento de precio/detalles no encontrado en:", producto);
        }
    });

    const totalElement = document.getElementById('precioTotal');
    if (totalElement) {
        // Formatea como moneda colombiana
        totalElement.textContent = total.toLocaleString('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 });
    } else {
        console.error("Elemento con ID 'precioTotal' no encontrado.");
    }
}

// --- Asegúrate que la función para descargar PDF también use selectores genéricos si es necesario ---
// (El código de descarga de PDF en tu Eliminar.js ya usa clases específicas,
//  si cambiaste a genéricas en cardgrid.html, actualiza también los selectores aquí)
const btnDescargar = document.getElementById('btn-descargar');

if (btnDescargar) {
    btnDescargar.addEventListener('click', function () {
        if (typeof jspdf === 'undefined') {
            console.warn('jsPDF no está cargado');
            return;
        }

        const { jsPDF } = jspdf;
        const doc = new jsPDF();
        let y = 15;

        // Título
        doc.setFontSize(20);
        doc.text("Mi Lista de Compras", 105, y, { align: 'center' });
        y += 20;

        // Productos
        doc.setFontSize(14);
        const productos = document.querySelectorAll('.card, .card2, .producto-item');

        productos.forEach((producto, index) => {
            if (y > 270) {
                doc.addPage();
                y = 15;
            }

            const nombreElement = producto.querySelector('.product-name, .lechuga-manojo-light, .papa-pastusa, .carne-para-asar');
            const detalleElement = producto.querySelector('.product-details, .makro-7-000-2, .isimo-12-000-3, .existo-17-000-2-1');
            const pesoElement = producto.querySelector('.peso');

            const nombre = nombreElement ? nombreElement.textContent.trim() : 'Producto Desconocido';
            const detalle = detalleElement ? detalleElement.textContent.trim() : 'Detalle Desconocido';
            const peso = pesoElement ? pesoElement.textContent.trim() : '';

            // Construye la línea completa para evitar que se encime
            let textoCompleto = `${index + 1}. ${nombre} - ${detalle}`;
            if (peso) {
                textoCompleto += ` | ${peso}`;
            }

            // Imprime toda la línea de producto
            const lineas = doc.splitTextToSize(textoCompleto, 180); // Por si se pasa de ancho
            doc.text(lineas, 15, y);
            y += lineas.length * 8 + 4; // Aumenta según el número de líneas generadas
        });

        // Total
        const totalTexto = document.getElementById('precioTotal').textContent;
        if (y > 270) {
            doc.addPage();
            y = 15;
        }

        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.text(`Total Estimado: ${totalTexto}`, 15, y + 5);

        doc.save('mi_lista_compras.pdf');
    });
}

// Llama a calcularTotal al cargar la página
document.addEventListener('DOMContentLoaded', calcularTotal);
