import { render, screen, waitFor } from "@testing-library/react";
import { AnalyticsKPIs } from "./AnalyticsKPIs";
import { getAnalyticsSummary } from "@/lib/api";
import { vi, describe, it, expect, beforeEach } from "vitest";

vi.mock("@/lib/api", () => ({
  getAnalyticsSummary: vi.fn(),
}));

describe("AnalyticsKPIs", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    vi.mocked(getAnalyticsSummary).mockReturnValue(new Promise(() => {}));
    render(<AnalyticsKPIs />);
    // Skeleton loaders should be present
    expect(document.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  });

  it("renders summary data correctly", async () => {
    const mockSummary = {
      headcount: 100,
      total_payroll_usd: 10000000,
      avg_payroll_usd: 100000,
      median_payroll_usd: 95000,
      fx_as_of: "2026-06-06",
    };
    vi.mocked(getAnalyticsSummary).mockResolvedValue(mockSummary);

    render(<AnalyticsKPIs />);

    await waitFor(() => {
      expect(screen.getByText("100")).toBeInTheDocument();
      expect(screen.getByText("$10,000,000")).toBeInTheDocument();
      expect(screen.getByText("$100,000")).toBeInTheDocument();
      expect(screen.getByText("$95,000")).toBeInTheDocument();
      expect(screen.getByText(/FX rates as of/)).toBeInTheDocument();
    });
  });

  it("handles error state gracefully", async () => {
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    vi.mocked(getAnalyticsSummary).mockRejectedValue(new Error("Failed to fetch"));

    render(<AnalyticsKPIs />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        "Failed to fetch analytics summary:",
        expect.any(Error),
      );
    });
    consoleSpy.mockRestore();
  });
});
