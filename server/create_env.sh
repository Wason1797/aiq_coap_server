rm .env
touch .env
echo "POSTGRESQL_DB_URL=$POSTGRESQL_DB_URL" >>.env
echo "MYSQL_DB_URL=$MYSQL_DB_URL" >>.env
echo "ALLOWED_BOT_USERS=$ALLOWED_BOT_USERS" >>.env
echo "BOT_TOKEN=$BOT_TOKEN" >>.env
echo "SECRET_KEY=$SECRET_KEY" >>.env
echo "STATION_TYPE=$STATION_TYPE" >>.env
echo "VERSION=$VERSION" >>.env
echo "ENV=$ENV" >>.env
