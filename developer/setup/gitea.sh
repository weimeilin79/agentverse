#!/bin/bash

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# --- Gitea Instance Settings ---
GITEA_CONTAINER_NAME="my-gitea-container"
HOST_GITEA_WEB_PORT=3005
HOST_GITEA_SSH_PORT=2222
GITEA_DATA_PATH="${PWD}/gitea-data"

# --- Gitea MCP Instance Settings ---
MCP_CONTAINER_NAME="my-gitea-mcp-container"
HOST_MCP_WEB_PORT=8085
MCP_IMAGE="gitea/gitea-mcp-server:0.3.0"

# --- Shared Settings ---
DOCKER_NETWORK_NAME="gitea-network"

# --- Admin User (used for token generation) ---
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
ADMIN_EMAIL="admin@example.com"

# --- Regular User ---
NEW_USER="dev"
NEW_USER_PASSWORD="dev"
NEW_USER_EMAIL="dev@example.com"

# ==============================================================================
# SCRIPT LOGIC
# ==============================================================================

echo " Gitea & Gitea-MCP (Hybrid Config) Full Setup Script"
echo "-----------------------------------------------------"
echo

# --- Step 0: Clean Up and Network Setup ---
echo "STEP 0: Cleaning up previous runs and setting up network..."
if [ "$(docker ps -a -q -f name=^/${MCP_CONTAINER_NAME}$)" ]; then
    docker stop "${MCP_CONTAINER_NAME}"
    docker rm "${MCP_CONTAINER_NAME}"
fi
if [ "$(docker ps -a -q -f name=^/${GITEA_CONTAINER_NAME}$)" ]; then
    docker stop "${GITEA_CONTAINER_NAME}"
    docker rm "${GITEA_CONTAINER_NAME}"
fi
docker network create "${DOCKER_NETWORK_NAME}" || true
mkdir -p "${GITEA_DATA_PATH}"
echo "Cleanup and network setup complete."
echo

# --- Step 1: Deploy Gitea Container ---
echo "STEP 1: Starting the main Gitea container..."
docker run \
    -d \
    --name "${GITEA_CONTAINER_NAME}" \
    --network "${DOCKER_NETWORK_NAME}" \
    -p "${HOST_GITEA_WEB_PORT}:3000" \
    -p "${HOST_GITEA_SSH_PORT}:22" \
    -v "${GITEA_DATA_PATH}:/data" \
    --restart=always \
    gitea/gitea:latest

echo "Container started. Waiting for it to create initial files..."
sleep 15

# --- Step 2: Get Cloud Shell URL ---
echo; echo "STEP 2: Getting the public Cloud Shell URL..."
if ! command -v cloudshell &> /dev/null; then
    GITEA_ROOT_URL="http://localhost:${HOST_GITEA_WEB_PORT}/"
else
    GITEA_ROOT_URL=$(cloudshell get-web-preview-url -p "${HOST_GITEA_WEB_PORT}")
fi
echo "--> Detected URL: ${GITEA_ROOT_URL}"

# --- Step 3: Update Config File ---
echo; echo "STEP 3: Modifying the configuration file inside the Gitea container..."
CONFIG_FILE_PATH="/data/gitea/conf/app.ini"
docker exec "${GITEA_CONTAINER_NAME}" sed -i "s|^ROOT_URL\s*=\s*.*|ROOT_URL = ${GITEA_ROOT_URL}|" "${CONFIG_FILE_PATH}"
if ! docker exec "${GITEA_CONTAINER_NAME}" grep -q "\[security\]" "${CONFIG_FILE_PATH}"; then
    docker exec "${GITEA_CONTAINER_NAME}" sh -c "echo -e '\n[security]' >> ${CONFIG_FILE_PATH}"
fi
docker exec "${GITEA_CONTAINER_NAME}" sed -i "/\[security\]/a INSTALL_LOCK = true" "${CONFIG_FILE_PATH}"
echo "Configuration updated."

