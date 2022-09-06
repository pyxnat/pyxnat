python setup.py build_sphinx
rm -rf /tmp/html
mv build/sphinx/html /tmp

GITHUB_REPO=https://${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git

git clone "$GITHUB_REPO" &> /dev/null
git checkout --orphan gh-pages
git rm --cached -r .
git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"

git remote rm origin
# Add new "origin" with access token in the git URL for authentication
git remote add origin $GITHUB_REPO > /dev/null 2>&1

mv /tmp/html/*  .
touch .nojekyll
curl "https://raw.githubusercontent.com/pyxnat/pyxnat/master/pyxnat.ico" -o _static/pyxnat.ico
git add --all
git commit -m 'Update documentation'
git push origin gh-pages --force
