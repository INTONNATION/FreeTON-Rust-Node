TOKEN=$4
REPO=$3
FILE=$1
VERSION=$2              
GITHUB="https://api.github.com"

if [ "$VERSION" = "latest" ]; then
  parser=".[0].assets | map(select(.name == \"$FILE\"))[0].id"
else
  parser=". | map(select(.tag_name == \"$VERSION\"))[0].assets | map(select(.name == \"$FILE\"))[0].id"
fi;

asset_id=`curl -H "Authorization: token $TOKEN" H "Accept: application/vnd.github.v3.raw" -s $GITHUB/repos/$REPO/releases | jq "$parser"`

wget -q --auth-no-challenge --header='Accept:application/octet-stream' \
  https://$TOKEN:@api.github.com/repos/$REPO/releases/assets/$asset_id \
  -O $2
