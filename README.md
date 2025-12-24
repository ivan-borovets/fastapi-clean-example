# Overview

📘 This FastAPI-based project and its documentation represent a practical interpretation of Clean Architecture and
Command Query Responsibility Segregation (CQRS) principles with elements of Domain-Driven Design (DDD).
Although it's not meant to serve as a comprehensive reference or a strict application of these methodologies, the
project demonstrates how their core ideas can be effectively put into practice in Python.
If they're new to you, refer to the [Useful Resources](#useful-resources) section.

# Table of contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
    1. [Introduction](#introduction)
    2. [Layered Approach](#layered-approach)
    3. [Dependency Rule](#dependency-rule)
        1. [Note on Adapters](#note-on-adapters)
    4. [Layered Approach Continued](#layered-approach-continued)
    5. [Dependency Inversion](#dependency-inversion)
    6. [Dependency Injection](#dependency-injection)
    7. [CQRS](#cqrs)
3. [Project](#project)
    1. [Dependency Graphs](#dependency-graphs)
    2. [Structure](#structure)
    3. [Technology Stack](#technology-stack)
    4. [API](#api)
        1. [General](#general)
        2. [Account](#account-apiv1account)
        3. [Users](#users-apiv1users)
    5. [Configuration](#configuration)
        1. [Files](#files)
        2. [Flow](#flow)
        3. [Local Environment](#local-environment)
        4. [Other Environments](#other-environments-devprod)
        5. [Adding New Environments](#adding-new-environments)
4. [Useful Resources](#useful-resources)
5. [Support the Project](#-support-the-project)
6. [Acknowledgements](#acknowledgements)

# Architecture Principles

## Introduction

This repository may be helpful for those seeking backend implementation in Python that is both framework-agnostic
and storage-agnostic (unlike Django).
Such flexibility can be achieved by using a web framework that doesn't impose strict software design (like FastAPI) and
applying a layered architecture patterned after the one proposed by Robert Martin, which we'll explore further.

The original explanation of Clean Architecture concepts can be
found [here](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
If you're still wondering why Clean Architecture matters, read the article — it only takes about 5 minutes.
In essence, it’s about making your application independent of external systems and highly testable.

<p align="center">
  <img src="docs/Robert_Martin_CA.png" alt="Clean Architecture Diagram" />
  <br><em>Figure 1: <b>Robert Martin's</b> Clean Architecture Diagram</em>
</p>

> "A computer program is a detailed description of the **policy** by which inputs are transformed into outputs."
>
> — Robert Martin

The most abstract policies define core business rules, while the least abstract ones handle I/O operations.
Being closer to implementation details, less abstract policies are more likely to change.
**Layer** represents a collection of components expressing policies at the same level of abstraction.

Concentric circles represent boundaries between different layers.
The meaning of arrows in the diagram will be discussed [later](#dependency-rule).
For now, we will focus on the purpose of the layers.

## Layered Approach

![#gold](https://placehold.co/15x15/gold/gold.svg) **Domain Layer**

- **Domain model** is a set of concepts, rules and behaviors that define what business (context) is and how it operates.
  It is expressed in **ubiquitous language** — consistent terminology shared by developers and domain experts.
  Domain layer implements domain model in code; this implementation is often called domain model.
- The strictest domain rules are **invariants** — conditions that must always hold true for the model.
  Enforcing invariants means maintaining data consistency in the model.
  This can be achieved through **encapsulation**, which hides internal state and couples data with behavior.
- Building blocks of domain model are (not limited to these):
    - **value objects** — smart business types (no identity, immutable, equal by value).
    - **entities** — business objects (have identity and lifecycle, equal by identity).
    - **domain services** — containers for behavior that has no place in the components above.
- Other domain model building blocks, unused in this project but important for deeper DDD:
    - **aggregates** — clusters of entities (1+) that must change together as a single unit,
      managed exclusively through their root, defining boundaries of transactional consistency.
    - **repositories** — abstractions emulating collections of aggregate roots.
- Domain model lies on a spectrum from anemic to rich.
    - **anemic** — simple data types, entities are just data holders, rules and behaviors live outside.
    - **rich** — value objects and entities encapsulate data and rules;
      invariants are enforced internally, so the model itself prevents invalid states.
      For components: anemic means no behavior within, rich — the contrary.
- Domain services originally represent operations that don't naturally belong to a specific entity or value object.
  But in projects with anemic entities, they can also contain logic that would otherwise be in those entities.
- In early stages of development when the domain model is not yet clearly defined,
  I'd recommend keeping entities flat and anemic, even though the latter weakens encapsulation.
  Once domain logic is well established, some entities can, as aggregate roots, become non-flat and rich.
  This best enforces invariants but can be tricky to design once and for all.
- Prefer rich value objects early, freeing entities and services from an excessive burden of local rules.
- Consider domain layer the most important, stable, and independent part of a system.

![#red](https://placehold.co/15x15/red/red.svg) **Application Layer**

- Business defines **use case** as specification of observable behavior that delivers value by achieving a goal.
- Within use case, the behavior is enacted by **actor** — possibly a client of the software system.
- Actor performs use case in steps, some of which require interaction with the system.
  These stepwise interactions with the system are handled at the application layer by **interactors**.
  In other words, each interactor handles a single business operation matching a step within use case.
- Interactors are stateless and cannot call each other, unlike use cases.
  Each is invoked independently - typically by external drivers such as HTTP controllers, message consumers, or
  scheduled jobs.
- Interactor orchestrates domain logic and external calls needed to perform the operation.
  Its primary responsibilities may include permission verification and transaction management.
  To access external systems, interactors rely on **interfaces (ports)** that abstract infrastructure details.
- Interactor uses **DTOs (Data Transfer Objects)** to exchange serializable data with external layers.
  These are simple, behavior-free carriers - the cross-layer transport for external contracts.
- If logic is reused across interactors: extract an application service when it falls under typical interactor
  responsibilities; otherwise, consider evolving the domain model to include it.
  Such evolution is a normal part of model enrichment.
- Together, domain and application layers form the **core** of the system.

![#green](https://placehold.co/15x15/green/green.svg) **Infrastructure Layer**

- This layer is responsible for adapting the core to external systems.
- It consists of **adapters**: driving and driven.
  Driving adapters call into the core, translating external requests into interactor calls.
  Driven adapters (port implementations) are called by the core via ports, allowing the core to interact with external
  systems (databases, APIs, file systems, etc.) while keeping the business logic decoupled.
- Related adapter logic can be grouped into **infrastructure service**.

> [!IMPORTANT]
> - Clean Architecture doesn't prescribe any particular number of layers.
    The key is to follow the Dependency Rule, which is explained in the next section.

## Dependency Rule

A dependency occurs when one software component relies on another to operate.
If you were to split all blocks of code into separate modules, dependencies would manifest as imports between those
modules.
Typically, dependencies are graphically depicted in UML style in such a way that

> [!IMPORTANT]
> - `A -> B` (**A points to B**) means **A depends on B**.

The key principle of Clean Architecture is the **Dependency Rule**.
This rule states that **more abstract software components must not depend on more concrete ones.**
In other words, dependencies must never point outwards.

> [!IMPORTANT]
> - Domain and application layers may import external tools and libraries to the extent necessary for describing
    business logic - those that extend the programming language's capabilities (math/numeric utilities, time zone
    conversion, object modeling, etc.). This trades some core stability for clarity and expressiveness. What is not
    acceptable are dependencies that bind business logic to implementation details (including frameworks) or to
    out-of-process systems (databases, brokers, file systems, cloud SDKs, etc.).
>
> - Components within the same layer **can depend on each other.** For example, components in the Infrastructure layer
    can interact with one another without crossing into other layers.
>
> - Components in any outer layer can depend on components in any inner layer, not necessarily the one closest to
    them. For example, components in the Presentation layer can directly depend on the Domain layer, bypassing the
    Application and Infrastructure layers.
>
> - Avoid letting business logic leak into peripheral details, such as raising business-specific exceptions in the
    Infrastructure layer without re-raising them in the business logic or declaring domain rules outside the Domain
    layer.
>
> - In specific cases where database constraints enforce business rules, the Infrastructure layer may raise
    domain-specific exceptions, such as `UsernameAlreadyExistsError` for a `UNIQUE CONSTRAINT` violation.
    Handling these exceptions in the Application layer ensures that any business logic implemented in adapters remains
    under control.
>
> - Avoid introducing elements in inner layers that specifically exist to support outer layers.
    For example, you might be tempted to place something in the Application layer that exists solely to support a
    specific piece of infrastructure.
    At first glance, based on imports, it might seem that the Dependency Rule isn't violated. However, in reality,
    you've broken the core idea of the rule by embedding infrastructure concerns (more concrete) into the business logic
    (more abstract).

### Note on Adapters

The **Infrastructure layer** in Clean Architecture acts as the adapter layer — connecting the application to
external systems.
In this project, we treat both **Infrastructure** and **Presentation** as adapters, since both adapt the application to
the outside world.
Speaking of dependencies direction, the diagram by R. Martin in Figure 1 can, without significant loss, be replaced by a
more concise and pragmatic one — where the adapter layer serves as a "bridge", depending both on the internal layers of
the application and external components.
This adjustment implies **reversing** the arrow from the blue layer to the green layer in R. Martin's diagram.

The proposed solution is a **trade-off**.
It doesn't strictly follow R. Martin's original concept but avoids introducing excessive abstractions with
implementations outside the application's boundaries.
Pursuing purity on the outermost layer is more likely to result in overengineering than in practical gains.

My approach retains nearly all advantages of Clean Architecture while simplifying real-world development.
When needed, adapters can be removed along with the external components they're written for, which isn't a
significant issue.

Let’s agree, for this project, to revise the principle:

Original:
> "Dependencies must never point outwards."

Revised:
> "Dependencies must never point outwards **within the core**."

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 10px; justify-items: center;">
  <img src="docs/onion_1.svg" alt="Revised Interpretation of CA-D" style="width: 400px; height: auto;" />
  <img src="docs/onion_2.svg" alt="Revised Interpretation of CA-D, alternative" style="width: 400px; height: auto;" />
</div>
<p align="center" style="font-size: 14px;">
  <em>Figure 2: <b>Revised Interpretation</b> of Clean Architecture<br>
  (diagrammed — original and alternative representation)
  </em>
</p>

## Layered Approach Continued

![#blue](https://placehold.co/15x15/blue/blue.svg) **Presentation Layer**

> [!NOTE]
> In the original diagram, the Presentation layer isn't explicitly distinguished and is instead included within the
> Interface Adapters layer. I chose to introduce it as a separate layer, marked in blue, as I see it as even more
> external compared to typical adapters.

- This layer handles external requests and includes **controllers** that validate inputs and pass them to the
  interactors in the Application layer. More abstract layers of the program assume that request data is already
  validated, allowing them to focus solely on their core logic.
- Controllers must be as thin as possible, containing no logic beyond basic input validation and routing. Their
  role is to act as an intermediary between the application and external systems (e.g., FastAPI).

> [!IMPORTANT]
> - **_Basic_** validation, like checking whether the structure of the incoming request matches the structure of the
    defined request model (e.g., type safety and required fields) should be performed by controllers at this layer,
    while **_business rule_** validation (e.g., ensuring the email domain is allowed, verifying the uniqueness of
    username, or checking if a user meets the required age) belongs to the Domain or Application layer.
> - Business rule validation often involves relationships between fields, such as ensuring that a discount applies only
    within a specific date range or a promotion code is valid for orders above a certain total.
> - **Carefully** consider using Pydantic for business rule validation. While convenient, Pydantic models are slower
    than regular dataclasses and reduce application core stability by coupling business logic to an external library.
> - If you choose Pydantic (or a similar tool bundled with web framework) for business model definitions, ensure that
    a Pydantic model in business layers is a separate model from the one in the Presentation layer, even if their
    structure appears identical. Mixing data presentation logic with business logic is a common mistake made early in
    development to save effort on creating separate models and field mapping, often due to not understanding that
    structural similarities are temporary.

![#gray](https://placehold.co/15x15/gray/gray.svg) **External Layer**

> [!NOTE]
> In the original diagram, external components are included in the blue layer (Frameworks & Drivers).
> I've marked them in gray to clearly distinguish them from layers within the application's boundaries.

- This layer represents fully external components such as web frameworks (e.g. FastAPI itself), databases, third-party
  APIs, and other services.
- These components operate outside the application’s core logic and can be easily replaced or modified without affecting
  the business rules, as they interact with the application only through the Presentation and Infrastructure layers.

<p align="center">
  <img src="docs/dep_graph_basic.svg" alt="Basic Dependency Graph" />
  <br><em>Figure 3: Basic Dependency Graph</em>
</p>

## Dependency Inversion

The **dependency inversion** technique enables reversing dependencies **by introducing an interface** between
components, allowing an inner layer to communicate with an outer layer while adhering to the Dependency Rule.

<p align="center">
  <img src="docs/dep_graph_inv_corrupted.svg" alt="Corrupted Dependency" />
  <br><em>Figure 4: <b>Corrupted</b> Dependency</em>
</p>

In this example, the Application component depends directly on the Infrastructure component, violating the Dependency
Rule.
This creates "corrupted" dependencies, where changes in the Infrastructure layer can propagate to and unintentionally
affect the Application layer.

<p align="center">
  <img src="docs/dep_graph_inv_correct.svg" alt="Correct Dependency" />
  <br><em>Figure 5: <b>Correct</b> Dependency</em>
</p>

In the correct design, the Application layer component depends on an **abstraction (port)**, and the Infrastructure
layer component **implements** the corresponding interface.
This makes the Infrastructure component an adapter for the port, effectively turning it into a plugin for
Application layer.
Such a design adheres to the **Dependency Inversion Principle (DIP)**, minimizing the impact of infrastructure changes
on core business logic.

## Dependency Injection

The idea behind **Dependency Injection** is that a component shouldn't create the dependencies it needs but rather
receive them.
From this definition, it's clear that one common way to implement DI is by passing dependencies as arguments to the
`__init__` method or functions.

But how exactly should these dependencies be initialized (and finalized)?

**DI frameworks** offer an elegant solution by automatically creating necessary objects (while managing their
**lifecycle**) and injecting them where needed.
This makes the process of dependency injection much cleaner and easier to manage.

<p align="center">
  <img src="docs/dep_graph_inv_correct_di.svg" alt="Correct Dependency with DI" />
  <br><em>Figure 6: <b>Correct</b> Dependency <b>with DI</b></em>
</p>

FastAPI provides a built-in **DI mechanism** called [Depends](https://fastapi.tiangolo.com/tutorial/dependencies/),
which tends to leak into different layers of the application. This creates tight coupling to FastAPI, violating the
principles of Clean Architecture, where the web framework belongs to the outermost layer and should remain easily
replaceable.

Refactoring the codebase to remove `Depends` when switching frameworks can be unnecessarily costly. It also has [other
limitations](https://dishka.readthedocs.io/en/stable/alternatives.html#why-not-fastapi) that are beyond the scope of
this README. Personally, I prefer [**Dishka**](https://dishka.readthedocs.io/en/stable/index.html) — a solution that
avoids these issues and remains framework-agnostic.

## CQRS

The project implements Command Query Responsibility Segregation (**CQRS**) — a pattern that separates read and write
operations into distinct paths.

- **Commands** (via interactors) handle write operations and business-critical reads using command gateways that work
  with entities and value objects.
- **Queries** are implemented through query services (similar contract to interactors) that use query gateways to fetch
  data optimized for presentation as query models.

This separation enables:

- Efficient read operations through specialized query gates, avoiding loading complete entity models.
- Performance optimization by tailoring data retrieval to specific view requirements.
- Flexibility to combine data from multiple models in read operations with minimal field selection.

# Project

## Dependency Graphs

<details>
  <summary>Application Controller - Interactor</summary>

  <p align="center">
  <img src="docs/application_controller_interactor.svg" alt="Application Controller - Interactor" />
  <br><em>Figure 7: Application Controller - Interactor</em>
  </p>

In the presentation layer, a Pydantic model appears when working with FastAPI and detailed information needs to be
displayed in OpenAPI documentation.
You might also find it convenient to validate certain fields using Pydantic;
however, be cautious to avoid leaking business rules into the presentation layer.

For request data, a plain `dataclass` is often sufficient.
Unlike lighter alternatives, it provides attribute access, which is more convenient for working in the application
layer.
However, such access is unnecessary for data returned to the client, where a `TypedDict` is sufficient (it's
approximately twice as fast to create as a dataclass with slots, with comparable access times).

</details>

<details>
  <summary>Application Interactor</summary>

  <p align="center">
  <img src="docs/application_interactor.svg" alt="Application Interactor" />
  <br><em>Figure 8: Application Interactor</em>
  </p>

</details>

<details>
  <summary>Application Interactor - Adapter</summary>

  <p align="center">
  <img src="docs/application_interactor_adapter.svg" alt="Application Interactor - Adapter" />
  <br><em>Figure 9: Application Interactor - Adapter</em>
  </p>

</details>

<details>
  <summary>Domain - Adapter</summary>

  <p align="center">
  <img src="docs/domain_adapter.svg" alt="Domain - Adapter" />
  <br><em>Figure 10: Domain - Adapter</em>
  </p>

</details>

<details>
  <summary>Infrastructure Controller - Handler</summary>
  <p align="center">
  <img src="docs/infrastructure_controller_handler.svg" alt="Infrastructure Controller - Handler" />
  <br><em>Figure 11: Infrastructure Controller - Handler</em>
  </p>

An infrastructure handler may be required as a temporary solution in cases where a separate context exists but isn't
physically separated into a distinct domain (e.g., not implemented as a standalone module within a monolithic
application).
In such cases, the handler operates as an application-level interactor but resides in the infrastructure layer.

Initially, I called these handlers interactors, but the community reacted very negatively to the idea of interactors in
the infrastructure layer, refusing to acknowledge that these essentially belong to another context.

In this application, such handlers include those managing user accounts, such as registration, login, and logout.

</details>

<details>
  <summary>Infrastructure Handler</summary>
  <p align="center">
  <img src="docs/infrastructure_handler.svg" alt="Infrastructure Handler" />
  <br><em>Figure 12: Infrastructure Handler</em>
  </p>

Ports in infrastructure are not commonly seen — typically, only concrete implementations are present.
However, in this project, since we have a separate layer of adapters (presentation) located outside the infrastructure,
ports are necessary to comply with the dependency rule.

</details>

<details>

**Identity Provider (IdP)** abstracts authentication details, linking the main business context with the authentication
context. In this example, the authentication context is not physically separated, making it an infrastructure detail.
However, it can potentially evolve into a separate domain.

  <summary>Identity Provider</summary>
  <p align="center">
  <img src="docs/identity_provider.svg" alt="Identity Provider" />
  <br><em>Figure 13: Identity Provider</em>
  </p>

Normally, IdP is expected to provide all information about current user.
However, in this project, since roles are not stored in sessions or tokens, retrieving them in main context was more
natural.

</details>

## Structure

```
.
├── config/...                                   # configuration files and scripts, includes Docker
├── Makefile                                     # shortcuts for setup and common tasks
├── scripts/...                                  # helper scripts
├── pyproject.toml                               # tooling and environment config (uv)
├── ...
└── src/
    └── app/
        ├── domain/                              # domain layer
        │   ├── services/...                     # domain layer services
        │   ├── entities/...                     # entities (have identity)
        │   │   ├── base.py                      # base declarations
        │   │   └── ...                          # concrete entities
        │   ├── value_objects/...                # value objects (no identity)
        │   │   ├── base.py                      # base declarations
        │   │   └── ...                          # concrete value objects
        │   └── ...                              # ports, enums, exceptions, etc.
        │
        ├── application/...                      # application layer
        │   ├── commands/                        # write ops, business-critical reads
        │   │   ├── create_user.py               # interactor
        │   │   └── ...                          # other interactors
        │   ├── queries/                         # optimized read operations
        │   │   ├── list_users.py                # query service
        │   │   └── ...                          # other query services
        │   └── common/                          # common layer objects
        │       ├── services/...                 # authorization, etc.
        │       └── ...                          # ports, exceptions, etc.
        │
        ├── infrastructure/...                   # infrastructure layer
        │   ├── adapters/...                     # port adapters
        │   ├── auth/...                         # auth context (session-based)
        │   └── ...                              # persistence, exceptions, etc.
        │
        ├── presentation/...                     # presentation layer
        │   └── http/                            # http interface
        │       ├── auth/...                     # web auth logic
        │       ├── controllers/...              # controllers and routers
        │       └── errors/...                   # error handling helpers
        │
        ├── setup/
        │   ├── ioc/...                          # dependency injection setup
        │   ├── config/...                       # app settings
        │   └── app_factory.py                   # app builder
        │  
        └── run.py                               # app entry point
```

## Technology Stack

- **Python**: `3.13`
- **Core**: `alembic`, `alembic-postgresql-enum`, `bcrypt`, `dishka`, `fastapi-error-map`, `fastapi`, `orjson`,
  `psycopg3[binary]`, `pyjwt[crypto]`, `sqlalchemy[mypy]`, `uuid-utils`, `uvicorn`, `uvloop`
- **Development**: `deptry`, `import-linter`, `mypy`, `pre-commit`, `ruff`, `slotscheck`
- **Testing**: `coverage`, `line-profiler`, `pytest`, `pytest-asyncio`

## API

<p align="center">
  <img src="docs/handlers.png" alt="Handlers" />
  <br><em>Figure 14: Handlers</em>
</p>

### General

- `/` (GET): Open to **everyone**.
    - Redirects to Swagger documentation.
- `/api/v1/health` (GET): Open to **everyone**.
    - Returns `200 OK` if the API is alive.

### Account (`/api/v1/account`)

- `/signup` (POST): Open to **everyone**.
    - Registers a new user with validation and uniqueness checks.
    - Passwords are peppered, salted, and stored as hashes.
    - A logged-in user cannot sign up until the session expires or is terminated.
- `/login` (POST): Open to **everyone**.
    - Authenticates registered user, sets a JWT access token with a session ID in cookies, and creates a session.
    - A logged-in user cannot log in again until the session expires or is terminated.
    - Authentication renews automatically when accessing protected routes before expiration.
    - If the JWT is invalid, expired, or the session is terminated, the user loses authentication. [^1]
- `/password` (PUT): Open to **authenticated users**.
    - The current user can change their password.
    - New password must differ from current password.
- `/logout` (DELETE): Open to **authenticated users**.
    - Logs the user out by deleting the JWT access token from cookies and removing the session from the database.

### Users (`/api/v1/users`)

- `/` (POST): Open to **admins**.
    - Creates a new user, including admins, if the username is unique.
    - Only super admins can create new admins.
- `/` (GET): Open to **admins**.
    - Retrieves a paginated list of existing users with relevant information.
- `/{user_id}/password` (PUT): Open to **admins**.
    - Admins can set passwords of subordinate users.
- `/{user_id}/roles/admin` (PUT): Open to **super admins**.
    - Grants admin rights to a specified user.
    - Super admin rights cannot be changed.
- `/{user_id}/roles/admin` (DELETE): Open to **super admins**.
    - Revokes admin rights from a specified user.
    - Super admin rights cannot be changed.
- `/{user_id}/activation` (PUT): Open to **admins**.
    - Restores a previously soft-deleted user.
    - Only super admins can activate other admins.
- `/{user_id}/activation` (DELETE): Open to **admins**.
    - Soft-deletes an existing user, making that user inactive.
    - Also deletes the user's sessions.
    - Only super admins can deactivate other admins.
    - Super admins cannot be soft-deleted.

> [!NOTE]
> - Super admin privileges must be initially granted manually (e.g., directly in the database), though the user
    account itself can be created through the API.

## Configuration

> [!WARNING]
> - This part of documentation is **not** related to the architecture approach.
> - Use any configuration method you prefer.

### Files

- **config.toml**: Main application settings organized in sections
- **export.toml**: Lists fields to export to .env (`export.fields = ["postgres.USER", "postgres.PASSWORD", ...]`)
- **.secrets.toml**: Optional sensitive data (same format as config.toml, merged with main config)

> [!IMPORTANT]
> - This project includes secret files for demonstration purposes only. In a real project, you **must** ensure that
    `.secrets.toml` and all `.env` files are not tracked by version control system to prevent exposing sensitive
    information. See this project's `.gitignore` for an example of how to properly exclude these sensitive files from
    Git.

### Flow

In this project I use my own configuration system based on TOML files as the single source of truth.
The system generates `.env` files for Docker and infrastructure components while the application reads settings directly
from the structured TOML files. More details are available at https://github.com/ivan-borovets/toml-config-manager

<p align="center">
  <img src="docs/toml_config_manager.svg" alt="Configuration flow" />
  <br><em>Figure 15: Configuration flow </em>
  <br><small>Here, the arrows represent usage flow, <b>not dependencies.</b></small>
</p>

### Local Environment

1. Configure local environment

* In this project, local configuration is already prepared in `config/local/`.  
  Nothing needs to be created — adjust files only if you want to change defaults.
* If you want to adjust settings, edit the existing TOML files in `config/local/` directly.  
  `.env.local` will be generated automatically — **don’t** create or edit it manually.
* Docker Compose in this project is already configured with `APP_ENV`.  
  Just keep in mind this variable if you change the setup:

```yaml
services:
  app:
    # ...
    environment:
      APP_ENV: ${APP_ENV}
```

2. Set environment variable

```shell
export APP_ENV=local
# export APP_ENV=dev
# export APP_ENV=prod
```

3. Check it and generate `.env`

```shell
# Probably you'll need Python 3.13 installed on your system to run these commands. 
# The next code section provides commands for its fast installation.
make env  # should print APP_ENV=local
make dotenv  # should tell you where .env.local was generated
```

4. Install `uv`

```shell
# sudo apt update
# sudo apt install pipx
# pipx ensurepath
# pipx install uv
# https://docs.astral.sh/uv/getting-started/installation/#shell-autocompletion
# uv python install 3.13  # To install Python
```

5. Set up virtual environment

```shell
uv sync --group dev
source .venv/bin/activate

# Alternatively,
# uv v
# source .venv/bin/activate  # on Unix
# .venv\Scripts\activate  # on Windows
# uv pip install -e . --group dev
```

Don't forget to tell your IDE where the interpreter is located.

Install pre-commit hooks:

```shell
# https://pre-commit.com/
pre-commit install
```

6. Launch

- To run only the database in Docker and use the app locally, use the following command:

    ```shell
    make up.db
    # make up.db-echo
    ```

- Then, apply the migrations:
    ```shell
    alembic upgrade head
    ```

- After applying the migrations, the database is ready, and you can launch the application locally (e.g., through your
  IDE). Remember to set the `APP_ENV` environment variable in your IDE's run configuration.

- To run via Docker Compose:

    ```shell
    make up
    # make up.echo
    ```

  In this case, migrations will be applied automatically at startup.

7. Shutdown

- To stop the containers, use:
    ```shell
    make down
    ```

### Other Environments (dev/prod)

1. Use the instructions about [local environment](#local-environment) above

* But make sure you've created similar structure in `config/dev` or `config/prod` with [files](#files):
    * `config.toml`
    * `.secrets.toml`
    * `export.toml`
    * `docker-compose.yaml` if needed
* `.env.dev` or `.env.prod` to be generated later — **don't** create them manually

### Adding New Environments

1. Add new value to `ValidEnvs` enum in `config/toml_config_manager.py` (and maybe in your app settings)
2. Update `ENV_TO_DIR_PATHS` mapping in the same file (and maybe in your app settings)
3. Create corresponding directory in `config/` folder
4. Add required configuration [files](#files)

Environment directories can also contain other env-specific files like `docker-compose.yaml`, which will be used by
Makefile commands.

# Useful Resources

## Layered Architecture

- [Robert C. Martin. Clean Architecture: A Craftsman's Guide to Software Structure and Design. 2017](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)

- [Alistair Cockburn. Hexagonal Architecture Explained. 2024](https://www.amazon.com/Hexagonal-Architecture-Explained-Alistair-Cockburn-ebook/dp/B0D4JQJ8KD)
  (introduced in 2005)

## Domain-Driven Design

- [Vlad Khononov. Learning Domain-Driven Design: Aligning Software Architecture and Business Strategy. 2021](https://www.amazon.com/Learning-Domain-Driven-Design-Aligning-Architecture/dp/1098100131)

- [Vaughn Vernon. Implementing Domain-Driven Design. 2013](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)

- [Eric Evans. Domain-Driven Design: Tackling Complexity in the Heart of Software. 2003](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)

- [Martin Fowler. Patterns of Enterprise Application Architecture. 2002](https://www.amazon.com/Patterns-Enterprise-Application-Architecture-Martin/dp/0321127420)

## Adjacent

- [Vladimir Khorikov. Unit Testing Principles. 2020](https://www.amazon.com/Unit-Testing-Principles-Practices-Patterns/dp/1617296279)

# ⭐ Support the Project

If you find this project useful, please give it a star or share it!
Your support means a lot.

👉 Check out the amazing [fastapi-error-map](https://github.com/ivan-borovets/fastapi-error-map), used here to enable
contextual, per-route error handling with automatic OpenAPI schema generation.

💬 Feel free to open issues, ask questions, or submit pull requests.

# Acknowledgements

I would like to express my sincere gratitude to the following individuals for their valuable ideas and support in
satisfying my curiosity throughout the development of this project:
[igoryuha](https://github.com/igoryuha),
[tishka17](https://github.com/tishka17),
[chessenjoyer17](https://github.com/chessenjoyer17),
[PlzTrustMe](https://github.com/PlzTrustMe),
[Krak3nDev](https://github.com/Krak3nDev),
[Ivankirpichnikov](https://github.com/Ivankirpichnikov),
[SamWarden](https://github.com/SamWarden),
[nkhitrov](https://github.com/nkhitrov),
[ApostolFet](https://github.com/ApostolFet),
Lancetnik, Sehat1137, Maclovi.

I also greatly appreciate the valuable insights shared by participants of the ASGI Community Telegram chat, despite
frequent and lively communication challenges, as well as the ⚗️ Reagento (adaptix/dishka)
[Telegram chat](https://t.me/reagento_ru) for their thoughtful discussions and generous knowledge exchange.

# Todo

- [x] set up CI
- [x] simplify settings
- [x] simplify annotations
- [ ] add integration tests
- [ ] explain design choices

[^1]: Session and token share the same expiry time, avoiding database reads if the token is expired.
This scheme of using JWT **is not** related to OAuth 2.0 and is a custom micro-optimization.
