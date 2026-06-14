export default async function () {
    //https://stackoverflow.com/questions/32491681/how-to-check-if-a-string-is-plaintext-or-base64-format-in-node-js
    return {
        check: async (_$p) => {
            try {
                const base64RegExp = /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$/;
                const isBase64 = (str) => base64RegExp.test(str);
                if (isBase64(_$p.data) === true) {
                    return true;
                }
                //err..
                throw `data is not base64`;
            }
            catch (err) {
                throw err;
            }
        }
    };
}
