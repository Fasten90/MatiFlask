if [ -d MatiFlask ]; then
    pushd MatiFlask
fi

git pull

touch ../MatiFlask.wsgi

popd
