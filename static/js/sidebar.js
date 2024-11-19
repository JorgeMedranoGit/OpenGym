document.querySelector('.toggle-sidebar-btn').addEventListener('click', function () {
    document.querySelector('.sidebar').classList.toggle('expanded');
});

document.querySelectorAll('.dynamic-div').forEach(function (div) {
    div.addEventListener('click', function () {
        div.classList.toggle('expanded');
    });
});

function handleResize() {
    if (window.innerWidth <= 768) {
        document.querySelector('.sidebar').classList.add('collapsed');
    } else {
        document.querySelector('.sidebar').classList.remove('collapsed');
    }
}

window.addEventListener('resize', handleResize);
window.addEventListener('load', handleResize);
/* function añadirProductoDesdeMaquina(idNombre, tipoMaquina, idEmpleado) {
    const cantidad = prompt("Ingrese la cantidad:");
    const precioUnitario = prompt("Ingrese el precio unitario:");

    // Obtener el nuevo nombre de máquina si se ha ingresado
    const nuevoNombre = document.getElementById('nuevoNombre').value.trim();
    const nuevoProveedorNombre = document.getElementById('nuevoProveedorNombre').value.trim();

    if (cantidad && precioUnitario) {
        const producto = {
            idNombre: idNombre,
            nombre: nuevoNombre || "Máquina " + idNombre, // Usa el nuevo nombre si se ingresó
            proveedor: nuevoProveedorNombre || "Proveedor X", // Usa el nuevo proveedor si se ingresó
            idEmpleado: idEmpleado,
            cantidad: parseInt(cantidad),
            precioUnitario: parseFloat(precioUnitario),
            tipoMaquina: tipoMaquina
        };

        // Agregar el producto a la lista
        productosSeleccionados.push(producto);
        mostrarProductos();
    } else {
        alert("Cantidad y precio unitario son requeridos.");
    }
} */