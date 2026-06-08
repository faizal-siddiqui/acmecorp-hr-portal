"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getAnalyticsSummary, AnalyticsSummary } from "@/lib/api";
import { Users, DollarSign, TrendingUp, BarChart3, Info } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export function AnalyticsKPIs() {
  const searchParams = useSearchParams();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;

    const fetchSummary = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams(searchParams.toString());
        // Remove pagination params as they don't apply to summary
        params.delete("page");
        params.delete("page_size");
        params.delete("sort_by");
        params.delete("sort_order");

        const data = await getAnalyticsSummary(params);
        if (!ignore) {
          setSummary(data);
        }
      } catch (error) {
        if (!ignore) {
          console.error("Failed to fetch analytics summary:", error);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    fetchSummary();

    return () => {
      ignore = true;
    };
  }, [searchParams]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (loading) {
    return (
      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-card rounded-lg border p-6 shadow-sm">
            <Skeleton className="mb-4 h-4 w-24" />
            <Skeleton className="h-8 w-32" />
          </div>
        ))}
      </div>
    );
  }

  if (!summary) return null;

  return (
    <div className="mb-8 space-y-2">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="bg-card rounded-lg border p-6 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-muted-foreground text-sm font-medium">Headcount</span>
            <Users className="text-muted-foreground h-4 w-4 opacity-70" />
          </div>
          <div className="text-2xl font-bold">{summary.headcount}</div>
          <p className="text-muted-foreground mt-1 text-xs">Active employees</p>
        </div>

        <div className="bg-card rounded-lg border p-6 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-muted-foreground text-sm font-medium">Total Payroll</span>
            <DollarSign className="text-muted-foreground h-4 w-4 opacity-70" />
          </div>
          <div className="text-2xl font-bold">{formatCurrency(summary.total_payroll_usd)}</div>
          <p className="text-muted-foreground mt-1 text-xs">Annual USD normalized</p>
        </div>

        <div className="bg-card rounded-lg border p-6 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-muted-foreground text-sm font-medium">Average Pay</span>
            <TrendingUp className="text-muted-foreground h-4 w-4 opacity-70" />
          </div>
          <div className="text-2xl font-bold">{formatCurrency(summary.avg_payroll_usd)}</div>
          <p className="text-muted-foreground mt-1 text-xs">Per employee (USD)</p>
        </div>

        <div className="bg-card rounded-lg border p-6 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-muted-foreground text-sm font-medium">Median Pay</span>
            <BarChart3 className="text-muted-foreground h-4 w-4 opacity-70" />
          </div>
          <div className="text-2xl font-bold">{formatCurrency(summary.median_payroll_usd)}</div>
          <p className="text-muted-foreground mt-1 text-xs">Per employee (USD)</p>
        </div>
      </div>

      <div className="text-muted-foreground flex items-center gap-1.5 px-1 text-[10px]">
        <Info className="h-3 w-3" />
        <span>FX rates as of {new Date(summary.fx_as_of).toLocaleDateString()}</span>
      </div>
    </div>
  );
}
