document.addEventListener("DOMContentLoaded", function () {
    function eliminarProducto(boton) {
        // Obtener el contenedor del producto
        let producto = boton.closest(".producto-item");
        let precioTexto = producto.querySelector(".producto-info p").textContent;
        
        // Extraer el precio del texto (asumiendo que siempre está antes del "|")
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
    }

    // Asignar evento a todos los botones de eliminar
    document.querySelectorAll(".btn-eliminar").forEach(boton => {
        boton.addEventListener("click", function () {
            eliminarProducto(this);
        });
    });
});
