<template>
  <article class="summary-card" :class="{ 'summary-card--active': totalCitas > 0 }">
    <div class="summary-card__icon" aria-hidden="true">
      <i :class="iconClass"></i>
    </div>

    <div class="summary-card__body">
      <h2>{{ nombre }}</h2>
      <p>{{ statusText }}</p>
    </div>

    <div class="summary-card__metric" :aria-label="`${totalCitas} citas reservadas`">
      <strong>{{ totalCitas }}</strong>
      <span>citas</span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { getEspecialidadIconClassById } from '@/utils/especialidades'

const props = defineProps({
  especialidadId: { type: Number, required: true },
  nombre: { type: String, required: true },
  totalCitas: { type: Number, default: 0 },
})

const iconClass = computed(() => getEspecialidadIconClassById(props.especialidadId))

const statusText = computed(() => {
  if (props.totalCitas === 0) return 'Sin citas pendientes'
  if (props.totalCitas === 1) return '1 cita pendiente de llegada'
  return `${props.totalCitas} citas pendientes de llegada`
})
</script>

<style scoped>
.summary-card {
  min-height: 104px;
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.96)),
    #fff;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

.summary-card--active {
  border-color: rgba(122, 0, 0, 0.28);
  box-shadow: 0 12px 26px rgba(122, 0, 0, 0.1);
}

.summary-card__icon {
  width: 52px;
  height: 52px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: #f3f4f6;
  color: #7a0000;
  border: 1px solid #e5e7eb;
}

.summary-card--active .summary-card__icon {
  background: #7a0000;
  color: #fff;
  border-color: #7a0000;
}

.summary-card__icon i {
  font-size: 23px;
  line-height: 1;
}

.summary-card__body {
  min-width: 0;
}

.summary-card__body h2 {
  margin: 0;
  color: #111827;
  font-size: 1.02rem;
  font-weight: 750;
  line-height: 1.2;
}

.summary-card__body p {
  margin: 5px 0 0;
  color: #667085;
  font-size: 0.9rem;
  line-height: 1.25;
}

.summary-card__metric {
  min-width: 64px;
  padding: 8px 10px;
  border-radius: 8px;
  display: grid;
  justify-items: center;
  background: #f8fafc;
  color: #475467;
}

.summary-card--active .summary-card__metric {
  background: #fff1f1;
  color: #7a0000;
}

.summary-card__metric strong {
  font-size: 1.45rem;
  line-height: 1;
}

.summary-card__metric span {
  margin-top: 3px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

@media (max-width: 460px) {
  .summary-card {
    grid-template-columns: 48px minmax(0, 1fr);
  }

  .summary-card__metric {
    grid-column: 1 / -1;
    grid-template-columns: auto auto;
    justify-content: center;
    gap: 6px;
  }
}
</style>
