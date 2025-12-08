import React from 'react'
import { Routes, Route, useSearchParams } from 'react-router-dom'

function Layout({ children }) {
  const [params] = useSearchParams()
  const user = params.get('user') || 'unknown'
  return (
    <div style={{ fontFamily: 'system-ui', padding: 20 }}>
      <h1>Dashboard</h1>
      <p>User: <b>{user}</b></p>
      {children}
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

export default function App() {
  return (
    <Routes>
      <Route path="/dashboard/super-admin" element={<Layout><SuperAdminPanel /></Layout>} />
      <Route path="/dashboard/admin" element={<Layout><AdminPanel /></Layout>} />
      <Route path="/dashboard/teacher" element={<Layout><TeacherPanel /></Layout>} />
      <Route path="*" element={<Layout><p>No route matched.</p></Layout>} />
    </Routes>
  )
}