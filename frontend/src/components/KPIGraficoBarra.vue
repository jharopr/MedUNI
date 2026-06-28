<template>
  <div class="kpi-grafico-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import {
  Chart,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

Chart.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  valor: {
    type: Number,
    required: true
  },
  meta: {
    type: Number,
    required: true
  },
  unidad: {
    type: String,
    default: ''
  },
  cumpleMeta: {
    type: Boolean,
    default: null
  },
  color: {
    type: String,
    default: '#7a0000'
  },
  metaColor: {
    type: String,
    default: '#10b981'
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const createChart = () => {
  if (!chartCanvas.value) return

  // Destruir gráfico anterior si existe
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')

  const valorColor = props.cumpleMeta === false ? '#ef4444' : props.color
  const metaColorFinal = props.metaColor

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Valor Actual vs Meta'],
      datasets: [
        {
          label: `Valor Actual (${props.unidad})`,
          data: [props.valor],
          backgroundColor: valorColor,
          borderRadius: 8,
          barThickness: 60
        },
        {
          label: `Meta (${props.unidad})`,
          data: [props.meta],
          backgroundColor: metaColorFinal || '#10b981',
          borderRadius: 8,
          barThickness: 60
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const value = context.parsed.y
              if (value === null) return ''
              return `${context.dataset.label}: ${value.toFixed(2)} ${props.unidad}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return value + ' ' + props.unidad
            }
          }
        }
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => [props.valor, props.meta], () => {
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

