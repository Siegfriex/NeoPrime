import React from 'react';
import { HashRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import StudentList from './pages/StudentList';
import StudentDetail from './pages/StudentDetail';
import StudentAdd from './pages/StudentAdd';
import EvaluationEntry from './pages/EvaluationEntry';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import AdmissionSimulator from './pages/AdmissionSimulator';

// Auth Layout (No Sidebar/Header)
const AuthLayout = () => (
  <div className="min-h-screen bg-white">
    <Outlet />
  </div>
);

const App: React.FC = () => {
  return (
    <HashRouter>
      <Routes>
        {/* Auth Routes */}
        <Route path="/auth" element={<AuthLayout />}>
          <Route path="login" element={<Login />} />
          <Route path="signup" element={<Signup />} />
        </Route>

        {/* Main App Routes */}
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="students" element={<StudentList />} />
          <Route path="students/new" element={<StudentAdd />} />
          <Route path="students/:id" element={<StudentDetail />} />
          <Route path="evaluations/new" element={<EvaluationEntry />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="simulation" element={<AdmissionSimulator />} />
          <Route path="settings" element={<Settings />} />
          <Route path="profile" element={<Profile />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </HashRouter>
  );
};

export default App;
