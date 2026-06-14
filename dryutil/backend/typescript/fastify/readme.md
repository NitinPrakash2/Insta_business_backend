# [vanilla]



# ref
  https://fastify.dev/docs/latest/Reference/TypeScript/
  https://medium.com/@christianinyekaka/building-a-restful-api-with-typescript-fastify-typeorm-and-postgresql-dd6309c0d05a
  https://typeorm.io/
  https://blog.heroku.com/build-openapi-apis-nodejs-fastify
  https://dev.to/franciscomendes10866/how-to-seed-database-using-typeorm-seeding-4kd5
  https://www.npmjs.com/package/date-fns

 
# solve-dependency-conflict
  https://dev.to/writech/how-to-fix-the-npm-conflicting-peer-dependency-error-3fag
  # incase of [dependency-compatibility]..first manually add `dependency` in `package.json` and run the cmd..
  $ npm install --legacy-peer-deps




# [SETUP] 
  $ cd project
  $ npm init -y
  $ npm i fastify
  $ npm i -D typescript @types/node
  $ npx tsc --init
  # setup additional..
  $ npm i typeorm-fastify-plugin @sinclair/typebox  @fastify/type-provider-typebox concurrently dotenv typeorm pg reflect-metadata mysql2 @fastify/autoload @fastify/jwt @fastify/auth
  $ npm install -g ts-node
  $ npm i nodemon
  $ npm i @fastify/cookie
  $ npm i typeorm-seeding
  $ npm i @fastify/cors
  $ npm i fastify-socket.io socket.io

  $ npm i uuid
  $ npm install exceljs
  $ npm i ajv

  $ npm install @whiskeysockets/baileys  --OR--  $ npm install @whiskeysockets/baileys@6.5.0

  $ npm install qrcode
  $ npm install --save-dev @types/qrcode

  
  $ npm install ts-node


  $ npm install -D ts-node


  $ npm install @octokit/app @octokit/rest simple-git


  $ npm install --save-dev ts-node


  $ npm install --save-dev tsc-alias


  $ npm install glob fs-extra --save-dev


  $ npm i -D @types/ws


  $ npm install --save-dev ts-node@latest


  $ npm i -D tsx

  $ npm install archiver tmp-promise

  $ npm i --save-dev @types/archiver 

  $ npm i --save-dev @types/fs-extra  


  $ npm install @fastify/multipart
















  

  # Creating the Database..
  $ sudo -u postgres psql
  $ CREATE DATABASE dryutil;
  # set permission..
  $ sudo -u postgres psql
  $ alter role usr1mn superuser;








  # now run..
  $ npm run build
   


# [Watch]
  $ npm run start:dev



# [Dev]
  $ npm run dev



# [Build]
  $ npm run build


# [Build-and-Run]
  $ npm run build && npm run start






# [Deployment]
  $ cd project

  # [Zip]
  $ tar czf dist.tar.gz dist


  # Login to `deployment/hosting` server..
  # Now, navigate to your prefer location for eg => `/home/fognasy/nodejs-proj`.
  $ mkdir dryutil
  $ cd dryutil
  # Upload, the below [files-or-dirs]..
  # eg => 
  [local-location=`/home/chist/Desktop/space/a/project/dryutil/backend/typescript/fastify/project/`]
  [server-location=`/home/fognasy/nodejs-proj/dryutil`]
  Hint: We can use `filezilla`
  /*
  dist.tar.gz
  .env
  package.json
  tsconfig.json
  */


  # now..
  # [UnZip]
  $ tar -xf dist.tar.gz



# [Deployment-run]
  # Outside dist -OR- src `path`..
  # [--DEPRECATED]
  $ pm2 start 'ts-node src/index.ts'  --name  "dryutilFastify" && pm2 save && pm2 startup && pm2 save
  # [--NEW]
  $ pm2 start 'dist/index.js'  --name  "dryutilFastify" && pm2 save && pm2 startup && pm2 save





# [list-package]
  $ npm list --depth=0







# Configure `Reverse-proxy` [Apache2]
  $ nano /etc/apache2/sites-available/nodeapp.conf
   

  /* [ref] https://socket.io/docs/v3/reverse-proxy/#apache-httpd
  <VirtualHost *:443>
    ServerName fastify.dryutil.1mn.io


    ProxyPreserveHost On
    RewriteEngine On


    SSLEngine On
    SSLCertificateFile "/etc/letsencrypt/live/fastify.dryutil.1mn.io/fullchain.pem"
    SSLCertificateKeyFile "/etc/letsencrypt/live/fastify.dryutil.1mn.io/privkey.pem"



    # Upgrade connections to WebSockets
    ProxyPass / http://localhost:8082/
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:8082/$1" [P,L]
    
    
    
    # Redirect http to https
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

    # Everything else forwards as HTTP to the node app.
    ProxyPass / http://127.0.0.1:8082/
    ProxyPassReverse / http://127.0.0.1:8082/


  </VirtualHost>

  */








  $ a2ensite nodeapp.conf

  # [no-need-to-run] $ a2dissite 000-default 
  $ a2enmod proxy proxy_http rewrite headers expires
  $ systemctl restart apache2







