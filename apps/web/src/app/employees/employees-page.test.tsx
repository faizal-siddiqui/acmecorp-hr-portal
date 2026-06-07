import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import EmployeesPage from './page';
import { getEmployees, getAnalyticsSummary, getAnalyticsBreakdown } from '@/lib/api';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('@/lib/api', () => ({
  getEmployees: vi.fn(),
  getAnalyticsSummary: vi.fn(),
  getAnalyticsBreakdown: vi.fn(),
  exportEmployees: vi.fn(),
}));

// Mock components that are tested elsewhere or too complex for this unit test
vi.mock('@/components/AnalyticsKPIs', () => ({
  AnalyticsKPIs: () => <div data-testid="analytics-kpis">Analytics KPIs</div>,
}));

vi.mock('@/components/AnalyticsBreakdown', () => ({
  AnalyticsBreakdown: () => <div data-testid="analytics-breakdown">Analytics Breakdown</div>,
}));

vi.mock('@/components/EmployeeCreateForm', () => ({
  EmployeeCreateForm: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="employee-create-form">
      <button onClick={onClose}>Close</button>
    </div>
  ),
}));

describe('EmployeesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (getEmployees as any).mockResolvedValue({
      items: [
        {
          id: 1,
          employee_code: 'E1',
          first_name: 'Alice',
          last_name: 'Zebra',
          email: 'alice@example.com',
          country: 'US',
          level: 'L3',
          status: 'active',
          hire_date: '2020-01-01',
          department_name: 'Engineering',
          base_annual: 100000,
          currency: 'USD',
          base_usd: 100000,
        },
      ],
      total: 1,
    });
    (getAnalyticsSummary as any).mockResolvedValue({});
    (getAnalyticsBreakdown as any).mockResolvedValue([]);
  });

  it('renders the employee directory with data', async () => {
    render(<EmployeesPage />);

    await waitFor(() => {
      expect(screen.getByText('Employee Directory')).toBeInTheDocument();
      expect(screen.getByText('Alice Zebra')).toBeInTheDocument();
      expect(screen.getByText('E1')).toBeInTheDocument();
      // Use getAllByText and check that at least one is in the table
      const engineeringElements = screen.getAllByText('Engineering');
      expect(engineeringElements.length).toBeGreaterThan(0);
    });
  });

  it('filters employees when search input changes', async () => {
    const { useRouter } = await import('next/navigation');
    const router = useRouter();
    
    render(<EmployeesPage />);

    const searchInput = screen.getByPlaceholderText(/Search name, email, or code/);
    fireEvent.change(searchInput, { target: { value: 'Bob' } });

    // Wait for debounce (500ms) + some buffer
    await waitFor(() => {
      expect(router.push).toHaveBeenCalledWith(expect.stringContaining('q=Bob'));
    }, { timeout: 3000 });
  });

  it('opens the add employee modal', async () => {
    render(<EmployeesPage />);

    const addButton = screen.getByText('Add Employee');
    fireEvent.click(addButton);

    expect(screen.getByTestId('employee-create-form')).toBeInTheDocument();
  });
});
