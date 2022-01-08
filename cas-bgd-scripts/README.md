# cas-bgd-scripts

#### Start with Docker
```
Root Folder:
    GitBash: cd /c/Users/Leoric/OneDrive/code/cas-bgd/cas-bgd-scripts
    WSL2: cd //mnt/c/Users/Leoric/OneDrive/code/cas-bgd/cas-bgd-scripts

Create k8s Secrets for 'confluent.config' AND 'Google Cloud' (Vision API) in folder '../cas-bgd-scripts/secrets/':
    ./create-secrets.sh
    kubectl describe secret img-secrets
    # Should contain: bgd-quickaccess.json & confluent.config

Create k8s Secrets in folder '../cas-bgd-chart/templates/secrets/':
    # Please make certain that these secrets exist AFTER running helm install:
    echo $(kubectl get secret redis-cloud-secrets -o jsonpath="{.data.image-labels}" | base64 --decode)
    echo $(kubectl get secret pexels-secrets -o jsonpath="{.data.token}" | base64 --decode)

Check k8s ConfigMap values from folder '../cas-bgd-chart/templates/cfg/':
    kubectl describe cm redis-cloud-cfg

Run:
    # Build
    helm dependency update cas-bgd-chart
    ./helm-start.sh -b
    
    # Run
    ./helm-start.sh

    # Stop
    ./helm-start.sh -h

    # Restart
    ./helm-start.sh -r

    # Docker exec into container
    ./helm-exec.sh

    # Build & Restart & k8s list
    ./helm-start.sh -b -r && k get all
```

#### Run components in dev environment (e.g., PyCharm)
```
Run img_label_processor:
    REDIS_HOST=cloud.redislabs.com ; REDIS_PORT=16666 ; REDIS_PASSWORD=<pw> ; \
        PEXEL_TOKEN=<secret token>
    python img_label_processor.py -v '../cas-bgd-scripts/secrets/bgd-recommender.json' \
            -f '../cas-bgd-scripts/secrets/confluent.config' -t 'user-events' -c '"index < 1"'
    
    OR the same in the container
    ./helm-exec.sh
    ./run-img-label-processor.sh -t \'user-events\' -c \'"index < 1"\'
```

