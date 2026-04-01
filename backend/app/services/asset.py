import uuid
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.device import Device, CMDBRelationship

class AssetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def transfer_device_location(self, device_id: uuid.UUID, new_location_id: uuid.UUID):
        stmt = select(Device).where(Device.id == device_id)
        dev = (await self.db.execute(stmt)).scalars().first()
        if dev:
            dev.location_id = new_location_id
            dev.version += 1
            await self.db.commit()
            return True
        return False
        
    async def build_topology_graph(self, root_device_id: uuid.UUID) -> Dict:
        """
        Module 3: Topology Mapping - BFS traversal 
        """
        nodes = {}
        edges = []
        visited = set()
        queue = [root_device_id]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Fetch node
            stmt_dev = select(Device).where(Device.id == current_id)
            dev = (await self.db.execute(stmt_dev)).scalars().first()
            if dev:
                nodes[str(current_id)] = {
                    "id": str(dev.id),
                    "type": "customNode",
                    "data": {"label": dev.name or dev.asset_tag or "Unknown", "status": dev.status, "type": dev.device_subtype}
                }
            
            # Fetch relations
            stmt_rel = select(CMDBRelationship).where(
                (CMDBRelationship.source_id == current_id) | 
                (CMDBRelationship.target_id == current_id)
            )
            rels = (await self.db.execute(stmt_rel)).scalars().all()
            for r in rels:
                edges.append({
                    "id": str(r.id),
                    "source": str(r.source_id),
                    "target": str(r.target_id),
                    "label": r.relationship_type
                })
                # Add to queue
                next_node = r.target_id if r.source_id == current_id else r.source_id
                if next_node not in visited:
                    queue.append(next_node)
        
        return {"nodes": list(nodes.values()), "edges": edges}
