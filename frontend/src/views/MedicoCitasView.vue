<template>
  <section class="doctor-page">
    <header class="doctor-header">
      <div>
        <p class="eyebrow">{{ auth.user?.especialidadNombre || 'Medico' }}</p>
        <h1>Mis pacientes</h1>
        <p>{{ doctorName }}</p>
      </div>

      <label class="date-filter">
        Seleccione fecha
        <input v-model="fecha" class="form-control" type="date" :min="hoy" @change="cargarCitas" />
      </label>
    </header>

    <section class="summary-strip">
      <div class="summary-indicator">
        <span>Pacientes programados</span>
        <strong>{{ citas.length }}</strong>
      </div>
      <div class="summary-indicator summary-indicator--arrived">
        <span>Con llegada registrada</span>
        <strong>{{ citasConLlegada }}</strong>
      </div>
    </section>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <section class="patients-panel">
      <details open>
        <summary>
          <span>Pacientes de la fecha</span>
          <strong>{{ citas.length }}</strong>
        </summary>

        <div v-if="loading" class="state">Cargando pacientes...</div>
        <div v-else-if="citas.length === 0" class="state">No tiene pacientes programados para esta fecha.</div>

        <div v-else class="patient-list">
          <article v-for="cita in citas" :key="cita.citaId" class="patient-item">
            <div class="patient-main">
              <h2>{{ cita.nombreEstudiante }}</h2>
              <p>{{ formatHora(cita.horaInicio) }} - {{ formatHora(cita.horaFin) }}</p>
            </div>

            <div class="arrival-state">
              <span v-if="cita.horaLlegada" class="badge text-bg-success">
                Llego {{ formatDateTime(cita.horaLlegada) }}
              </span>
              <span v-else class="badge text-bg-secondary">Sin llegada</span>
            </div>

            <div class="attention-state">
              <span v-if="cita.horaInicioAtencion && !cita.horaFinAtencion" class="badge text-bg-warning">
                En atencion
              </span>
              <span v-else-if="cita.horaInicioAtencion" class="badge text-bg-info">
                Iniciada {{ formatDateTime(cita.horaInicioAtencion) }}
              </span>
              <span v-else class="badge text-bg-light">Pendiente</span>
            </div>

            <div class="patient-actions">
              <button
                class="btn btn-sm btn-primary"
                type="button"
                :disabled="!cita.horaLlegada || cita.horaInicioAtencion || actionId === cita.citaId"
                @click="iniciar(cita)"
              >
                Iniciar cita
              </button>
              <button
                class="btn btn-sm btn-outline-primary"
                type="button"
                :disabled="!cita.horaInicioAtencion || cita.horaFinAtencion || actionId === cita.citaId"
                @click="finalizar(cita)"
              >
                Finalizar
              </button>
            </div>
          </article>
        </div>
      </details>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuth } from '@/stores/auth'
import { fetchCitasMedico, finalizarCitaMedico, iniciarCitaMedico } from '@/services/api'

const auth = useAuth()
const hoy = new Date().toISOString().slice(0, 10)
const fecha = ref(hoy)
const citas = ref([])
const loading = ref(false)
const actionId = ref(null)
const error = ref('')
const success = ref('')

const doctorName = computed(() => {
  if (!auth.user) return ''
  return `${auth.user.nombres || ''} ${auth.user.apellidos || ''}`.trim()
})

const citasConLlegada = computed(() => citas.value.filter((cita) => !!cita.horaLlegada).length)

onMounted(() => {
  cargarCitas()
})

async function cargarCitas() {
  if (fecha.value < hoy) {
    fecha.value = hoy
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    citas.value = await fetchCitasMedico(auth.user?.id, fecha.value)
  } catch (e) {
    error.value = e.message || 'No se pudieron cargar las citas del medico'
  } finally {
    loading.value = false
  }
}

async function iniciar(cita) {
  actionId.value = cita.citaId
  error.value = ''
  success.value = ''

  try {
    await iniciarCitaMedico(auth.user?.id, cita.citaId)
    success.value = `Cita iniciada para ${cita.nombreEstudiante}`
    await cargarCitas()
  } catch (e) {
    error.value = e.message || 'No se pudo iniciar la cita'
  } finally {
    actionId.value = null
  }
}

async function finalizar(cita) {
  actionId.value = cita.citaId
  error.value = ''
  success.value = ''

  try {
    await finalizarCitaMedico(auth.user?.id, cita.citaId)
    success.value = `Cita finalizada para ${cita.nombreEstudiante}`
    await cargarCitas()
  } catch (e) {
    error.value = e.message || 'No se pudo finalizar la cita'
  } finally {
    actionId.value = null
  }
}

function formatHora(value) {
  if (!value) return '--:--'
  return String(value).slice(0, 5)
}

function formatDateTime(value) {
  if (!value) return ''
  return new Date(value).toLocaleTimeString('es-PE', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}
</script>

<style scoped>
.doctor-page {
  display: grid;
  gap: 18px;
}

.doctor-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #7a0000;
  font-weight: 800;
  text-transform: uppercase;
  font-size: 0.78rem;
}

.doctor-header h1 {
  margin: 0;
  color: #111827;
}

.doctor-header p {
  margin: 4px 0 0;
  color: #667085;
}

.date-filter {
  min-width: 220px;
  display: grid;
  gap: 6px;
  color: #344054;
  font-weight: 700;
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.summary-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 18px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
}

.summary-indicator span {
  color: #667085;
  font-weight: 700;
}

.summary-indicator strong {
  color: #7a0000;
  font-size: 2rem;
  line-height: 1;
}

.summary-indicator--arrived strong {
  color: #047857;
}

.patients-panel {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.patients-panel summary {
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  padding: 16px;
  background: #f8fafc;
  font-weight: 800;
}

.patients-panel summary strong {
  color: #7a0000;
}

.state {
  padding: 28px;
  text-align: center;
  color: #667085;
}

.patient-list {
  display: grid;
}

.patient-item {
  display: grid;
  grid-template-columns: minmax(220px, 1.4fr) minmax(160px, auto) minmax(120px, auto) auto;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-top: 1px solid #eef2f6;
}

.patient-main h2 {
  margin: 0;
  font-size: 1rem;
  color: #111827;
}

.patient-main p {
  margin: 4px 0 0;
  color: #7a0000;
  font-weight: 800;
}

.patient-actions {
  display: flex;
  justify-content: end;
  gap: 8px;
  white-space: nowrap;
}

@media (max-width: 920px) {
  .patient-item {
    grid-template-columns: 1fr;
    align-items: start;
  }

  .patient-actions {
    justify-content: start;
  }
}

@media (max-width: 680px) {
  .doctor-header,
  .summary-strip {
    grid-template-columns: 1fr;
    display: grid;
  }

  .date-filter {
    min-width: 0;
  }
}
</style>
