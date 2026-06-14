import "reflect-metadata";

import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import * as dotenv from "dotenv";
import Fastify from "fastify";
import path from "path";
import { TypeBoxTypeProvider } from "@fastify/type-provider-typebox";
import AutoLoad from "@fastify/autoload";
import { configureDatabase } from "./db.config.js";
//import { configureRoutes } from "./routes/movie";
import cors from '@fastify/cors';
//import { Server } from "socket.io";
import multipart from "@fastify/multipart";


//set..
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

 
dotenv.config();

 

//set..
interface ServerToClientEvents {
  /*noArg: () => void;
  basicEmit: (a: number, b: string, c: Buffer) => void;
  withAck: (d: string, callback: (e: number) => void) => void;*/
  //get_link: (d: JSON, callback: (e: number) => void) => void;
  get_link: (d: JSON) => void;
}
interface ClientToServerEvents {
  /*hello: (payload:string) => void;*/
  get_link: (payload:{task_link_id:string}) => void;
}
interface InterServerEvents {
  ping: () => void;
}
/*interface SocketData {
  name: string;
  age: number;
}*/
/*declare module 'fastify' {
  interface FastifyInstance {
    io: Server<
    ClientToServerEvents,
    ServerToClientEvents,
    InterServerEvents
    //SocketData
    >
  }
}*/


//set..
async function startServer() {
  const server = Fastify({
    pluginTimeout:-1 //NOTE: We are setting it, Because in case we have `much-data` in `DB`..So now, it will protect us from `AVV_ERR_PLUGIN_EXEC_TIMEOUT` error.
  }).withTypeProvider<TypeBoxTypeProvider>();


  

  //set..
  await configureDatabase(server);


  //set..//https://www.npmjs.com/package/@fastify/cors
  await server.register(cors, {
    // put your options here
    origin:`*`,
    //set..
    //exposedHeaders: ['Content-Disposition'] // Important for downloads!

  });
  //form-request..
  await server.register(multipart, {
    //addToBody: false, // we will handle parts manually
    //attachFieldsToBody: false,
    /*attachFieldsToBody: false, // keep streaming API
    limits: {
      fileSize: 50 * 1024 * 1024, // 50MB
    }*/
  });
  










  //----GLOBAL----// [START]
  /*seed-real..
  NOTE: This can be `take-long` to complete, In case we have `much-data` in `DB`..
  So, Fastify-Server throw a ERROR called `AVV_ERR_PLUGIN_EXEC_TIMEOUT`.
  Also, we are using `async` pattern..So there is no thing like `done()` [ref] https://stackoverflow.com/questions/75823473/fastify-avvioerror-error-plugin-did-not-start-in-time
  */
  await server.register(AutoLoad, {
    dir:  path.join(__dirname, "database/seed/real"),
    options: Object.assign({}),
    scriptPattern: /(?<!\.d)\.(ts|tsx|js)$/  //  /(?<!\.d)\.(ts|tsx)$/
  });
  //set..
  await server.register(AutoLoad, {
    options: Object.assign({}),
    dir: path.join(__dirname, "plugins"),
    //options: Object.assign({}),
    //https://github.com/fastify/fastify-autoload
    scriptPattern: /(?<!\.d)\.(ts|tsx|js)$/  //   /(?<!\.d)\.(ts|tsx)$/
  });
  //----GLOBAL----// [END]

  







 
  
  //----party_1----//  [START]
  await server.register(AutoLoad, {
    options: {
      prefix: `/admin`,
    },
    dir:  path.join(__dirname, "parties/party_1/routes"),
    //options: Object.assign({}),
    scriptPattern:  /(?<!\.d)\.(ts|tsx|js)$/  //  /(?<!\.d)\.(ts|tsx)$/
  });//configureRoutes(server);
  /*await server.register(AutoLoad, {
    options: {
      prefix: `/admin`,
    },
    dir: path.join(__dirname, "parties/party_1/plugins"),
    //options: Object.assign({}),
    //https://github.com/fastify/fastify-autoload
    scriptPattern:  /(?<!\.d)\.(ts|tsx|js)$/  //  /(?<!\.d)\.(ts|tsx)$/,
    //ignorePattern: /(?:)/, // matches nothing, but avoids ENOENT
  });*/ //server.register(require('./plugins/auth'));
  //----party_1----//  [END]

  







  //----party_2----//  [START]
  await server.register(AutoLoad, {
    options: {
      prefix: `/client`,
    },
    dir:  path.join(__dirname, "parties/party_2/routes"),
    //options: Object.assign({}),
    scriptPattern:  /(?<!\.d)\.(ts|tsx|js)$/  //  /(?<!\.d)\.(ts|tsx)$/
  });//configureRoutes(server);
  /*await server.register(AutoLoad, {
    options: {
      prefix: `/client`,
    },
    dir: path.join(__dirname, "parties/party_2/plugins"),
    //options: Object.assign({}),
    //https://github.com/fastify/fastify-autoload
    scriptPattern:  /(?<!\.d)\.(ts|tsx|js)$/  //  /(?<!\.d)\.(ts|tsx)$/,
    //ignorePattern: /(?:)/, // matches nothing, but avoids ENOENT
  });*/ //server.register(require('./plugins/auth'));
  //----party_2----//  [END]

















  //set..
  await server.listen({ port: parseInt(`${process.env.PORT}`) });
}
startServer()
  .then(() => {
    console.log(`Server started successfully at: ${process.env.PORT}`);
  })
  .catch((err) => {
    console.error("Error starting server:", err);
    process.exit(1);
  });
