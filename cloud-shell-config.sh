#!/bin/bash

# Use it with:
# eval "$(curl -fsSL https://vicenteherrera.com/cloud-shell-config.sh)"

# Set up aliases for kubectl
alias k='kubectl'

# Function to change the default namespace or list all namespaces
kns() {
    if [ -z "$1" ]; then
        current=$(kubectl config view --minify -o jsonpath='{..namespace}')
        current=${current:-default}

        echo "Available namespaces:"

        namespaces=$(kubectl get namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}')
        for ns in $namespaces; do
            if [ "$ns" == "$current" ]; then
                echo "* $ns (current)"
            else
                echo "  $ns"
            fi
        done
    else
        kubectl config set-context --current --namespace="$1"
        echo "Switched to namespace '$1'"
    fi
}

# Export the aliases and functions
export -f kns
