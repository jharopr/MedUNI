<template>
  <div v-if="mostrar" class="modal-overlay" @click.self="cerrar">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Calificar Atención</h5>
        <button type="button" class="btn-close" @click="cerrar" aria-label="Cerrar"></button>
      </div>
      
      <div class="modal-body">
        <div class="mb-3">
          <label class="form-label">¿Cómo calificarías tu experiencia?</label>
          <div class="calificacion-estrellas">
            <button
              v-for="i in 5"
              :key="i"
              type="button"
              class="btn-estrella"
              :class="{ 'activa': calificacion >= i, 'hover': hoverRating >= i }"
              @click="calificacion = i"
              @mouseenter="hoverRating = i"
              @mouseleave="hoverRating = 0"
            >
              <i class="bi" :class="calificacion >= i ? 'bi-star-fill' : 'bi-star'"></i>
            </button>
          </div>
          <small class="text-muted">Selecciona de 1 a 5 estrellas</small>
        </div>

        <div class="mb-3">
          <label for="comentario" class="form-label">Comentario (opcional)</label>
          <textarea
            id="comentario"
            class="form-control"
            v-model="comentario"
            rows="3"
            placeholder="Comparte tu experiencia..."
            maxlength="500"
          ></textarea>
          <small class="text-muted">{{ comentario.length }}/500 caracteres</small>
        </div>

        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="cerrar">
          Cancelar
        </button>
        <button 
          type="button" 
          class="btn btn-primary" 
          @click="enviarCalificacion"
          :disabled="calificacion === 0 || enviando"
        >
          <span v-if="enviando" class="spinner-border spinner-border-sm me-2"></span>
          {{ enviando ? 'Enviando...' : 'Enviar Calificación' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import * as api from '../services/api'
import { useAuth } from '../stores/auth'

const props = defineProps({
  mostrar: {
    type: Boolean,
    default: false
  },
  cita: {
    type: Object,
    default: null
  },
  estudianteId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['cerrar', 'calificacion-enviada'])

const calificacion = ref(0)
const comentario = ref('')
const hoverRating = ref(0)
const error = ref(null)
const enviando = ref(false)

watch(() => props.mostrar, (nuevoValor) => {
  if (nuevoValor) {
    // Resetear valores al abrir
    calificacion.value = 0
    comentario.value = ''
    error.value = null
    hoverRating.value = 0
  }
})

function cerrar() {
  emit('cerrar')
}

async function enviarCalificacion() {
  if (calificacion.value === 0) {
    error.value = 'Por favor selecciona una calificación'
    return
  }

  if (!props.cita || !props.cita.citaId) {
    error.value = 'Error: No se pudo identificar la cita'
    return
  }

  enviando.value = true
  error.value = null

  try {
    await api.crearCalificacion(
      props.cita.citaId,
      calificacion.value,
      comentario.value.trim() || null,
      props.estudianteId
    )
    
    emit('calificacion-enviada', {
      citaId: props.cita.citaId,
      calificacion: calificacion.value,
      comentario: comentario.value
    })
    
    cerrar()
  } catch (e) {
    error.value = e.message || 'Error al enviar la calificación. Inténtalo de nuevo.'
    console.error('Error al calificar:', e)
  } finally {
    enviando.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  margin: 0;
  font-weight: 600;
  color: #1f2328;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  opacity: 0.5;
  padding: 0;
  width: 30px;
  height: 30px;
}

.btn-close:hover {
  opacity: 1;
}

.modal-body {
  padding: 1.25rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1.25rem;
  border-top: 1px solid #dee2e6;
}

.calificacion-estrellas {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0;
}

.btn-estrella {
  background: none;
  border: none;
  padding: 0;
  font-size: 2rem;
  color: #ddd;
  cursor: pointer;
  transition: transform 0.1s, color 0.2s;
}

.btn-estrella:hover {
  transform: scale(1.1);
}

.btn-estrella.activa {
  color: #ffc107;
}

.btn-estrella.hover:not(.activa) {
  color: #ffc107;
  opacity: 0.6;
}

.form-control {
  border: 1px solid #ced4da;
  border-radius: 6px;
  padding: 0.5rem;
}

.form-control:focus {
  border-color: #7a0000;
  outline: none;
  box-shadow: 0 0 0 0.2rem rgba(122, 0, 0, 0.25);
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>

