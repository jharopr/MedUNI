<template>
  <section class="audit-page">
    <header class="audit-header">
      <div>
        <p class="eyebrow">Administracion</p>
        <h1>Historial de acciones</h1>
        <p class="subtitle">Seguimiento de acciones realizadas por medicos, personal de topico y estudiantes.</p>
      </div>
      <button class="refresh-btn" type="button" @click="cargarAuditoria" :disabled="loading">
        {{ loading ? 'Cargando...' : 'Actualizar' }}
      </button>
    </header>

    <form class="filters" @submit.prevent="cargarAuditoria">
      <label>
        Rol
        <select v-model="filtros.rol">
          <option value="todos">Todos</option>
          <option value="medico">Medico</option>
          <option value="topico">Topico</option>
          <option value="estudiante">Estudiante</option>
          <option value="administrador">Administrador</option>
        </select>
      </label>

      <label>
        Accion
        <input v-model.trim="filtros.accion" type="search" placeholder="Ej. registrar_llegada" />
      </label>

      <label>
        Desde
        <input v-model="filtros.fechaDesde" type="date" />
      </label>

      <label>
        Hasta
        <input v-model="filtros.fechaHasta" type="date" />
      </label>

      <button type="submit" class="primary-btn">Buscar</button>
    </form>

    <div class="summary-grid">
      <article
        v-for="card in resumenCards"
        :key="card.key"
        class="summary-card"
        :class="card.key"
      >
        <span class="role-icon">{{ card.icon }}</span>
        <div>
          <p>{{ card.label }}</p>
          <strong>{{ card.total }}</strong>
        </div>
      </article>
    </div>

    <div v-if="error" class="state state-error">{{ error }}</div>
    <div v-else-if="loading" class="state">Cargando historial...</div>

    <div v-else class="audit-table-wrap">
      <table class="audit-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Rol</th>
            <th>Usuario</th>
            <th>Accion</th>
            <th>Entidad</th>
            <th>Detalle</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="auditorias.length === 0">
            <td colspan="6" class="empty">No hay acciones registradas con los filtros seleccionados.</td>
          </tr>
          <tr v-for="item in auditorias" :key="item.id">
            <td>
              <div class="date-cell">
                <strong>{{ formatDate(item.fecha) }}</strong>
                <span>{{ formatTime(item.fecha) }}</span>
              </div>
            </td>
            <td>
              <span class="role-badge" :class="item.rol">{{ rolLabel(item.rol) }}</span>
            </td>
            <td>
              <div class="user-cell">
                <strong>{{ item.usuarioNombre || 'Usuario no identificado' }}</strong>
                <span v-if="item.codigoEstudiante">Codigo: {{ item.codigoEstudiante }}</span>
                <span v-else-if="item.usuarioCorreo">{{ item.usuarioCorreo }}</span>
              </div>
            </td>
            <td>{{ accionLabel(item.accion) }}</td>
            <td>
              <div class="entity-cell">
                <strong>{{ item.entidad || '-' }}</strong>
                <span v-if="item.entidadId">ID {{ item.entidadId }}</span>
              </div>
            </td>
            <td class="detail-cell">{{ item.detalle || 'Sin detalle adicional' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import * as api from '../services/api'

const filtros = reactive({
  rol: 'todos',
  accion: '',
  fechaDesde: '',
  fechaHasta: '',
  limit: 150,
})

const auditorias = ref([])
const resumen = ref({})
const loading = ref(false)
const error = ref('')

const resumenCards = computed(() => [
  { key: 'medico', label: 'Medicos', icon: 'M', total: resumen.value.medico || 0 },
  { key: 'topico', label: 'Topico', icon: 'T', total: resumen.value.topico || 0 },
  { key: 'estudiante', label: 'Estudiantes', icon: 'E', total: resumen.value.estudiante || 0 },
  { key: 'administrador', label: 'Administradores', icon: 'A', total: resumen.value.administrador || 0 },
])

async function cargarAuditoria() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.fetchHistorialAuditoria({ ...filtros })
    auditorias.value = Array.isArray(data?.items) ? data.items : []
    resumen.value = data?.resumen && typeof data.resumen === 'object' ? data.resumen : {}
  } catch (e) {
    error.value = e.message || 'No se pudo cargar el historial de auditoria.'
  } finally {
    loading.value = false
  }
}

