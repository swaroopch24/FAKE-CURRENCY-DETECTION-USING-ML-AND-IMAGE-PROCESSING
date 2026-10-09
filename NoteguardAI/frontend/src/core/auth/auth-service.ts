import apiClient from "../api/client";

export interface UserProfile {
  id: string;
  full_name: string;
  email: string;
  role: string;
}

export class AuthService {
  static getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  static getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("refresh_token");
  }

  static getUserProfile(): UserProfile | null {
    if (typeof window === "undefined") return null;
    const profile = localStorage.getItem("user_profile");
    if (!profile) return null;
    try {
      return JSON.parse(profile);
    } catch {
      return null;
    }
  }

  static setSession(accessToken: string, refreshToken: string, user: UserProfile): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    localStorage.setItem("user_profile", JSON.stringify(user));
  }

  static clearSession(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_profile");
  }

  static isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  static async login(email: string, password: string): Promise<UserProfile> {
    const res = await apiClient.post("/auth/login", { email, password });
    if (res.data?.success) {
      const { access_token, refresh_token, user } = res.data.data;
      this.setSession(access_token, refresh_token, user);
      return user;
    }
    throw new Error("Authentication failed");
  }

  static async register(fullName: string, email: string, password: string): Promise<UserProfile> {
    const res = await apiClient.post("/auth/register", {
      full_name: fullName,
      email,
      password
    });
    if (res.data?.success) {
      return res.data.data;
    }
    throw new Error("Registration failed");
  }

  static async logout(): Promise<void> {
    try {
      await apiClient.post("/auth/logout");
    } catch (err) {
      console.error("Logout request to server failed", err);
    } finally {
      this.clearSession();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  }
}
