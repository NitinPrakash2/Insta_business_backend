import { FastifyInstance, FastifyReply, FastifyRequest } from "fastify";
import fp from "fastify-plugin";
import cookie from "@fastify/cookie";

export default fp(async (fastify: FastifyInstance) => {
  if (!process.env.SECRET_FOR_COOKIES_SIGN) {
    throw new Error(
      "Environment variable `SECRET_FOR_COOKIES_SIGN` is required",
    );
  }


  //console.log(`--pass`);
  const SECRET_FOR_COOKIES_SIGN = process.env.SECRET_FOR_COOKIES_SIGN;
   
  //vali..
  if (!SECRET_FOR_COOKIES_SIGN) {
    fastify.log.error(
      "Cookie key not found. Make sure env var `SECRET_FOR_COOKIES_SIGN` is set.",
    );
  }
  //all ok..


  //set..
  await fastify.register(cookie, {
    secret: SECRET_FOR_COOKIES_SIGN, // for cookies signature
    hook: 'onRequest', // set to false to disable cookie autoparsing or set autoparsing on any of the following hooks: 'onRequest', 'preParsing', 'preHandler', 'preValidation'. default: 'onRequest'
    parseOptions: {}  // options for parsing cookies
  });


  /*//----test----// [START]
  //----test----// [END]*/



});