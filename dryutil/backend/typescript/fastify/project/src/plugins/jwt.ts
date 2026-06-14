/*import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import fp from "fastify-plugin";
import jwt from "@fastify/jwt";
import auth from "@fastify/auth";

export default fp(async (fastify: FastifyInstance) => {
  if (!process.env.RSA_PUBLIC_KEY_BASE_64) {
    throw new Error(
      "Environment variable `RSA_PUBLIC_KEY_BASE_64` is required",
    );
  }
  //console.log(`--pass`);
  
  const publicKey = Buffer.from(
    process.env.RSA_PUBLIC_KEY_BASE_64,
    "base64",
  ).toString("ascii");
  if (!publicKey) {
    fastify.log.error(
      "Public key not found. Make sure env var `RSA_PUBLIC_KEY_BASE_64` is set.",
    );
  }

  fastify.register(jwt, {
    secret: {
      public: publicKey,
    },
  });

   

  fastify.register(auth);

  fastify.decorate("verifyJWT", async (request:FastifyRequest, reply:FastifyReply) => {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.send(err);
    }
  });

});*/

//https://www.npmjs.com/package/@fastify/jwt
/*declare module "@fastify/jwt" {
  interface FastifyJWT {
    payload: { id: string } // payload type is used for signing and verifying
    user: {
      id: string,
      name: string,
      age: string
    } // user type is return type of `request.user` object
  }
}*/
 


import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import fp from "fastify-plugin";
import jwt from "@fastify/jwt";
//import auth from "@fastify/auth";

export default fp(async (fastify: FastifyInstance) => {
  if (!process.env.RSA_PUBLIC_KEY_BASE_64) {
    throw new Error(
      "Environment variable `RSA_PUBLIC_KEY_BASE_64` is required",
    );
  }
  if (!process.env.RSA_PRIVATE_KEY_BASE_64) {
    throw new Error(
      "Environment variable `RSA_PRIVATE_KEY_BASE_64` is required",
    );
  }



  //console.log(`--pass`);
  const publicKey = Buffer.from(
    process.env.RSA_PUBLIC_KEY_BASE_64,
    "base64",
  ).toString("ascii");
  const privateKey = Buffer.from(
    process.env.RSA_PRIVATE_KEY_BASE_64,
    "base64",
  ).toString("ascii");
  //vali..
  if (!publicKey) {
    fastify.log.error(
      "Public key not found. Make sure env var `RSA_PUBLIC_KEY_BASE_64` is set.",
    );
  }
  if (!privateKey) {
    fastify.log.error(
      "Private key not found. Make sure env var `RSA_PRIVATE_KEY_BASE_64` is set.",
    );
  }
  //all ok..

  //set..
  await fastify.register(jwt, {
    secret: {
      public: publicKey,
      private: privateKey,
    },
    sign: { algorithm: 'RS256' }
  });
  //console.log(publicKey);



  /*//----test----// [START]
  //create a jwt token..
  const payload = {
    id: `user.id`,
    email: `user.email`,
    name: `user.name`,
  };
  const token = fastify.jwt.sign(payload, {});
  console.log(token);

  //verify a jwt token..
  const token_verify = fastify.jwt.verify(token);//+`__TYPO`
  console.log(token_verify);

  //decode..
  const token_decode = fastify.jwt.decode(token);
  console.log(token_decode);
  //----test----// [END]*/



});