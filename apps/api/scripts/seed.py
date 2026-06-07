import asyncio
import random
from datetime import date
from typing import List, Dict, Optional

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, engine
from app.models import Employee, Department, Compensation, User, FxRate
from scripts.generators import DataGenerator, COUNTRIES, DEPARTMENTS, LEVELS


async def clear_database(session: AsyncSession):
    """Clears existing data from tables."""
    print("Clearing existing data...")
    # Order matters for FK constraints
    await session.execute(delete(Compensation))
    await session.execute(delete(Employee))
    await session.execute(delete(Department))
    await session.commit()


async def seed_departments(session: AsyncSession) -> Dict[str, int]:
    """Seeds departments and returns a mapping of name to ID."""
    print("Seeding departments...")
    dept_map = {}
    for dept_name in DEPARTMENTS:
        stmt = select(Department).where(Department.name == dept_name)
        result = await session.execute(stmt)
        dept = result.scalar_one_or_none()
        if not dept:
            dept = Department(name=dept_name)
            session.add(dept)
            await session.flush()
        dept_map[dept_name] = dept.id
    return dept_map


async def seed_employees(session: AsyncSession, dept_map: Dict[str, int], num_employees: int = 10000):
    """Seeds employees with hierarchy and compensation."""
    print(f"Generating {num_employees} employees...")
    gen = DataGenerator(seed=42)
    
    # 1. Generate all employee data in memory first to build hierarchy
    all_emps_data = []
    by_dept_level = {d: {l: [] for l in LEVELS} for d in DEPARTMENTS}
    
    for _ in range(num_employees):
        level = gen.random_level()
        dept_name = gen.random_department()
        country = gen.random_country()
        
        emp_info = gen.generate_employee_basic(level, country)
        emp_info["department_name"] = dept_name
        emp_info["department_id"] = dept_map[dept_name]
        emp_info["hire_date"] = gen.random_hire_date()
        
        # Salary and bonus
        salary = gen.get_salary_for_level(level, country["code"])
        bonus = gen.get_bonus_for_level(level, salary)
        emp_info["base_salary"] = salary
        emp_info["bonus"] = bonus
        emp_info["currency"] = country["currency"]
        
        all_emps_data.append(emp_info)
        by_dept_level[dept_name][level].append(emp_info)

    # 2. Assign managers in memory (using indices/references)
    print("Assigning managers...")
    for emp in all_emps_data:
        level_idx = LEVELS.index(emp["level"])
        if level_idx < len(LEVELS) - 1: # Not L7
            higher_levels = LEVELS[level_idx + 1:]
            potential_managers = []
            for h_level in higher_levels:
                potential_managers.extend(by_dept_level[emp["department_name"]][h_level])
            
            if not potential_managers:
                # Fallback to any higher level in any dept
                for d in DEPARTMENTS:
                    for h_level in higher_levels:
                        potential_managers.extend(by_dept_level[d][h_level])
            
            if potential_managers:
                emp["manager_ref"] = random.choice(potential_managers)
            else:
                emp["manager_ref"] = None
        else:
            emp["manager_ref"] = None

    # 3. Insert employees level by level to satisfy manager_id FK
    print("Inserting employees...")
    for level in reversed(LEVELS): # L7 down to L1
        level_emps = [e for e in all_emps_data if e["level"] == level]
        if not level_emps:
            continue
            
        # Prepare batch insert for employees
        emp_mappings = []
        for emp_data in level_emps:
            manager_id = None
            if emp_data.get("manager_ref") and "db_id" in emp_data["manager_ref"]:
                manager_id = emp_data["manager_ref"]["db_id"]
            
            emp_mappings.append({
                "employee_code": emp_data["employee_code"],
                "first_name": emp_data["first_name"],
                "last_name": emp_data["last_name"],
                "email": emp_data["email"],
                "country": emp_data["country"],
                "level": emp_data["level"],
                "status": emp_data["status"],
                "department_id": emp_data["department_id"],
                "manager_id": manager_id
            })
        
        # Execute batch insert and get IDs
        result = await session.execute(
            insert(Employee).returning(Employee.id),
            emp_mappings
        )
        inserted_ids = result.scalars().all()
        
        # Assign DB IDs back to our memory objects and create compensations
        comp_mappings = []
        for emp_data, db_id in zip(level_emps, inserted_ids):
            emp_data["db_id"] = db_id
            comp_mappings.append({
                "employee_id": db_id,
                "base_annual": emp_data["base_salary"],
                "bonus_annual": emp_data["bonus"],
                "currency": emp_data["currency"],
                "effective_date": emp_data["hire_date"],
                "is_current": True
            })
            
        # Batch insert compensations for this level
        await session.execute(insert(Compensation), comp_mappings)
        
        print(f"  Inserted {len(level_emps)} employees at level {level}")
        await session.commit()


async def main():
    async with engine.begin() as conn:
        # Optional: ensure tables exist if not using migrations
        # await conn.run_sync(Base.metadata.create_all)
        pass

    async with AsyncSessionLocal() as session:
        await clear_database(session)
        dept_map = await seed_departments(session)
        await seed_employees(session, dept_map, num_employees=10000)
        await session.commit()
    
    print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
