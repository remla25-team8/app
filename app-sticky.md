# App Repository README

## Assignment 5: Istio Service Mesh (Member 1 Contributions)

This repository contains the *Restaurant Sentiment Analysis* web application, serving as the frontend and API service. For Assignment 5, Member 1 modified the application to support **Traffic Management** requirements at the **Excellent** level, specifically Sticky Sessions and version consistency, while preserving existing functionality (Prometheus metrics, Swagger, feedback endpoint).

### Changes Made

1. **Sticky Sessions Support**:
   - Updated `app.py` in the `/analyze` route to parse the `x-user-id` header from incoming requests and forward it to `model-service` via the `/predict` endpoint.
   - Added logging for `x-user-id` to debug Istio Sticky Sessions routing.
   - Updated Swagger documentation to include the `x-user-id` header parameter.

2. **Version Consistency**:
   - Updated `requirements.txt` to ensure `lib-ml==1.19.0` and `lib-version==0.9.5` match `model-service` (versions assumed; confirm with A1).

### Testing Instructions

1. **Prerequisites**:
   - Deploy the Helm chart from the `operation` repository:
     ```bash
     helm install my-app ./helm/myapp -n default
     ```
   - Verify `MODEL_SERVICE_URL` is set to `http://model-service:8080` in the Helm ConfigMap.
   - Add `192.168.56.90 app.local` to `/etc/hosts` (local or Vagrant host).
   - Ensure `app` v2 image (`ghcr.io/remla25-team8/app:2.0.0`) is available.

2. **Automated Testing**:
   - Use the test script from the `operation` repository:
     ```bash
     bash helm/myapp/tests/sticky-session-test.sh
     ```
   - **Expected Output**:
     - First loop: ~90% v1 (`1.1.4`), ~10% v2 (`2.0.0`) responses.
     - Second loop: All `x-user-id: test-user` requests route to v2.

3. **Manual Testing**:
   ```bash
   # Test default routing
   curl -H "Host: app.local" http://192.168.56.90/analyze -d '{"review": "Great food!"}' -H "Content-Type: application/json"
   
   # Test Sticky Sessions
   curl -H "Host: app.local" -H "x-user-id: test-user" http://192.168.56.90/analyze -d '{"review": "Great food!"}' -H "Content-Type: application/json"
   ```
   - **Expected Output**: JSON response with `sentiment`, `confidence`, `processed_review`. For `x-user-id: test-user`, expect v2 routing (verify via response differences or logs).

### Verification Methods

1. **Sticky Sessions**:
   - Check logs: `kubectl logs -l app.kubernetes.io/name=myapp -n default` (look for `Received request with x-user-id: test-user`).
   - Confirm `x-user-id: test-user` requests consistently route to v2 (check response or coordinate with team for v2-specific markers).

2. **Version Consistency**:
   - Compare `requirements.txt` with `model-service/requirements.txt` to confirm `lib-ml==1.19.0` and `lib-version==0.9.5`.
   - Run `kubectl exec -it <app-pod> -n default -- pip list` to verify installed versions.

3. **Functionality**:
   - Test endpoints: Ensure `/`, `/info`, `/analyze`, and `/feedback` work as before.
   - Verify `x-user-id` is forwarded to `model-service` (check `model-service` logs).
   - Confirm Prometheus metrics are intact: `curl http://<app-pod>:8080/metrics`.

If the endpoint fails or routing is inconsistent, check Flask logs or the Istio VirtualService in the `operation` repository.