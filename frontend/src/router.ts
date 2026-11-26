
import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory('/portal'),

  routes: [
    {
      path: '/',
      component: () => import('./pages/Home.vue')
    },
    {
      path: '/login',
      component: () => import('./pages/Login.vue')
    },

    {
      path: '/client/dashboard',
      component: () => import('./pages/client/Dashboard.vue')
    },
    {
      path: '/client/project/:projectName',
      component: () => import('./pages/client/ProjectDetails.vue')
    },

    // Vendor Portal
    {
      path: '/vendor/dashboard',
      component: () => import('./pages/vendor/Dashboard.vue')
    },
    {
      path: '/vendor/project/:projectName',
      component: () => import('./pages/vendor/ProjectDetails.vue')
    },

    {
      path: '/:pathMatch(.*)*',
      component: () => import('./pages/NotFound.vue')
    }
  ]
})
