# Just used in Landun + devcloud env for ci

source ./.bashrc
echo ">>> Python version : "
python -V

conda activate py385br

echo ">>> Python version : "
python -V

cd /data/dt4test/build_dt4test_ci
pwd

python -m pip install wheel
python -m pip install twine

echo ">> python setup.py sdist bdist_wheel ..."
python setup.py sdist bdist_wheel

echo ">> twine check dist/*"
python -m twine check dist/*

ls -al dist

cp dist/dt4test-*.tar.gz ./dt4test-release.tar.gz

ls -al ./

echo "You can upload this lib to Pypii with username mawentao : twine upload dist/* "
