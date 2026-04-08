import asyncio
import logging
from sqlalchemy import select, func, update
from backend.src.infrastructure.database import SessionLocal
from backend.src.contexts.license.models import SoftwareLicense
from backend.src.contexts.inventory.models import SoftwareInstallation

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def fix_license_consistency():
    """
    Script to synchronize used_seats with actual active installations.
    """
    logger.info("Starting License Consistency Check...")
    
    async with SessionLocal() as db:
        try:
            # 1. Get all licenses
            result = await db.execute(select(SoftwareLicense))
            licenses = result.scalars().all()
            
            mismatches_found = 0
            fixed_count = 0
            
            for lic in licenses:
                # 2. Count actual active installations for this license
                count_query = select(func.count(SoftwareInstallation.id)).where(
                    SoftwareInstallation.license_id == lic.id,
                    SoftwareInstallation.deleted_at == None
                )
                actual_count_res = await db.execute(count_query)
                actual_count = actual_count_res.scalar()
                
                if lic.used_seats != actual_count:
                    mismatches_found += 1
                    logger.warning(
                        f"Mismatch found for License ID {lic.id}: "
                        f"Current used_seats={lic.used_seats}, Actual active installations={actual_count}"
                    )
                    
                    # 3. Fix the mismatch
                    lic.used_seats = actual_count
                    fixed_count += 1
            
            if fixed_count > 0:
                await db.commit()
                logger.info(f"Successfully fixed {fixed_count} license seat counts.")
            else:
                logger.info("No mismatches found. Database is consistent.")
                
        except Exception as e:
            logger.error(f"Error during consistency check: {str(e)}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(fix_license_consistency())
