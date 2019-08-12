python setup.py build_sphinx
export COMMITTER_EMAIL="$(git log -1 --pretty="%cE")"
export AUTHOR_NAME="$(git log -1 --pretty="%aN")"
export INITIAL_COMMIT="$(git rev-list HEAD | tail -n 1)"
echo $COMMITTER_EMAIL
echo $AUTHOR_NAME

rm -rf /tmp/html
mv build/sphinx/html /tmp
git config --local user.name $AUTHOR_NAME
git config --local user.email $COMMITTER_EMAIL
git checkout gh-pages
git reset --hard $INITIAL_COMMIT # back to the initial commit
git push origin gh-pages --force
rm -r *
mv /tmp/html/*  .
touch .nojekyll
curl "https://raw.githubusercontent.com/xgrg/pyxnat/nosetests/pyxnat.png" -o _static/pyxnat.png
git add --all
git commit -m 'Update documentation'
git push origin gh-pages
