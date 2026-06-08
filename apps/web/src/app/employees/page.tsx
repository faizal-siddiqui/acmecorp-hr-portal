"use client";

import { useEffect, useState, useCallback, Suspense } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { getEmployees, Employee, exportEmployees } from "@/lib/api";
import {
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Filter,
  ExternalLink,
  UserPlus,
  Download,
} from "lucide-react";
import Link from "next/link";
import { EmployeeCreateForm } from "@/components/EmployeeCreateForm";
import { AnalyticsKPIs } from "@/components/AnalyticsKPIs";
import { AnalyticsBreakdown } from "@/components/AnalyticsBreakdown";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

const COUNTRIES = ["US", "GB", "DE", "FR", "IN", "CA", "AU", "SG", "BR", "JP"];
const DEPARTMENTS = [
  "Engineering",
  "Sales",
  "Marketing",
  "Finance",
  "HR",
  "Operations",
  "Support",
  "Product",
  "Legal",
  "Design",
];
const LEVELS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"];
const STATUSES = ["active", "inactive"];

const SortIcon = ({
  field,
  sortBy,
  sortOrder,
}: {
  field: string;
  sortBy: string;
  sortOrder: string;
}) => {
  if (sortBy !== field) return <ArrowUpDown className="ml-2 h-4 w-4 opacity-50" />;
  return sortOrder === "asc" ? (
    <ArrowUp className="ml-2 h-4 w-4" />
  ) : (
    <ArrowDown className="ml-2 h-4 w-4" />
  );
};

