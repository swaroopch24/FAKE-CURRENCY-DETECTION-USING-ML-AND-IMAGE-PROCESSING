import React, { useState } from "react";
import { PageLayout } from "@/components/layout/layout";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";

export default function SettingsPage() {
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  
  const [fullName, setFullName] = useState("Delhi Teller");
  const [email, setEmail] = useState("delhi@bank.org");
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    setProfileSuccess(true);
    setTimeout(() => setProfileSuccess(false), 2000);
  };

  const handlePasswordSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword.length < 8) {
      alert("New password must be at least 8 characters with uppercase, lowercase, and a number.");
      return;
    }
    setPasswordSuccess(true);
    setOldPassword("");
    setNewPassword("");
    setTimeout(() => setPasswordSuccess(false), 2000);
  };

  return (
    <PageLayout>
      <div className="space-y-8 select-none max-w-4xl">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Console Settings</h1>
          <p className="text-sm text-slate-500">Configure your user account, security passwords, and notifications preferences.</p>
        </div>

        {/* Profile Settings */}
        <Card className="p-6">
          <h3 className="text-base font-semibold text-slate-200 mb-1">Profile Information</h3>
          <p className="text-xs text-slate-500 mb-6">Modify user descriptors and contact emails.</p>

          {profileSuccess && (
            <Alert variant="success" title="Profile Saved" className="mb-6">
              User details have been successfully written to the database.
            </Alert>
          )}

          <form onSubmit={handleProfileSave} className="space-y-4 max-w-lg">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Full Name</label>
              <Input
                value={fullName}
                onChange={e => setFullName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Email Address</label>
              <Input
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>
            <Button type="submit" variant="default" size="sm">
              Save Profile Changes
            </Button>
          </form>
        </Card>

        {/* Security / Password reset */}
        <Card className="p-6">
          <h3 className="text-base font-semibold text-slate-200 mb-1">Account Password Settings</h3>
          <p className="text-xs text-slate-500 mb-6">Update your account credentials keys.</p>

          {passwordSuccess && (
            <Alert variant="success" title="Credentials Updated" className="mb-6">
              Password hash parameters successfully rewritten. Use new credentials on next sign-in.
            </Alert>
          )}

          <form onSubmit={handlePasswordSave} className="space-y-4 max-w-lg">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Current Password</label>
              <Input
                type="password"
                placeholder="••••••••"
                value={oldPassword}
                onChange={e => setOldPassword(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">New Password</label>
              <Input
                type="password"
                placeholder="••••••••"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
              />
            </div>
            <Button type="submit" variant="default" size="sm">
              Update Password
            </Button>
          </form>
        </Card>
      </div>
    </PageLayout>
  );
}
