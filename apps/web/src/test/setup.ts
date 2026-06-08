import "@testing-library/jest-dom";
import { vi } from "vitest";

const mockPush = vi.fn();
const mockReplace = vi.fn();
const mockBack = vi.fn();
const mockPrefetch = vi.fn();

// Mock Next.js router
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
    prefetch: mockPrefetch,
    back: mockBack,
  }),
  usePathname: () => "",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock fetch
global.fetch = vi.fn();
