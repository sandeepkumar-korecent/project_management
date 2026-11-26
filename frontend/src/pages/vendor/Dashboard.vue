
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')

const summary = ref({
  total_projects: 0,
  total_tasks: 0,
  completed_tasks: 0,
  total_deliverables: 0
})

const projects = ref<any[]>([])
const tasks = ref<any[]>([])
const deliverables = ref<any[]>([])

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await call(
      'project_management.api.vendor.get_dashboard'
    )

    summary.value = response.summary
    projects.value = response.projects
    tasks.value = response.tasks
    deliverables.value = response.deliverables

  } catch (error) {
    errorMessage.value = 'Unable to load vendor dashboard. Please try again.'
  } finally {
    loading.value = false
  }
}

async function logout() {
  try {
    await call('/api/method/logout')
    router.replace('/login')
  } catch (error) {
    errorMessage.value = 'Unable to logout. Please try again.'
  }
}

function openProject(projectName: string) {
  router.push(`/vendor/project/${encodeURIComponent(projectName)}`)
}

onMounted(() => {
  loadDashboard()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Header -->
    <header class="border-b bg-white">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

        <div>
          <h1 class="text-2xl font-bold text-slate-800">
            Vendor Portal
          </h1>

          <p class="text-sm text-slate-500">
            Welcome to your project dashboard
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

      <!-- Loading -->
      <div
        v-if="loading"
        class="py-12 text-center text-slate-500"
      >
        Loading dashboard...
      </div>

      <!-- Error -->
      <div
        v-else-if="errorMessage"
        class="rounded-lg bg-red-50 p-4 text-red-600"
      >
        {{ errorMessage }}

        <button
          @click="loadDashboard"
          class="ml-2 font-semibold underline"
        >
          Retry
        </button>
      </div>

      <template v-else>

        <!-- Summary Cards -->
        <section class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <p class="text-sm text-slate-500">
              Assigned Projects
            </p>

            <h2 class="mt-3 text-3xl font-bold text-blue-600">
              {{ summary.total_projects }}
            </h2>
          </div>

          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <p class="text-sm text-slate-500">
              Total Tasks
            </p>

            <h2 class="mt-3 text-3xl font-bold text-purple-600">
              {{ summary.total_tasks }}
            </h2>
          </div>

          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <p class="text-sm text-slate-500">
              Completed Tasks
            </p>

            <h2 class="mt-3 text-3xl font-bold text-green-600">
              {{ summary.completed_tasks }}
            </h2>
          </div>

          <div class="rounded-xl border bg-white p-5 shadow-sm">
            <p class="text-sm text-slate-500">
              Total Deliverables
            </p>

            <h2 class="mt-3 text-3xl font-bold text-orange-600">
              {{ summary.total_deliverables }}
            </h2>
          </div>

        </section>

        <!-- Assigned Projects -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">

          <div class="mb-5">
            <h2 class="text-lg font-bold text-slate-800">
              My Assigned Projects
            </h2>

            <p class="mt-1 text-sm text-slate-500">
              Projects assigned to your vendor account
            </p>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">

              <thead class="border-b bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-4 py-3">Project</th>
                  <th class="px-4 py-3">Client</th>
                  <th class="px-4 py-3">Status</th>
                  <th class="px-4 py-3">Start Date</th>
                  <th class="px-4 py-3">End Date</th>
                  <th class="px-4 py-3">Action</th>
                </tr>
              </thead>

              <tbody>

                <tr
                  v-for="project in projects"
                  :key="project.name"
                  class="border-b last:border-0"
                >
                  <td class="px-4 py-4">
                    <p class="font-medium text-slate-800">
                      {{ project.project_name }}
                    </p>

                    <p class="mt-1 text-xs text-slate-400">
                      {{ project.name }}
                    </p>
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ project.client || '-' }}
                  </td>

                  <td class="px-4 py-4">
                    <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                      {{ project.status }}
                    </span>
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ project.start_date || '-' }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ project.end_date || '-' }}
                  </td>

                    <td class="px-4 py-4">
                        <button
                            @click="openProject(project.name)"
                            class="font-medium text-blue-600 hover:underline"
                        >
                            View Details
                        </button>
                        </td>

                </tr>

                <tr v-if="projects.length === 0">
                  <td
                    colspan="6"
                    class="px-4 py-8 text-center text-slate-500"
                  >
                    No projects assigned to your vendor account.
                  </td>
                </tr>
                

              </tbody>
            </table>
          </div>

        </section>

        <!-- Recent Tasks -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">

          <h2 class="mb-5 text-lg font-bold text-slate-800">
            Recent Project Tasks
          </h2>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">

              <thead class="border-b bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-4 py-3">Task</th>
                  <th class="px-4 py-3">Project</th>
                  <th class="px-4 py-3">Status</th>
                  <th class="px-4 py-3">Due Date</th>
                  <th class="px-4 py-3">Progress</th>
                </tr>
              </thead>

              <tbody>

                <tr
                  v-for="task in tasks"
                  :key="task.name"
                  class="border-b last:border-0"
                >
                  <td class="px-4 py-4 font-medium text-slate-800">
                    {{ task.task_title }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ task.project }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ task.status }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ task.due_date || '-' }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ task.progress || 0 }}%
                  </td>
                </tr>

                <tr v-if="tasks.length === 0">
                  <td
                    colspan="5"
                    class="px-4 py-8 text-center text-slate-500"
                  >
                    No tasks found.
                  </td>
                </tr>

              </tbody>
            </table>
          </div>

        </section>

        <!-- Recent Deliverables -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">

          <h2 class="mb-5 text-lg font-bold text-slate-800">
            Recent Deliverables
          </h2>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">

              <thead class="border-b bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-4 py-3">Deliverable</th>
                  <th class="px-4 py-3">Project</th>
                  <th class="px-4 py-3">Status</th>
                  <th class="px-4 py-3">Submitted On</th>
                  <th class="px-4 py-3">File</th>
                </tr>
              </thead>

              <tbody>

                <tr
                  v-for="item in deliverables"
                  :key="item.name"
                  class="border-b last:border-0"
                >
                  <td class="px-4 py-4 font-medium text-slate-800">
                    {{ item.deliverable_name }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ item.project }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ item.status }}
                  </td>

                  <td class="px-4 py-4 text-slate-600">
                    {{ item.submitted_on || '-' }}
                  </td>

                  <td class="px-4 py-4">
                    <a
                      v-if="item.file"
                      :href="item.file"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="font-medium text-blue-600 hover:underline"
                    >
                      View File
                    </a>

                    <span v-else class="text-slate-400">
                      No File
                    </span>
                  </td>
                </tr>

                <tr v-if="deliverables.length === 0">
                  <td
                    colspan="5"
                    class="px-4 py-8 text-center text-slate-500"
                  >
                    No deliverables found.
                  </td>
                </tr>

              </tbody>
            </table>
          </div>

        </section>

      </template>

    </main>
  </div>
</template>
