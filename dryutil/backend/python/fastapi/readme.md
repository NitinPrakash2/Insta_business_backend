# [fastapi]



# ref
  https://fastapi.tiangolo.com/
  https://github.com/vllm-project/vllm
  https://pytorch.org/
  https://www.tensorflow.org/
   


# [Pre-requisites]
  # Install Python 3.10+ (3.10, 3.11, or 3.12 are fine).
  # Check
  $ python3 --version
  # [Python]
  # If your Machine uses python → make sure it points to Python 3, not 2.x.
  $ sudo apt update
  $ sudo apt install python3 python3-venv python3-pip -y
  # [Poetry] (dependency + environment manager)
  $ curl -sSL https://install.python-poetry.org | python3 -
  # Add to PATH:
  $ export PATH="$HOME/.local/bin:$PATH"
  $ poetry --version






# [NOTES]..
/*
Optional: GPU / CUDA (for AI training)

Since your current GPU is GT 730 (Kepler), CUDA won’t work well.

For dev you can stick with CPU PyTorch (torch auto-installs CPU version).

Later, on cloud or a better GPU, install CUDA-enabled PyTorch from PyTorch site.

*/









# [SETUP] 
  $ cd project
  
  [--DEPRECATED] $ poetry config virtualenvs.in-project true
  $ poetry init
  # setup additional..

  $ poetry add fastapi
  $ poetry add uvicorn

  $ poetry add sqlalchemy[asyncio] asyncpg alembic

  $ poetry add httpx


  $ poetry add python-jose[cryptography]
  $ poetry add python-dotenv
  $ poetry add jsonschema



  $ poetry add typesense








  # Check your virtual environment
  $ poetry env list



   




  

  # Creating the Database..
  $ sudo -u postgres psql
  $ CREATE DATABASE dryutil;
  # set permission..
  $ sudo -u postgres psql
  $ alter role usr1mn superuser;







  # [Utility_id:8] required [Pre-requisites]
  ## For self-hosted Typesense Server [ref] https://typesense.org/downloads
  $ curl -O https://dl.typesense.org/releases/VERSION/typesense-server-VERSION-amd64.deb  #eg => $ curl -O https://dl.typesense.org/releases/29.0/typesense-server-29.0-amd64.deb
  $ sudo dpkg -i typesense-server-VERSION-amd64.deb   #eg => $ sudo dpkg -i typesense-server-29.0-amd64.deb

  # check config file for [creds]
  $ sudo nano /etc/typesense/typesense-server.ini

  # Status
  $ sudo systemctl status typesense-server
  # Start
  $ sudo systemctl start typesense-server
  # Stop
  $ sudo systemctl stop typesense-server
  # Restart
  $ sudo systemctl restart typesense-server

  # Test
  $ curl -i http://localhost:8108/health -H "X-TYPESENSE-API-KEY: KEY"







      










# [Dev]
  $ poetry run uvicorn src.index:app --reload








# [Deployment]
  $ cd project

  # [Zip]
  $ tar czf src.tar.gz src


  # Login to `deployment/hosting` server..
  # Now, navigate to your prefer location for eg => `/home/fognasy/python-proj`.
  $ mkdir dryutil
  $ cd dryutil
  # Upload, the below [files-or-dirs]..
  # eg => 
  [local-location=`/home/chist/Desktop/space/a/project/dryutil/backend/python/fastapi/project/`]
  [server-location=`/home/fognasy/python-proj/dryutil`]
  Hint: We can use `filezilla`
  /*
  src.tar.gz
  .env
  pyproject.toml
  */


  # now..
  # [UnZip]
  $ tar -xf src.tar.gz


  # install..
  $ poetry install --no-root



# [Deployment-run]
  # Outside src `path`..
  $ poetry env info --path
  `Sample-Output => /home/chist/.cache/pypoetry/virtualenvs/project-RM1810Px-py3.12 `
  # now, construct path like `/home/chist/.cache/pypoetry/virtualenvs/project-RM1810Px-py3.12` + `/bin/uvicorn`
  $ pm2 start '/home/chist/.cache/pypoetry/virtualenvs/project-RM1810Px-py3.12/bin/uvicorn src.index:app'  --name  "dryutilFastapi" && pm2 save && pm2 startup && pm2 save
  





# [list-package]
  $ npm list --depth=0





# Configure `Reverse-proxy` [Apache2]
  $ nano /etc/apache2/sites-available/nodeapp.conf
   


  /* [ref] https://socket.io/docs/v3/reverse-proxy/#apache-httpd
  <VirtualHost *:443>
    ServerName fastapi.dryutil.1mn.io


    ProxyPreserveHost On
    RewriteEngine On


    SSLEngine On
    SSLCertificateFile "/etc/letsencrypt/live/fastapi.dryutil.1mn.io/fullchain.pem"
    SSLCertificateKeyFile "/etc/letsencrypt/live/fastapi.dryutil.1mn.io/privkey.pem"



    # Upgrade connections to WebSockets
    ProxyPass / http://localhost:8000/
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:8000/$1" [P,L]
    
    
    
    # Redirect http to https
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

    # Everything else forwards as HTTP to the node app.
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/


  </VirtualHost>

  */








  $ a2ensite nodeapp.conf

  # [no-need-to-run] $ a2dissite 000-default 
  $ a2enmod proxy proxy_http rewrite headers expires
  $ systemctl restart apache2







