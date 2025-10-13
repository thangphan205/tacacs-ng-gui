#!/bin/sh

# Shared mount point inside the container (defined in docker-compose.yml)
SHARED_DIR="/opt/tacacs_shared_data"
CONFIG_FILE="$SHARED_DIR/etc/tac_plus-ng.cfg"
RELOAD_TRIGGER_FILE="$SHARED_DIR/restart_trigger.txt"

# 1. Ensure directories exist on the shared volume (for first run)
mkdir -p "$SHARED_DIR/etc"
mkdir -p "$SHARED_DIR/log"

# 2. Set permissive permissions for shared volume (crucial for R/W by FastAPI)
chmod -R 777 "$SHARED_DIR"

# 3. Check and create placeholder config file if it doesn't exist
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating placeholder config file: $CONFIG_FILE"
    echo "#!/usr/local/sbin/tac_plus-ng" > "$CONFIG_FILE"
    echo "id = spawnd { listen = { address = 0.0.0.0 port = 49 } }" >> "$CONFIG_FILE"
    echo "id = tac_plus-ng { log authenticationlog { destination = $SHARED_DIR/log/auth.log } }" >> "$CONFIG_FILE"
fi

# 4. Create initial reload trigger file (needed for the monitor to get a starting timestamp)
touch "$RELOAD_TRIGGER_FILE"

# --- Configuration Reload Monitor Function ---
# This function runs in the background and watches the trigger file
monitor_config_changes() {
    # Get initial timestamp of the trigger file
    LAST_CHANGE=$(stat -c %Y "$RELOAD_TRIGGER_FILE")
    echo "Starting configuration monitor. Initial timestamp: $LAST_CHANGE"

    while true; do
        sleep 5 # Check every 5 seconds
        CURRENT_CHANGE=$(stat -c %Y "$RELOAD_TRIGGER_FILE")

        if [ "$CURRENT_CHANGE" -gt "$LAST_CHANGE" ]; then
            echo "Configuration change detected! Sending SIGHUP to tac_plus-ng process."
            
            # Send SIGHUP to the master process to restart/reload the configuration
            if killall -HUP tac_plus-ng; then
                echo "SIGHUP sent successfully. Configuration should be reloading..."
            else
                echo "Warning: Could not send SIGHUP. tac_plus-ng might not be running yet."
            fi

            # Update the timestamp
            LAST_CHANGE="$CURRENT_CHANGE"
        fi
    done
}

# 5. Start the monitor in the background
monitor_config_changes &

# 6. Start the tac_plus-ng daemon in foreground mode (-f)
echo "Starting tac_plus-ng daemon..."
# 'exec' replaces the current shell process with tac_plus-ng, keeping the container alive
exec /usr/local/sbin/tac_plus-ng -f "$CONFIG_FILE"
