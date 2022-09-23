## python-order-utils Monorepo Contribution Guide

All contributions to the python-order-utils are welcome and greatly appreciated! This document serves to outline the process for contributions and help you get set up.

### Steps to get started

1. Fork 'Polymarket/python-order-utils'
2. Clone your fork
3. Follow the [installation instructions](./README.md) in the monorepo's top level README.
4. Open pull requests with the `[WIP]` flag against the `main` branch and include a description of the intended change in the PR description.

Before removing the `[WIP]` tag and submitting a PR for review, make sure that:

- it passes our linter checks
- the test suite passes for all packages
- it passes our continuous integration tests
- your fork is up to date with `main`

### Branch structure & naming

Our main branch, `main`, represents the current development state of the codebase. All pull requests should be opened against `main`.

Name your branch with the format `{fix | feat | refactor | chore }/{ description }`

- A `fix` addresses a bug or other issue
- A `feat` adds new functionality/interface surface area
- A `refactor` changes no business logic or interfaces, but improves implementation
- A `chore` addresses minor improvements or configuration changes

