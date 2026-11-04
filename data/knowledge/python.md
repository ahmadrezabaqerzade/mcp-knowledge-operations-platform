# Python Programming

## 1. Overview

Python is a high-level, general-purpose programming language known for its readability, simplicity, and extensive ecosystem.

It is widely used in software engineering, automation, data science, machine learning, deep learning, and artificial intelligence.

Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming.

## 2. Core Language Concepts

### 2.1 Variables and Data Types

Python uses dynamic typing, meaning variables do not require explicit type declarations.

Common built-in data types include:

- `int`: Integer numbers
- `float`: Floating-point numbers
- `complex`: Complex numbers
- `str`: Text strings
- `bool`: Boolean values
- `list`: Ordered, mutable collections
- `tuple`: Ordered, immutable collections
- `dict`: Key-value mappings
- `set`: Unordered collections of unique elements
- `NoneType`: Represents the absence of a value

### 2.2 Control Flow

Python provides control-flow statements for decision-making and repetition.

- `if`, `elif`, and `else` implement conditional execution.
- `for` iterates over iterable objects.
- `while` repeats execution while a condition remains true.
- `break` terminates a loop.
- `continue` skips the current iteration.
- `match` supports structural pattern matching.

### 2.3 Functions

Functions are reusable blocks of code defined using the `def` keyword.

Functions can accept positional arguments, keyword arguments, default values, and variable-length arguments.

The `return` statement sends a result back to the caller.

Python also supports:

- Lambda expressions
- Closures
- Decorators
- Generators
- Recursive functions
- Higher-order functions

### 2.4 Object-Oriented Programming

Python supports object-oriented programming through classes and objects.

Important concepts include:

- Classes and instances
- Instance and class attributes
- Instance, class, and static methods
- Inheritance
- Encapsulation
- Polymorphism
- Composition
- Abstract base classes
- Properties and descriptors

### 2.5 Modules and Packages

A module is a Python file containing reusable code.

A package organizes related modules into a directory hierarchy.

The `import` statement makes modules, classes, and functions available to other Python files.

The `__init__.py` file can be used to initialize regular Python packages and expose selected package interfaces.

## 3. Type System

Python supports optional static type annotations.

Common typing constructs include:

- `str`, `int`, `float`, and `bool`
- `list[str]` and `dict[str, int]`
- `tuple` and `set`
- `Optional` and union types
- `Literal` and `Enum`
- `TypedDict`
- `Protocol`
- `TypeVar` and generics
- Callable types

Type hints improve readability, editor support, and static analysis. They do not normally enforce runtime type checking by themselves.

## 4. Error Handling

Python uses exceptions to represent errors and exceptional conditions.

Important constructs include:

- `try`
- `except`
- `else`
- `finally`
- `raise`

Custom exceptions can be created by inheriting from `Exception`.

Good error handling should distinguish expected failures from unexpected programming errors.

## 5. File and Data Handling

Python provides built-in tools for reading and writing files.

The `pathlib` module provides an object-oriented interface for filesystem paths.

The `json` module supports JSON serialization and deserialization.

The `csv` module handles comma-separated data.

The `logging` module provides configurable application logging.

Context managers, commonly used through the `with` statement, help manage resources safely.

## 6. Modern Python Development

Modern Python projects commonly use:

- `pyproject.toml` for project configuration and metadata
- `uv` for dependency and environment management
- `pytest` for automated testing
- `ruff` for linting and formatting
- Type hints for clearer interfaces
- Virtual environments for dependency isolation
- Git for version control
- Build backends for creating distributions

## 7. Asynchronous Programming

Python supports asynchronous programming using `asyncio`.

Important concepts include:

- `async def` for defining coroutines
- `await` for awaiting asynchronous operations
- Tasks for scheduling concurrent coroutines
- Futures for representing eventual results
- Async context managers
- Async iterators and generators

Asynchronous programming is particularly useful for I/O-bound workloads such as network requests, database operations, and concurrent service interactions.

## 8. Testing and Code Quality

Automated testing helps verify software behavior.

Common testing practices include:

- Unit testing
- Integration testing
- Parameterized testing
- Fixtures
- Mocking
- Regression testing

`pytest` is a widely used Python testing framework.

`ruff` provides fast linting and formatting.

## 9. Applications

Python is commonly used in:

- Web development
- Data engineering
- Machine learning
- Deep learning
- Natural language processing
- Computer vision
- Automation
- API development
- AI agent systems
- Model serving and orchestration
