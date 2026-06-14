import { Instance as Entity } from "../../database/entity/instance.js";
//import base64 from "../util/base64";
//set..
export default async function (server, _$p = { data: {} }) {
    return {
        //set..
        i: async (request, reply) => {
            try {
                const { project, instance } = request.params; //request.query
                //const user_id = request.user.id;
                const repository = server.orm["typeorm"].getRepository(Entity);
                const entity = await repository.findOne({ where: {
                        //user_id: user_id,
                        project: {
                            name: project
                        },
                        name: instance,
                    } });
                if (!entity) {
                    reply.code(404).send({ error: "Not found" });
                    return;
                }
                else {
                    /*reply.code(200).send({
                      success: true,
                      data: {
                        l: [entity],
                      },
                    });*/
                    //set.. 
                    const _lib_ = (await import(`./l/${entity.utility_id}/index.js`)).default;
                    const _lib = await (await _lib_(server, { data: {
                            instance: entity,
                        } })).i(request, reply);
                    return _lib;
                }
            }
            catch (error) {
                console.log(error);
                reply.code(400).send({ error: error });
            }
        },
        i_init: async (request, reply) => {
            try {
                const { project, instance } = request.params; //request.query
                //const user_id = request.user.id;
                const repository = server.orm["typeorm"].getRepository(Entity);
                const entity = await repository.findOne({ where: {
                        //user_id: user_id,
                        project: {
                            name: project
                        },
                        name: instance,
                    } });
                if (!entity) {
                    reply.code(404).send({ error: "Not found" });
                    return;
                }
                else {
                    /*reply.code(200).send({
                      success: true,
                      data: {
                        l: [entity],
                      },
                    });*/
                    //set.. 
                    const _lib_ = (await import(`./l/${entity.utility_id}/index.js`)).default;
                    const _lib = await (await _lib_(server, { data: {
                            instance: entity,
                        } })).i_init(request, reply);
                    return _lib;
                }
            }
            catch (error) {
                console.log(error);
                reply.code(400).send({ error: error });
            }
        },
        //set..
        get_schema_for_create: async (request, reply) => {
            //console.log(`--get_schema_for_create`);
            try {
                let { utility_id } = request.body; //request.query
                const { id } = request.params;
                //set..
                try {
                    if (id) {
                        const repository = server.orm["typeorm"].getRepository(Entity);
                        const entity = await repository.findOne({ where: {
                                //user_id: user_id,
                                id: id,
                            } });
                        //vali..
                        if (!entity) {
                            reply.code(404).send({ error: "Not found" });
                            return;
                        }
                        //update..
                        utility_id = entity.utility_id;
                    }
                }
                catch (error) { }
                //set..
                if (!utility_id) {
                    reply.code(404).send({ error: "Not found" });
                    return;
                }
                else {
                    /*reply.code(200).send({
                      success: true,
                      data: {
                        l: [entity],
                      },
                    });*/
                    //set.. 
                    const _lib_ = (await import(`./l/${utility_id}/index.js`)).default; //${utility_id}
                    const _lib = await (await _lib_(server, { data: {
                        //instance:entity,
                        } })).get_schema_for_create(request, reply);
                    //return _lib;
                    //set..
                    let _r = _lib;
                    let _r_body = _r[`body`];
                    _r[`body`] = {
                        type: 'object',
                        required: [`name`, `project_id`, `utility_id`, `config_id`, `data`],
                        properties: {
                            name: { type: 'string', minLength: 1 },
                            project_id: { type: 'string', minLength: 1 },
                            utility_id: { type: 'string', minLength: 1 },
                            config_id: { type: ['string', 'null'], minLength: 1 },
                            //set..
                            data: _r_body[`properties`][`data`],
                        }
                    };
                    //console.log(JSON.stringify(_r,null,2));
                    return _r;
                }
            }
            catch (error) {
                console.log(error);
                reply.code(400).send({ error: error });
            }
        },
        get_schema_for_run: async (request, reply) => {
            try {
                const { project, instance } = request.params; //request.query
                const repository = server.orm["typeorm"].getRepository(Entity);
                const entity = await repository.findOne({ where: {
                        //user_id: user_id,
                        project: {
                            name: project
                        },
                        name: instance,
                    } });
                if (!entity) {
                    return reply.code(404).send({ error: "Not found" });
                }
                //all ok..
                //set..
                const { utility_id } = entity; //request.body; //request.query
                if (!utility_id) {
                    reply.code(404).send({ error: "Not found" });
                    return;
                }
                else {
                    //set.. 
                    const _lib_ = (await import(`./l/${utility_id}/index.js`)).default; //${utility_id}
                    const _lib = await (await _lib_(server, { data: {
                        //instance:entity,
                        } })).get_schema_for_run(request, reply);
                    return _lib;
                }
            }
            catch (error) {
                console.log(error);
                reply.code(400).send({ error: error });
            }
        }
    };
}
