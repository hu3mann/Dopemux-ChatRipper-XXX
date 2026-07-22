# `dopemux` CLI

The `dopemux` executable wires the orchestration CLI to the new session factory. It currently exposes a single `start` command.

## `dopemux start`

Start a Dopemux session. The command now routes the legacy `--alt-routing` flag, and the new `--mobile` alias, to the "happy"
mobile-control session.

```bash
$ dopemux start --alt-routing
```

Outputs a confirmation showing the "happy (mobile-control)" session and the router in use.

### Options

- `--alt-routing`
  - Legacy flag that now maps directly to the mobile-control session. A warning is printed to highlight the new behaviour.
- `--mobile`
  - Preferred alias for the mobile-control session. Safe to use in CI or automation.
- `--profile-overlay PATH`
  - Optional JSON document that overlays additional metadata onto the session profile. The loader expects UTF-8 encoded JSON.

### Mobile control router guardrails

The mobile-control session uses the `MobileControlRouter`, which applies an allow-list and confirmation guard to keep automated
workflows push-safe. Operations such as `open_app`, `home`, and `type_text` require guard confirmation before they dispatch.
Disallowed actions raise a `RoutingError`.
