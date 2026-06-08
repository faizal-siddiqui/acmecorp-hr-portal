"use client";

import { useEffect, useState } from "react";
import { getEmployeeHistory, SalaryHistoryItem } from "@/lib/api";
import { History, User, Calendar, ArrowRight } from "lucide-react";

interface CompensationHistoryProps {
  employeeId: string;
  refreshTrigger?: number;
}

export function CompensationHistory({ employeeId, refreshTrigger }: CompensationHistoryProps) {
  const [history, setHistory] = useState<SalaryHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const data = await getEmployeeHistory(employeeId);
        setHistory(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load history");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [employeeId, refreshTrigger]);

  if (loading && history.length === 0) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-muted h-20 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600">{error}</div>;
  }

  if (history.length === 0) {
    return (
      <div className="bg-muted/30 rounded-xl border border-dashed py-12 text-center">
        <History className="text-muted-foreground/50 mx-auto mb-3 h-8 w-8" />
        <p className="text-muted-foreground text-sm">No compensation changes recorded yet.</p>
      </div>
    );
  }

  const formatField = (field: string) => {
    return field.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const formatValue = (field: string, value: string | null) => {
    if (value === null) return "N/A";
    if (field.includes("annual") || field.includes("base")) {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD", // This is a simplification, ideally we'd use the record's currency
        maximumFractionDigits: 0,
      }).format(parseInt(value));
    }
    return value;
  };

  return (
    <div className="relative space-y-0">
      {/* Vertical line */}
      <div className="bg-border absolute top-2 bottom-2 left-[19px] w-0.5" />

      <div className="space-y-6">
        {history.map((item) => (
          <div key={item.id} className="relative pl-12">
            {/* Dot */}
            <div className="bg-background border-primary absolute top-1.5 left-0 z-10 flex h-10 w-10 items-center justify-center rounded-full border-2 shadow-sm">
              <History className="text-primary h-4 w-4" />
            </div>

            <div className="bg-card rounded-xl border p-4 shadow-xs transition-shadow hover:shadow-md">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <span className="bg-primary/10 text-primary inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium">
                  {formatField(item.field)}
                </span>
                <div className="text-muted-foreground flex items-center text-xs">
                  <Calendar className="mr-1 h-3 w-3" />
                  {new Date(item.changed_at).toLocaleString(undefined, {
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                </div>
              </div>

              <div className="mb-3 flex items-center gap-3 text-sm">
                <span className="text-muted-foreground font-medium line-through">
                  {formatValue(item.field, item.old_value)}
                </span>
                <ArrowRight className="text-muted-foreground h-4 w-4" />
                <span className="text-foreground font-bold">
                  {formatValue(item.field, item.new_value)}
                </span>
              </div>

              <div className="text-muted-foreground flex items-center border-t pt-3 text-xs">
                <User className="mr-1 h-3 w-3" />
                <span>Changed by {item.changed_by_email}</span>
              </div>

              {item.note && (
                <p className="text-muted-foreground bg-muted/50 mt-2 rounded p-2 text-xs italic">
                  &quot;{item.note}&quot;
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
