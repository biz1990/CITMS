import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.src.contexts.license.services.license import LicenseService
from backend.src.contexts.license.models import SoftwareLicense
from backend.src.contexts.inventory.models import SoftwareInstallation

# Simulation of concurrent license assignment
async def simulate_concurrent_assignment(engine, catalog_id, num_concurrent=5):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def assign_task(task_id):
        async with async_session() as session:
            service = LicenseService(session)
            # Create a dummy installation for each task
            installation_id = uuid.uuid4()
            # In a real test, we would insert this into the DB first
            print(f"Task {task_id}: Attempting to assign license for catalog {catalog_id}")
            try:
                await service.auto_assign_license(catalog_id, installation_id)
                print(f"Task {task_id}: SUCCESS")
            except Exception as e:
                print(f"Task {task_id}: FAILED - {str(e)}")

    # Run tasks concurrently
    tasks = [assign_task(i) for i in range(num_concurrent)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # This is a conceptual test case. 
    # To run it, you would need a running DB and initialized models.
    print("Conceptual Concurrency Test for License Assignment")
    print("1. Transaction A starts, calls get_available_license() with FOR UPDATE.")
    print("2. Transaction B starts, calls get_available_license() with FOR UPDATE, waits for A.")
    print("3. Transaction A increments used_seats and commits.")
    print("4. Transaction B's lock is released, it re-evaluates the query.")
    print("5. If seats are still available, B proceeds; otherwise, it finds another row or fails.")
