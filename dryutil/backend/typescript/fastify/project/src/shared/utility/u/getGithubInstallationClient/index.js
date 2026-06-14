//import { App } from "@octokit/app";
//import { Octokit } from "@octokit/rest";
async function index(_p) {
    const { App } = await import("@octokit/app"); // dynamic ESM import inside CJS project
    const { Octokit } = await import("@octokit/rest"); // dynamic ESM import inside CJS project
    const privateKey = Buffer.from(_p.privateKey, "base64").toString("utf8");
    // Build once and reuse across routes
    const app = new App({
        appId: _p.appId, //process.env.GITHUB_APP_ID!,
        privateKey: privateKey, //process.env.GITHUB_PRIVATE_KEY!,
        Octokit, // gives us the `.rest` API
    });
    const id = _p.installationId; //?? Number(process.env.GITHUB_INSTALLATION_ID!);
    // Returns an authenticated Octokit client (installation-scoped)
    return app.getInstallationOctokit(id);
}
export { index as getGithubInstallationClient };
/*
==USAGE==



*/
