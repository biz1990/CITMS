import pytest
from app.tasks.maintenance import _password_rotation, _data_cleanup
from app.tasks.license import _audit_licenses
from app.tasks.itsm import _itsm_sla_check

@pytest.mark.asyncio
async def test_celery_password_rotation_runner():
    # Calling the underlyng async function directly (bypass celery decorator)
    # The runner initializes its own AsyncSessionLocal inside, so we just execution assertion
    # that it doesn't crash on an empty system.
    try:
        await _password_rotation()
        passed = True
    except Exception:
        passed = False
    assert passed

@pytest.mark.asyncio
async def test_celery_data_cleanup_runner():
    try:
        await _data_cleanup()
        passed = True
    except Exception:
        passed = False
    assert passed
    
@pytest.mark.asyncio
async def test_celery_audit_licenses_runner():
    try:
        await _audit_licenses()
        passed = True
    except Exception:
        passed = False
    assert passed

@pytest.mark.asyncio
async def test_celery_itsm_sla_runner():
    try:
        await _itsm_sla_check()
        passed = True
    except Exception:
        passed = False
    assert passed
