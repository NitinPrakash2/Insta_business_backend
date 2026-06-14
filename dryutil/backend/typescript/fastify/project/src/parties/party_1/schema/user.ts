import { FastifyInstance } from "fastify";
//https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/
export default async function(server:FastifyInstance) {
    return {
        create: {
            body: {
                type: 'object',
                required: [`name`,`email`,`pwd`],
                properties: {
                  name: { type: 'string', minLength: 1 },
                  email: { type: 'string', minLength: 1 },
                  pwd: { type: 'string', minLength: 1 },
                }
            },
            querystring: {},
            headers: {},
            params: {}
        },
        update: {
            body: {
                type: 'object',
                required: [`name`,`email`,`pwd`],
                properties: {
                  name: { type: 'string', minLength: 1 },
                  email: { type: 'string', minLength: 1 },
                  pwd: { type: 'string', minLength: 1 },
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
        login:  {
          body: {
              type: 'object',
              required: [`email`,`pwd`],
              properties: {
                email: { type: 'string', minLength: 1 },
                pwd: { type: 'string', minLength: 1 },
              }
          },
          querystring: {},
          headers: {},
          params: {}
        },





        //set..
        create_access_token:  {
          body: {
            type: 'object',
            required: [`party`,
              `route`
            ],
            properties: {
              party: {
                type: 'array',
                items: {
                  type: 'string',
                  enum: ['party_1', 'party_2'] //allowed values
                },
                minItems: 1,       // at least one element required
                uniqueItems: true  // optional: prevents duplicates
              },
              route: {
                type: 'object',
                required: [
                  `i`,`i_init`
                ],
                additionalProperties: false,
                properties: {
                  i: {
                    type: 'array',
                    items: {
                      type: 'string'
                    },
                    uniqueItems: true,
                    //minItems: 1, 
                  },
                  i_init: {
                    type: 'array',
                    items: {
                      type: 'string'
                    },
                    uniqueItems: true,
                    //minItems: 1, 
                  }
                }

              }
            }
          },
          querystring: {},
          headers: {},
          params: {}
        },



    };
}