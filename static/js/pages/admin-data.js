/**
 * Admin: pestaña "Gestión de datos" — casos (CRUD) y carteras.
 */
(function () {
    'use strict';

    const CRED = { credentials: 'same-origin' };

    function apiFetch(url, options) {
        const opts = Object.assign({}, CRED, options || {});
        if (opts.body && typeof opts.body === 'string' && !(opts.headers && opts.headers['Content-Type'])) {
            opts.headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
        }
        return fetch(url, opts);
    }

    let casesPage = 1;
    const casesPerPage = 20;
    let searchDebounce = null;
    let selectsLoaded = false;

    function $(id) {
        return document.getElementById(id);
    }

    function openAdminDataTab(section) {
        switchAdminView('datos');
        const sec =
            section === 'carteras' ? 'carteras' : section === 'import' || section === 'csv' ? 'import' : 'casos';
        document.querySelectorAll('.data-subnav-btn').forEach((btn) => {
            btn.classList.toggle('active', btn.getAttribute('data-data-section') === sec);
        });
        const elCasos = $('data-section-casos');
        const elCarteras = $('data-section-carteras');
        const elImport = $('data-section-import');
        if (elCasos) elCasos.hidden = sec !== 'casos';
        if (elCarteras) elCarteras.hidden = sec !== 'carteras';
        if (elImport) elImport.hidden = sec !== 'import';
        if (sec === 'carteras') loadCarterasDataPanel();
        else if (sec === 'casos') loadCases();
    }
    window.openAdminDataTab = openAdminDataTab;

    function switchAdminView(view) {
        const resumen = $('admin-panel-resumen');
        const datos = $('admin-panel-datos');
        if (!resumen || !datos) return;

        document.querySelectorAll('.admin-view-tab').forEach((tab) => {
            tab.classList.toggle('active', tab.getAttribute('data-admin-view') === view);
        });

        if (view === 'resumen') {
            resumen.hidden = false;
            datos.hidden = true;
        } else {
            resumen.hidden = true;
            datos.hidden = false;
            const secCasos = $('data-section-casos');
            const showImport = $('data-section-import') && !$('data-section-import').hidden;
            const shouldLoadCases = secCasos && !secCasos.hidden && !showImport;
            if (!selectsLoaded) {
                loadReferenceSelects().then(() => {
                    selectsLoaded = true;
                    if (shouldLoadCases) loadCases();
                });
            } else if (shouldLoadCases) {
                loadCases();
            }
        }
    }
    window.switchAdminView = switchAdminView;

    async function loadReferenceSelects() {
        try {
            const [carterasRes, statusesRes, gestoresRes] = await Promise.all([
                apiFetch('/api/carteras'),
                apiFetch('/api/case-statuses'),
                apiFetch('/api/users/gestores'),
            ]);

            const carterasJson = await carterasRes.json();
            const statusesJson = await statusesRes.json();
            const carteras = Array.isArray(carterasJson) ? carterasJson : [];
            const statuses = Array.isArray(statusesJson) ? statusesJson : [];
            let gestoresData = { success: false, data: [] };
            if (gestoresRes.ok) {
                const gJson = await gestoresRes.json();
                gestoresData = gJson && typeof gJson === 'object' ? gJson : { success: false, data: [] };
            }

            const carteraSel = $('caseCarteraId');
            const statusSel = $('caseStatusId');
            const gestorSel = $('caseAssignedToId');

            const activeCarteras = carteras.filter((c) => c.activo);
            carteraSel.innerHTML =
                '<option value="">— Seleccionar —</option>' +
                activeCarteras.map((c) => `<option value="${c.id}">${escapeHtml(c.nombre)}</option>`).join('');

            statusSel.innerHTML = statuses
                .filter((s) => s.activo !== false)
                .map((s) => `<option value="${s.id}">${escapeHtml(s.nombre)}</option>`)
                .join('');

            gestorSel.innerHTML = '<option value="">— Sin asignar —</option>';
            if (gestoresData.success && Array.isArray(gestoresData.data)) {
                gestoresData.data.forEach((g) => {
                    const opt = document.createElement('option');
                    opt.value = g.id;
                    opt.textContent = g.username;
                    gestorSel.appendChild(opt);
                });
            }
        } catch (e) {
            console.error('loadReferenceSelects:', e);
            if (typeof showError === 'function') showError('Error al cargar listas del formulario');
        }
    }

    function escapeHtml(text) {
        if (text == null) return '';
        const d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }

    async function loadCases() {
        const tbody = $('casesTableBody');
        if (!tbody) return;

        tbody.innerHTML = '<tr><td colspan="9" class="data-table-empty">Cargando…</td></tr>';

        const params = new URLSearchParams();
        params.set('page', String(casesPage));
        params.set('per_page', String(casesPerPage));
        const q = ($('casesSearchInput') && $('casesSearchInput').value.trim()) || '';
        if (q) params.set('search', q);

        try {
            const res = await apiFetch('/api/cases?' + params.toString());
            const json = await res.json();

            if (!json.success) {
                tbody.innerHTML =
                    '<tr><td colspan="9" class="data-table-empty">Error: ' + escapeHtml(json.error || 'desconocido') + '</td></tr>';
                return;
            }

            const pag = json.pagination || {};
            renderCasesTable(json.data || [], pag);
            if (pag.page) casesPage = pag.page;
        } catch (e) {
            console.error('loadCases:', e);
            tbody.innerHTML = '<tr><td colspan="9" class="data-table-empty">Error de red al cargar casos</td></tr>';
        }
    }

    function renderCasesTable(rows, pagination) {
        const tbody = $('casesTableBody');
        const info = $('casesPageInfo');
        const prev = $('casesPagePrev');
        const next = $('casesPageNext');

        if (!rows.length) {
            tbody.innerHTML = '<tr><td colspan="9" class="data-table-empty">No hay casos</td></tr>';
        } else {
            tbody.innerHTML = '';
            rows.forEach((c) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${c.id}</td>
                    <td>${escapeHtml(c.name)} ${escapeHtml(c.lastname)}</td>
                    <td>${escapeHtml(c.dni || '—')}</td>
                    <td>${escapeHtml(c.nro_cliente || '—')}</td>
                    <td>$${Number(c.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</td>
                    <td>${escapeHtml(c.cartera_nombre || '—')}</td>
                    <td>${escapeHtml(c.status_nombre || '—')}</td>
                    <td>${escapeHtml(c.assigned_to || '—')}</td>
                    <td class="data-table-actions"></td>
                `;
                const actions = tr.querySelector('.data-table-actions');
                const btnEdit = document.createElement('button');
                btnEdit.type = 'button';
                btnEdit.className = 'btn-table';
                btnEdit.textContent = 'Editar';
                btnEdit.addEventListener('click', () => openCaseModal(c.id));
                const btnDel = document.createElement('button');
                btnDel.type = 'button';
                btnDel.className = 'btn-table btn-table-danger';
                btnDel.textContent = 'Eliminar';
                btnDel.addEventListener('click', () => deleteCase(c.id, c.name, c.lastname));
                actions.appendChild(btnEdit);
                actions.appendChild(btnDel);
                tbody.appendChild(tr);
            });
        }

        const page = pagination.page || 1;
        const pages = pagination.pages || 1;
        const total = pagination.total || 0;
        if (info) info.textContent = `Página ${page} de ${pages} (${total} casos)`;
        if (prev) prev.disabled = page <= 1;
        if (next) next.disabled = page >= pages;
    }

    async function openCaseModal(caseId) {
        const modal = $('caseFormModal');
        const title = $('caseFormTitle');
        const form = $('caseForm');
        const caseIdInput = $('caseFormCaseId');

        if (!modal || !form) return;

        if (!selectsLoaded) {
            await loadReferenceSelects();
            selectsLoaded = true;
        }

        form.reset();
        caseIdInput.value = '';

        if (caseId) {
            title.textContent = 'Editar caso';
            caseIdInput.value = String(caseId);
            apiFetch('/api/cases/' + caseId)
                .then((r) => r.json())
                .then((json) => {
                    if (!json.success || !json.data) {
                        if (typeof showError === 'function') showError(json.error || 'No se pudo cargar el caso');
                        return;
                    }
                    const d = json.data;
                    $('caseName').value = d.name || '';
                    $('caseLastname').value = d.lastname || '';
                    $('caseDni').value = d.dni || '';
                    $('caseNroCliente').value = d.nro_cliente || '';
                    $('caseTotal').value = d.total != null ? d.total : '';
                    $('caseMontoInicial').value = d.monto_inicial != null ? d.monto_inicial : '';
                    if (d.fecha_ultimo_pago) {
                        $('caseFechaUltimoPago').value = d.fecha_ultimo_pago.slice(0, 10);
                    }
                    $('caseTelefono').value = d.telefono || '';
                    $('caseCalleNombre').value = d.calle_nombre || '';
                    $('caseCalleNro').value = d.calle_nro || '';
                    $('caseLocalidad').value = d.localidad || '';
                    $('caseCp').value = d.cp || '';
                    $('caseProvincia').value = d.provincia || '';
                    $('caseCarteraId').value = String(d.cartera_id || '');
                    $('caseStatusId').value = String(d.status_id || '');
                    $('caseAssignedToId').value = d.assigned_to_id != null ? String(d.assigned_to_id) : '';
                    $('caseNotes').value = d.notes || '';
                    modal.classList.add('is-open');
                })
                .catch((e) => {
                    console.error(e);
                    if (typeof showError === 'function') showError('Error al cargar el caso');
                });
        } else {
            title.textContent = 'Nuevo caso';
            modal.classList.add('is-open');
        }
    }

    window.openCaseModal = openCaseModal;

    function closeCaseModal() {
        const modal = $('caseFormModal');
        if (modal) modal.classList.remove('is-open');
    }

    async function deleteCase(id, name, lastname) {
        if (!confirm('¿Eliminar el caso #' + id + ' (' + name + ' ' + lastname + ')?')) return;
        try {
            const res = await apiFetch('/api/cases/' + id, { method: 'DELETE' });
            const json = await res.json();
            if (json.success) {
                if (typeof showSuccess === 'function') showSuccess('Caso eliminado');
                loadCases();
            } else {
                if (typeof showError === 'function') showError(json.error || 'Error al eliminar');
            }
        } catch (e) {
            console.error(e);
            if (typeof showError === 'function') showError('Error al eliminar caso');
        }
    }

    async function submitCaseForm(ev) {
        ev.preventDefault();
        const caseId = $('caseFormCaseId').value;

        const totalNum = parseFloat($('caseTotal').value);
        const carteraIdNum = parseInt($('caseCarteraId').value, 10);
        if (Number.isNaN(totalNum) || totalNum < 0) {
            if (typeof showError === 'function') showError('Total inválido');
            return;
        }
        if (Number.isNaN(carteraIdNum)) {
            if (typeof showError === 'function') showError('Seleccioná una cartera');
            return;
        }

        const payload = {
            name: $('caseName').value.trim(),
            lastname: $('caseLastname').value.trim(),
            total: totalNum,
            cartera_id: carteraIdNum,
            status_id: parseInt($('caseStatusId').value, 10) || undefined,
            dni: $('caseDni').value.trim() || null,
            nro_cliente: $('caseNroCliente').value.trim() || null,
            telefono: $('caseTelefono').value.trim() || null,
            calle_nombre: $('caseCalleNombre').value.trim() || null,
            calle_nro: $('caseCalleNro').value.trim() || null,
            localidad: $('caseLocalidad').value.trim() || null,
            cp: $('caseCp').value.trim() || null,
            provincia: $('caseProvincia').value.trim() || null,
            notes: $('caseNotes').value.trim() || null,
        };

        const mi = $('caseMontoInicial').value;
        if (mi !== '') payload.monto_inicial = parseFloat(mi);

        const fup = $('caseFechaUltimoPago').value;
        if (fup) payload.fecha_ultimo_pago = fup;

        const gest = $('caseAssignedToId').value;
        if (gest === '') {
            payload.assigned_to_id = null;
        } else {
            payload.assigned_to_id = parseInt(gest, 10);
        }

        if (caseId) {
            const res = await apiFetch('/api/cases/' + caseId, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });
            const json = await res.json();
            if (json.success) {
                if (typeof showSuccess === 'function') showSuccess('Caso actualizado');
                closeCaseModal();
                loadCases();
            } else {
                if (typeof showError === 'function') showError(json.error || 'Error al guardar');
            }
        } else {
            const createPayload = Object.assign({}, payload);
            if (!createPayload.status_id) delete createPayload.status_id;
            const res = await apiFetch('/api/cases', {
                method: 'POST',
                body: JSON.stringify(createPayload),
            });
            const json = await res.json();
            if (json.success) {
                if (typeof showSuccess === 'function') showSuccess('Caso creado');
                closeCaseModal();
                casesPage = 1;
                loadCases();
            } else {
                if (typeof showError === 'function') showError(json.error || 'Error al crear');
            }
        }
    }

    // ——— Carteras (panel datos) ———
    async function loadCarterasDataPanel() {
        const list = $('carterasListData');
        if (!list) return;
        list.innerHTML = '<div class="data-table-empty">Cargando carteras…</div>';
        try {
            const res = await apiFetch('/api/carteras');
            if (!res.ok) throw new Error('fetch');
            const carteras = await res.json();
            renderCarterasListData(carteras);
        } catch (e) {
            console.error(e);
            list.innerHTML = '<div class="data-table-empty" style="color:#dc2626;">Error al cargar carteras</div>';
        }
    }

    function renderCarterasListData(carteras) {
        const list = $('carterasListData');
        if (!list) return;
        if (!carteras.length) {
            list.innerHTML = '<div class="data-table-empty">No hay carteras registradas</div>';
            return;
        }
        list.innerHTML = '';
        carteras.forEach((cartera) => {
            const row = document.createElement('div');
            row.className = 'cartera-row ' + (cartera.activo ? 'cartera-row-active' : 'cartera-row-inactive');
            const left = document.createElement('div');
            left.innerHTML =
                '<div class="cartera-row-name">' +
                escapeHtml(cartera.nombre) +
                '</div><div class="cartera-row-meta">' +
                (cartera.activo ? 'Activa' : 'Inactiva') +
                '</div>';
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn-primary btn-danger';
            btn.textContent = cartera.activo ? 'Desactivar' : 'Eliminar';
            btn.addEventListener('click', () => deleteCarteraData(cartera.id, cartera.nombre, cartera.activo));
            row.appendChild(left);
            row.appendChild(btn);
            list.appendChild(row);
        });
    }

    async function addCarteraData(ev) {
        ev.preventDefault();
        const input = $('newCarteraNombreData');
        const nombre = (input && input.value.trim()) || '';
        if (!nombre) {
            if (typeof showError === 'function') showError('El nombre es requerido');
            return;
        }
        try {
            const res = await apiFetch('/api/carteras', {
                method: 'POST',
                body: JSON.stringify({ nombre: nombre, activo: true }),
            });
            const result = await res.json();
            if (result.success) {
                input.value = '';
                if (typeof showSuccess === 'function') showSuccess('Cartera agregada');
                loadCarterasDataPanel();
                if (typeof loadCarteraFilter === 'function') loadCarteraFilter();
                if (selectsLoaded) loadReferenceSelects();
            } else {
                if (typeof showError === 'function') showError(result.error || 'Error');
            }
        } catch (e) {
            console.error(e);
            if (typeof showError === 'function') showError('Error al agregar cartera');
        }
    }

    async function downloadCsvTemplate() {
        try {
            const res = await apiFetch('/api/cases/import-template');
            if (!res.ok) {
                if (typeof showError === 'function') showError('No se pudo descargar la plantilla');
                return;
            }
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'casos_plantilla.csv';
            a.rel = 'noopener';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            console.error(e);
            if (typeof showError === 'function') showError('Error al descargar la plantilla');
        }
    }

    async function runCasesCsvImport() {
        const input = $('casesCsvFile');
        const out = $('casesCsvResult');
        if (!input || !input.files || !input.files[0]) {
            if (typeof showError === 'function') showError('Seleccioná un archivo CSV');
            return;
        }
        const fd = new FormData();
        fd.append('file', input.files[0]);
        try {
            const res = await fetch('/api/cases/import', {
                method: 'POST',
                body: fd,
                credentials: 'same-origin',
            });
            const json = await res.json();
            if (out) {
                out.hidden = false;
                const errs = json.errors && json.errors.length;
                out.classList.toggle('has-errors', !!errs || json.success === false);
                let text = '';
                if (json.success) {
                    text =
                        'Importados: ' +
                        json.imported +
                        '\nOmitidos (nro_cliente duplicado): ' +
                        json.skipped;
                    if (errs) {
                        text += '\n\nErrores por fila:\n';
                        text += json.errors.map(function (e) {
                            return 'Fila ' + e.row + ': ' + e.message;
                        }).join('\n');
                    }
                } else {
                    text = (json.error || 'Error') + '\n';
                    if (json.errors && json.errors.length) {
                        text += json.errors.map(function (e) {
                            return 'Fila ' + e.row + ': ' + e.message;
                        }).join('\n');
                    }
                }
                out.textContent = text;
            }
            if (json.success && typeof showSuccess === 'function') {
                showSuccess('Importación: ' + json.imported + ' caso(s) nuevos');
            }
            if (!json.success && typeof showError === 'function') {
                showError(json.error || 'Falló la importación');
            }
            if (json.success && json.imported > 0) {
                loadCases();
            }
        } catch (e) {
            console.error(e);
            if (out) {
                out.hidden = false;
                out.classList.add('has-errors');
                out.textContent = String(e);
            }
            if (typeof showError === 'function') showError('Error de red al importar');
        }
    }

    async function deleteCarteraData(carteraId, nombre, activo) {
        const accion = activo ? 'desactivar' : 'eliminar';
        if (!confirm('¿' + accion.charAt(0).toUpperCase() + accion.slice(1) + ' la cartera "' + nombre + '"?')) return;
        try {
            const res = await apiFetch('/api/carteras/' + carteraId, { method: 'DELETE' });
            const result = await res.json();
            if (result.success) {
                if (typeof showSuccess === 'function') showSuccess(result.message || 'Listo');
                loadCarterasDataPanel();
                if (typeof loadCarteraFilter === 'function') loadCarteraFilter();
                if (selectsLoaded) loadReferenceSelects();
            } else {
                if (typeof showError === 'function') showError(result.error || 'Error');
            }
        } catch (e) {
            console.error(e);
            if (typeof showError === 'function') showError('Error al procesar cartera');
        }
    }

    function init() {
        document.querySelectorAll('.admin-view-tab').forEach((tab) => {
            tab.addEventListener('click', () => {
                const view = tab.getAttribute('data-admin-view');
                if (view) switchAdminView(view);
            });
        });

        document.querySelectorAll('.data-subnav-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
                const sec = btn.getAttribute('data-data-section');
                document.querySelectorAll('.data-subnav-btn').forEach((b) => b.classList.remove('active'));
                btn.classList.add('active');
                const elCasos = $('data-section-casos');
                const elCarteras = $('data-section-carteras');
                const elImport = $('data-section-import');
                if (sec === 'carteras') {
                    if (elCasos) elCasos.hidden = true;
                    if (elCarteras) elCarteras.hidden = false;
                    if (elImport) elImport.hidden = true;
                    loadCarterasDataPanel();
                } else if (sec === 'import') {
                    if (elCasos) elCasos.hidden = true;
                    if (elCarteras) elCarteras.hidden = true;
                    if (elImport) elImport.hidden = false;
                } else {
                    if (elCasos) elCasos.hidden = false;
                    if (elCarteras) elCarteras.hidden = true;
                    if (elImport) elImport.hidden = true;
                    loadCases();
                }
            });
        });

        const searchInput = $('casesSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                clearTimeout(searchDebounce);
                searchDebounce = setTimeout(() => {
                    casesPage = 1;
                    loadCases();
                }, 350);
            });
        }

        const btnNew = $('btnNewCase');
        if (btnNew) btnNew.addEventListener('click', () => openCaseModal(null));

        const prevBtn = $('casesPagePrev');
        const nextBtn = $('casesPageNext');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (!prevBtn.disabled && casesPage > 1) {
                    casesPage--;
                    loadCases();
                }
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (!nextBtn.disabled) {
                    casesPage++;
                    loadCases();
                }
            });
        }

        const caseForm = $('caseForm');
        if (caseForm) caseForm.addEventListener('submit', submitCaseForm);

        $('caseFormModalClose') &&
            $('caseFormModalClose').addEventListener('click', () => closeCaseModal());
        $('caseFormCancel') && $('caseFormCancel').addEventListener('click', () => closeCaseModal());

        const caseModal = $('caseFormModal');
        if (caseModal) {
            caseModal.addEventListener('click', (ev) => {
                if (ev.target === caseModal) closeCaseModal();
            });
        }

        const formCartera = $('addCarteraFormData');
        if (formCartera) formCartera.addEventListener('submit', addCarteraData);

        const btnTpl = $('btnDownloadCsvTemplate');
        if (btnTpl) btnTpl.addEventListener('click', downloadCsvTemplate);
        const btnImp = $('btnCasesCsvImport');
        if (btnImp) btnImp.addEventListener('click', runCasesCsvImport);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
