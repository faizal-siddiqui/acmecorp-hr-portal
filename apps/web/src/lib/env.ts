/**
 * Typed, validated environment variables for the web app.
 * NEXT_PUBLIC_* values are inlined at build time by Next.js.
 */

function readEnv(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (value === undefined || value === "") {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export const env = {
  apiUrl: readEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000"),
} as const;
