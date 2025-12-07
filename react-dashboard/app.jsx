import React, { useMemo } from 'react'

function useQuery() {
  return useMemo(() => new URLSearchParams(window.location.search), [])
}

export default function App() {
  const q = useQuery()
  const role = q.get('role') || 'guest'
  const user = q.get('user') || 'unknown'

  return (
    <div style={{ fontFamily: 'system-ui', padding: 20 }}>
      <h1>Dashboard</h1>
      <p>User: <b>{user}</b></p>
      <p>Role: <b>{role}</b></p>

      {role === 'super-admin' && <SuperAdminPanel />}
      {role === 'admin' && <AdminPanel />}
      {role === 'teacher' && <TeacherPanel />}
      {role === 'student' && <StudentPanel />}

      <hr />
      <p>Tip: This app is embedded in PyQt6 QWebEngineView.</p>
    </div>
  )
}

function Card({ title, children }) {
  return (
    <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, marginBottom: 12 }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      {children}
    </div>
  )
}

function SuperAdminPanel() {
  return (
    <>
      <Card title="System Overview">
        <ul>
          <li>Total Users</li>
          <li>Active Sessions</li>
          <li>DB Health</li>
        </ul>
      </Card>
      <Card title="Global Settings">
        <button>Backup DB</button> <button>Rotate Keys</button>
      </Card>
    </>
  )
}

function AdminPanel() {
  return (
    <>
      <Card title="User Management">
        <button>Create User</button> <button>Disable User</button>
      </Card>
      <Card title="Content Controls">
        <button>Whitelist</button> <button>Blacklist</button>
      </Card>
    </>
  )
}

function TeacherPanel() {
  return (
    <>
      <Card title="Classroom">
        <button>Start Session</button> <button>Assign Task</button>
      </Card>
      <Card title="Reports">
        <button>View Activity</button>
      </Card>
    </>
  )
}

function StudentPanel() {
  return (
    <>
      <Card title="Student View">
        <p>Limited access.</p>
      </Card>
    </>
  )
}