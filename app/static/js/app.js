const workspace = document.querySelector('.workspace');

function showAgendamiento() {
    workspace.innerHTML = `
        <h2>Cruce Agendamiento</h2>
        <form method="post" action="/agendamiento/procesar" enctype="multipart/form-data">
            <div class="form-group">
                <label>Export Bitrix</label>
                <input type="file" name="export_file" accept=".xls,.xlsx" required>
            </div>

            <div class="form-group">
                <label>Base Manager</label>
                <input type="file" name="base_file" accept=".xls,.xlsx" required>
            </div>

            <button type="submit">Procesar</button>
        </form>
    `;
}

function showInventario() {
    workspace.innerHTML = `
        <h2>Inventario de Cajas</h2>

        <form id="inventarioForm">
            <div class="form-group">
                <label>Archivo de Ventas</label>
                <input type="file" name="file" accept=".xls,.xlsx" required>
            </div>

            <button type="submit">Procesar</button>
        </form>
    `;

    const form = document.getElementById("inventarioForm");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const fileInput = form.querySelector('input[type="file"]');
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const response = await fetch("/inventario/procesar", {
            method: "POST",
            body: formData
        });

        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "Inventario_Cajas.xlsx";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    });
}

