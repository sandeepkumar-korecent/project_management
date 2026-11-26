
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { call } from 'frappe-ui'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const reviewing = ref('')
const reviewMessage = ref('')

const project = ref<any>(null)
const tasks = ref<any[]>([])
const deliverables = ref<any[]>([])
const members = ref<any[]>([])

// Raven project discussion
const discussionMessages = ref<any[]>([])
const discussionInput = ref('')
const discussionLoading = ref(false)
const discussionSending = ref(false)
const discussionError = ref('')

// Task comments
const activeTaskComments = ref('')
const taskComments = ref<Record<string, any[]>>({})
const taskCommentInputs = ref<Record<string, string>>({})
const taskCommentLoading = ref('')

// Client member invitation
const fullName = ref('')
const email = ref('')
const inviting = ref(false)
const inviteMessage = ref('')
const inviteErrorMessage = ref('')

// Load project details
async function loadProjectDetails() {
  loading.value = true
  errorMessage.value = ''

  try {
    const projectName = String(route.params.projectName)

    const response = await call(
      'project_management.api.client.get_project_details',
      {
        project_name: projectName
      }
    )

    project.value = response.project
    tasks.value = response.tasks
    deliverables.value = response.deliverables
    members.value = response.members || []

    await loadProjectDiscussion()

  } catch (error) {
    errorMessage.value = 'Unable to load project details or you do not have access to this project.'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/client/dashboard')
}

async function logout() {
  try {
    await call('/api/method/logout')
    router.replace('/login')
  } catch (error) {
    errorMessage.value = 'Unable to logout. Please try again.'
  }
}

function getProgress(progress: number) {
  if (!progress) {
    return 0
  }

  return Math.min(100, Math.max(0, progress))
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

// Send a Raven project message
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

    // Add the newly sent message to the discussion
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

// Invite a new client team member
async function inviteMember() {
  inviteMessage.value = ''
  inviteErrorMessage.value = ''

  if (!fullName.value.trim()) {
    inviteErrorMessage.value = 'Please enter the member name.'
    return
  }

  if (!email.value.trim()) {
    inviteErrorMessage.value = 'Please enter the member email.'
    return
  }

  inviting.value = true

  try {
    await call(
      'project_management.api.client.invite_client_member',
      {
        project_name: project.value.name,
        full_name: fullName.value.trim(),
        email: email.value.trim()
      }
    )

    fullName.value = ''
    email.value = ''

    await loadProjectDetails()

    inviteMessage.value = 'Client team member invited successfully.'

  } catch (error: any) {
    inviteErrorMessage.value =
      error?.messages?.[0] ||
      error?.message ||
      'Unable to invite this member. Please try again.'
  } finally {
    inviting.value = false
  }
}

// Show or hide task comments
async function toggleTaskComments(taskName: string) {
  if (activeTaskComments.value === taskName) {
    activeTaskComments.value = ''
    return
  }

  activeTaskComments.value = taskName

  if (taskComments.value[taskName]) {
    return
  }

  try {
    const response = await call(
      'project_management.api.client.get_comments',
      {
        reference_doctype: 'Task',
        reference_name: taskName
      }
    )

    taskComments.value[taskName] = response || []

  } catch (error) {
    taskComments.value[taskName] = []
  }
}

// Add task comment
async function addTaskComment(taskName: string) {
  const content = taskCommentInputs.value[taskName] || ''

  if (!content.trim()) {
    return
  }

  taskCommentLoading.value = taskName

  try {
    await call(
      'project_management.api.client.add_comment',
      {
        reference_doctype: 'Task',
        reference_name: taskName,
        content: content.trim()
      }
    )

    taskCommentInputs.value[taskName] = ''

    const response = await call(
      'project_management.api.client.get_comments',
      {
        reference_doctype: 'Task',
        reference_name: taskName
      }
    )

    taskComments.value[taskName] = response || []

  } catch (error) {
    alert('Unable to add task comment. Please try again.')
  } finally {
    taskCommentLoading.value = ''
  }
}

// Review deliverable
async function reviewDeliverable(item: any, decision: string) {
  reviewMessage.value = ''

  if (
    decision === 'Changes Requested' &&
    !item.new_feedback?.trim()
  ) {
    reviewMessage.value = 'Please enter feedback before requesting changes.'
    return
  }

  reviewing.value = item.name

  try {
    await call(
      'project_management.api.client.review_deliverable',
      {
        deliverable_name: item.name,
        decision: decision,
        feedback: item.new_feedback || ''
      }
    )

    reviewMessage.value = 'Deliverable review saved successfully.'

    await loadProjectDetails()

  } catch (error) {
    reviewMessage.value = 'Unable to save the review. Please try again.'
  } finally {
    reviewing.value = ''
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
            Client Portal
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
        v-else-if="errorMessage"
        class="rounded-lg bg-red-50 p-4 text-red-600"
      >
        {{ errorMessage }}
      </div>

      <template v-else-if="project">

        <!-- Project Information -->
        <section class="rounded-xl border bg-white p-6 shadow-sm">

          <div class="flex flex-wrap items-start justify-between gap-4">

            <div>
              <h2 class="text-2xl font-bold text-slate-800">
                {{ project.project_name }}
              </h2>

              <p class="mt-1 text-sm text-slate-500">
                Project ID: {{ project.name }}
              </p>
            </div>

            <span class="rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700">
              {{ project.status }}
            </span>

          </div>

          <div class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-3">

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

          <div v-if="project.description" class="mt-6 border-t pt-5">
            <h3 class="mb-2 font-semibold text-slate-800">
              Project Description
            </h3>

            <p class="whitespace-pre-line text-sm leading-6 text-slate-600">
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
                Share project updates and communicate with the project team.
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

        <!-- Client Team Members -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">

          <div class="mb-5">
            <h2 class="text-lg font-bold text-slate-800">
              Client Team Members
            </h2>

            <p class="mt-1 text-sm text-slate-500">
              Invite your colleagues to access and monitor this project.
            </p>
          </div>

          <!-- Invitation Form -->
          <div class="rounded-lg bg-slate-50 p-5">

            <h3 class="mb-4 font-semibold text-slate-800">
              Invite New Member
            </h3>

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">

              <div>
                <label class="mb-2 block text-sm font-medium text-slate-700">
                  Full Name
                </label>

                <input
                  v-model="fullName"
                  type="text"
                  placeholder="Enter full name"
                  class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div>
                <label class="mb-2 block text-sm font-medium text-slate-700">
                  Email Address
                </label>

                <input
                  v-model="email"
                  type="email"
                  placeholder="Enter email address"
                  class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

            </div>

            <button
              @click="inviteMember"
              :disabled="inviting"
              class="mt-4 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {{ inviting ? 'Inviting...' : 'Invite Member' }}
            </button>

            <div
              v-if="inviteMessage"
              class="mt-4 rounded-lg bg-green-50 p-3 text-sm text-green-700"
            >
              {{ inviteMessage }}
            </div>

            <div
              v-if="inviteErrorMessage"
              class="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-600"
            >
              {{ inviteErrorMessage }}
            </div>

          </div>

          <!-- Existing Members -->
          <div class="mt-6">

            <div class="mb-4 flex items-center justify-between">
              <h3 class="font-semibold text-slate-800">
                Existing Members
              </h3>

              <span class="text-sm text-slate-500">
                {{ members.length }} Members
              </span>
            </div>

            <div class="space-y-3">

              <div
                v-for="member in members"
                :key="member.user"
                class="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-4"
              >

                <div>
                  <p class="font-medium text-slate-800">
                    {{ member.full_name || member.user }}
                  </p>

                  <p class="mt-1 text-sm text-slate-500">
                    {{ member.user }}
                  </p>
                </div>

                <span class="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">
                  Project Member
                </span>

              </div>

              <div
                v-if="members.length === 0"
                class="py-6 text-center text-sm text-slate-500"
              >
                No additional client members have been added yet.
              </div>

            </div>

          </div>

        </section>

        <!-- Task Progress -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">

          <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
            <h2 class="text-lg font-bold text-slate-800">
              Project Tasks
            </h2>

            <span class="text-sm text-slate-500">
              {{ tasks.length }} Tasks
            </span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">

              <thead class="border-b bg-slate-50 text-slate-600">
                <tr>
                  <th class="px-4 py-3">Task</th>
                  <th class="px-4 py-3">Status</th>
                  <th class="px-4 py-3">Start Date</th>
                  <th class="px-4 py-3">Due Date</th>
                  <th class="px-4 py-3">Progress</th>
                </tr>
              </thead>

              <tbody>

                <template v-for="task in tasks" :key="task.name">

                  <tr class="border-b">

                    <td class="px-4 py-4">
                      <p class="font-medium text-slate-800">
                        {{ task.task_title }}
                      </p>

                      <p class="mt-1 text-xs text-slate-400">
                        {{ task.name }}
                      </p>

                      <button
                        @click="toggleTaskComments(task.name)"
                        class="mt-2 text-xs font-semibold text-blue-600 hover:underline"
                      >
                        {{ activeTaskComments === task.name ? 'Hide Comments' : 'View / Add Comments' }}
                      </button>
                    </td>

                    <td class="px-4 py-4 text-slate-600">
                      {{ task.status }}
                    </td>

                    <td class="px-4 py-4 text-slate-600">
                      {{ task.start_date || '-' }}
                    </td>

                    <td class="px-4 py-4 text-slate-600">
                      {{ task.due_date || '-' }}
                    </td>

                    <td class="min-w-40 px-4 py-4">

                      <div class="mb-2 flex justify-between text-xs">
                        <span class="text-slate-500">Progress</span>

                        <span class="font-semibold text-slate-700">
                          {{ getProgress(task.progress) }}%
                        </span>
                      </div>

                      <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                        <div
                          class="h-full rounded-full bg-blue-600"
                          :style="{ width: getProgress(task.progress) + '%' }"
                        ></div>
                      </div>

                    </td>

                  </tr>

                  <!-- Task Comments -->
                  <tr
                    v-if="activeTaskComments === task.name"
                    class="border-b bg-slate-50"
                  >

                    <td colspan="5" class="px-4 py-5">

                      <h4 class="mb-4 font-semibold text-slate-800">
                        Comments for {{ task.task_title }}
                      </h4>

                      <div class="space-y-3">

                        <div
                          v-for="comment in (taskComments[task.name] || [])"
                          :key="comment.name"
                          class="rounded-lg border bg-white p-3"
                        >

                          <div class="flex flex-wrap justify-between gap-2">

                            <p class="text-sm font-semibold text-slate-800">
                              {{ comment.full_name }}
                            </p>

                            <p class="text-xs text-slate-400">
                              {{ comment.creation }}
                            </p>

                          </div>

                          <p class="mt-2 whitespace-pre-line text-sm text-slate-600">
                            {{ comment.content }}
                          </p>

                        </div>

                        <p
                          v-if="taskComments[task.name]?.length === 0"
                          class="text-sm text-slate-500"
                        >
                          No comments on this task yet.
                        </p>

                      </div>

                      <div class="mt-4">

                        <textarea
                          v-model="taskCommentInputs[task.name]"
                          rows="2"
                          placeholder="Write a comment about this task..."
                          class="w-full rounded-lg border border-slate-300 bg-white p-3 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        ></textarea>

                        <button
                          @click="addTaskComment(task.name)"
                          :disabled="taskCommentLoading === task.name"
                          class="mt-3 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                        >
                          {{ taskCommentLoading === task.name ? 'Posting...' : 'Post Comment' }}
                        </button>

                      </div>

                    </td>

                  </tr>

                </template>

                <tr v-if="tasks.length === 0">
                  <td colspan="5" class="px-4 py-8 text-center text-slate-500">
                    No tasks found for this project.
                  </td>
                </tr>

              </tbody>
            </table>
          </div>

        </section>

        <!-- Deliverables and Client Review -->
        <section class="mt-8 rounded-xl border bg-white p-6 shadow-sm">

          <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
            <h2 class="text-lg font-bold text-slate-800">
              Project Deliverables
            </h2>

            <span class="text-sm text-slate-500">
              {{ deliverables.length }} Deliverables
            </span>
          </div>

          <!-- Review Message -->
          <div
            v-if="reviewMessage"
            class="mb-5 rounded-lg bg-blue-50 p-3 text-sm text-blue-700"
          >
            {{ reviewMessage }}
          </div>

          <div class="space-y-4">

            <div
              v-for="item in deliverables"
              :key="item.name"
              class="rounded-lg border border-slate-200 p-4"
            >

              <!-- Deliverable Information -->
              <div class="flex flex-wrap items-start justify-between gap-3">

                <div>
                  <h3 class="font-semibold text-slate-800">
                    {{ item.deliverable_name }}
                  </h3>

                  <p class="mt-1 text-xs text-slate-500">
                    Deliverable ID: {{ item.name }}
                  </p>

                  <p class="mt-1 text-xs text-slate-500">
                    Submitted: {{ item.submitted_on || '-' }}
                  </p>
                </div>

                <span
                  class="rounded-full px-3 py-1 text-xs font-medium"
                  :class="{
                    'bg-blue-50 text-blue-700': item.status === 'Submitted',
                    'bg-green-50 text-green-700': item.status === 'Accepted',
                    'bg-orange-50 text-orange-700': item.status === 'Changes Requested'
                  }"
                >
                  {{ item.status }}
                </span>

              </div>

              <!-- Submitted File -->
              <div v-if="item.file" class="mt-4">
                <a
                  :href="item.file"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-sm font-medium text-blue-600 hover:underline"
                >
                  View Submitted File
                </a>
              </div>

              <!-- Previous Client Feedback -->
              <div
                v-if="item.client_feedback"
                class="mt-4 rounded-lg bg-slate-50 p-3"
              >
                <p class="text-xs font-semibold text-slate-600">
                  Client Feedback
                </p>

                <p class="mt-1 whitespace-pre-line text-sm text-slate-700">
                  {{ item.client_feedback }}
                </p>
              </div>

              <!-- Review Actions -->
              <div
                v-if="item.status === 'Submitted'"
                class="mt-5 border-t pt-4"
              >

                <h4 class="mb-2 text-sm font-semibold text-slate-800">
                  Review Deliverable
                </h4>

                <textarea
                  v-model="item.new_feedback"
                  rows="3"
                  placeholder="Enter feedback here. Feedback is required when requesting changes."
                  class="w-full rounded-lg border border-slate-300 p-3 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                ></textarea>

                <div class="mt-4 flex flex-wrap gap-3">

                  <button
                    @click="reviewDeliverable(item, 'Accepted')"
                    :disabled="reviewing === item.name"
                    class="rounded-lg bg-green-600 px-5 py-2 text-sm font-semibold text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {{ reviewing === item.name ? 'Saving...' : 'Accept Deliverable' }}
                  </button>

                  <button
                    @click="reviewDeliverable(item, 'Changes Requested')"
                    :disabled="reviewing === item.name"
                    class="rounded-lg bg-orange-500 px-5 py-2 text-sm font-semibold text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Request Changes
                  </button>

                </div>

              </div>

              <!-- Accepted Status -->
              <div
                v-else-if="item.status === 'Accepted'"
                class="mt-4 rounded-lg bg-green-50 p-3 text-sm font-medium text-green-700"
              >
                Deliverable accepted.
              </div>

              <!-- Changes Requested Status -->
              <div
                v-else-if="item.status === 'Changes Requested'"
                class="mt-4 rounded-lg bg-orange-50 p-3 text-sm text-orange-700"
              >
                Changes requested. The team needs to submit an updated deliverable.
              </div>

            </div>

            <div
              v-if="deliverables.length === 0"
              class="py-8 text-center text-sm text-slate-500"
            >
              No deliverables submitted for this project.
            </div>

          </div>

        </section>

      </template>

    </main>
  </div>
</template>
