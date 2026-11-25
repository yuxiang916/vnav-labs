#!/usr/bin/env bash
set -eo pipefail
package_root="$(cd "$(dirname "$0")/.." && pwd)"
workspace="$HOME/lab4_ws"
mkdir -p "$workspace/src" "$HOME/lab4-results"
for package in controller_pkg planner_pkg trajectory_generation_pkg; do
    if [ -e "$workspace/src/$package" ]; then
        echo "Workspace package already exists: $workspace/src/$package" >&2
        exit 1
    fi
done
for package in controller_pkg planner_pkg trajectory_generation_pkg; do
    cp -R "$package_root/$package" "$workspace/src/"
done
tar -xzf "$package_root/dependencies/lab4-dependencies.tar.gz" -C "$workspace/src"
tar -xzf "$package_root/dependencies/lab4-bridge.tar.gz" -C "$workspace/src"
python3 "$package_root/tools/prepare_workspace.py"
cp "$package_root/tools/"*.py "$HOME/lab4-results/"
cp "$package_root/tools/race.rviz" "$HOME/lab4-results/"
bash "$package_root/tools/build.sh"
