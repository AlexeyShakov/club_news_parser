FROM rabbitmq:3-management-alpine
RUN apk update && apk add curl
