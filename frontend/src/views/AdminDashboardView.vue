<template>
  <div class="dashboard-container">
    <div class="header">
      <h1>Dashboard Administrativo</h1>
      <p class="subtitle">Indicadores de Rendimiento (KPIs)</p>
    </div>

    <div v-if="loading" class="loading">
      <p>Cargando indicadores...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-else class="kpis-grid">
      <div 
        v-for="kpi in kpis" 
        :key="kpi.key"
        :class="['kpi-card', { 'cumple-meta': kpi.cumple_meta, 'no-cumple': kpi.cumple_meta === false }]"
      >
        <div class="kpi-header">
          <h3>{{ kpi.nombre }}</h3>
          <span v-if="kpi.cumple_meta !== null" :class="['meta-badge', kpi.cumple_meta ? 'meta-ok' : 'meta-fail']">
            {{ kpi.cumple_meta ? '✓ Cumple' : '✗ No cumple' }}
          </span>
        </div>
        <div class="kpi-value">
          <span class="valor">{{ kpi.valor }}</span>
          <span class="unidad">{{ kpi.unidad }}</span>
        </div>
        <div class="kpi-meta">
          <p><strong>Meta:</strong> {{ kpi.meta_texto }}</p>
          <p v-if="kpi.detalle" class="detalle">{{ kpi.detalle }}</p>
        </div>
        
        <!-- Gráfico del KPI -->
        <div class="kpi-grafico-wrapper">
          <KPIGraficoBarra
            v-if="kpi.key === 'tiempo_espera_promedio' || kpi.key === 'tiempo_ciclo_admision'"
            :valor="kpi.valor"
            :meta="kpi.meta"
            :unidad="kpi.unidad"
            :cumple-meta="kpi.cumple_meta"
            :color="kpi.cumple_meta === false ? '#ef4444' : '#3b82f6'"
          />
          <KPIGraficoCircular
            v-else-if="kpi.key === 'tasa_ausentismo'"
            :valor="kpi.valor"
            :max="100"
            :color="kpi.cumple_meta === false ? '#ef4444' : '#3b82f6'"
          />
          <KPIGraficoCircular
            v-else-if="kpi.key === 'tasa_ocupacion_medica'"
            :valor="kpi.valor"
            :max="100"
            :color="kpi.cumple_meta === false ? '#ef4444' : '#10b981'"
          />
          <KPIGraficoBarra
            v-else-if="kpi.key === 'nivel_satisfaccion'"
            :valor="kpi.valor"
            :meta="kpi.meta"
            :unidad="kpi.unidad"
            :cumple-meta="kpi.cumple_meta"
            :color="kpi.cumple_meta === false ? '#ef4444' : '#fbbf24'"
            :meta-color="'#10b981'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import * as api from '../services/api'
import KPIGraficoBarra from '../components/KPIGraficoBarra.vue'
import KPIGraficoCircular from '../components/KPIGraficoCircular.vue'

const kpis = ref([])
const loading = ref(true)
const error = ref(null)

const kpisConfig = {
  tiempo_espera_promedio: {
    nombre: 'Tiempo de Espera Promedio',
    meta_texto: '< 15 minutos',
    unidad_display: 'min'
  },
  tasa_ausentismo: {
    nombre: 'Tasa de Ausentismo',
    meta_texto: '< 10%',
    unidad_display: '%'
  },
  tasa_ocupacion_medica: {
    nombre: 'Tasa de Ocupación Médica',
    meta_texto: '> 85%',
    unidad_display: '%'
  },
  nivel_satisfaccion: {
    nombre: 'Nivel de Satisfacción',
    meta_texto: '> 4.0/5.0',
    unidad_display: '/5'
  },
  tiempo_ciclo_admision: {
    nombre: 'Tiempo de Ciclo de Admisión',
    meta_texto: '< 2 minutos',
    unidad_display: 'min'
  }
}

async function cargarKPIs() {
  loading.value = true
  error.value = null
  
  try {
    const data = await api.fetchAllKPIs()
    
    kpis.value = Object.entries(data).map(([key, value]) => {
      const config = kpisConfig[key]
      return {
        key,
        nombre: config.nombre,
        valor: value.valor,
        unidad: config.unidad_display,
        meta: value.meta,
        meta_texto: config.meta_texto,
        cumple_meta: value.cumple_meta,
        detalle: getDetalle(key, value)
      }
    })
  } catch (e) {
    error.value = e.message || 'Error al cargar los KPIs'
    console.error('Error:', e)
  } finally {
    loading.value = false
  }
}

function getDetalle(key, value) {
  switch (key) {
    case 'tiempo_espera_promedio':
      return `Total atenciones: ${value.total_atenciones}`
    case 'tasa_ausentismo':
      return `Citas incumplidas: ${value.citas_incumplidas} de ${value.total_citas}`
    case 'tasa_ocupacion_medica':
      return `Semana ${formatFecha(value.semana_inicio)} - ${formatFecha(value.semana_fin)}: ${value.citas_atendidas} citas atendidas / ${value.cupos_ofertados} cupos`
    case 'nivel_satisfaccion':
      return `Total calificaciones: ${value.total_calificaciones}`
    case 'tiempo_ciclo_admision':
      return `Total reservas: ${value.total_reservas}`
    default:
      return null
  }
}

function formatFecha(value) {
  if (!value) return ''
  return new Date(`${value}T00:00:00`).toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
  })
}

onMounted(() => {
  cargarKPIs()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1400px;
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

.loading, .error {
  text-align: center;
  padding: 3rem;
  color: #5f6b7a;
}

.error {
  color: #dc2626;
}

.kpis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.kpi-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #7a0000;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.kpi-card.cumple-meta {
  border-left-color: #10b981;
}

.kpi-card.no-cumple {
  border-left-color: #ef4444;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.kpi-header h3 {
  margin: 0;
  color: #1f2328;
  font-size: 1.1rem;
}

.meta-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.meta-ok {
  background: #d1fae5;
  color: #065f46;
}

.meta-fail {
  background: #fee2e2;
  color: #991b1b;
}

.kpi-value {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.valor {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2328;
}

.unidad {
  font-size: 1.2rem;
  color: #5f6b7a;
}

.kpi-meta {
  border-top: 1px solid #e4e7ec;
  padding-top: 1rem;
}

.kpi-meta p {
  margin: 0.5rem 0;
  color: #5f6b7a;
  font-size: 0.9rem;
}

.kpi-meta strong {
  color: #1f2328;
}

.detalle {
  font-size: 0.85rem;
  color: #7a0000;
}

.kpi-grafico-wrapper {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e4e7ec;
}

.kpis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}
</style>
