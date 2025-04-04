document.addEventListener("DOMContentLoaded", function () {
    function eliminarProducto(boton) {
        // Mostrar alerta de confirmación
        if (!confirm("¿Estás seguro de que quieres eliminar este producto?")) {
            return; // Si el usuario cancela, no hace nada
        }

        // Obtener el contenedor del producto
        let producto = boton.closest(".producto-item");
        let precioTexto = producto.querySelector(".producto-info p").textContent;
        
        // Extraer el precio del texto
        let precio = parseInt(precioTexto.match(/\$\d+/)[0].replace("$", ""));

        // Eliminar el producto de la lista
        producto.remove();

        // Actualizar el contador de productos
        let contadorElement = document.getElementById("contador");
        let contador = parseInt(contadorElement.textContent);
        contadorElement.textContent = contador - 1;

        // Actualizar el precio total
        let precioTotalElement = document.getElementById("precioTotal");
        let precioTotal = parseInt(precioTotalElement.textContent.replace("$", "").replace(".", ""));
        precioTotal -= precio;
        precioTotalElement.textContent = `$${precioTotal.toLocaleString()}`;

        // Mostrar alerta de eliminación exitosa
        alert("El producto ha sido eliminado de la lista.");
    }

    // Asignar evento a todos los botones de eliminar
    document.querySelectorAll(".btn-eliminar").forEach(boton => {
        boton.addEventListener("click", function () {
            eliminarProducto(this);
        });
    });
});
document.getElementById("btn-descargar").addEventListener("click", function () {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    doc.setFont("helvetica", "bold");
    doc.text("Lista de Productos", 20, 20);

    let productos = document.querySelectorAll(".producto-item");
    let y = 40; // Posición inicial en el PDF

    productos.forEach((producto, index) => {
        let nombre = producto.querySelector("h3").textContent;
        let precio = producto.querySelector(".producto-info p").textContent;

        doc.setFont("helvetica", "normal");
        doc.text(`${index + 1}. ${nombre} - ${precio}`, 20, y);
        y += 10;
    });

    doc.text(`Total estimado: ${document.getElementById("precioTotal").textContent}`, 20, y + 10);

    doc.save("Lista_de_productos.pdf");
});
