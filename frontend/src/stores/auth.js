import { defineStore } from 'pinia'
import * as api from '../services/api'

export const useAuth = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    role: localStorage.getItem('role') || 'estudiante',
    loading: false,
    error: null,
  }),
  getters: { 
    isAuth: (s) => !!s.token,
    isAdmin: (s) => s.role === 'administrador',
    isEstudiante: (s) => s.role === 'estudiante',
    isTopico: (s) => s.role === 'topico',
    isMedico: (s) => s.role === 'medico'
  },
  actions: {
    async login(username, password, role = 'estudiante') {
      this.loading = true; this.error = null
      try {
        const resp = await api.login({ username, password, role })

        // Acepta { token, user } o { access_token, user }
        const token = resp?.token ?? resp?.access_token
        const user  = resp?.userData ?? resp?.user ?? null
        const userRole = resp?.role || role

        if (!token) throw new Error('Respuesta de login inválida')

        this.token = token
        this.user  = user
        this.role  = userRole
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('role', userRole)
        return true
      } catch (e) {
        this.error = e.message || 'Credenciales inválidas'
        throw e
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.user = null
      this.role = 'estudiante'
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('role')
      // (redirige desde el componente: router.replace({ name: 'login' }))
    },
  },
})
