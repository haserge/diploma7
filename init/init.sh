#!/bin/sh

result=1

until [ $result -eq 0 ]
do
  echo "Waiting for postgres..."	
  pg_isready -h $DATABASE_HOST
  result=$?
  sleep 1
done  

echo "Postgres on host $DATABASE_HOST is ready, running the migrations and starting backend..."

exec "$@"
