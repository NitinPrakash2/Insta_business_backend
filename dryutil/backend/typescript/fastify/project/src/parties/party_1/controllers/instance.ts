import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import { Instance as Entity } from "../../../database/entity/instance.js";
//import base64 from "../util/base64";
import I from "../../../shared/utility/index.js";

//set..
export default async function(server:FastifyInstance) {
    
    return {
        index: async (request: any, reply: FastifyReply) => {
          const user_id = request.user.id;
          const repository = server.orm["typeorm"].getRepository(Entity);
          const l = await repository.find({where:{user_id:user_id}});
          reply.code(200).send({ success: true, data: { l } });
        },
        create: async (request:any, reply:FastifyReply) => {
            try {
              const { name, project_id, utility_id, config_id, data } = request.body;
              const entity = new Entity();
              entity.name = name;
              entity.project_id = project_id;
              entity.utility_id = utility_id;
              entity.config_id = config_id;
              entity.data = data;
              entity.user_id = request.user.id;
              //console.log(entity.user_id);


               

              //set..
              const repository = server.orm["typeorm"].getRepository(Entity);

              //check..
              const _get_user = await repository.findOne({ where: { name:name,project_id:project_id } });
              if (_get_user) {
                //err..
                reply.status(403).send({
                  success: false,
                  msg: `Already exists!`,
                  data: {
                  },
                });
              }
              //all ok..


              //set..
              const result = await repository.save(entity);
              const _rsp_db = result;
              reply.status(201).send({
                success: true,
                data: {
                  l: [result],

                  //set..
                  hint: _rsp_db.name.startsWith(`public:`) ? [`Note: Currently [instance-name='public:${_rsp_db.name}'] starts with [prefix='public:'] So, it will be accessible for anyone. Please ignore this [WARNING] if you created it intentionally. `] : [`If you are the owner of this resource, and want to make it accessible without [auth] then.. you need to rename it like => [instance-name='public:${_rsp_db.name}']`]


                },
              });
            } catch (error) {
              reply.code(400).send({ error: error as string });
            }
        },
        view:  async (request:any, reply:any) => {
              try {
                const { id } = request.params; //request.query
                const repository = server.orm["typeorm"].getRepository(Entity);
                const entity = await repository.findOne({ where: { id } });
                if (!entity) {
                  reply.code(404).send({ error: "Not found" });
                } else {
                  reply.code(200).send({
                    success: true,
                    data: {
                      l: [entity],
                    },
                  });
                }
              } catch (error) {
                reply.code(400).send({ error: error as string });
              }
        },
        delete: async (request:any, reply:any) => {
            const { id } = request.params; //request.query
            const repository = server.orm["typeorm"].getRepository(Entity);
            const entity = await repository.findOne({ where: { id } });
            if (!entity) {
              reply.code(404).send({ error: "Not found" });
            } else {
              await repository.remove(entity);
              reply.code(200).send({ success: true });
            }
        },
        update: async (request:any, reply:any) => {
            try {
            const { id } = request.params; //request.query
            const { name, project_id, utility_id, config_id, data } = request.body;
            const user_id = request.user.id;



            //set..
            const repository = server.orm["typeorm"].getRepository(Entity);
            const entity = await repository.findOne({ where: { id, user_id:user_id } });
            if (!entity) {
              reply.code(404).send({ error: "Not found" });
            } else {
              entity.name = name;
              entity.project_id = project_id;
              entity.utility_id = utility_id;
              entity.config_id = config_id;
              entity.data = data;
              const _rsp_db = await repository.save(entity);
              reply.code(200).send({
                success: true,
                data: {
                  l: [entity],

                  //set..
                  hint: _rsp_db.name.startsWith(`public:`) ? [`Note: Currently [instance-name='public:${_rsp_db.name}'] starts with [prefix='public:'] So, it will be accessible for anyone. Please ignore this [WARNING] if you created it intentionally. `] : [`If you are the owner of this resource, and want to make it accessible without [auth] then.. you need to rename it like => [instance-name='public:${_rsp_db.name}']`]

                },
              });
            }
            } catch (error) {
              reply.code(400).send({ error: error as string });
            }
        },


        //set..
        patch: async (request: any, reply: any) => {
        try {
          const { id } = request.params;
          const body = request.body;
          const user_id = request.user.id;

          //set..
          const repository = server.orm["typeorm"].getRepository(Entity);
          const entity = await repository.findOne({ where: { id, user_id: user_id } });

          if (!entity) {
            return reply.code(404).send({ error: "Not found" });
          }

          // ✅ allowed fields for patching
          const allowedFields = [
            "name", 
            //"project_id", 
            //"utility_id", 
            //"config_id", 
            "data"
          ];

          // 🚀 generic patch with whitelist
          Object.entries(body).forEach(([key, value]) => {
            if (value !== undefined && allowedFields.includes(key)) {
              (entity as any)[key] = value;
            }
          });

          const _rsp_db = await repository.save(entity);

          return reply.code(200).send({
            success: true,
            data: { 
              l: [entity],

              //set..
              hint: _rsp_db.name.startsWith(`public:`) ? [`Note: Currently [instance-name='public:${_rsp_db.name}'] starts with [prefix='public:'] So, it will be accessible for anyone. Please ignore this [WARNING] if you created it intentionally. `] : [`If you are the owner of this resource, and want to make it accessible without [auth] then.. you need to rename it like => [instance-name='public:${_rsp_db.name}']`]

            },
          });
        } catch (error) {
          return reply.code(400).send({ error: (error as Error).message });
        }
        },




        //set..
        i:  async (request:any, reply:any) => {
              try {
                const _lib = await (await I(server,{data:{}})).i(request,reply);
                return _lib;
              } catch (error) {
                reply.code(400).send({ error: error as string });
              }
        },



    };
    
}
 