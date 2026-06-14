//https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/
export default async function (server) {
    return {
        create: {
            body: {
                type: 'object',
                required: [`name`, `project_id`, `data`],
                properties: {
                    name: { type: 'string', minLength: 1 },
                    project_id: { type: 'string', minLength: 1 },
                    data: { type: 'object', },
                }
            },
            querystring: {},
            headers: {},
            params: {}
        },
        update: {
            body: {
                type: 'object',
                required: [`name`, `project_id`, `data`],
                properties: {
                    name: { type: 'string', minLength: 1 },
                    project_id: { type: 'string', minLength: 1 },
                    data: { type: 'object', },
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
        }
    };
}
