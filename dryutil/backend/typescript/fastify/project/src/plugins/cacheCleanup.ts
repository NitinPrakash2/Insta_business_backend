// plugins/cacheCleanup.ts (with warnThreshold)
import fp from "fastify-plugin";
import fs from "fs";
import path from "path";

interface CleanupOptions {
  cacheDirs: string[];
  maxBytes?: number;
  ttl?: number;
  cleanupInterval?: number;
  sharedQuota?: boolean;
  warnThreshold?: number; // e.g., 0.8 = 80%
}


//set..
/*const cacheDir = "/var/cache/images";
// Make sure the directory exists
if (!fs.existsSync(cacheDir)) {
  fs.mkdirSync(cacheDir, { recursive: true });
}*/
const cacheDir = path.join(process.cwd(), "c_a_c_h_e/images");
console.log(`cacheDir: ${cacheDir}`);
if (!fs.existsSync(cacheDir)) {
  fs.mkdirSync(cacheDir, { recursive: true });
}
 


//set..
export default fp(async (fastify, /*opts: CleanupOptions*/) => {
  const opts:CleanupOptions = {
      cacheDirs: [
        /*"/home/ubuntu/app/cache/images",
        "/home/ubuntu/app/cache/thumbs"*/
        cacheDir,
      ],
      maxBytes: 10 * 1024 * 1024 * 1024, // 10GB
      ttl: 7 * 24 * 60 * 60 * 1000,      // 7 days
      cleanupInterval: 3600_000,         // 1h
      sharedQuota: true,
      warnThreshold: 0.8                 // warn at 80% usage
  };


  //set..
  const cacheDirs = opts.cacheDirs || [];
  const maxBytes = opts.maxBytes || 8 * 1024 * 1024 * 1024;
  const ttl = opts.ttl || 7 * 24 * 60 * 60 * 1000;
  const cleanupInterval = opts.cleanupInterval || 3600_000;
  const sharedQuota = opts.sharedQuota || false;
  const warnThreshold = opts.warnThreshold ?? 0.8;

  for (const dir of cacheDirs) {
    fs.mkdirSync(dir, { recursive: true });
  }

  function collectFiles() {
    const all: { p: string; atime: number; size: number; dir: string }[] = [];
    for (const dir of cacheDirs) {
      try {
        const files = fs.readdirSync(dir).map(f => {
          const p = path.join(dir, f);
          const st = fs.statSync(p);
          return { p, atime: st.atimeMs, size: st.size, dir };
        });
        all.push(...files);
      } catch (err) {
        fastify.log.error(err, `cannot read ${dir}`);
      }
    }
    return all;
  }

  function cleanup() {
    try {
      let files = collectFiles();
      let total = files.reduce((s, f) => s + f.size, 0);
      const now = Date.now();

      // TTL cleanup
      for (const f of files) {
        if (now - f.atime > ttl) {
          fs.unlinkSync(f.p);
          total -= f.size;
        }
      }
      files = collectFiles();

      if (sharedQuota) {
        if (total > maxBytes) {
          files.sort((a, b) => a.atime - b.atime);
          for (const f of files) {
            if (total <= maxBytes) break;
            fs.unlinkSync(f.p);
            total -= f.size;
          }
        }
        const usageRatio = total / maxBytes;
        if (usageRatio >= warnThreshold) {
          fastify.log.warn(`[cache-cleanup] Shared quota high: ${(usageRatio*100).toFixed(1)}% used`);
        }
        fastify.log.info(`[cache-cleanup] total usage=${(total/1024/1024).toFixed(1)}MB (shared)`);
      } else {
        for (const dir of cacheDirs) {
          let dirFiles = files.filter(f => f.dir === dir);
          let dirTotal = dirFiles.reduce((s, f) => s + f.size, 0);
          if (dirTotal > maxBytes) {
            dirFiles.sort((a, b) => a.atime - b.atime);
            for (const f of dirFiles) {
              if (dirTotal <= maxBytes) break;
              fs.unlinkSync(f.p);
              dirTotal -= f.size;
            }
          }
          const usageRatio = dirTotal / maxBytes;
          if (usageRatio >= warnThreshold) {
            fastify.log.warn(`[cache-cleanup] ${dir} quota high: ${(usageRatio*100).toFixed(1)}% used`);
          }
          fastify.log.info(`[cache-cleanup] ${dir}: usage=${(dirTotal/1024/1024).toFixed(1)}MB`);
        }
      }
    } catch (err) {
      fastify.log.error(err, "cache cleanup failed");
    }
  }

  setInterval(cleanup, cleanupInterval).unref();
  fastify.addHook("onClose", async () => clearInterval as any);
});
