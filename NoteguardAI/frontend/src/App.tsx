import React from "react";
import { Routes, Route } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";
import VerifyPage from "@/pages/VerifyPage";
import HistoryPage from "@/pages/HistoryPage";
import AnalyticsPage from "@/pages/AnalyticsPage";
import ReportsPage from "@/pages/ReportsPage";
import SettingsPage from "@/pages/SettingsPage";
import AdminPage from "@/pages/AdminPage";
import AboutPage from "@/pages/AboutPage";
import LogoutPage from "@/pages/LogoutPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/verify" element={<VerifyPage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="/analytics" element={<AnalyticsPage />} />
      <Route path="/reports" element={<ReportsPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/admin" element={<AdminPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/logout" element={<LogoutPage />} />
    </Routes>
  );
}
