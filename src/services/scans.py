from src.core.scan import scan
from src.db import get_session
from src.models import Scan


def run_scan(ip_target: str, port_target: int, user_id: int):
    """
    Runs a scan on the target and store the result in the database
    """
    result = scan(ip_target, port_target)
    with get_session() as db:
        scan_instance = Scan(
            user_id=user_id, ip_target=ip_target, port_target=port_target, result=result
        )
        db.add(scan_instance)
        db.commit()
        return scan_instance
