import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import { User } from "../../../database/entity/user.js";
import login from "../util/login.js";
import access_token from "../util/access_token.js";

//set..
export default async function(server:FastifyInstance) {
    
    return {
        index: async (request:FastifyRequest, reply:FastifyReply) => {
            const repository = server.orm["typeorm"].getRepository(User);
            const l = await repository.find();
            reply.code(200).send({ success: true, data: { l } });
        },
        create: async (request:any, reply:FastifyReply) => {
            // The `name` and `mail` types are automatically inferred
            const { name, email, pwd } = request.body;
            try {
              const user = new User();
              user.name = name;
              user.email = email;
              user.pwd = pwd;

              //set..
              const repository = server.orm["typeorm"].getRepository(User);

              //check..
              const _get_user = await repository.findOne({ where: { email } });
              if (_get_user) {
                //err..
                reply.status(403).send({
                  success: false,
                  msg: `User already exists!`,
                  data: {
                  },
                });
              }
              //all ok..




              /*//set..
              let _token_rsp;
              try {
                _token_rsp = await (await login(server, request, reply)).set_token(user);
              } catch (error) {
                reply.code(401).send({ error: error as string });
              }
              //all done..*/






              //set..
              const result = await repository.save(user);
              const _new_r = {id:result.id};
              reply.status(201).send({
                success: true,
                data: {
                  l: [_new_r/*result*/],
                },
              });
            } catch (error) {
              reply.code(400).send({ error: error as string });
            }
        },
        view:  async (request:any, reply:any) => {
              try {
                const { id } = request.params; //request.query
                const repository = server.orm["typeorm"].getRepository(User);
                const user = await repository.findOne({ where: { id } });
                if (!user) {
                  reply.code(404).send({ error: "User not found" });
                } else {
                  reply.code(200).send({
                    success: true,
                    data: {
                      l: [user],
                    },
                  });
                }
              } catch (error) {
                reply.code(400).send({ error: error as string });
              }
        },
        delete: async (request:any, reply:any) => {
            const { id } = request.params; //request.query
            const repository = server.orm["typeorm"].getRepository(User);
            const user = await repository.findOne({ where: { id } });
            if (!user) {
              reply.code(404).send({ error: "User not found" });
            } else {
              await repository.remove(user);
              reply.code(200).send({ success: true });
            }
        },
        update: async (request:any, reply:any) => {
            const { id } = request.params; //request.query
            
            const { name, email, pwd } = request.body;
            const repository = server.orm["typeorm"].getRepository(User);
            const user = await repository.findOne({ where: { id } });
            if (!user) {
              reply.code(404).send({ error: "User not found" });
            } else {
              user.name = name;
              user.email = email;
              user.pwd = pwd;
              await repository.save(user);
              reply.code(200).send({
                success: true,
                data: {
                  l: [user],
                },
              });
            }
        },
        login: async (request:any, reply:FastifyReply) => {
          const { email, pwd } = request.body;
          try {
            const user = new User();
            user.email = email;
            user.pwd = pwd;

            //set..
            const repository = server.orm["typeorm"].getRepository(User);

            

            //check..
            //https://orkhan.gitbook.io/typeorm/docs/select-query-builder
            const _get_user = await repository
            /*.createQueryBuilder(`user`).select(`user.*`)
            .where("user.email = :email", { email: email }).getRawOne();*/
            .createQueryBuilder().select(`*`)
            .where("email = :email", { email: email }).getRawOne();
            //.findOne({ where: { email } });
            //console.log(_get_user);
            
            if (!_get_user) {
              //err..
              reply.status(404).send({
                success: false,
                msg: `User not exists!`,
                data: {
                },
              });
            }
            //validate password..
            if (_get_user?.pwd!=pwd) {
              //err..
              reply.status(401).send({
                success: false,
                msg: `Invalid credentials!`,
                data: {
                },
              });
            }
            //all ok..


            //update..
            user.id = _get_user?.id;
            //all ok..




            //set..
            let _token_rsp;
            try {
            _token_rsp = await (await login(server,request,reply)).set_token(user);
            } catch (error) {
            reply.code(401).send({ error: error as string });
            }
            //all done..



            //set..
            const result = _get_user;
            reply.status(200).send({
              success: true,
              msg: `Login successful!`,
              data: {
                //l: [result],
                token: _token_rsp?.token,
              },
            });
            
          } catch (error) {
            reply.code(400).send({ error: error as string });
          }
        },
        check_auth: async (request:FastifyRequest, reply:FastifyReply) => {
          reply.code(200).send({ success: true,
          msg:`Authentication is ok!`, 
          data: {} });
        },




        //set..
        create_access_token:  async (request:any, reply:FastifyReply) => {
          //const { email, pwd } = request.body;
          const { party,route } = request.body;
          const user_id = request.user.id;
          try {
            const user = new User();

            //set..
            const repository = server.orm["typeorm"].getRepository(User);

            

            //check..
            //https://orkhan.gitbook.io/typeorm/docs/select-query-builder
            const _get_user = await repository
            /*.createQueryBuilder(`user`).select(`user.*`)
            .where("user.email = :email", { email: email }).getRawOne();*/
            .createQueryBuilder().select(`*`)
            .where("id = :id", { id: user_id }).getRawOne();
            //.findOne({ where: { email } });
            //console.log(_get_user);
            
            if (!_get_user) {
              //err..
              reply.status(404).send({
                success: false,
                msg: `User not exists!`,
                data: {
                },
              });
            }
            //all ok..


            //update..
            user.id = _get_user?.id;
            //all ok..




            //set..
            let _token_rsp;
            try {
            _token_rsp = await (await access_token(server,request,reply)).set_token(user,{
              payload:{
                security: {
                  party:party,
                  route:route,
                }
              }
            });
            } catch (error) {
            reply.code(401).send({ error: error as string });
            }
            //all done..



            //set..
            const result = _get_user;
            reply.status(200).send({
              success: true,
              msg: `Access token created! for ${party}`,
              data: {
                //l: [result],
                token: _token_rsp?.token,
              },
            });
            
          } catch (error) {
            reply.code(400).send({ error: error as string });
          }
        },





    };
    
}
 