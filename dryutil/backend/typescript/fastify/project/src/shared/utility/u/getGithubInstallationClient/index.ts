import { App } from "@octokit/app";
import { Octokit } from "@octokit/rest";

async function index(_p: { 
  installationId?: any, //Where to Find Installation ID ? [Check-on-your-github="https://github.com/settings/installations/<INSTALLATION_ID>"]
  appId?: any,
  /**
   * Must be in base64
   */
  privateKey?: any,
}) {
  const privateKey = Buffer.from(_p.privateKey, "base64").toString("utf8");
  // Build once and reuse across routes
  const app = new App({
    appId:  _p.appId,//process.env.GITHUB_APP_ID!,
    privateKey: privateKey,//process.env.GITHUB_PRIVATE_KEY!,
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
