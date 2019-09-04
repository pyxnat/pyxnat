python setup.py build_sphinx
rm -rf /tmp/html
mv build/sphinx/html /tmp

TARGET_REPO="$TRAVIS_REPO_SLUG"
GITHUB_REPO=https://${GH_TOKEN}@github.com/${TARGET_REPO}.git

git clone "$GITHUB_REPO" &> /dev/null
git checkout --orphan gh-pages
git rm --cached -r .
git config --local user.name "Travis CI"
git config --local user.email "travis@travis-ci.org"

git remote rm origin
# Add new "origin" with access token in the git URL for authentication
git remote add origin $GITHUB_REPO > /dev/null 2>&1

mv /tmp/html/*  .
touch .nojekyll
curl "https://raw.githubusercontent.com/pyxnat/pyxnat/master/pyxnat.ico" -o _static/pyxnat.ico
git add --all
git commit -m 'Update documentation'
git push origin gh-pages --force
