# Dashboard Dynamic Data Integration

## ✅ Completed Updates

The dashboard has been updated to fetch and display real data from the database instead of using mock data.

### 1. API Integration

**Updated API Base URL:**
- Changed from `http://localhost:4000` to `http://localhost:5000` (Flask API server)

**New API Functions:**
- `getStatsOverview()` - Fetches dashboard statistics
- `getUsers()` - Fetches all users with proper data transformation
- `getStudents()` - Fetches all students with their modes
- `getActivity()` - Fetches activity logs
- `getViolations()` - Fetches security violations
- `setStudentMode()` - Updates student mode
- `toggleUserStatus()` - Toggles user active status

### 2. React Query Hooks

Created `useDashboardData.ts` with custom hooks:
- `useStats()` - Fetches and caches statistics (refetches every 30s)
- `useUsers()` - Fetches and caches users (refetches every 30s)
- `useStudents()` - Fetches and caches students (refetches every 30s)
- `useActivity()` - Fetches activity logs (refetches every 10s)
- `useViolations()` - Fetches violations (refetches every 30s)
- `useUpdateStudentMode()` - Mutation for updating student mode
- `useToggleUserStatus()` - Mutation for toggling user status

### 3. Updated Components

**AdminDashboard:**
- ✅ Real-time statistics from database
- ✅ Dynamic user count, active users, students by mode
- ✅ Recent violations count
- ✅ Loading states with skeletons
- ✅ Error handling

**UserTable:**
- ✅ Fetches real users from database
- ✅ Displays Gmail, role, status, last login
- ✅ Toggle user status functionality
- ✅ Loading and empty states

**StudentTable (New):**
- ✅ Displays all students with their assigned modes
- ✅ Color-coded mode badges (Exam, Study, Restricted, Free)
- ✅ Violation count per student
- ✅ Mode change dropdown (Admin/Teacher only)
- ✅ Real-time updates

**ViolationsTable (New):**
- ✅ Displays security violations
- ✅ Severity indicators (Low, Medium, High, Critical)
- ✅ Violation type, description, attempted URL
- ✅ Filterable by student ID
- ✅ Timestamp display

**Charts:**
- ✅ `RoleDistributionChart` - Uses real user data
- ✅ `LoginActivityChart` - Uses real activity logs
- ✅ Loading states
- ✅ Empty state handling

**TeacherDashboard:**
- ✅ Real student statistics
- ✅ Activity and violations tabs
- ✅ Student management interface

### 4. API Server Updates

**New Endpoints:**
- `GET /api/students` - Get all students
- `POST /api/students/<id>/mode` - Set student mode
- `GET /api/activity` - Get activity logs (supports `studentId` and `limit` params)
- `GET /api/violations` - Get violations (supports `studentId` and `limit` params)
- `PATCH /api/users/<id>/toggle-status` - Toggle user status

**Enhanced Endpoints:**
- `GET /api/stats` - Now includes mode distribution and recent violations
- `GET /api/users` - Returns Gmail and teacher approval status

### 5. Data Flow

```
Database (MySQL)
    ↓
Flask API Server (Port 5000)
    ↓
React Dashboard (Port 3000)
    ↓
React Query (Caching & Refetching)
    ↓
UI Components (Charts, Tables, Cards)
```

### 6. Features

**Real-time Updates:**
- Statistics refresh every 30 seconds
- Activity logs refresh every 10 seconds
- Automatic cache invalidation on mutations

**Loading States:**
- Skeleton loaders for all data tables
- Loading indicators for charts
- Graceful error handling

**Data Visualization:**
- Role distribution pie chart
- Login activity area chart
- Student mode statistics
- Violation severity indicators

**Interactive Features:**
- Change student modes (Admin/Teacher)
- Toggle user status (Admin)
- Filter violations by student
- View activity logs

### 7. Environment Configuration

Make sure your `.env` or environment variables are set:

```env
VITE_API_URL=http://localhost:5000
```

Or update `react-dashboard/src/lib/api.ts` if using a different API URL.

### 8. Testing

To test the dynamic dashboard:

1. **Start the API server:**
   ```bash
   python api_server.py
   ```

2. **Start the React dashboard:**
   ```bash
   cd react-dashboard
   npm run dev
   ```

3. **Open dashboard from PyQt6:**
   - Login as Admin/Teacher/Super Admin
   - Click Dashboard button
   - Dashboard should load with real data

### 9. Data Transformation

The API responses are transformed to match the dashboard's TypeScript interfaces:

- User roles: `superadmin` → `super-admin`
- Database fields: `created_at` → `createdAt`
- Gmail field mapping
- Mode enum values

### 10. Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Export functionality for reports
- [ ] Advanced filtering and search
- [ ] Pagination for large datasets
- [ ] Activity timeline visualization
- [ ] Student performance metrics
- [ ] Mode change history chart

## 🎯 Key Benefits

1. **Live Data**: Dashboard shows real-time database information
2. **Automatic Updates**: Data refreshes automatically without page reload
3. **Performance**: React Query caching reduces API calls
4. **User Experience**: Loading states and error handling
5. **Scalability**: Easy to add new data sources and visualizations

