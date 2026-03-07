#!/bin/bash
# OPTIONAL: Ethernet toggle for direct GPU server connection
#
# Switches between static IP (direct server connection) and DHCP (router/internet).
#
# ⚠️  NEVER use `networksetup` — it resets the entire network stack,
#     killing gateway, Telegram, and LLM connections.
#     Use `ipconfig set` instead — changes only the target interface.
#
# Usage:
#   ./switch-ethernet.sh        # Interactive: prompts for mode
#   ./switch-ethernet.sh static  # Direct server connection
#   ./switch-ethernet.sh dhcp    # Router/internet mode

INTERFACE="<INTERFACE_NAME>"      # e.g., en5
STATIC_IP="<STATIC_IP>"          # e.g., 10.0.0.1
SUBNET="255.255.255.0"
SERVER_IP="<SERVER_IP>"           # e.g., 10.0.0.2
SUDO_PASS="<SUDO_PASSWORD>"

MODE="${1}"

if [ -z "$MODE" ]; then
    echo "Select mode:"
    echo "  1) Static (direct server connection: $STATIC_IP → $SERVER_IP)"
    echo "  2) DHCP (router/internet)"
    read -p "Choice [1/2]: " choice
    case "$choice" in
        1) MODE="static" ;;
        2) MODE="dhcp" ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
fi

case "$MODE" in
    static)
        echo "Switching $INTERFACE to static: $STATIC_IP"
        echo "$SUDO_PASS" | sudo -S ipconfig set "$INTERFACE" MANUAL "$STATIC_IP" "$SUBNET"
        echo "Testing connection to server ($SERVER_IP)..."
        sleep 2
        if ping -c 1 -W 2 "$SERVER_IP" > /dev/null 2>&1; then
            echo "✅ Server reachable at $SERVER_IP"
        else
            echo "⚠️  Server not reachable. Check cable and server config."
        fi
        ;;
    dhcp)
        echo "Switching $INTERFACE to DHCP"
        echo "$SUDO_PASS" | sudo -S ipconfig set "$INTERFACE" DHCP
        echo "✅ DHCP mode active"
        ;;
    *)
        echo "Usage: $0 [static|dhcp]"
        exit 1
        ;;
esac
