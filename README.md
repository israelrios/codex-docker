# codex-docker

`codex-docker` starts an ephemeral Docker container in the current shell directory and launches Codex automatically in yolo mode.

## Behavior

- Installs the Docker CLI in the image.
- Uses the current shell `PWD` as the container working directory.
- Maps the current directory into the container at the same absolute path.
- Maps `~/.codex` into the container at the same absolute path.
- Maps each existing path listed in `sandbox_workspace_write.writable_roots` from `~/.codex/config.toml`.
- Forwards the invoking shell environment into the container, excluding keys matched by `vars-to-ignore.txt`.
- Forwards the invoking shell's current `PATH` and prepends it to the image `PATH`.
- Maps directory paths referenced by those forwarded variables when they exist on the host, excluding paths under `/usr` and `/var`.
- Reuses the host CA trust store by bind-mounting the host certificate paths read-only.
- Leaves host Docker integration disabled by default.
- `--docker` bind-mounts the host Docker socket into the container when available and adds the socket group when needed so the in-container Docker CLI can talk to the host daemon.
- Uses Docker host network mode.
- Runs the container with the invoking user UID and GID.
- Starts `codex --dangerously-bypass-approvals-and-sandbox` automatically.

Missing writable roots are skipped with a warning so a stale path in `config.toml` does not break the launcher.

## Usage

Build and run automatically:

```bash
./codex-docker
```

Forward extra Codex CLI arguments:

```bash
./codex-docker -- --model gpt-5.4 --search
```

Enable host Docker access inside the container:

```bash
./codex-docker --docker
```

Print the generated Docker command:

```bash
./codex-docker --print-command
```

Print the command without running anything:

```bash
./codex-docker --dry-run
```

Force an image rebuild:

```bash
./codex-docker --rebuild
```
