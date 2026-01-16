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
