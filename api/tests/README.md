To run api tests:

```
conda env create -f api/environment.yml
export MONGO_URL=mongodb://localhost:27017
export MONGO_DB_NAME='eotdl-test'
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus
mkdir -p $PROMETHEUS_MULTIPROC_DIR
make test
```

In separate terminal
```
conda activate test-eotdl-api
PYTHONPATH=. pytest api/tests/unit/datasets/test_deactivate_dataset.py
```
