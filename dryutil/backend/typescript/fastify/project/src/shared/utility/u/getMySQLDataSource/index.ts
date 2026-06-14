import { DataSource } from 'typeorm';

type MySQLConfig = {
  host: string;
  port: string | number;
  username: string;
  password: string;
  database: string;
};

type CachedMySQL = {
  dataSource: DataSource;
  lastUsed: number;
};

const connectionCache = new Map<string, CachedMySQL>();

// Configurable TTL in milliseconds (e.g., 5 minutes)
const TTL = 5 * 60 * 1000;

// GC Interval (e.g., every 1 minute)
const GC_INTERVAL = 60 * 1000;

// Generate unique key from config
function getCacheKey(config: MySQLConfig): string {
  return `${config.host}:${config.port}:${config.username}:${config.database}`;
}

// Reuse or create a connection
export async function getMySQLDataSource(config: MySQLConfig): Promise<DataSource> {
  const key = getCacheKey(config);
  const now = Date.now();

  const cached = connectionCache.get(key);
  if (cached && cached.dataSource.isInitialized) {
    cached.lastUsed = now;
    return cached.dataSource;
  }

  const dataSource = new DataSource({
    type: 'mysql',
    host: config.host,
    port: parseInt(config.port as string, 10),
    username: config.username,
    password: config.password,
    database: config.database,
    synchronize: false,
    logging: false,
    entities: [], // optionally plug in
  });

  await dataSource.initialize();

  connectionCache.set(key, {
    dataSource,
    lastUsed: now,
  });

  return dataSource;
}

// GC to clean up idle connections
function startConnectionGarbageCollector() {
  setInterval(async () => {
    const now = Date.now();

    for (const [key, { dataSource, lastUsed }] of connectionCache.entries()) {
      const idleTime = now - lastUsed;

      if (idleTime > TTL) {
        try {
          await dataSource.destroy();
          connectionCache.delete(key);
          console.log(`[MySQL GC] Closed idle connection: ${key}`);
        } catch (err) {
          console.warn(`[MySQL GC] Failed to destroy DataSource for ${key}`, err);
        }
      }
    }
  }, GC_INTERVAL);
}

// Start it immediately
startConnectionGarbageCollector();



/*
♻️ Reuses MySQL connections
🧹 Auto-cleans unused connections after TTL
📈 Scalable: handles many dynamic configs

==USAGE==
const ds = await getMySQLDataSource(mysqlConfig);
const results = await ds.query('SELECT * FROM your_table');

*/