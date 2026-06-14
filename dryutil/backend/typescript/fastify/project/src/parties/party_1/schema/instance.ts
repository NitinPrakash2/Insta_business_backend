import { FastifyInstance } from "fastify";
import I from "../../../shared/utility/index";

//https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/
export default async function(server:FastifyInstance) {
     /*try {
                    const _lib = await (await I(server,{data:{}})).i(request,reply);
                    return _lib;
                  } catch (error) {
                    reply.code(400).send({ error: error as string });
                  }*/


    //set..
    return {
        create: {
            body: {
                type: 'object',
                required: [`name`,`project_id`, `utility_id`, `config_id`, `data`],
                properties: {
                  name: { type: 'string', minLength: 1 },
                  project_id: { type: 'string', minLength: 1 },
                  utility_id: { type: 'string', minLength: 1 },
                  config_id: { type: ['string','null'], minLength: 1 },
                  data: { type: 'object' },
                }
            },
            querystring: {},
            headers: {},
            params: {}
        },
        update: {
            body: {
                type: 'object',
                required: [`name`,`project_id`, `utility_id`, `config_id`, `data`],
                properties: {
                  name: { type: 'string', minLength: 1 },
                  project_id: { type: 'string', minLength: 1 },
                  utility_id: { type: 'string', minLength: 1 },
                  config_id: { type: ['string','null'], minLength: 1 },
                  data: { type: 'object' },
                }
            },
            querystring: {},
            headers: {},
            params: {
                type: 'object',
                required: [`id`],
                properties: {
                  id: { type: 'string', minLength: 1 },
                }
            }
        },
        delete: {
            body: {},
            querystring: {},
            headers: {},
            params: {
              type: 'object',
              required: [`id`],
              properties: {
                id: { type: 'string', minLength: 1 },
              }
            }
        },
        view: {
            //body: {},
            querystring: {},
            headers: {},
            params: {
              type: 'object',
              required: [`id`],
              properties: {
                id: { type: 'string', minLength: 1 },
              }
            }
        },
        index: {
          //body: {},
          querystring: {
            type: 'object',
            //required: [`name`,],
            properties: {
              //name: { type: 'string', minLength: 1 },
            }
          }, 
          
          headers: {},
          params: {}
        },




        //set..
        i: {
            //body: {},
            querystring: {},
            headers: {},
            params: {
              type: 'object',
              required: [`project`,`instance`],
              properties: {
                project: { type: 'string', minLength: 1 },
                instance: { type: 'string', minLength: 1 },
              }
            }
        },


    };
}