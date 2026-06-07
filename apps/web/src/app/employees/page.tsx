"use client";

import { useEffect, useState, useCallback } from "react";
import { apiFetch } from "@/lib/api";
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

interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  country: string;
  level: string;
  status: string;
  department_name: string;
  base_annual: number;
  currency: string;
  base_usd: number;
}

interface PaginatedResponse {
  items: Employee[];
  total: number;
  page: number;
  page_size: number;
}

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const pageSize = 25;

  const fetchEmployees = useCallback(async (currentPage: number) => {
    setLoading(true);
    try {
      const response = await apiFetch(`/employees/?page=${currentPage}&page_size=${pageSize}`);
      if (response.ok) {
        const data: PaginatedResponse = await response.json();
        setEmployees(data.items);
        setTotal(data.total);
      }
    } catch (error) {
      console.error("Failed to fetch employees:", error);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  useEffect(() => {
    fetchEmployees(page);
  }, [page, fetchEmployees]);

  const totalPages = Math.ceil(total / pageSize);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Employee Directory</h1>
        <div className="text-sm text-muted-foreground">
          Total Employees: {total}
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Department</TableHead>
              <TableHead>Level</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Base (USD)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-40" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-4 w-20 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : employees.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  No employees found.
                </TableCell>
              </TableRow>
            ) : (
              employees.map((employee) => (
                <TableRow key={employee.id}>
                  <TableCell className="font-medium">{employee.employee_code}</TableCell>
                  <TableCell>{`${employee.first_name} ${employee.last_name}`}</TableCell>
                  <TableCell>{employee.email}</TableCell>
                  <TableCell>{employee.department_name}</TableCell>
                  <TableCell>{employee.level}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      employee.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {employee.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'USD',
                    }).format(employee.base_usd)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="mt-6">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious 
                  href="#" 
                  onClick={(e) => { e.preventDefault(); handlePageChange(page - 1); }}
                  className={page === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>
              
              {/* Simple pagination - show current and neighbors */}
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
                      onClick={(e) => { e.preventDefault(); handlePageChange(pageNum); }}
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
                  onClick={(e) => { e.preventDefault(); handlePageChange(page + 1); }}
                  className={page === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
}
