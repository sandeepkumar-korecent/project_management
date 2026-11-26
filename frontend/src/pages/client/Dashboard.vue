
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')

const dashboard = ref({
  total_projects: 0,
  total_tasks: 0,
  completed_tasks: 0,
  pending_tasks: 0,
  projects: [] as any[],
  tasks: [] as any[],
  deliverables: [] as any[]
})

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await call(
      'project_management.api.client.get_dashboard'
    )

    dashboard.value = response
  } catch (error) {
    errorMessage.value = 'Unable to load dashboard.'
  } finally {
    loading.value = false
  }
}

function openProject(projectName: string) {
  router.push(`/client/project/${encodeURIComponent(projectName)}`)
}

async function logout() {
  try {
    await call('/api/method/logout')
    router.replace('/login')
  } catch (error) {
    errorMessage.value = 'Unable to logout. Please try again.'
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">

    <header class="border-b bg-white">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div>
          <h1 class="text-2xl font-bold text-slate-800">
            Client Portal
          </h1>
          <p class="text-sm text-slate-500">
            Project Management Dashboard
          </p>
        </div>

        <button
          @click="logout"
          class="rounded-lg bg-red-50 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-100"
        >
          Logout
        </button>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-6 py-8">

      <div v-if="loading" class="py-12 text-center text-slate-500">
        Loading dashboard...
      </div>

      <div
        v-else-if="errorMessage"
        class="rounded-lg bg-red-50 p-4 text-red-600"
      >
        {{ errorMessage }}
      </div>

      <template v-else>

        <!-- Summary Cards -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

          <div class="rounded-xl border bg-white p-6 shadow-sm">
            <p class="text-sm text-slate-500">Total Projects</p>
            <h2 class="mt-3 text-3xl font-bold text-slate-800">
              {{ dashboard.total_projects }}
            </h2>
          </div>

          <div class="rounded-xl border bg-white p-6 shadow-sm">
            <p class="text-sm text-slate-500">Total Tasks</p>
            <h2 class="mt-3 text-3xl font-bold text-blue-600">
              {{ dashboard.total_tasks }}
            </h2>
          </div>

          <div class="rounded-xl border bg-white p-6 shadow-sm">
            <p class="text-sm text-slate-500">Completed Tasks</p>
            <h2 class="mt-3 text-3xl font-bold text-green-600">
              {{ dashboard.completed_tasks }}
            </h2>
          </div>

          <div class="rounded-xl border bg-white p-6 shadow-sm">
            <p class="text-sm text-slate-500">Pending Tasks</p>
            <h2 class="mt-3 text-3xl font-bold text-orange-600">
              {{ dashboard.pending_tasks }}
            </h2>
          </div>

        </div>

        <!-- Projects -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">
          <h2 class="mb-5 text-lg font-bold text-slate-800">
            My Projects
          </h2>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">

              <thead class="border-b bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-4 py-3">Project</th>
                  <th class="px-4 py-3">Status</th>
                  <th class="px-4 py-3">Start Date</th>
                  <th class="px-4 py-3">End Date</th>
                  <th class="px-4 py-3">Action</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="project in dashboard.projects"
                  :key="project.name"
                  class="border-b last:border-0"
                >
                  <td class="px-4 py-3 font-medium text-slate-800">
                    {{ project.project_name }}
                  </td>

                  <td class="px-4 py-3">
                    <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                      {{ project.status }}
                    </span>
                  </td>

                  <td class="px-4 py-3 text-slate-600">
                    {{ project.start_date || '-' }}
                  </td>

                  <td class="px-4 py-3 text-slate-600">
                    {{ project.end_date || '-' }}
                  </td>

                  <td class="px-4 py-3">
                    <button
                      @click="openProject(project.name)"
                      class="font-medium text-blue-600 hover:underline"
                    >
                      View Details
                    </button>
                  </td>
                </tr>

                <tr v-if="dashboard.projects.length === 0">
                  <td colspan="5" class="px-4 py-8 text-center text-slate-500">
                    No projects available.
                  </td>
                </tr>
              </tbody>

            </table>
          </div>
        </section>

        <!-- Recent Tasks -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">
          <h2 class="mb-5 text-lg font-bold text-slate-800">
            Recent Tasks
          </h2>

          <div v-if="dashboard.tasks.length === 0" class="text-sm text-slate-500">
            No tasks available.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="task in dashboard.tasks"
              :key="task.name"
              class="flex flex-wrap items-center justify-between gap-3 border-b pb-3 last:border-0"
            >
              <div>
                <p class="font-medium text-slate-800">
                  {{ task.task_title }}
                </p>
                <p class="text-xs text-slate-500">
                  {{ task.project }}
                </p>
              </div>

              <div class="text-right">
                <p class="text-sm font-medium text-slate-700">
                  {{ task.status }}
                </p>
                <p class="text-xs text-slate-500">
                  Due: {{ task.due_date || '-' }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- Recent Deliverables -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">
          <h2 class="mb-5 text-lg font-bold text-slate-800">
            Recent Deliverables
          </h2>

          <div v-if="dashboard.deliverables.length === 0" class="text-sm text-slate-500">
            No deliverables available.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="item in dashboard.deliverables"
              :key="item.name"
              class="flex flex-wrap items-center justify-between gap-3 border-b pb-3 last:border-0"
            >
              <div>
                <p class="font-medium text-slate-800">
                  {{ item.deliverable_name }}
                </p>
                <p class="text-xs text-slate-500">
                  {{ item.project }}
                </p>
              </div>

              <span class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
                {{ item.status }}
              </span>
            </div>
          </div>
        </section>

      </template>
    </main>
  </div>
</template>
