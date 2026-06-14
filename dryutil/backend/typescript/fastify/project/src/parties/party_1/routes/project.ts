import { FastifyInstance, FastifyRequest } from "fastify";
import Controller from "../controllers/project.js";
import Schema from "../schema/project.js";

//export function configureRoutes(server: FastifyInstance) {
export default async function(server: FastifyInstance) {
  //set vars..
  const _ep_prefix = `/api/project`;


  /*server.get(
    `${_ep_prefix}`,
  (await Controller(server))[`index`]);*/





  //----protected----// [START]
  await server.register(async function(server: FastifyInstance) {
    /*server.addHook(`preHandler`, require('../middlewares/auth').default);*/
    server.addHook('preHandler', async (request, reply) => { await (await import(`../middlewares/auth.js`)).default(request, reply,); });
    //all done..


    //set..
    server.get(
      `${_ep_prefix}`,
      {
        schema: (await Schema(server))[`index`],
      },
    (await Controller(server))[`index`]);
    server.post(
      `${_ep_prefix}/create`,
      {
        schema: (await Schema(server))[`create`],
      },
      (await Controller(server))[`create`]
    );
    server.get(
      `${_ep_prefix}/view/:id`,
      {
        schema: (await Schema(server))[`view`],
      },
      (await Controller(server))[`view`]
    );
    server.delete(
      `${_ep_prefix}/delete/:id`,
      {
        schema: (await Schema(server))[`delete`]
      },
      (await Controller(server))[`delete`],
    );
    server.put(
      `${_ep_prefix}/update/:id`,
      {
        schema: (await Schema(server))[`update`],
      },
      (await Controller(server))[`update`]
    );


  });
  //----protected----// [END]



}