# --- Step 4: Restart Gitea and Wait for Health Check ---
echo; echo "STEP 4: Restarting Gitea and waiting for it to be ready..."
docker restart "${GITEA_CONTAINER_NAME}"
echo "--> Waiting for Gitea API to come online..."
ATTEMPTS=0
MAX_ATTEMPTS=30
until [ "$(docker exec "${GITEA_CONTAINER_NAME}" curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/v1/version)" = "200" ]; do
    if [ ${ATTEMPTS} -eq ${MAX_ATTEMPTS} ]; then
        echo "Error: Gitea did not become healthy in time. Check logs with 'docker logs ${GITEA_CONTAINER_NAME}'"
        exit 1
    fi
    ATTEMPTS=$((ATTEMPTS+1))
    printf "."
    sleep 2
done
echo " Gitea API is online!"

# --- Step 5: Create Users ---
echo; echo "STEP 5: Creating Gitea users..."
docker exec -u git "${GITEA_CONTAINER_NAME}" gitea admin user create \
    --username "${ADMIN_USER}" \
    --password "${ADMIN_PASSWORD}" \
    --email "${ADMIN_EMAIL}" \
    --admin \
    --must-change-password=false || echo "--> Admin user '${ADMIN_USER}' likely already exists. Continuing..."

docker exec -u git "${GITEA_CONTAINER_NAME}" gitea admin user create \
    --username "${NEW_USER}" \
    --password "${NEW_USER_PASSWORD}" \
    --email "${NEW_USER_EMAIL}" \
    --must-change-password=false || echo "--> Regular user '${NEW_USER}' likely already exists. Continuing..."

# --- Step 6: Generate Access Token for MCP ---
echo; echo "STEP 6: Generating a unique access token for user '${NEW_USER}'..."
MCP_TOKEN_NAME="gitea-mcp-token-$(date +%s)"
GITEA_MCP_TOKEN=$(docker exec -u git "${GITEA_CONTAINER_NAME}" gitea admin user generate-access-token \
    --username "${NEW_USER}" \
    --token-name "${MCP_TOKEN_NAME}" \
    --scopes "all" | awk '{print $NF}' | tr -d '\r')

if [ -z "$GITEA_MCP_TOKEN" ]; then
    echo "Error: Failed to generate Gitea access token. Please check Gitea logs."
    exit 1
fi
echo "--> Successfully parsed token for user '${NEW_USER}': ${GITEA_MCP_TOKEN}"

# --- Step 7: Start Gitea-MCP Container ---
echo; echo "STEP 7: Starting the Gitea-MCP container with a hybrid configuration..."
GITEA_INTERNAL_URL="http://${GITEA_CONTAINER_NAME}:3000"

# Using the requested hybrid of environment variable for token and flags for other settings.
# The --entrypoint flag is CRITICAL to prevent the "executable file not found" error.
docker run \
    -d \
    --name "${MCP_CONTAINER_NAME}" \
    --network "${DOCKER_NETWORK_NAME}" \
    -p "${HOST_MCP_WEB_PORT}:8080" \
    --restart=always \
    -e GITEA_ACCESS_TOKEN="${GITEA_MCP_TOKEN}" \
    --entrypoint "/app/gitea-mcp" \
    "${MCP_IMAGE}" \
    -host "${GITEA_INTERNAL_URL}" \
    -transport "sse" \
    -insecure

# --- Final Output ---
echo
echo "-----------------------------------------------------"
echo " SCRIPT COMPLETE! ALL SERVICES ARE READY!"
echo
echo " >> Main Gitea Web UI: ${GITEA_ROOT_URL}"
echo " >> Gitea-MCP Web UI:  (Preview on port ${HOST_MCP_WEB_PORT} in Cloud Shell)"
echo
echo " >> Admin User:        '${ADMIN_USER}' / '${ADMIN_PASSWORD}'"
echo " >> Regular User:      '${NEW_USER}' / '${NEW_USER_PASSWORD}'"
echo
echo " >> Data is stored in: ${GITEA_DATA_PATH}"
echo