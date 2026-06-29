<template>
  <section class="checkin-page">
    <header class="page-header">
      <div>
        <h1>Topico</h1>
        <p>Citas reservadas por especialidad y registro de llegada por codigo de estudiante.</p>
      </div>
      <label class="date-filter">
        Fecha
        <input v-model="fecha" type="date" class="form-control" @change="cargarResumen" />
      </label>
    </header>

    <section class="search-panel">
      <label for="codigoBusqueda">Codigo de estudiante</label>
      <div class="search-row">
        <input
          id="codigoBusqueda"
          v-model.trim="codigoBusqueda"
          class="form-control"
          type="text"
          placeholder="Ej. 20234044I"
          @keyup.enter="buscarPorCodigo"
        />
        <button class="btn btn-primary" type="button" :disabled="buscando || !codigoBusqueda" @click="buscarPorCodigo">
          {{ buscando ? 'Buscando...' : 'Buscar' }}
        </button>
      </div>
    </section>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <section class="specialty-summary" aria-label="Citas por especialidad">
      <TopicoEspecialidadSummaryCard
        v-for="esp in resumen"
        :key="esp.especialidadId"
        :especialidad-id="esp.especialidadId"
        :nombre="esp.especialidadNombre"
        :total-citas="esp.totalCitas"
      />
    </section>

    <BaseModal v-model:open="modalOpen" aria-label="Confirmar llegada">
      <template #header="{ close }">
        <div class="modal-heading">
          <div>
            <h2>{{ citasPendientes.length > 1 ? 'Seleccionar cita' : 'Confirmar hora de llegada' }}</h2>
            <p>
              {{
                citasPendientes.length > 1
                  ? 'El estudiante tiene mas de una cita pendiente en esta fecha.'
                  : 'La hora se registrara automaticamente con la hora actual.'
              }}
            </p>
          </div>
          <button class="btn-close" type="button" aria-label="Cerrar" @click="close">x</button>
        </div>
      </template>

      <div v-if="citasPendientes.length > 1" class="appointment-picker">
        <p class="picker-title">Elija la cita a la que llego el estudiante:</p>
        <button
          v-for="cita in citasPendientes"
          :key="cita.citaId"
          type="button"
          class="appointment-option"
          :class="{ 'appointment-option--selected': citaSeleccionada?.citaId === cita.citaId }"
          @click="seleccionarCita(cita)"
        >
          <span class="appointment-specialty">{{ cita.especialidadNombre }}</span>
          <span class="appointment-time">
            {{ formatHora(cita.horaInicio) }} - {{ formatHora(cita.horaFin) }}
          </span>
          <span class="appointment-meta">
            {{ cita.nombreMedico }}
          </span>
        </button>
      </div>

      <div v-if="citaSeleccionada" class="modal-content-body">
        <dl>
          <div>
            <dt>Estudiante</dt>
            <dd>{{ citaSeleccionada.nombreEstudiante }}</dd>
          </div>
          <div>
            <dt>Codigo</dt>
            <dd>{{ citaSeleccionada.codigoEstudiante }}</dd>
          </div>
          <div>
            <dt>Especialidad</dt>
            <dd>{{ citaSeleccionada.especialidadNombre }}</dd>
          </div>
          <div>
            <dt>Medico</dt>
            <dd>{{ citaSeleccionada.nombreMedico }}</dd>
          </div>
          <div>
            <dt>Horario</dt>
            <dd>{{ formatFecha(citaSeleccionada.fecha) }} - {{ formatHora(citaSeleccionada.horaInicio) }} a {{ formatHora(citaSeleccionada.horaFin) }}</dd>
          </div>
        </dl>
      </div>

      <template #footer="{ close }">
        <button class="btn btn-outline-secondary" type="button" @click="close">Cancelar</button>
        <button class="btn btn-primary" type="button" :disabled="registrando || !citaSeleccionada" @click="confirmarLlegada">
          {{ registrando ? 'Registrando...' : 'Confirmar llegada' }}
        </button>
      </template>
    </BaseModal>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import TopicoEspecialidadSummaryCard from '@/components/TopicoEspecialidadSummaryCard.vue'
import { useAuth } from '@/stores/auth'
import {
  buscarCitaTopicoPorCodigo,
  fetchResumenCitasTopico,
  registrarLlegadaTopico,
} from '@/services/api'

const auth = useAuth()
const fecha = ref(new Date().toISOString().slice(0, 10))
const resumen = ref([])
const codigoBusqueda = ref('')
const citaSeleccionada = ref(null)
const citasPendientes = ref([])
const modalOpen = ref(false)
const buscando = ref(false)
const registrando = ref(false)
const error = ref('')
const success = ref('')

