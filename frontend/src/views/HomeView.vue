<template>
  <div class="home-container">
    <div class="home-content">
      <div class="logo-section">
        <img :src="logoBlanco" alt="UNI" class="home-logo" />
        <h1 class="home-title">MedUNI</h1>
        <p class="home-subtitle">Bienvenido al sistema</p>
      </div>

      <div class="buttons-section">
        <button class="home-btn home-btn-estudiante" @click="goToLogin('estudiante')">
          <span class="btn-icon">E</span>
          <span class="btn-text">
            <strong>Acceso Estudiante</strong>
            <small>Reserva tus citas medicas</small>
          </span>
        </button>

        <button class="home-btn home-btn-admin" @click="goToLogin('administrador')">
          <span class="btn-icon">A</span>
          <span class="btn-text">
            <strong>Acceso Administrativo</strong>
            <small>Panel de gestion y KPIs</small>
          </span>
        </button>

        <button class="home-btn home-btn-topico" @click="goToLogin('topico')">
          <span class="btn-icon">T</span>
          <span class="btn-text">
            <strong>Personal de topico</strong>
            <small>Check-in de citas reservadas</small>
          </span>
        </button>

        <button class="home-btn home-btn-medico" @click="goToLogin('medico')">
          <span class="btn-icon">M</span>
          <span class="btn-text">
            <strong>Acceso Medico</strong>
            <small>Gestion de pacientes del dia</small>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import logoBlanco from '@/assets/logo-uni-blanco.png'

const router = useRouter()

function goToLogin(type) {
  router.push({ name: 'login', query: { tipo: type } })
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #7a0000 0%, #9d0000 50%, #7a0000 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.home-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.home-content {
  text-align: center;
  z-index: 1;
  max-width: 600px;
  width: 100%;
}

.logo-section {
  margin-bottom: 3rem;
  animation: fadeInDown 0.6s ease-out;
}

.home-logo {
  width: 120px;
  height: auto;
  margin-bottom: 1.5rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.home-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  letter-spacing: 2px;
}

.home-subtitle {
  font-size: clamp(1.2rem, 2.5vw, 1.8rem);
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 300;
}

.buttons-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.home-btn {
  width: 100%;
  padding: 1.5rem 2rem;
  border: none;
  border-radius: 16px;
  background: #ffffff;
  color: #1f2328;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  text-align: left;
}

.home-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.home-btn:active {
  transform: translateY(-2px);
}

.btn-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  display: inline-grid;
  place-items: center;
  background: #7a0000;
  color: #fff;
  font-weight: 700;
  line-height: 1;
}

.btn-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
  flex: 1;
}

.btn-text strong {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2328;
}

.btn-text small {
  font-size: 0.9rem;
  color: #5f6b7a;
  font-weight: 400;
}

.home-btn-estudiante,
.home-btn-admin,
.home-btn-topico,
.home-btn-medico {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

.home-btn-estudiante:hover,
.home-btn-admin:hover,
.home-btn-topico:hover,
.home-btn-medico:hover {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 1rem;
  }

  .logo-section {
    margin-bottom: 2rem;
  }

  .home-logo {
    width: 100px;
  }

  .home-btn {
    padding: 1.25rem 1.5rem;
  }
}
</style>
