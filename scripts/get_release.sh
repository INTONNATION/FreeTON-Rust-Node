VERSION=$1
REPO=$2
TOKEN=$3

if [ "$VERSION" = "latest" ]; then
  parser=".[0].assets[0].id"
else
  parser=".[] | select(.tag_name == \"ton-node-v-$VERSION\").assets[0].id"
fi;

asset_id=`curl -H "Authorization: token $TOKEN" H "Accept: application/vnd.github.v3.raw" -s https://api.github.com/repos/$REPO/releases | jq "$parser"`

wget -qO- --auth-no-challenge --header='Accept:application/octet-stream' https://$TOKEN:@api.github.com/repos/$REPO/releases/assets/$asset_id | tar xvz -C /usr/local/bin/
