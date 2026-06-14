import { Config as Entity } from "../../../database/entity/config.js";
//import base64 from "../util/base64";
//set..
export default async function (server) {
    return {
        index: async (request, reply) => {
            const repository = server.orm["typeorm"].getRepository(Entity);
            const l = await repository.find();
            reply.code(200).send({ success: true, data: { l } });
        },
        create: async (request, reply) => {
            try {
                const { name, project_id, data } = request.body;
                const entity = new Entity();
                entity.name = name;
                entity.project_id = project_id;
                entity.data = data;
                entity.user_id = request.user.id;
                //console.log(entity.user_id);
                //set..
                const repository = server.orm["typeorm"].getRepository(Entity);
                //check..
                const _get_user = await repository.findOne({ where: { name: name, project_id: project_id } });
                if (_get_user) {
                    //err..
                    reply.status(403).send({
                        success: false,
                        msg: `Already exists!`,
                        data: {},
                    });
                }
                //all ok..
                //set..
                const result = await repository.save(entity);
                reply.status(201).send({
                    success: true,
                    data: {
                        l: [result],
                    },
                });
            }
            catch (error) {
                reply.code(400).send({ error: error });
            }
        },
        view: async (request, reply) => {
            try {
                const { id } = request.params; //request.query
                const repository = server.orm["typeorm"].getRepository(Entity);
                const entity = await repository.findOne({ where: { id } });
                if (!entity) {
                    reply.code(404).send({ error: "Not found" });
                }
                else {
                    reply.code(200).send({
                        success: true,
                        data: {
                            l: [entity],
                        },
                    });
                }
            }
            catch (error) {
                reply.code(400).send({ error: error });
            }
        },
        delete: async (request, reply) => {
            const { id } = request.params; //request.query
            const repository = server.orm["typeorm"].getRepository(Entity);
            const entity = await repository.findOne({ where: { id } });
            if (!entity) {
                reply.code(404).send({ error: "Not found" });
            }
            else {
                await repository.remove(entity);
                reply.code(200).send({ success: true });
            }
        },
        update: async (request, reply) => {
            try {
                const { id } = request.params; //request.query
                const { name, project_id, data } = request.body;
                //set..
                const repository = server.orm["typeorm"].getRepository(Entity);
                const entity = await repository.findOne({ where: { id } });
                if (!entity) {
                    reply.code(404).send({ error: "Not found" });
                }
                else {
                    entity.name = name;
                    entity.project_id = project_id;
                    entity.data = data;
                    await repository.save(entity);
                    reply.code(200).send({
                        success: true,
                        data: {
                            l: [entity],
                        },
                    });
                }
            }
            catch (error) {
                reply.code(400).send({ error: error });
            }
        },
    };
}