onMounted(() => {
  cargarResumen()
})

async function cargarResumen() {
  error.value = ''
  success.value = ''

  try {
    resumen.value = await fetchResumenCitasTopico(fecha.value)
  } catch (e) {
    error.value = e.message || 'No se pudo cargar el resumen de citas'
  }
}

async function buscarPorCodigo() {
  if (!codigoBusqueda.value) return

  buscando.value = true
  error.value = ''
  success.value = ''
  citaSeleccionada.value = null
  citasPendientes.value = []

  try {
    const resultados = await buscarCitaTopicoPorCodigo(codigoBusqueda.value, fecha.value)
    const pendientes = resultados.filter((cita) => !cita.registradaLlegada)

    if (!resultados.length) {
      error.value = 'No se encontro una cita reservada para ese codigo en la fecha seleccionada.'
      return
    }

    if (!pendientes.length) {
      error.value = 'Todas las citas de este estudiante en la fecha seleccionada ya tienen hora de llegada registrada.'
      return
    }

    citasPendientes.value = pendientes
    citaSeleccionada.value = pendientes.length === 1 ? pendientes[0] : null
    modalOpen.value = true
  } catch (e) {
    error.value = e.message || 'No se pudo buscar la cita'
  } finally {
    buscando.value = false
  }
}

function seleccionarCita(cita) {
  citaSeleccionada.value = cita
}

async function confirmarLlegada() {
  if (!citaSeleccionada.value) return

  registrando.value = true
  error.value = ''
  success.value = ''

  try {
    await registrarLlegadaTopico(citaSeleccionada.value.citaId, auth.user?.id)
    success.value = `Llegada registrada para ${citaSeleccionada.value.nombreEstudiante}`
    modalOpen.value = false
    codigoBusqueda.value = ''
    citaSeleccionada.value = null
    citasPendientes.value = []
    await cargarResumen()
  } catch (e) {
    error.value = e.message || 'No se pudo registrar la llegada'
  } finally {
    registrando.value = false
  }
}

function formatHora(value) {
  if (!value) return '--:--'
  return String(value).slice(0, 5)
}

function formatFecha(value) {
  if (!value) return ''
  return new Date(`${value}T00:00:00`).toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}
</script>

<style scoped>
.checkin-page {
  display: grid;
  gap: 18px;
}

.page-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  color: #111827;
}

.page-header p {
  margin: 4px 0 0;
  color: #667085;
}

.date-filter {
  display: grid;
  gap: 6px;
  min-width: 210px;
  color: #344054;
  font-weight: 600;
}

.search-panel {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
}

.search-panel label {
  color: #344054;
  font-weight: 700;
}

.search-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.specialty-summary {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}

.modal-heading {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 8px;
}

.modal-heading h2 {
  margin: 0;
  font-size: 1.25rem;
}

.modal-heading p {
  margin: 4px 0 0;
  color: #667085;
  font-size: 0.9rem;
}

.modal-content-body dl {
  display: grid;
  gap: 10px;
  margin: 0;
}

.appointment-picker {
  display: grid;
  gap: 10px;
  margin-bottom: 16px;
}

.picker-title {
  margin: 0;
  color: #344054;
  font-weight: 700;
}

.appointment-option {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4px 12px;
  width: 100%;
  padding: 12px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  color: #111827;
  text-align: left;
  cursor: pointer;
}

.appointment-option:hover {
  border-color: #b42318;
  background: #fff7f7;
}

.appointment-option--selected {
  border-color: #990000;
  background: #fff1f1;
  box-shadow: 0 0 0 2px rgba(153, 0, 0, 0.12);
}

.appointment-specialty {
  font-weight: 800;
}

.appointment-time {
  color: #990000;
  font-weight: 800;
}

.appointment-meta {
  grid-column: 1 / -1;
  color: #667085;
  font-size: 0.92rem;
}

.modal-content-body dl > div {
  display: grid;
  grid-template-columns: 130px 1fr;
  gap: 10px;
}

.modal-content-body dt {
  color: #667085;
  font-weight: 700;
}

.modal-content-body dd {
  margin: 0;
  color: #111827;
}

@media (max-width: 720px) {
  .page-header,
  .search-row {
    grid-template-columns: 1fr;
    display: grid;
  }

  .date-filter {
    min-width: 0;
  }

  .modal-content-body dl > div {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
</style>
