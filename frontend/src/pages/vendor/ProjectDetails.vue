
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { call, FileUploader } from 'frappe-ui'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const project = ref<any>(null)
const tasks = ref<any[]>([])
const deliverables = ref<any[]>([])

const deliverableName = ref('')
const description = ref('')
const fileUrl = ref('')
const fileName = ref('')

// Raven project discussion
const discussionMessages = ref<any[]>([])
const discussionInput = ref('')
const discussionLoading = ref(false)
const discussionSending = ref(false)
const discussionError = ref('')

// Load project details
async function loadProjectDetails() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await call(
      'project_management.api.vendor.get_project_details',
      {
        project_name: String(route.params.projectName)
      }
    )

    project.value = response.project
    tasks.value = response.tasks
    deliverables.value = response.deliverables

    await loadProjectDiscussion()

  } catch (error) {
    errorMessage.value = 'Unable to load project details.'
  } finally {
    loading.value = false
  }
}

// Load Raven project discussion
async function loadProjectDiscussion() {
  if (!project.value) {
    return
  }

  discussionLoading.value = true
  discussionError.value = ''

  try {
    const response = await call(
      'project_management.api.discussion.get_project_discussion',
      {
        project_name: project.value.name
      }
    )

    // Raven returns newest messages first.
    // Reverse them to display oldest messages first.
    discussionMessages.value = (response.messages || []).reverse()

  } catch (error: any) {
    discussionError.value =
      error?.messages?.[0] ||
      error?.message ||
      'Unable to load project discussion.'
  } finally {
    discussionLoading.value = false
  }
}

// Send Raven project message
async function sendProjectMessage() {
  discussionError.value = ''

  const message = discussionInput.value.trim()

  if (!message) {
    discussionError.value = 'Please enter a message.'
    return
  }

  if (message.length > 5000) {
    discussionError.value = 'Message cannot be longer than 5000 characters.'
    return
  }

  discussionSending.value = true

  try {
    const response = await call(
      'project_management.api.discussion.send_project_message',
      {
        project_name: project.value.name,
        message: message
      }
    )

    discussionMessages.value.push(response)
    discussionInput.value = ''

  } catch (error: any) {
    discussionError.value =
      error?.messages?.[0] ||
      error?.message ||
      'Unable to send message. Please try again.'
  } finally {
    discussionSending.value = false
  }
}

// Format message date
function formatMessageDate(date: string) {
  if (!date) {
    return ''
  }

  return new Date(date).toLocaleString()
}

// Handle uploaded file
function onFileUploaded(file: any) {
  fileUrl.value = file.file_url
  fileName.value = file.file_name
  errorMessage.value = ''
  successMessage.value = ''
}

// Submit deliverable
async function submitDeliverable() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!deliverableName.value.trim()) {
    errorMessage.value = 'Please enter a deliverable name.'
    return
  }

  if (!fileUrl.value) {
    errorMessage.value = 'Please upload a file.'
    return
  }

  submitting.value = true

  try {
    await call(
      'project_management.api.vendor.submit_deliverable',
      {
        project_name: project.value.name,
        deliverable_name: deliverableName.value,
        description: description.value,
        file_url: fileUrl.value
      }
    )

    successMessage.value = 'Deliverable submitted successfully.'

    deliverableName.value = ''
    description.value = ''
    fileUrl.value = ''
    fileName.value = ''

    await loadProjectDetails()

  } catch (error) {
    errorMessage.value = 'Unable to submit deliverable. Please try again.'
  } finally {
    submitting.value = false
  }
}

function goBack() {
  router.push('/vendor/dashboard')
}

async function logout() {
  try {
    await call('/api/method/logout')
    router.replace('/login')
  } catch (error) {
    errorMessage.value = 'Unable to logout.'
  }
}

