export function validateMySQLViewQueryForUpsert(query) {
    const normalized = query.trim().toLowerCase();
    // Block clearly dangerous operations
    const forbiddenPatterns = [
        /\bdrop\b/,
        /\bdelete\b/,
        /\btruncate\b/,
        /\binsert\b/,
        /\bupdate\b/,
        /\balter\b/,
        /\bcreate\s+database\b/,
        /\bcreate\s+table\b/,
        /\bshutdown\b/,
        /\bexec\b/,
        /\bgrant\b/,
        /\brevoke\b/,
    ];
    for (const pattern of forbiddenPatterns) {
        if (pattern.test(normalized)) {
            return {
                valid: false,
                reason: `Query contains forbidden keyword matching pattern: ${pattern}`,
            };
        }
    }
    // Only allow `CREATE OR REPLACE VIEW ... AS SELECT ...`
    const validCreateViewPattern = /^create\s+or\s+replace\s+view\s+\S+\s+as\s+select\s+/;
    if (!validCreateViewPattern.test(normalized)) {
        return {
            valid: false,
            reason: "Query must begin with `CREATE OR REPLACE VIEW view_name AS SELECT ...`",
        };
    }
    return { valid: true };
}
/*
==USAGE==
const q1 = `CREATE OR REPLACE VIEW my_view AS SELECT id FROM users`;
console.log(validateMySQLViewQuery(q1)); // ✅ valid

const q2 = `CREATE VIEW my_view AS SELECT id FROM users`;
console.log(validateMySQLViewQuery(q2)); // ❌ not allowed

const q3 = `CREATE OR REPLACE VIEW my_view AS DELETE FROM users`;
console.log(validateMySQLViewQuery(q3)); // ❌ dangerous


*/ 
