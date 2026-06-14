import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import { User } from "../../../database/entity/user";

export default async function(server:FastifyInstance,request:FastifyRequest,reply:FastifyReply) {
    return {
        set_token: async (user:User) => {
            try {
            //throw `err: token`;
            //console.log(user.id);
            //set..
            const payload = {
                id: user.id,
                name: user.name,
                //set..
                security: {
                   party:[`party_1`,`party_2`]
                }
            };
            const token = server.jwt.sign(payload, {
               sub: user.id    
            });
            //all done..

             

            //set..
            reply.setCookie(`access_token`,`${token}`,{
                httpOnly:true,
                secure:true,
                signed:false,
                //expires
                path:`/`
            });

            //set..
            return {
                token:token,
            };
            } catch (err) { throw err; }
        }
    };
}