import fastifyCookie from "@fastify/cookie";
export default async function (request, reply) {
    let send_err = () => {
        reply.status(401).send({
            success: false,
            msg: `Unable to authenticate!`,
            data: {},
        });
    };
    try {
        //console.log('second');
        //next();
        //test..err//https://fastify.dev/docs/latest/Reference/Errors/
        //send_err();
        //set..
        let _token = ``;
        //set..
        const _cookie = fastifyCookie.parse(`${request?.headers?.cookie}`, {});
        //check & set..
        if (_cookie?.access_token) {
            //update..
            _token = _cookie?.access_token;
        }
        //set..
        let _authorization = request.headers?.authorization;
        //check & set..
        if (typeof _authorization === "string") {
            _authorization = _authorization.trim();
            if (_authorization.startsWith(`Bearer`)) {
                let _auth_arr = _authorization.split(` `);
                if (_auth_arr.length === 2) {
                    //update..
                    _token = _auth_arr[1];
                }
            }
        }
        //log..
        //console.log(_token);
        //set..
        _token = _token.trim();
        //check..
        if (_token === ``) {
            //err..
            send_err();
            return;
        }
        //all ok..
        //set..
        const _verify_token = request.server.jwt.verify(_token, {
            ignoreExpiration: true,
            //complete:true,
        });
        //set..
        let _token_data = _verify_token;
        //console.log( _token_data?.id );
        //log..
        //console.log(_token_data);
        //vali..
        if (_token_data[`security`][`party`].indexOf(`party_1`) == -1) {
            //err..
            send_err();
            return;
        }
        //all ok..
        //update..
        request.user = {
            id: _token_data?.id
        };
        //console.log( request.user );
        //all ok..
        //done();
    }
    catch (error) {
        send_err();
    }
}
;
