#!/usr/bin/env python3
"""Main entry point for the Fields application."""
import sys
import os
import click
from utils import get_logger, set_global_debug, get_file_reader, parse_spreadsheet_row, SummarizePermit, Spreadsheet

# Add the src directory to Python path so imports work from any location
sys.path.insert(0, os.path.dirname(__file__))


def set_debug_flag(ctx, param, value):
    """Callback to set debug flag in context and global logger."""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = value
    # Set global debug before any commands run
    set_global_debug(value)


@click.group()
@click.version_option(version="0.1.0")
@click.option('--debug/--no-debug', default=False, callback=set_debug_flag,
              expose_value=False, help='Enable debug output.')
def cli():
    """Fields - A Python package for field management and processing."""
    pass


@cli.command()
@click.pass_context
def hello(ctx):
    """Say hello."""
    logger = get_logger()
    logger.debug("Executing hello command")
    logger.info("Hello from Fields!")


@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--lines', '-n', type=int, help='Number of lines to read (default: all)')
@click.option('--encoding', default='utf-8', help='File encoding (default: utf-8)')
@click.pass_context
def read_file(ctx, filename, lines, encoding):
    """Test Read and display the contents of a file."""
    logger = get_logger()
    logger.debug(f"Reading file: {filename}")

    try:
        reader = get_file_reader()
        content = reader.read_lines(filename)

        if lines and lines > 0:
            content = content[:lines]
            logger.debug(f"Displaying first {lines} lines")
        else:
            logger.debug("Displaying all lines")

        # Display the content
        for i, line in enumerate(content, 1):
            click.echo(f"{i:4d}: {line.rstrip()}")

        logger.info(f"Successfully read {len(content)} lines from {filename}")

    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--max-length', '-l', type=int, default=500,
              help='Maximum length of summary (default: 500)')
@click.pass_context
def summarize_file(ctx, filename, max_length):
    """Summarize the contents of a permit file."""
    logger = get_logger()

    try:
        summarizer = SummarizePermit()
        result = summarizer.summarize_from_file(filename, max_length=max_length)

        if not result.get("success", False):
            logger.error(f"Failed to summarize file: {result.get('error', 'Unknown error')}")
            ctx.exit(1)

        # Display the summary results
        click.echo(f"📄 File: {result['file_path']}")
        click.echo(f"📋 Type: {result['file_type'].upper()}")
        if result.get('pages') and result['pages'] > 1:
            click.echo(f"📑 Pages: {result['pages']}")
        click.echo(f"📊 Words: {result['word_count']:,}")
        click.echo(f"📏 Characters: {result['character_count']:,}")
        click.echo()

        # Display date/time slots if found
        date_time_slots = result.get('date_time_slots', [])
        if date_time_slots:
            click.echo("🕒 Available Time Slots:")
            click.echo("-" * 50)
            for i, slot in enumerate(date_time_slots, 1):
                click.echo(f"{i:2d}. {slot}")
            click.echo()

        # Display field names if found
        field_names = result.get('field_names', [])
        if field_names:
            click.echo("🏟️  Available Fields:")
            click.echo("-" * 50)
            for i, field in enumerate(field_names, 1):
                click.echo(f"{i:2d}. {field}")
            click.echo()

        # Display field-specific date/time slots
        field_date_time_slots = result.get('field_date_time_slots', {})
        if field_date_time_slots:
            click.echo("📅 Field-Specific Time Slots:")
            click.echo("-" * 50)
            for field_name, time_slots in field_date_time_slots.items():
                if time_slots:  # Only show fields that have time slots
                    click.echo(f"🏟️  {field_name}:")
                    for i, slot in enumerate(time_slots, 1):
                        click.echo(f"   {i}. {slot}")
                    click.echo()

        click.echo("📝 Summary:")
        click.echo("-" * 50)
        click.echo(result['summary'])

        logger.info(f"Successfully summarized file: {filename}")

    except Exception as e:
        logger.error(f"Error summarizing file {filename}: {e}")
        ctx.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.pass_context
def summarize_directory(ctx, directory):
    """Summarize permit files in a directory."""
    logger = get_logger()

    try:
        click.echo(f"📁 Directory: {directory}")

        # List all files in the directory
        files = []
        summaries = []
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    files.append(item_path)
        except PermissionError:
            logger.warning(f"Permission denied accessing directory: {directory}")

        if files:
            click.echo(f"\n📄 Files found ({len(files)}):")
            click.echo("-" * 50)
            for i, file in enumerate(sorted(files), 1):
                click.echo(f"{i:3d}. {file}")
        else:
            click.echo("\n📄 No files found in this directory.")

        if files:
            click.echo(f"\n📄 Processing found ({len(files)}):")
            click.echo("-" * 50)
            for i, file in enumerate(sorted(files), 1):
                click.echo(f"Processing :: {i:3d}. {file}")
                summarizer = SummarizePermit()
                result = summarizer.summarize_from_file(file, max_length=500)

                if not result.get("success", False):
                    logger.error(f"Failed to summarize file: {result.get('error', 'Unknown error')}")
                    ctx.exit(1)

                summaries.append(result)    
        else:
            click.echo("\n📄 No files found in this directory.")

        if summaries:
            spreadsheet_summary = Spreadsheet()

            click.echo(f"\n📄 Summaries found ({len(summaries)}):")
            click.echo("-" * 50)
            for i, summary in enumerate(summaries, 1):
                
                issued_date = summary['issued_date']

                for field_name in summary['field_names']:
                    truncated_field_name = field_name[0:field_name.find("(Athletic Field Use)")].strip()
                    click.echo(f"{i:3d}. {truncated_field_name}")
                    if not spreadsheet_summary.sheet_exists(truncated_field_name):
                        spreadsheet_summary.create_sheet(truncated_field_name)
                    
                    for row in summary['field_date_time_slots'][field_name]:
                        spreadsheet_summary.switch_sheet(truncated_field_name)

                        if row.find("--") < 1:
                            spreadsheet_summary.add_row(parse_spreadsheet_row(row, issued_date))

            # Remove the initial worksheet
            del spreadsheet_summary.worksheets["Sheet1"]

            click.echo(f"{len(spreadsheet_summary.worksheets)} worksheets created")
            spreadsheet_summary.save_to_excel("/tmp/spreadsheet_summary.xlsx")

        click.echo("-" * 50)
        logger.info(f"Successfully processed directory: {directory} (found {len(files)} files)")

    except Exception as e:
        logger.error(f"Error processing directory {directory}: {e}")
        ctx.exit(1)


def main():
    """Main function - kept for backward compatibility."""
    print("Main function executed successfully!")


if __name__ == "__main__":
    cli()