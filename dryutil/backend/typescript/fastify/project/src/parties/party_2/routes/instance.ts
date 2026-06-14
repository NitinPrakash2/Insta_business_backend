import { FastifyInstance, FastifyRequest } from "fastify";
import Controller from "../controllers/instance.js";
import Schema from "../schema/instance.js";
import Ajv from "ajv";
import I from "../../../shared/utility/index.js";
  

//export function configureRoutes(server: FastifyInstance) {
export default async function(server: FastifyInstance) {
  //set vars..
  //const _ep_prefix = `/api/instance`;
  const _ep_prefix_0 = `/api/i`;
  const _ep_prefix_1 = `/api/i_init`;


  /*server.get(
    `${_ep_prefix}`,
  (await Controller(server))[`index`]);*/
  //console.log(`--server [instance]`);


  //--u--// [START]
  /*server.all(
     `${_ep_prefix_0}/:project/:instance`,
      {
        //schema: (await Schema(server))[`update`],
      },
      //(await Controller(server))[`update`]
      async (request:any, reply) => {
        let schema:any = {};//getSchemaByUtilityId(utility_id);
        try {
          schema = await (await I(server, { data: {} })).get_schema_for_run(request, reply);
        } catch (error) {
          reply.code(400).send({ error: error as string });
          return;
        }
        //console.log(schema);


        //set..
        const ajv = new Ajv();
        const validate = ajv.compile(schema?.[`body`]);
        const validate_querystring = ajv.compile(schema?.[`querystring`]);

        if (!validate(request.body)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate.errors });
        }
        if (!validate_querystring(request.query)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate_querystring.errors });
        }

        //set..
        return (await Controller(server))[`i`](request, reply);
      }
  )*/
  //--u--// [END]

  



  //----protected----// [START]
  await server.register(async function(server: FastifyInstance) {
    /*server.addHook(`preHandler`, require('../middlewares/auth').default);*/
    server.addHook('preHandler', async (request, reply) => { await (await import(`../middlewares/auth.js`)).default(request, reply,); });
    //all done..


    /*//set..
    server.get(
      `${_ep_prefix}`,
      {
        schema: (await Schema(server))[`index`],
      },
    (await Controller(server))[`index`]);
    server.post(
      `${_ep_prefix}/create`,
      {
        //schema: (await Schema(server))[`create`],
      },
      //(await Controller(server))[`create`]
      async (request:any, reply) => {
        let schema:any = {};//getSchemaByUtilityId(utility_id);
        try {
          schema = await (await I(server, { data: {} })).get_schema_for_create(request, reply);
        } catch (error) {
          reply.code(400).send({ error: error as string });
        }


        //set..
        const ajv = new Ajv();
        const validate = ajv.compile(schema?.[`body`]);

        if (!validate(request.body)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate.errors });
        }

        //set..
        return (await Controller(server))[`create`](request, reply);
      }

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
        //schema: (await Schema(server))[`update`],
      },
      //(await Controller(server))[`update`]
      async (request:any, reply) => {
        let schema:any = {};//getSchemaByUtilityId(utility_id);
        try {
          schema = await (await I(server, { data: {} })).get_schema_for_create(request, reply);
        } catch (error) {
          reply.code(400).send({ error: error as string });
          return;
        }
        //console.log(schema);


        //set..
        const ajv = new Ajv();
        const validate = ajv.compile(schema?.[`body`]);

        if (!validate(request.body)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate.errors });
        }

        //set..
        return (await Controller(server))[`update`](request, reply);
      }
    );*/




    //--u--// [START]
    /*server.all(
      `${_ep_prefix_0}/:project/:instance`,
      {
        schema: (await Schema(server))[`i`],
      },
      (await Controller(server))[`i`], 
    );*/
    server.all(
     `${_ep_prefix_0}/:project/:instance`,
      {
        //schema: (await Schema(server))[`update`],
      },
      //(await Controller(server))[`update`]
      async (request:FastifyRequest, reply) => {
        const contentType = request.headers["content-type"] || "";
        //console.log(contentType);

        /*//test.. [START]
        if (contentType.includes('multipart/form-data')) {
          console.log(contentType);
          // Only now call request.parts()
          const parts = request.parts();
          console.log(`==parts-log==`);
          console.log(parts);
          for await (const part of parts) {
            console.log("Got part:", part.fieldname,);
          }
        }
        //test.. [END]*/


        //set..
        let schema:any = {};//getSchemaByUtilityId(utility_id);
        try {
          schema = await (await I(server, { data: {} })).get_schema_for_run(request, reply);
        } catch (error) {
          reply.code(400).send({ error: error as string });
          return;
        }
        //console.log(schema);



        //set..
        const ajv = new Ajv();

        //check & set..
        if (!contentType.includes('multipart/form-data')) {
        const validate = ajv.compile(schema?.[`body`]);
        if (!validate(request.body)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate.errors });
        }
        }

        const validate_querystring = ajv.compile(schema?.[`querystring`]);
        if (!validate_querystring(request.query)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate_querystring.errors });
        }

        //set..
        return (await Controller(server))[`i`](request, reply);
      }
    )
    server.all(
     `${_ep_prefix_1}/:project/:instance`,
      {
        //schema: (await Schema(server))[`update`],
      },
      //(await Controller(server))[`update`]
      async (request:any, reply) => {
        let schema:any = {};//getSchemaByUtilityId(utility_id);
        try {
          schema = await (await I(server, { data: {} })).get_schema_for_run(request, reply);
        } catch (error) {
          reply.code(400).send({ error: error as string });
          return;
        }
        //console.log(schema);


        //set..
        const ajv = new Ajv();
        const validate = ajv.compile(schema?.[`body`]);
        const validate_querystring = ajv.compile(schema?.[`querystring`]);

        if (!validate(request.body)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate.errors });
        }
        if (!validate_querystring(request.query)) {
          return reply.code(400).send({ error: 'Validation failed', details: validate_querystring.errors });
        }

        //set..
        return (await Controller(server))[`i_init`](request, reply);
      }
    )
    //--u--// [END]


  });
  //----protected----// [END]



}