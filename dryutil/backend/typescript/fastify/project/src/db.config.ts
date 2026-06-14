import plugin from "typeorm-fastify-plugin";
import { FastifyInstance } from "fastify";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";


import { User } from "./database/entity/user.js";
import { Project } from "./database/entity/project.js";
import { Config } from "./database/entity/config.js";
import { Utility } from "./database/entity/utility.js";
import { Instance } from "./database/entity/instance.js";

/*
import { Link } from "./database/entity/link";
import { link_type } from "./database/entity/link_type";
import { creator_type } from "./database/entity/creator_type";
import { credential } from "./database/entity/credential";
import { credential_type } from "./database/entity/credential_type";
import { Import } from "./database/entity/import";
import { import_type } from "./database/entity/import_type";
import { task_link } from "./database/entity/task_link";
import { link_data } from "./database/entity/link_data";
import { Export } from "./database/entity/export";
import { export_type } from "./database/entity/export_type";
import { link_data_status } from "./database/entity/link_data_status";
import { link_level } from "./database/entity/link_level";*/


//set..
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


export async function configureDatabase(server: FastifyInstance) {
  //console.log(process.env.DB_USERNAME);
  await server.register(plugin, {
    namespace: "typeorm",
    type: "postgres", //mysql
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT || "5432"), //3306
    username: process.env.DB_USERNAME,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_DATABASE,
    synchronize: process.env.NODE_ENV === "dev" ? true : false,
    logging: process.env.NODE_ENV === "dev" ? true : false,
    migrations: [join(__dirname + "migration/*.js")],
    subscribers: [],
    migrationsRun: process.env.NODE_ENV === "dev" ? false : false,
    entities: [User, Project, Config, Utility, Instance /*Link,link_type,creator_type,
    credential,credential_type,Import,import_type,
    task_link,link_data,Export,export_type,link_data_status,
    link_level*/],
  });
}