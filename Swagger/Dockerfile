FROM  swaggerapi/swagger-ui
COPY . ./
WORKDIR ./
EXPOSE 8080
COPY ./doc/Swagger.yml ./usr/share/nginx/html/doc/Swagger.yml
ENV API_URL doc/Swagger.yml
