import fastifyCookie from "@fastify/cookie";
export default async function (request, reply) {
    const params = request.params;
    const { url } = request;
    //set vars..
    let _mware = {
        var: {
            is_auth_rqd: true,
            err: {
                data: {}
            }
        }
    };
    //set..
    let send_err = () => {
        reply.status(401).send({
            success: false,
            msg: `Unable to authenticate!`,
            data: _mware.var.err.data,
        });
    };
    /*//test..
    _mware.var.is_auth_rqd = false;*/
    //check & set..
    if (url.startsWith('/client/api/i/') || url.startsWith('/client/api/i_init/')) {
        const instanceName = params?.instance;
        //console.log(instanceName);
        //console.log(url);
        // 🚀 bypass auth if instance_name exists AND starts with "public:"
        if (typeof instanceName === 'string' && instanceName.startsWith('public:')) {
            return;
        }
        if (typeof instanceName === 'string' && !instanceName.startsWith('public:')) {
            //update..
            _mware.var.err[`data`] = {
                hint: [`If you are the owner of this resource, and want to make it accessible without [auth] then.. you need to rename it like => [instance-name='public:${instanceName}']`]
            };
        }
    }
    //check & set..
    if (_mware.var.is_auth_rqd) {
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
}
;