function EmployeesPageContent() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // State from URL
  const page = parseInt(searchParams.get("page") || "1");
  const q = searchParams.get("q") || "";
  const country = searchParams.get("country") || "";
  const department = searchParams.get("department") || "";
  const level = searchParams.get("level") || "";
  const status = searchParams.get("status") || "";
  const sortBy = searchParams.get("sort_by") || "";
  const sortOrder = searchParams.get("sort_order") || "asc";

  const pageSize = 25;

  const updateFilters = useCallback(
    (updates: Record<string, string | number | null>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(updates).forEach(([key, value]) => {
        if (value === null || value === "") {
          params.delete(key);
        } else {
          params.set(key, value.toString());
        }
      });
      // Reset to page 1 on filter change, unless we are explicitly setting the page
      if (!updates.page) {
        params.set("page", "1");
      }
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, pathname, searchParams],
  );

  useEffect(() => {
    let ignore = false;

    const startFetching = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          page_size: pageSize.toString(),
          ...(q && { q }),
          ...(country && { country }),
          ...(department && { department }),
          ...(level && { level }),
          ...(status && { status }),
          ...(sortBy && { sort_by: sortBy }),
          ...(sortOrder && { sort_order: sortOrder }),
        });

        const data = await getEmployees(params);
        if (!ignore) {
          setEmployees(data.items);
          setTotal(data.total);
        }
      } catch (error) {
        if (!ignore) {
          console.error("Failed to fetch employees:", error);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    startFetching();

    return () => {
      ignore = true;
    };
  }, [page, pageSize, q, country, department, level, status, sortBy, sortOrder]);

  // Debounced search
  const [searchInput, setSearchInput] = useState(q);
  const [prevQ, setPrevQ] = useState(q);

  if (q !== prevQ) {
    setSearchInput(q);
    setPrevQ(q);
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== q) {
        updateFilters({ q: searchInput });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput, q, updateFilters]);

  const handleSort = (field: string) => {
    if (sortBy === field) {
      updateFilters({ sort_order: sortOrder === "asc" ? "desc" : "asc" });
    } else {
      updateFilters({ sort_by: field, sort_order: "asc" });
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      updateFilters({ page: newPage });
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const params = new URLSearchParams({
        ...(q && { q }),
        ...(country && { country }),
        ...(department && { department }),
        ...(level && { level }),
        ...(status && { status }),
        ...(sortBy && { sort_by: sortBy }),
        ...(sortOrder && { sort_order: sortOrder }),
      });

      const response = await exportEmployees(params);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `employees_export_${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Failed to export employees:", error);
      alert("Failed to export employees. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Employee Directory</h1>
          <p className="text-muted-foreground mt-1">
            Manage and view all employees across the organization.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={handleExport} disabled={exporting}>
            <Download className="mr-2 h-4 w-4" />
            {exporting ? "Exporting..." : "Export CSV"}
          </Button>
          <Button onClick={() => setIsAddModalOpen(true)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Add Employee
          </Button>
          <div className="bg-muted rounded-full px-3 py-1 text-sm font-medium">Total: {total}</div>
        </div>
      </div>

      <AnalyticsKPIs />

      <div className="mb-8">
        <AnalyticsBreakdown />
      </div>

      {/* Filters */}
      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-6">
        <div className="relative lg:col-span-2">
          <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search name, email, or code..."
            className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring w-full rounded-md border py-2 pr-4 pl-10 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
        </div>

        <select
          className="border-input bg-background focus-visible:ring-ring w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
          value={country}
          onChange={(e) => updateFilters({ country: e.target.value })}
        >
          <option value="">All Countries</option>
          {COUNTRIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <select
          className="border-input bg-background focus-visible:ring-ring w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
          value={department}
          onChange={(e) => updateFilters({ department: e.target.value })}
        >
          <option value="">All Departments</option>
          {DEPARTMENTS.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>

        <select
          className="border-input bg-background focus-visible:ring-ring w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
          value={level}
          onChange={(e) => updateFilters({ level: e.target.value })}
        >
          <option value="">All Levels</option>
          {LEVELS.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>

        <select
          className="border-input bg-background focus-visible:ring-ring w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
          value={status}
          onChange={(e) => updateFilters({ status: e.target.value })}
        >
          <option value="">All Statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="bg-card rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">Code</TableHead>
              <TableHead
                className="hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => handleSort("name")}
              >
                <div className="flex items-center">
                  Name <SortIcon field="name" sortBy={sortBy} sortOrder={sortOrder} />
                </div>
              </TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Department</TableHead>
              <TableHead>Level</TableHead>
              <TableHead
                className="hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => handleSort("hireDate")}
              >
                <div className="flex items-center">
                  Hire Date <SortIcon field="hireDate" sortBy={sortBy} sortOrder={sortOrder} />
                </div>
              </TableHead>
              <TableHead>Status</TableHead>
              <TableHead
                className="hover:bg-muted/50 cursor-pointer text-right transition-colors"
                onClick={() => handleSort("salary")}
              >
                <div className="flex items-center justify-end">
                  Salary (USD) <SortIcon field="salary" sortBy={sortBy} sortOrder={sortOrder} />
                </div>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Skeleton className="h-4 w-12" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-32" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-40" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-24" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-16" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-20" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-16" />
                  </TableCell>
                  <TableCell className="text-right">
                    <Skeleton className="ml-auto h-4 w-20" />
                  </TableCell>
                </TableRow>
              ))
            ) : employees.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="h-32 text-center">
                  <div className="text-muted-foreground flex flex-col items-center justify-center">
                    <Filter className="mb-2 h-8 w-8 opacity-20" />
                    <p>No employees found matching your filters.</p>
                    <Button variant="link" onClick={() => router.push(pathname)} className="mt-2">
                      Clear all filters
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              employees.map((employee) => (
                <TableRow key={employee.id} className="group">
                  <TableCell className="text-muted-foreground font-mono text-xs">
                    {employee.employee_code}
                  </TableCell>
                  <TableCell className="font-medium">
                    <Link
                      href={`/employees/${employee.id}`}
                      className="hover:text-primary flex items-center transition-colors"
                    >
                      {`${employee.first_name} ${employee.last_name}`}
                      <ExternalLink className="ml-2 h-3 w-3 opacity-0 transition-opacity group-hover:opacity-100" />
                    </Link>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{employee.email}</TableCell>
                  <TableCell>{employee.department_name}</TableCell>
                  <TableCell>
                    <span className="bg-muted rounded px-2 py-0.5 text-xs font-medium">
                      {employee.level}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm">
                    {new Date(employee.hire_date + "T00:00:00").toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <span
                      className={`rounded-full px-2 py-1 text-[10px] font-bold tracking-wider uppercase ${
                        employee.status === "active"
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {employee.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {new Intl.NumberFormat("en-US", {
                      style: "currency",
                      currency: "USD",
                      maximumFractionDigits: 0,
                    }).format(employee.base_usd)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-muted-foreground text-sm">
            Showing {employees.length} of {total} employees
          </div>
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    handlePageChange(page - 1);
                  }}
                  className={page === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>

              {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                let pageNum: number;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (page <= 3) {
                  pageNum = i + 1;
                } else if (page >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = page - 2 + i;
                }

                return (
                  <PaginationItem key={pageNum}>
                    <PaginationLink
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        handlePageChange(pageNum);
                      }}
                      isActive={page === pageNum}
                    >
                      {pageNum}
                    </PaginationLink>
                  </PaginationItem>
                );
              })}

              <PaginationItem>
                <PaginationNext
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    handlePageChange(page + 1);
                  }}
                  className={
                    page === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"
                  }
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}

      {isAddModalOpen && (
        <EmployeeCreateForm
          onClose={() => setIsAddModalOpen(false)}
          onSuccess={() => {
            // Re-fetch or update list
            router.refresh();
          }}
        />
      )}
    </div>
  );
}

export default function EmployeesPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto px-4 py-10 sm:px-6 lg:px-8">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <Skeleton className="mb-2 h-10 w-64" />
              <Skeleton className="h-4 w-96" />
            </div>
            <Skeleton className="h-6 w-24 rounded-full" />
          </div>
          <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-6">
            <Skeleton className="h-10 w-full lg:col-span-2" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
          <div className="bg-card rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">
                    <Skeleton className="h-4 w-12" />
                  </TableHead>
                  <TableHead>
                    <Skeleton className="h-4 w-24" />
                  </TableHead>
                  <TableHead>
                    <Skeleton className="h-4 w-32" />
                  </TableHead>
                  <TableHead>
                    <Skeleton className="h-4 w-24" />
                  </TableHead>
                  <TableHead>
                    <Skeleton className="h-4 w-16" />
                  </TableHead>
                  <TableHead>
                    <Skeleton className="h-4 w-20" />
                  </TableHead>
                  <TableHead>
                    <Skeleton className="h-4 w-16" />
                  </TableHead>
                  <TableHead className="text-right">
                    <Skeleton className="ml-auto h-4 w-20" />
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Skeleton className="h-4 w-12" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-32" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-40" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-24" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-16" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-20" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-16" />
                    </TableCell>
                    <TableCell className="text-right">
                      <Skeleton className="ml-auto h-4 w-20" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      }
    >
      <EmployeesPageContent />
    </Suspense>
  );
}
