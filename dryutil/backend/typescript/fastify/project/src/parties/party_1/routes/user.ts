import { FastifyInstance, FastifyRequest } from "fastify";
import Controller from "../controllers/user.js";
import Schema from "../schema/user.js";

//export function configureRoutes(server: FastifyInstance) {
export default async function(server: FastifyInstance) {
  //set vars..
  const _ep_prefix = `/api/user`;


  //<{ Reply: IReply }>
  server.get(
    `${_ep_prefix}`,
  (await Controller(server))[`index`]);


  //<{ Body: StaticType; Reply: IReply }>
  server.post(
    `${_ep_prefix}/create`,
    {
      schema: (await Schema(server))[`create`],
    },
    (await Controller(server))[`create`]
  );


  //<{ Querystring: IQuerystring; Reply: IReply }>
  server.get(
    `${_ep_prefix}/view/:id`,
    {
      schema: (await Schema(server))[`view`],
    },
    (await Controller(server))[`view`]
  );


  //<{ Body: StaticType; Reply: IReply }>
  server.post(
    `${_ep_prefix}/login`,
    {
      schema: (await Schema(server))[`login`],
    },
    (await Controller(server))[`login`]
  );







  //----protected----// [START]
  await server.register(async function(server: FastifyInstance) {
    /*server.addHook(`preHandler`, require('../middlewares/auth').default);*/
    server.addHook('preHandler', async (request, reply) => { await (await import(`../middlewares/auth.js`)).default(request, reply,); });
    //all done..


    //set.. //<{ Querystring: IQuerystring; Reply: IdeleteReply }>
    server.delete(
      `${_ep_prefix}/delete/:id`,
      {
        schema: (await Schema(server))[`delete`]
      },
      (await Controller(server))[`delete`],
    );
    //<{ Querystring: IQuerystring; Body: StaticType; Reply: IReply }>
    server.put(
      `${_ep_prefix}/update/:id`,
      {
        schema: (await Schema(server))[`update`],
      },
      (await Controller(server))[`update`]
    );



    //set..
    server.get(
      `${_ep_prefix}/check_auth`,
    (await Controller(server))[`check_auth`]);




    //set..
    server.post(
      `${_ep_prefix}/create_access_token`,
      {
        schema: (await Schema(server))[`create_access_token`],
      },
      (await Controller(server))[`create_access_token`]
    );




  });
  //----protected----// [END]



}