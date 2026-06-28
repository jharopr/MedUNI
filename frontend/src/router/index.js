import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView      from '../views/LoginView.vue'
import ReservarView   from '../views/ReservarView.vue'
import CalendarView   from '../views/CalendarView.vue'
import HorariosDiaView from '@/views/HorariosDiaView.vue'
import HorariosHoraView from '@/views/HorariosHoraView.vue'
import HistorialView from '@/views/HistorialView.vue'
import AdminDashboardView from '@/views/AdminDashboardView.vue'
// ESPECIALIDADES
import EspecialidadesView from '../views/EspecialidadesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login',     name: 'login',    component: LoginView },
    { path: '/reservar',  name: 'reservar', component: ReservarView, meta: { requiresAuth: true, requiresEstudiante: true } },
    { path: '/calendario',name: 'calendar', component: CalendarView, meta: { requiresAuth: true, requiresEstudiante: true } }, 
    { path: '/historial', name: 'historial', component: HistorialView, meta: { requiresAuth: true, requiresEstudiante: true } },
    // ESPECIALIDADES ROUTER
    { path: '/especialidades',name: 'especialidades', component: EspecialidadesView, meta: { requiresAuth: true, requiresEstudiante: true } },
    // HORARIOS DIA ROUTER
    { path: '/disponibilidad/:especialidadId',name: 'disponibilidad', component: HorariosDiaView, meta: { requiresAuth: true, requiresEstudiante: true } },
    //HORARIOS HORA ROUTER
    { path: '/horarios/:selectedDate',name: 'horarios', component: HorariosHoraView, meta: { requiresAuth: true, requiresEstudiante: true } },
    // ADMIN ROUTES
    { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboardView, meta: { requiresAuth: true, requiresAdmin: true } },
    // 👈 nuevo
    { path: '/about', redirect: '/login' },
    { path: '/:pathMatch(.*)*', component: { template: '<div class="p-3">404</div>' } },
  ],
  scrollBehavior() { return { top: 0 } }
})

// Guard sencillo
router.beforeEach((to) => {
  const isAuth = !!localStorage.getItem('token')
  const role = localStorage.getItem('role') || 'estudiante'

  // rutas protegidas
  if (to.meta.requiresAuth && !isAuth) {
    return { name: 'home' }
  }

  // Verificar rol para rutas de estudiante
  if (to.meta.requiresEstudiante && role !== 'estudiante') {
    return { name: 'admin-dashboard' }
  }

  // Verificar rol para rutas de admin
  if (to.meta.requiresAdmin && role !== 'administrador') {
    return { name: 'calendar' }
  }

  // si ya está logueado y va a login o home, redirigir según rol
  if ((to.name === 'login' || to.name === 'home') && isAuth) {
    if (role === 'administrador') {
      return { name: 'admin-dashboard' }
    }
    return { name: 'calendar' }
  }
})

export default router
