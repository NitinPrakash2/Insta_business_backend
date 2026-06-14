import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason,
  WASocket,
} from "@whiskeysockets/baileys";

import QRCode from "qrcode";
import fs from "fs";
import path from "path";


//
// Unified registry for clients
//
type ClientKey = string; // e.g. "85e6c11a-8233-4a1b-bac8-5019b648f986:number1"

interface ClientState {
  sock?: WASocket;
  promise?: Promise<WASocket>;
  connected: boolean;
}

const clientRegistry: Record<ClientKey, ClientState> = {};

//
// Public function: get client (creates or returns existing)
//
async function getBaileysClient(_$v:{
  typ:`send_msg` | `init`
},instanceId: string, number: string): Promise<WASocket> {
  const key: ClientKey = `${instanceId}:${number}`;

  // Already connected → return socket
  if (clientRegistry[key]?.sock && clientRegistry[key].connected) {
    return clientRegistry[key].sock!;
  }

  // Already initializing → return pending promise
  if (clientRegistry[key]?.promise) {
    return clientRegistry[key].promise!;
  }

  // Otherwise, start fresh init
  clientRegistry[key] = {
    connected: false,
    promise: initClient(_$v, instanceId, number, key),
  };

  return clientRegistry[key].promise!;
}

//
// Internal: initialize client
//
async function initClient(_$v:any, instanceId: string, number: string, key: ClientKey): Promise<WASocket> {
  const sessionPath = `./s_e_s_s_i_o_n/baileys_wa/${instanceId}/${number}`;
  const { state, saveCreds } = await useMultiFileAuthState(sessionPath);

  const sock = makeWASocket({
    auth: state,
    printQRInTerminal: false,
    //logger: false,
    //maxMsgRetryCount:2,
  });

  const _close_conn = (sock:any,reject:any) => {
    /*if (sock) {
    try {
      sock.end(new Error("Connection closed")); // closes WS + stops events
    } catch (e) {
      console.warn(`[${key}] Socket already closed`);
    }      
    }*/
    reject(new Error("Err: connection=close"));
  };

  clientRegistry[key].sock = sock;

  sock.ev.on("creds.update", saveCreds);

  return new Promise<WASocket>((resolve, reject) => {
    sock.ev.on("connection.update", (update) => {
      const { connection, qr, isNewLogin, lastDisconnect } = update;



      //check & set..
      if (_$v[`typ`]==`send_msg`) {
      if (!isNewLogin) {
        //console.log(`isNewLogin: ${isNewLogin}`);
        _close_conn(sock,reject);
      }
      }



      //check & set..
      if (_$v[`typ`]==`init`) {
      if (qr) {
        console.log(`📲 [${key}] Scan this QR:`);
        /*QRCode.toString(qr, { type: "terminal", small: true }, (err, str) => {
          if (!err) {
          //console.log(str);
          //set..
          reject({
            typ:`qr`,
            data: {
              //img:str,
              base64: qr,
            }
          });
          }
        });*/
        QRCode.toDataURL(qr, { type: "image/png" }, (err, url) => {
          if (!err) {
            // url is like: "data:image/png;base64,AAAA..."
            reject({
              typ: "qr",
              data: {
                number: number,
                base64: url, // full data URL base64 string
              }
            });
          } else {
            reject(err);
          }
        });



      }
      }



      if (connection === "open") {
        console.log(`✅ [${key}] WhatsApp connected!`);
        clientRegistry[key].connected = true;
        resolve(sock); // <-- resolve only here
      }

      if (connection === "close") {
        const reason = (lastDisconnect?.error as any)?.output?.statusCode;
        clientRegistry[key].connected = false;
        clientRegistry[key].promise = undefined;

 

        if (reason === DisconnectReason.loggedOut || reason === 401) {
          console.log(`⚠️ [${key}] Session invalidated → clearing and regenerating...`);
          fs.rmSync(sessionPath, { recursive: true, force: true });
          /* getBaileysClient(_$v, instanceId, number).then(resolve).catch(reject); */
        } else {
          console.log(`❌ [${key}] Disconnected, retrying...`);
          /* getBaileysClient(_$v, instanceId, number).then(resolve).catch(reject); */
        }


        
        //check & set..
        if (_$v[`typ`]==`send_msg`) {
        _close_conn(sock,reject);
        }


        //check & set..
        if (_$v[`typ`]==`init`) {
        getBaileysClient(_$v, instanceId, number).then(resolve).catch(reject);
        }





      }


    });
  });
}




//--avail-numbers--//
function isSessionValid(instanceId: string, number: string): boolean {
  const dir = path.join("./s_e_s_s_i_o_n/baileys_wa", instanceId, number);
  const credsFile = path.join(dir, "creds.json");
  return fs.existsSync(credsFile);
}
function getAvailableNumbers(instanceId: string, numbers: string[]): string[] {
  return numbers.filter((num) => isSessionValid(instanceId, num));
}




export { getBaileysClient, clientRegistry, getAvailableNumbers };
