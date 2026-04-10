import { openDB, IDBPDatabase } from 'idb';

const DB_NAME = 'citms_offline_db';
const STORE_NAME = 'offline_inventory';

export interface OfflineDevice {
  id: string;
  hostname: string;
  serial_number: string;
  status: string;
  last_seen: string;
  sync_status: 'pending' | 'synced' | 'conflict';
  local_changes?: any;
}

export async function initDB(): Promise<IDBPDatabase> {
  return openDB(DB_NAME, 1, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    },
  });
}

export async function saveOfflineDevices(devices: any[]) {
  const db = await initDB();
  const tx = db.transaction(STORE_NAME, 'readwrite');
  const store = tx.objectStore(STORE_NAME);
  for (const device of devices) {
    await store.put(device);
  }
  await tx.done;
}

export async function getOfflineDevices() {
  const db = await initDB();
  return db.getAll(STORE_NAME);
}

export async function clearOfflineDevices() {
  const db = await initDB();
  const tx = db.transaction(STORE_NAME, 'readwrite');
  await tx.objectStore(STORE_NAME).clear();
  await tx.done;
}
