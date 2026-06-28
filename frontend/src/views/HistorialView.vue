<template>
  <div class="historial-container">
    <div class="header">
      <h1>Historial de Citas</h1>
      <p class="subtitle">Consulta tus citas pasadas organizadas por especialidad</p>
    </div>

    <!-- Modal de Calificación -->
    <CalificarModal
      v-if="estudianteDatos"
      :mostrar="mostrarModalCalificar"
      :cita="citaParaCalificar"
      :estudianteId="estudianteDatos.id"
      @cerrar="mostrarModalCalificar = false"
      @calificacion-enviada="onCalificacionEnviada"
    />

    <div v-if="loading" class="loading">
      <p>Cargando historial...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="historial.length === 0" class="empty">
      <p>No tienes citas en tu historial</p>
    </div>

    <div v-else class="historial-list">
      <div 
        v-for="especialidad in historial" 
        :key="especialidad.especialidadId"
        class="especialidad-section"
      >
        <h2 class="especialidad-title">{{ especialidad.especialidadNombre }}</h2>
        <div class="citas-list">
          <div 
            v-for="cita in especialidad.citas" 
            :key="cita.citaId"
            class="cita-card"
          >
            <div class="cita-info">
              <div class="cita-header">
                <span class="medico-nombre">{{ cita.medicoNombre }}</span>
                <div class="d-flex align-items-center gap-2">
                  <span :class="['estado-badge', `estado-${cita.estado}`]">
                    {{ getEstadoLabel(cita.estado) }}
                  </span>
                  <span v-if="cita.estado === 'atendida' && cita.horaAtencion && !cita.tieneCalificacion" class="badge bg-warning text-dark">
                    <i class="bi bi-star me-1"></i>Pendiente calificar
                  </span>
                  <span v-if="cita.tieneCalificacion" class="badge bg-info">
                    <i class="bi bi-star-fill me-1"></i>Calificada ({{ cita.calificacion }}/5)
                  </span>
                </div>
              </div>
              <div class="cita-details">
                <p><strong>Fecha:</strong> {{ formatFecha(cita.fecha) }}</p>
                <p><strong>Hora:</strong> {{ cita.hora }}</p>
                <p v-if="cita.horaAtencion"><strong>Atendida a las:</strong> {{ formatHoraAtencion(cita.horaAtencion) }}</p>
              </div>
              <div v-if="cita.estado === 'atendida' && !cita.tieneCalificacion" class="cita-actions mt-2">
                <button 
                  class="btn btn-sm btn-primary"
                  @click="abrirModalCalificar(cita)"
                >
                  <i class="bi bi-star me-1"></i>
                  Calificar Atención
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../stores/auth'
import * as api from '../services/api'
import CalificarModal from '../components/CalificarModal.vue'

const auth = useAuth()
const historial = ref([])
const loading = ref(true)
const error = ref(null)
const estudianteDatos = ref(null)
const mostrarModalCalificar = ref(false)
const citaParaCalificar = ref(null)

async function cargarHistorial() {
  loading.value = true
  error.value = null
  
  try {
    // Obtener datos del usuario (similar a CalendarView)
    const username = localStorage.getItem('user')
    if (!username) {
      error.value = 'No se pudo obtener la información del usuario'
      return
    }
    
    estudianteDatos.value = await api.fetchUsuario(username)
    
    if (!estudianteDatos.value || !estudianteDatos.value.id) {
      error.value = 'No se pudo obtener el ID del estudiante'
      return
    }
    
    const data = await api.fetchHistorialCitasPorEspecialidad(estudianteDatos.value.id)
    historial.value = data
  } catch (e) {
    error.value = e.message || 'Error al cargar el historial'
    console.error('Error:', e)
  } finally {
    loading.value = false
  }
}

function formatFecha(fecha) {
  if (!fecha) return 'N/A'
  const date = new Date(fecha)
  return date.toLocaleDateString('es-PE', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function formatHoraAtencion(horaAtencionStr) {
  if (!horaAtencionStr) return 'N/A'
  const date = new Date(horaAtencionStr)
  return date.toLocaleTimeString('es-PE', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getEstadoLabel(estado) {
  const estados = {
    'cancelada': 'Cancelada',
    'atendida': 'Atendida'
  }
  return estados[estado] || estado
}

function abrirModalCalificar(cita) {
  citaParaCalificar.value = cita
  mostrarModalCalificar.value = true
}

function onCalificacionEnviada(calificacionData) {
  // Actualizar la cita en el historial para reflejar que ya tiene calificación
  for (const especialidad of historial.value) {
    const cita = especialidad.citas.find(c => c.citaId === calificacionData.citaId)
    if (cita) {
      cita.tieneCalificacion = true
      cita.calificacion = calificacionData.calificacion
      break
    }
  }
  
  // Recargar el historial para asegurar datos actualizados
  cargarHistorial()
}

onMounted(() => {
  cargarHistorial()
})
</script>

<style scoped>
.historial-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  color: #1f2328;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #5f6b7a;
  font-size: 1rem;
}

.loading, .error, .empty {
  text-align: center;
  padding: 3rem;
  color: #5f6b7a;
}

.error {
  color: #dc2626;
}

.historial-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.especialidad-section {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.especialidad-title {
  color: #7a0000;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  border-bottom: 2px solid #e4e7ec;
  padding-bottom: 0.5rem;
}

.citas-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cita-card {
  background: #f6f7f9;
  border-radius: 8px;
  padding: 1rem;
  border-left: 4px solid #7a0000;
}

.cita-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.medico-nombre {
  font-weight: 600;
  color: #1f2328;
  font-size: 1.1rem;
}

.estado-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.estado-cancelada {
  background: #fee2e2;
  color: #991b1b;
}

.estado-atendida {
  background: #d1fae5;
  color: #065f46;
}

.cita-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cita-details p {
  margin: 0;
  color: #5f6b7a;
  font-size: 0.95rem;
}

.cita-details strong {
  color: #1f2328;
}
</style>

