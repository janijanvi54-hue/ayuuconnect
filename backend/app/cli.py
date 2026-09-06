"""Flask CLI commands (seeding helpers).

The full `seed-demo` command is implemented alongside the models in
Phase 2/3. Registering an empty command group here keeps the app factory
stable across phases.
"""

import click
from flask.cli import with_appcontext


@click.command("seed-demo")
@with_appcontext
def seed_demo_command():
    """Seed development data (implemented in Phase 2/3)."""
    click.echo("Seed command will be implemented with the database models.")


def register_commands(app):
    app.cli.add_command(seed_demo_command)