onMounted(() => {
  loadProjectDetails()
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
            Project Details
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

      <button
        @click="goBack"
        class="mb-6 text-sm font-medium text-blue-600 hover:underline"
      >
        ← Back to Dashboard
      </button>

      <div v-if="loading" class="py-12 text-center text-slate-500">
        Loading project details...
      </div>

      <div
        v-else-if="errorMessage && !project"
        class="rounded-lg bg-red-50 p-4 text-red-600"
      >
        {{ errorMessage }}
      </div>

      <template v-else-if="project">

        <!-- Project Information -->
        <section class="rounded-xl border bg-white p-6 shadow-sm">
          <h2 class="text-2xl font-bold text-slate-800">
            {{ project.project_name }}
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Project ID: {{ project.name }}
          </p>

          <div class="mt-6 grid gap-5 sm:grid-cols-3">
            <div>
              <p class="text-sm text-slate-500">Client</p>
              <p class="mt-1 font-medium text-slate-800">
                {{ project.client || '-' }}
              </p>
            </div>

            <div>
              <p class="text-sm text-slate-500">Start Date</p>
              <p class="mt-1 font-medium text-slate-800">
                {{ project.start_date || '-' }}
              </p>
            </div>

            <div>
              <p class="text-sm text-slate-500">End Date</p>
              <p class="mt-1 font-medium text-slate-800">
                {{ project.end_date || '-' }}
              </p>
            </div>
          </div>

          <div v-if="project.description" class="mt-5 border-t pt-4">
            <h3 class="font-semibold text-slate-800">
              Description
            </h3>
            <p class="mt-2 whitespace-pre-line text-sm text-slate-600">
              {{ project.description }}
            </p>
          </div>
        </section>

        <!-- Raven Project Discussion -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">

          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-800">
                Project Discussion
              </h2>

              <p class="mt-1 text-sm text-slate-500">
                Communicate with the project manager and your project team.
              </p>
            </div>

            <button
              @click="loadProjectDiscussion"
              :disabled="discussionLoading"
              class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            >
              {{ discussionLoading ? 'Refreshing...' : 'Refresh' }}
            </button>
          </div>

          <!-- Messages -->
          <div class="mt-5 max-h-96 space-y-4 overflow-y-auto rounded-lg bg-slate-50 p-4">

            <div
              v-if="discussionLoading && discussionMessages.length === 0"
              class="py-6 text-center text-sm text-slate-500"
            >
              Loading discussion...
            </div>

            <div
              v-for="message in discussionMessages"
              :key="message.name"
              class="rounded-lg border bg-white p-4"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <p class="font-semibold text-slate-800">
                  {{ message.full_name || message.owner }}
                </p>

                <p class="text-xs text-slate-400">
                  {{ formatMessageDate(message.creation) }}
                </p>
              </div>

              <p class="mt-2 whitespace-pre-line break-words text-sm leading-6 text-slate-600">
                {{ message.text }}
              </p>
            </div>

            <div
              v-if="!discussionLoading && discussionMessages.length === 0"
              class="py-6 text-center text-sm text-slate-500"
            >
              No messages yet. Start the project discussion.
            </div>
          </div>

          <!-- Discussion Error -->
          <div
            v-if="discussionError"
            class="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-600"
          >
            {{ discussionError }}
          </div>

          <!-- Send Message -->
          <div class="mt-5 border-t pt-5">
            <textarea
              v-model="discussionInput"
              rows="3"
              maxlength="5000"
              placeholder="Write a message to the project team..."
              class="w-full rounded-lg border border-slate-300 p-3 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            ></textarea>

            <div class="mt-3 flex flex-wrap items-center justify-between gap-3">
              <p class="text-xs text-slate-400">
                {{ discussionInput.length }}/5000 characters
              </p>

              <button
                @click="sendProjectMessage"
                :disabled="discussionSending || !discussionInput.trim()"
                class="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {{ discussionSending ? 'Sending...' : 'Send Message' }}
              </button>
            </div>
          </div>

        </section>

        <!-- Project Tasks -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">
          <h2 class="mb-5 text-lg font-bold text-slate-800">
            Project Tasks
          </h2>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="border-b bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-4 py-3">Task</th>
                  <th class="px-4 py-3">Assigned To</th>
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
                    {{ task.assigned_to || '-' }}
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
                  <td colspan="5" class="px-4 py-8 text-center text-slate-500">
                    No tasks found.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Submit Deliverable -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">
          <h2 class="text-lg font-bold text-slate-800">
            Submit Deliverable
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Upload your completed work for this project.
          </p>

          <div class="mt-5 space-y-4">

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Deliverable Name
              </label>

              <input
                v-model="deliverableName"
                type="text"
                placeholder="Enter deliverable name"
                class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Description
              </label>

              <textarea
                v-model="description"
                rows="3"
                placeholder="Describe your deliverable"
                class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
              ></textarea>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-slate-700">
                Upload File
              </label>

              <FileUploader
                doctype="Project"
                :docname="project.name"
                fieldname="description"
                :file-types="['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', 'image/*']"
                @success="onFileUploaded"
              >
                <template #default="{ uploading, progress, error, openFileSelector }">
                  <button
                    type="button"
                    @click="openFileSelector"
                    :disabled="uploading"
                    class="rounded-lg border border-blue-300 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100 disabled:opacity-50"
                  >
                    {{ uploading ? `Uploading ${progress}%` : 'Choose File' }}
                  </button>

                  <p v-if="error" class="mt-2 text-sm text-red-600">
                    {{ error }}
                  </p>
                </template>
              </FileUploader>

              <p v-if="fileName" class="mt-2 text-sm text-green-700">
                Uploaded: {{ fileName }}
              </p>
            </div>

            <div
              v-if="errorMessage"
              class="rounded-lg bg-red-50 p-3 text-sm text-red-600"
            >
              {{ errorMessage }}
            </div>

            <div
              v-if="successMessage"
              class="rounded-lg bg-green-50 p-3 text-sm text-green-700"
            >
              {{ successMessage }}
            </div>

            <button
              @click="submitDeliverable"
              :disabled="submitting"
              class="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {{ submitting ? 'Submitting...' : 'Submit Deliverable' }}
            </button>

          </div>
        </section>

        <!-- Existing Deliverables -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">
          <h2 class="mb-5 text-lg font-bold text-slate-800">
            Submitted Deliverables
          </h2>

          <div class="space-y-3">
            <div
              v-for="item in deliverables"
              :key="item.name"
              class="rounded-lg border p-4"
            >
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 class="font-semibold text-slate-800">
                    {{ item.deliverable_name }}
                  </h3>
                  <p class="mt-1 text-xs text-slate-500">
                    Submitted: {{ item.submitted_on || '-' }}
                  </p>
                </div>

                <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                  {{ item.status }}
                </span>
              </div>

              <a
                v-if="item.file"
                :href="item.file"
                target="_blank"
                rel="noopener noreferrer"
                class="mt-3 inline-block text-sm text-blue-600 hover:underline"
              >
                View File
              </a>

              <p
                v-if="item.client_feedback"
                class="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-600"
              >
                Client Feedback: {{ item.client_feedback }}
              </p>
            </div>

            <p
              v-if="deliverables.length === 0"
              class="py-6 text-center text-sm text-slate-500"
            >
              No deliverables submitted yet.
            </p>
          </div>
        </section>

      </template>
    </main>
  </div>
</template>