function rolLabel(rol) {
  const labels = {
    medico: 'Medico',
    topico: 'Topico',
    estudiante: 'Estudiante',
    administrador: 'Admin',
  }
  return labels[rol] || 'Otro'
}

function accionLabel(accion) {
  return String(accion || '').split('_').join(' ')
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return new Intl.DateTimeFormat('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(date)
}

function formatTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat('es-PE', { hour: '2-digit', minute: '2-digit' }).format(date)
}

onMounted(cargarAuditoria)
</script>

<style scoped>
.audit-page {
  display: grid;
  gap: 1.25rem;
  max-width: 1280px;
  margin: 0 auto;
}

.audit-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 .25rem;
  color: #7a0000;
  font-size: .78rem;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: #172033;
  font-size: clamp(1.7rem, 2.5vw, 2.4rem);
}

.subtitle {
  color: #5f6b7a;
  margin: .35rem 0 0;
}

.refresh-btn,
.primary-btn {
  border: 0;
  border-radius: 8px;
  background: #7a0000;
  color: #fff;
  font-weight: 700;
  min-height: 42px;
  padding: 0 .95rem;
}

.refresh-btn:disabled,
.primary-btn:disabled {
  opacity: .65;
}

.filters {
  display: grid;
  grid-template-columns: 180px minmax(220px, 1fr) 170px 170px auto;
  gap: .9rem;
  align-items: end;
  padding: 1rem;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
}

label {
  display: grid;
  gap: .35rem;
  color: #172033;
  font-weight: 700;
}

select,
input {
  width: 100%;
  min-height: 42px;
  border: 1px solid #d7dce4;
  border-radius: 8px;
  padding: 0 .75rem;
  color: #172033;
  background: #fff;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: .9rem;
  padding: 1rem;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
}

.role-icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  color: #fff;
  background: #7a0000;
  font-weight: 900;
}

.summary-card p {
  margin: 0;
  color: #5f6b7a;
}

.summary-card strong {
  display: block;
  color: #172033;
  font-size: 1.65rem;
  line-height: 1;
}

.summary-card.medico .role-icon { background: #0f766e; }
.summary-card.topico .role-icon { background: #075985; }
.summary-card.estudiante .role-icon { background: #7a0000; }
.summary-card.administrador .role-icon { background: #4338ca; }

.state {
  padding: 1.25rem;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  color: #5f6b7a;
  text-align: center;
}

.state-error {
  border-color: #fecaca;
  background: #fef2f2;
  color: #991b1b;
}

.audit-table-wrap {
  overflow: auto;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 960px;
}

th,
td {
  padding: .9rem 1rem;
  border-bottom: 1px solid #edf0f4;
  vertical-align: top;
  text-align: left;
}

th {
  color: #344054;
  background: #f8fafc;
  font-size: .82rem;
  text-transform: uppercase;
}

.date-cell,
.user-cell,
.entity-cell {
  display: grid;
  gap: .15rem;
}

.date-cell span,
.user-cell span,
.entity-cell span {
  color: #667085;
  font-size: .86rem;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  border-radius: 999px;
  padding: 0 .7rem;
  background: #f2f4f7;
  color: #344054;
  font-weight: 800;
  font-size: .82rem;
}

.role-badge.medico { background: #ccfbf1; color: #115e59; }
.role-badge.topico { background: #e0f2fe; color: #075985; }
.role-badge.estudiante { background: #fee2e2; color: #7a0000; }
.role-badge.administrador { background: #e0e7ff; color: #3730a3; }

.detail-cell {
  max-width: 320px;
  color: #475467;
}

.empty {
  color: #667085;
  text-align: center;
  padding: 2rem;
}

@media (max-width: 900px) {
  .audit-header {
    display: grid;
  }

  .filters {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
