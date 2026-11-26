# Project Management

A Frappe application for managing projects, tasks, time logs, deliverables, and communication between project teams, clients, and vendors.

It has a Frappe Desk interface for internal users and separate web portals for clients and vendors. Raven is used for project discussions so that internal, client, and vendor conversations remain in separate channels.

## Features

### Projects

- Create and update projects
- Assign a Project Manager
- Add internal team members
- Add client and vendor members
- Track project dates, status, and description
- Configure task reminders

### Tasks

- Create tasks under a project
- Assign a task to a Frappe User
- Set start date, due date, progress, and completion date
- Track the status of a task as Open, In Progress, Blocked, or Completed
- Use Frappe list, calendar, and Gantt views
- Restrict task updates to the assigned user

### My Day

Users can maintain a personal list of assigned tasks for a selected working day. Each entry can have a plan date and display order.

### Time Tracking

- Add time logs to tasks
- Record start time, end time, project, user, and description
- Show the calculated time spent
- Limit time log entries to the logged-in user and assigned tasks

### Deliverables

- Vendors can submit deliverables from the Vendor Portal
- A deliverable can be connected to one or more tasks in the same project
- Project Managers can review the submitted work
- Delivery status is tracked as Submitted, Changes Requested, or Accepted
- Review comments and client feedback are stored with the deliverable

### Client Portal

Client users can:

- Sign in to a separate project portal
- View projects linked to their client account
- Open project details and task information
- View submitted deliverables
- Submit feedback where review access is enabled
- Join the client project discussion channel

### Vendor Portal

Vendor users can:

- Sign in to a separate vendor portal
- View projects linked to their vendor account
- View only tasks assigned to them
- View and manage their own deliverables
- Submit deliverables against project tasks
- Join the vendor project discussion channel

### Reports and Dashboard

The app includes project, task, and deliverable summaries, along with:

- Projects by Status chart
- Tasks by Status chart
- Deliverables by Status chart
- Project Progress report
- Time Tracking report
- Project and task number cards

## User Roles

| Role | Access |
|---|---|
| System Manager | Full administrative access |
| Project Manager | Manage projects, team members, tasks, deliverables, reports, and discussions |
| Project Team Member | Work on assigned tasks and use project discussions |
| Project Client | View permitted client projects and use the client portal |
| Project Vendor | View permitted vendor projects and use the vendor portal |

The app uses the standard Frappe `User` document; no separate custom user document is created.

## How Access Works

Internal users work through Frappe Desk. Client and vendor users work through the Vue-based portal available at `/portal`.

- Client API methods return projects and records belonging to the logged-in client
- Vendor API methods return projects and records belonging to the logged-in vendor
- Vendors can see only tasks assigned to their own Frappe User
- Vendors can see only deliverables submitted by their own Frappe User
- Portal APIs use the current Frappe session and do not accept an arbitrary user ID
- Document and task permissions are checked on the server

## Project Discussions

The app creates a private Raven workspace for each project. Three channels are created:

| Channel | Members | Purpose |
|---|---|---|
| `internal` | Project Manager and Project Team Members | Internal project discussion |
| `discussion` | Project Manager, Project Team Members, and Client Members | Client-facing discussion |
| `external` | Project Manager, Project Team Members, and Vendor Members | Vendor-facing discussion |

Client users do not receive access to the vendor channel, and vendor users do not receive access to the client channel. Project managers and team members can use all project channels from Desk and Raven.

When project membership changes, the app updates the associated Raven workspace membership.

## Tech Stack

- Frappe Framework
- Python
- MariaDB
- Redis
- Vue 3
- TypeScript
- Vue Router
- Tailwind CSS
- Vite
- Raven

## App Structure

```text
project_management/
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── client/
│       │   └── vendor/
│       ├── App.vue
│       ├── main.ts
│       └── router.ts
├── images/
└── project_management/
    ├── api/
    ├── project_management/
    │   ├── dashboard_chart/
    │   ├── doctype/
    │   ├── number_card/
    │   └── report/
    ├── hooks.py
    ├── permissions.py
    ├── raven_integration.py
    ├── tasks.py
    └── utils.py
```

## Requirements

Before installing the app, make sure the following are available:

- Frappe Bench
- A compatible Frappe Framework version
- Python 3.14 or a Python version supported by the target Frappe version
- Node.js and npm
- MariaDB
- Redis
- Git
- Raven, if project discussions are required

## Installation

From the Bench directory:

```bash
cd ~/frappe/frappe-bench
```

Add the app:

```bash
bench get-app <repository-url>
```

Install it on a site:

```bash
bench --site <site-name> install-app project_management
```

Run migrations:

```bash
bench --site <site-name> migrate
bench --site <site-name> clear-cache
```

### Install Raven

If Raven is not already installed:

```bash
bench get-app --branch develop https://github.com/frappe/raven
bench --site <site-name> install-app raven
```

Use the branch and version that are compatible with the target Frappe and Bench installation.

### Build the portal

Install dependencies and build the Vue frontend:

```bash
cd apps/project_management
npm install
npm run build
```

Build Bench assets:

```bash
cd ../..
bench build --app project_management
```

Start the development server:

```bash
bench start
```

Open the Frappe site in a browser and sign in with a user that has the required role and document permissions.

## Development Commands

```bash
# Run migrations
bench --site <site-name> migrate

# Clear cached data
bench --site <site-name> clear-cache

# Run the frontend development server
cd apps/project_management
npm run dev

# Build application assets
cd ~/frappe/frappe-bench
bench build --app project_management
```

## Screenshots

### Portal Login

![Project Portal login](images/Screenshot%20from%202026-11-26%2015-50-28.png)

### Portal Views

![Portal project view](images/Screenshot%20from%202026-11-26%2015-50-40.png)

![Portal project information](images/Screenshot%20from%202026-11-26%2015-50-49.png)

![Project details](images/Screenshot%20from%202026-11-26%2015-51-06.png)

![Project workspace](images/Screenshot%20from%202026-11-26%2015-51-15.png)

### Dashboard and Project Workflow

<p align="center">
  <img src="images/Screenshot%20from%202026-11-26%2015-51-35.png" alt="Portal dashboard" width="48%">
  <img src="images/Screenshot%20from%202026-11-26%2015-51-45.png" alt="Project overview" width="48%">
</p>

<p align="center">
  <img src="images/Screenshot%20from%202026-11-26%2015-51-59.png" alt="Portal workflow" width="48%">
  <img src="images/Screenshot%20from%202026-11-26%2015-52-05.png" alt="Project management" width="48%">
</p>

## Security Notes

- Use server-side permissions; do not rely on hidden frontend controls
- Keep client and vendor data isolated by account membership
- Do not trust user IDs sent from the browser
- Check task assignment and deliverable ownership on the server
- Keep client and vendor discussions in separate Raven channels
- Do not commit passwords, API keys, CSRF tokens, or private session cookies
- Review screenshots before sharing them so they do not contain sensitive company or user data

## License

MIT License

## Author

Sandeep Kumar
