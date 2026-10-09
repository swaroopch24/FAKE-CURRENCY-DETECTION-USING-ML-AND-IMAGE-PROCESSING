import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Alert } from "@/components/ui/alert";
import { AuthService } from "@/core/auth/auth-service";
import { User, Lock, Eye, EyeOff, Shield } from "lucide-react";

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register" | "forgot">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = () => {
    const err: Record<string, string> = {};

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      err.email = "Please enter a valid email address.";
    }

    if (mode === "register" && fullName.trim().length === 0) {
      err.fullName = "Full Name is required.";
    }

    if (mode === "login" || mode === "register") {
      if (password.length < 6) {
        err.password = "Password must be at least 6 characters.";
      }
    }

    if (mode === "register" && password !== confirmPassword) {
      err.confirmPassword = "Passwords do not match.";
    }

    setErrors(err);
    return Object.keys(err).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError("");
    setSuccessMsg("");
    
    if (!validateForm()) return;

    setIsLoading(true);

    try {
      if (mode === "login") {
        await AuthService.login(email, password);
        setSuccessMsg("Session authorized. Redirecting to FCD Dashboard...");
        setTimeout(() => {
          navigate("/dashboard");
        }, 600);
      } else if (mode === "register") {
        await AuthService.register(fullName, email, password);
        setSuccessMsg("Registration successful! You can now log in.");
        setFullName("");
        setPassword("");
        setConfirmPassword("");
        setTimeout(() => {
          setMode("login");
          setSuccessMsg("");
        }, 1200);
      } else {
        setSuccessMsg("Password reset link sent to your email.");
      }
    } catch (err: any) {
      const apiError = err.response?.data?.detail?.error?.message || err.message;
      setServerError(apiError || "Authentication service failed. Please check credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070B14] flex flex-col items-center justify-center p-6 relative overflow-hidden select-none">
      {/* Background Graphic Element */}
      <div className="absolute right-10 top-1/2 -translate-y-1/2 opacity-10 pointer-events-none hidden lg:block">
        <div className="w-[500px] h-[500px] rounded-full border-4 border-blue-500 flex items-center justify-center">
          <div className="w-[350px] h-[350px] rounded-3xl bg-blue-600/30 flex items-center justify-center text-blue-400 text-9xl font-black">
            ₹
          </div>
        </div>
      </div>

      {/* Brand Header */}
      <div className="flex items-center gap-3 mb-8 cursor-pointer" onClick={() => navigate("/")}>
        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
          <Shield className="h-6 w-6 fill-current text-white" />
        </div>
        <span className="font-black tracking-wider text-slate-100 text-xl">FCD SYSTEM</span>
      </div>

      {/* Main Login Card */}
      <Card className="w-full max-w-md p-8 border-slate-800/80 bg-slate-900/60 backdrop-blur-xl shadow-[0_0_40px_rgba(0,0,0,0.8)] relative z-10">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-extrabold text-slate-100 mb-1">
            {mode === "login" && "Welcome Back!"}
            {mode === "register" && "Create Account"}
            {mode === "forgot" && "Reset Password"}
          </h2>
          <p className="text-xs text-slate-400">
            {mode === "login" && "Login to your account"}
            {mode === "register" && "Register to access FCD System"}
            {mode === "forgot" && "Enter email to receive reset instructions"}
          </p>
        </div>

        {serverError && (
          <Alert variant="destructive" title="Error" className="mb-6">
            {serverError}
          </Alert>
        )}

        {successMsg && (
          <Alert variant="success" title="Success" className="mb-6">
            {successMsg}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <div className="relative">
              <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Full Name"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                error={errors.fullName}
                className="pl-9 bg-slate-950/80 border-slate-800 text-sm"
              />
            </div>
          )}

          <div className="relative">
            <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Username or Email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              error={errors.email}
              className="pl-9 bg-slate-950/80 border-slate-800 text-sm"
            />
          </div>

          {(mode === "login" || mode === "register") && (
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <Input
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                error={errors.password}
                className="pl-9 pr-10 bg-slate-950/80 border-slate-800 text-sm"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3 text-slate-400 hover:text-slate-200"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          )}

          {mode === "register" && (
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <Input
                type="password"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                error={errors.confirmPassword}
                className="pl-9 bg-slate-950/80 border-slate-800 text-sm"
              />
            </div>
          )}

          {mode === "login" && (
            <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={e => setRememberMe(e.target.checked)}
                  className="rounded bg-slate-950 border-slate-800 text-blue-600 focus:ring-0"
                />
                <span>Remember Me</span>
              </label>
              <button
                type="button"
                onClick={() => setMode("forgot")}
                className="text-blue-400 hover:text-blue-300 transition-colors"
              >
                Forgot Password?
              </button>
            </div>
          )}

          <Button
            type="submit"
            className="w-full py-2.5 mt-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(59,130,246,0.4)] transition-all"
            isLoading={isLoading}
          >
            {mode === "login" && "LOGIN"}
            {mode === "register" && "REGISTER"}
            {mode === "forgot" && "SEND RESET LINK"}
          </Button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-800/80 text-center text-xs text-slate-400">
          {mode === "login" && (
            <p>
              Don't have an account?{" "}
              <button onClick={() => setMode("register")} className="text-blue-400 hover:underline font-semibold">
                Register
              </button>
            </p>
          )}
          {mode === "register" && (
            <p>
              Already have an account?{" "}
              <button onClick={() => setMode("login")} className="text-blue-400 hover:underline font-semibold">
                Login
              </button>
            </p>
          )}
          {mode === "forgot" && (
            <button onClick={() => setMode("login")} className="text-blue-400 hover:underline font-semibold">
              Back to Login
            </button>
          )}
        </div>
      </Card>
    </div>
  );
}
