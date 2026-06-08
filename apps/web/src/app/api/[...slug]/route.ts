import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.INTERNAL_API_URL || "http://localhost:8000";

async function handleRequest(
  req: NextRequest,
  { params }: { params: Promise<{ slug: string[] }> },
) {
  const url = new URL(req.url);
  const searchParams = url.searchParams.toString();
  // Get the path after /api
  const path = url.pathname.replace(/^\/api/, "");
  const targetUrl = `${API_URL}${path}${searchParams ? `?${searchParams}` : ""}`;

  const headers = new Headers(req.headers);
  // Remove host header to avoid issues with some backend servers
  headers.delete("host");
  // Ensure the backend knows the actual origin if needed
  const ip = req.headers.get("x-forwarded-for") || "";
  headers.set("X-Forwarded-For", ip);

  const options: RequestInit = {
    method: req.method,
    headers,
  };

  // Only include body for methods that support it
  if (!["GET", "HEAD"].includes(req.method)) {
    try {
      options.body = await req.blob();
    } catch {
      // No body or error reading body
    }
  }

  try {
    const response = await fetch(targetUrl, options);

    // Get the response body as a blob
    const body = await response.blob();

    // Create a new response with the same status and headers
    const res = new NextResponse(body, {
      status: response.status,
      statusText: response.statusText,
    });

    // Copy headers from the backend response, but skip some that might cause issues
    response.headers.forEach((value, key) => {
      if (!["content-encoding", "transfer-encoding", "content-length"].includes(key.toLowerCase())) {
        res.headers.set(key, value);
      }
    });

    return res;
  } catch (error) {
    console.error("Proxy error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}

export const GET = handleRequest;
export const POST = handleRequest;
export const PUT = handleRequest;
export const DELETE = handleRequest;
export const PATCH = handleRequest;
