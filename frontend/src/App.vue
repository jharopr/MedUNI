<script setup>
import { useAuth } from './stores/auth'
import { useRoute, useRouter } from 'vue-router'
const auth = useAuth()
const route = useRoute()
const router = useRouter()
import logoBlanco from "@/assets/logo-uni-blanco.png";
const onLogout = async () => {
  await auth.logout()
  router.replace({ name: 'home' })
}
</script>

<template>
  <nav v-if="route.path !== '/login' && route.path !== '/'" class="navbar navbar-expand-lg nav-primary">
    <div class="container">
      <RouterLink class="navbar-brand text-white fw-semibold d-flex align-items-center gap-2" to="/">
  <img :src="logoBlanco" alt="UNI" class="brand-img" />
        MedUNI
      </RouterLink>
      <div class="collapse navbar-collapse show">
        <ul class="navbar-nav ms-auto gap-2 align-items-center">
          <li class="nav-item" v-if="!auth.isAuth">
            <RouterLink class="btn btn-light btn-sm" to="/login">Ingresar</RouterLink>
          </li>
          <template v-else>
            <li class="nav-item" v-if="auth.isEstudiante">
              <RouterLink class="nav-link text-white" to="/historial">
                Historial
              </RouterLink>
            </li>
            <li class="nav-item" v-if="auth.isEstudiante">
              <RouterLink class="nav-link text-white" to="/especialidades">
                Reservar cita
              </RouterLink>
            </li>
            <li class="nav-item" v-if="auth.isTopico">
              <RouterLink class="nav-link text-white" to="/topico/check-in">
                Check-in
              </RouterLink>
            </li>
            <li class="nav-item">
              <button class="btn btn-outline-light btn-sm" @click="onLogout">Salir</button>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
  <main class="container py-4"><RouterView /></main>
</template>

<style scoped>
.nav-primary{ background: #7b0000; }
.brand-img{ height:48px; width:auto; }

.nav-link {
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 500;
  padding: 0.5rem 1rem !important;
  border-radius: 6px;
  transition: all 0.2s;
  text-decoration: none;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff !important;
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  color: #fff !important;
}
</style>
