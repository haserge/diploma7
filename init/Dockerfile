FROM alpine:3.14
RUN apk add --no-cache postgresql-client
WORKDIR /code
COPY init.sh .
RUN chmod +x /code/init.sh
CMD ["./init.sh"]
