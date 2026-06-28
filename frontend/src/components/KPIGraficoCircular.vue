<template>
  <div class="kpi-grafico-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import {
  Chart,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

Chart.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  valor: {
    type: Number,
    required: true
  },
  max: {
    type: Number,
    required: true
  },
  color: {
    type: String,
    default: '#7a0000'
  },
  backgroundColor: {
    type: String,
    default: '#e5e7eb'
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const createChart = () => {
  if (!chartCanvas.value) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  
  const porcentaje = Math.min((props.valor / props.max) * 100, 100)
  const restante = 100 - porcentaje

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Alcanzado', 'Restante'],
      datasets: [{
        data: [porcentaje, restante],
        backgroundColor: [props.color, props.backgroundColor],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const value = context.parsed
              if (context.dataIndex === 0) {
                return `Alcanzado: ${props.valor.toFixed(2)}% (${value.toFixed(1)}%)`
              }
              return `${context.label}: ${value.toFixed(1)}%`
            }
          }
        }
      },
      cutout: '70%'
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => [props.valor, props.max], () => {
  createChart()
}, { deep: true })

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.kpi-grafico-container {
  width: 100%;
  height: 250px;
  margin-top: 1rem;
}
</style>

