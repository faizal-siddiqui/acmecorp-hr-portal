const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }

  return response;
}

export interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  country: string;
  level: string;
  status: string;
  hire_date: string;
  department_name: string;
  base_annual: number;
  currency: string;
  base_usd: number;
}

export interface EmployeeDetail extends Employee {
  bonus_annual: number;
  monthly_base: number;
  total_comp: number;
  total_comp_usd: number;
}

export async function getEmployees(params: URLSearchParams) {
  const response = await apiFetch(`/employees/?${params.toString()}`);
  if (!response.ok) throw new Error("Failed to fetch employees");
  return response.json();
}

export async function getEmployee(id: string): Promise<EmployeeDetail> {
  const response = await apiFetch(`/employees/${id}`);
  if (!response.ok) {
    if (response.status === 404) throw new Error("Employee not found");
    throw new Error("Failed to fetch employee");
  }
  return response.json();
}

export interface CompensationUpdate {
  base_annual: number;
  bonus_annual: number;
  currency: string;
  effective_date: string;
}

export async function updateCompensation(id: number, data: CompensationUpdate) {
  const response = await apiFetch(`/employees/${id}/compensation`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to update compensation");
  }
  return response.json();
}

export interface SalaryHistoryItem {
  id: number;
  employee_id: number;
  field: string;
  old_value: string | null;
  new_value: string;
  changed_by_email: string;
  changed_at: string;
  note: string | null;
}

export async function getEmployeeHistory(id: string): Promise<SalaryHistoryItem[]> {
  const response = await apiFetch(`/employees/${id}/history`);
  if (!response.ok) throw new Error("Failed to fetch employee history");
  return response.json();
}

export interface EmployeeCreate {
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  country: string;
  level: string;
  hire_date: string;
  department_id: number;
  base_annual: number;
  bonus_annual: number;
  currency: string;
}

export async function createEmployee(data: EmployeeCreate): Promise<EmployeeDetail> {
  const response = await apiFetch("/employees/", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to create employee");
  }
  return response.json();
}

export async function updateEmployeeStatus(id: number, status: "active" | "inactive") {
  const response = await apiFetch(`/employees/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to update employee status");
  }
  return response.json();
}

export interface Department {
  id: number;
  name: string;
}

export async function getDepartments(): Promise<Department[]> {
  const response = await apiFetch("/employees/meta/departments");
  if (!response.ok) throw new Error("Failed to fetch departments");
  return response.json();
}
