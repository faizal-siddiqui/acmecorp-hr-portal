"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";

export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    // Test protected route
    apiFetch("/employees/")
      .then(async (res) => {
        if (res.ok) {
          const data = await res.json();
          setMessage(data.message);
        }
      })
      .finally(() => setLoading(false));
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold tracking-tight">Salary Management</h1>
        <p className="text-muted-foreground text-sm">
          ACME Corp HR — employee directory, compensation &amp; analytics
        </p>
      </div>
      
      {message && (
        <p className="text-green-600 font-medium">
          {message}
        </p>
      )}

      <div className="flex gap-4">
        <Button variant="outline" onClick={handleLogout}>
          Logout
        </Button>
      </div>

      <p className="text-muted-foreground rounded border px-4 py-2 font-mono text-sm">
        ✅ Authentication Implemented (Story B1)
      </p>
    </main>
  );
}
